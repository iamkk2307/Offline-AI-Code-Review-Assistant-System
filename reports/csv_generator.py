"""
CSV Report Generator
"""
import csv
import os
from datetime import datetime
from reports.base_generator import BaseReportGenerator

class CSVReportGenerator(BaseReportGenerator):
    @property
    def format(self) -> str: return 'csv'
    @property
    def extension(self) -> str: return '.csv'
    
    def generate(self, analysis_data: dict, output_dir: str) -> str:
        output_path = self._make_output_path(output_dir, 'code_review_issues')
        file_results = analysis_data.get('file_results', [])
        
        rows = []
        for fr in file_results:
            for issue in fr.get('issues', []):
                rows.append({
                    'file': fr.get('filename', ''),
                    'language': fr.get('language', ''),
                    'severity': issue.get('severity', ''),
                    'category': issue.get('category', ''),
                    'title': issue.get('title', ''),
                    'description': issue.get('description', ''),
                    'line_number': issue.get('line_number', ''),
                    'suggestion': issue.get('suggestion', ''),
                    'rule_id': issue.get('rule_id', ''),
                    'overall_score': round(fr.get('scores', {}).get('overall', 0), 1),
                })
        
        if not rows:
            rows = [{'file': 'No issues found', 'language': '', 'severity': '', 'category': '', 'title': '', 'description': '', 'line_number': '', 'suggestion': '', 'rule_id': '', 'overall_score': ''}]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        
        return output_path
