"""
Settings API Routes
===================
Manage user preferences and application settings.
"""

import json
import os
from flask import Blueprint, jsonify, request
from loguru import logger

settings_bp = Blueprint('settings', __name__)

_SETTINGS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'data', 'settings.json'
)

DEFAULT_SETTINGS = {
    "theme": "dark",
    "language": "en",
    "report_output_dir": "",
    "auto_save": True,
    "analysis_on_open": False,
    "max_workers": 4,
    "show_info_issues": True,
    "default_report_format": "html",
}


def _load_settings() -> dict:
    """Load settings from JSON file, returning defaults if missing."""
    if os.path.isfile(_SETTINGS_FILE):
        try:
            with open(_SETTINGS_FILE, 'r') as f:
                stored = json.load(f)
                return {**DEFAULT_SETTINGS, **stored}
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def _save_settings(settings: dict) -> None:
    """Persist settings to disk."""
    os.makedirs(os.path.dirname(_SETTINGS_FILE), exist_ok=True)
    with open(_SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)


@settings_bp.route('/', methods=['GET'])
def get_settings():
    """Return current application settings."""
    return jsonify(_load_settings())


@settings_bp.route('/', methods=['PUT'])
def update_settings():
    """Update application settings."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    
    current = _load_settings()
    current.update(data)
    
    try:
        _save_settings(current)
        return jsonify(current)
    except Exception as e:
        logger.error(f"Failed to save settings: {e}")
        return jsonify({"error": str(e)}), 500


@settings_bp.route('/reset', methods=['POST'])
def reset_settings():
    """Reset all settings to defaults."""
    _save_settings(DEFAULT_SETTINGS.copy())
    return jsonify(DEFAULT_SETTINGS)
