from pathlib import Path
import asyncio
import os
from typing import Dict, Any
from sqlalchemy.orm import Session
from services.project_analyser import AngularProjectAnalyzer
from services.target_structure_generator import ReactMigrationStructureGenerator
from services.db_service import MigrationDBService
from config.db_config import get_db
from config.llm_config import llm_config
from datetime import datetime
from services.react_generator import ReactComponentGenerator

class AnalysisService:
    """Service to manage project analysis tasks"""
    
    @staticmethod
    async def analyze_project(project_path: str, project_id: str) -> Dict[str, Any]:
        """
        Analyze a project at the given path and return the analysis results
        Args:
            project_path: Path to the project to analyze
            project_id: Unique identifier for the project
        """
        db = next(get_db())
        try:
            # Create analysis directory if it doesn't exist
            analysis_path = str(Path(project_path).parent / "analysis")
            os.makedirs(analysis_path, exist_ok=True)
            
            # Run the analyzer
            analyzer = AngularProjectAnalyzer(
                project_path=project_path,
                output_file=str(Path(analysis_path) / f"{project_id}_analysis.json")
            )
            analysis_results = await analyzer.analyze_project()
            
            # Save analysis to database and get the saved instance
            analysis_instance = MigrationDBService.save_analysis(db, project_id, analysis_results)
            if not analysis_instance:
                raise Exception("Failed to save analysis results to database")
            
            # Generate target structure
            target_generator = ReactMigrationStructureGenerator(
                analysis_file=str(Path(analysis_path) / f"{project_id}_analysis.json"),
                llm_config=llm_config,
                project_id=project_id
            )
            target_structure = await target_generator.generate_migration_structure()
            
            # Save target structure to database and get the saved instance
            structure_instance = MigrationDBService.save_target_structure(db, project_id, target_structure)
            if not structure_instance:
                raise Exception("Failed to save target structure to database")
            
            # Generate React components
            output_dir = str(Path(analysis_path) / "react_output")
            react_generator = ReactComponentGenerator(
                migration_file=target_generator.output_file,
                analysis_file=str(Path(analysis_path) / f"{project_id}_analysis.json"),
                output_dir=output_dir,
                llm_config=llm_config
            )
            await react_generator.generate_project()
            
            return {
                "status": "success",
                "project_id": project_id,
                "analysis_results": analysis_results,
                "target_structure": target_structure,
                "react_output_dir": output_dir,
                "timestamp": str(analysis_instance.created_at)
            }
        except Exception as e:
            try:
                db.rollback()
            except:
                pass
            print(f"Error analyzing project: {str(e)}")
            return {
                "status": "error",
                "project_id": project_id,
                "message": str(e),
                "timestamp": str(datetime.now())
            }
        finally:
            db.close()

    @staticmethod
    async def start_analysis(project_path: str, project_id: str) -> Dict[str, Any]:
        """
        Start project analysis in the background
        Args:
            project_path: Path to the project to analyze
            project_id: Unique identifier for the project
        """
        try:
            # Create task for background processing
            task = asyncio.create_task(AnalysisService.analyze_project(project_path, project_id))
            return {
                "status": "started",
                "project_id": project_id,
                "message": "Analysis started in background",
                "timestamp": str(datetime.now())
            }
        except Exception as e:
            return {
                "status": "error",
                "project_id": project_id,
                "message": f"Failed to start analysis: {str(e)}",
                "timestamp": str(datetime.now())
            }
