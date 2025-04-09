from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.migration_models import ProjectAnalysis, TargetStructure
import logging

logger = logging.getLogger(__name__)

class CleanupService:
    @staticmethod
    def cleanup_old_records(db: Session, hours: int = 6):
        """Clean up records older than specified hours"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Delete old target structures
            old_structures = db.query(TargetStructure).filter(
                TargetStructure.updated_at < cutoff_time
            ).all()
            
            for structure in old_structures:
                db.delete(structure)
            
            # Delete old analyses
            old_analyses = db.query(ProjectAnalysis).filter(
                ProjectAnalysis.updated_at < cutoff_time
            ).all()
            
            for analysis in old_analyses:
                db.delete(analysis)
            
            db.commit()
            
            logger.info(f"Cleaned up {len(old_structures)} structures and {len(old_analyses)} analyses older than {hours} hours")
            
        except Exception as e:
            logger.error(f"Error during database cleanup: {str(e)}")
            db.rollback()