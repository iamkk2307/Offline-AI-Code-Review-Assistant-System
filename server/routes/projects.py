"""
Projects API Routes
===================
Handles project (workspace) CRUD operations.
"""

import os
from flask import Blueprint, jsonify, request, current_app
from loguru import logger

from database.repository import ProjectRepository, get_db_session

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/', methods=['GET'])
def list_projects():
    """Return all saved projects ordered by last accessed."""
    try:
        with get_db_session() as session:
            repo = ProjectRepository(session)
            projects = repo.get_all()
            return jsonify([p.to_dict() for p in projects])
    except Exception as e:
        logger.error(f"Failed to list projects: {e}")
        return jsonify({"error": str(e)}), 500


@projects_bp.route('/', methods=['POST'])
def create_project():
    """
    Create a new project workspace.
    
    Body:
        name: str — project display name
        path: str — absolute path to the project folder
    """
    data = request.get_json()
    if not data or 'path' not in data:
        return jsonify({"error": "Missing required field: path"}), 400
    
    project_path = data['path']
    if not os.path.isdir(project_path):
        # Fallback check: check if it exists relative to the project workspace root
        from server.app import ROOT_DIR
        folder_name = os.path.basename(project_path.replace('\\', '/').rstrip('/'))
        fallback_path = os.path.join(ROOT_DIR, folder_name)
        if os.path.isdir(fallback_path):
            project_path = fallback_path
        else:
            return jsonify({"error": f"Directory not found: {project_path}"}), 400
    
    name = data.get('name', os.path.basename(project_path))
    
    try:
        with get_db_session() as session:
            repo = ProjectRepository(session)
            # Check if project already exists
            existing = repo.get_by_path(project_path)
            if existing:
                return jsonify(existing.to_dict()), 200
            
            project = repo.create(name=name, path=project_path)
            logger.info(f"Created project: {name} at {project_path}")
            return jsonify(project.to_dict()), 201
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        return jsonify({"error": str(e)}), 500


@projects_bp.route('/<int:project_id>', methods=['GET'])
def get_project(project_id: int):
    """Get project by ID."""
    try:
        with get_db_session() as session:
            repo = ProjectRepository(session)
            project = repo.get_by_id(project_id)
            if not project:
                return jsonify({"error": "Project not found"}), 404
            return jsonify(project.to_dict())
    except Exception as e:
        logger.error(f"Failed to get project {project_id}: {e}")
        return jsonify({"error": str(e)}), 500


@projects_bp.route('/<int:project_id>', methods=['DELETE'])
def delete_project(project_id: int):
    """Delete a project and all associated analysis results."""
    try:
        with get_db_session() as session:
            repo = ProjectRepository(session)
            success = repo.delete(project_id)
            if not success:
                return jsonify({"error": "Project not found"}), 404
            logger.info(f"Deleted project {project_id}")
            return jsonify({"message": "Project deleted successfully"})
    except Exception as e:
        logger.error(f"Failed to delete project {project_id}: {e}")
        return jsonify({"error": str(e)}), 500


@projects_bp.route('/<int:project_id>/files', methods=['GET'])
def get_project_files(project_id: int):
    """
    List all source files in a project directory.
    Respects exclusion rules from config.
    """
    try:
        with get_db_session() as session:
            repo = ProjectRepository(session)
            project = repo.get_by_id(project_id)
            if not project:
                return jsonify({"error": "Project not found"}), 404
        
        cfg = current_app.config.get('CONFIG')
        from utils.file_utils import collect_source_files
        files = collect_source_files(project.path, cfg)
        
        return jsonify({
            "project_id": project_id,
            "total_files": len(files),
            "files": files[:200],  # Return first 200 for listing
        })
    except Exception as e:
        logger.error(f"Failed to get files for project {project_id}: {e}")
        return jsonify({"error": str(e)}), 500


@projects_bp.route('/<int:project_id>/stats', methods=['GET'])
def get_project_stats(project_id: int):
    """Return language distribution and file count statistics."""
    try:
        with get_db_session() as session:
            repo = ProjectRepository(session)
            project = repo.get_by_id(project_id)
            if not project:
                return jsonify({"error": "Project not found"}), 404
        
        from utils.file_utils import collect_source_files, get_language_stats
        from server.config import Config
        cfg = Config()
        files = collect_source_files(project.path, cfg)
        stats = get_language_stats(files)
        
        return jsonify({
            "project_id": project_id,
            "total_files": len(files),
            "language_distribution": stats,
        })
    except Exception as e:
        logger.error(f"Failed to get stats for project {project_id}: {e}")
        return jsonify({"error": str(e)}), 500
