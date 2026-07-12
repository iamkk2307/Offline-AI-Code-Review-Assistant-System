import os
import tempfile
import pytest

from utils.language_detector import (
    detect_language,
    get_language_from_extension,
    get_all_supported_extensions,
    get_supported_languages
)

def test_extension_map():
    assert get_language_from_extension('.py') == 'Python'
    assert get_language_from_extension('py') == 'Python'
    assert get_language_from_extension('.java') == 'Java'
    assert get_language_from_extension('.js') == 'JavaScript'
    assert get_language_from_extension('.ts') == 'TypeScript'
    assert get_language_from_extension('.sh') == 'Bash'
    assert get_language_from_extension('.json') == 'JSON'
    assert get_language_from_extension('.xyz') is None

def test_supported_lists():
    exts = get_all_supported_extensions()
    assert '.py' in exts
    assert '.java' in exts
    
    langs = get_supported_languages()
    assert 'Python' in langs
    assert 'Java' in langs
    assert 'C++' in langs

def test_disambiguate_c_cpp():
    f1 = tempfile.NamedTemporaryFile(suffix='.h', mode='w', delete=False)
    f1.write("#include <iostream>\nstd::cout << 'hello';")
    f1.close()
    cpp_path = f1.name
    
    f2 = tempfile.NamedTemporaryFile(suffix='.h', mode='w', delete=False)
    f2.write("int main();\nvoid test();")
    f2.close()
    c_path = f2.name
        
    try:
        assert detect_language(cpp_path) == 'C++'
        assert detect_language(c_path) == 'C'
    finally:
        os.remove(cpp_path)
        os.remove(c_path)

def test_detect_from_content():
    f1 = tempfile.NamedTemporaryFile(suffix='', mode='w', delete=False)
    f1.write("#!/usr/bin/env python\nprint('hello')")
    f1.close()
    py_path = f1.name
        
    f2 = tempfile.NamedTemporaryFile(suffix='', mode='w', delete=False)
    f2.write("<?php echo 'hello';")
    f2.close()
    php_path = f2.name

    try:
        assert detect_language(py_path) == 'Python'
        assert detect_language(php_path) == 'PHP'
    finally:
        os.remove(py_path)
        os.remove(php_path)
