"""
Base Language Plugin Interface
================================
Abstract base class that every language plugin must implement.
Defines the contract for: parsing, feature extraction, static analysis,
security analysis, performance analysis, and full review.

Design Pattern: Strategy Pattern — each language plugin is a concrete strategy.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ParseResult:
    """Result of parsing a source file."""
    language: str
    file_path: str
    content: str
    lines: list[str]
    ast: Optional[Any] = None          # Language-specific AST
    tokens: list[dict] = field(default_factory=list)
    parse_errors: list[str] = field(default_factory=list)
    is_valid: bool = True


@dataclass
class Issue:
    """
    A code issue detected by static/security/performance analysis.
    
    Severity levels:
        CRITICAL — immediate security threat or crash risk
        HIGH     — significant bug or security flaw
        MEDIUM   — code quality problem
        LOW      — minor style or convention issue
        INFO     — informational suggestion
    """
    title: str
    description: str
    severity: str           # CRITICAL | HIGH | MEDIUM | LOW | INFO
    category: str           # security | performance | maintainability | style | bug
    line_number: int
    column: int = 0
    end_line: int = 0
    suggestion: str = ""
    reason: str = ""
    rule_id: str = ""
    code_snippet: str = ""
    
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "category": self.category,
            "line_number": self.line_number,
            "column": self.column,
            "end_line": self.end_line,
            "suggestion": self.suggestion,
            "reason": self.reason,
            "rule_id": self.rule_id,
            "code_snippet": self.code_snippet,
        }


@dataclass
class Features:
    """
    Extracted code metrics and features (50+ features).
    Used as input to ML models.
    """
    # === Code Metrics ===
    loc: int = 0                    # Lines of code (total)
    sloc: int = 0                   # Source lines (non-blank, non-comment)
    blank_lines: int = 0
    comment_lines: int = 0
    comment_ratio: float = 0.0      # comment_lines / loc
    function_count: int = 0
    class_count: int = 0
    method_count: int = 0
    import_count: int = 0
    global_variables: int = 0
    constants: int = 0
    parameter_count: int = 0        # Total params across all functions
    return_statements: int = 0
    exception_handling: int = 0     # try/catch/except blocks
    loop_count: int = 0
    nested_loops: int = 0
    conditional_count: int = 0      # if/else/switch statements
    recursion_count: int = 0        # Recursive function calls
    switch_statements: int = 0
    
    # === Complexity Metrics ===
    cyclomatic_complexity: float = 0.0
    halstead_length: float = 0.0
    halstead_volume: float = 0.0
    halstead_difficulty: float = 0.0
    halstead_effort: float = 0.0
    maintainability_index: float = 0.0
    max_nesting_depth: int = 0
    avg_function_length: float = 0.0
    avg_class_size: float = 0.0
    
    # === Style Metrics ===
    avg_identifier_length: float = 0.0
    naming_violations: int = 0
    duplicate_lines: int = 0
    duplicate_ratio: float = 0.0
    dead_code_lines: int = 0
    todo_count: int = 0
    fixme_count: int = 0
    long_methods: int = 0           # Functions > threshold lines
    large_classes: int = 0          # Classes > threshold methods
    long_parameter_lists: int = 0   # Functions with > threshold params
    magic_numbers: int = 0
    
    # === Security Features ===
    hardcoded_credentials: int = 0
    sql_queries: int = 0
    shell_executions: int = 0
    eval_usage: int = 0
    file_operations: int = 0
    network_operations: int = 0
    
    # === Performance Features ===
    memory_allocations: int = 0
    nested_iterations: int = 0
    redundant_calculations: int = 0
    object_creations: int = 0
    collection_usage: int = 0
    expensive_operations: int = 0
    
    def to_vector(self) -> list[float]:
        """Convert to a flat numeric vector for ML model input."""
        return [
            float(self.loc),
            float(self.sloc),
            float(self.blank_lines),
            float(self.comment_lines),
            float(self.comment_ratio),
            float(self.function_count),
            float(self.class_count),
            float(self.method_count),
            float(self.import_count),
            float(self.global_variables),
            float(self.constants),
            float(self.parameter_count),
            float(self.return_statements),
            float(self.exception_handling),
            float(self.loop_count),
            float(self.nested_loops),
            float(self.conditional_count),
            float(self.recursion_count),
            float(self.switch_statements),
            float(self.cyclomatic_complexity),
            float(self.halstead_length),
            float(self.halstead_volume),
            float(self.halstead_difficulty),
            float(self.halstead_effort),
            float(self.maintainability_index),
            float(self.max_nesting_depth),
            float(self.avg_function_length),
            float(self.avg_class_size),
            float(self.avg_identifier_length),
            float(self.naming_violations),
            float(self.duplicate_lines),
            float(self.duplicate_ratio),
            float(self.dead_code_lines),
            float(self.todo_count),
            float(self.fixme_count),
            float(self.long_methods),
            float(self.large_classes),
            float(self.long_parameter_lists),
            float(self.magic_numbers),
            float(self.hardcoded_credentials),
            float(self.sql_queries),
            float(self.shell_executions),
            float(self.eval_usage),
            float(self.file_operations),
            float(self.network_operations),
            float(self.memory_allocations),
            float(self.nested_iterations),
            float(self.redundant_calculations),
            float(self.object_creations),
            float(self.collection_usage),
            float(self.expensive_operations),
        ]
    
    @classmethod
    def feature_names(cls) -> list[str]:
        """Return ordered list of feature names (matches to_vector() order)."""
        return [
            'loc', 'sloc', 'blank_lines', 'comment_lines', 'comment_ratio',
            'function_count', 'class_count', 'method_count', 'import_count',
            'global_variables', 'constants', 'parameter_count', 'return_statements',
            'exception_handling', 'loop_count', 'nested_loops', 'conditional_count',
            'recursion_count', 'switch_statements',
            'cyclomatic_complexity', 'halstead_length', 'halstead_volume',
            'halstead_difficulty', 'halstead_effort', 'maintainability_index',
            'max_nesting_depth', 'avg_function_length', 'avg_class_size',
            'avg_identifier_length', 'naming_violations',
            'duplicate_lines', 'duplicate_ratio', 'dead_code_lines',
            'todo_count', 'fixme_count',
            'long_methods', 'large_classes', 'long_parameter_lists', 'magic_numbers',
            'hardcoded_credentials', 'sql_queries', 'shell_executions',
            'eval_usage', 'file_operations', 'network_operations',
            'memory_allocations', 'nested_iterations', 'redundant_calculations',
            'object_creations', 'collection_usage', 'expensive_operations',
        ]
    
    def to_dict(self) -> dict:
        return {name: val for name, val in zip(self.feature_names(), self.to_vector())}


class BaseLanguagePlugin(ABC):
    """
    Abstract base class for all language plugins.
    
    Each plugin must:
    1. Parse source code into a ParseResult (with optional AST)
    2. Extract 50+ features into a Features object
    3. Run static analysis to detect issues
    4. Run security analysis
    5. Run performance analysis
    6. Provide a full review() method that orchestrates all of the above
    
    Plugin auto-discovery: The PluginRegistry scans the parsers/ directory and
    loads any class that inherits from BaseLanguagePlugin.
    """
    
    @property
    @abstractmethod
    def language(self) -> str:
        """Language name (e.g., 'Python', 'Java')."""
        ...
    
    @property
    @abstractmethod
    def file_extensions(self) -> list[str]:
        """List of file extensions handled (e.g., ['.py'])."""
        ...
    
    @abstractmethod
    def parse(self, file_path: str, content: str) -> ParseResult:
        """
        Parse source code and return a ParseResult.
        Must not raise — capture errors in ParseResult.parse_errors.
        """
        ...
    
    @abstractmethod
    def extract_features(self, parse_result: ParseResult) -> Features:
        """Extract 50+ code features from a ParseResult."""
        ...
    
    @abstractmethod
    def run_static_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        """
        Run static analysis rules.
        Returns list of Issues (smells, naming, complexity, dead code, etc.)
        """
        ...
    
    @abstractmethod
    def run_security_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        """
        Detect security vulnerabilities.
        Returns list of Issues (injections, hardcoded secrets, unsafe APIs, etc.)
        """
        ...
    
    @abstractmethod
    def run_performance_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        """
        Detect performance issues.
        Returns list of Issues (nested loops, redundant work, etc.)
        """
        ...
    
    def review(self, file_path: str) -> tuple[ParseResult, Features, list[Issue]]:
        """
        Full review pipeline for a single file.
        Orchestrates: parse → extract → static → security → performance.
        
        Returns:
            (ParseResult, Features, all_issues)
        """
        from utils.file_utils import read_file_content
        content = read_file_content(file_path)
        
        parse_result = self.parse(file_path, content)
        features = self.extract_features(parse_result)
        
        all_issues: list[Issue] = []
        all_issues.extend(self.run_static_analysis(parse_result, features))
        all_issues.extend(self.run_security_analysis(parse_result, features))
        all_issues.extend(self.run_performance_analysis(parse_result, features))
        
        # Sort by severity priority
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'INFO': 4}
        all_issues.sort(key=lambda x: (severity_order.get(x.severity, 99), x.line_number))
        
        return parse_result, features, all_issues
