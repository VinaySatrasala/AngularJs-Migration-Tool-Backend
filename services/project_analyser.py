import os
import json
import re
import asyncio
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from concurrent.futures import ThreadPoolExecutor

# Import your LLM configuration
from config.llm_config import llm_config

class AngularProjectAnalyzer:
    """
    Analyzer for AngularJS projects that creates a structured analysis of the codebase.
    Uses LLMs to generate descriptions and understand relationships between files.
    """
    def __init__(self, project_path: str, output_file: str = "analysis.json"):
        self.project_path = Path(project_path)
        self.output_file = output_file
        self.file_extensions = {'.js', '.html', '.css', '.json', '.md'}
        self.analysis_results = {}
        self.llm = llm_config._langchain_llm
        self.embedding_model = llm_config._langchain_embedding
        
        # Regex patterns for identifying dependencies
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
            'injection': re.compile(r'\$inject\s*=\s*\[(.*?)\]|\bfunction\s*\((.*?)\)')
        }

    async def analyze_project(self) -> Dict[str, Any]:
        """Main method to analyze the entire AngularJS project"""
        print(f"Starting analysis of project at: {self.project_path}")
        
        # 1. Gather all relevant files
        all_files = self._gather_files()
        print(f"Found {len(all_files)} files to analyze")
        
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
        
        # 4. Use LLM to generate descriptions for each file
        for file_path, info in file_info_results.items():
            description = await self._generate_file_description(info)
            info['description'] = description
        
        # 5. Save results to JSON file
        self.analysis_results = file_info_results
        self._save_analysis()
        
        print(f"Analysis complete. Results saved to {self.output_file}")
        return self.analysis_results

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
            
            # Extract Angular-specific information based on file type
            angular_components = self._extract_angular_components(content, file_type)
            
            return {
                "file_name": file_path.name,
                "relative_path": relative_path,
                "file_type": file_type,
                "size_bytes": file_path.stat().st_size,
                "content": content,
                "angular_components": angular_components,
                "dependencies": [],  # Will be filled later
                "description": ""    # Will be filled by LLM
            }
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
            return {
                "file_name": file_path.name,
                "relative_path": str(file_path.relative_to(self.project_path)),
                "file_type": file_path.suffix[1:],
                "error": str(e),
                "content": "",
                "angular_components": [],
                "dependencies": [],
                "description": "Error processing file"
            }

    def _extract_angular_components(self, content: str, file_type: str) -> Dict[str, List[str]]:
        """Extract Angular-specific components from file content"""
        components = {
            "modules": [],
            "controllers": [],
            "services": [],
            "directives": [],
            "components": []
        }
        
        if file_type != 'js':
            return components
            
        # Extract modules
        modules = self.patterns['angular_module'].findall(content)
        components["modules"] = list(set(modules))
        
        # Extract controllers
        controllers = self.patterns['angular_controller'].findall(content)
        components["controllers"] = list(set(controllers))
        
        # Extract services (factory, service, provider)
        services = self.patterns['angular_service'].findall(content)
        components["services"] = list(set(services))
        
        # Extract directives
        directives = self.patterns['angular_directive'].findall(content)
        components["directives"] = list(set(directives))
        
        # Extract components (Angular 1.5+)
        component = self.patterns['angular_component'].findall(content)
        components["components"] = list(set(component))
        
        return components

    def _find_dependencies(self, content: str, file_path: str, all_files: Dict[str, Dict]) -> List[str]:
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
                        
                    angular_components = other_info.get('angular_components', {})
                    for component_type in ['services', 'directives', 'components']:
                        if injection in angular_components.get(component_type, []):
                            dependencies.add(other_path)
        
        # HTML file dependencies
        elif file_type == 'html':
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

    def _extract_injections(self, content: str) -> List[str]:
        """Extract Angular dependency injection names from JS content"""
        injections = []
        
        # Look for explicit $inject arrays
        inject_matches = self.patterns['injection'].findall(content)
        
        for match_group in inject_matches:
            for match in match_group:
                if not match:
                    continue
                    
                # Clean up the match
                params = re.findall(r'[\'"]([^\'"]+)[\'"]', match)
                if not params:
                    # Try to extract function parameters
                    params = [p.strip() for p in match.split(',')]
                    
                for param in params:
                    # Skip built-in services that start with $ and standard service names
                    if (param and not param.startswith('$') and 
                        param not in ['scope', 'rootScope', 'window', 'document']):
                        injections.append(param)
        
        return list(set(injections))

    async def _generate_file_description(self, file_info: Dict[str, Any]) -> str:
        """Generate a description for a file using LLM"""
        try:
            file_type = file_info['file_type']
            content = file_info['content']
            file_name = file_info['file_name']
            
            # Truncate content if too long
            if len(content) > 8000:
                content = content[:4000] + "\n...(content truncated)...\n" + content[-4000:]
            
            # Create prompt based on file type
            if file_type == 'js':
                prompt = f"""
                Analyze this AngularJS JavaScript file '{file_name}'. 
                Provide a concise description (max 2 sentences) explaining what this file does.
                Include the main purpose, any Angular components defined (modules, controllers, services, etc.), 
                and its role in the application architecture.

                File content:
                ```javascript
                {content}
                ```
                
                Description:
                """
            elif file_type == 'html':
                prompt = f"""
                Analyze this AngularJS HTML template file '{file_name}'.
                Provide a concise description (max 2 sentences) explaining what this view template contains.
                Include main UI elements, directives used, and which part of the application it likely represents.

                File content:
                ```html
                {content}
                ```
                
                Description:
                """
            else:
                prompt = f"""
                Analyze this {file_type} file '{file_name}' from an AngularJS project.
                Provide a concise description (max 2 sentences) explaining what this file does.
                Include its purpose and role in the application.

                File content:
                ```
                {content}
                ```
                
                Description:
                """
            
            # Call the LLM
            response = await asyncio.to_thread(
                self.llm.predict, 
                prompt
            )
            
            # Clean up the response
            description = response.strip()
            
            # Limit to max 2 sentences if needed
            sentences = re.split(r'(?<=[.!?])\s+', description)
            if len(sentences) > 2:
                description = ' '.join(sentences[:2])
                
            return description
            
        except Exception as e:
            print(f"Error generating description for {file_info['relative_path']}: {str(e)}")
            return "Unable to generate description due to an error."

    def _save_analysis(self) -> None:
        """Save analysis results to JSON file"""
        # Create analysis directory if it doesn't exist
        analysis_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'analysis')
        os.makedirs(analysis_dir, exist_ok=True)
        
        # Generate a unique project ID based on the project path
        project_id = os.path.basename(self.project_path)
        if not project_id:  # If project_path ends with a separator
            project_id = os.path.basename(os.path.dirname(self.project_path))
            
        # Create the analysis file path
        analysis_file = os.path.join(analysis_dir, f"{project_id}_analysis.json")
        
        # Remove actual file content from output to reduce size
        output_results = {}
        
        for file_path, info in self.analysis_results.items():
            output_info = info.copy()
            
            # Store a truncated version of content or remove entirely
            content_preview = info['content'][:200] + "..." if len(info['content']) > 200 else info['content']
            output_info['content_preview'] = content_preview
            output_info.pop('content', None)
            
            output_results[file_path] = output_info
            
        with open(analysis_file, 'w') as f:
            json.dump(output_results, f, indent=2)
            
        # Update the output file path
        self.output_file = analysis_file

async def main():
    # Get project path from command line or use default
    import sys
    project_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_file = sys.argv[2] if len(sys.argv) > 2 else "analysis.json"
    
    analyzer = AngularProjectAnalyzer(project_path, output_file)
    results = await analyzer.analyze_project()
    
    # Print summary
    total_files = len(results)
    file_types = {}
    component_counts = {
        "modules": 0,
        "controllers": 0,
        "services": 0,
        "directives": 0,
        "components": 0
    }
    
    for file_info in results.values():
        file_type = file_info['file_type']
        file_types[file_type] = file_types.get(file_type, 0) + 1
        
        for component_type, components in file_info.get('angular_components', {}).items():
            component_counts[component_type] += len(components)
    
    print(f"\nProject Analysis Summary:")
    print(f"Total files analyzed: {total_files}")
    print(f"File types distribution: {file_types}")
    print(f"Angular components found:")
    for component_type, count in component_counts.items():
        print(f"  - {component_type}: {count}")
    print(f"\nFull analysis saved to: {output_file}")

if __name__ == "__main__":
    asyncio.run(main())