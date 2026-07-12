"""
File Utilities
==============
Helpers for discovering and filtering source files in a project directory.
Respects exclusion rules from application config.
"""

import os
import fnmatch
from typing import Optional, Callable
from loguru import logger

from utils.language_detector import detect_language, get_all_supported_extensions


def collect_source_files(
    project_path: str,
    config=None,
    progress_callback: Optional[Callable[[int], None]] = None,
) -> list[dict]:
    """
    Recursively collect all supported source files in a project directory.
    
    Args:
        project_path: Root directory to scan.
        config: Application config with exclusion rules.
        progress_callback: Optional callback(count) called every 100 files found.
    
    Returns:
        List of file info dicts: {path, relative_path, language, size, extension}
    """
    if not os.path.isdir(project_path):
        raise ValueError(f"Not a directory: {project_path}")
    
    # Get exclusion rules from config or use defaults
    excluded_dirs = set(getattr(config, 'EXCLUDED_DIRS', [
        'node_modules', '.git', '__pycache__', 'venv', '.venv',
        'env', 'dist', 'build', '.next', 'coverage',
    ]))
    excluded_patterns = getattr(config, 'EXCLUDED_PATTERNS', [
        '*.min.js', '*.min.css', '*.map', '*.lock',
    ])
    max_file_size_mb = getattr(config, 'MAX_FILE_SIZE_MB', 10)
    max_files = getattr(config, 'MAX_FILES_PER_PROJECT', 5000)
    supported_exts = set(get_all_supported_extensions())
    
    files = []
    
    for root, dirs, filenames in os.walk(project_path, topdown=True):
        # Prune excluded directories (in-place to stop os.walk from descending)
        dirs[:] = [
            d for d in dirs
            if d not in excluded_dirs and not d.startswith('.')
        ]
        
        for filename in filenames:
            if len(files) >= max_files:
                logger.warning(f"Reached max file limit ({max_files}). Stopping scan.")
                return files
            
            # Skip excluded patterns
            if any(fnmatch.fnmatch(filename, pat) for pat in excluded_patterns):
                continue
            
            # Check extension
            ext = os.path.splitext(filename)[1].lower()
            if ext not in supported_exts:
                continue
            
            file_path = os.path.join(root, filename)
            
            # Skip oversized files
            try:
                size = os.path.getsize(file_path)
                if size > max_file_size_mb * 1024 * 1024:
                    logger.debug(f"Skipping oversized file: {file_path} ({size / 1024 / 1024:.1f} MB)")
                    continue
                if size == 0:
                    continue
            except OSError:
                continue
            
            # Detect language
            language = detect_language(file_path)
            if not language:
                continue
            
            relative_path = os.path.relpath(file_path, project_path)
            files.append({
                "path": file_path,
                "relative_path": relative_path,
                "language": language,
                "size": size,
                "extension": ext,
                "filename": filename,
            })
            
            if progress_callback and len(files) % 100 == 0:
                progress_callback(len(files))
    
    return files


def get_language_stats(files: list[dict]) -> dict[str, dict]:
    """
    Compute language distribution from a list of file info dicts.
    
    Returns:
        {language: {count, percentage, total_size}}
    """
    total = len(files)
    if total == 0:
        return {}
    
    stats: dict[str, dict] = {}
    for f in files:
        lang = f.get('language', 'Unknown')
        if lang not in stats:
            stats[lang] = {'count': 0, 'total_size': 0}
        stats[lang]['count'] += 1
        stats[lang]['total_size'] += f.get('size', 0)
    
    for lang, data in stats.items():
        data['percentage'] = round(data['count'] / total * 100, 1)
    
    return dict(sorted(stats.items(), key=lambda x: x[1]['count'], reverse=True))


def read_file_content(file_path: str) -> str:
    """
    Read file content with encoding fallback.
    Tries UTF-8 first, then latin-1 as fallback.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='strict') as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin-1', errors='replace') as f:
            return f.read()
    except Exception as e:
        logger.warning(f"Could not read file {file_path}: {e}")
        return ""


def get_file_lines(file_path: str) -> list[str]:
    """Read file and return list of lines (preserving newlines)."""
    content = read_file_content(file_path)
    return content.splitlines(keepends=True)


def format_size(size_bytes: int) -> str:
    """Human-readable file size string."""
    for unit in ('B', 'KB', 'MB', 'GB'):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes //= 1024
    return f"{size_bytes:.1f} TB"
