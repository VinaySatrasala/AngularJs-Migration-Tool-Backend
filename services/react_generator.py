import json
import os
from pathlib import Path
import asyncio
from typing import Dict, List, Any, Union
import logging
import re
from datetime import datetime
from utils.react_generator_prompts import _build_generation_prompt
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
        self.migration_file = migration_file
        self.analysis_file = analysis_file
        self.output_dir = Path(output_dir)
        self.llm_config = llm_config
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Data containers
        self.migration_data = {}
        self.analysis_data = {}
        self.source_files = {}
    
    def _setup_logging(self):
        """
        Setup logging with file and console output.
        
        Returns:
            Configured logger
        """
        # Create logs directory
        logs_dir = self.output_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = logs_dir / f"generation_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        return logging.getLogger(__name__)
    
    def _validate_migration_structure(self, data: Dict[str, Any]) -> bool:
        """
        Validate the overall structure of the migration data.
        
        Args:
            data: Migration data dictionary
        
        Returns:
            bool: Whether the structure is valid
        """
        required_keys = ['file_name', 'relative_path', 'file_type']
        
        def validate_node(node):
            # Check for dictionary type
            if not isinstance(node, dict):
                return False
            
            # Check if it's a file entry
            if all(key in node for key in required_keys):
                return True
            
            # Recursively validate nested structures
            return all(validate_node(value) for value in node.values())
        
        try:
            return validate_node(data)
        except Exception as e:
            self.logger.error(f"Structure validation failed: {str(e)}")
            return False
    
    async def load_data(self):
        """
        Load migration and analysis data with error handling.
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
            
            self.logger.info("Successfully loaded and validated migration data")
        
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            raise
    
    def _find_source_file(self, source_files: List[str]) -> str:
        """
        Find and append content from all available source files.

        Args:
            source_files: List of potential source file paths.

        Returns:
            Concatenated content of all found source files, or an empty string.
        """
        combined_content = []

        print(f"Debug: Checking source files: {source_files}")

        for file_path in source_files:
            # Debug print to check if the file exists in analysis data
            if file_path in self.analysis_data:
                print(f"Debug: Found {file_path} in analysis_data")

                content = self.analysis_data[file_path].get('content', '')
                if content:
                    print(f"Debug: Adding content from {file_path}")
                    combined_content.append(content)
                else:
                    print(f"Debug: {file_path} exists but has no content.")
            else:
                print(f"Debug: {file_path} NOT found in analysis_data")

        result = "\n\n".join(combined_content) if combined_content else ""
        
        # Debug print final result length
        print(f"Debug: Final combined content length: {len(result)}")

        return result


    
    
    def _extract_code(self, response: str, file_type: str) -> str:
        """
        Extract clean code from AI response.
        
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
            # Ensure valid JSON
            try:
                json.loads(code)
            except json.JSONDecodeError:
                # Attempt to fix common JSON issues
                code = re.sub(r',\s*}', '}', code)
                code = re.sub(r',\s*]', ']', code)
        
        return code.strip()
    
    async def generate_project(self):
        """
        Main method to generate the entire React project.
        """
        try:
            # Load migration data
            await self.load_data()
            
            # Create output directory
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate files
            for file_path, file_info in self.migration_data.items():
                try:
                    # Skip metadata entries
                    if file_path in ['__metadata__', 'project_structure']:
                        continue
                    
                    # Determine full output path
                    output_path = self.output_dir / file_info['relative_path']
                    
                    # Create parent directory
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Generate prompt
                    source_content = self._find_source_file(file_info.get('source_files', []))
                    prompt = _build_generation_prompt(source_content,file_info)
                    print(prompt)
                    # Generate code
                    response = await self.llm_config._langchain_llm.apredict(prompt)
                    print(response)
                    # Extract and clean code
                    generated_code = self._extract_code(response, file_info['file_type'])
                    
                    # Write to file
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(generated_code)
                    
                    self.logger.info(f"Generated: {file_info['relative_path']}")
                
                except Exception as e:
                    self.logger.error(f"Error generating {file_path}: {str(e)}")
                    continue
            
            self.logger.info("Project generation completed successfully")
        
        except Exception as e:
            self.logger.error(f"Project generation failed: {str(e)}")
            raise