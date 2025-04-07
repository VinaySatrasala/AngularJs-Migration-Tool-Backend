import json
import os
from pathlib import Path
import asyncio
from typing import Dict, List, Any, Union
import re
from datetime import datetime
from services.db_service import MigrationDBService
from utils.react_generator_prompts import _build_generation_prompt
import concurrent
from sqlalchemy.orm import Session

class ReactComponentGenerator:
    """
    Generates a React application from a predefined migration structure.
    Focuses on creating a clean, structured React project.
    """
    
    def __init__(self,db : Session,output_dir: Union[str, Path], llm_config: Any,project_id : str,instructions : str = ""):
        """
        Initialize the React project generator.
        
        Args:
            migration_file: Path to the JSON file containing the project structure
            analysis_file: Path to the JSON file containing source file analysis
            output_dir: Directory where the React project will be created
            llm_config: Configuration for the language model
        """

        

        self.output_dir = Path(output_dir)
        self.llm_config = llm_config
        self.db = db
        self.project_id = project_id
        self.instructions = instructions
        # Data containers
        self.migration_data = {}
        self.analysis_data = {}
        self.flattened_migration_data = {}
    
    def _validate_migration_structure(self, data: Dict[str, Any]) -> bool:
        """
        Validate the overall structure of the migration data.
        
        Args:
            data: Migration data dictionary
        
        Returns:
            bool: Whether the structure is valid
        """
        if not isinstance(data, dict):
            return False
        
        return True
    
    async def load_data(self):
        """
        Load migration and analysis data from the database with comprehensive error handling.
        """
        try:
            # Load migration (target structure) data from DB
            structure_record = MigrationDBService.get_target_structure(self.db, self.project_id)
            if not structure_record:
                raise ValueError(f"No migration structure found in DB for project_id: {self.project_id}")
            self.migration_data = structure_record["structure_data"]

            # Load analysis data from DB
            analysis_record = MigrationDBService.get_analysis(self.db, self.project_id)
            if not analysis_record:
                raise ValueError(f"No analysis data found in DB for project_id: {self.project_id}")
            
            # Remove "content" from each file entry in analysis data
            analysis_data = analysis_record["analysis_data"]
            self.analysis_data = analysis_data

            # Validate structure
            if not self._validate_migration_structure(self.migration_data):
                raise ValueError("Invalid migration data structure")

            self.flattened_migration_data = self.convert_to_folder_structure()
            # print("Success: " + str(self.flattened_migration_data))

        except Exception as e:
            # print(f"Error loading data: {str(e)}")
            raise

    def convert_to_folder_structure(self):
        data = self.migration_data
        folder_structure = {}
        
        def insert_into_structure(path, structure):
            parts = path.split("/")
            current = structure
            for part in parts[:-1]:  # Traverse folders
                current = current.setdefault(part, {})
            current[parts[-1]] = {}  # Store file as empty dict
        
        def process_node(node):
            if isinstance(node, dict):
                for key, value in node.items():
                    if isinstance(value, dict) and "relative_path" in value:
                        insert_into_structure(value["relative_path"], folder_structure)
                    else:
                        process_node(value)
        
        process_node(data)
        return folder_structure
    
    def _find_source_file_content(self, source_files: List[str]) -> str:
        """
        Enhanced source file content retrieval.

        Args:
            source_files: List of potential source file paths.

        Returns:
            Concatenated content of source files.
        """
        combined_content = []

        for file_path in source_files:
            # Try multiple matching strategies
            matched_content = None
            
            # 1. Direct match
            matched_content = self.analysis_data.get(file_path, {}).get('content')
            
            # 2. Partial path match
            if not matched_content:
                matched_content = next(
                    (data.get('content') for key, data in self.analysis_data.items() 
                     if file_path in key),
                    None
                )
            
            # 3. Filename match
            if not matched_content:
                filename = os.path.basename(file_path)
                matched_content = next(
                    (data.get('content') for key, data in self.analysis_data.items() 
                     if filename in key),
                    None
                )
            
            if matched_content:
                combined_content.append(matched_content)
        
        return "\n\n".join(combined_content) if combined_content else ""
    
    def _extract_code(self, response: str, file_type: str) -> str:
        """
        Robust code extraction with enhanced cleaning.
        
        Args:
            response: Raw AI response
            file_type: Type of file being generated
        
        Returns:
            Cleaned code string
        """
        # Remove markdown code block syntax
        code = re.sub(r'^```[\w]*\n', '', response)
        code = re.sub(r'\n```$', '', code)
        
        # Additional cleaning for specific file types
        if file_type == 'json':
            try:
                # Attempt to parse and re-format JSON
                parsed_json = json.loads(code)
                return json.dumps(parsed_json, indent=2)
            except json.JSONDecodeError:
                # Attempt to fix common JSON issues
                code = re.sub(r',\s*}', '}', code)
                code = re.sub(r',\s*]', ']', code)
        
        return code.strip()
    
    async def _generate_project_files(self):
        """
        Comprehensive project file generation with parallel processing
        Fully async implementation
        """
        async def _process_file_or_directory(key: str, value: Any, current_path: Path):
            """
            Process individual file or directory
            """
            # Skip metadata keys
            if key in ['file_name', 'file_type', 'dependencies', 'source_files', 
                       'description', 'migration_suggestions', 'relative_path']:
                return None

            # Direct file with metadata
            if isinstance(value, dict) and 'file_type' in value:
                try:
                    await self._generate_single_file_async(value, current_path)
                except Exception as e:
                    print(f"Error generating file {key}: {e}")
                return None

            # Directory processing
            if isinstance(value, dict):
                # Create directory
                os.makedirs(current_path, exist_ok=True)
                
                # Handle files in components/services
                if 'files' in value:
                    file_tasks = [
                        self._generate_single_file_async(
                            file_info, 
                            current_path / filename
                        )
                        for filename, file_info in value['files'].items()
                    ]
                    await asyncio.gather(*file_tasks)
                else:
                    # Recursively process nested directories
                    for nested_key, nested_value in value.items():
                        nested_path = current_path / nested_key
                        await _process_file_or_directory(nested_key, nested_value, nested_path)
            
            return None

        try:
            # Ensure output directory exists
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Create tasks for each top-level item
            tasks = [
                _process_file_or_directory(key, value, self.output_dir / key)
                for key, value in self.migration_data.items()
            ]
            
            # Wait for all tasks to complete
            await asyncio.gather(*tasks)
            
        
        except Exception as e:
            raise

    async def _generate_single_file_async(self, file_info: Dict[str, Any], file_path: Union[str, Path]):
        """
        Async method to generate a single file
        """
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        try:
            # Convert to Path if it's a string
            file_path = Path(file_path)
            
            # Find source file content
            source_content = self._find_source_file_content(
                file_info.get('source_files', [])
            )
            
            # Prepare generation prompt
            prompt = _build_generation_prompt(source_content, file_info,self.flattened_migration_data,self.instructions)
            # print(prompt)
            # Generate code using LLM
            response = self.llm_config._langchain_llm.invoke(prompt)
            # print(response)
            # Extract and clean code
            generated_code = self._extract_code(response.content, file_info['file_type'])
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(generated_code)
            
        
        except Exception as e:
            raise

    async def generate_project(self):
        """
        Main method to generate the entire React project
        Fully async and compatible with web frameworks
        """
        try:
            # Load migration data
            await self.load_data()
            
            # Generate project files
            await self._generate_project_files()
        
        except Exception as e:
            raise