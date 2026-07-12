"""SQL Language Plugin"""
import re
from parsers.base_plugin import BaseLanguagePlugin, ParseResult, Features, Issue

class SQLPlugin(BaseLanguagePlugin):
    @property
    def language(self) -> str: return 'SQL'
    @property
    def file_extensions(self) -> list[str]: return ['.sql']
    
    def parse(self, file_path: str, content: str) -> ParseResult:
        lines = content.splitlines(keepends=True)
        return ParseResult(language='SQL', file_path=file_path, content=content, lines=lines, is_valid=True)
    
    def extract_features(self, parse_result: ParseResult) -> Features:
        content = parse_result.content; lines = parse_result.lines; f = Features()
        f.loc = len(lines); f.blank_lines = sum(1 for l in lines if l.strip() == '')
        f.comment_lines = sum(1 for l in lines if l.strip().startswith('--'))
        f.sloc = f.loc - f.blank_lines; f.comment_ratio = f.comment_lines / max(f.loc, 1)
        f.function_count = len(re.findall(r'\bCREATE\s+(OR REPLACE\s+)?FUNCTION\b', content, re.IGNORECASE))
        f.class_count = len(re.findall(r'\bCREATE\s+TABLE\b', content, re.IGNORECASE))
        f.sql_queries = len(re.findall(r'\b(SELECT|INSERT|UPDATE|DELETE|MERGE)\b', content, re.IGNORECASE))
        f.conditional_count = len(re.findall(r'\bCASE\s+WHEN\b', content, re.IGNORECASE))
        f.loop_count = len(re.findall(r'\bLOOP\b|\bWHILE\b', content, re.IGNORECASE))
        f.todo_count = len(re.findall(r'--.*\bTODO\b', content, re.IGNORECASE))
        f.cyclomatic_complexity = float(1 + f.conditional_count + f.loop_count)
        f.maintainability_index = 60.0
        return f
    
    def run_static_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []; lines = parse_result.lines
        for i, line in enumerate(lines, 1):
            if re.search(r'\bSELECT\s+\*', line, re.IGNORECASE):
                issues.append(Issue(title="SELECT * Usage", description="SELECT * fetches all columns, including unnecessary ones.", severity="MEDIUM", category="performance", line_number=i, suggestion="List only the columns you need.", rule_id="SQL001", code_snippet=line.strip()[:120]))
            if re.search(r'\bNOLOCK\b', line, re.IGNORECASE):
                issues.append(Issue(title="NOLOCK Hint", description="NOLOCK can cause dirty reads.", severity="HIGH", category="bug", line_number=i, suggestion="Use proper transaction isolation levels.", rule_id="SQL002", code_snippet=line.strip()[:120]))
        return issues
    
    def run_security_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []; lines = parse_result.lines
        for i, line in enumerate(lines, 1):
            if re.search(r"'\s*\+|'\s*\|\|", line):
                issues.append(Issue(title="SQL Injection via Concatenation", description="String concatenation in SQL is injection-prone.", severity="CRITICAL", category="security", line_number=i, suggestion="Use parameterized queries or stored procedures.", rule_id="SQLSec001", code_snippet=line.strip()[:120]))
            if re.search(r'\bGRANT\s+ALL\b', line, re.IGNORECASE):
                issues.append(Issue(title="GRANT ALL Privileges", description="Granting all privileges is a security risk.", severity="HIGH", category="security", line_number=i, suggestion="Grant only the minimum required privileges.", rule_id="SQLSec002", code_snippet=line.strip()[:120]))
        return issues
    
    def run_performance_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []; lines = parse_result.lines
        for i, line in enumerate(lines, 1):
            if re.search(r'\bNOT IN\s*\(', line, re.IGNORECASE):
                issues.append(Issue(title="NOT IN with Subquery", description="NOT IN can be slow with large datasets or NULLs.", severity="MEDIUM", category="performance", line_number=i, suggestion="Use NOT EXISTS or LEFT JOIN for better performance.", rule_id="SQLP001", code_snippet=line.strip()[:120]))
            if re.search(r'\bFUNCTION\b.*\bWHERE\b', line, re.IGNORECASE):
                issues.append(Issue(title="Function in WHERE Clause", description="Functions in WHERE prevent index usage.", severity="HIGH", category="performance", line_number=i, suggestion="Restructure query to avoid function calls on indexed columns.", rule_id="SQLP002", code_snippet=line.strip()[:120]))
        return issues
