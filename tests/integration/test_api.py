import os
import tempfile
import json
import pytest
from server.app import create_app
from server.config import Config

class TestConfig(Config):
    TESTING = True
    DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def client():
    app = create_app(TestConfig())
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "models_loaded" in data

def test_projects_crud(client):
    # Create project using a real directory path
    with tempfile.TemporaryDirectory() as temp_dir:
        payload = {"name": "API Test Proj", "path": temp_dir}
        res = client.post("/api/projects/", json=payload)
        assert res.status_code == 201
        project = res.get_json()
        assert project["id"] is not None
        assert project["name"] == "API Test Proj"
        
        # List projects
        res = client.get("/api/projects/")
        assert res.status_code == 200
        projects = res.get_json()
        assert len(projects) == 1
        assert projects[0]["id"] == project["id"]
        
        # Get project
        res = client.get(f"/api/projects/{project['id']}")
        assert res.status_code == 200
        assert res.get_json()["name"] == "API Test Proj"
        
        # Delete project
        res = client.delete(f"/api/projects/{project['id']}")
        assert res.status_code == 200
        assert res.get_json()["message"] == "Project deleted successfully"

def test_settings_endpoints(client):
    # Get settings
    res = client.get("/api/settings/")
    assert res.status_code == 200
    settings = res.get_json()
    assert "theme" in settings
    
    # Update settings
    payload = {"theme": "light", "max_workers": 8}
    res = client.put("/api/settings/", json=payload)
    assert res.status_code == 200
    updated = res.get_json()
    assert updated["theme"] == "light"
    assert updated["max_workers"] == 8
    
    # Reset settings
    res = client.post("/api/settings/reset")
    assert res.status_code == 200
    reset_settings = res.get_json()
    assert reset_settings["theme"] == "dark"
