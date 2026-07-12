"""
Server Configuration
====================
Environment-based configuration for the Flask backend.
All paths resolve relative to the project root.
"""

import os
from dataclasses import dataclass, field


def _project_root() -> str:
    """Return the absolute path to the project root directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@dataclass
class Config:
    """
    Application configuration with sensible defaults.
    All values can be overridden by environment variables.
    """
    # Application metadata
    APP_NAME: str = "Offline Code Review Assistant"
    APP_VERSION: str = "1.0.0"
    
    # Server settings
    HOST: str = field(default_factory=lambda: os.getenv('HOST', '127.0.0.1'))
    PORT: int = field(default_factory=lambda: int(os.getenv('PORT', '5000')))
    DEBUG: bool = field(default_factory=lambda: os.getenv('DEBUG', 'false').lower() == 'true')
    SECRET_KEY: str = field(default_factory=lambda: os.getenv('SECRET_KEY', 'offline-code-review-secret-2024'))
    
    # Paths
    PROJECT_ROOT: str = field(default_factory=_project_root)
    
    @property
    def DATA_DIR(self) -> str:
        """User data directory for databases, logs, and reports."""
        data_dir = os.path.join(self.PROJECT_ROOT, 'data')
        os.makedirs(data_dir, exist_ok=True)
        return data_dir
    
    @property
    def DATABASE_URL(self) -> str:
        """SQLite database connection string."""
        db_path = os.path.join(self.DATA_DIR, 'code_review.db')
        return f"sqlite:///{db_path}"
    
    @property
    def MODELS_DIR(self) -> str:
        """Directory containing pre-trained ML model files."""
        return os.path.join(self.PROJECT_ROOT, 'ml', 'models')
    
    @property
    def REPORTS_OUTPUT_DIR(self) -> str:
        """Default directory for generated reports."""
        reports_dir = os.path.join(self.DATA_DIR, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        return reports_dir
    
    # Logging
    LOG_LEVEL: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))
    
    # Analysis settings
    MAX_FILE_SIZE_MB: int = 10          # Skip files larger than this
    MAX_FILES_PER_PROJECT: int = 5000  # Hard cap on files analyzed
    ANALYSIS_TIMEOUT_SEC: int = 300    # Max time for full project analysis
    MAX_WORKERS: int = 4               # Background analysis threads
    
    # Feature extraction
    MIN_FUNCTION_LENGTH_WARNING: int = 50   # Lines that trigger "long method"
    MAX_NESTING_DEPTH_WARNING: int = 4      # Nesting depth that triggers warning
    MAX_PARAMETERS_WARNING: int = 7         # Parameter count that triggers warning
    MAX_CLASS_METHODS_WARNING: int = 20     # Methods count that triggers warning
    
    # Code Health weights (must sum to 1.0)
    WEIGHT_QUALITY: float = 0.30
    WEIGHT_SECURITY: float = 0.25
    WEIGHT_MAINTAINABILITY: float = 0.20
    WEIGHT_PERFORMANCE: float = 0.15
    WEIGHT_READABILITY: float = 0.10
    
    # Supported file extensions → language mapping
    LANGUAGE_EXTENSIONS: dict = field(default_factory=lambda: {
        '.py':    'Python',
        '.java':  'Java',
        '.js':    'JavaScript',
        '.jsx':   'JavaScript',
        '.ts':    'TypeScript',
        '.tsx':   'TypeScript',
        '.c':     'C',
        '.h':     'C',
        '.cpp':   'C++',
        '.hpp':   'C++',
        '.cc':    'C++',
        '.cs':    'C#',
        '.php':   'PHP',
        '.html':  'HTML',
        '.htm':   'HTML',
        '.css':   'CSS',
        '.scss':  'CSS',
        '.sql':   'SQL',
        '.sh':    'Bash',
        '.bash':  'Bash',
        '.json':  'JSON',
    })
    
    # Directories to skip during analysis
    EXCLUDED_DIRS: list = field(default_factory=lambda: [
        'node_modules', '.git', '__pycache__', 'venv', '.venv',
        'env', 'dist', 'build', '.next', 'coverage', '.pytest_cache',
        '.mypy_cache', 'target', 'bin', 'obj', '.idea', '.vscode',
        'vendor', 'packages', 'bower_components',
    ])
    
    # Files to skip
    EXCLUDED_PATTERNS: list = field(default_factory=lambda: [
        '*.min.js', '*.min.css', '*.map', '*.lock',
        'package-lock.json', 'yarn.lock', '*.generated.*',
    ])


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG: bool = True
    LOG_LEVEL: str = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG: bool = False
    LOG_LEVEL: str = 'WARNING'


def get_config() -> Config:
    """Return appropriate config based on environment."""
    env = os.getenv('FLASK_ENV', 'production')
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
    }
    return configs.get(env, Config)()
