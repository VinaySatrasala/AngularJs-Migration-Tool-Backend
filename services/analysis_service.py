import json
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
    async def migrate_project(project_path: str, project_id: str,instructions : str = "") -> Dict[str, Any]:
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
                    
            # Run the analyzer
            analyzer = AngularProjectAnalyzer(
                project_path=project_path,
                instructions = instructions
            )
            analysis_results = await analyzer.analyze_project()
            
            # Save analysis to database and get the saved instance
            analysis_instance = MigrationDBService.save_analysis(db, project_id, analysis_results)
            if not analysis_instance:
                raise Exception("Failed to save analysis results to database")
            
            # Generate target structure
            target_generator = ReactMigrationStructureGenerator(
                db = db,
                llm_config=llm_config,
                project_id=project_id,
                instructions = instructions
            )
            target_structure = await target_generator.generate_react_structure()
            
            # Save target structure to database and get the saved instance
            structure_instance = MigrationDBService.save_target_structure(db, project_id, target_structure)
            if not structure_instance:
                raise Exception("Failed to save target structure to database")
            
            # Generate React components
            react_generator = ReactComponentGenerator(
                db=db,
                output_dir=output_dir,
                llm_config=llm_config,
                project_id=project_id,
                instructions = instructions
            )
            await react_generator.generate_project()
            
            # Remove from database after successful generation
            # MigrationDBService.delete_project_data(db, project_id)
            
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
            # print(f"Error analyzing project: {str(e)}")
            raise e
        finally:
            db.close()
            
    
    @staticmethod
    async def generate_target_structure(project_path : str, project_id : str, instructions : str = "") -> Dict[str,Any]:
        """
            Making editable target structre by the user
            
        """
        
        # Generating analysis
        db = next(get_db())
        try:            
            # Run the analyzer
            analyzer = AngularProjectAnalyzer(
                project_path=project_path,
                instructions = instructions
            )
            analysis_results = await analyzer.analyze_project()
            
            # Save analysis to database and get the saved instance
            analysis_instance = MigrationDBService.save_analysis(db, project_id, analysis_results)
            if not analysis_instance:
                raise Exception("Failed to save analysis results to database")
            
            # Generate target structure
            target_generator = ReactMigrationStructureGenerator(
                db = db,
                llm_config=llm_config,
                project_id=project_id,
                instructions = instructions
            )
            target_structure = await target_generator.generate_react_structure()
            
            # Save target structure to database and get the saved instance
            # print("here" + instructions)
            structure_instance = MigrationDBService.save_target_structure(db, project_id, target_structure, instructions)
            if not structure_instance:
                raise Exception("Failed to save target structure to database")
            
            
            return {
                "project_id": project_id,
                "target_structure": target_structure,
            }
        except Exception as e:
            try:
                db.rollback()
            except:
                pass
            # print(f"Error analyzing project: {str(e)}")
            raise e
        finally:
            db.close()
       
    @staticmethod
    async def migrate_from_target(project_id: str, target_structure: Dict[str, Any]) -> Dict[str, Any]:
        db = next(get_db())
        try:
            # Define output directory (React code will be generated here)
            output_dir = Path(f"output/{project_id}")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save target structure to DB if there are any changes from frontend
            structure_instance = MigrationDBService.save_target_structure(db, project_id, target_structure)
            if not structure_instance:
                raise Exception("Failed to save target structure to database")
            
            target_data = MigrationDBService.get_target_structure(db, project_id)
            # print(target_data)
            # Initialize generator and trigger code generation
            react_generator = ReactComponentGenerator(
                db=db,
                output_dir=output_dir,
                llm_config=llm_config,
                project_id=project_id,
                instructions = target_data.get("instructions")

            )
            await react_generator.generate_project()

            return {
                "status": "success",
                "project_id": project_id,
                "target_structure": target_structure,
                "output_dir": str(output_dir)
            }

        except Exception as e:
            try:
                db.rollback()
            except:
                pass
            # print(f"Error during migration: {str(e)}")
            raise e
        finally:
            db.close()
    
