from sqlalchemy.orm import Session
from models.migration_models import ProjectAnalysis, TargetStructure
from typing import Dict, Any, Optional
import json

class MigrationDBService:
    """Service for handling database operations for project analysis and target structure"""
    
    @staticmethod
    def save_analysis(db: Session, project_id: str, analysis_data: Dict[str, Any]) -> Optional[ProjectAnalysis]:
        """
        Save or update project analysis data
        Args:
            db: Database session
            project_id: Project identifier
            analysis_data: Analysis results to save
        """
        try:
            # Validate inputs
            if not project_id or not analysis_data:
                print("Error: Invalid project_id or analysis_data")
                return None

            # Check if analysis exists
            db_analysis = db.query(ProjectAnalysis).filter(ProjectAnalysis.project_id == project_id).first()
            
            if db_analysis:
                # Update existing analysis
                db_analysis.analysis_data = analysis_data
                db.commit()
                db.refresh(db_analysis)
                return db_analysis
            else:
                # Create new analysis
                db_analysis = ProjectAnalysis(
                    project_id=project_id,
                    analysis_data=analysis_data
                )
                db.add(db_analysis)
                db.commit()
                db.refresh(db_analysis)
                return db_analysis
        except Exception as e:
            print(f"Error saving analysis: {str(e)}")
            db.rollback()
            return None

    @staticmethod
    def save_target_structure(db: Session, project_id: str, structure_data: Dict[str, Any], instructions : str = "") -> Optional[TargetStructure]:
        """
        Save or update target structure data
        Args:
            db: Database session
            project_id: Project identifier
            structure_data: Target structure to save
        """
        try:
            # Validate inputs
            if not project_id or not structure_data:
                print("Error: Invalid project_id or structure_data")
                return None

            # Verify analysis exists first
            analysis = db.query(ProjectAnalysis).filter(ProjectAnalysis.project_id == project_id).first()
            if not analysis:
                print(f"Error: No analysis found for project_id {project_id}")
                return None

            # Check if structure exists
            db_structure = db.query(TargetStructure).filter(TargetStructure.project_id == project_id).first()
            
            if db_structure:
                # Update existing structure
                db_structure.structure_data = structure_data
                db.commit()
                db.refresh(db_structure)
                return db_structure
            else:
                # Create new structure
                db_structure = TargetStructure(
                    project_id=project_id,
                    structure_data=structure_data,
                    instructions=instructions,
                )
                db.add(db_structure)
                db.commit()
                db.refresh(db_structure)
                return db_structure
        except Exception as e:
            print(f"Error saving target structure: {str(e)}")
            db.rollback()
            return None

    @staticmethod
    def get_analysis(db: Session, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project analysis data by project ID"""
        try:
            if not project_id:
                return None
            db_analysis = db.query(ProjectAnalysis).filter(ProjectAnalysis.project_id == project_id).first()
            return {
                "analysis_data": db_analysis.analysis_data,
                "created_at": str(db_analysis.created_at),
                "updated_at": str(db_analysis.updated_at)
            } if db_analysis else None
        except Exception as e:
            print(f"Error retrieving analysis: {str(e)}")
            return None

    @staticmethod
    def get_target_structure(db: Session, project_id: str) -> Optional[Dict[str, Any]]:
        """Get target structure data by project ID"""
        try:
            if not project_id:
                return None
            db_structure = db.query(TargetStructure).filter(TargetStructure.project_id == project_id).first()
            return {
                "structure_data": db_structure.structure_data,
                "instructions": db_structure.instructions,
                "created_at": str(db_structure.created_at),
                "updated_at": str(db_structure.updated_at)
            } if db_structure else None
        except Exception as e:
            print(f"Error retrieving target structure: {str(e)}")
            return None

    @staticmethod
    def has_target_structure(db: Session, project_id: str) -> bool:
        """Check if target structure exists for project ID"""
        try:
            if not project_id:
                return False
            return db.query(TargetStructure).filter(TargetStructure.project_id == project_id).first() is not None
        except Exception as e:
            print(f"Error checking target structure existence: {str(e)}")
            return False
    
    @staticmethod
    def delete_project_data(db: Session, project_id: str) -> None:
        """Delete analysis and target structure data for a given project_id"""
        try:
            db_structure = db.query(TargetStructure).filter(TargetStructure.project_id == project_id).first()
            if db_structure:
                db.delete(db_structure)
            
            db_analysis = db.query(ProjectAnalysis).filter(ProjectAnalysis.project_id == project_id).first()
            if db_analysis:
                db.delete(db_analysis)
            
            db.commit()
        except Exception as e:
            print(f"Error deleting project data: {str(e)}")
            db.rollback()

