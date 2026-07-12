import os
import tempfile
import pytest
from ml.predictors.model_manager import ModelManager
from review_engine.engine import ReviewEngine
from review_engine.review_result import ProjectReviewResult
from utils.file_utils import collect_source_files
from server.config import Config

@pytest.fixture
def test_project():
    temp_dir = tempfile.TemporaryDirectory()
    
    # Create a couple of mock source files with some issues
    py_code = """
def process_data(data):
    # TODO: implement
    eval(data)
    password = "secret_value"
    return data
"""
    js_code = """
function calculate(val) {
  var x = 10; // unused
  return val * 2;
}
"""
    sql_code = """
SELECT * FROM users WHERE id = 'val';
"""
    
    with open(os.path.join(temp_dir.name, "main.py"), "w") as f:
        f.write(py_code)
    with open(os.path.join(temp_dir.name, "utils.js"), "w") as f:
        f.write(js_code)
    with open(os.path.join(temp_dir.name, "schema.sql"), "w") as f:
        f.write(sql_code)
        
    yield temp_dir.name
    
    temp_dir.cleanup()

def test_full_review_flow(test_project):
    # Load ML models
    models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'ml', 'models')
    mm = ModelManager(models_dir=models_dir)
    mm.load_all()
    
    cfg = Config()
    engine = ReviewEngine(model_manager=mm, config=cfg)
    
    # Collect files
    files = collect_source_files(test_project, cfg)
    assert len(files) == 3
    
    # Run analysis
    progress_calls = []
    def progress_callback(processed, current):
        progress_calls.append((processed, current))
        
    result_dict = engine.analyze_project(
        project_path=test_project,
        files=files,
        progress_callback=progress_callback
    )
    
    # Verify results
    assert len(progress_calls) == 3
    assert result_dict["total_files"] == 3
    assert result_dict["analyzed_files"] == 3
    assert result_dict["failed_files"] == 0
    
    scores = result_dict["scores"]
    assert 0 <= scores["overall"] <= 100
    assert 0 <= scores["security"] <= 100
    assert 0 <= scores["quality"] <= 100
    
    issue_summary = result_dict["issue_summary"]
    assert issue_summary["total"] > 0
    assert issue_summary["critical"] >= 0
    
    # Check language distribution
    dist = result_dict["language_distribution"]
    assert dist["Python"] == 1
    assert dist["JavaScript"] == 1
    assert dist["SQL"] == 1
    
    # Check top critical issues
    top_issues = result_dict["top_critical_issues"]
    assert len(top_issues) > 0
    assert any(i["title"] in ("Hardcoded Credential", "Unsafe eval Usage") for i in top_issues)
