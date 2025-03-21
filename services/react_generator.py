import os
import json
import asyncio
from typing import Dict, List, Any
from pathlib import Path

class ReactComponentGenerator:
    """
    Generates React component files based on the migration structure.
    Uses LLM to transform AngularJS code into React components.
    """
    def __init__(self, migration_file: str, analysis_file: str, output_dir: str, llm_config):
        self.migration_file = migration_file
        self.analysis_file = analysis_file
        self.output_dir = Path(output_dir)
        self.llm = llm_config._langchain_llm
        self.migration_data = self._load_migration_data()
        self.analysis_data = self._load_analysis_data()
        
    def _load_migration_data(self) -> Dict[str, Any]:
        """Load the migration structure from JSON file"""
        with open(self.migration_file, 'r') as f:
            return json.load(f)
    
    def _load_analysis_data(self) -> Dict[str, Any]:
        """Load the analysis data from JSON file"""
        with open(self.analysis_file, 'r') as f:
            return json.load(f)
    
    async def generate_project(self) -> None:
        """Generate all React components and files for the project"""
        print(f"Generating React project based on migration structure in: {self.migration_file}")
        
        # Create output directory structure
        self._create_directory_structure()
        
        # Generate components
        await self._generate_components()
        
        # Generate pages
        await self._generate_pages()
        
        # Generate hooks and services
        await self._generate_hooks_and_services()
        
        # Generate contexts
        await self._generate_contexts()
        
        # Generate routing
        await self._generate_routing()
        
        # Generate project.js
        await self._generate_project_component()
        
        print(f"React project generation complete. Files saved to {self.output_dir}")
    
    def _create_directory_structure(self) -> None:
        """Create the directory structure for the React project"""
        directories = [
            self.output_dir,
            self.output_dir / "components",
            self.output_dir / "pages",
            self.output_dir / "hooks",
            self.output_dir / "services",
            self.output_dir / "contexts",
            self.output_dir / "utils",
            self.output_dir / "routes"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
        print(f"Created directory structure in {self.output_dir}")
    
    async def _generate_components(self) -> None:
        """Generate React component files"""
        components = self.migration_data.get("components", [])
        
        for i, component_info in enumerate(components):
            print(f"Generating component {i+1}/{len(components)}: {component_info.get('name', 'Unnamed')}")
            await self._generate_component_file(component_info, "components")
    
    async def _generate_pages(self) -> None:
        """Generate React page component files"""
        pages = self.migration_data.get("pages", [])
        
        for i, page_info in enumerate(pages):
            print(f"Generating page {i+1}/{len(pages)}: {page_info.get('name', 'Unnamed')}")
            await self._generate_component_file(page_info, "pages")
    
    async def _generate_hooks_and_services(self) -> None:
        """Generate React hooks and services"""
        hooks = self.migration_data.get("hooks", [])
        services = self.migration_data.get("services", [])
        
        for i, hook_info in enumerate(hooks):
            print(f"Generating hook {i+1}/{len(hooks)}: {hook_info.get('name', 'Unnamed')}")
            await self._generate_hook_file(hook_info)
            
        for i, service_info in enumerate(services):
            print(f"Generating service {i+1}/{len(services)}: {service_info.get('name', 'Unnamed')}")
            await self._generate_service_file(service_info)
    
    async def _generate_contexts(self) -> None:
        """Generate React context files"""
        contexts = self.migration_data.get("contexts", [])
        
        for i, context_info in enumerate(contexts):
            print(f"Generating context {i+1}/{len(contexts)}: {context_info.get('name', 'Unnamed')}")
            await self._generate_context_file(context_info)
    
    async def _generate_routing(self) -> None:
        """Generate React routing files"""
        routing_info = self.migration_data.get("routing", {})
        
        if not routing_info:
            return
            
        print("Generating routing files")
        
        # Create the main routes file
        router_file = self.output_dir / "routes" / "index.js"
        router_content = await self._generate_router_content(routing_info)
        
        with open(router_file, 'w') as f:
            f.write(router_content)
            
        # If using centralized routing, create AppRouter component
        if routing_info.get("structure", "centralized") == "centralized":
            app_router_file = self.output_dir / "routes" / "AppRouter.js"
            app_router_content = await self._generate_app_router_content(routing_info)
            
            with open(app_router_file, 'w') as f:
                f.write(app_router_content)
    
    async def _generate_project_component(self) -> None:
        """Generate the main Project.js component"""
        print("Generating Project.js component")
        
        # Find dependencies based on controller-view relationships
        controller_deps = []
        view_deps = []
        
        # Find components that might be part of Project
        project_related = []
        for component in self.migration_data.get("components", []) + self.migration_data.get("pages", []):
            name = component.get("name", "")
            source_files = component.get("sourceFiles", [])
            
            for source in source_files:
                base_name = Path(source).name.lower()
                if "project" in base_name:
                    project_related.append(component)
                    break
        
        # Get routing info
        routing_info = self.migration_data.get("routing", {})
        
        # Generate the Project.js component
        project_file = self.output_dir / "Project.js"
        project_content = await self._generate_project_js_content(project_related, routing_info)
        
        with open(project_file, 'w') as f:
            f.write(project_content)
            
        # Generate index.js to import and export Project component
        index_file = self.output_dir / "index.js"
        index_content = """import Project from './Project';

export default Project;
"""
        with open(index_file, 'w') as f:
            f.write(index_content)
    
    async def _generate_component_file(self, component_info: Dict[str, Any], folder: str) -> None:
        """Generate a React component file"""
        name = component_info.get("name", "UnnamedComponent")
        source_files = component_info.get("sourceFiles", [])
        
        # Get original source contents from analysis data
        source_contents = []
        for source_path in source_files:
            if source_path in self.analysis_data:
                file_info = self.analysis_data[source_path]
                if "content" in file_info:
                    source_contents.append({
                        "path": source_path,
                        "content": file_info["content"],
                        "description": file_info.get("description", "")
                    })
        
        # Generate React component
        component_content = await self._generate_react_component(component_info, source_contents)
        
        # Write to file
        component_file = self.output_dir / folder / f"{name}.js"
        with open(component_file, 'w') as f:
            f.write(component_content)
    
    async def _generate_hook_file(self, hook_info: Dict[str, Any]) -> None:
        """Generate a React hook file"""
        name = hook_info.get("name", "useUnnamedHook")
        source_files = hook_info.get("sourceFiles", [])
        
        # Get original source contents from analysis data
        source_contents = []
        for source_path in source_files:
            if source_path in self.analysis_data:
                file_info = self.analysis_data[source_path]
                if "content" in file_info:
                    source_contents.append({
                        "path": source_path,
                        "content": file_info["content"],
                        "description": file_info.get("description", "")
                    })
        
        # Generate React hook
        hook_content = await self._generate_react_hook(hook_info, source_contents)
        
        # Write to file
        hook_file = self.output_dir / "hooks" / f"{name}.js"
        with open(hook_file, 'w') as f:
            f.write(hook_content)
    
    async def _generate_service_file(self, service_info: Dict[str, Any]) -> None:
        """Generate a React service file"""
        name = service_info.get("name", "UnnamedService")
        source_files = service_info.get("sourceFiles", [])
        
        # Get original source contents from analysis data
        source_contents = []
        for source_path in source_files:
            if source_path in self.analysis_data:
                file_info = self.analysis_data[source_path]
                if "content" in file_info:
                    source_contents.append({
                        "path": source_path,
                        "content": file_info["content"],
                        "description": file_info.get("description", "")
                    })
        
        # Generate React service
        service_content = await self._generate_react_service(service_info, source_contents)
        
        # Write to file
        service_file = self.output_dir / "services" / f"{name}.js"
        with open(service_file, 'w') as f:
            f.write(service_content)
    
    async def _generate_context_file(self, context_info: Dict[str, Any]) -> None:
        """Generate a React context file"""
        name = context_info.get("name", "UnnamedContext")
        source_files = context_info.get("sourceFiles", [])
        
        # Get original source contents from analysis data
        source_contents = []
        for source_path in source_files:
            if source_path in self.analysis_data:
                file_info = self.analysis_data[source_path]
                if "content" in file_info:
                    source_contents.append({
                        "path": source_path,
                        "content": file_info["content"],
                        "description": file_info.get("description", "")
                    })
        
        # Generate React context
        context_content = await self._generate_react_context(context_info, source_contents)
        
        # Write to file
        context_file = self.output_dir / "contexts" / f"{name}.js"
        with open(context_file, 'w') as f:
            f.write(context_content)
    
    # ...existing code...
    async def _generate_react_component(self, component_info: Dict[str, Any], source_contents: List[Dict[str, Any]]) -> str:
        """Generate a React component from Angular sources"""
        name = component_info.get("name", "UnnamedComponent")
        component_type = component_info.get("type", "functional")
        dependencies = component_info.get("dependencies", [])
        props = component_info.get("props", [])
        state_items = component_info.get("stateItems", [])
        description = component_info.get("description", "")
        route_info = component_info.get("routeInfo", {})
        
        # Create source content snippets for context
        source_content_snippets = []
        for source in source_contents:
            snippet = f"File: {source['path']}\n{source['content'][:500]}..."
            source_content_snippets.append(snippet)

        # Create prompt for the LLM
        prompt = f"""
        Convert this AngularJS component to a React component.
        Component name: {name}
        Type: {component_type}
        Description: {description}
        
        Original AngularJS source:
        {'\n'.join(source_content_snippets)}
        
        Dependencies to import: {', '.join(dependencies)}
        Props to include: {', '.join(props)}
        State items: {', '.join(state_items)}
        Routing information: {json.dumps(route_info, indent=2)}
        
        Generate a modern React component using:
        - Functional component with hooks
        - ES6+ syntax
        - Proper TypeScript types
        - React Router v6 if routing is needed
        - Clean code practices
        """

        # Generate React component using LLM
        response = await self.llm.agenerate([prompt])
        component_code = response.generations[0].text.strip()
        
        return component_code

    async def _generate_react_hook(self, hook_info: Dict[str, Any], source_contents: List[Dict[str, Any]]) -> str:
        """Generate a React hook from Angular service/factory"""
        name = hook_info.get("name", "useUnnamedHook")
        dependencies = hook_info.get("dependencies", [])
        state_items = hook_info.get("stateItems", [])
        description = hook_info.get("description", "")

        # Create source snippets
        source_content_snippets = []
        for source in source_contents:
            snippet = f"File: {source['path']}\n{source['content'][:500]}..."
            source_content_snippets.append(snippet)

        prompt = f"""
        Convert this AngularJS service/factory to a React hook.
        Hook name: {name}
        Description: {description}
        
        Original AngularJS source:
        {'\n'.join(source_content_snippets)}
        
        Dependencies to import: {', '.join(dependencies)}
        State items to manage: {', '.join(state_items)}
        
        Generate a modern React hook using:
        - Modern hooks practices
        - ES6+ syntax
        - TypeScript types
        - Clean code practices
        """

        response = await self.llm.agenerate([prompt])
        hook_code = response.generations[0].text.strip()
        
        return hook_code

    async def _generate_react_service(self, service_info: Dict[str, Any], source_contents: List[Dict[str, Any]]) -> str:
        """Generate a React service from Angular service"""
        name = service_info.get("name", "UnnamedService")
        dependencies = service_info.get("dependencies", [])
        methods = service_info.get("methods", [])
        description = service_info.get("description", "")

        source_content_snippets = []
        for source in source_contents:
            snippet = f"File: {source['path']}\n{source['content'][:500]}..."
            source_content_snippets.append(snippet)

        prompt = f"""
        Convert this AngularJS service to a React/TypeScript service class.
        Service name: {name}
        Description: {description}
        
        Original AngularJS source:
        {'\n'.join(source_content_snippets)}
        
        Dependencies to import: {', '.join(dependencies)}
        Methods to implement: {', '.join(methods)}
        
        Generate a modern service class using:
        - ES6+ class syntax
        - TypeScript types
        - Async/await for async operations
        - Clean code practices
        """

        response = await self.llm.agenerate([prompt])
        service_code = response.generations[0].text.strip()
        
        return service_code

    async def _generate_react_context(self, context_info: Dict[str, Any], source_contents: List[Dict[str, Any]]) -> str:
        """Generate a React context from Angular scope/service"""
        name = context_info.get("name", "UnnamedContext")
        state_items = context_info.get("stateItems", [])
        methods = context_info.get("methods", [])
        description = context_info.get("description", "")

        source_content_snippets = []
        for source in source_contents:
            snippet = f"File: {source['path']}\n{source['content'][:500]}..."
            source_content_snippets.append(snippet)

        prompt = f"""
        Create a React context from this AngularJS scope/service.
        Context name: {name}
        Description: {description}
        
        Original AngularJS source:
        {'\n'.join(source_content_snippets)}
        
        State items to manage: {', '.join(state_items)}
        Methods to implement: {', '.join(methods)}
        
        Generate a modern React context using:
        - Context API with TypeScript
        - Custom provider component
        - useContext hook
        - Clean code practices
        """

        response = await self.llm.agenerate([prompt])
        context_code = response.generations[0].text.strip()
        
        return context_code

    async def _generate_router_content(self, routing_info: Dict[str, Any]) -> str:
        """Generate React Router configuration"""
        routes = routing_info.get("routes", [])
        structure = routing_info.get("structure", "centralized")
        
        prompt = f"""
        Create React Router (v6) configuration from these routes:
        {json.dumps(routes, indent=2)}
        
        Routing structure: {structure}
        
        Generate modern React Router setup using:
        - React Router v6 syntax
        - TypeScript types
        - Lazy loading where appropriate
        - Clean code practices
        """

        response = await self.llm.agenerate([prompt])
        router_code = response.generations[0].text.strip()
        
        return router_code

    async def _generate_app_router_content(self, routing_info: Dict[str, Any]) -> str:
        """Generate main AppRouter component"""
        routes = routing_info.get("routes", [])
        
        prompt = f"""
        Create React Router (v6) AppRouter component from these routes:
        {json.dumps(routes, indent=2)}
        
        Generate AppRouter component using:
        - React Router v6 components
        - TypeScript types
        - Layout components if needed
        - Clean code practices
        """

        response = await self.llm.agenerate([prompt])
        app_router_code = response.generations[0].text.strip()
        
        return app_router_code

    async def _generate_project_js_content(self, project_related: List[Dict[str, Any]], routing_info: Dict[str, Any]) -> str:
        """Generate main Project.js component"""
        prompt = f"""
        Create main Project.js React component:
        Related components: {json.dumps(project_related, indent=2)}
        Routing setup: {json.dumps(routing_info, indent=2)}
        
        Generate Project component using:
        - Modern React practices
        - TypeScript types
        - Router integration
        - Context providers if needed
        - Clean code practices
        """

        response = await self.llm.agenerate([prompt])
        project_code = response.generations[0].text.strip()
        
        return project_code