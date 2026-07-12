"""
Offline ML-Based Code Review Assistant — Flask Backend
=======================================================
Entry point for the Python backend server.
Initializes Flask app, registers blueprints, sets up logging.
"""

import os
import sys
from flask import Flask, jsonify
from flask_cors import CORS
from loguru import logger

# Add project root to path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from server.config import Config
from server.routes.projects import projects_bp
from server.routes.analysis import analysis_bp
from server.routes.reports import reports_bp
from server.routes.search import search_bp
from server.routes.settings import settings_bp
from database.db import init_db
from ml.predictors.model_manager import ModelManager


def create_app(config: Config = None) -> Flask:
    """
    Flask application factory.
    
    Args:
        config: Optional configuration object. Uses default if not provided.
    
    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)
    
    # Load configuration
    cfg = config or Config()
    app.config.from_object(cfg)
    
    # Setup CORS — only allow localhost (Electron renderer)
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5173",
                "http://localhost:3000",
                "file://*"
            ]
        }
    })
    
    # Configure logging
    _setup_logging(cfg)
    
    # Initialize database
    with app.app_context():
        init_db(cfg.DATABASE_URL)
        logger.info(f"Database initialized at: {cfg.DATABASE_URL}")
    
    # Load ML models
    model_manager = ModelManager(models_dir=cfg.MODELS_DIR)
    model_manager.load_all()
    app.config['MODEL_MANAGER'] = model_manager
    logger.info(f"Loaded {model_manager.model_count} ML models")
    
    # Register blueprints
    app.register_blueprint(projects_bp, url_prefix='/api/projects')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(reports_bp,  url_prefix='/api/reports')
    app.register_blueprint(search_bp,   url_prefix='/api/search')
    app.register_blueprint(settings_bp, url_prefix='/api/settings')
    
    # Health check endpoint
    @app.route('/api/health')
    def health():
        return jsonify({
            "status": "ok",
            "version": cfg.APP_VERSION,
            "models_loaded": model_manager.model_count,
            "cwd": ROOT_DIR
        })
    
    # Global error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found", "message": str(e)}), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal server error: {e}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500
    
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad request", "message": str(e)}), 400
    
    logger.info(f"Flask app created — version {cfg.APP_VERSION}")
    return app


def _setup_logging(cfg: Config) -> None:
    """Configure loguru logger with file rotation."""
    logger.remove()  # Remove default handler
    
    # Console handler
    logger.add(
        sys.stderr,
        level=cfg.LOG_LEVEL,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> — <level>{message}</level>",
        colorize=True,
    )
    
    # File handler with rotation
    log_path = os.path.join(cfg.DATA_DIR, "logs", "server.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    logger.add(
        log_path,
        level="DEBUG",
        rotation="10 MB",
        retention="1 week",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} — {message}",
    )


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Code Review Assistant Backend')
    parser.add_argument('--port', type=int, default=5000, help='Server port')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()
    
    app = create_app()
    logger.info(f"Starting server on port {args.port}")
    app.run(
        host='127.0.0.1',
        port=args.port,
        debug=args.debug,
        use_reloader=False,  # Disable reloader in production
    )
