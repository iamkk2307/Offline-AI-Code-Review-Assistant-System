"""
Java Language Plugin
====================
Regex-based analysis for Java source files.
"""

import re
import math
from parsers.base_plugin import BaseLanguagePlugin, ParseResult, Features, Issue


class JavaPlugin(BaseLanguagePlugin):
    """Language plugin for Java (.java) files."""
    
    @property
    def language(self) -> str:
        return 'Java'
    
    @property
    def file_extensions(self) -> list[str]:
        return ['.java']
    
    def parse(self, file_path: str, content: str) -> ParseResult:
        lines = content.splitlines(keepends=True)
        errors = []
        if content.count('{') != content.count('}'):
            errors.append("Warning: Unbalanced curly braces.")
        return ParseResult(
            language='Java',
            file_path=file_path,
            content=content,
            lines=lines,
            parse_errors=errors,
            is_valid=True,
        )
    
    def extract_features(self, parse_result: ParseResult) -> Features:
        content = parse_result.content
        lines   = parse_result.lines
        f = Features()
        
        f.loc         = len(lines)
        f.blank_lines = sum(1 for l in lines if l.strip() == '')
        f.comment_lines = sum(1 for l in lines if l.strip().startswith('//') or l.strip().startswith('*'))
        f.sloc        = f.loc - f.blank_lines
        f.comment_ratio = f.comment_lines / max(f.loc, 1)
        
        f.class_count    = len(re.findall(r'\b(class|interface|enum)\s+\w+', content))
        f.function_count = len(re.findall(r'\b(public|private|protected|static)\s+\w+[\w<>[\],\s]+\w+\s*\(', content))
        f.method_count   = f.function_count
        f.import_count   = len(re.findall(r'^\s*import\s+', content, re.MULTILINE))
        f.loop_count     = len(re.findall(r'\b(for|while|do)\s*[\(\{]', content))
        f.nested_loops   = len(re.findall(r'\bfor\s*\([^)]*\)\s*\{[^}]*\bfor\b', content, re.DOTALL))
        f.conditional_count = len(re.findall(r'\b(if|else if|switch)\s*\(', content))
        f.exception_handling = len(re.findall(r'\btry\s*\{', content))
        f.todo_count = len(re.findall(r'//.*\bTODO\b', content, re.IGNORECASE))
        f.fixme_count = len(re.findall(r'//.*\bFIXME\b', content, re.IGNORECASE))
        f.magic_numbers = len(re.findall(r'\b(?<!\.)(?!0x)\d{2,}\b', content))
        f.sql_queries = len(re.findall(r'\b(SELECT|INSERT|UPDATE|DELETE)\b', content, re.IGNORECASE))
        f.eval_usage = 0  # Java doesn't have eval
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
        
        stripped = [l.strip() for l in lines if l.strip() and not l.strip().startswith('//')]
        if stripped:
            from collections import Counter
            counts = Counter(stripped)
            f.duplicate_lines = sum(c - 1 for c in counts.values() if c > 1)
            f.duplicate_ratio = f.duplicate_lines / max(len(stripped), 1)
        
        return f
    
    def run_static_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []
        content = parse_result.content
        lines   = parse_result.lines
        
        # Catch generic Exception
        for i, line in enumerate(lines, 1):
            if re.search(r'catch\s*\(\s*Exception\s+\w+\s*\)', line):
                issues.append(Issue(
                    title="Catch Generic Exception",
                    description="Catching the generic Exception class hides bugs.",
                    severity="MEDIUM", category="bug", line_number=i,
                    suggestion="Catch specific exception types.", rule_id="JA001",
                    code_snippet=line.strip()[:120],
                ))
            # Empty catch blocks
            if re.search(r'catch\s*\([^)]+\)\s*\{\s*\}', line):
                issues.append(Issue(
                    title="Empty Catch Block",
                    description="Silently swallowing exceptions is dangerous.",
                    severity="HIGH", category="bug", line_number=i,
                    suggestion="Log the exception or re-throw it.", rule_id="JA002",
                    code_snippet=line.strip()[:120],
                ))
            # System.out.println
            if re.search(r'System\.out\.(print|println)\s*\(', line):
                issues.append(Issue(
                    title="System.out.println Usage",
                    description="Use a logging framework instead of print statements.",
                    severity="INFO", category="style", line_number=i,
                    suggestion="Use SLF4J or Log4j: logger.info(\"message\");", rule_id="JA003",
                    code_snippet=line.strip()[:120],
                ))
        
        if features.cyclomatic_complexity > 15:
            issues.append(Issue(
                title="High Cyclomatic Complexity",
                description=f"Complexity is {features.cyclomatic_complexity:.0f}.",
                severity="HIGH", category="maintainability", line_number=1,
                suggestion="Refactor into smaller methods.", rule_id="JA004",
            ))
        
        return issues
    
    def run_security_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []
        lines = parse_result.lines
        
        patterns = [
            (r'(password|passwd|secret|apikey)\s*=\s*"[^"]{4,}"', "Hardcoded Credential", "CRITICAL", "JSec001"),
            (r'Statement.*execute.*\+', "SQL Injection Risk (String Concat)", "HIGH", "JSec002"),
            (r'Runtime\.getRuntime\(\)\.exec\s*\(', "Command Injection Risk", "HIGH", "JSec003"),
            (r'(MD5|SHA1)\s*\.', "Weak Hash Algorithm", "MEDIUM", "JSec004"),
            (r'new\s+ObjectInputStream\s*\(', "Insecure Deserialization", "HIGH", "JSec005"),
            (r'\.setHeader\s*\(\s*"Access-Control-Allow-Origin"\s*,\s*"\*"', "CORS Wildcard", "MEDIUM", "JSec006"),
        ]
        
        for pattern, title, severity, rule_id in patterns:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(Issue(
                        title=title,
                        description=f"Line {i}: {line.strip()[:80]}",
                        severity=severity, category="security",
                        line_number=i, rule_id=rule_id,
                        code_snippet=line.strip()[:120],
                    ))
        
        return issues
    
    def run_performance_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []
        lines = parse_result.lines
        
        patterns = [
            (r'\bString\s+\w+\s*=\s*"[^"]*"\s*\+', "String Concatenation", "LOW", "performance", "Use StringBuilder for string concatenation.", "JP001"),
            (r'\bnew\s+\w+\[]\s*\{', "Large Array Literal", "INFO", "performance", "Consider using a collection instead.", "JP002"),
        ]
        
        for pattern, title, severity, category, suggestion, rule_id in patterns:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    issues.append(Issue(
                        title=title, description=f"Line {i}.",
                        severity=severity, category=category,
                        line_number=i, suggestion=suggestion, rule_id=rule_id,
                        code_snippet=line.strip()[:120],
                    ))
        
        return issues
