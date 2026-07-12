"""HTML Language Plugin"""
import re
from parsers.base_plugin import BaseLanguagePlugin, ParseResult, Features, Issue

class HTMLPlugin(BaseLanguagePlugin):
    @property
    def language(self) -> str: return 'HTML'
    @property
    def file_extensions(self) -> list[str]: return ['.html', '.htm', '.xhtml']
    
    def parse(self, file_path: str, content: str) -> ParseResult:
        lines = content.splitlines(keepends=True)
        errors = []
        if content.count('<') != content.count('>'):
            errors.append("Warning: Unbalanced angle brackets.")
        return ParseResult(language='HTML', file_path=file_path, content=content, lines=lines, parse_errors=errors, is_valid=True)
    
    def extract_features(self, parse_result: ParseResult) -> Features:
        content = parse_result.content; lines = parse_result.lines; f = Features()
        f.loc = len(lines); f.blank_lines = sum(1 for l in lines if l.strip() == '')
        f.comment_lines = content.count('<!--')
        f.sloc = f.loc - f.blank_lines; f.comment_ratio = f.comment_lines / max(f.loc, 1)
        f.function_count = len(re.findall(r'<script\b', content, re.IGNORECASE))
        f.import_count = len(re.findall(r'<(script|link)\b', content, re.IGNORECASE))
        f.todo_count = len(re.findall(r'<!--.*\bTODO\b', content, re.IGNORECASE))
        f.fixme_count = len(re.findall(r'<!--.*\bFIXME\b', content, re.IGNORECASE))
        f.eval_usage = len(re.findall(r'\beval\s*\(', content))
        f.sql_queries = 0; f.cyclomatic_complexity = 1.0; f.maintainability_index = 50.0
        return f
    
    def run_static_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []; lines = parse_result.lines; content = parse_result.content
        if not re.search(r'<!DOCTYPE html>', content, re.IGNORECASE):
            issues.append(Issue(title="Missing DOCTYPE", description="HTML5 DOCTYPE declaration is missing.", severity="MEDIUM", category="style", line_number=1, suggestion="Add <!DOCTYPE html> at the top.", rule_id="HTML001"))
        if not re.search(r'<meta\s+[^>]*charset', content, re.IGNORECASE):
            issues.append(Issue(title="Missing Charset Meta", description="Character encoding is not declared.", severity="LOW", category="style", line_number=1, suggestion='Add <meta charset="UTF-8">.', rule_id="HTML002"))
        if not re.search(r'<title>', content, re.IGNORECASE):
            issues.append(Issue(title="Missing <title>", description="Page has no title element.", severity="MEDIUM", category="style", line_number=1, suggestion="Add a descriptive <title> for SEO.", rule_id="HTML003"))
        for i, line in enumerate(lines, 1):
            if re.search(r'<img\b(?![^>]*\balt=)', line, re.IGNORECASE):
                issues.append(Issue(title="Missing alt Attribute", description="Image tag missing alt attribute.", severity="LOW", category="style", line_number=i, suggestion='Add alt="description" for accessibility.', rule_id="HTML004", code_snippet=line.strip()[:120]))
        return issues
    
    def run_security_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []; lines = parse_result.lines
        patterns = [
            (r'on\w+\s*=\s*["\'].*\beval\b', "Inline Event Handler with eval", "CRITICAL", "HTMLSec001"),
            (r'<script[^>]*>.*?</script>', "Inline Script Block", "INFO", "HTMLSec002"),
            (r'javascript:', "javascript: Protocol", "HIGH", "HTMLSec003"),
            (r'<!--.*password.*-->', "Password in HTML Comment", "CRITICAL", "HTMLSec004"),
        ]
        for pattern, title, severity, rule_id in patterns:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE | re.DOTALL):
                    issues.append(Issue(title=title, description=f"Line {i}.", severity=severity, category="security", line_number=i, rule_id=rule_id, code_snippet=line.strip()[:120]))
        return issues
    
    def run_performance_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []; content = parse_result.content
        script_count = len(re.findall(r'<script\b', content, re.IGNORECASE))
        if script_count > 5:
            issues.append(Issue(title="Many Script Tags", description=f"Found {script_count} script tags. Bundle JS files.", severity="MEDIUM", category="performance", line_number=1, suggestion="Use a bundler like Webpack or Vite.", rule_id="HTMLP001"))
        return issues
