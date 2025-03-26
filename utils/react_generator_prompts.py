from typing import Any, Dict


def _build_generation_prompt(source_content : str,file_info: Dict[str, Any]) -> str:
        """
        Build a generation prompt for a specific file.
        
        Args:
            source_content: Source content for the file
            file_info: Information about the file to generate
        
        Returns:
            Prompt string for code generation
        """
        
        # Base prompt template
        base_prompt = f"""Generate a React {file_info['file_type']} for {file_info['relative_path']}

        File Details:
        - Description: {file_info.get('description', '')}
        - Dependencies: {', '.join(file_info.get('dependencies', []))}
        - Migration Suggestions: {file_info.get('migration_suggestions', '')}

        {f"Source Content:\n```\n{source_content}\n```" if source_content else ""}

        Generation Requirements:
        1. Follow modern React best practices
        2. Use functional components
        3. Implement all specified dependencies
        4. Maintain original functionality
        5. Use appropriate React patterns

        Return ONLY the code for the file."""
        
        return base_prompt
    