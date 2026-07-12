"""JSON Language Plugin"""
import re
import json
from parsers.base_plugin import BaseLanguagePlugin, ParseResult, Features, Issue

class JSONPlugin(BaseLanguagePlugin):
    @property
    def language(self) -> str: return 'JSON'
    @property
    def file_extensions(self) -> list[str]: return ['.json', '.jsonc']
    
    def parse(self, file_path: str, content: str) -> ParseResult:
        lines = content.splitlines(keepends=True)
        errors = []
        try:
            # Strip comments from jsonc
            stripped = re.sub(r'//[^\n]*', '', content)
            json.loads(stripped)
        except json.JSONDecodeError as e:
            errors.append(f"JSON parse error at line {e.lineno}: {e.msg}")
        return ParseResult(language='JSON', file_path=file_path, content=content, lines=lines, parse_errors=errors, is_valid=len(errors) == 0)
    
    def extract_features(self, parse_result: ParseResult) -> Features:
        content = parse_result.content; lines = parse_result.lines; f = Features()
        f.loc = len(lines); f.blank_lines = sum(1 for l in lines if l.strip() == '')
        f.sloc = f.loc - f.blank_lines
        f.comment_ratio = 0.0
        f.hardcoded_credentials = len(re.findall(r'"(password|secret|api_key|apikey|token)"\s*:\s*"[^"]{4,}"', content, re.IGNORECASE))
        f.magic_numbers = len(re.findall(r':\s*\d{4,}', content))
        f.cyclomatic_complexity = 1.0; f.maintainability_index = 80.0
        return f
    
    def run_static_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []
        for err in parse_result.parse_errors:
            issues.append(Issue(title="JSON Parse Error", description=err, severity="CRITICAL", category="bug", line_number=1, rule_id="JSON001"))
        if parse_result.is_valid and len(parse_result.content) > 100000:
            issues.append(Issue(title="Large JSON File", description=f"File is {len(parse_result.content)//1024}KB. Consider splitting.", severity="LOW", category="performance", line_number=1, rule_id="JSON002"))
        return issues
    
    def run_security_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []; lines = parse_result.lines
        patterns = [
            (r'"(password|passwd|secret|api_key|apikey|token)"\s*:\s*"[^"]{4,}"', "Hardcoded Credential", "CRITICAL", "JSONSec001"),
            (r'"(private_key|certificate|pem)"\s*:', "Private Key Data", "CRITICAL", "JSONSec002"),
        ]
        for pattern, title, severity, rule_id in patterns:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(Issue(title=title, description=f"Line {i}.", severity=severity, category="security", line_number=i, rule_id=rule_id, code_snippet=line.strip()[:120]))
        return issues
    
    def run_performance_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        return []
