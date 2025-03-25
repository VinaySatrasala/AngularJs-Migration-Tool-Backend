# AngularJS to React Migration Tool

A powerful, AI-driven tool that automatically migrates AngularJS applications to modern React applications. This tool analyzes your AngularJS codebase, understands its structure and patterns, and generates equivalent React components while preserving the application's functionality and architecture.

## Table of Contents
- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [API Endpoints](#api-endpoints)
- [Core Components](#core-components)
- [Installation](#installation)
- [Usage](#usage)
- [Technical Details](#technical-details)

## Features

### Intelligent Analysis
- Comprehensive AngularJS pattern detection
- Deep dependency analysis
- Code structure and relationship mapping
- AI-powered code understanding
- Automated component identification

### Smart Migration
- Automated conversion of AngularJS to React
- Preservation of component relationships
- Modern React patterns implementation
- State management strategy generation
- Routing structure migration
- Dependency injection transformation

### Robust Architecture
- Asynchronous processing
- Modular design
- Error handling and recovery
- Clean code organization
- Database integration
- Temporary file management

## Architecture Overview

The system is built on a modern, scalable architecture that combines FastAPI, SQLAlchemy, and AI/LLM capabilities:

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Client    │────▶│  FastAPI     │────▶│  Analysis    │
│   (HTTP)    │     │  Endpoints   │     │  Service     │
└─────────────┘     └──────────────┘     └──────────────┘
                                               │
                                               ▼
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Output    │◀────│    React     │◀────│  Migration   │
│   (ZIP)     │     │  Generator   │     │  Structure   │
└─────────────┘     └──────────────┘     └──────────────┘
```

## Project Structure

```
project/
├── config/               # Configuration files
│   ├── db_config.py     # Database configuration
│   └── llm_config.py    # Language model settings
│
├── models/              # Database models
│   ├── analysis.py      # Analysis result models
│   └── github_request.py# Request models
│
├── routes/              # API endpoints
│   ├── base_routes.py   # Base endpoints
│   └── migration_routes.py # Migration endpoints
│
├── services/            # Core business logic
│   ├── analysis_service.py    # Orchestration service
│   ├── project_analyser.py    # AngularJS analysis
│   ├── react_generator.py     # React code generation
│   └── target_structure_generator.py # Migration planning
│
├── utils/              # Helper utilities
│   └── analysis_prompts.py # AI prompts
│
├── uploads/            # Temporary file storage
└── output/            # Generated React files
```

## How It Works

### 1. Project Submission
Users can submit their AngularJS projects in two ways:
- GitHub repository URL
- ZIP file upload

The system:
1. Generates a unique project ID
2. Creates temporary storage
3. Processes the input (cloning repo or extracting ZIP)

### 2. Analysis Phase
The `AngularProjectAnalyzer` performs a deep analysis of the codebase:

```python
Patterns detected:
- angular.module()     # Module definitions
- .controller()       # Controllers
- .service()         # Services
- .factory()         # Factories
- .directive()       # Directives
- .component()       # Components
- $inject           # Dependency injection
- routing configs   # UI-Router/ngRoute
```

Each file is analyzed for:
- Dependencies
- Component relationships
- State management
- Routing configuration
- Template structure

### 3. Migration Planning
The `ReactMigrationStructureGenerator` creates a comprehensive migration plan:

1. **Component Hierarchy**
   - Maps AngularJS components to React
   - Determines parent-child relationships
   - Plans component composition

2. **State Management**
   - Identifies global state needs
   - Plans Context/Redux implementation
   - Maps services to hooks

3. **Routing Structure**
   - Converts Angular routes to React Router
   - Preserves route parameters
   - Maintains nested routing

### 4. React Generation
The `ReactComponentGenerator` creates the React application:

1. **Component Creation**
   - Converts controllers to functional components
   - Transforms templates to JSX
   - Implements hooks for lifecycle methods
   - Creates custom hooks from services

2. **State Implementation**
   - Sets up Context providers
   - Implements state management
   - Converts $scope to hooks

3. **Routing Setup**
   - Configures React Router
   - Sets up route components
   - Preserves route parameters

### 5. Output Delivery
The final step packages and delivers the migrated application:

1. Creates a structured React project
2. Packages all components into a ZIP
3. Cleans up temporary files
4. Delivers the ZIP to the user

## API Endpoints

### Base Endpoint
- GET / - Welcome message and available endpoints

### Migration Endpoints
- POST /api/v1/migration/github
  - Body: { "github_url": "string" }
  - Returns: ZIP file of migrated React app

- POST /api/v1/migration/zip
  - Body: form-data with ZIP file
  - Returns: ZIP file of migrated React app

## Core Components

### AnalysisService
Orchestrates the entire migration process:
- Manages project lifecycle
- Coordinates analysis and generation
- Handles database operations
- Manages file operations

### AngularProjectAnalyzer
Performs deep analysis of AngularJS code:
- Pattern detection
- Dependency tracking
- Code structure analysis
- AI-assisted understanding

### ReactMigrationStructureGenerator
Plans the React application structure:
- Component hierarchy
- State management strategy
- Routing configuration
- Dependency mapping

### ReactComponentGenerator
Creates React components:
- Component conversion
- JSX generation
- Hook implementation
- Style migration

## Installation

1. Clone the repository
```bash
git clone <repository-url>
cd AngularJs-React-Migration
```

2. Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your configurations
```

## Usage

1. Start the server
```bash
uvicorn server:app --reload
```

2. Submit your AngularJS project:
   - Use the API endpoints with Postman/curl
   - Or use the web interface if available

3. Wait for the migration to complete

4. Download the migrated React application

## Technical Details

### Dependencies
- FastAPI: Web framework
- SQLAlchemy: Database ORM
- GitPython: Git operations
- LangChain: AI/LLM integration
- Pydantic: Data validation

### Database Schema
- Analysis results
- Migration structures
- Project metadata

### AI/LLM Integration
- Code analysis
- Pattern recognition
- Migration strategy
- Component generation

### Error Handling
- Input validation
- Process recovery
- File cleanup
- Error reporting

## Contributing
Contributions are welcome! Please read our contributing guidelines and submit pull requests to our repository.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
