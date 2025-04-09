def get_specialized_prompt(file_types, angular_code):
    """Generate specialized prompts based on file type combinations"""
    
    # Sort file types to ensure consistent handling of combinations
    file_types.sort()
    file_types_key = "-".join(file_types)
    
    # Base prompt parts that are common to all combinations
    base_intro = """
    You are a senior software engineer with extensive expertise in exact AngularJS to React conversions.
    Convert the following AngularJS code to React with 100% functional equivalence and feature parity.
    
    CRITICAL REQUIREMENTS:
    - DO NOT include comments in the output
    - Convert EVERY function with proper React equivalents
    - Maintain exact business logic, variable names, and logic flow
    - Provide ALL necessary imports at the top of the file
    - Return a complete, production-ready React component that can be used immediately
    - ALWAYS include a proper export statement (default or named)
    - Ensure the component renders and operates correctly without additional modifications
    - If multiple components are needed, include them all in a single file with appropriate exports
    """
    
    base_structure = """
    1. STRUCTURE CONVERSION:
       - Convert AngularJS controllers to React functional components
       - Convert Angular modules/services to custom hooks
       - Transform directive attributes to equivalent React props
       - Ensure all dependencies are properly imported
       - Include a proper export statement for every component (default or named)
    """
    
    base_state = """
    2. STATE MANAGEMENT:
       - Convert $scope variables → useState hooks with identical variable names
       - Convert $rootScope → React Context where appropriate
       - Use useRef for DOM references
       - Convert service state → custom hooks with useState
    """
    
    base_lifecycle = """
    3. LIFECYCLE & EFFECTS:
       - $onInit → useEffect with empty dependency array
       - $onDestroy → useEffect return function (cleanup)
       - $onChanges → useEffect with dependencies
       - $watch → useEffect with proper dependency arrays
       - $timeout → setTimeout + useEffect cleanup
       - $interval → setInterval + useEffect cleanup
    """
    
    base_events = """
    4. EVENT HANDLING:
       - ng-click → onClick
       - ng-change → onChange
       - ng-submit → onSubmit
       - maintain exact event handler logic and parameters
       - preserve all function return values
    """
    
    # Common final output requirements for all prompts
    final_requirements = """
    FINAL OUTPUT REQUIREMENTS:
    - Your output MUST be a working React component that can be imported and used directly
    - Include ALL necessary imports (React, hooks, external libraries)
    - Include a proper export statement (export default ComponentName)
    - Ensure complete functionality matching the original Angular code
    - Handle all edge cases and error states 
    - The component should work as a drop-in replacement for the Angular code
    """
    
    # Specialized prompt sections based on file type combinations
    prompts = {
        # Single file types
        "javascript": {
            "intro": base_intro + "\nFOCUS: This is primarily a JavaScript conversion task. Ensure all Angular services, factories, and controllers are properly transformed to React hooks and components.",
            "specialized": """
            JAVASCRIPT CONVERSION SPECIFICS:
            - Convert Angular dependency injection to React imports and hooks
            - Transform Angular promises to async/await or modern Promise chains
            - Replace Angular's $q with native JavaScript promises
            - Convert Angular's $timeout and $interval to setTimeout/setInterval with proper cleanup
            - Transform scope inheritance patterns to React's prop drilling or Context API
            - Convert Angular event system ($emit, $broadcast) to custom React event handling
            - Replace $watch with useEffect hooks using appropriate dependency arrays
            """
        },
        "html": {
            "intro": base_intro + "\nFOCUS: This is primarily an HTML template conversion task. Ensure all Angular template syntax is properly transformed to JSX.",
            "specialized": """
            HTML CONVERSION SPECIFICS:
            - Transform Angular expressions {{ }} to JSX expressions { }
            - Convert ng-if to conditional rendering with && or ternary operators
            - Transform ng-show/ng-hide to conditional style or className props
            - Replace ng-repeat with map() functions preserving all iterator variables
            - Convert ng-class to className with conditional logic
            - Transform ng-style to style objects
            - Convert Angular filters to equivalent JavaScript methods
            - Handle HTML attributes properly (class→className, for→htmlFor, etc.)
            """
        },
        "cshtml": {
            "intro": base_intro + "\nFOCUS: This is primarily a Razor/CSHTML template conversion task. Ensure all Razor and Angular syntax is properly transformed to JSX.",
            "specialized": """
            CSHTML/RAZOR CONVERSION SPECIFICS:
            - Transform Razor syntax (@Model, @foreach, etc.) to JSX equivalents
            - Convert Angular expressions {{ }} to JSX expressions { }
            - Transform @if/@else to conditional rendering with && or ternary operators
            - Replace @foreach loops with map() functions
            - Handle HTML attributes properly (class→className, for→htmlFor, etc.)
            - Convert Angular directives to React props and components
            - Handle server-side variables appropriately
            """
        },
        "css": {
            "intro": base_intro + "\nFOCUS: This conversion includes CSS styling. Ensure styles are properly transformed to React's styling approach.",
            "specialized": """
            CSS CONVERSION SPECIFICS:
            - Convert inline styles to React style objects
            - Transform class-based styles to className props
            - Consider using CSS modules or styled-components based on complexity
            - Convert dynamic Angular classes to conditional className props
            - Ensure specificity and cascade are maintained in the React implementation
            - Handle media queries appropriately
            """
        },
        "scss": {
            "intro": base_intro + "\nFOCUS: This conversion includes SCSS styling. Ensure styles are properly transformed to React's styling approach.",
            "specialized": """
            SCSS CONVERSION SPECIFICS:
            - Transform SCSS variables to CSS variables or React theme constants
            - Convert SCSS nesting to appropriate React styling solution
            - Transform SCSS mixins and functions to JavaScript utility functions
            - Consider styled-components or CSS modules for component scoping
            - Preserve the cascade and specificity in the React implementation
            - Handle media queries appropriately
            """
        },
        
        # Common combinations
        "javascript-html": {
            "intro": base_intro + "\nFOCUS: This conversion involves both JavaScript and HTML templates. Ensure proper transformation of Angular controllers and views into React components with JSX.",
            "specialized": """
            JAVASCRIPT + HTML CONVERSION SPECIFICS:
            - Transform Angular controllers to React functional components
            - Convert HTML templates to JSX syntax
            - Replace Angular expressions {{ }} with JSX expressions { }
            - Transform ng-if/ng-show/ng-hide to conditional rendering
            - Convert ng-repeat to map() functions with proper keys
            - Replace ng-class with conditional className props
            - Transform event bindings (ng-click, etc.) to React event handlers
            - Convert two-way binding (ng-model) to controlled components
            """
        },
        "javascript-cshtml": {
            "intro": base_intro + "\nFOCUS: This conversion involves both JavaScript and Razor templates. Ensure proper transformation of Angular controllers and Razor views into React components with JSX.",
            "specialized": """
            JAVASCRIPT + CSHTML CONVERSION SPECIFICS:
            - Transform Angular controllers to React functional components
            - Convert Razor templates to JSX syntax
            - Replace both Razor syntax (@Model) and Angular expressions {{ }} with JSX expressions { }
            - Transform Razor conditionals and Angular directives to React patterns
            - Convert server-side loops to client-side map() functions
            - Ensure proper handling of server-side data in the React component
            - Transform event bindings to React event handlers
            """
        },
        "javascript-css": {
            "intro": base_intro + "\nFOCUS: This conversion involves both JavaScript functionality and CSS styling. Ensure proper transformation of Angular controllers and styles into React components with appropriate styling approach.",
            "specialized": """
            JAVASCRIPT + CSS CONVERSION SPECIFICS:
            - Transform Angular controllers to React functional components
            - Convert Angular services to custom hooks
            - Ensure proper state management with useState and useEffect
            - Transform inline styles to React style objects
            - Convert class-based styles to className props
            - Consider CSS-in-JS approaches for dynamic styling
            - Handle dynamic classes based on component state
            """
        },
        "javascript-scss": {
            "intro": base_intro + "\nFOCUS: This conversion involves both JavaScript functionality and SCSS styling. Ensure proper transformation of Angular controllers and SCSS styles into React components with appropriate styling approach.",
            "specialized": """
            JAVASCRIPT + SCSS CONVERSION SPECIFICS:
            - Transform Angular controllers to React functional components
            - Convert Angular services to custom hooks
            - Ensure proper state management with useState and useEffect
            - Consider styled-components or CSS modules for SCSS features
            - Transform SCSS variables to theme constants
            - Convert nested SCSS rules appropriately
            - Handle dynamic styling based on component state
            """
        },
        "javascript-html-css": {
            "intro": base_intro + "\nFOCUS: This is a comprehensive conversion including JavaScript logic, HTML templates, and CSS styling. Create a complete React component with matching functionality and appearance.",
            "specialized": """
            COMPREHENSIVE CONVERSION (JS + HTML + CSS):
            - Transform Angular controllers to React functional components
            - Convert HTML templates to JSX with proper React patterns
            - Transform all Angular directives to React equivalents
            - Ensure proper state management with hooks
            - Convert CSS styling to appropriate React approach
            - Handle all component lifecycle methods
            - Maintain identical visual appearance and behavior
            """
        },
        "javascript-html-scss": {
            "intro": base_intro + "\nFOCUS: This is a comprehensive conversion including JavaScript logic, HTML templates, and SCSS styling. Create a complete React component with matching functionality and appearance.",
            "specialized": """
            COMPREHENSIVE CONVERSION (JS + HTML + SCSS):
            - Transform Angular controllers to React functional components
            - Convert HTML templates to JSX with proper React patterns
            - Transform all Angular directives to React equivalents
            - Ensure proper state management with hooks
            - Convert SCSS styling to appropriate React approach (consider styled-components)
            - Transform SCSS variables, mixins, and nesting
            - Maintain identical visual appearance and behavior
            """
        },
        "javascript-cshtml-css": {
            "intro": base_intro + "\nFOCUS: This conversion involves JavaScript, Razor templates, and CSS styling. Create a complete React component that handles both Angular and Razor syntax.",
            "specialized": """
            COMPREHENSIVE CONVERSION (JS + CSHTML + CSS):
            - Transform Angular controllers to React functional components
            - Convert Razor templates to JSX with proper React patterns
            - Transform both Angular directives and Razor syntax
            - Handle server-side Razor variables in client-side React
            - Ensure proper state management with hooks
            - Convert CSS styling to appropriate React approach
            - Maintain identical visual appearance and behavior
            """
        },
        "javascript-cshtml-scss": {
            "intro": base_intro + "\nFOCUS: This conversion involves JavaScript, Razor templates, and SCSS styling. Create a complete React component that handles both Angular and Razor syntax with advanced styling.",
            "specialized": """
            COMPREHENSIVE CONVERSION (JS + CSHTML + SCSS):
            - Transform Angular controllers to React functional components
            - Convert Razor templates to JSX with proper React patterns
            - Transform both Angular directives and Razor syntax
            - Handle server-side Razor variables in client-side React
            - Ensure proper state management with hooks
            - Convert SCSS styling to appropriate React approach (consider styled-components)
            - Transform SCSS variables, mixins, and nesting
            - Maintain identical visual appearance and behavior
            """
        }
    }
    
    # Get the appropriate prompt based on the file type combination
    # If the specific combination isn't defined, fall back to a generic approach
    if file_types_key in prompts:
        selected_prompt = prompts[file_types_key]
        
        specialized_prompt = f"""
        {selected_prompt['intro']}
        
        FILE TYPE SPECIFICS:
        - Converting {', '.join(file_types)} files to React
        
        {selected_prompt['specialized']}
        
        {final_requirements}
        
        COMPREHENSIVE CONVERSION RULES:
        
        {base_structure}
        
        {base_state}
        
        {base_lifecycle}
        
        {base_events}
        
        5. DATA BINDING & RENDERING:
           - ng-model → controlled components (value + onChange)
           - ng-repeat → map function with exact iterator variables
           - ng-if/ng-show/ng-hide → conditional rendering
           - Convert Angular interpolation in JSX
           - ng-class → className with conditional objects/functions
           - ng-style → style object with same properties
           - filters → equivalent JavaScript methods or utility functions
           
        6. HTTP & DATA FETCHING:
           - $http → fetch or axios with identical URL structure and parameters
           - maintain all query parameters, headers, and request configuration
           - transform promise chains to async/await or chained .then()
           - preserve error handling patterns
           
        7. FORM HANDLING:
           - Form validation → controlled form + validation state
           - ng-required → required prop + validation state
           - Form submission → onSubmit handler with identical logic
        
        8. ADVANCED PATTERNS:
           - Convert custom directives → React components with identical props
           - Convert transclusion → children props
           - Convert complex services → custom hooks with same API
           - Handle route parameters with useParams or similar
           - Manage query strings with appropriate React hooks
        
        AngularJS Code:
        {angular_code}
        
        Output ONLY production-ready React code with exact functional equivalence. The code MUST be a complete, 
        working React component that can be used immediately with proper imports and exports. NO explanations or comments.
        """
    else:
        # Handle any combination not explicitly defined with a generic approach
        file_type_guidance = ""
        if "javascript" in file_types:
            file_type_guidance += "- Focus on JavaScript functionality conversion\n"
        if "cshtml" in file_types:
            file_type_guidance += "- Convert Razor/CSHTML templates to JSX\n"
        if "html" in file_types:
            file_type_guidance += "- Convert HTML templates and attributes to JSX\n"
        if "css" in file_types:
            file_type_guidance += "- Include CSS conversion to CSS-in-JS or styled-components\n"
        if "scss" in file_types:
            file_type_guidance += "- Convert SCSS to appropriate React styling approach\n"
        
        specialized_prompt = f"""
        {base_intro}
        
        FILE TYPE SPECIFICS:
        {file_type_guidance}
        
        {final_requirements}
        
        COMPREHENSIVE CONVERSION RULES:
        
        {base_structure}
        
        {base_state}
        
        {base_lifecycle}
        
        {base_events}
        
        5. DATA BINDING & RENDERING:
           - ng-model → controlled components (value + onChange)
           - ng-repeat → map function with exact iterator variables
           - ng-if/ng-show/ng-hide → conditional rendering
           - Convert Angular interpolation in JSX
           - ng-class → className with conditional objects/functions
           - ng-style → style object with same properties
           - filters → equivalent JavaScript methods or utility functions
           
        6. HTTP & DATA FETCHING:
           - $http → fetch or axios with identical URL structure and parameters
           - maintain all query parameters, headers, and request configuration
           - transform promise chains to async/await or chained .then()
           - preserve error handling patterns
           
        7. FORM HANDLING:
           - Form validation → controlled form + validation state
           - ng-required → required prop + validation state
           - Form submission → onSubmit handler with identical logic
        
        8. ADVANCED PATTERNS:
           - Convert custom directives → React components with identical props
           - Convert transclusion → children props
           - Convert complex services → custom hooks with same API
           - Handle route parameters with useParams or similar
           - Manage query strings with appropriate React hooks
        
        AngularJS Code:
        {angular_code}
        
        Output ONLY production-ready React code with exact functional equivalence. The code MUST be a complete, 
        working React component that can be used immediately with proper imports and exports. NO explanations or comments.
        """
    
    return specialized_prompt
