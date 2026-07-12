"""
Review Engine — Core Orchestrator
===================================
Coordinates the complete analysis pipeline for files and projects.

Pipeline:
  File → Language Detection → Parser Plugin → Static/Security/Perf Analysis
       → Feature Extraction → ML Prediction → ReviewResult → Health Score

Implements the Observer Pattern for progress reporting.
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Callable
from loguru import logger

from parsers.plugin_registry import PluginRegistry
from parsers.base_plugin import Features, Issue
from ml.predictors.model_manager import ModelManager
from review_engine.review_result import FileReviewResult, ProjectReviewResult
from review_engine.health_score import HealthScoreCalculator


class ReviewEngine:
    """
    Main review engine that orchestrates the full analysis pipeline.
    
    Supports:
    - Single file analysis (synchronous, fast)
    - Full project analysis (parallel, with progress callbacks)
    """
    
    def __init__(self, model_manager: ModelManager, config=None):
        self._model_manager = model_manager
        self._config = config
        self._registry = PluginRegistry.get_instance()
        self._health_calc = HealthScoreCalculator(config)
    
    def analyze_file(self, file_path: str) -> FileReviewResult:
        """
        Analyze a single source file synchronously.
        
        Args:
            file_path: Absolute path to the source file.
        
        Returns:
            FileReviewResult with all scores, issues, and features.
        """
        start_time = time.time()
        
        # Get language plugin
        plugin = self._registry.get_plugin_for_file(file_path)
        if not plugin:
            from utils.language_detector import detect_language
            language = detect_language(file_path) or 'Unknown'
            return FileReviewResult(
                file_path=file_path,
                language=language,
                error=f"No plugin available for this file type.",
            )
        
        try:
            # Run full plugin review (parse → extract → analyze)
            parse_result, features, issues = plugin.review(file_path)
            
            # ML predictions
            ml_scores = self._model_manager.predict(features)
            
            # Calculate performance score from features/issues
            perf_score = self._calc_performance_score(features, issues)
            
            # Combine all scores into health score
            health = self._health_calc.calculate(
                quality_score=ml_scores.get('quality_score', 50.0),
                security_score=(1.0 - ml_scores.get('security_risk_score', 0.5)) * 100,
                maintainability_score=ml_scores.get('maintainability_score', 50.0),
                performance_score=perf_score,
                readability_score=ml_scores.get('readability_score', 50.0),
            )
            
            duration = time.time() - start_time
            
            return FileReviewResult(
                file_path=file_path,
                language=plugin.language,
                parse_errors=parse_result.parse_errors,
                features=features,
                issues=issues,
                ml_scores=ml_scores,
                scores={
                    'overall':         health,
                    'quality':         ml_scores.get('quality_score', 50.0),
                    'security':        (1.0 - ml_scores.get('security_risk_score', 0.5)) * 100,
                    'maintainability': ml_scores.get('maintainability_score', 50.0),
                    'performance':     perf_score,
                    'readability':     ml_scores.get('readability_score', 50.0),
                },
                duration_seconds=duration,
            )
        
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return FileReviewResult(
                file_path=file_path,
                language=plugin.language,
                error=str(e),
            )
    
    def analyze_project(
        self,
        project_path: str,
        files: list[dict],
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> dict:
        """
        Analyze all files in a project in parallel.
        
        Args:
            project_path: Root directory of the project.
            files: List of file info dicts from collect_source_files().
            progress_callback: Optional callback(processed_count, current_file_path).
        
        Returns:
            ProjectReviewResult as a dict.
        """
        start_time = time.time()
        max_workers = getattr(self._config, 'MAX_WORKERS', 4) if self._config else 4
        
        file_results = []
        processed = 0
        
        logger.info(f"Analyzing {len(files)} files with {max_workers} workers")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(self.analyze_file, f['path']): f
                for f in files
            }
            
            for future in as_completed(future_to_file):
                file_info = future_to_file[future]
                try:
                    result = future.result(timeout=30)
                    file_results.append(result)
                except Exception as e:
                    logger.error(f"Failed analyzing {file_info['path']}: {e}")
                    file_results.append(FileReviewResult(
                        file_path=file_info['path'],
                        language=file_info.get('language', 'Unknown'),
                        error=str(e),
                    ))
                
                processed += 1
                if progress_callback:
                    progress_callback(processed, file_info['path'])
        
        duration = time.time() - start_time
        
        # Build project-level result
        project_result = ProjectReviewResult(
            project_path=project_path,
            file_results=file_results,
            duration_seconds=duration,
        )
        
        return project_result.to_dict()
    
    def _calc_performance_score(self, features: Features, issues: list[Issue]) -> float:
        """Derive performance score from features and issues."""
        score = 100.0
        
        # Penalize for performance issues
        perf_issues = [i for i in issues if i.category == 'performance']
        score -= len([i for i in perf_issues if i.severity == 'CRITICAL']) * 20
        score -= len([i for i in perf_issues if i.severity == 'HIGH']) * 12
        score -= len([i for i in perf_issues if i.severity == 'MEDIUM']) * 6
        score -= len([i for i in perf_issues if i.severity == 'LOW']) * 2
        
        # Penalize for nested loops
        score -= min(20.0, features.nested_loops * 5)
        score -= min(10.0, features.nested_iterations * 3)
        
        return max(0.0, min(100.0, score))
