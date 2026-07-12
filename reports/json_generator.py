"""
JSON Report Generator
"""
import json
import os
from datetime import datetime
from reports.base_generator import BaseReportGenerator

class JSONReportGenerator(BaseReportGenerator):
    @property
    def format(self) -> str: return 'json'
    @property
    def extension(self) -> str: return '.json'
    
    def generate(self, analysis_data: dict, output_dir: str) -> str:
        output_data = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "generator": "Offline ML Code Review Assistant v1.0.0",
                "format": "json",
            },
            **analysis_data,
        }
        output_path = self._make_output_path(output_dir, 'code_review_report')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, default=str)
        return output_path
