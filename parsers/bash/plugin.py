"""Bash Language Plugin"""
import re
from parsers.base_plugin import BaseLanguagePlugin, ParseResult, Features, Issue

class BashPlugin(BaseLanguagePlugin):
    @property
    def language(self) -> str: return 'Bash'
    @property
    def file_extensions(self) -> list[str]: return ['.sh', '.bash', '.zsh']
    
    def parse(self, file_path: str, content: str) -> ParseResult:
        lines = content.splitlines(keepends=True)
        return ParseResult(language='Bash', file_path=file_path, content=content, lines=lines, is_valid=True)
    
    def extract_features(self, parse_result: ParseResult) -> Features:
        content = parse_result.content; lines = parse_result.lines; f = Features()
        f.loc = len(lines); f.blank_lines = sum(1 for l in lines if l.strip() == '')
        f.comment_lines = sum(1 for l in lines if l.strip().startswith('#'))
        f.sloc = f.loc - f.blank_lines; f.comment_ratio = f.comment_lines / max(f.loc, 1)
        f.function_count = len(re.findall(r'^\s*\w+\s*\(\s*\)\s*\{', content, re.MULTILINE))
        f.loop_count = len(re.findall(r'\b(for|while|until)\s+', content))
        f.conditional_count = len(re.findall(r'\bif\s+\[', content))
        f.eval_usage = len(re.findall(r'\beval\s+', content))
        f.todo_count = len(re.findall(r'#.*\bTODO\b', content, re.IGNORECASE))
        f.fixme_count = len(re.findall(r'#.*\bFIXME\b', content, re.IGNORECASE))
        f.shell_executions = len(re.findall(r'`[^`]+`|\$\(', content))
        f.cyclomatic_complexity = float(1 + f.conditional_count + f.loop_count)
        f.maintainability_index = 60.0
        return f
    
    def run_static_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []; lines = parse_result.lines
        for i, line in enumerate(lines, 1):
            if re.search(r'\[ .+ \]', line) and not re.search(r'\[\[ .+ \]\]', line):
                issues.append(Issue(title="Use [[ ]] Instead of [ ]", description="[[ ]] is safer and supports more features.", severity="LOW", category="style", line_number=i, rule_id="SH001", code_snippet=line.strip()[:120]))
            if re.search(r'==[^\=]', line) and not re.search(r'\[\[', line):
                issues.append(Issue(title="String Comparison in Single Brackets", description="Use = inside [ ] or == inside [[ ]].", severity="MEDIUM", category="bug", line_number=i, rule_id="SH002", code_snippet=line.strip()[:120]))
        return issues
    
    def run_security_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []; lines = parse_result.lines
        patterns = [
            (r'\beval\s+', "eval Usage", "HIGH", "SHSec001"),
            (r'(password|secret|key)\s*=\s*["\'][^"\']{4,}["\']', "Hardcoded Credential", "CRITICAL", "SHSec002"),
            (r'curl\s+.*-k\b|curl\s+.*--insecure', "Insecure curl (--insecure)", "HIGH", "SHSec003"),
            (r'chmod\s+777', "Dangerous chmod 777", "HIGH", "SHSec004"),
            (r'\$\*|\$@', "Unquoted Shell Variables", "MEDIUM", "SHSec005"),
        ]
        for pattern, title, severity, rule_id in patterns:
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(Issue(title=title, description=f"Line {i}.", severity=severity, category="security", line_number=i, rule_id=rule_id, code_snippet=line.strip()[:120]))
        return issues
    
    def run_performance_analysis(self, parse_result: ParseResult, features: Features) -> list[Issue]:
        issues = []; lines = parse_result.lines
        for i, line in enumerate(lines, 1):
            if re.search(r'\bcat\s+\S+\s*\|\s*grep\b', line):
                issues.append(Issue(title="Useless Use of cat", description="'cat file | grep' can be simplified to 'grep pattern file'.", severity="INFO", category="performance", line_number=i, rule_id="SHP001", code_snippet=line.strip()[:120]))
        return issues
