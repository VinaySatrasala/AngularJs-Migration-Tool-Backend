from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ProjectAnalysis(Base):
    __tablename__ = 'project_analysis'

    id = Column(Integer, primary_key=True)
    project_id = Column(String(255), nullable=False)
    analysis_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TargetStructure(Base):
    __tablename__ = 'target_structure'

    id = Column(Integer, primary_key=True)
    project_id = Column(String(255), nullable=False)
    analysis_id = Column(Integer, ForeignKey('project_analysis.id'))
    structure_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
