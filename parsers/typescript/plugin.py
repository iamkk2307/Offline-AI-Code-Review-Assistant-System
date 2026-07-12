"""
TypeScript Language Plugin
==========================
Extends JavaScript analysis with TypeScript-specific rules.
"""

import re
import math
from parsers.base_plugin import BaseLanguagePlugin, ParseResult, Features, Issue
from parsers.javascript.plugin import JavaScriptPlugin


class TypeScriptPlugin(BaseLanguagePlugin):
    """Language plugin for TypeScript (.ts, .tsx) files."""
    
    @property
    def language(self) -> str:
        return 'TypeScript'
    
    @property
    def file_extensions(self) -> list[str]:
        return ['.ts', '.tsx', '.mts']
    
    def parse(self, file_path: str, content: str) -> ParseResult:
        lines = content.splitlines(keepends=True)
        errors = []
        if content.count('{') != content.count('}'):
            errors.append("Warning: Unbalanced curly braces.")
        return ParseResult(
            language='TypeScript',
            file_path=file_path,
            content=content,
            lines=lines,
            parse_errors=errors,
            is_valid=True,
        )
    
    def extract_features(self, parse_result: ParseResult) -> Features:
        """Reuse JS feature extraction, add TS-specific metrics."""
        js = JavaScriptPlugin()
        # Create a fake JS parse result
        js_result = ParseResult(
            language='JavaScript',
            file_path=parse_result.file_path,
            content=parse_result.content,
            lines=parse_result.lines,
        )
        f = js.extract_features(js_result)
        
        content = parse_result.content
        
        # TypeScript-specific: interface/type definitions
        f.class_count += len(re.findall(r'\b(interface|type)\s+\w+', content))
        
        # 'any' type usage counts as naming violation
        f.naming_violations += len(re.findall(r':\s*any\b', content))
        
        return f
    
    def run_static_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        js = JavaScriptPlugin()
        js_result = ParseResult(
            language='JavaScript',
            file_path=parse_result.file_path,
            content=parse_result.content,
            lines=parse_result.lines,
        )
        issues = js.run_static_analysis(js_result, features)
        
        lines = parse_result.lines
        
        # TypeScript-specific rules
        for i, line in enumerate(lines, 1):
            # 'any' type
            if re.search(r':\s*any\b', line):
                issues.append(Issue(
                    title="TypeScript 'any' Type",
                    description="Using 'any' defeats TypeScript's type safety.",
                    severity="MEDIUM",
                    category="style",
                    line_number=i,
                    suggestion="Use a specific type, 'unknown', or a generic constraint.",
                    rule_id="TS001",
                    code_snippet=line.strip()[:120],
                ))
            # Type assertion with 'as any'
            if re.search(r'\bas\s+any\b', line):
                issues.append(Issue(
                    title="Type Cast to 'any'",
                    description="Casting to 'any' removes all type safety.",
                    severity="HIGH",
                    category="bug",
                    line_number=i,
                    suggestion="Use proper type guards or 'as unknown as TargetType'.",
                    rule_id="TS002",
                    code_snippet=line.strip()[:120],
                ))
            # @ts-ignore
            if re.search(r'@ts-ignore', line):
                issues.append(Issue(
                    title="TypeScript Error Suppression",
                    description="@ts-ignore suppresses type errors silently.",
                    severity="MEDIUM",
                    category="style",
                    line_number=i,
                    suggestion="Fix the underlying type error instead of suppressing it.",
                    rule_id="TS003",
                    code_snippet=line.strip()[:120],
                ))
        
        return issues
    
    def run_security_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        js = JavaScriptPlugin()
        js_result = ParseResult(
            language='JavaScript',
            file_path=parse_result.file_path,
            content=parse_result.content,
            lines=parse_result.lines,
        )
        return js.run_security_analysis(js_result, features)
    
    def run_performance_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        js = JavaScriptPlugin()
        js_result = ParseResult(
            language='JavaScript',
            file_path=parse_result.file_path,
            content=parse_result.content,
            lines=parse_result.lines,
        )
        return js.run_performance_analysis(js_result, features)
