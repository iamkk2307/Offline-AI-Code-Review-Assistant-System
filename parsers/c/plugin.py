"""
C Language Plugin
=================
Regex-based analysis for C source files.
"""

import re
import math
from parsers.base_plugin import BaseLanguagePlugin, ParseResult, Features, Issue


class CPlugin(BaseLanguagePlugin):
    @property
    def language(self) -> str:
        return 'C'
    
    @property
    def file_extensions(self) -> list[str]:
        return ['.c', '.h']
    
    def parse(self, file_path: str, content: str) -> ParseResult:
        lines = content.splitlines(keepends=True)
        errors = []
        if content.count('{') != content.count('}'):
            errors.append("Unbalanced curly braces.")
        return ParseResult(language='C', file_path=file_path, content=content, lines=lines, parse_errors=errors, is_valid=True)
    
    def extract_features(self, parse_result: ParseResult) -> Features:
        content = parse_result.content
        lines = parse_result.lines
        f = Features()
        f.loc = len(lines)
        f.blank_lines = sum(1 for l in lines if l.strip() == '')
        f.comment_lines = sum(1 for l in lines if l.strip().startswith('//') or l.strip().startswith('*') or l.strip().startswith('/*'))
        f.sloc = f.loc - f.blank_lines
        f.comment_ratio = f.comment_lines / max(f.loc, 1)
        f.function_count = len(re.findall(r'^\w[\w\s\*]+\s+\w+\s*\([^)]*\)\s*\{', content, re.MULTILINE))
        f.import_count = len(re.findall(r'^\s*#include\s*[<"]', content, re.MULTILINE))
        f.global_variables = len(re.findall(r'^(int|char|float|double|long|short)\s+\w+\s*[=;]', content, re.MULTILINE))
        f.loop_count = len(re.findall(r'\b(for|while|do)\s*\(', content))
        f.nested_loops = len(re.findall(r'\bfor\s*\([^)]*\)\s*\{[^}]*\bfor\b', content, re.DOTALL))
        f.conditional_count = len(re.findall(r'\b(if|else if|switch)\s*\(', content))
        f.exception_handling = 0  # C has no exceptions
        f.todo_count = len(re.findall(r'//.*\bTODO\b', content, re.IGNORECASE))
        f.fixme_count = len(re.findall(r'//.*\bFIXME\b', content, re.IGNORECASE))
        f.magic_numbers = len(re.findall(r'\b(?<!\.)(?!0x)\d{2,}\b', content))
        f.sql_queries = len(re.findall(r'\b(SELECT|INSERT|UPDATE|DELETE)\b', content, re.IGNORECASE))
        f.shell_executions = len(re.findall(r'\b(system|popen)\s*\(', content))
        f.cyclomatic_complexity = float(1 + f.conditional_count + f.loop_count)
        operators = re.findall(r'[\+\-\*\/\%\=\<\>\!\&\|\^]+', content)
        operands = re.findall(r'\b[a-zA-Z_]\w*\b', content)
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
            if re.search(r'\bgoto\b', line):
                issues.append(Issue(title="goto Statement", description="goto makes control flow hard to follow.", severity="MEDIUM", category="style", line_number=i, suggestion="Restructure code to avoid goto.", rule_id="C001", code_snippet=line.strip()[:120]))
            if re.search(r'\bgets\s*\(', line):
                issues.append(Issue(title="Dangerous gets() Function", description="gets() is vulnerable to buffer overflow.", severity="CRITICAL", category="security", line_number=i, suggestion="Use fgets() with a size limit.", rule_id="C002", code_snippet=line.strip()[:120]))
        
        if features.cyclomatic_complexity > 15:
            issues.append(Issue(title="High Complexity", description=f"Complexity is {features.cyclomatic_complexity:.0f}.", severity="HIGH", category="maintainability", line_number=1, rule_id="C003"))
        
        return issues
    
    def run_security_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []
        lines = parse_result.lines
        
        patterns = [
            (r'\bgets\s*\(',       "Buffer Overflow (gets)",     "CRITICAL", "CSec001"),
            (r'\bstrcpy\s*\(',     "Buffer Overflow (strcpy)",   "HIGH",     "CSec002"),
            (r'\bsprintf\s*\(',    "Buffer Overflow (sprintf)",  "MEDIUM",   "CSec003"),
            (r'\bsystem\s*\(',     "Command Injection (system)", "HIGH",     "CSec004"),
            (r'\bmalloc\s*\(',     "malloc Without NULL Check",  "LOW",      "CSec005"),
            (r'(password|secret)\s*=\s*"[^"]{4,}"', "Hardcoded Credential", "CRITICAL", "CSec006"),
        ]
        
        for pattern, title, severity, rule_id in patterns:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(Issue(title=title, description=f"Line {i}: {line.strip()[:80]}", severity=severity, category="security", line_number=i, rule_id=rule_id, code_snippet=line.strip()[:120]))
        
        return issues
    
    def run_performance_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []
        lines = parse_result.lines
        
        for i, line in enumerate(lines, 1):
            if re.search(r'\bmalloc\s*\(.*\)\s*;', line) and 'free(' not in parse_result.content[parse_result.content.find(line.strip()):parse_result.content.find(line.strip()) + 500]:
                issues.append(Issue(title="Potential Memory Leak", description="malloc() without corresponding free().", severity="HIGH", category="performance", line_number=i, suggestion="Ensure every malloc() has a corresponding free().", rule_id="CP001", code_snippet=line.strip()[:120]))
        
        return issues
