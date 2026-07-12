"""
Report Factory
===============
Factory pattern for creating report generators.
"""

from reports.base_generator import BaseReportGenerator


class ReportFactory:
    """Creates the appropriate report generator based on format string."""
    
    @staticmethod
    def create(fmt: str) -> BaseReportGenerator:
        fmt = fmt.lower().strip()
        
        if fmt == 'pdf':
            from reports.pdf_generator import PDFReportGenerator
            return PDFReportGenerator()
        elif fmt in ('html', 'htm'):
            from reports.html_generator import HTMLReportGenerator
            return HTMLReportGenerator()
        elif fmt in ('markdown', 'md'):
            from reports.markdown_generator import MarkdownReportGenerator
            return MarkdownReportGenerator()
        elif fmt == 'json':
            from reports.json_generator import JSONReportGenerator
            return JSONReportGenerator()
        elif fmt == 'csv':
            from reports.csv_generator import CSVReportGenerator
            return CSVReportGenerator()
        else:
            raise ValueError(f"Unsupported report format: {fmt}. Choose from: pdf, html, markdown, json, csv")
