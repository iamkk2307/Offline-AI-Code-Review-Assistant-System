/**
 * API Service Layer
 * Communicates with the Python Flask backend running at localhost:5000
 */

const BASE_URL = 'http://127.0.0.1:5000/api';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new ApiError(res.status, data.error || `HTTP ${res.status}`);
  }
  return data as T;
}

// ── Health ──────────────────────────────────────────────
export const api = {
  health: () => request<{ status: string; version: string; models_loaded: number; cwd?: string }>('/health'),

  // ── Projects ────────────────────────────────────────
  projects: {
    list:   () => request<import('@/types').Project[]>('/projects/'),
    get:    (id: number) => request<import('@/types').Project>(`/projects/${id}`),
    create: (name: string, path: string) =>
      request<import('@/types').Project>('/projects/', {
        method: 'POST',
        body: JSON.stringify({ name, path }),
      }),
    delete: (id: number) => request<{ message: string }>(`/projects/${id}`, { method: 'DELETE' }),
    stats:  (id: number) => request<{ total_files: number; language_distribution: Record<string, any> }>(`/projects/${id}/stats`),
  },

  // ── Analysis ────────────────────────────────────────
  analysis: {
    start: (projectId: number, options?: object) =>
      request<{ job_id: string; status: string }>('/analysis/start', {
        method: 'POST',
        body: JSON.stringify({ project_id: projectId, options }),
      }),
    status: (jobId: string) =>
      request<import('@/types').AnalysisJob>(`/analysis/status/${jobId}`),
    result: (analysisId: number) =>
      request<import('@/types').AnalysisResult>(`/analysis/results/${analysisId}`),
    history: (projectId: number) =>
      request<import('@/types').AnalysisSummary[]>(`/analysis/project/${projectId}/history`),
    latest: (projectId: number) =>
      request<import('@/types').AnalysisResult>(`/analysis/project/${projectId}/latest`),
    analyzeFile: (filePath: string) =>
      request<import('@/types').FileReviewResult>('/analysis/file', {
        method: 'POST',
        body: JSON.stringify({ file_path: filePath }),
      }),
  },

  // ── Reports ─────────────────────────────────────────
  reports: {
    generate: (analysisId: number, format: string, outputPath?: string) =>
      request<import('@/types').ReportGenResult>('/reports/generate', {
        method: 'POST',
        body: JSON.stringify({ analysis_id: analysisId, format, output_path: outputPath }),
      }),
    list: () => request<any[]>('/reports/list'),
  },

  // ── Search ──────────────────────────────────────────
  search: {
    query: (q: string, filters?: { severity?: string; language?: string; category?: string }) =>
      request<import('@/types').SearchResult>(
        `/search/?q=${encodeURIComponent(q)}${filters?.severity ? `&severity=${filters.severity}` : ''}${filters?.language ? `&language=${filters.language}` : ''}${filters?.category ? `&category=${filters.category}` : ''}`
      ),
  },

  // ── Settings ────────────────────────────────────────
  settings: {
    get:    () => request<import('@/types').AppSettings>('/settings/'),
    update: (settings: Partial<import('@/types').AppSettings>) =>
      request<import('@/types').AppSettings>('/settings/', {
        method: 'PUT',
        body: JSON.stringify(settings),
      }),
    reset: () => request<import('@/types').AppSettings>('/settings/reset', { method: 'POST' }),
  },
};

export default api;
