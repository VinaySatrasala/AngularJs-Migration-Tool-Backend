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
            output_dir = Path(f"output/{project_id}")
            output_dir.mkdir(parents=True, exist_ok=True)
        
            analysis_dir = output_dir / "analysis"
            analysis_dir.mkdir(parents=True, exist_ok=True)
            
            analysis_file = analysis_dir / f"{project_id}_analysis.json"
            analysis_file_content = analysis_dir / f"{project_id}_analysis_with_content.json"
            react_structure_file = output_dir / "react_migration_structure.json"
            
            # Run the analyzer
            analyzer = AngularProjectAnalyzer(
                project_path=project_path,
                project_id=project_id,
                output_file=str(analysis_file)
            )
            analysis_results = await analyzer.analyze_project()
            
            # Save analysis to database and get the saved instance
            analysis_instance = MigrationDBService.save_analysis(db, project_id, analysis_results)
            if not analysis_instance:
                raise Exception("Failed to save analysis results to database")
            
            # Generate target structure
            target_generator = ReactMigrationStructureGenerator(
                analysis_file=str(analysis_file),
                llm_config=llm_config,
                project_id=project_id,
            )
            target_structure = await target_generator.generate_react_structure()
            
            # Save target structure to database and get the saved instance
            structure_instance = MigrationDBService.save_target_structure(db, project_id, target_structure)
            if not structure_instance:
                raise Exception("Failed to save target structure to database")
            
            # Generate React components
            react_generator = ReactComponentGenerator(
                migration_file=str(react_structure_file),
                analysis_file=str(analysis_file_content),
                output_dir=output_dir / "react_output",
                llm_config=llm_config
            )
            await react_generator.generate_project()
            
            return {
                "status": "success",
                "project_id": project_id,
                "analysis_results": analysis_results,
                "target_structure": target_structure,
                "output_dir": str(output_dir),
                "timestamp": str(analysis_instance.created_at)
            }
        except Exception as e:
            try:
                db.rollback()
            except:
                pass
            print(f"Error analyzing project: {str(e)}")
            raise e
        finally:
            db.close()
