import os
import pytest
from ml.predictors.model_manager import ModelManager
from parsers.base_plugin import Features

def test_model_manager_fallback():
    # Construct with non-existent directory to trigger heuristics fallback
    manager = ModelManager(models_dir="/non/existent/path")
    manager.load_all()
    
    assert not manager.is_ready
    assert manager.model_count == 0
    
    # Run prediction which should use heuristic fallback
    f = Features()
    f.loc = 100
    f.sloc = 80
    f.cyclomatic_complexity = 25.0  # High complexity -> High severity heuristic
    f.hardcoded_credentials = 1     # Hardcoded -> Critical severity heuristic
    
    preds = manager.predict(f)
    assert preds["predicted_severity"] == "CRITICAL"
    assert preds["bug_probability"] > 0.0
    assert preds["security_risk_score"] > 0.0
    assert preds["quality_score"] < 100.0

def test_model_manager_real():
    # Test loading actual trained models bundled in ml/models
    models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'ml', 'models')
    
    manager = ModelManager(models_dir=models_dir)
    manager.load_all()
    
    assert manager.is_ready
    assert manager.model_count == 6
    
    # Run prediction using the actual ML models
    f = Features()
    f.loc = 50
    f.sloc = 40
    f.cyclomatic_complexity = 5.0
    f.maintainability_index = 80.0
    f.comment_ratio = 0.2
    
    preds = manager.predict(f)
    assert "overall_score" not in preds  # Health score calculated in engine, not predictor
    assert 0.0 <= preds["bug_probability"] <= 1.0
    assert 0.0 <= preds["security_risk_score"] <= 1.0
    assert 0.0 <= preds["quality_score"] <= 100.0
    assert 0.0 <= preds["maintainability_score"] <= 100.0
    assert 0.0 <= preds["readability_score"] <= 100.0
    assert preds["predicted_severity"] in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
