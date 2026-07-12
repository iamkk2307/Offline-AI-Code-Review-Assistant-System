"""
PDF Report Generator
=====================
Generates PDF reports using ReportLab.
"""
import os
from datetime import datetime
from reports.base_generator import BaseReportGenerator


class PDFReportGenerator(BaseReportGenerator):
    @property
    def format(self) -> str: return 'pdf'
    @property
    def extension(self) -> str: return '.pdf'
    
    def generate(self, analysis_data: dict, output_dir: str) -> str:
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
            )
            from reportlab.lib.enums import TA_CENTER
        except ImportError:
            # Fallback to HTML if ReportLab not installed
            from reports.html_generator import HTMLReportGenerator
            gen = HTMLReportGenerator()
            return gen.generate(analysis_data, output_dir)
        
        output_path = self._make_output_path(output_dir, 'code_review_report')
        doc = SimpleDocTemplate(output_path, pagesize=A4,
                                rightMargin=0.75*inch, leftMargin=0.75*inch,
                                topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        styles = getSampleStyleSheet()
        title_style   = ParagraphStyle('Title', parent=styles['Title'], fontSize=24, spaceAfter=12, textColor=colors.HexColor('#6366f1'))
        heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, spaceBefore=16, spaceAfter=8, textColor=colors.HexColor('#1e293b'))
        body_style    = styles['BodyText']
        
        scores  = analysis_data.get('scores', {})
        issue_s = analysis_data.get('issue_summary', {})
        project_name = os.path.basename(analysis_data.get('project_path', 'Project'))
        
        def s(k): return round(scores.get(k, 0), 1)
        
        story = [
            Paragraph(f"Code Review Report", title_style),
            Paragraph(f"Project: {project_name}", body_style),
            Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", body_style),
            Spacer(1, 0.3*inch),
            HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')),
            Spacer(1, 0.2*inch),
            Paragraph("Score Summary", heading_style),
        ]
        
        score_data = [
            ['Metric', 'Score', 'Rating'],
            ['Overall Health', str(s('overall')), self._get_score_label(s('overall'))],
            ['Code Quality', str(s('quality')), self._get_score_label(s('quality'))],
            ['Security', str(s('security')), self._get_score_label(s('security'))],
            ['Maintainability', str(s('maintainability')), self._get_score_label(s('maintainability'))],
            ['Performance', str(s('performance')), self._get_score_label(s('performance'))],
            ['Readability', str(s('readability')), self._get_score_label(s('readability'))],
        ]
        
        score_table = Table(score_data, colWidths=[3*inch, 1.5*inch, 2*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("Issue Summary", heading_style))
        issue_data = [
            ['Severity', 'Count'],
            ['Critical', str(issue_s.get('critical', 0))],
            ['High', str(issue_s.get('high', 0))],
            ['Medium', str(issue_s.get('medium', 0))],
            ['Low', str(issue_s.get('low', 0))],
            ['Info', str(issue_s.get('info', 0))],
            ['Total', str(issue_s.get('total', 0))],
        ]
        issue_table = Table(issue_data, colWidths=[3*inch, 1.5*inch])
        issue_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.white]),
        ]))
        story.append(issue_table)
        
        # Critical Issues
        critical_issues = analysis_data.get('top_critical_issues', [])
        if critical_issues:
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("Critical & High Issues", heading_style))
            for issue in critical_issues[:15]:
                sev = issue.get('severity', '')
                story.append(Paragraph(
                    f"<b>[{sev}] {issue.get('title','')}</b> — {issue.get('filename','')}, Line {issue.get('line_number','')}",
                    body_style
                ))
                story.append(Paragraph(issue.get('description', ''), body_style))
                if issue.get('suggestion'):
                    story.append(Paragraph(f"💡 {issue.get('suggestion','')}", body_style))
                story.append(Spacer(1, 0.1*inch))
        
        doc.build(story)
        return output_path
