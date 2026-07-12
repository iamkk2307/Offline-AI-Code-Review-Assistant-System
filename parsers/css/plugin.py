"""CSS Language Plugin"""
import re
from parsers.base_plugin import BaseLanguagePlugin, ParseResult, Features, Issue

class CSSPlugin(BaseLanguagePlugin):
    @property
    def language(self) -> str: return 'CSS'
    @property
    def file_extensions(self) -> list[str]: return ['.css', '.scss', '.sass', '.less']
    
    def parse(self, file_path: str, content: str) -> ParseResult:
        lines = content.splitlines(keepends=True)
        errors = []
        if content.count('{') != content.count('}'):
            errors.append("Unbalanced curly braces in CSS.")
        return ParseResult(language='CSS', file_path=file_path, content=content, lines=lines, parse_errors=errors, is_valid=True)
    
    def extract_features(self, parse_result: ParseResult) -> Features:
        content = parse_result.content; lines = parse_result.lines; f = Features()
        f.loc = len(lines); f.blank_lines = sum(1 for l in lines if l.strip() == '')
        f.comment_lines = content.count('/*')
        f.sloc = f.loc - f.blank_lines; f.comment_ratio = f.comment_lines / max(f.loc, 1)
        f.class_count = len(re.findall(r'\.[a-zA-Z][\w-]+\s*\{', content))
        f.todo_count = len(re.findall(r'/\*.*\bTODO\b', content, re.IGNORECASE))
        f.magic_numbers = len(re.findall(r':\s*\d+px', content))
        f.duplicate_lines = len(re.findall(r'([a-z-]+:\s*[^;]+;).*\1', content, re.DOTALL))
        f.cyclomatic_complexity = 1.0; f.maintainability_index = 70.0
        return f
    
    def run_static_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []; lines = parse_result.lines
        for i, line in enumerate(lines, 1):
            if re.search(r'!important', line):
                issues.append(Issue(title="!important Override", description="Using !important makes CSS hard to maintain.", severity="LOW", category="style", line_number=i, suggestion="Increase selector specificity instead.", rule_id="CSS001", code_snippet=line.strip()[:120]))
            if re.search(r'#[a-zA-Z][\w-]+', line) and '{' in line:
                issues.append(Issue(title="ID Selector in CSS", description="ID selectors are too specific and hard to override.", severity="LOW", category="style", line_number=i, suggestion="Use class selectors for reusability.", rule_id="CSS002", code_snippet=line.strip()[:120]))
        return issues
    
    def run_security_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []; lines = parse_result.lines
        for i, line in enumerate(lines, 1):
            if re.search(r'expression\s*\(', line, re.IGNORECASE):
                issues.append(Issue(title="CSS expression() Usage", description="CSS expression() can execute JavaScript.", severity="CRITICAL", category="security", line_number=i, rule_id="CSSec001", code_snippet=line.strip()[:120]))
            if re.search(r'url\s*\(\s*["\']?data:', line, re.IGNORECASE):
                issues.append(Issue(title="Data URI in CSS", description="Data URIs can be used to embed malicious content.", severity="MEDIUM", category="security", line_number=i, rule_id="CSSec002", code_snippet=line.strip()[:120]))
        return issues
    
    def run_performance_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []; content = parse_result.content
        if len(re.findall(r'\*\s*\{', content)) > 0:
            issues.append(Issue(title="Universal Selector (*)", description="Universal selector matches all elements and is slow.", severity="MEDIUM", category="performance", line_number=1, suggestion="Use specific selectors.", rule_id="CSSP001"))
        return issues
