"""
HTML Report Generator
======================
Generates a complete, self-contained HTML report with inline CSS and Chart.js charts.
"""

import os
import json
from datetime import datetime
from reports.base_generator import BaseReportGenerator


_HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Code Review Report — {project_name}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
:root {{
  --bg: #0f172a; --surface: #1e293b; --surface2: #2d3a4f;
  --primary: #6366f1; --text: #e2e8f0; --muted: #94a3b8;
  --excellent: #10b981; --good: #84cc16; --fair: #f59e0b; --poor: #ef4444;
  --critical: #ef4444; --high: #f97316; --medium: #eab308; --low: #22c55e; --info: #3b82f6;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: var(--bg); color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif; line-height: 1.6; }}
.container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
.header {{ text-align: center; padding: 3rem 0; border-bottom: 1px solid var(--surface2); margin-bottom: 2rem; }}
.header h1 {{ font-size: 2.5rem; background: linear-gradient(135deg, #6366f1, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
.header p {{ color: var(--muted); margin-top: 0.5rem; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 2rem 0; }}
.card {{ background: var(--surface); border-radius: 12px; padding: 1.5rem; border: 1px solid var(--surface2); }}
.card h3 {{ color: var(--muted); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }}
.score {{ font-size: 3rem; font-weight: 700; }}
.score.excellent {{ color: var(--excellent); }}
.score.good {{ color: var(--good); }}
.score.fair {{ color: var(--fair); }}
.score.poor {{ color: var(--poor); }}
.section {{ background: var(--surface); border-radius: 12px; padding: 2rem; border: 1px solid var(--surface2); margin: 1.5rem 0; }}
.section h2 {{ font-size: 1.4rem; margin-bottom: 1.5rem; color: var(--text); border-bottom: 1px solid var(--surface2); padding-bottom: 0.75rem; }}
.issue {{ background: var(--surface2); border-radius: 8px; padding: 1rem; margin: 0.75rem 0; border-left: 4px solid; }}
.issue.CRITICAL {{ border-color: var(--critical); }}
.issue.HIGH {{ border-color: var(--high); }}
.issue.MEDIUM {{ border-color: var(--medium); }}
.issue.LOW {{ border-color: var(--low); }}
.issue.INFO {{ border-color: var(--info); }}
.badge {{ display: inline-block; padding: 0.2em 0.7em; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }}
.badge.CRITICAL {{ background: rgba(239,68,68,0.2); color: var(--critical); }}
.badge.HIGH {{ background: rgba(249,115,22,0.2); color: var(--high); }}
.badge.MEDIUM {{ background: rgba(234,179,8,0.2); color: var(--medium); }}
.badge.LOW {{ background: rgba(34,197,94,0.2); color: var(--low); }}
.badge.INFO {{ background: rgba(59,130,246,0.2); color: var(--info); }}
.chart-container {{ position: relative; height: 300px; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
th {{ background: var(--surface2); padding: 0.75rem 1rem; text-align: left; font-size: 0.85rem; color: var(--muted); text-transform: uppercase; }}
td {{ padding: 0.75rem 1rem; border-bottom: 1px solid var(--surface2); font-size: 0.9rem; }}
tr:hover td {{ background: rgba(99,102,241,0.05); }}
.footer {{ text-align: center; padding: 2rem 0; color: var(--muted); font-size: 0.85rem; border-top: 1px solid var(--surface2); margin-top: 3rem; }}
code {{ background: var(--surface2); padding: 0.1em 0.4em; border-radius: 4px; font-size: 0.85em; font-family: 'Courier New', monospace; }}
</style>
</head>
<body>
<div class="container">

  <div class="header">
    <h1>🔍 Code Review Report</h1>
    <p>Project: <strong>{project_name}</strong> · Generated: {generated_at} · Duration: {duration}s</p>
  </div>

  <!-- Score Cards -->
  <div class="grid">
    <div class="card">
      <h3>Overall Health</h3>
      <div class="score {overall_class}">{overall_score}</div>
      <div style="color:var(--muted);font-size:0.85rem">{overall_label}</div>
    </div>
    <div class="card"><h3>Quality</h3><div class="score {quality_class}">{quality_score}</div></div>
    <div class="card"><h3>Security</h3><div class="score {security_class}">{security_score}</div></div>
    <div class="card"><h3>Maintainability</h3><div class="score {maintainability_class}">{maintainability_score}</div></div>
    <div class="card"><h3>Performance</h3><div class="score {performance_class}">{performance_score}</div></div>
    <div class="card"><h3>Readability</h3><div class="score {readability_class}">{readability_score}</div></div>
  </div>

  <!-- Issue Summary -->
  <div class="section">
    <h2>📊 Issue Summary</h2>
    <div class="grid">
      <div class="card"><h3>Total Issues</h3><div class="score" style="color:var(--primary)">{total_issues}</div></div>
      <div class="card"><h3>Critical</h3><div class="score" style="color:var(--critical)">{critical_issues}</div></div>
      <div class="card"><h3>High</h3><div class="score" style="color:var(--high)">{high_issues}</div></div>
      <div class="card"><h3>Medium</h3><div class="score" style="color:var(--medium)">{medium_issues}</div></div>
      <div class="card"><h3>Low</h3><div class="score" style="color:var(--low)">{low_issues}</div></div>
      <div class="card"><h3>Files Analyzed</h3><div class="score" style="color:var(--muted)">{total_files}</div></div>
    </div>
  </div>

  <!-- Charts -->
  <div class="section">
    <h2>📈 Visual Analysis</h2>
    <div class="grid" style="grid-template-columns: 1fr 1fr;">
      <div>
        <div class="chart-container">
          <canvas id="scoresChart"></canvas>
        </div>
      </div>
      <div>
        <div class="chart-container">
          <canvas id="languageChart"></canvas>
        </div>
      </div>
    </div>
  </div>

  <!-- Language Distribution -->
  <div class="section">
    <h2>🌐 Language Distribution</h2>
    <table>
      <thead><tr><th>Language</th><th>Files</th><th>Percentage</th></tr></thead>
      <tbody>{language_rows}</tbody>
    </table>
  </div>

  <!-- Most Problematic Files -->
  <div class="section">
    <h2>⚠️ Most Problematic Files</h2>
    <table>
      <thead><tr><th>File</th><th>Language</th><th>Score</th><th>Critical</th><th>High</th><th>Medium</th></tr></thead>
      <tbody>{file_rows}</tbody>
    </table>
  </div>

  <!-- Critical Issues -->
  <div class="section">
    <h2>🚨 Critical & High Issues</h2>
    {critical_issues_html}
  </div>

</div>

<script>
// Scores Radar Chart
const scoresCtx = document.getElementById('scoresChart').getContext('2d');
new Chart(scoresCtx, {{
  type: 'radar',
  data: {{
    labels: ['Quality', 'Security', 'Maintainability', 'Performance', 'Readability'],
    datasets: [{{
      label: 'Scores',
      data: [{quality_score}, {security_score}, {maintainability_score}, {performance_score}, {readability_score}],
      backgroundColor: 'rgba(99, 102, 241, 0.2)',
      borderColor: '#6366f1',
      pointBackgroundColor: '#6366f1',
    }}]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    scales: {{ r: {{ min: 0, max: 100, grid: {{ color: '#2d3a4f' }}, ticks: {{ color: '#94a3b8' }}, pointLabels: {{ color: '#e2e8f0' }} }} }},
    plugins: {{ legend: {{ labels: {{ color: '#e2e8f0' }} }} }}
  }}
}});

// Language Donut Chart
const langCtx = document.getElementById('languageChart').getContext('2d');
new Chart(langCtx, {{
  type: 'doughnut',
  data: {{
    labels: {lang_labels},
    datasets: [{{
      data: {lang_values},
      backgroundColor: ['#6366f1','#818cf8','#a5b4fc','#c7d2fe','#e0e7ff','#4f46e5','#4338ca','#3730a3'],
    }}]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    plugins: {{
      legend: {{ position: 'right', labels: {{ color: '#e2e8f0' }} }},
      title: {{ display: true, text: 'Language Distribution', color: '#e2e8f0' }}
    }}
  }}
}});
</script>

<div class="footer">
  <p>Generated by <strong>Offline ML Code Review Assistant v1.0.0</strong> · Fully offline, no cloud services</p>
</div>
</body>
</html>'''


class HTMLReportGenerator(BaseReportGenerator):
    """Generates self-contained HTML reports with Chart.js visualizations."""
    
    @property
    def format(self) -> str: return 'html'
    
    @property
    def extension(self) -> str: return '.html'
    
    def generate(self, analysis_data: dict, output_dir: str) -> str:
        scores  = analysis_data.get('scores', {})
        issue_s = analysis_data.get('issue_summary', {})
        lang    = analysis_data.get('language_distribution', {})
        files   = analysis_data.get('most_problematic_files', [])
        critical_issues = analysis_data.get('top_critical_issues', [])
        
        def score_class(s):
            if s >= 85: return 'excellent'
            if s >= 70: return 'good'
            if s >= 55: return 'fair'
            return 'poor'
        
        def score_label(s):
            if s >= 85: return 'Excellent'
            if s >= 70: return 'Good'
            if s >= 55: return 'Fair'
            if s >= 40: return 'Poor'
            return 'Critical'
        
        def fmt_score(s): return str(round(s, 1))
        
        # Language table rows
        total_files = sum(lang.values()) or 1
        lang_rows = ''.join(
            f'<tr><td>{l}</td><td>{c}</td><td>{c/total_files*100:.1f}%</td></tr>'
            for l, c in lang.items()
        )
        
        # File table rows
        file_rows = ''.join(
            f'<tr><td><code>{f["filename"]}</code></td><td>{f["language"]}</td>'
            f'<td>{round(f.get("overall_score",0),1)}</td>'
            f'<td style="color:var(--critical)">{f["issue_summary"].get("critical",0)}</td>'
            f'<td style="color:var(--high)">{f["issue_summary"].get("high",0)}</td>'
            f'<td style="color:var(--medium)">{f["issue_summary"].get("medium",0)}</td></tr>'
            for f in files[:15]
        )
        
        # Critical issues HTML
        critical_html = ''
        for issue in critical_issues[:20]:
            sev = issue.get('severity', 'INFO')
            critical_html += f'''
            <div class="issue {sev}">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem">
                <strong>{issue.get("title","")}</strong>
                <span class="badge {sev}">{sev}</span>
              </div>
              <div style="color:var(--muted);font-size:0.85rem">{issue.get("filename","")} · Line {issue.get("line_number","")}</div>
              <div style="margin-top:0.5rem">{issue.get("description","")}</div>
              {f'<div style="color:var(--info);margin-top:0.5rem;font-size:0.85rem">💡 {issue.get("suggestion","")}</div>' if issue.get("suggestion") else ""}
            </div>'''
        
        overall = scores.get('overall', 0.0)
        
        html = _HTML_TEMPLATE.format(
            project_name        = os.path.basename(analysis_data.get('project_path', 'Project')),
            generated_at        = datetime.now().strftime('%Y-%m-%d %H:%M'),
            duration            = round(analysis_data.get('duration_seconds', 0), 1),
            overall_score       = fmt_score(overall),
            overall_class       = score_class(overall),
            overall_label       = score_label(overall),
            quality_score       = fmt_score(scores.get('quality', 0)),
            quality_class       = score_class(scores.get('quality', 0)),
            security_score      = fmt_score(scores.get('security', 0)),
            security_class      = score_class(scores.get('security', 0)),
            maintainability_score = fmt_score(scores.get('maintainability', 0)),
            maintainability_class = score_class(scores.get('maintainability', 0)),
            performance_score   = fmt_score(scores.get('performance', 0)),
            performance_class   = score_class(scores.get('performance', 0)),
            readability_score   = fmt_score(scores.get('readability', 0)),
            readability_class   = score_class(scores.get('readability', 0)),
            total_issues        = issue_s.get('total', 0),
            critical_issues     = issue_s.get('critical', 0),
            high_issues         = issue_s.get('high', 0),
            medium_issues       = issue_s.get('medium', 0),
            low_issues          = issue_s.get('low', 0),
            total_files         = analysis_data.get('total_files', 0),
            language_rows       = lang_rows,
            file_rows           = file_rows,
            critical_issues_html = critical_html,
            lang_labels         = json.dumps(list(lang.keys())),
            lang_values         = json.dumps(list(lang.values())),
        )
        
        output_path = self._make_output_path(output_dir, 'code_review_report')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_path
