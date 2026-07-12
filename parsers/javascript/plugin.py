"""
JavaScript Language Plugin
==========================
Regex + heuristic-based analysis for JavaScript files.
"""

import re
import math
from parsers.base_plugin import BaseLanguagePlugin, ParseResult, Features, Issue


class JavaScriptPlugin(BaseLanguagePlugin):
    """Language plugin for JavaScript (.js, .jsx) files."""
    
    @property
    def language(self) -> str:
        return 'JavaScript'
    
    @property
    def file_extensions(self) -> list[str]:
        return ['.js', '.jsx', '.mjs', '.cjs']
    
    def parse(self, file_path: str, content: str) -> ParseResult:
        lines = content.splitlines(keepends=True)
        errors = []
        # Basic syntax check: unbalanced braces
        if content.count('{') != content.count('}'):
            errors.append("Warning: Unbalanced curly braces detected.")
        return ParseResult(
            language='JavaScript',
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
        comment_single = sum(1 for l in lines if l.strip().startswith('//'))
        f.comment_lines = comment_single + content.count('/*')
        f.sloc        = f.loc - f.blank_lines
        f.comment_ratio = f.comment_lines / max(f.loc, 1)
        
        # Functions (arrow, regular, method)
        f.function_count = len(re.findall(
            r'\b(function\s+\w+|const\s+\w+\s*=\s*\(|=>\s*\{|\bfunction\s*\()',
            content
        ))
        f.class_count  = len(re.findall(r'\bclass\s+\w+', content))
        f.import_count = len(re.findall(r'\b(import|require)\s*[\(\{]', content))
        f.loop_count   = len(re.findall(r'\b(for|while|do)\s*\(', content))
        f.nested_loops = len(re.findall(r'\bfor\s*\([^)]*\)\s*\{[^}]*\bfor\b', content, re.DOTALL))
        f.conditional_count = len(re.findall(r'\b(if|else if|switch)\s*\(', content))
        f.exception_handling = len(re.findall(r'\btry\s*\{', content))
        f.eval_usage = len(re.findall(r'\beval\s*\(', content))
        f.todo_count  = len(re.findall(r'//.*\bTODO\b',  content, re.IGNORECASE))
        f.fixme_count = len(re.findall(r'//.*\bFIXME\b', content, re.IGNORECASE))
        f.magic_numbers = len(re.findall(r'\b(?<!\.)\d{2,}\b', content))
        f.sql_queries = len(re.findall(r'\b(SELECT|INSERT|UPDATE|DELETE)\b', content, re.IGNORECASE))
        f.shell_executions = len(re.findall(r'\b(exec|spawn|execSync|spawnSync)\s*\(', content))
        f.network_operations = len(re.findall(r'\b(fetch|axios|XMLHttpRequest|http\.get)\b', content))
        f.file_operations = len(re.findall(r'\bfs\.(read|write|append|unlink)\b', content))
        
        # Cyclomatic complexity
        f.cyclomatic_complexity = float(1 + f.conditional_count + f.loop_count + f.exception_handling)
        
        # Halstead (approximation)
        operators = re.findall(r'[\+\-\*\/\%\=\<\>\!\&\|\^]+', content)
        operands  = re.findall(r'\b[a-zA-Z_]\w*\b', content)
        n1, n2 = len(set(operators)), len(set(operands))
        N1, N2 = len(operators), len(operands)
        if n1 > 0 and n2 > 0:
            n = n1 + n2
            N = N1 + N2
            f.halstead_length     = float(N)
            f.halstead_volume     = float(N * math.log2(n)) if n > 1 else 0.0
            f.halstead_difficulty = float((n1 / 2) * (N2 / max(n2, 1)))
            f.halstead_effort     = f.halstead_difficulty * f.halstead_volume
        
        if f.halstead_volume > 0 and f.sloc > 0:
            mi = (171 - 5.2 * math.log(max(f.halstead_volume, 1))
                  - 0.23 * f.cyclomatic_complexity - 16.2 * math.log(max(f.sloc, 1)))
            f.maintainability_index = max(0.0, min(100.0, mi))
        
        # Duplicate lines
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
        
        # var usage (prefer const/let)
        for i, line in enumerate(lines, 1):
            if re.search(r'\bvar\s+\w+', line):
                issues.append(Issue(
                    title="Use of 'var'",
                    description="'var' has function scope and can cause bugs. Use 'const' or 'let'.",
                    severity="LOW",
                    category="style",
                    line_number=i,
                    suggestion="Replace 'var' with 'const' (if not reassigned) or 'let'.",
                    rule_id="JS001",
                    code_snippet=line.strip()[:120],
                ))
        
        # == instead of ===
        for i, line in enumerate(lines, 1):
            if re.search(r'[^=!<>]==[^=]', line) and '===' not in line:
                issues.append(Issue(
                    title="Loose Equality (==)",
                    description="Using '==' instead of '===' can cause unexpected type coercion.",
                    severity="MEDIUM",
                    category="bug",
                    line_number=i,
                    suggestion="Use strict equality '===' to avoid type coercion bugs.",
                    rule_id="JS002",
                    code_snippet=line.strip()[:120],
                ))
        
        # console.log in production code
        for i, line in enumerate(lines, 1):
            if re.search(r'\bconsole\.(log|debug|warn)\s*\(', line):
                issues.append(Issue(
                    title="Console Statement",
                    description="Debug console statement found.",
                    severity="INFO",
                    category="style",
                    line_number=i,
                    suggestion="Remove console statements before production deployment.",
                    rule_id="JS003",
                    code_snippet=line.strip()[:120],
                ))
        
        # High complexity
        if features.cyclomatic_complexity > 15:
            issues.append(Issue(
                title="High Cyclomatic Complexity",
                description=f"Complexity is {features.cyclomatic_complexity:.0f}.",
                severity="HIGH",
                category="maintainability",
                line_number=1,
                suggestion="Refactor complex logic into smaller functions.",
                rule_id="JS004",
            ))
        
        return issues
    
    def run_security_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []
        lines = parse_result.lines
        
        security_patterns = [
            (r'\beval\s*\(',           "Unsafe eval()",            "HIGH",     "security", "Use JSON.parse() or Function() constructor carefully.", "JSS001"),
            (r'innerHTML\s*=',         "XSS via innerHTML",        "HIGH",     "security", "Use textContent or DOMPurify to sanitize HTML.", "JSS002"),
            (r'document\.write\s*\(',  "Unsafe document.write()",  "MEDIUM",   "security", "Avoid document.write(); use DOM manipulation instead.", "JSS003"),
            (r'(password|secret|key)\s*[:=]\s*["\'][^"\']{4,}["\']',
             "Hardcoded Credential",    "CRITICAL",  "security", "Store secrets in environment variables, never in source.", "JSS004"),
            (r'\bwith\s*\(',           "Dangerous 'with' Statement","MEDIUM",   "security", "Avoid 'with' — it makes code unpredictable.", "JSS005"),
            (r'new Function\s*\(',     "Dynamic Function Creation", "HIGH",     "security", "new Function() is similar to eval() — avoid when possible.", "JSS006"),
            (r'location\.href\s*=',    "Open Redirect Risk",        "MEDIUM",   "security", "Validate redirect URLs against an allowlist.", "JSS007"),
        ]
        
        for pattern, title, severity, category, suggestion, rule_id in security_patterns:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(Issue(
                        title=title,
                        description=f"Found at line {i}: {line.strip()[:80]}",
                        severity=severity,
                        category=category,
                        line_number=i,
                        suggestion=suggestion,
                        rule_id=rule_id,
                        code_snippet=line.strip()[:120],
                    ))
        
        return issues
    
    def run_performance_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []
        lines = parse_result.lines
        
        perf_patterns = [
            (r'for\s*\([^)]*\)\s*\{[^}]*for\s*\(',
             "Nested Loop", "MEDIUM", "performance",
             "Nested loops may cause O(n²) complexity. Consider algorithmic improvements.", "JSP001"),
            (r'document\.getElementById|querySelector',
             "DOM Query in Possible Loop", "INFO", "performance",
             "Cache DOM queries outside loops to avoid reflow.", "JSP002"),
            (r'\.innerHTML\s*\+=',
             "Inefficient innerHTML Concatenation", "MEDIUM", "performance",
             "Use DocumentFragment or array.join() for batch DOM updates.", "JSP003"),
            (r'\bJSON\.parse\s*\(\s*JSON\.stringify',
             "Deep Clone via JSON", "LOW", "performance",
             "Use structuredClone() or a proper deep-clone library.", "JSP004"),
        ]
        
        for pattern, title, severity, category, suggestion, rule_id in perf_patterns:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    issues.append(Issue(
                        title=title,
                        description=f"Found at line {i}.",
                        severity=severity,
                        category=category,
                        line_number=i,
                        suggestion=suggestion,
                        rule_id=rule_id,
                        code_snippet=line.strip()[:120],
                    ))
        
        return issues
