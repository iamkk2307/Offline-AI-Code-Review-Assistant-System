"""
Language Detector
=================
Detects programming language from file extension and content heuristics.
Supports all 13 languages in the plugin system.
"""

import os
import re
from typing import Optional


# Map file extensions to language names
EXTENSION_MAP: dict[str, str] = {
    '.py':    'Python',
    '.java':  'Java',
    '.js':    'JavaScript',
    '.jsx':   'JavaScript',
    '.mjs':   'JavaScript',
    '.cjs':   'JavaScript',
    '.ts':    'TypeScript',
    '.tsx':   'TypeScript',
    '.mts':   'TypeScript',
    '.c':     'C',
    '.h':     'C',
    '.cpp':   'C++',
    '.hpp':   'C++',
    '.cc':    'C++',
    '.cxx':   'C++',
    '.hxx':   'C++',
    '.cs':    'C#',
    '.php':   'PHP',
    '.html':  'HTML',
    '.htm':   'HTML',
    '.xhtml': 'HTML',
    '.css':   'CSS',
    '.scss':  'CSS',
    '.sass':  'CSS',
    '.less':  'CSS',
    '.sql':   'SQL',
    '.sh':    'Bash',
    '.bash':  'Bash',
    '.zsh':   'Bash',
    '.fish':  'Bash',
    '.json':  'JSON',
    '.jsonc': 'JSON',
}

# Content heuristics: (pattern, language)
CONTENT_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r'^#!.*python',         re.IGNORECASE | re.MULTILINE), 'Python'),
    (re.compile(r'^#!.*/bash',          re.IGNORECASE | re.MULTILINE), 'Bash'),
    (re.compile(r'^#!.*/sh\b',         re.IGNORECASE | re.MULTILINE), 'Bash'),
    (re.compile(r'^\s*<\?php\b',         re.IGNORECASE | re.MULTILINE), 'PHP'),
    (re.compile(r'<!DOCTYPE html>',     re.IGNORECASE),                 'HTML'),
    (re.compile(r'<html\b',            re.IGNORECASE),                 'HTML'),
    (re.compile(r'^\s*import java\.',   re.MULTILINE),                 'Java'),
    (re.compile(r'^\s*package\s+\w+;',  re.MULTILINE),                 'Java'),
    (re.compile(r'^\s*using System',    re.MULTILINE),                 'C#'),
    (re.compile(r'^\s*namespace\s+\w+', re.MULTILINE),                 'C#'),
    (re.compile(r'^\s*#include\s*<',    re.MULTILINE),                 'C'),
    (re.compile(r'^\s*SELECT\s+\w+',    re.IGNORECASE | re.MULTILINE), 'SQL'),
    (re.compile(r'^\s*CREATE TABLE',    re.IGNORECASE | re.MULTILINE), 'SQL'),
    (re.compile(r'^\s*\{',             re.MULTILINE),                 'JSON'),
]


def detect_language(file_path: str) -> Optional[str]:
    """
    Detect programming language for a file.
    
    Strategy:
    1. Check file extension (fast, reliable for most cases)
    2. Fall back to content heuristics for ambiguous cases
    
    Args:
        file_path: Absolute path to the file.
    
    Returns:
        Language name (e.g., 'Python', 'Java') or None if unrecognized.
    """
    # Step 1: Extension-based detection
    ext = os.path.splitext(file_path)[1].lower()
    if ext in EXTENSION_MAP:
        # Disambiguate .h files: C vs C++
        if ext == '.h':
            return _disambiguate_c_cpp(file_path)
        return EXTENSION_MAP[ext]
    
    # Step 2: Content heuristics for extensionless or unusual files
    return _detect_from_content(file_path)


def _disambiguate_c_cpp(file_path: str) -> str:
    """
    Determine if a .h file belongs to C or C++ based on content.
    Looks for C++ specific keywords.
    """
    try:
        content = _read_sample(file_path, 2048)
        cpp_indicators = ['class ', 'namespace ', 'template<', '#include <iostream>',
                          'std::', 'virtual ', 'override', 'nullptr']
        if any(indicator in content for indicator in cpp_indicators):
            return 'C++'
    except Exception:
        pass
    return 'C'


def _detect_from_content(file_path: str) -> Optional[str]:
    """Apply content heuristics to detect language."""
    try:
        content = _read_sample(file_path, 4096)
        for pattern, language in CONTENT_PATTERNS:
            if pattern.search(content):
                return language
    except Exception:
        pass
    return None


def _read_sample(file_path: str, max_bytes: int = 4096) -> str:
    """Read first N bytes of a file as text."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read(max_bytes)


def get_language_from_extension(ext: str) -> Optional[str]:
    """Return language name for a file extension string (with or without dot)."""
    if not ext.startswith('.'):
        ext = '.' + ext
    return EXTENSION_MAP.get(ext.lower())


def get_all_supported_extensions() -> list[str]:
    """Return all supported file extensions."""
    return list(EXTENSION_MAP.keys())


def get_supported_languages() -> list[str]:
    """Return list of unique supported language names."""
    return sorted(set(EXTENSION_MAP.values()))
