"""
Search API Routes
=================
Global search across files, issues, and analysis results.
"""

from flask import Blueprint, jsonify, request
from loguru import logger
from database.repository import AnalysisRepository, get_db_session

search_bp = Blueprint('search', __name__)


@search_bp.route('/', methods=['GET'])
def global_search():
    """
    Search issues and files across all analyses.
    
    Query params:
        q: str           — search query
        severity: str    — filter by severity (critical|high|medium|low|info)
        language: str    — filter by language
        category: str    — filter by issue category
        limit: int       — max results (default 50)
    """
    q = request.args.get('q', '').strip()
    severity = request.args.get('severity', '').lower()
    language = request.args.get('language', '')
    category = request.args.get('category', '')
    limit = min(int(request.args.get('limit', 50)), 200)
    
    try:
        with get_db_session() as session:
            repo = AnalysisRepository(session)
            results = repo.search_issues(
                query=q,
                severity=severity or None,
                language=language or None,
                category=category or None,
                limit=limit,
            )
            return jsonify({
                "query": q,
                "total": len(results),
                "results": results,
            })
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return jsonify({"error": str(e)}), 500
