
"""
Enhanced prompts for AngularJS file analysis focused on migration preparation.
Each prompt targets a specific file type and requests detailed information
needed to understand AngularJS code structure and migration complexity.
"""

def get_js_prompt(file_name: str, content: str, instructions: str = "") -> str:
    """Creates a prompt for analyzing JavaScript files."""
    instruction_text = f"\nAdditional instructions: {instructions}" if instructions else ""
    
    return f"""You are a JavaScript analyzer for an AngularJS to React migration project.
Please analyze this JavaScript file and provide insights in a valid JSON format.

File: {file_name}
Content: {content}{instruction_text}

Analysis guidance:
- Focus on identifying AngularJS-specific patterns that will need migration
- Check for $scope usage which will need conversion to React state/props
- Identify service dependencies that will need React context or hooks
- Note usage of $watch and other lifecycle methods that need React equivalents
- Pay special attention to DOM manipulation which requires different approach in React

IMPORTANT: Your response must be ONLY valid JSON in this exact format:
{{
    "module_declarations": [],
    "controllers": [
        {{
            "name": "",
            "dependencies": [],
            "scope_usage": []
        }}
    ],
    "services": [
        {{
            "name": "",
            "type": "",  
            "dependencies": []
        }}
    ],
    "directives": [
        {{
            "name": "",
            "requires_template": false,
            "dom_manipulation": false
        }}
    ],
    "scope_variables": [],
    "dependencies": [],
    "watchers": [
        {{
            "watched_expression": "",
            "complexity": ""
        }}
    ],
    "api_calls": [
        {{
            "endpoint": "",
            "method": "",
            "service": ""
        }}
    ],
    "routing_config": {{
        "has_routing": false,
        "routes": [
            {{
                "path": "",
                "template": "",
                "controller": ""
            }}
        ]
    }},
    "template_bindings": [],
    "migration_complexity": "low|medium|high",
    "complexity_factors": [],
    "summary": ""
}}

Return ONLY the JSON object, no other text."""

def get_html_prompt(file_name: str, content: str, instructions: str = "") -> str:
    """Creates a prompt for analyzing HTML template files."""
    instruction_text = f"\nAdditional instructions: {instructions}" if instructions else ""
    
    return f"""You are an HTML analyzer for an AngularJS to React migration project.
Please analyze this HTML template file and provide insights in a valid JSON format.

File: {file_name}
Content: {content}{instruction_text}

Analysis guidance:
- Identify all ng-* directives which will need React equivalents
- Note usage of filters which need to be converted to JavaScript functions
- Identify form validation approaches that will need React form libraries
- Pay attention to ng-if, ng-repeat, ng-show which need conditional rendering in React
- Look for ng-include which needs component composition in React

IMPORTANT: Your response must be ONLY valid JSON in this exact format:
{{
    "directives_used": [
        {{
            "name": "",
            "count": 0,
            "react_equivalent": ""
        }}
    ],
    "controllers": [],
    "filters_used": [
        {{
            "name": "",
            "count": 0
        }}
    ],
    "scope_bindings": [
        {{
            "expression": "",
            "binding_type": "one-way|two-way|event"
        }}
    ],
    "events": [
        {{
            "name": "",
            "handler": ""
        }}
    ],
    "includes": [],
    "form_validation": {{
        "has_forms": false,
        "validation_types": [],
        "custom_validators": []
    }},
    "ui_components": [
        {{
            "name": "",
            "complexity": "low|medium|high"
        }}
    ],
    "migration_complexity": "low|medium|high",
    "complexity_factors": [],
    "summary": ""
}}

Return ONLY the JSON object, no other text."""

