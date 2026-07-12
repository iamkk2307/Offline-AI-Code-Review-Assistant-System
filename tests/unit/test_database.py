import os
import tempfile
import pytest
from sqlalchemy import create_engine
from database.db import init_db, get_session
from database.repository import ProjectRepository, AnalysisRepository
from database.models import Base

@pytest.fixture
def temp_db():
    fd, db_path = tempfile.mkstemp(suffix=".db")
    db_url = f"sqlite:///{db_path}"
    
    # Initialize DB
    init_db(db_url)
    
    yield db_url
    
    # Close any open connections and cleanup
    try:
        os.close(fd)
        os.remove(db_path)
    except Exception:
        pass

def test_project_repository(temp_db):
    session = get_session()
    repo = ProjectRepository(session)
    
    # Create project
    project = repo.create(name="TestProj", path="/path/to/proj", description="Testing description")
    assert project.id is not None
    assert project.name == "TestProj"
    assert project.path == "/path/to/proj"
    
    # Get all projects
    projects = repo.get_all()
    assert len(projects) == 1
    assert projects[0].id == project.id
    
    # Find project
    p = repo.get_by_id(project.id)
    assert p is not None
    assert p.path == "/path/to/proj"
    
    p2 = repo.get_by_path("/path/to/proj")
    assert p2 is not None
    assert p2.id == project.id
    
    # Update last analyzed
    repo.update_last_analyzed(project.id)
    session.commit()
    
    p_updated = repo.get_by_id(project.id)
    assert p_updated.last_analyzed is not None
    
    # Delete project
    assert repo.delete(project.id)
    session.commit()
    
    assert repo.get_by_id(project.id) is None
    session.close()

def test_analysis_repository(temp_db):
    session = get_session()
    proj_repo = ProjectRepository(session)
    analysis_repo = AnalysisRepository(session)
    
    project = proj_repo.create(name="TestProj", path="/path/to/proj")
    session.commit()
    
    # Mock ProjectReviewResult dict
    mock_result = {
        "project_path": "/path/to/proj",
        "duration_seconds": 1.5,
        "total_files": 10,
        "scores": {
            "overall": 85.0,
            "quality": 88.0,
            "security": 90.0,
            "maintainability": 80.0,
            "performance": 85.0,
            "readability": 82.0
        },
        "issue_summary": {
            "total": 5,
            "critical": 0,
            "high": 1,
            "medium": 2,
            "low": 2,
            "info": 0
        },
        "file_results": [
            {
                "file_path": "/path/to/proj/file.py",
                "filename": "file.py",
                "language": "Python",
                "scores": {"overall": 85.0},
                "issues": [
                    {
                        "title": "SQL Injection",
                        "description": "Risk detected",
                        "severity": "HIGH",
                        "category": "security",
                        "line_number": 10
                    }
                ]
            }
        ]
    }
    
    analysis = analysis_repo.save_project_analysis(project.id, mock_result)
    session.commit()
    
    assert analysis.id is not None
    assert analysis.project_id == project.id
    assert analysis.overall_score == 85.0
    assert analysis.high_issues == 1
    
    # Retrieve
    a = analysis_repo.get_by_id(analysis.id)
    assert a is not None
    assert a.overall_score == 85.0
    
    # Latest
    latest = analysis_repo.get_latest_by_project(project.id)
    assert latest is not None
    assert latest.id == analysis.id
    
    # Search issues
    issues = analysis_repo.search_issues(query="Injection")
    assert len(issues) == 1
    assert issues[0]["title"] == "SQL Injection"
    
    # Dashboard stats
    stats = analysis_repo.get_dashboard_stats()
    assert stats["total_projects"] == 1
    assert stats["total_analyses"] == 1
    
    session.close()
