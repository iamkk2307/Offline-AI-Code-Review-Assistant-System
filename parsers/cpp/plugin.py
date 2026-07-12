"""
C++ Language Plugin
===================
Extends C plugin with C++-specific rules.
"""

import re
from parsers.base_plugin import BaseLanguagePlugin, ParseResult, Features, Issue
from parsers.c.plugin import CPlugin


class CppPlugin(BaseLanguagePlugin):
    @property
    def language(self) -> str:
        return 'C++'
    
    @property
    def file_extensions(self) -> list[str]:
        return ['.cpp', '.hpp', '.cc', '.cxx', '.hxx']
    
    def parse(self, file_path: str, content: str) -> ParseResult:
        c = CPlugin()
        result = c.parse(file_path, content)
        result.language = 'C++'
        return result
    
    def extract_features(self, parse_result: ParseResult) -> Features:
        c = CPlugin()
        c_result = ParseResult(language='C', file_path=parse_result.file_path, content=parse_result.content, lines=parse_result.lines)
        f = c.extract_features(c_result)
        content = parse_result.content
        f.class_count = len(re.findall(r'\bclass\s+\w+', content))
        f.exception_handling = len(re.findall(r'\btry\s*\{', content))
        f.template_count = len(re.findall(r'\btemplate\s*<', content))
        return f
    
    def run_static_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        c = CPlugin()
        c_result = ParseResult(language='C', file_path=parse_result.file_path, content=parse_result.content, lines=parse_result.lines)
        issues = c.run_static_analysis(c_result, features)
        
        lines = parse_result.lines
        for i, line in enumerate(lines, 1):
            if re.search(r'\busing namespace std\b', line):
                issues.append(Issue(title="'using namespace std'", description="Pollutes global namespace and can cause ambiguity.", severity="MEDIUM", category="style", line_number=i, suggestion="Use explicit std:: prefix or selective using declarations.", rule_id="CPP001", code_snippet=line.strip()[:120]))
            if re.search(r'\bnew\s+\w+', line) and 'unique_ptr' not in line and 'shared_ptr' not in line:
                issues.append(Issue(title="Raw new Without Smart Pointer", description="Raw new can lead to memory leaks.", severity="MEDIUM", category="performance", line_number=i, suggestion="Use std::unique_ptr or std::shared_ptr.", rule_id="CPP002", code_snippet=line.strip()[:120]))
        
        return issues
    
    def run_security_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        c = CPlugin()
        c_result = ParseResult(language='C', file_path=parse_result.file_path, content=parse_result.content, lines=parse_result.lines)
        return c.run_security_analysis(c_result, features)
    
    def run_performance_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []
        lines = parse_result.lines
        for i, line in enumerate(lines, 1):
            if re.search(r'\bpush_back\s*\(', line):
                issues.append(Issue(title="push_back vs emplace_back", description="emplace_back can be more efficient.", severity="INFO", category="performance", line_number=i, suggestion="Use emplace_back() to construct in-place.", rule_id="CPPPP001", code_snippet=line.strip()[:120]))
        return issues
