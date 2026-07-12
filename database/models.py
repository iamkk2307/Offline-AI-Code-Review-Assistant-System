"""
Database Models
===============
SQLAlchemy ORM models for all application entities.
Uses the Repository Pattern for data access.
"""

import json
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, Boolean,
    ForeignKey, Index, create_engine
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class Project(Base):
    """Represents a code review project workspace."""
    __tablename__ = 'projects'
    
    id            = Column(Integer, primary_key=True, autoincrement=True)
    name          = Column(String(255), nullable=False)
    path          = Column(String(1024), nullable=False, unique=True)
    description   = Column(Text, default='')
    created_at    = Column(DateTime, default=datetime.utcnow)
    last_analyzed = Column(DateTime, nullable=True)
    total_files   = Column(Integer, default=0)
    
    # Relationships
    analyses = relationship('Analysis', back_populates='project', cascade='all, delete-orphan')
    
    __table_args__ = (
        Index('ix_projects_path', 'path'),
    )
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_analyzed": self.last_analyzed.isoformat() if self.last_analyzed else None,
            "total_files": self.total_files,
        }


class Analysis(Base):
    """Stores results of a full project analysis."""
    __tablename__ = 'analyses'
    
    id                    = Column(Integer, primary_key=True, autoincrement=True)
    project_id            = Column(Integer, ForeignKey('projects.id'), nullable=False)
    created_at            = Column(DateTime, default=datetime.utcnow)
    duration_seconds      = Column(Float, default=0.0)
    
    # Aggregate scores (0–100)
    overall_score         = Column(Float, default=0.0)
    quality_score         = Column(Float, default=0.0)
    security_score        = Column(Float, default=0.0)
    performance_score     = Column(Float, default=0.0)
    maintainability_score = Column(Float, default=0.0)
    readability_score     = Column(Float, default=0.0)
    
    # Project statistics
    total_files           = Column(Integer, default=0)
    total_issues          = Column(Integer, default=0)
    critical_issues       = Column(Integer, default=0)
    high_issues           = Column(Integer, default=0)
    medium_issues         = Column(Integer, default=0)
    low_issues            = Column(Integer, default=0)
    info_issues           = Column(Integer, default=0)
    
    # Full serialized result (JSON)
    result_json           = Column(Text, default='{}')
    
    # Relationships
    project  = relationship('Project', back_populates='analyses')
    
    __table_args__ = (
        Index('ix_analyses_project_id', 'project_id'),
        Index('ix_analyses_created_at', 'created_at'),
    )
    
    def to_dict(self) -> dict:
        result = {
            "id": self.id,
            "project_id": self.project_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "duration_seconds": self.duration_seconds,
            "scores": {
                "overall": self.overall_score,
                "quality": self.quality_score,
                "security": self.security_score,
                "performance": self.performance_score,
                "maintainability": self.maintainability_score,
                "readability": self.readability_score,
            },
            "issue_summary": {
                "total": self.total_issues,
                "critical": self.critical_issues,
                "high": self.high_issues,
                "medium": self.medium_issues,
                "low": self.low_issues,
                "info": self.info_issues,
            },
            "total_files": self.total_files,
        }
        # Merge in detailed result JSON
        try:
            result.update(json.loads(self.result_json or '{}'))
        except (json.JSONDecodeError, TypeError):
            pass
        return result
    
    def to_summary_dict(self) -> dict:
        """Lightweight summary without full result_json."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "duration_seconds": self.duration_seconds,
            "overall_score": self.overall_score,
            "total_files": self.total_files,
            "total_issues": self.total_issues,
            "critical_issues": self.critical_issues,
        }
