"""
C# Language Plugin
==================
Regex-based analysis for C# source files.
"""

import re
import math
from parsers.base_plugin import BaseLanguagePlugin, ParseResult, Features, Issue


class CSharpPlugin(BaseLanguagePlugin):
    @property
    def language(self) -> str:
        return 'C#'
    
    @property
    def file_extensions(self) -> list[str]:
        return ['.cs']
    
    def parse(self, file_path: str, content: str) -> ParseResult:
        lines = content.splitlines(keepends=True)
        errors = []
        if content.count('{') != content.count('}'):
            errors.append("Unbalanced braces.")
        return ParseResult(language='C#', file_path=file_path, content=content, lines=lines, parse_errors=errors, is_valid=True)
    
    def extract_features(self, parse_result: ParseResult) -> Features:
        content = parse_result.content
        lines   = parse_result.lines
        f = Features()
        f.loc = len(lines)
        f.blank_lines = sum(1 for l in lines if l.strip() == '')
        f.comment_lines = sum(1 for l in lines if l.strip().startswith('//') or l.strip().startswith('///'))
        f.sloc = f.loc - f.blank_lines
        f.comment_ratio = f.comment_lines / max(f.loc, 1)
        f.class_count = len(re.findall(r'\b(class|interface|struct|enum)\s+\w+', content))
        f.function_count = len(re.findall(r'\b(public|private|protected|internal|static)\s+[\w<>\[\]]+\s+\w+\s*\(', content))
        f.method_count = f.function_count
        f.import_count = len(re.findall(r'^\s*using\s+[\w.]+\s*;', content, re.MULTILINE))
        f.loop_count = len(re.findall(r'\b(for|foreach|while|do)\s*[\(\{]', content))
        f.conditional_count = len(re.findall(r'\b(if|else if|switch)\s*\(', content))
        f.exception_handling = len(re.findall(r'\btry\s*\{', content))
        f.todo_count = len(re.findall(r'//.*\bTODO\b', content, re.IGNORECASE))
        f.fixme_count = len(re.findall(r'//.*\bFIXME\b', content, re.IGNORECASE))
        f.magic_numbers = len(re.findall(r'\b(?<!\.)(?!0x)\d{2,}\b', content))
        f.sql_queries = len(re.findall(r'\b(SELECT|INSERT|UPDATE|DELETE)\b', content, re.IGNORECASE))
        f.cyclomatic_complexity = float(1 + f.conditional_count + f.loop_count + f.exception_handling)
        operators = re.findall(r'[\+\-\*\/\%\=\<\>\!\&\|\^]+', content)
        operands  = re.findall(r'\b[a-zA-Z_]\w*\b', content)
        n1, n2 = len(set(operators)), len(set(operands))
        N1, N2 = len(operators), len(operands)
        if n1 > 0 and n2 > 0:
            n = n1 + n2; N = N1 + N2
            f.halstead_volume = float(N * math.log2(n)) if n > 1 else 0.0
            f.halstead_difficulty = float((n1 / 2) * (N2 / max(n2, 1)))
            f.halstead_effort = f.halstead_difficulty * f.halstead_volume
            f.halstead_length = float(N)
        if f.halstead_volume > 0 and f.sloc > 0:
            mi = 171 - 5.2 * math.log(max(f.halstead_volume, 1)) - 0.23 * f.cyclomatic_complexity - 16.2 * math.log(max(f.sloc, 1))
            f.maintainability_index = max(0.0, min(100.0, mi))
        return f
    
    def run_static_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []
        lines = parse_result.lines
        
        for i, line in enumerate(lines, 1):
            if re.search(r'\bcatch\s*\(\s*Exception\s+\w+\s*\)', line):
                issues.append(Issue(title="Catch Generic Exception", description="Catching Exception hides specific errors.", severity="MEDIUM", category="bug", line_number=i, suggestion="Catch specific exception types.", rule_id="CS001", code_snippet=line.strip()[:120]))
            if re.search(r'Console\.(Write|WriteLine)\s*\(', line):
                issues.append(Issue(title="Console Output", description="Use ILogger instead of Console output.", severity="INFO", category="style", line_number=i, rule_id="CS002", code_snippet=line.strip()[:120]))
        
        return issues
    
    def run_security_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []
        lines = parse_result.lines
        
        patterns = [
            (r'(password|secret|apikey)\s*=\s*"[^"]{4,}"', "Hardcoded Credential", "CRITICAL", "CSSec001"),
            (r'SqlCommand.*\+', "SQL Injection Risk", "HIGH", "CSSec002"),
            (r'Process\.Start\s*\(', "Command Injection Risk", "HIGH", "CSSec003"),
            (r'MD5\.Create\(\)', "Weak Hash (MD5)", "MEDIUM", "CSSec004"),
        ]
        
        for pattern, title, severity, rule_id in patterns:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(Issue(title=title, description=f"Line {i}.", severity=severity, category="security", line_number=i, rule_id=rule_id, code_snippet=line.strip()[:120]))
        
        return issues
    
    def run_performance_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []
        lines = parse_result.lines
        
        for i, line in enumerate(lines, 1):
            if re.search(r'\+\s*=.*string|string.*\+=', line, re.IGNORECASE):
                issues.append(Issue(title="String Concatenation", description="Use StringBuilder for repeated concatenation.", severity="MEDIUM", category="performance", line_number=i, rule_id="CSP001", code_snippet=line.strip()[:120]))
        
        return issues
