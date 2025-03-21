import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

class ReactMigrationStructureGenerator:
    """
    Generates a recommended React project structure based on AngularJS project analysis.
    Uses LLM to suggest component organization, dependencies, and routing approach.
    """
    def __init__(self, analysis_file: str, llm_config, project_id: str):
        """
        Initialize the target structure generator
        Args:
            analysis_file: Path to the analysis JSON file
            llm_config: Configuration for the language model
            project_id: Unique identifier for the project
        """
        if not analysis_file or not project_id:
            raise ValueError("analysis_file and project_id are required")
            
        if not Path(analysis_file).exists():
            raise FileNotFoundError(f"Analysis file not found: {analysis_file}")
            
        self.analysis_file = analysis_file
        self.project_id = project_id
        self.llm = llm_config._langchain_llm
        self.output_dir = Path(analysis_file).parent
        self.output_file = str(self.output_dir / f"{project_id}_migration_structure.json")
        
        # Load analysis data
        self.analysis_data = self._load_analysis()
        if not self.analysis_data:
            raise ValueError("Invalid or empty analysis data")
            
        # Initialize migration structure
        self.migration_structure = self._init_migration_structure()

    def _init_migration_structure(self) -> Dict[str, Any]:
        """Initialize the migration structure with metadata"""
        return {
            "project_id": self.project_id,
            "components": [],
            "pages": [],
            "hooks": [],
            "services": [],
            "contexts": [],
            "routing": {
                "type": "react-router-dom",
                "routes": []
            },
            "metadata": {
                "generated_at": str(datetime.now()),
                "analysis_file": self.analysis_file,
                "source_files": list(self.analysis_data.keys()) if isinstance(self.analysis_data, dict) else []
            }
        }

    def _load_analysis(self) -> Optional[Dict[str, Any]]:
        """Load and validate the analysis data from JSON file"""
        try:
            with open(self.analysis_file, 'r') as f:
                data = json.load(f)
                
            # Validate analysis data structure
            if not isinstance(data, dict):
                print(f"Error: Analysis data must be a dictionary, got {type(data)}")
                return None
                
            return data
        except json.JSONDecodeError as e:
            print(f"Error decoding analysis file: {str(e)}")
            return None
        except Exception as e:
            print(f"Error loading analysis file: {str(e)}")
            return None

    async def generate_migration_structure(self) -> Dict[str, Any]:
        """Generate the recommended React migration structure"""
        try:
            print(f"Generating React migration structure for project {self.project_id}")
            print(f"Using analysis from: {self.analysis_file}")
            
            # 1. Identify Angular controllers and their views
            controller_view_pairs = self._identify_controller_view_pairs()
            if not controller_view_pairs:
                print("Warning: No controller-view pairs found")
            else:
                print(f"Found {len(controller_view_pairs)} potential React components")
            
            # 2. Process each pair to create component suggestions
            for i, (controller, view) in enumerate(controller_view_pairs):
                print(f"Processing component {i+1}/{len(controller_view_pairs)}")
                try:
                    component_structure = await self._generate_component_structure(controller, view)
                    if not component_structure:
                        print(f"Warning: Failed to generate component structure for {controller.get('file_name', 'unknown')}")
                        continue
                        
                    # Determine if this is likely a page or regular component
                    if self._is_likely_page(controller, view):
                        self.migration_structure["pages"].append(component_structure)
                    else:
                        self.migration_structure["components"].append(component_structure)
                except Exception as e:
                    print(f"Error processing component: {str(e)}")
                    continue
            
            # 3. Process services for potential hooks or contexts
            services = self._identify_services()
            if not services:
                print("Warning: No services found")
            else:
                print(f"Found {len(services)} services to process")
                
            for service in services:
                try:
                    service_structure = await self._generate_service_structure(service)
                    if not service_structure:
                        print(f"Warning: Failed to generate service structure for {service.get('file_name', 'unknown')}")
                        continue
                        
                    if service_structure["migrationType"] == "hook":
                        self.migration_structure["hooks"].append(service_structure)
                    elif service_structure["migrationType"] == "context":
                        self.migration_structure["contexts"].append(service_structure)
                    else:
                        self.migration_structure["services"].append(service_structure)
                except Exception as e:
                    print(f"Error processing service: {str(e)}")
                    continue
            
            # 4. Generate routing structure
            try:
                routing_structure = await self._generate_routing_structure()
                if routing_structure:
                    self.migration_structure["routing"] = routing_structure
            except Exception as e:
                print(f"Error generating routing structure: {str(e)}")
            
            # 5. Save the migration structure
            self._save_migration_structure()
            
            # 6. Add summary statistics
            self.migration_structure["statistics"] = {
                "total_components": len(self.migration_structure["components"]),
                "total_pages": len(self.migration_structure["pages"]),
                "total_hooks": len(self.migration_structure["hooks"]),
                "total_services": len(self.migration_structure["services"]),
                "total_contexts": len(self.migration_structure["contexts"]),
                "total_routes": len(self.migration_structure["routing"]["routes"])
            }
            
            print(f"Migration structure generation complete for project {self.project_id}")
            print(f"Results saved to {self.output_file}")
            print("Summary:")
            for key, value in self.migration_structure["statistics"].items():
                print(f"  {key}: {value}")
            
            return self.migration_structure
        except Exception as e:
            print(f"Error generating migration structure: {str(e)}")
            raise

    def _save_migration_structure(self) -> None:
        """Save the migration structure to a JSON file"""
        try:
            # Create output directory if it doesn't exist
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save with pretty printing for readability
            with open(self.output_file, 'w') as f:
                json.dump(self.migration_structure, f, indent=2)
                
            print(f"Migration structure saved to: {self.output_file}")
        except Exception as e:
            print(f"Error saving migration structure: {str(e)}")
            raise

    def _identify_controller_view_pairs(self) -> List[tuple]:
        """
        Identify potential controller-view pairs from the analysis
        Returns list of tuples: (controller_file_info, view_file_info)
        """
        try:
            controller_view_pairs = []
            js_files = {path: info for path, info in self.analysis_data.items() if path.endswith('.js')}
            html_files = {path: info for path, info in self.analysis_data.items() if path.endswith('.html')}
            
            # Match controllers with their views based on naming patterns and dependencies
            for js_path, js_info in js_files.items():
                # Skip non-controller files
                if 'controller' not in js_path.lower() and not any('controller' in dep.lower() for dep in js_info.get('dependencies', [])):
                    continue
                    
                # Look for matching view file
                js_basename = Path(js_path).stem
                potential_views = []
                
                # Check dependencies first
                for html_path, html_info in html_files.items():
                    if js_path in html_info.get('dependencies', []) or html_path in js_info.get('dependencies', []):
                        potential_views.append((html_path, html_info))
                
                # If no views found by dependencies, try naming patterns
                if not potential_views:
                    for html_path, html_info in html_files.items():
                        base_name = Path(html_path).stem
                        # Common naming patterns: controller.js -> view.html or something similar
                        if (js_basename.replace('Controller', '') in base_name or
                            base_name.replace('View', '') in js_basename or
                            base_name.replace('.view', '') in js_basename):
                            potential_views.append((html_path, html_info))
                
                # If we found views, add the pair
                for view_path, view_info in potential_views:
                    controller_view_pairs.append((js_info, view_info))
            
            return controller_view_pairs
        except Exception as e:
            print(f"Error identifying controller-view pairs: {str(e)}")
            return []

    def _identify_services(self) -> List[Dict[str, Any]]:
        """Identify Angular services that should be migrated to React services or hooks"""
        try:
            services = []
            
            for path, info in self.analysis_data.items():
                if not path.endswith('.js'):
                    continue
                    
                # Look for service, factory, or provider in the description or path
                description = info.get('description', '').lower()
                if ('service' in description or 'factory' in description or 'provider' in description or
                    'service' in path.lower() or 'factory' in path.lower() or 'provider' in path.lower()):
                    services.append(info)
            
            return services
        except Exception as e:
            print(f"Error identifying services: {str(e)}")
            return []

    def _is_likely_page(self, controller_info: Dict[str, Any], view_info: Dict[str, Any]) -> bool:
        """Determine if this component is likely a page (vs a regular component)"""
        try:
            # Check if it's involved in routing
            controller_routing = controller_info.get('routing_info', '').lower()
            view_routing = view_info.get('routing_info', '').lower()
            
            if ('route' in controller_routing or 'state' in controller_routing or
                'ui-view' in view_routing or 'ng-view' in view_routing or
                'not involved in routing' not in controller_routing):
                return True
                
            # Check naming patterns
            controller_name = controller_info.get('file_name', '').lower()
            view_name = view_info.get('file_name', '').lower()
            
            page_indicators = ['page', 'view', 'screen', 'dashboard', 'home', 'login', 'detail']
            for indicator in page_indicators:
                if indicator in controller_name or indicator in view_name:
                    return True
                    
            return False
        except Exception as e:
            print(f"Error determining if component is a page: {str(e)}")
            return False

    async def _generate_component_structure(self, controller_info: Dict[str, Any], view_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate React component structure from Angular controller and view"""
        try:
            controller_path = controller_info.get('relative_path', '')
            view_path = view_info.get('relative_path', '')
            
            # Create a prompt for the LLM to suggest React component structure
            prompt = f"""
            I'm migrating an AngularJS application to React. I need to convert an AngularJS controller and view pair to a React component.

            Controller file: {controller_path}
            Controller description: {controller_info.get('description', 'No description available')}
            Controller routing info: {controller_info.get('routing_info', 'No routing info available')}
            Controller dependencies: {controller_info.get('dependencies', [])}

            View file: {view_path}
            View description: {view_info.get('description', 'No description available')}
            View routing info: {view_info.get('routing_info', 'No routing info available')}
            
            Based on this information, provide a JSON structure describing the appropriate React component for migration:
            
            ```json
            {{
              "name": "ComponentName", // Suggested React component name (PascalCase)
              "type": "functional", // functional or class
              "sourceFiles": [], // List of original Angular files this component replaces
              "dependencies": [], // Recommended React dependencies (useState, useEffect, etc)
              "props": [], // Suggested props the component should accept
              "stateItems": [], // Suggested state items the component should maintain
              "description": "", // Brief description of what the component does
              "routeInfo": {{
                "isRouted": false, // Whether this should be a routed component
                "potentialRoute": "" // Potential route path if applicable
              }}
            }}
            ```
            
            Return ONLY the JSON object without any additional explanation.
            """
            
            # Call the LLM
            response = await asyncio.to_thread(
                self.llm.predict, 
                prompt
            )
            
            # Extract JSON from the response
            try:
                # Find JSON between triple backticks if present
                json_str = response
                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0]
                elif "```" in response:
                    json_str = response.split("```")[1].split("```")[0]
                    
                # Parse JSON
                component_structure = json.loads(json_str)
                
                # Add source information
                component_structure["sourceFiles"] = [
                    controller_path,
                    view_path
                ]
                
                return component_structure
            except json.JSONDecodeError as e:
                print(f"Error parsing LLM response as JSON: {str(e)}")
                return None
                
        except Exception as e:
            print(f"Error generating component structure: {str(e)}")
            return None

    async def _generate_service_structure(self, service_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate React service/hook structure from Angular service"""
        try:
            service_path = service_info.get('relative_path', '')
            
            # Create a prompt for the LLM
            prompt = f"""
            I'm migrating an AngularJS service to React. Help me determine if this should be a custom hook, context, or regular service.

            Service file: {service_path}
            Service description: {service_info.get('description', 'No description available')}
            Service dependencies: {service_info.get('dependencies', [])}
            
            Based on this information, provide a JSON structure describing how to migrate this service:
            
            ```json
            {{
              "name": "serviceName", // Suggested name (camelCase for hooks, PascalCase for contexts)
              "migrationType": "hook", // One of: hook, context, or service
              "sourceFiles": [], // List of original Angular files this replaces
              "dependencies": [], // Required React dependencies
              "description": "", // Brief description of what it does
              "stateItems": [], // State managed by this hook/context/service
              "methods": [] // Methods to be exposed
            }}
            ```
            
            Return ONLY the JSON object without any additional explanation.
            """
            
            # Call the LLM
            response = await asyncio.to_thread(
                self.llm.predict, 
                prompt
            )
            
            # Extract JSON from the response
            try:
                # Find JSON between triple backticks if present
                json_str = response
                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0]
                elif "```" in response:
                    json_str = response.split("```")[1].split("```")[0]
                    
                # Parse JSON
                service_structure = json.loads(json_str)
                
                # Add source information
                service_structure["sourceFiles"] = [service_path]
                
                return service_structure
            except json.JSONDecodeError as e:
                print(f"Error parsing LLM response as JSON: {str(e)}")
                return None
                
        except Exception as e:
            print(f"Error generating service structure: {str(e)}")
            return None

    async def _generate_routing_structure(self) -> Optional[Dict[str, Any]]:
        """Generate React routing structure from Angular routes"""
        try:
            # Create a prompt for the LLM
            prompt = f"""
            I'm migrating an AngularJS application to React. Help me generate a routing structure.

            Here are the pages we've identified:
            {json.dumps([page for page in self.migration_structure["pages"]], indent=2)}
            
            Based on this information, provide a JSON structure for React Router setup:
            
            ```json
            {{
              "type": "react-router-dom",
              "version": "6.x",
              "structure": "centralized", // centralized or distributed
              "routes": [
                {{
                  "path": "/path",
                  "component": "ComponentName",
                  "exact": true,
                  "children": []
                }}
              ],
              "configuration": {{
                "basename": "",
                "hashType": false,
                "features": []
              }}
            }}
            ```
            
            Return ONLY the JSON object without any additional explanation.
            """
            
            # Call the LLM
            response = await asyncio.to_thread(
                self.llm.predict, 
                prompt
            )
            
            # Extract JSON from the response
            try:
                # Find JSON between triple backticks if present
                json_str = response
                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0]
                elif "```" in response:
                    json_str = response.split("```")[1].split("```")[0]
                    
                # Parse JSON
                routing_structure = json.loads(json_str)
                return routing_structure
            except json.JSONDecodeError as e:
                print(f"Error parsing LLM response as JSON: {str(e)}")
                return None
                
        except Exception as e:
            print(f"Error generating routing structure: {str(e)}")
            return None

    def _generate_component_name(self, controller_path: str, view_path: str) -> str:
        """Generate a component name from controller and view paths"""
        # Get base names without extensions
        controller_base = Path(controller_path).stem
        view_base = Path(view_path).stem
        
        # Clean up common suffixes
        name = controller_base.replace('Controller', '').replace('Ctrl', '')
        
        # Convert to PascalCase
        import re
        words = re.findall(r'[A-Z][a-z]*|[a-z]+', name)
        pascal_case = ''.join(word.capitalize() for word in words)
        
        return f"{pascal_case}Component"

    def _generate_route_path(self, file_path: str) -> str:
        """Generate a potential route path from a file path"""
        # Extract file name without extension
        file_name = Path(file_path).stem
        
        # Clean up common suffixes
        route_name = file_name.replace('Controller', '').replace('Ctrl', '').replace('View', '')
        
        # Convert to kebab-case
        import re
        words = re.findall(r'[A-Z][a-z]*|[a-z]+', route_name)
        kebab_case = '-'.join(word.lower() for word in words)
        
        return f"/{kebab_case}"

async def main():
    # Get analysis file from command line or use default
    import sys
    from config.llm_config import llm_config
    
    analysis_file = sys.argv[1] if len(sys.argv) > 1 else "analysis.json"
    
    # Generate migration structure
    generator = ReactMigrationStructureGenerator(analysis_file, llm_config, "my_project")
    migration_structure = await generator.generate_migration_structure()
    
    # Print summary
    print("\nMigration Structure Summary:")
    print(f"Components: {len(migration_structure['components'])}")
    print(f"Pages: {len(migration_structure['pages'])}")
    print(f"Hooks: {len(migration_structure['hooks'])}")
    print(f"Services: {len(migration_structure['services'])}")
    print(f"Contexts: {len(migration_structure['contexts'])}")
    print(f"Routes: {len(migration_structure['routing']['routes'])}")
    print(f"\nFull migration structure saved to: {generator.output_file}")

if __name__ == "__main__":
    asyncio.run(main())