"""
Repository Pattern Implementation
===================================
Data access layer for all database entities.
Encapsulates all database queries, keeping business logic clean.
"""

import json
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from loguru import logger

from database.models import Project, Analysis
from database.db import get_db_session


class ProjectRepository:
    """Repository for Project entity CRUD operations."""
    
    def __init__(self, session: Session):
        self._session = session
    
    def get_all(self) -> list[Project]:
        """Return all projects ordered by last analyzed (most recent first)."""
        return (
            self._session.query(Project)
            .order_by(desc(Project.last_analyzed), desc(Project.created_at))
            .all()
        )
    
    def get_by_id(self, project_id: int) -> Optional[Project]:
        """Find project by primary key."""
        return self._session.query(Project).filter(Project.id == project_id).first()
    
    def get_by_path(self, path: str) -> Optional[Project]:
        """Find project by filesystem path."""
        return self._session.query(Project).filter(Project.path == path).first()
    
    def create(self, name: str, path: str, description: str = '') -> Project:
        """Create and persist a new project."""
        project = Project(
            name=name,
            path=path,
            description=description,
            created_at=datetime.utcnow(),
        )
        self._session.add(project)
        self._session.flush()  # Get the ID without committing
        logger.info(f"Created project {project.id}: {name}")
        return project
    
    def update_last_analyzed(self, project_id: int) -> None:
        """Update the last_analyzed timestamp for a project."""
        project = self.get_by_id(project_id)
        if project:
            project.last_analyzed = datetime.utcnow()
            self._session.flush()
    
    def delete(self, project_id: int) -> bool:
        """Delete project and all associated analyses. Returns True if deleted."""
        project = self.get_by_id(project_id)
        if not project:
            return False
        self._session.delete(project)
        logger.info(f"Deleted project {project_id}")
        return True
    
    def count(self) -> int:
        """Return total number of projects."""
        return self._session.query(Project).count()


class AnalysisRepository:
    """Repository for Analysis entity operations."""
    
    def __init__(self, session: Session):
        self._session = session
    
    def get_by_id(self, analysis_id: int) -> Optional[Analysis]:
        """Find analysis by primary key."""
        return self._session.query(Analysis).filter(Analysis.id == analysis_id).first()
    
    def get_by_project(self, project_id: int, limit: int = 20) -> list[Analysis]:
        """Return recent analyses for a project."""
        return (
            self._session.query(Analysis)
            .filter(Analysis.project_id == project_id)
            .order_by(desc(Analysis.created_at))
            .limit(limit)
            .all()
        )
    
    def get_latest_by_project(self, project_id: int) -> Optional[Analysis]:
        """Return the most recent analysis for a project."""
        return (
            self._session.query(Analysis)
            .filter(Analysis.project_id == project_id)
            .order_by(desc(Analysis.created_at))
            .first()
        )
    
    def save_project_analysis(self, project_id: int, project_result: dict) -> Analysis:
        """
        Persist a complete project analysis result.
        
        Args:
            project_id: ID of the analyzed project.
            project_result: Full ProjectReviewResult dict from the review engine.
        
        Returns:
            Saved Analysis record.
        """
        scores = project_result.get('scores', {})
        issue_summary = project_result.get('issue_summary', {})
        
        analysis = Analysis(
            project_id=project_id,
            created_at=datetime.utcnow(),
            duration_seconds=project_result.get('duration_seconds', 0.0),
            overall_score=scores.get('overall', 0.0),
            quality_score=scores.get('quality', 0.0),
            security_score=scores.get('security', 0.0),
            performance_score=scores.get('performance', 0.0),
            maintainability_score=scores.get('maintainability', 0.0),
            readability_score=scores.get('readability', 0.0),
            total_files=project_result.get('total_files', 0),
            total_issues=issue_summary.get('total', 0),
            critical_issues=issue_summary.get('critical', 0),
            high_issues=issue_summary.get('high', 0),
            medium_issues=issue_summary.get('medium', 0),
            low_issues=issue_summary.get('low', 0),
            info_issues=issue_summary.get('info', 0),
            result_json=json.dumps(project_result, default=str),
        )
        self._session.add(analysis)
        self._session.flush()
        logger.info(f"Saved analysis {analysis.id} for project {project_id}")
        return analysis
    
    def search_issues(self, query: str = '', severity: str = None,
                      language: str = None, category: str = None,
                      limit: int = 50) -> list[dict]:
        """
        Search across all analysis results for matching issues.
        Since issues are stored as JSON, this does a Python-side filter.
        
        Returns:
            List of matching issue dicts with analysis context.
        """
        analyses = (
            self._session.query(Analysis)
            .order_by(desc(Analysis.created_at))
            .limit(20)  # Search recent 20 analyses
            .all()
        )
        
        results = []
        query_lower = query.lower()
        
        for analysis in analyses:
            try:
                data = json.loads(analysis.result_json or '{}')
                file_results = data.get('file_results', [])
                
                for file_result in file_results:
                    if language and file_result.get('language', '').lower() != language.lower():
                        continue
                    
                    for issue in file_result.get('issues', []):
                        # Apply filters
                        if severity and issue.get('severity', '').upper() != severity.upper():
                            continue
                        if category and issue.get('category', '').lower() != category.lower():
                            continue
                        if query_lower and query_lower not in json.dumps(issue).lower():
                            continue
                        
                        results.append({
                            **issue,
                            "file_path": file_result.get('file_path', ''),
                            "language": file_result.get('language', ''),
                            "analysis_id": analysis.id,
                            "project_id": analysis.project_id,
                        })
                        
                        if len(results) >= limit:
                            return results
            except Exception:
                continue
        
        return results
    
    def get_dashboard_stats(self) -> dict:
        """Return aggregate statistics for the dashboard."""
        from sqlalchemy import func
        
        total_analyses = self._session.query(func.count(Analysis.id)).scalar() or 0
        total_projects = self._session.query(func.count(Project.id)).scalar() or 0
        
        latest = (
            self._session.query(Analysis)
            .order_by(desc(Analysis.created_at))
            .first()
        )
        
        return {
            "total_analyses": total_analyses,
            "total_projects": total_projects,
            "latest_analysis": latest.to_summary_dict() if latest else None,
        }