def get_css_prompt(file_name: str, content: str, instructions: str = "") -> str:
    """Creates a prompt for analyzing CSS files."""
    instruction_text = f"\nAdditional instructions: {instructions}" if instructions else ""
    
    return f"""You are a CSS analyzer for an AngularJS to React migration project.
Please analyze this CSS file and provide insights in a valid JSON format.

File: {file_name}
Content: {content}{instruction_text}

Analysis guidance:
- Identify selectors that target AngularJS-specific attributes (ng-*)
- Note any !important flags that may complicate component styling in React
- Look for global styles that would need to be scoped in React components
- Check for vendor prefixes and browser compatibility issues
- Identify any complex animations that might need React animation libraries

IMPORTANT: Your response must be ONLY valid JSON in this exact format:
{{
    "selectors_count": 0,
    "angular_specific_selectors": [],
    "major_components": [
        {{
            "name": "",
            "selector": "",
            "complexity": "low|medium|high"
        }}
    ],
    "animation_effects": [
        {{
            "type": "",
            "complexity": "low|medium|high"
        }}
    ],
    "responsive_design": {{
        "has_responsive": false,
        "breakpoints": [],
        "mobile_first": false
    }},
    "third_party": [],
    "global_styles": [],
    "migration_complexity": "low|medium|high",
    "complexity_factors": [],
    "summary": ""
}}

Return ONLY the JSON object, no other text."""

def get_json_prompt(file_name: str, content: str, instructions: str = "") -> str:
    """Creates a prompt for analyzing JSON configuration files."""
    instruction_text = f"\nAdditional instructions: {instructions}" if instructions else ""
    
    return f"""You are a JSON analyzer for an AngularJS to React migration project.
Please analyze this JSON configuration file and provide insights in a valid JSON format.

File: {file_name}
Content: {content}{instruction_text}

Analysis guidance:
- Determine if this is a package.json, angular.json, or other config file
- Identify AngularJS dependencies that will need React alternatives
- Note build tools and processes that will need updating
- Look for custom configurations specific to the AngularJS application
- Check for environment configurations that will need migration

IMPORTANT: Your response must be ONLY valid JSON in this exact format:
{{
    "purpose": "",
    "key_structures": [],
    "dependencies": [
        {{
            "name": "",
            "version": "",
            "react_alternative": ""
        }}
    ],
    "build_config": {{
        "tools": [],
        "scripts": [],
        "environments": []
    }},
    "angular_specific": [],
    "migration_complexity": "low|medium|high",
    "complexity_factors": [],
    "summary": ""
}}

Return ONLY the JSON object, no other text."""

def get_default_prompt(file_name: str, content: str, file_type: str, instructions: str = "") -> str:
    """Creates a generic prompt for analyzing other file types."""
    instruction_text = f"\nAdditional instructions: {instructions}" if instructions else ""
    
    return f"""You are a file analyzer for an AngularJS to React migration project.
Please analyze this {file_type} file and provide insights in a valid JSON format.

File: {file_name}
Content: {content}{instruction_text}

Analysis guidance:
- Determine how this file relates to the AngularJS application architecture
- Identify any AngularJS-specific code or references
- Note dependencies or connections to other parts of the application
- Consider how this file would need to be handled in a React application

IMPORTANT: Your response must be ONLY valid JSON in this exact format:
{{
    "file_purpose": "",
    "relation_to_angular": "",
    "dependencies": [],
    "references": [
        {{
            "type": "",
            "name": "",
            "context": ""
        }}
    ],
    "migration_complexity": "low|medium|high",
    "complexity_factors": [],
    "summary": ""
}}

Return ONLY the JSON object, no other text."""

def get_test_prompt(file_name: str, content: str, instructions: str = "") -> str:
    """Creates a prompt for analyzing test files (spec.js)."""
    instruction_text = f"\nAdditional instructions: {instructions}" if instructions else ""
    
    return f"""You are a test analyzer for an AngularJS to React migration project.
Please analyze this test file and provide insights in a valid JSON format.

File: {file_name}
Content: {content}{instruction_text}

Analysis guidance:
- Identify test framework being used (Jasmine, Karma, etc.)
- Note AngularJS-specific test utilities like $httpBackend or $controller
- Identify mocked dependencies and services
- Check for DOM testing approaches that will need different libraries in React
- Consider how these tests would be rewritten using React Testing Library or Jest

IMPORTANT: Your response must be ONLY valid JSON in this exact format:
{{
    "test_framework": "",
    "test_cases": [
        {{
            "description": "",
            "component_tested": "",
            "mocks": []
        }}
    ],
    "angular_test_utils": [],
    "dom_assertions": [],
    "async_testing": false,
    "coverage": {{
        "has_coverage": false,
        "coverage_type": ""
    }},
    "migration_complexity": "low|medium|high",
    "complexity_factors": [],
    "summary": ""
}}

Return ONLY the JSON object, no other text."""