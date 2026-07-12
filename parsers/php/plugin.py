"""
PHP Language Plugin
===================
"""
import re
import math
from parsers.base_plugin import BaseLanguagePlugin, ParseResult, Features, Issue

class PHPPlugin(BaseLanguagePlugin):
    @property
    def language(self) -> str: return 'PHP'
    @property
    def file_extensions(self) -> list[str]: return ['.php']
    
    def parse(self, file_path: str, content: str) -> ParseResult:
        lines = content.splitlines(keepends=True)
        return ParseResult(language='PHP', file_path=file_path, content=content, lines=lines, is_valid=True)
    
    def extract_features(self, parse_result: ParseResult) -> Features:
        content = parse_result.content; lines = parse_result.lines; f = Features()
        f.loc = len(lines); f.blank_lines = sum(1 for l in lines if l.strip() == '')
        f.comment_lines = sum(1 for l in lines if l.strip().startswith('//') or l.strip().startswith('#') or l.strip().startswith('*'))
        f.sloc = f.loc - f.blank_lines; f.comment_ratio = f.comment_lines / max(f.loc, 1)
        f.function_count = len(re.findall(r'\bfunction\s+\w+\s*\(', content))
        f.class_count = len(re.findall(r'\b(class|interface|trait)\s+\w+', content))
        f.import_count = len(re.findall(r'\b(require|include|use)\s+', content))
        f.loop_count = len(re.findall(r'\b(for|foreach|while|do)\s*[\(\{]', content))
        f.conditional_count = len(re.findall(r'\b(if|elseif|switch)\s*\(', content))
        f.exception_handling = len(re.findall(r'\btry\s*\{', content))
        f.eval_usage = len(re.findall(r'\beval\s*\(', content))
        f.todo_count = len(re.findall(r'//.*\bTODO\b', content, re.IGNORECASE))
        f.fixme_count = len(re.findall(r'//.*\bFIXME\b', content, re.IGNORECASE))
        f.sql_queries = len(re.findall(r'\b(SELECT|INSERT|UPDATE|DELETE)\b', content, re.IGNORECASE))
        f.shell_executions = len(re.findall(r'\b(exec|system|shell_exec|passthru|popen)\s*\(', content))
        f.cyclomatic_complexity = float(1 + f.conditional_count + f.loop_count + f.exception_handling)
        operators = re.findall(r'[\+\-\*\/\%\=\<\>\!\&\|\^\.]+', content)
        operands = re.findall(r'\b[a-zA-Z_]\w*\b', content)
        n1, n2 = len(set(operators)), len(set(operands)); N1, N2 = len(operators), len(operands)
        if n1 > 0 and n2 > 0:
            n = n1 + n2; N = N1 + N2; f.halstead_volume = float(N * math.log2(n)) if n > 1 else 0.0
            f.halstead_difficulty = float((n1 / 2) * (N2 / max(n2, 1))); f.halstead_effort = f.halstead_difficulty * f.halstead_volume; f.halstead_length = float(N)
        if f.halstead_volume > 0 and f.sloc > 0:
            mi = 171 - 5.2 * math.log(max(f.halstead_volume,1)) - 0.23 * f.cyclomatic_complexity - 16.2 * math.log(max(f.sloc,1))
            f.maintainability_index = max(0.0, min(100.0, mi))
        return f
    
    def run_static_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []; lines = parse_result.lines
        for i, line in enumerate(lines, 1):
            if re.search(r'\becho\s+\$_', line):
                issues.append(Issue(title="XSS via echo $_", description="Directly echoing user input is an XSS vulnerability.", severity="CRITICAL", category="security", line_number=i, suggestion="Use htmlspecialchars() to sanitize output.", rule_id="PHP001", code_snippet=line.strip()[:120]))
        if features.cyclomatic_complexity > 15:
            issues.append(Issue(title="High Complexity", description=f"Complexity is {features.cyclomatic_complexity:.0f}.", severity="HIGH", category="maintainability", line_number=1, rule_id="PHP002"))
        return issues
    
    def run_security_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []; lines = parse_result.lines
        patterns = [
            (r'\$_(GET|POST|REQUEST|COOKIE)\[', "Unvalidated User Input", "HIGH", "PHPSec001"),
            (r'mysql_query\s*\(.*\$_', "SQL Injection Risk", "CRITICAL", "PHPSec002"),
            (r'\beval\s*\(', "eval() Usage", "HIGH", "PHPSec003"),
            (r'\b(exec|system|shell_exec|passthru)\s*\(', "Command Injection", "HIGH", "PHPSec004"),
            (r'(password|passwd|secret)\s*=\s*["\'][^"\']{4,}["\']', "Hardcoded Credential", "CRITICAL", "PHPSec005"),
            (r'md5\s*\(', "Weak Hash (md5)", "MEDIUM", "PHPSec006"),
        ]
        for pattern, title, severity, rule_id in patterns:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(Issue(title=title, description=f"Line {i}.", severity=severity, category="security", line_number=i, rule_id=rule_id, code_snippet=line.strip()[:120]))
        return issues
    
    def run_performance_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []; lines = parse_result.lines
        for i, line in enumerate(lines, 1):
            if re.search(r'\bquery\s*\(', line) and re.search(r'\bfor\b|\bforeach\b|\bwhile\b', parse_result.lines[max(0,i-5):i+5 if i < len(lines) else len(lines)][0] if i > 0 else ''):
                issues.append(Issue(title="Possible N+1 Query", description="Database query inside a loop may cause N+1 problem.", severity="HIGH", category="performance", line_number=i, suggestion="Use eager loading or batch queries.", rule_id="PHPPERF001", code_snippet=line.strip()[:120]))
        return issues
