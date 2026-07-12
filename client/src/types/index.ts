/**
 * TypeScript type definitions for the entire application.
 */

export interface Project {
  id: number;
  name: string;
  path: string;
  description: string;
  created_at: string;
  last_analyzed: string | null;
  total_files: number;
}

export interface Scores {
  overall: number;
  quality: number;
  security: number;
  maintainability: number;
  performance: number;
  readability: number;
  [key: string]: number;
}

export interface IssueSummary {
  total: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  info: number;
  [key: string]: number;
}

export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
export type IssueCategory = 'security' | 'performance' | 'maintainability' | 'style' | 'bug';

export interface Issue {
  title: string;
  description: string;
  severity: Severity;
  category: IssueCategory;
  line_number: number;
  column: number;
  end_line: number;
  suggestion: string;
  reason: string;
  rule_id: string;
  code_snippet: string;
  // Enriched when searching across project
  file_path?: string;
  filename?: string;
  language?: string;
  analysis_id?: number;
}

export interface Features {
  loc: number;
  sloc: number;
  function_count: number;
  class_count: number;
  cyclomatic_complexity: number;
  maintainability_index: number;
  comment_ratio: number;
  duplicate_ratio: number;
  magic_numbers: number;
  nested_loops: number;
  hardcoded_credentials: number;
  eval_usage: number;
  [key: string]: number; // Allow additional features
}

export interface FileReviewResult {
  file_path: string;
  filename: string;
  language: string;
  scores: Scores;
  ml_scores: {
    bug_probability: number;
    security_risk_score: number;
    quality_score: number;
    maintainability_score: number;
    readability_score: number;
    predicted_severity: Severity;
  };
  features: Features;
  issues: Issue[];
  issue_summary: IssueSummary;
  parse_errors: string[];
  duration_seconds: number;
  error: string | null;
}

export interface ProblematicFile {
  file_path: string;
  filename: string;
  language: string;
  overall_score: number;
  issue_summary: IssueSummary;
}

export interface AnalysisResult {
  id: number;
  project_id: number;
  created_at: string;
  duration_seconds: number;
  total_files: number;
  analyzed_files: number;
  failed_files: number;
  scores: Scores;
  issue_summary: IssueSummary;
  language_distribution: Record<string, number>;
  most_problematic_files: ProblematicFile[];
  top_critical_issues: (Issue & { filename: string; language: string })[];
  file_results: FileReviewResult[];
}

export interface AnalysisSummary {
  id: number;
  project_id: number;
  created_at: string;
  duration_seconds: number;
  overall_score: number;
  total_files: number;
  total_issues: number;
  critical_issues: number;
}

export interface AnalysisJob {
  job_id: string;
  project_id: number;
  status: 'queued' | 'collecting_files' | 'running' | 'saving' | 'completed' | 'failed';
  progress: number;
  current_file: string | null;
  total_files: number;
  processed_files: number;
  result_id: number | null;
  error: string | null;
}

export interface SearchResult {
  query: string;
  total: number;
  results: Issue[];
}

export interface AppSettings {
  theme: 'dark' | 'light' | 'auto';
  language: string;
  report_output_dir: string;
  auto_save: boolean;
  analysis_on_open: boolean;
  max_workers: number;
  show_info_issues: boolean;
  default_report_format: string;
}

export interface ReportGenResult {
  success: boolean;
  format: string;
  file_path: string;
  file_name: string;
}
