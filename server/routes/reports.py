"""
Reports API Routes
==================
Handles report generation and download in multiple formats.
"""

import os
from flask import Blueprint, jsonify, request, send_file, current_app
from loguru import logger

from database.repository import AnalysisRepository, get_db_session

reports_bp = Blueprint('reports', __name__)

SUPPORTED_FORMATS = {'pdf', 'html', 'markdown', 'json', 'csv'}


@reports_bp.route('/generate', methods=['POST'])
def generate_report():
    """
    Generate a report for a completed analysis.
    
    Body:
        analysis_id: int     — analysis result ID
        format: str          — 'pdf' | 'html' | 'markdown' | 'json' | 'csv'
        output_path: str     — optional custom output path
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    
    analysis_id = data.get('analysis_id')
    fmt = data.get('format', 'html').lower()
    
    if not analysis_id:
        return jsonify({"error": "Missing required field: analysis_id"}), 400
    if fmt not in SUPPORTED_FORMATS:
        return jsonify({"error": f"Unsupported format. Choose from: {', '.join(SUPPORTED_FORMATS)}"}), 400
    
    try:
        with get_db_session() as session:
            repo = AnalysisRepository(session)
            result = repo.get_by_id(analysis_id)
            if not result:
                return jsonify({"error": "Analysis not found"}), 404
            analysis_data = result.to_dict()
        
        from reports.report_factory import ReportFactory
        from server.config import Config
        
        cfg = Config()
        output_path = data.get('output_path', cfg.REPORTS_OUTPUT_DIR)
        
        generator = ReportFactory.create(fmt)
        file_path = generator.generate(analysis_data, output_path)
        
        logger.info(f"Generated {fmt} report: {file_path}")
        return jsonify({
            "success": True,
            "format": fmt,
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
        })
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        return jsonify({"error": str(e)}), 500


@reports_bp.route('/download/<path:file_path>', methods=['GET'])
def download_report(file_path: str):
    """Download a generated report file."""
    if not os.path.isfile(file_path):
        return jsonify({"error": "Report file not found"}), 404
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=os.path.basename(file_path),
    )


@reports_bp.route('/list', methods=['GET'])
def list_reports():
    """List recently generated reports from the output directory."""
    from server.config import Config
    cfg = Config()
    reports_dir = cfg.REPORTS_OUTPUT_DIR
    
    try:
        files = []
        for fname in os.listdir(reports_dir):
            fpath = os.path.join(reports_dir, fname)
            if os.path.isfile(fpath):
                stat = os.stat(fpath)
                files.append({
                    "name": fname,
                    "path": fpath,
                    "size": stat.st_size,
                    "created": stat.st_ctime,
                    "format": os.path.splitext(fname)[1].lstrip('.'),
                })
        files.sort(key=lambda x: x['created'], reverse=True)
        return jsonify(files[:50])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
