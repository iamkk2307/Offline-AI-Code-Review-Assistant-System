"""
Python Language Plugin
======================
Full implementation for Python source code analysis.
Uses Python's built-in ast module for accurate parsing.
"""

import ast
import re
import math
from typing import Optional

from parsers.base_plugin import BaseLanguagePlugin, ParseResult, Features, Issue


class PythonPlugin(BaseLanguagePlugin):
    """Language plugin for Python (.py) files."""
    
    @property
    def language(self) -> str:
        return 'Python'
    
    @property
    def file_extensions(self) -> list[str]:
        return ['.py', '.pyw']
    
    # ── Parse ────────────────────────────────────────────────────────────────
    
    def parse(self, file_path: str, content: str) -> ParseResult:
        lines = content.splitlines(keepends=True)
        parse_errors = []
        tree = None
        
        try:
            tree = ast.parse(content, filename=file_path)
        except SyntaxError as e:
            parse_errors.append(f"SyntaxError at line {e.lineno}: {e.msg}")
        except Exception as e:
            parse_errors.append(f"Parse error: {e}")
        
        return ParseResult(
            language='Python',
            file_path=file_path,
            content=content,
            lines=lines,
            ast=tree,
            parse_errors=parse_errors,
            is_valid=len(parse_errors) == 0,
        )
    
    # ── Feature Extraction ────────────────────────────────────────────────
    
    def extract_features(self, parse_result: ParseResult) -> Features:
        content = parse_result.content
        lines = parse_result.lines
        tree = parse_result.ast
        f = Features()
        
        # Basic LOC metrics
        f.loc = len(lines)
        f.blank_lines = sum(1 for l in lines if l.strip() == '')
        f.comment_lines = sum(1 for l in lines if l.strip().startswith('#'))
        f.sloc = f.loc - f.blank_lines - f.comment_lines
        f.comment_ratio = f.comment_lines / max(f.loc, 1)
        
        # TODO / FIXME
        f.todo_count  = len(re.findall(r'#.*\bTODO\b',  content, re.IGNORECASE))
        f.fixme_count = len(re.findall(r'#.*\bFIXME\b', content, re.IGNORECASE))
        
        if tree is None:
            return f
        
        # AST-based metrics
        functions, classes = [], []
        all_identifiers = []
        max_depth = [0]
        
        class Visitor(ast.NodeVisitor):
            def __init__(self):
                self._depth = 0
            
            def visit_FunctionDef(self, node):
                functions.append(node)
                self.generic_visit(node)
            visit_AsyncFunctionDef = visit_FunctionDef
            
            def visit_ClassDef(self, node):
                classes.append(node)
                self.generic_visit(node)
            
            def visit_Name(self, node):
                all_identifiers.append(node.id)
                self.generic_visit(node)
            
            def visit_Import(self, node):
                f.import_count += len(node.names)
                self.generic_visit(node)
            
            def visit_ImportFrom(self, node):
                f.import_count += 1
                self.generic_visit(node)
            
            def visit_Global(self, node):
                f.global_variables += len(node.names)
                self.generic_visit(node)
            
            def visit_Return(self, node):
                f.return_statements += 1
                self.generic_visit(node)
            
            def visit_Try(self, node):
                f.exception_handling += 1
                self.generic_visit(node)
            
            def visit_For(self, node):
                f.loop_count += 1
                self.generic_visit(node)
            
            def visit_While(self, node):
                f.loop_count += 1
                self.generic_visit(node)
            
            def visit_If(self, node):
                f.conditional_count += 1
                self.generic_visit(node)
            
            def visit_Call(self, node):
                # Detect eval / exec
                if isinstance(node.func, ast.Name) and node.func.id in ('eval', 'exec'):
                    f.eval_usage += 1
                # Detect network
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ('get', 'post', 'request', 'urlopen'):
                        f.network_operations += 1
                    if node.func.attr in ('open', 'read', 'write'):
                        f.file_operations += 1
                self.generic_visit(node)
            
            def visit_Assign(self, node):
                # Detect magic numbers
                for child in ast.walk(node):
                    if isinstance(child, ast.Constant) and isinstance(child.value, (int, float)):
                        if child.value not in (0, 1, -1, 2, 100, True, False):
                            f.magic_numbers += 1
                self.generic_visit(node)
        
        visitor = Visitor()
        visitor.visit(tree)
        
        f.function_count = len(functions)
        f.class_count    = len(classes)
        f.method_count   = sum(
            len([n for n in ast.walk(c) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))])
            for c in classes
        )
        
        # Function-level metrics
        func_lengths = []
        for func in functions:
            length = func.end_lineno - func.lineno + 1 if hasattr(func, 'end_lineno') else 10
            func_lengths.append(length)
            args_count = len(func.args.args) + len(func.args.posonlyargs)
            f.parameter_count += args_count
            if args_count > 7:
                f.long_parameter_lists += 1
            if length > 50:
                f.long_methods += 1
            # Check recursion
            func_name = func.name
            for node in ast.walk(func):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id == func_name:
                        f.recursion_count += 1
                        break
        
        f.avg_function_length = sum(func_lengths) / max(len(func_lengths), 1)
        
        # Class metrics
        class_sizes = []
        for cls in classes:
            methods = [n for n in ast.walk(cls) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            class_sizes.append(len(methods))
            if len(methods) > 20:
                f.large_classes += 1
        f.avg_class_size = sum(class_sizes) / max(len(class_sizes), 1)
        
        # Cyclomatic complexity (simplified McCabe)
        f.cyclomatic_complexity = float(
            1 + f.conditional_count + f.loop_count + f.exception_handling
        )
        
        # Halstead metrics (approximate)
        operators = re.findall(r'[\+\-\*\/\%\=\<\>\!\&\|\^~]+', content)
        operands  = re.findall(r'\b\w+\b', content)
        n1, n2 = len(set(operators)), len(set(operands))
        N1, N2 = len(operators), len(operands)
        N = N1 + N2
        if n1 > 0 and n2 > 0 and N > 0:
            n = n1 + n2
            f.halstead_length     = float(N)
            f.halstead_volume     = float(N * math.log2(n)) if n > 0 else 0.0
            f.halstead_difficulty = float((n1 / 2) * (N2 / max(n2, 1)))
            f.halstead_effort     = f.halstead_difficulty * f.halstead_volume
        
        # Maintainability Index (SEI formula)
        if f.halstead_volume > 0 and f.sloc > 0:
            import math as _m
            mi = (171
                  - 5.2 * _m.log(f.halstead_volume)
                  - 0.23 * f.cyclomatic_complexity
                  - 16.2 * _m.log(f.sloc))
            f.maintainability_index = max(0.0, min(100.0, mi))
        
        # Identifier stats
        if all_identifiers:
            f.avg_identifier_length = sum(len(i) for i in all_identifiers) / len(all_identifiers)
            # Naming violations: single-char names (except i, j, k, x, y, n)
            allowed_singles = {'i', 'j', 'k', 'x', 'y', 'n', 'e', 'f', 'v', '_'}
            f.naming_violations = sum(
                1 for ident in all_identifiers
                if len(ident) == 1 and ident not in allowed_singles
            )
        
        # Constants (ALL_CAPS names at module level)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        f.constants += 1
        
        # Nested loops detection
        for func in functions:
            depth = _get_max_loop_depth(func)
            if depth > 1:
                f.nested_loops += 1
            if depth > max_depth[0]:
                max_depth[0] = depth
        f.max_nesting_depth = max_depth[0]
        
        # Duplicate lines (simple heuristic)
        stripped = [l.strip() for l in lines if l.strip() and not l.strip().startswith('#')]
        if stripped:
            from collections import Counter
            counts = Counter(stripped)
            f.duplicate_lines = sum(c - 1 for c in counts.values() if c > 1)
            f.duplicate_ratio = f.duplicate_lines / max(len(stripped), 1)
        
        # Security: SQL queries
        f.sql_queries = len(re.findall(
            r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b',
            content, re.IGNORECASE
        ))
        # Shell executions
        f.shell_executions = len(re.findall(
            r'\b(os\.system|subprocess\.|popen|shell=True)\b', content
        ))
        
        return f
    
    # ── Static Analysis ───────────────────────────────────────────────────
    
    def run_static_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []
        content = parse_result.content
        lines   = parse_result.lines
        tree    = parse_result.ast
        
        # Parse errors become issues
        for err in parse_result.parse_errors:
            issues.append(Issue(
                title="Syntax Error",
                description=err,
                severity="CRITICAL",
                category="bug",
                line_number=1,
                rule_id="PY001",
            ))
        
        if tree is None:
            return issues
        
        # Long methods
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                length = getattr(node, 'end_lineno', node.lineno) - node.lineno + 1
                if length > 50:
                    issues.append(Issue(
                        title="Long Method",
                        description=f"Function '{node.name}' is {length} lines long.",
                        severity="MEDIUM",
                        category="maintainability",
                        line_number=node.lineno,
                        suggestion="Break this function into smaller, focused functions.",
                        reason="Functions over 50 lines are harder to understand and test.",
                        rule_id="PY002",
                    ))
                # Long parameter list
                args_count = len(node.args.args) + len(node.args.posonlyargs)
                if args_count > 7:
                    issues.append(Issue(
                        title="Long Parameter List",
                        description=f"Function '{node.name}' has {args_count} parameters.",
                        severity="MEDIUM",
                        category="style",
                        line_number=node.lineno,
                        suggestion="Consider using a config object or dataclass.",
                        rule_id="PY003",
                    ))
        
        # Missing docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if not (node.body and isinstance(node.body[0], ast.Expr)
                        and isinstance(node.body[0].value, ast.Constant)
                        and isinstance(node.body[0].value.value, str)):
                    if not node.name.startswith('_'):
                        issues.append(Issue(
                            title="Missing Docstring",
                            description=f"'{node.name}' has no docstring.",
                            severity="LOW",
                            category="style",
                            line_number=node.lineno,
                            suggestion="Add a docstring describing purpose, args, and return value.",
                            rule_id="PY004",
                        ))
        
        # Magic numbers
        magic_threshold = 5
        magic_count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if node.value not in (0, 1, -1, 2, 100, True, False):
                    magic_count += 1
        if magic_count > magic_threshold:
            issues.append(Issue(
                title="Magic Numbers",
                description=f"Found {magic_count} magic numbers in the code.",
                severity="LOW",
                category="style",
                line_number=1,
                suggestion="Extract magic numbers into named constants.",
                rule_id="PY005",
            ))
        
        # High cyclomatic complexity
        if features.cyclomatic_complexity > 15:
            issues.append(Issue(
                title="High Cyclomatic Complexity",
                description=f"Cyclomatic complexity is {features.cyclomatic_complexity:.0f} (threshold: 15).",
                severity="HIGH",
                category="maintainability",
                line_number=1,
                suggestion="Simplify conditional logic or split into smaller functions.",
                rule_id="PY006",
            ))
        
        # Bare except clauses
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append(Issue(
                    title="Bare Except Clause",
                    description="Using bare `except:` catches all exceptions including system exits.",
                    severity="MEDIUM",
                    category="bug",
                    line_number=node.lineno,
                    suggestion="Catch specific exceptions: `except ValueError:` or `except Exception:`",
                    rule_id="PY007",
                ))
        
        # Unused imports (basic heuristic)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname or alias.name.split('.')[0]
                    if name not in content.split('\n', node.lineno)[-1:] and \
                            content.count(name) <= 1:
                        issues.append(Issue(
                            title="Potentially Unused Import",
                            description=f"Import '{alias.name}' may be unused.",
                            severity="INFO",
                            category="style",
                            line_number=node.lineno,
                            suggestion="Remove unused imports to keep code clean.",
                            rule_id="PY008",
                        ))
        
        return issues
    
    # ── Security Analysis ─────────────────────────────────────────────────
    
    def run_security_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []
        content = parse_result.content
        lines   = parse_result.lines
        
        security_patterns = [
            # SQL injection
            (r'(execute|query)\s*\(\s*["\']?\s*SELECT.*%[s|d]',
             "SQL Injection Risk", "HIGH", "security",
             "Use parameterized queries instead of string formatting.",
             "PYS001"),
            # Hardcoded passwords
            (r'(password|passwd|pwd|secret|api_key|apikey)\s*=\s*["\'][^"\']{4,}["\']',
             "Hardcoded Credential", "CRITICAL", "security",
             "Move secrets to environment variables or a secure vault.",
             "PYS002"),
            # Eval usage
            (r'\beval\s*\(',
             "Unsafe eval() Usage", "HIGH", "security",
             "eval() can execute arbitrary code. Use ast.literal_eval() for data.",
             "PYS003"),
            # Shell injection
            (r'os\.system\s*\(',
             "Shell Command Injection Risk", "HIGH", "security",
             "Use subprocess with a list of arguments and shell=False.",
             "PYS004"),
            (r'shell\s*=\s*True',
             "Subprocess with shell=True", "HIGH", "security",
             "Avoid shell=True to prevent command injection.",
             "PYS005"),
            # Weak hashing
            (r'\b(md5|sha1)\s*\(',
             "Weak Cryptographic Hash", "MEDIUM", "security",
             "Use SHA-256 or stronger for security purposes.",
             "PYS006"),
            # Pickle deserialization
            (r'\bpickle\.loads?\s*\(',
             "Insecure Deserialization (pickle)", "HIGH", "security",
             "pickle.load() can execute arbitrary code. Use JSON or safer formats.",
             "PYS007"),
            # Directory traversal
            (r'open\s*\([^)]*\.\.[^)]*\)',
             "Directory Traversal Risk", "HIGH", "security",
             "Validate and sanitize file paths before opening.",
             "PYS008"),
            # Hardcoded API keys (generic pattern)
            (r'["\'][A-Za-z0-9]{32,}["\']',
             "Possible Hardcoded API Key", "MEDIUM", "security",
             "Move API keys to environment variables.",
             "PYS009"),
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
    
    # ── Performance Analysis ───────────────────────────────────────────────
    
    def run_performance_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []
        content = parse_result.content
        lines   = parse_result.lines
        tree    = parse_result.ast
        
        if tree is None:
            return issues
        
        # Nested loops
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                depth = _get_max_loop_depth(node)
                if depth >= 3:
                    issues.append(Issue(
                        title="Deeply Nested Loops",
                        description=f"Function '{node.name}' has loops nested {depth} levels deep (O(n^{depth}) complexity).",
                        severity="HIGH",
                        category="performance",
                        line_number=node.lineno,
                        suggestion="Consider using vectorized operations, dictionaries, or algorithmic improvements.",
                        rule_id="PYP001",
                    ))
                elif depth == 2:
                    issues.append(Issue(
                        title="Nested Loops",
                        description=f"Function '{node.name}' has nested loops (O(n²) complexity).",
                        severity="MEDIUM",
                        category="performance",
                        line_number=node.lineno,
                        suggestion="Consider if the nested loop can be replaced with a set/dict lookup.",
                        rule_id="PYP002",
                    ))
        
        # Performance patterns
        perf_patterns = [
            (r'\+\s*=.*\bstr\b|\bstr\b.*\+=',
             "String Concatenation in Loop", "MEDIUM", "performance",
             "Use ''.join() instead of += for string concatenation in loops.",
             "PYP003"),
            (r'\.append\s*\(.*\)\s*$',
             "List append in possible loop", "INFO", "performance",
             "Consider list comprehensions for better performance.",
             "PYP004"),
            (r'\brange\s*\(\s*len\s*\(',
             "range(len()) Anti-Pattern", "LOW", "performance",
             "Use enumerate() instead of range(len()).",
             "PYP005"),
            (r'\bos\.listdir\b',
             "os.listdir() Usage", "INFO", "performance",
             "Consider os.scandir() which is faster for large directories.",
             "PYP006"),
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


def _get_max_loop_depth(node: ast.AST, current_depth: int = 0) -> int:
    """Recursively find maximum loop nesting depth in an AST node."""
    max_depth = current_depth
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.For, ast.While)):
            depth = _get_max_loop_depth(child, current_depth + 1)
        else:
            depth = _get_max_loop_depth(child, current_depth)
        max_depth = max(max_depth, depth)
    return max_depth
