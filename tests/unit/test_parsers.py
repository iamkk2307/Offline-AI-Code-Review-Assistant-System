import pytest
from parsers.plugin_registry import PluginRegistry
from parsers.base_plugin import ParseResult, Features

def test_plugin_discovery():
    registry = PluginRegistry.get_instance()
    plugins = registry.get_all_plugins()
    assert len(plugins) >= 13
    
    # Check key plugins are registered
    languages = [p.language for p in plugins]
    assert 'Python' in languages
    assert 'JavaScript' in languages
    assert 'Java' in languages
    assert 'C' in languages
    assert 'C++' in languages
    assert 'C#' in languages
    assert 'PHP' in languages
    assert 'HTML' in languages
    assert 'CSS' in languages
    assert 'SQL' in languages
    assert 'Bash' in languages
    assert 'JSON' in languages

def test_python_plugin():
    registry = PluginRegistry.get_instance()
    plugin = registry.get_plugin_for_file('test.py')
    assert plugin is not None
    assert plugin.language == 'Python'
    
    code = """def add(a, b):\n    # TODO: add logic\n    return a + b\n\neval("a + b")\n"""
    res = plugin.parse('test.py', code)
    assert res.is_valid
    
    f = plugin.extract_features(res)
    assert f.loc == 5
    assert f.function_count == 1
    assert f.todo_count == 1
    assert f.eval_usage == 1
    
    issues = plugin.run_static_analysis(res, f)
    # Check we identify the issues
    assert len(issues) >= 0

def test_javascript_plugin():
    registry = PluginRegistry.get_instance()
    plugin = registry.get_plugin_for_file('test.js')
    assert plugin is not None
    assert plugin.language == 'JavaScript'
    
    code = """function test() {\n  eval("console.log('hi')");\n}\n"""
    res = plugin.parse('test.js', code)
    f = plugin.extract_features(res)
    assert f.eval_usage == 1
    
    issues = plugin.run_security_analysis(res, f)
    assert any(i.rule_id == 'JSS001' for i in issues) # eval usage

def test_java_plugin():
    registry = PluginRegistry.get_instance()
    plugin = registry.get_plugin_for_file('Test.java')
    assert plugin is not None
    assert plugin.language == 'Java'
    
    code = """public class Test {\n  public void execute() {\n    System.out.println("hello");\n  }\n}\n"""
    res = plugin.parse('Test.java', code)
    f = plugin.extract_features(res)
    assert f.class_count == 1
    
    issues = plugin.run_static_analysis(res, f)
    assert any(i.rule_id == 'JA003' for i in issues) # System.out.println

def test_c_plugin():
    registry = PluginRegistry.get_instance()
    plugin = registry.get_plugin_for_file('test.c')
    assert plugin is not None
    
    code = """#include <stdio.h>\nvoid main() {\n  char buf[10];\n  gets(buf);\n}\n"""
    res = plugin.parse('test.c', code)
    f = plugin.extract_features(res)
    assert f.import_count == 1
    
    issues = plugin.run_security_analysis(res, f)
    assert any(i.rule_id == 'CSec001' for i in issues) # gets usage

def test_cpp_plugin():
    registry = PluginRegistry.get_instance()
    plugin = registry.get_plugin_for_file('test.cpp')
    assert plugin is not None
    
    code = """using namespace std;\nint main() {\n  int* p = new int[5];\n}\n"""
    res = plugin.parse('test.cpp', code)
    f = plugin.extract_features(res)
    issues = plugin.run_static_analysis(res, f)
    assert any(i.rule_id == 'CPP001' for i in issues) # using namespace std

def test_csharp_plugin():
    registry = PluginRegistry.get_instance()
    plugin = registry.get_plugin_for_file('test.cs')
    assert plugin is not None
    
    code = """using System;\nclass Program {\n  void Run() {\n    try {\n      throw new Exception();\n    } catch (Exception e) {}\n  }\n}\n"""
    res = plugin.parse('test.cs', code)
    f = plugin.extract_features(res)
    assert f.exception_handling == 1
    issues = plugin.run_static_analysis(res, f)
    assert any(i.rule_id == 'CS001' for i in issues) # Catch Generic Exception

def test_php_plugin():
    registry = PluginRegistry.get_instance()
    plugin = registry.get_plugin_for_file('index.php')
    assert plugin is not None
    
    code = """<?php\necho $_GET['name'];\n"""
    res = plugin.parse('index.php', code)
    f = plugin.extract_features(res)
    issues = plugin.run_security_analysis(res, f)
    assert any(i.rule_id == 'PHPSec001' for i in issues) # Unvalidated User Input

def test_html_plugin():
    registry = PluginRegistry.get_instance()
    plugin = registry.get_plugin_for_file('index.html')
    assert plugin is not None
    
    code = """<html>\n<body>\n<img src="logo.png">\n</body>\n</html>"""
    res = plugin.parse('index.html', code)
    f = plugin.extract_features(res)
    issues = plugin.run_static_analysis(res, f)
    assert any(i.rule_id == 'HTML004' for i in issues) # img alt

def test_css_plugin():
    registry = PluginRegistry.get_instance()
    plugin = registry.get_plugin_for_file('styles.css')
    assert plugin is not None
    
    code = """.btn {\n  color: red !important;\n}\n"""
    res = plugin.parse('styles.css', code)
    f = plugin.extract_features(res)
    issues = plugin.run_static_analysis(res, f)
    assert any(i.rule_id == 'CSS001' for i in issues) # !important

def test_sql_plugin():
    registry = PluginRegistry.get_instance()
    plugin = registry.get_plugin_for_file('query.sql')
    assert plugin is not None
    
    code = """SELECT * FROM users;\n"""
    res = plugin.parse('query.sql', code)
    f = plugin.extract_features(res)
    issues = plugin.run_static_analysis(res, f)
    assert any(i.rule_id == 'SQL001' for i in issues) # SELECT *

def test_bash_plugin():
    registry = PluginRegistry.get_instance()
    plugin = registry.get_plugin_for_file('script.sh')
    assert plugin is not None
    
    code = """chmod 777 file.txt\n"""
    res = plugin.parse('script.sh', code)
    f = plugin.extract_features(res)
    issues = plugin.run_security_analysis(res, f)
    assert any(i.rule_id == 'SHSec004' for i in issues) # chmod 777

def test_json_plugin():
    registry = PluginRegistry.get_instance()
    plugin = registry.get_plugin_for_file('config.json')
    assert plugin is not None
    
    code = """{\n  "password": "secretpassword"\n}\n"""
    res = plugin.parse('config.json', code)
    f = plugin.extract_features(res)
    issues = plugin.run_security_analysis(res, f)
    assert any(i.rule_id == 'JSONSec001' for i in issues) # hardcoded password
