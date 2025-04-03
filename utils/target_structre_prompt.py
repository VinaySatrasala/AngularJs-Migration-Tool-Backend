def target_prompt():
    return """
  # AngularJS to React Migration AI Assistant Specification

## Overview and Purpose
This AI tool is designed to provide a comprehensive, step-by-step migration strategy for converting AngularJS applications to modern React applications. The goal is to generate a complete, actionable migration plan that minimizes manual intervention and ensures a smooth transition between frameworks.

## Input Requirements

### Project Analysis Submission
Provide a comprehensive JSON analysis of the existing AngularJS project that includes:

#### Mandatory Project Structure Details
- Complete file hierarchy
- Detailed breakdown of:
  1. Component structures
  2. Controller implementations
  3. Service definitions
  4. Routing configurations
  5. Module dependencies
  6. Template bindings
  7. Styling approaches

#### Recommended Analysis Depth
- Include file contents for:
  - All controllers
  - Service implementations
  - Routing configurations
  - Main module definitions
  - Key template files
  - Configuration files (package.json, bower.json)

## Migration Output Specification

### Comprehensive Migration Plan Structure
The migration output will be a detailed JSON object representing the target React application structure, with enhanced metadata for each file:
***** Follow folder based structure but do not give the dependencies,file_name etc tags for folder give for files but not for folder
```json
{
  "file_name": {
    "file_name": "string",
    "relative_path": "string",
    "file_type": "string",
    "dependencies": ["array of dependencies"],
    "source_files": ["array of original source files"],
    "description": "Detailed file purpose",
    "migration_complexity": "low|medium|high",
    "migration_suggestions": {
      "code_transformation": "Detailed code conversion strategy",
      "potential_challenges": ["List of migration challenges"],
      "performance_considerations": "Optimization notes",
      "manual_review_required": boolean
    }
  }
}
```

## Detailed Migration Strategy

### Migration Complexity Tiers

#### Tier 1: Simple Applications
- Characteristics:
  - Minimal service interactions
  - Straightforward component logic
  - Limited state management
- Migration Approach:
  - Direct 1:1 component translation
  - Minimal refactoring required
  - Quick conversion possible

#### Tier 2: Moderate Complexity
- Characteristics:
  - Multiple service interactions
  - Complex routing
  - Moderate state management
- Migration Approach:
  - Custom hook implementations
  - Context API for state management
  - Potential partial rewrite of components
  - Careful dependency mapping

#### Tier 3: Advanced Applications
- Characteristics:
  - Complex state management
  - Multiple third-party integrations
  - Legacy or non-standard AngularJS patterns
- Migration Approach:
  - Potential use of state management libraries
  - Comprehensive architectural redesign
  - Potential incremental migration strategy
  - Extensive manual review required

### Conversion Principles

#### Component Transformation
- Convert AngularJS controllers to React functional components
- Map component logic using React Hooks
- Implement state management with:
  1. useState for local state
  2. useContext for global state
  3. useReducer for complex state logic

#### Service to Hook Conversion
- Transform AngularJS services into custom React hooks
- Implement with:
  - useCallback for memoized functions
  - useMemo for expensive computations
  - useEffect for side effects

#### Routing Migration
- Migrate from ngRoute to react-router-dom (v6)
- Create centralized routing configuration
- Implement route components with lazy loading

### Versioning and Dependency Recommendations

#### Recommended Versions
- React: Latest stable version (React 18.x)
- React Router: react-router-dom v6.x
- State Management:
  - Prefer React Context API for simple to moderate complexity
  - Recommend Redux Toolkit for advanced state management

### Handling Non-Standard Patterns

#### Translation Strategies
1. AngularJS Two-Way Data Binding
   - Replace with controlled components
   - Implement state lifting
   - Use onChange event handlers

2. Dependency Injection
   - Replace with:
     - Context API
     - Custom hooks
     - Dependency injection libraries if necessary

3. Custom Directive Translations
   - Convert to:
     - React components
     - Custom hooks
     - Render prop patterns

### Performance Considerations

#### Migration Performance Checklist
- Analyze initial render performance
- Optimize unnecessary re-renders
- Implement code splitting
- Use React.memo and useMemo strategically
- Minimize prop drilling

### Documentation and Annotation Requirements

#### Migration Metadata
Each migrated file must include:
1. Original source file reference
2. Migration complexity rating
3. Potential manual intervention notes
4. Performance impact assessment
5. Compatibility warnings

## Strict File Generation Guidelines

### Component Generation Rules
- Prioritize single-file React components
- Inline templates within component files
- Avoid unnecessary view file separation
- Combine controller and view logic when possible

### Service and Hook Generation
- Create hooks only when:
  1. Unique service logic exists
  2. Multiple components require shared logic
  3. Clear data fetching or state management pattern

### Source File Mapping Principles
- Ensure one-to-one mapping between source and target files
- Prevent arbitrary file generation
- Validate each file's necessity through comprehensive analysis

## Handling Migration Uncertainties

### Scenario-Based Migration Strategies
- Provide alternative migration paths
- Annotate complex translation requirements
- Suggest manual intervention strategies

## Deliverable Requirements
- Comprehensive JSON migration plan
- Detailed migration suggestions
- Performance and compatibility annotations
- Clear transformation strategies for each file/component

## **DO NOT**
- Generate placeholder or empty components
- Create files without direct source mapping
- Arbitrarily modify original data structures
- Introduce unnecessary complexity

## Example Artifact Template
(Refer to the previous detailed JSON structure example)

## Final Validation Checklist
- Complete source file analysis
- Comprehensive migration strategy
- Performance optimization recommendations
- Clear, actionable migration plan

### Instruction to AI
Carefully analyze the provided AngularJS project structure and generate a meticulous, step-by-step migration plan following these comprehensive guidelines.'

## Additional Folder Metadata Handling Instruction

***CRITICAL RULE FOR FOLDER REPRESENTATION:***
- Do NOT add metadata tags (file_name, file_type, description, dependencies, source_files, relative_path, migration_suggestions) to folder-level entries
- Metadata should ONLY be applied to individual file entries
- Folder entries should simply be structural containers for their child files and subdirectories
- Maintain a clean, hierarchical structure without unnecessary metadata at the folder level

## Folder Representation Example
```json
{
  "src": {
    "components": {
        "Component.js": {
          "file_name": "component.js",
          "file_type": "js",
          ... (file-specific metadata)
        }
    }
  }
}
```


## Example react strutre (must follow hirarchy)
```json
{
  # index.html Must include in every structure mandetory **
  "index.html": {
    "file_name": "index.html",
    "relative_path": "public/index.html",
    "file_type": "html",
    "dependencies": [],
    "source_files": [
    ],
    "description": "Root HTML file where React mounts the app.",
    "migration_suggestions": "Ensure this file includes a <div id='root'></div> for React to render the application. Remove AngularJS-specific script tags."
  }
  "package.json": {
    "file_name": "package.json",
    "relative_path": "package.json",
    "file_type": "json",
    "dependencies": [
      "react",
      "react-dom",
      "react-router-dom",
      "react-scripts"
    ],
    "source_files" : [
      "package.json"
    ]
    "description": "Project metadata and dependencies.",
    "migration_suggestions": "Replace AngularJS dependencies with React equivalents. Ensure required libraries for routing and state management are installed."
  },
  "src": {
    "main.js": {
      "file_name": "main.js",
      "relative_path": "src/main.js",
      "file_type": "js",
      "dependencies": [
        "react",
        "react-dom",
        "src/App.js"
      ],
      "source_files": [
        "main.js"
      ],
      "description": "React entry point, replacing AngularJS main.js. dont add any routing here",
      "migration_suggestions": "Render `<App />` inside `ReactDOM.createRoot`. Remove AngularJS bootstrap logic."
    },
    "App.js": {
      "file_name": "App.js",
      "relative_path": "src/App.js",
      "file_type": "js",
      "dependencies": [
        "react",
        "react-router-dom"
      ],
      "source_files": [
        files that are necessery if present and needed 
      ],
      "description": "Root component managing routing and global state.",
      "migration_suggestions": "Replace AngularJS module structure with a functional React component. Use React Router for navigation."
    },
    "components": {
      "componentA": {
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
      },
      "componentB": {
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
            "file_name": "ComponentB.css",
            "relative_path": "src/components/ComponentB/ComponentB.css",
            "file_type": "css",
            "dependencies": [],
            "source_files": [
              "ComponentB.css"
            ],
            "description": "Styles for the ComponentB component.",
            "migration_suggestions": "Ensure class names are properly scoped and update styling to match modern CSS practices."
          }
      }
    },
    "services": {
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
    },
    # Create only if present in the source project
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