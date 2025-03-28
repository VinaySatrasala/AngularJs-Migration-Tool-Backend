from typing import Any, Dict  

def _build_generation_prompt(source_content: str, file_info: Dict[str, Any]) -> str:
    """
    Build a structured prompt for generating a React file based on AngularJS source content.

    Args:
        source_content: Source content for the file from the AngularJS project.
        file_info: Metadata about the file to be generated, including description, dependencies, and migration suggestions.

    Returns:
        A well-structured prompt string to guide the AI in generating an optimized React file.
    """
    
    # Base prompt template
    base_prompt = f"""
    You are a React migration assistant. Convert the given AngularJS file into an optimized React {file_info['file_type']} file while following best practices.

    ### **File Details:**
    - **Target Path:** `{file_info['relative_path']}`
    - **File Type:** `{file_info['file_type']}`
    - **Description:** {file_info.get('description', 'No description provided.')}
    - **Dependencies:** {', '.join(file_info.get('dependencies', [])) if file_info.get('dependencies') else 'None'}
    - **Migration Suggestions:** {file_info.get('migration_suggestions', 'No migration instructions provided.')}

    {f"### **Source Content:**\n```\n{source_content}\n```" if source_content else "No source content available."}

    ## **Generation Guidelines:**
    1. **Follow Modern React Practices:** Use functional components, hooks, and ES6+ syntax.
    2. **Preserve Component Structure:** Maintain component purpose and functionality while adapting it to React conventions.
    3. **Implement Required Dependencies:** Ensure all necessary dependencies (React libraries, local imports, and third-party modules) are correctly included.
    4. **Maintain Routing Behavior:** If the component interacts with routing, use `react-router-dom`, but **handle all routing logic in `App.js`** rather than defining it in each component.
    5. **Optimize Code Structure:** Ensure code clarity, modularization, and maintainability.

    ## **CSS & Styling Rules:**
    - **DO NOT** generate inline styles or `styled-components` if a CSS file exists for the component or if global styles handle the design.
    - **USE** existing CSS classes instead of generating new styles unless absolutely necessary.
    - **PRESERVE** the CSS structure from the AngularJS project—do not modify styles unless required for React compatibility.
    - **AVOID** unnecessary CSS files—if a CSS file was not present in the original AngularJS structure, do not generate one.

    ## **Preserving Data & Logic:**
    - **DO NOT** transform static data into API calls—if the AngularJS code had hardcoded values, keep them hardcoded in React.
    - **DO NOT** introduce additional state management solutions unless required.
    - **KEEP** the logic consistent with the original implementation unless changes are necessary for React migration.

    ## **Return Instructions:**
    - Generate **only** the complete and functional React `{file_info['file_type']}` file.
    - Do **not** include explanations, extra comments, or additional notes—only return the code.
    ## **Additional Notes:**
    - &lt;Route&gt; uses element=&lt;YourComponent /&gt; instead of component=YourComponent.
    - Replace $routeProvider with react-router-dom's <Routes> and <Route>.
    - Define routes inside <Routes> using <Route path="..." element=Component />.
    - Move navigation logic to useNavigate() instead of $location.path().
    - Ensure all route components are function components.
    - Include BrowserRouter or MemoryRouter at the top level."
    - DO NOT use generic import paths like 'path/to/...'. Always use the correct relative path from the project structure.
    - NEVER create a new file or assume a missing dependency—omit it from the imports instead.

    """

    return base_prompt
