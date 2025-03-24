"""
Enhanced prompts for AngularJS file analysis focused on migration preparation.
Each prompt targets a specific file type and requests detailed information
needed to understand AngularJS code structure and migration complexity.
"""

def get_js_prompt(file_name: str, content: str) -> str:
    """Creates a prompt for analyzing JavaScript files."""
    return f"""You are a JavaScript analyzer for an AngularJS to React migration project.
Please analyze this JavaScript file and provide insights in a valid JSON format.

File: {file_name}
Content: {content}

IMPORTANT: Your response must be ONLY valid JSON in this exact format:
{{
    "module_declarations": [],
    "controllers": [],
    "services": [],
    "directives": [],
    "scope_variables": [],
    "dependencies": [],
    "watchers": [],
    "api_calls": [],
    "routing_config": {{
        "has_routing": false,
        "routes": []
    }},
    "template_bindings": [],
    "migration_complexity": "low",
    "summary": ""
}}

Return ONLY the JSON object, no other text."""

def get_html_prompt(file_name: str, content: str) -> str:
    """Creates a prompt for analyzing HTML template files."""
    return f"""You are an HTML analyzer for an AngularJS to React migration project.
Please analyze this HTML template file and provide insights in a valid JSON format.

File: {file_name}
Content: {content}

IMPORTANT: Your response must be ONLY valid JSON in this exact format:
{{
    "directives_used": [],
    "controllers": [],
    "filters_used": [],
    "scope_bindings": [],
    "events": [],
    "includes": [],
    "form_validation": {{
        "has_forms": false,
        "validation_types": []
    }},
    "ui_components": [],
    "migration_complexity": "low",
    "summary": ""
}}

Return ONLY the JSON object, no other text."""

def get_css_prompt(file_name: str, content: str) -> str:
    """Creates a prompt for analyzing CSS files."""
    return f"""You are a CSS analyzer for an AngularJS to React migration project.
Please analyze this CSS file and provide insights in a valid JSON format.

File: {file_name}
Content: {content}

IMPORTANT: Your response must be ONLY valid JSON in this exact format:
{{
    "selectors_count": 0,
    "major_components": [],
    "animation_effects": [],
    "responsive_design": {{
        "has_responsive": false,
        "breakpoints": []
    }},
    "third_party": [],
    "migration_complexity": "low",
    "summary": ""
}}

Return ONLY the JSON object, no other text."""

def get_json_prompt(file_name: str, content: str) -> str:
    """Creates a prompt for analyzing JSON configuration files."""
    return f"""You are a JSON analyzer for an AngularJS to React migration project.
Please analyze this JSON configuration file and provide insights in a valid JSON format.

File: {file_name}
Content: {content}

IMPORTANT: Your response must be ONLY valid JSON in this exact format:
{{
    "purpose": "",
    "key_structures": [],
    "dependencies": [],
    "build_config": {{}},
    "migration_complexity": "low",
    "summary": ""
}}

Return ONLY the JSON object, no other text."""

def get_default_prompt(file_name: str, content: str, file_type: str) -> str:
    """Creates a generic prompt for analyzing other file types."""
    return f"""You are a file analyzer for an AngularJS to React migration project.
Please analyze this {file_type} file and provide insights in a valid JSON format.

File: {file_name}
Content: {content}

IMPORTANT: Your response must be ONLY valid JSON in this exact format:
{{
    "file_purpose": "",
    "relation_to_angular": "",
    "dependencies": [],
    "migration_complexity": "low",
    "summary": ""
}}

Return ONLY the JSON object, no other text."""