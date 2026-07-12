"""
Analysis API Routes
===================
Handles code analysis requests, progress tracking, and results retrieval.
Uses background threads for heavy analysis work.
"""

import os
import threading
import uuid
from flask import Blueprint, jsonify, request, current_app
from loguru import logger

from database.repository import ProjectRepository, AnalysisRepository, get_db_session

analysis_bp = Blueprint('analysis', __name__)

# In-memory analysis job tracker {job_id: {status, progress, result, error}}
_analysis_jobs: dict = {}
_jobs_lock = threading.Lock()


@analysis_bp.route('/start', methods=['POST'])
def start_analysis():
    """
    Start a full analysis of a project asynchronously.
    
    Body:
        project_id: int — ID of the project to analyze
        options: dict  — optional analysis settings
    
    Returns:
        job_id: str — UUID to poll for progress
    """
    data = request.get_json()
    if not data or 'project_id' not in data:
        return jsonify({"error": "Missing required field: project_id"}), 400
    
    project_id = data['project_id']
    options = data.get('options', {})
    
    # Validate project exists
    try:
        with get_db_session() as session:
            repo = ProjectRepository(session)
            project = repo.get_by_id(project_id)
            if not project:
                return jsonify({"error": f"Project {project_id} not found"}), 404
            project_path = project.path
            project_name = project.name
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    # Create job
    job_id = str(uuid.uuid4())
    with _jobs_lock:
        _analysis_jobs[job_id] = {
            "job_id": job_id,
            "project_id": project_id,
            "status": "queued",
            "progress": 0,
            "current_file": None,
            "total_files": 0,
            "processed_files": 0,
            "result_id": None,
            "error": None,
        }
    
    # Start background analysis thread
    thread = threading.Thread(
        target=_run_analysis,
        args=(job_id, project_id, project_path, project_name, options, current_app._get_current_object()),
        daemon=True,
    )
    thread.start()
    
    logger.info(f"Started analysis job {job_id} for project {project_id}")
    return jsonify({"job_id": job_id, "status": "queued"}), 202


@analysis_bp.route('/status/<job_id>', methods=['GET'])
def get_job_status(job_id: str):
    """Poll analysis job status and progress."""
    with _jobs_lock:
        job = _analysis_jobs.get(job_id)
    
    if not job:
        return jsonify({"error": "Job not found"}), 404
    
    return jsonify(job)


@analysis_bp.route('/results/<int:analysis_id>', methods=['GET'])
def get_analysis_result(analysis_id: int):
    """Retrieve a completed analysis result by ID."""
    try:
        with get_db_session() as session:
            repo = AnalysisRepository(session)
            result = repo.get_by_id(analysis_id)
            if not result:
                return jsonify({"error": "Analysis result not found"}), 404
            return jsonify(result.to_dict())
    except Exception as e:
        logger.error(f"Failed to get analysis result {analysis_id}: {e}")
        return jsonify({"error": str(e)}), 500


@analysis_bp.route('/project/<int:project_id>/history', methods=['GET'])
def get_analysis_history(project_id: int):
    """Get analysis history for a project."""
    try:
        with get_db_session() as session:
            repo = AnalysisRepository(session)
            results = repo.get_by_project(project_id, limit=20)
            return jsonify([r.to_summary_dict() for r in results])
    except Exception as e:
        logger.error(f"Failed to get history for project {project_id}: {e}")
        return jsonify({"error": str(e)}), 500


@analysis_bp.route('/project/<int:project_id>/latest', methods=['GET'])
def get_latest_analysis(project_id: int):
    """Get the most recent analysis result for a project."""
    try:
        with get_db_session() as session:
            repo = AnalysisRepository(session)
            result = repo.get_latest_by_project(project_id)
            if not result:
                return jsonify({"error": "No analysis found for this project"}), 404
            return jsonify(result.to_dict())
    except Exception as e:
        logger.error(f"Failed to get latest analysis for project {project_id}: {e}")
        return jsonify({"error": str(e)}), 500


@analysis_bp.route('/file', methods=['POST'])
def analyze_single_file():
    """
    Analyze a single file (synchronous — fast path for quick checks).
    
    Body:
        file_path: str — absolute path to file
    """
    data = request.get_json()
    if not data or 'file_path' not in data:
        return jsonify({"error": "Missing required field: file_path"}), 400
    
    file_path = data['file_path']
    if not os.path.isfile(file_path):
        return jsonify({"error": f"File not found: {file_path}"}), 400
    
    try:
        model_manager = current_app.config.get('MODEL_MANAGER')
        from review_engine.engine import ReviewEngine
        from server.config import Config
        
        engine = ReviewEngine(model_manager=model_manager, config=Config())
        result = engine.analyze_file(file_path)
        return jsonify(result.to_dict())
    except Exception as e:
        logger.error(f"Failed to analyze file {file_path}: {e}")
        return jsonify({"error": str(e)}), 500


def _run_analysis(job_id: str, project_id: int, project_path: str,
                  project_name: str, options: dict, app) -> None:
    """
    Background worker: runs the full project analysis pipeline.
    Updates job status in _analysis_jobs dict throughout execution.
    """
    def update_job(**kwargs):
        with _jobs_lock:
            _analysis_jobs[job_id].update(kwargs)
    
    try:
        update_job(status='running', progress=5)
        
        with app.app_context():
            from review_engine.engine import ReviewEngine
            from utils.file_utils import collect_source_files
            from server.config import Config
            
            cfg = Config()
            model_manager = app.config.get('MODEL_MANAGER')
            engine = ReviewEngine(model_manager=model_manager, config=cfg)
            
            # Collect files
            update_job(status='collecting_files', progress=10)
            files = collect_source_files(project_path, cfg)
            total = len(files)
            update_job(total_files=total, progress=15)
            
            if total == 0:
                update_job(status='completed', progress=100,
                           error="No supported source files found in project.")
                return
            
            logger.info(f"Job {job_id}: analyzing {total} files")
            
            # Run analysis with progress callback
            def on_progress(processed: int, current_file: str):
                pct = 15 + int((processed / total) * 75)
                update_job(
                    processed_files=processed,
                    current_file=os.path.basename(current_file),
                    progress=pct,
                )
            
            project_result = engine.analyze_project(
                project_path=project_path,
                files=files,
                progress_callback=on_progress,
            )
            
            # Save to database
            update_job(status='saving', progress=92)
            with get_db_session() as session:
                repo = AnalysisRepository(session)
                record = repo.save_project_analysis(project_id, project_result)
                result_id = record.id
                
                # Update project last analyzed
                proj_repo = ProjectRepository(session)
                proj_repo.update_last_analyzed(project_id)
            
            update_job(
                status='completed',
                progress=100,
                result_id=result_id,
                processed_files=total,
            )
            logger.info(f"Job {job_id} completed. Result ID: {result_id}")
    
    except Exception as e:
        logger.error(f"Analysis job {job_id} failed: {e}")
        update_job(status='failed', error=str(e), progress=0)
