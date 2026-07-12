"""
ML Model Manager
=================
Loads, caches, and manages all pre-trained ML models.
Provides a unified interface for running predictions.

Design Pattern: Facade — provides a simple interface to the model ensemble.
"""

import os
import json
import time
import numpy as np
import joblib
from typing import Optional
from loguru import logger

from parsers.base_plugin import Features


class ModelManager:
    """
    Manages all pre-trained ML models for inference.
    
    Models are loaded once at startup and cached in memory.
    All prediction methods are < 1 second per file on a standard CPU.
    """
    
    MODEL_FILES = {
        'bug_detector':           'bug_detector.joblib',
        'security_risk':          'security_risk.joblib',
        'severity_classifier':    'severity_classifier.joblib',
        'quality_scorer':         'quality_scorer.joblib',
        'maintainability_scorer': 'maintainability_scorer.joblib',
        'readability_scorer':     'readability_scorer.joblib',
        'scaler':                 'scaler.joblib',
        'severity_encoder':       'severity_label_encoder.joblib',
    }
    
    def __init__(self, models_dir: str):
        self.models_dir = models_dir
        self._models: dict = {}
        self._scaler = None
        self._severity_encoder = None
        self._metadata: dict = {}
        self._loaded = False
    
    def load_all(self) -> None:
        """Load all model files from the models directory."""
        metadata_path = os.path.join(self.models_dir, 'metadata.json')
        if os.path.isfile(metadata_path):
            with open(metadata_path) as f:
                self._metadata = json.load(f)
        
        failed = []
        for name, filename in self.MODEL_FILES.items():
            path = os.path.join(self.models_dir, filename)
            if os.path.isfile(path):
                try:
                    model = joblib.load(path)
                    if name == 'scaler':
                        self._scaler = model
                    elif name == 'severity_encoder':
                        self._severity_encoder = model
                    else:
                        self._models[name] = model
                    logger.debug(f"Loaded model: {filename}")
                except Exception as e:
                    logger.warning(f"Failed to load {filename}: {e}")
                    failed.append(name)
            else:
                logger.warning(f"Model file not found: {path}")
                failed.append(name)
        
        self._loaded = True
        if failed:
            logger.warning(f"Missing/failed models: {failed}. Using fallback scores.")
        else:
            logger.info(f"All {len(self._models)} ML models loaded successfully.")
    
    @property
    def model_count(self) -> int:
        """Number of successfully loaded models."""
        return len(self._models)
    
    @property
    def is_ready(self) -> bool:
        """True if at least the scaler and one model are loaded."""
        return self._scaler is not None and len(self._models) > 0
    
    def predict(self, features: Features) -> dict:
        """
        Run all ML models on a Features object and return predictions.
        
        Returns dict with all scores:
            bug_probability:      0.0–1.0
            security_risk_score:  0.0–1.0
            quality_score:        0–100
            maintainability_score: 0–100
            readability_score:    0–100
            predicted_severity:   CRITICAL|HIGH|MEDIUM|LOW|INFO
        
        Falls back to heuristic scores if models are not loaded.
        """
        if not self.is_ready:
            return self._heuristic_scores(features)
        
        try:
            # Build feature vector
            X_raw = np.array([features.to_vector()], dtype=np.float64)
            # Replace NaN/inf
            X_raw = np.nan_to_num(X_raw, nan=0.0, posinf=100.0, neginf=0.0)
            X_scaled = self._scaler.transform(X_raw)
            
            result = {}
            
            # Bug probability
            if 'bug_detector' in self._models:
                proba = self._models['bug_detector'].predict_proba(X_scaled)[0]
                result['bug_probability'] = float(proba[1])
            else:
                result['bug_probability'] = self._heuristic_bug_prob(features)
            
            # Security risk
            if 'security_risk' in self._models:
                proba = self._models['security_risk'].predict_proba(X_scaled)[0]
                result['security_risk_score'] = float(proba[1])
            else:
                result['security_risk_score'] = self._heuristic_security_risk(features)
            
            # Code quality (0–100)
            if 'quality_scorer' in self._models:
                score = self._models['quality_scorer'].predict(X_scaled)[0]
                result['quality_score'] = float(np.clip(score, 0, 100))
            else:
                result['quality_score'] = self._heuristic_quality(features)
            
            # Maintainability (0–100)
            if 'maintainability_scorer' in self._models:
                score = self._models['maintainability_scorer'].predict(X_scaled)[0]
                result['maintainability_score'] = float(np.clip(score, 0, 100))
            else:
                result['maintainability_score'] = features.maintainability_index
            
            # Readability (0–100)
            if 'readability_scorer' in self._models:
                score = self._models['readability_scorer'].predict(X_scaled)[0]
                result['readability_score'] = float(np.clip(score, 0, 100))
            else:
                result['readability_score'] = self._heuristic_readability(features)
            
            # Severity classification
            if 'severity_classifier' in self._models and self._severity_encoder is not None:
                pred_class = self._models['severity_classifier'].predict(X_scaled)[0]
                result['predicted_severity'] = str(self._severity_encoder.inverse_transform([pred_class])[0])
            else:
                result['predicted_severity'] = self._heuristic_severity(features)
            
            return result
        
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            return self._heuristic_scores(features)
    
    # ── Fallback heuristics when models are not available ─────────────────
    
    def _heuristic_scores(self, features: Features) -> dict:
        """Rule-based fallback when ML models are unavailable."""
        return {
            'bug_probability':        self._heuristic_bug_prob(features),
            'security_risk_score':    self._heuristic_security_risk(features),
            'quality_score':          self._heuristic_quality(features),
            'maintainability_score':  float(features.maintainability_index),
            'readability_score':      self._heuristic_readability(features),
            'predicted_severity':     self._heuristic_severity(features),
        }
    
    def _heuristic_bug_prob(self, f: Features) -> float:
        score = 0.0
        if f.cyclomatic_complexity > 20: score += 0.3
        elif f.cyclomatic_complexity > 10: score += 0.15
        if f.duplicate_ratio > 0.2: score += 0.1
        if f.nested_loops > 3: score += 0.15
        if f.exception_handling == 0 and f.function_count > 3: score += 0.1
        if f.long_methods > 5: score += 0.1
        return float(min(1.0, score))
    
    def _heuristic_security_risk(self, f: Features) -> float:
        score = 0.0
        score += min(0.4, f.hardcoded_credentials * 0.2)
        score += min(0.3, f.eval_usage * 0.15)
        score += min(0.2, f.shell_executions * 0.1)
        score += min(0.1, f.sql_queries * 0.02)
        return float(min(1.0, score))
    
    def _heuristic_quality(self, f: Features) -> float:
        score = 70.0
        score -= min(30.0, f.cyclomatic_complexity * 0.8)
        score -= min(15.0, f.magic_numbers * 0.5)
        score -= min(15.0, f.duplicate_ratio * 50)
        score += min(10.0, f.comment_ratio * 30)
        score -= min(10.0, f.naming_violations * 0.3)
        return float(max(0.0, min(100.0, score)))
    
    def _heuristic_readability(self, f: Features) -> float:
        score = 70.0
        score += min(15.0, f.comment_ratio * 50)
        score -= min(20.0, f.avg_function_length * 0.1)
        score -= min(15.0, f.naming_violations * 0.5)
        score -= min(10.0, f.magic_numbers * 0.3)
        return float(max(0.0, min(100.0, score)))
    
    def _heuristic_severity(self, f: Features) -> str:
        if f.hardcoded_credentials > 0 or f.eval_usage > 2:
            return 'CRITICAL'
        if f.cyclomatic_complexity > 30 or f.shell_executions > 3:
            return 'HIGH'
        if f.cyclomatic_complexity > 15 or f.duplicate_ratio > 0.3:
            return 'MEDIUM'
        if f.magic_numbers > 10 or f.naming_violations > 10:
            return 'LOW'
        return 'INFO'
