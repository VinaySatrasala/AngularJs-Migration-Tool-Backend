import json
import os
from pathlib import Path
import asyncio
from typing import Dict, List, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)

class ReactMigrationStructureGenerator:
    """
    A class that generates a proposed React project structure from an AngularJS project analysis.
    
    This class analyzes an AngularJS project and generates a React migration structure by
    leveraging AI to determine the optimal component hierarchy, state management,
    and routing approach for the migrated application.
    """
    
    def __init__(self, analysis_file: str, llm_config: Any, project_id: str):
        """
        Initialize the ReactMigrationStructureGenerator.
        
        Args:
            analysis_file: Path to the JSON file containing AngularJS project analysis
            llm_config: Configuration for the language model to use
            project_id: Unique identifier for the project
        """
        self.analysis_file = analysis_file
        self.llm_config = llm_config
        self.project_id = project_id
        self.analysis_data = None
        
    async def load_analysis_data(self) -> Dict[str, Any]:
        """
        Load the AngularJS project analysis from the JSON file.
        
        Returns:
            Dict containing the analysis data
        """
        if not os.path.exists(self.analysis_file):
            raise FileNotFoundError(f"Analysis file not found: {self.analysis_file}")
            
        try:
            with open(self.analysis_file, 'r') as f:
                self.analysis_data = json.load(f)
            return self.analysis_data
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in analysis file: {self.analysis_file}")
    
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
            logger.info("Querying LLM for React structure generation...")
            ai_response = await self._query_llm(prompt)
            
            # Process and validate the structure
            logger.info("Validating generated structure...")
            validated_structure = self._validate_structure(ai_response)
            
            # Save the structure
            logger.info("Saving React migration structure...")
            output_dir = Path(self.analysis_file).parent.parent
            output_file = output_dir / "react_migration_structure.json"
            
            with open(output_file, 'w') as f:
                json.dump(validated_structure, f, indent=2)
                
            logger.info(f"React structure saved to: {output_file}")
            return validated_structure
            
        except Exception as e:
            logger.error(f"Error generating React structure: {str(e)}")
            raise
    
    def _build_structure_generation_prompt(self) -> str:
        """
        Build a detailed prompt for the AI to generate the React structure.
        
        Returns:
            String containing the prompt for the AI
        """
        prompt = """Analyze the following AngularJS project and generate a React migration structure.

Here is the AngularJS project analysis:
```json
{json_data}
```

Generate a flat JSON object where each key is a target React file path. The structure must follow this format:

{
  "[file_path]": {
    "file_name": "Name of the file",
    "relative_path": "Path from project root",
    "file_type": "File extension (no dot)",
    "dependencies": [
      "List of files/packages this file depends on in React",
      "Include both npm packages and local files"
    ],
    "source_files": [
      "List of original AngularJS files required for migrating this file"
    ],
    "description": "Purpose of this file",
    "migration_suggestions": "How to convert from AngularJS equivalent",
    "routing_info": "Routing-related details if applicable"
  }
}

Dependencies should include:
- NPM packages needed (react, react-router-dom, etc.)
- Local files imported/used by this file
- CSS and asset files directly imported
- Parent components that use this file
- Child components rendered by this file

For each AngularJS file in the analysis:
1. Create equivalent React file(s)
2. Map controllers to functional components
3. Convert services to hooks or context
4. Transform templates to JSX
5. Update routing configuration
6. Include all necessary dependencies

Return ONLY the JSON object with the complete file structure."""

        # Format the prompt with the analysis data
        formatted_prompt = prompt.replace("{json_data}", json.dumps(self.analysis_data, indent=2))
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
            logger.info("Sending prompt to LLM...")
            
            # Add system message to the prompt
            full_prompt = "You are a React migration expert. Always respond with valid JSON only.\n\n" + prompt
            response_text = await self.llm_config._langchain_llm.apredict(full_prompt)
            response_text = response_text.strip()
            
            logger.info("Received response from LLM")
            
            # Try to find JSON in the response
            import re
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)
            
            if json_match:
                json_str = json_match.group(1).strip()
                logger.info("Found JSON in code block")
            else:
                # If no code blocks, try to find JSON between curly braces
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end].strip()
                    logger.info("Found JSON between curly braces")
                else:
                    logger.error("No JSON found in response")
                    logger.error(f"Response text: {response_text}")
                    raise ValueError("Could not find JSON in LLM response")
            
            # Parse the JSON
            try:
                result = json.loads(json_str)
                logger.info("Successfully parsed JSON response")
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {str(e)}")
                logger.error(f"JSON string: {json_str}")
                raise ValueError("LLM response was not valid JSON")
                
        except Exception as e:
            logger.error(f"Error in LLM query: {str(e)}")
            if 'response_text' in locals():
                logger.error(f"Full response: {response_text}")
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
                
            # Required files that must exist
            required_files = {
                "index.html": {
                    "relative_path": "public/index.html",
                    "file_type": "html",
                    "source_files": ["index.html"]
                },
                "package.json": {
                    "relative_path": "package.json",
                    "file_type": "json",
                    "source_files": []
                },
                "src/App.js": {
                    "relative_path": "src/App.js",
                    "file_type": "js",
                    "source_files": ["app.module.js", "app.config.js"]
                },
                "src/routes/AppRoutes.js": {
                    "relative_path": "src/routes/AppRoutes.js",
                    "file_type": "js",
                    "source_files": ["app.config.js"]
                }
            }
            
            # Required fields for each file
            required_fields = [
                "file_name",
                "relative_path",
                "file_type",
                "dependencies",
                "source_files",
                "description",
                "migration_suggestions",
                "routing_info"
            ]
            
            # Ensure all required files exist
            for file_path, defaults in required_files.items():
                if file_path not in structure:
                    logger.warning(f"Adding missing required file: {file_path}")
                    structure[file_path] = {
                        "file_name": os.path.basename(file_path),
                        "relative_path": defaults["relative_path"],
                        "file_type": defaults["file_type"],
                        "dependencies": [],
                        "source_files": defaults.get("source_files", []),
                        "description": f"Required {defaults['file_type']} file for React project",
                        "migration_suggestions": "Create this file following React best practices",
                        "routing_info": "Update routing configuration as needed"
                    }
                    
            # Validate and fix each file entry
            for file_path, file_data in structure.items():
                if not isinstance(file_data, dict):
                    raise ValueError(f"File data for {file_path} must be a dictionary")
                    
                # Ensure all required fields exist
                for field in required_fields:
                    if field not in file_data:
                        if field in ["dependencies", "source_files"]:
                            file_data[field] = []
                        else:
                            file_data[field] = f"Default {field} for {file_path}"
                            
                # Ensure dependencies and source_files are lists
                if not isinstance(file_data["dependencies"], list):
                    file_data["dependencies"] = []
                if not isinstance(file_data.get("source_files"), list):
                    file_data["source_files"] = []
                    
                # Normalize file name and path
                if "/" in file_path:
                    file_data["file_name"] = file_path.split("/")[-1]
                else:
                    file_data["file_name"] = file_path
                    
                if "relative_path" not in file_data:
                    file_data["relative_path"] = file_path
                    
                # Ensure file type is without dot
                file_data["file_type"] = file_data["file_type"].lstrip(".")
            
            logger.info("Successfully validated structure")
            return structure
            
        except Exception as e:
            logger.error(f"Error validating structure: {str(e)}")
            logger.error(f"Structure: {json.dumps(structure, indent=2)}")
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