import os
import json
import re
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor

# Import your LLM configuration
from config.llm_config import llm_config

# Import file-specific prompts
from utils.analysis_prompts import (
    get_js_prompt,
    get_html_prompt,
    get_css_prompt,
    get_json_prompt,
    get_default_prompt
)

class AngularProjectAnalyzer:
    """
    Analyzer for AngularJS projects that creates a structured analysis of the codebase.
    Uses LLMs to generate comprehensive analysis for migration planning.
    """
    def __init__(self, project_path: str,instructions : str = ""):
        self.project_path = Path(project_path)
        self.file_extensions = {'.js', '.html', '.css', '.json', '.md','.cshtml'}
        self.analysis_results = {}
        self.llm = llm_config._langchain_llm
        self.instructions = instructions
        self.patterns = {
            'angular_module': re.compile(r'angular\.module\([\'"]([^\'"]+)[\'"]'),
            'angular_controller': re.compile(r'\.controller\([\'"]([^\'"]+)[\'"]'),
            'angular_service': re.compile(r'\.(?:factory|service|provider)\([\'"]([^\'"]+)[\'"]'),
            'angular_directive': re.compile(r'\.directive\([\'"]([^\'"]+)[\'"]'),
            'require_import': re.compile(r'require\([\'"]([^\'"]+)[\'"]'),
            'import_statement': re.compile(r'import.*?from\s+[\'"]([^\'"]+)[\'"]'),
            'angular_component': re.compile(r'component\([\'"]([^\'"]+)[\'"]'),
            'ng_include': re.compile(r'ng-include=[\'"]([^\'"]+)[\'"]'),
            'html_script_src': re.compile(r'<script.*?src=[\'"]([^\'"]+)[\'"]'),
            'html_link_href': re.compile(r'<link.*?href=[\'"]([^\'"]+)[\'"]'),
            'injection': re.compile(r'\$inject\s*=\s*\[(.*?)\]|\bfunction\s*\((.*?)\)'),
            'routing': re.compile(r'\.(?:config|when|state|otherwise)\s*\(\s*(?:function|\[|{)')
        }
        


    async def analyze_project(self) -> Dict[str, Any]:
        """Main method to analyze the entire AngularJS project"""
        # print(f"Starting analysis of project at: {self.project_path}")
        
        # 1. Gather all relevant files
        all_files = self._gather_files()
        # print(f"Found {len(all_files)} files to analyze")
        
        # 2. Process each file to extract basic information
        with ThreadPoolExecutor() as executor:
            file_info_futures = [
                executor.submit(self._extract_file_info, file_path) 
                for file_path in all_files
            ]
            file_info_results = {
                future.result()['relative_path']: future.result() 
                for future in file_info_futures
            }
        
        # 3. Analyze dependencies between files
        for file_path, info in file_info_results.items():
            dependencies = self._find_dependencies(info['content'], file_path, file_info_results)
            info['dependencies'] = dependencies
        
        # 4. Use LLM to analyze each file
        for file_path, info in file_info_results.items():
            migration_analysis = await self._analyze_with_ai(info)
            info.update(migration_analysis)
        
        # 5. Save both versions of results
        self.analysis_results = file_info_results
        
        return file_info_results
    def _gather_files(self) -> List[Path]:
        """Gather all relevant files from the project directory"""
        all_files = []
        
        for file_path in self.project_path.glob('**/*'):
            if file_path.is_file() and file_path.suffix in self.file_extensions:
                # Skip node_modules, dist, and other common build directories
                if any(part in str(file_path) for part in ['node_modules', 'dist', 'build', '.git']):
                    continue
                all_files.append(file_path)
                
        return all_files

    def _extract_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Extract basic information from a file"""
        try:
            content = file_path.read_text(errors='replace')
            
            # Get file type and relative path
            file_type = file_path.suffix[1:]  # Remove the leading dot
            relative_path = str(file_path.relative_to(self.project_path))
            
            return {
                "file_name": file_path.name,
                "relative_path": relative_path,
                "file_type": file_type,
                "content": content,
                "dependencies": []  # Will be filled later
            }
            
        except Exception as e:
            # print(f"Error processing file {file_path}: {str(e)}")
            return {
                "file_name": file_path.name,
                "relative_path": str(file_path.relative_to(self.project_path)),
                "file_type": file_path.suffix[1:],
                "error": str(e),
                "content": "",
                "dependencies": []
            }


    def  _find_dependencies(self, content: str, file_path: str, all_files: Dict[str, Dict]) -> List[str]:
        """Find dependencies for a given file"""
        dependencies = set()
        file_type = file_path.split('.')[-1]
        
        # JS file dependencies
        if file_type == 'js':
            # Look for requires and imports
            requires = self.patterns['require_import'].findall(content)
            imports = self.patterns['import_statement'].findall(content)
            
            # Process requires and imports to find actual files
            for req in requires + imports:
                resolved_path = self._resolve_path(req, file_path, all_files)
                if resolved_path:
                    dependencies.add(resolved_path)
                    
            # Look for injected dependencies
            injections = self._extract_injections(content)
            for injection in injections:
                # Find files that provide this service/component
                for other_path, other_info in all_files.items():
                    if other_path == file_path:
                        continue
                    
                    # Check if the file might contain the service
                    other_content = other_info.get('content', '')
                    service_pattern = f"(?:service|factory|provider|component|directive)\\(['\"]({injection})['\"]"
                    if re.search(service_pattern, other_content):
                        dependencies.add(other_path)
        
        # HTML file dependencies
        elif file_type == 'html' or file_type == 'cshtml':
            # Look for script and link tags
            scripts = self.patterns['html_script_src'].findall(content)
            links = self.patterns['html_link_href'].findall(content)
            includes = self.patterns['ng_include'].findall(content)
            
            for src in scripts + links + includes:
                resolved_path = self._resolve_path(src, file_path, all_files)
                if resolved_path:
                    dependencies.add(resolved_path)
        
        return list(dependencies)



    
    def _resolve_path(self, import_path: str, current_file: str, all_files: Dict[str, Dict]) -> Optional[str]:
        """Resolve a relative import path to an actual file in the project"""
        # Handle common JS extensions that might be omitted
        if not any(import_path.endswith(ext) for ext in ['.js', '.html', '.css', '.json']):
            import_path = f"{import_path}.js"
            
        # Remove any query parameters or hashes
        import_path = import_path.split('?')[0].split('#')[0]
        
        # Skip external dependencies (URLs, node_modules)
        if import_path.startswith(('http://', 'https://', '/')):
            return None
            
        # Get the directory of the current file
        current_dir = os.path.dirname(current_file)
        
        # Handle relative paths
        if import_path.startswith('./') or import_path.startswith('../'):
            full_path = os.path.normpath(os.path.join(current_dir, import_path))
        else:
            # Try to find the file in the project
            full_path = import_path
            
        # Check if the resolved path exists in our file list
        if full_path in all_files:
            return full_path
            
        # Try with different extensions
        for ext in ['.js', '.html', '.css', '.json']:
            if f"{full_path}{ext}" in all_files:
                return f"{full_path}{ext}"
                
        return None
    
    @staticmethod
    def parse_json_response(response: str):
        """
        Attempts to parse a JSON response, handling extra text, formatting issues, 
        and extracting JSON if necessary.
        
        :param response: The raw response string from LLM or another source.
        :return: Parsed JSON object or an error message.
        """
        try:
            # Strip leading/trailing whitespace
            response = response.content.strip()

            # Attempt direct JSON parsing
            return json.loads(response)

        except json.JSONDecodeError:
            # If parsing fails, try extracting JSON using regex
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass  # Continue to fallback handling

        # Fallback: Return raw response with an error message
        return {"error": "Failed to parse JSON", "raw_response": response}
    
    async def _analyze_with_ai(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send the file to AI for analysis with file-type specific prompts
        and get structured migration insights
        """
        try:
            file_type = file_info['file_type']
            content = file_info['content']
            file_name = file_info['file_name']
            
            # Select the appropriate prompt based on file type
            if file_type == 'js':
                prompt = get_js_prompt(file_name, content,self.instructions)
            elif file_type == 'html':
                prompt = get_html_prompt(file_name, content,self.instructions)
            elif file_type == 'css':
                prompt = get_css_prompt(file_name, content,self.instructions)
            elif file_type == 'json':
                prompt = get_json_prompt(file_name, content,self.instructions)
            else:
                prompt = get_default_prompt(file_name, content, file_type,self.instructions)
            
            # Call the LLM
            response = await asyncio.to_thread(
                self.llm.invoke, 
                prompt
            )
            
            # Parse the JSON response
            return self.parse_json_response(response)
            
        except Exception as e:
            # print(f"Error analyzing file {file_info['relative_path']}: {str(e)}")
            return {
                "analysis_error": str(e),
                "migration_insights": "Unable to analyze due to an error."
            }
            

        
    def _extract_injections(self, content: str) -> List[str]:
        """Extract Angular dependency injection names from the content"""
        injections = set()
        
        # Find all injection patterns
        matches = self.patterns['injection'].finditer(content)
        for match in matches:
            # Check both capture groups (array and function params)
            injection_list = match.group(1) or match.group(2)
            if injection_list:
                # Split by comma and clean up each injection name
                items = [
                    item.strip().strip('"\'') 
                    for item in injection_list.split(',')
                ]
                # Filter out Angular's built-in services
                filtered_items = [
                    item for item in items 
                    if not item.startswith('$') and item
                ]
                injections.update(filtered_items)
        
        return list(injections)
