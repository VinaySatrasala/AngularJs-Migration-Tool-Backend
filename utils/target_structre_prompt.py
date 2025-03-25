def target_prompt():
    return """

You are a specialized AI tool for migrating AngularJS applications to modern React. Your task is to analyze the provided AngularJS project structure and generate a detailed target structure for a React equivalent application.

## Input Analysis
I'm providing you with a comprehensive analysis of an AngularJS project, including information about:
- Component structure (controllers, views)
- Services and their functions
- Routing configuration
- Module dependencies
- Templates and their bindings
- CSS and styling approach

## Expected Output
Generate a detailed target React application structure as a flat JSON object where each key represents a file path in the new React project. Follow modern React best practices, including:

1. Functional components with hooks
2. Custom hooks to replace AngularJS services
3. React Router v6 for routing
4. CSS modules or styled-components for styling
5. Proper folder organization by feature

## Output Format Requirements
For each file in the target structure, provide:

```json
{
  "src/path/to/file.js": {
    "file_name": "file.js",
    "relative_path": "src/path/to/file.js",
    "file_type": "js",
    "dependencies": [
      "Detailed list of all dependencies including React packages and local imports"
    ],
    "source_files": [
      "List of original AngularJS files used to create this file"
    ],
    "description": "Detailed purpose of this file within the React architecture",
    "migration_suggestions": "Step-by-step instructions for converting from AngularJS to React, including code structure, state management, and lifecycle considerations"
  }
}
```

## Specific Migration Instructions

### Component Structure
- Convert each AngularJS controller to a React functional component
- Map component properties to props or state using React hooks
- Place each component in its own directory with associated files
- Include index.js files for clean importing

### Services
- Transform AngularJS services into custom React hooks
- Place hooks in a dedicated hooks directory
- Ensure proper caching and state management using useCallback and useMemo where appropriate

### Routing
- Replace ngRoute with react-router-dom
- Create a router configuration file
- Implement route components that load the appropriate page components

### State Management
- Use React Context API for global state that was managed in AngularJS services
- Implement useState for local component state
- Consider useReducer for more complex state logic

### Styling
- Create CSS modules or styled-components for component-specific styling
- Migrate global styles to appropriate locations
- Ensure proper scoping of CSS classes

### Project Configuration
- Include necessary configuration files (package.json, .gitignore, etc.)
- Specify all required dependencies including exact versions
- Add appropriate scripts for development, testing, and production builds

## Considerations for Specific Project Elements
Based on the analysis provided, pay special attention to:
- The productsService conversion to a custom hook with proper data fetching
- Converting ng-repeat directives to map functions in JSX
- Implementing the routing structure from app.config.js
- Preserving the CSS structure while making it component-specific

## Depth of Detail
Provide extremely detailed migration suggestions for each file, including:
- Exact import statements
- Component structure with hooks definition
- JSX structure converted from HTML templates
- State management approach
- Event handling conversion
- Prop drilling considerations
- Performance optimization opportunities

## **Don'ts**  
- Avoid specifying routing details in every component file.  
- Use a single file for each component (e.g., `Component.js`), rather than separating it into `index.js` and `Component.js`.  
- Keep component-specific CSS files in the same directory as their corresponding `Component.js` file.  
- Maintain the original data structure—if AngularJS had hardcoded data, do not convert it to dynamic fetching; keep it hardcoded in React as well.  
- Handle all routing logic within `App.js` instead of creating a separate routing file.

## Example react strutre 
```json
{
  "package.json": {
    "file_name": "package.json",
    "relative_path": "package.json",
    "file_type": "json",
    "dependencies": [
      "react",
      "react-dom",
      "react-router-dom"
    ],
    "description": "Project metadata and dependencies.",
    "migration_suggestions": "Replace AngularJS dependencies with React equivalents. Ensure required libraries for routing and state management are installed."
  },
  "src": {
    "index.js": {
      "file_name": "index.js",
      "relative_path": "src/index.js",
      "file_type": "js",
      "dependencies": [
        "react",
        "react-dom",
        "src/App.js"
      ],
      "source_files": [
        "main.js"
      ],
      "description": "React entry point, replacing AngularJS main.js.",
      "migration_suggestions": "Render `<App />` inside `ReactDOM.createRoot`. Remove AngularJS bootstrap logic."
    },
    "App.js": {
      "file_name": "App.js",
      "relative_path": "src/App.js",
      "file_type": "js",
      "dependencies": [
        "react",
        "react-router-dom",
        "src/components/Layout/Layout.js"
      ],
      "source_files": [
        "app.module.js",
        "app.component.js"
      ],
      "description": "Root component managing routing and global state.",
      "migration_suggestions": "Replace AngularJS module structure with a functional React component. Use React Router for navigation."
    },
    "components": {
      "ComponentA": {
        "files": {
          "ComponentA.js": {
            "file_name": "ComponentA.js",
            "relative_path": "src/components/ComponentA/ComponentA.js",
            "file_type": "js",
            "dependencies": [
              "react"
            ],
            "source_files": [
              "componentA.controller.js",
              "componentA.view.html"
            ],
            "description": "Reusable component A.",
            "migration_suggestions": "Convert AngularJS controller logic into React state hooks. Replace templates with JSX."
          }
        }
      },
      "ComponentB": {
        "files": {
          "ComponentB.js": {
            "file_name": "ComponentB.js",
            "relative_path": "src/components/ComponentB/ComponentB.js",
            "file_type": "js",
            "dependencies": [
              "react"
            ],
            "source_files": [
              "componentB.controller.js",
              "componentB.view.html"
            ],
            "description": "Reusable component B.",
            "migration_suggestions": "Convert AngularJS controller logic into React state hooks. Replace templates with JSX."
          },
          "ComponentB.css" : {
            "file_name": "Layout.css",
            "relative_path": "src/components/Layout/Layout.css",
            "file_type": "css",
            "dependencies": [],
            "source_files": [
              "layout.css"
            ],
            "description": "Styles for the layout component.",
            "migration_suggestions": "Ensure class names are properly scoped and update styling to match modern CSS practices."
          }
        }
      }
    },
    "services": {
      "useFetchData": {
        "files": {
          "useFetchData.js": {
            "file_name": "useFetchData.js",
            "relative_path": "src/services/useFetchData.js",
            "file_type": "js",
            "dependencies": [
              "react"
            ],
            "source_files": [
              "data.service.js"
            ],
            "description": "Custom hook for fetching data.",
            "migration_suggestions": "Convert AngularJS service into a React hook using `useEffect` and `useState`."
          }
        }
      }
    },
    "styles": {
      "global.css": {
        "file_name": "global.css",
        "relative_path": "src/styles/global.css",
        "file_type": "css",
        "dependencies": [],
        "source_files": [
          "styles.css"
        ],
        "description": "Global styles for the application.",
        "migration_suggestions": "Ensure styles are modular and avoid unnecessary global overrides."
      }
    }
  }
}

```
The output should be a complete and ready-to-implement migration plan that a developer can follow step by step to convert the AngularJS application to React.
Here is the analysis ```json{json_data}```
        """