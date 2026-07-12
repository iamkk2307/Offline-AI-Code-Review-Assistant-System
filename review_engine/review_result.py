"""
Review Result Data Structures
================================
Defines FileReviewResult and ProjectReviewResult with full JSON serialization.
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from parsers.base_plugin import Features, Issue


@dataclass
class FileReviewResult:
    """Complete review result for a single source file."""
    
    file_path: str
    language: str
    
    # Analysis results
    features: Optional[Features] = None
    issues: list[Issue] = field(default_factory=list)
    parse_errors: list[str] = field(default_factory=list)
    
    # ML scores
    ml_scores: dict = field(default_factory=dict)
    
    # Combined scores (0–100)
    scores: dict = field(default_factory=dict)
    
    # Meta
    duration_seconds: float = 0.0
    error: Optional[str] = None
    
    @property
    def issue_summary(self) -> dict:
        """Count issues by severity."""
        summary = {'total': len(self.issues), 'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
        for issue in self.issues:
            key = issue.severity.lower()
            if key in summary:
                summary[key] += 1
        return summary
    
    @property
    def overall_score(self) -> float:
        return self.scores.get('overall', 0.0)
    
    @property
    def relative_path(self) -> str:
        return os.path.basename(self.file_path)
    
    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "filename": os.path.basename(self.file_path),
            "language": self.language,
            "scores": self.scores,
            "ml_scores": self.ml_scores,
            "features": self.features.to_dict() if self.features else {},
            "issues": [i.to_dict() for i in self.issues],
            "issue_summary": self.issue_summary,
            "parse_errors": self.parse_errors,
            "duration_seconds": self.duration_seconds,
            "error": self.error,
        }


class ProjectReviewResult:
    """Aggregated review result for an entire project."""
    
    def __init__(self, project_path: str, file_results: list[FileReviewResult], duration_seconds: float):
        self.project_path = project_path
        self.file_results = file_results
        self.duration_seconds = duration_seconds
    
    @property
    def successful_results(self) -> list[FileReviewResult]:
        return [r for r in self.file_results if not r.error]
    
    @property
    def language_distribution(self) -> dict:
        dist: dict[str, int] = {}
        for r in self.file_results:
            dist[r.language] = dist.get(r.language, 0) + 1
        return dict(sorted(dist.items(), key=lambda x: x[1], reverse=True))
    
    @property
    def aggregate_scores(self) -> dict:
        results = self.successful_results
        if not results:
            return {'overall': 0.0, 'quality': 0.0, 'security': 0.0,
                    'maintainability': 0.0, 'performance': 0.0, 'readability': 0.0}
        
        def avg(key):
            vals = [r.scores.get(key, 0.0) for r in results]
            return round(sum(vals) / max(len(vals), 1), 1)
        
        return {
            'overall':         avg('overall'),
            'quality':         avg('quality'),
            'security':        avg('security'),
            'maintainability': avg('maintainability'),
            'performance':     avg('performance'),
            'readability':     avg('readability'),
        }
    
    @property
    def issue_summary(self) -> dict:
        summary = {'total': 0, 'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
        for r in self.file_results:
            for key, val in r.issue_summary.items():
                summary[key] = summary.get(key, 0) + val
        return summary
    
    @property
    def most_problematic_files(self) -> list[dict]:
        """Top 10 files by issue count, sorted by critical+high count."""
        ranked = sorted(
            self.successful_results,
            key=lambda r: (
                r.issue_summary.get('critical', 0) * 100 +
                r.issue_summary.get('high', 0) * 10 +
                r.issue_summary.get('medium', 0)
            ),
            reverse=True,
        )
        return [
            {
                "file_path": r.file_path,
                "filename": os.path.basename(r.file_path),
                "language": r.language,
                "overall_score": r.overall_score,
                "issue_summary": r.issue_summary,
            }
            for r in ranked[:10]
        ]
    
    @property
    def top_critical_issues(self) -> list[dict]:
        """All CRITICAL and HIGH issues across the project."""
        issues = []
        for r in self.file_results:
            for issue in r.issues:
                if issue.severity in ('CRITICAL', 'HIGH'):
                    d = issue.to_dict()
                    d['file_path'] = r.file_path
                    d['filename'] = os.path.basename(r.file_path)
                    d['language'] = r.language
                    issues.append(d)
        return sorted(issues, key=lambda x: x['severity'] == 'CRITICAL', reverse=True)[:50]
    
    def to_dict(self) -> dict:
        return {
            "project_path":          self.project_path,
            "total_files":           len(self.file_results),
            "analyzed_files":        len(self.successful_results),
            "failed_files":          len(self.file_results) - len(self.successful_results),
            "duration_seconds":      round(self.duration_seconds, 2),
            "scores":                self.aggregate_scores,
            "issue_summary":         self.issue_summary,
            "language_distribution": self.language_distribution,
            "most_problematic_files": self.most_problematic_files,
            "top_critical_issues":   self.top_critical_issues,
            "file_results":          [r.to_dict() for r in self.file_results],
        }
