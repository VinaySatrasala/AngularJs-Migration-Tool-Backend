import json
import os
from pathlib import Path
import asyncio
from typing import Dict, List, Any, Union
import re
from datetime import datetime
import logging

import concurrent

class ReactComponentGenerator:
    """
    Generates a React application from a predefined migration structure.
    Focuses on creating a clean, structured React project.
    """
    
    def __init__(self, migration_file: str, analysis_file: str, output_dir: Union[str, Path], llm_config: Any):
        """
        Initialize the React project generator.
        
        Args:
            migration_file: Path to the JSON file containing the project structure
            analysis_file: Path to the JSON file containing source file analysis
            output_dir: Directory where the React project will be created
            llm_config: Configuration for the language model
        """
        # Setup logging
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s: %(message)s',
            filename='react_generator.log'
        )
        self.logger = logging.getLogger(__name__)
        
        self.migration_file = migration_file
        self.analysis_file = analysis_file
        self.output_dir = Path(output_dir)
        self.llm_config = llm_config
        
        # Data containers
        self.migration_data = {}
        self.analysis_data = {}
    
    def _validate_migration_structure(self, data: Dict[str, Any]) -> bool:
        """
        Validate the overall structure of the migration data.
        
        Args:
            data: Migration data dictionary
        
        Returns:
            bool: Whether the structure is valid
        """
        if not isinstance(data, dict):
            self.logger.error("Migration data is not a dictionary")
            return False
        
        return True
    
    async def load_data(self):
        """
        Load migration and analysis data with comprehensive error handling.
        """
        try:
            # Load migration data
            with open(self.migration_file, 'r', encoding='utf-8') as f:
                self.migration_data = json.load(f)
            
            # Load analysis data
            with open(self.analysis_file, 'r', encoding='utf-8') as f:
                self.analysis_data = json.load(f)
            
            # Validate structure
            if not self._validate_migration_structure(self.migration_data):
                raise ValueError("Invalid migration data structure")
            
            self.logger.info("Data loaded successfully")
        
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            raise
    
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
                    self.logger.error(f"Failed to generate file {current_path}: {e}")
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
            
            self.logger.info("Parallel project generation completed successfully")
        
        except Exception as e:
            self.logger.error(f"Project file generation failed: {e}")
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
            from utils.react_generator_prompts import _build_generation_prompt
            prompt = _build_generation_prompt(source_content, file_info)
            
            # Generate code using LLM
            response = self.llm_config._langchain_llm.predict(prompt)
            
            # Extract and clean code
            generated_code = self._extract_code(response, file_info['file_type'])
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(generated_code)
            
            self.logger.info(f"Generated: {file_path}")
        
        except Exception as e:
            self.logger.error(f"Error generating {file_path}: {e}")
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
            self.logger.error(f"Project generation failed: {e}")
            raise