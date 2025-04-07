import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from services.db_service import MigrationDBService
from utils.target_structre_prompt import target_prompt
from sqlalchemy.orm import Session

# logger = logging.getLogger(__name__)

class ReactMigrationStructureGenerator:
    """
    A class that generates a proposed React project structure from an AngularJS project analysis.
    
    This class analyzes an AngularJS project and generates a React migration structure by
    leveraging AI to determine the optimal component hierarchy, state management,
    and routing approach for the migrated application.
    """
    
    def __init__(self, db: Session, llm_config: Any, project_id: str,instructions : str = ""):
        """
        Initialize the ReactMigrationStructureGenerator.

        Args:
            db: SQLAlchemy DB session
            llm_config: Configuration for the language model to use
            project_id: Unique identifier for the project
        """
        self.db = db
        self.project_id = project_id
        self.analysis_data = None
        self.llm_config = llm_config
        self.instructions = instructions

    async def load_analysis_data(self) -> Dict[str, Any]:
        """
        Load the AngularJS project analysis from the database and remove file content.

        Returns:
            Dict containing the analysis data without file contents
        """
        analysis_record = MigrationDBService.get_analysis(self.db, self.project_id)
        if not analysis_record:
            raise ValueError(f"No analysis data found in DB for project_id: {self.project_id}")
        
        analysis_data = analysis_record["analysis_data"]

        # Remove "content" field from each file entry
        for file_path, file_info in analysis_data.items():
            if isinstance(file_info, dict) and "content" in file_info:
                file_info.pop("content")

        self.analysis_data = analysis_data
        return self.analysis_data


    
    async def generate_react_structure(self) -> Dict[str, Any]:
        """
        Generate a complete React project structure based on the AngularJS analysis.
        
        Returns:
            Dict containing the React file structure with source file dependencies, 
            migration suggestions, and routing information for each target file.
        """
        if not self.analysis_data:
            await self.load_analysis_data()
        
        # Create a comprehensive prompt for the AI
        prompt = self._build_structure_generation_prompt()
        
        try:
            # Get the AI response
            # logger.info("Querying LLM for React structure generation...")
            ai_response = await self._query_llm(prompt)
            
            # Process and validate the structure
            # logger.info("Validating generated structure...")
            validated_structure = self._validate_structure(ai_response)
            # Save the structure
            # logger.info("Saving React migration structure...")
                
            # logger.info(f"React structure saved to: {output_file}")
            return validated_structure
            
        except Exception as e:
            # logger.error(f"Error generating React structure: {str(e)}")
            raise
    
    def _build_structure_generation_prompt(self) -> str:
        """
        Build a detailed prompt for the AI to generate the React structure.
        
        Returns:
            String containing the prompt for the AI
        """
        prompt = target_prompt()

        # Format the prompt with the analysis data
        formatted_prompt = prompt.replace("{json_data}", json.dumps(self.analysis_data, indent=2)).replace("{instructions}", self.instructions or "")
        
        return formatted_prompt
    
    async def _query_llm(self, prompt: str) -> Dict[str, Any]:
        """
        Query the language model with the given prompt.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            Dict containing the LLM's response
        """
        try:
            # Use langchain LLM for structured output
            # logger.info("Sending prompt to LLM...")
            
            # Add system message to the prompt
            full_prompt = "You are a React migration expert. Always respond with valid JSON only.\n\n" + prompt
            response_text = await self.llm_config._langchain_llm.ainvoke(full_prompt)
            response_text = response_text.content.strip()
            
            # logger.info("Received response from LLM")
            
            # Try to find JSON in the response
            import re
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)
            
            if json_match:
                json_str = json_match.group(1).strip()
                # logger.info("Found JSON in code block")
            else:
                # If no code blocks, try to find JSON between curly braces
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end].strip()
                    # logger.info("Found JSON between curly braces")
                else:
                    # logger.error("No JSON found in response")
                    # logger.error(f"Response text: {response_text}")
                    raise ValueError("Could not find JSON in LLM response")
            
            # Parse the JSON
            try:
                result = json.loads(json_str)
                # logger.info("Successfully parsed JSON response")
                return result
            except json.JSONDecodeError as e:
                # logger.error(f"Invalid JSON: {str(e)}")
                # logger.error(f"JSON string: {json_str}")
                raise ValueError("LLM response was not valid JSON")
                
        except Exception as e:
            # logger.error(f"Error in LLM query: {str(e)}")
            # if 'response_text' in locals():
                # logger.error(f"Full response: {response_text}")
            raise Exception(f"Error querying LLM: {str(e)}")
            
    def _validate_structure(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize the structure returned by the AI.
        
        Args:
            structure: The structure to validate
            
        Returns:
            Validated and normalized structure
        """
        try:
            if not isinstance(structure, dict):
                raise ValueError("Structure must be a dictionary")
            
            # Required fields for each file
            required_fields = [
                "file_name",
                "relative_path",
                "file_type",
                "dependencies",
                "source_files",
                "description",
                "migration_suggestions"
            ]

            # Validate and fix each entry
            for key, value in structure.items():
                if not isinstance(value, dict):
                    raise ValueError(f"Entry for {key} must be a dictionary")
                
                # **Check if it's a file (has 'file_type')**
                is_file = "file_type" in value

                if is_file:
                    # Ensure all required fields exist for files
                    for field in required_fields:
                        if field not in value:
                            if field in ["dependencies", "source_files"]:
                                value[field] = []
                            else:
                                value[field] = f"Default {field} for {key}"

                    # Ensure dependencies and source_files are lists
                    if not isinstance(value["dependencies"], list):
                        value["dependencies"] = []
                    if not isinstance(value.get("source_files"), list):
                        value["source_files"] = []

                    # Normalize file name and path
                    if "/" in key:
                        value["file_name"] = key.split("/")[-1]
                    else:
                        value["file_name"] = key

                    if "relative_path" not in value:
                        value["relative_path"] = key

                    # Ensure file type is without dot
                    value["file_type"] = value["file_type"].lstrip(".")

            return structure

        except Exception as e:
            raise

            
        except Exception as e:
            # logger.error(f"Error validating structure: {str(e)}")
            # logger.error(f"Structure: {json.dumps(structure, indent=2)}")
            raise
            
    
    def _count_files(self, structure: Dict[str, Any]) -> int:
        """Count total files in the structure recursively"""
        count = 0
        
        if "files" in structure:
            count += len(structure["files"])
            
        if "subdirectories" in structure:
            for subdir in structure["subdirectories"].values():
                count += self._count_files(subdir)
                
        return count
    
    def _get_timestamp(self) -> str:
        """Get the current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    