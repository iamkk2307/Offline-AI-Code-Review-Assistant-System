/**
 * Global Zustand State Store
 * Manages application state: projects, current analysis, settings, and UI state.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  Project, AnalysisResult, AnalysisJob, AppSettings, AnalysisSummary
} from '@/types';

interface AppState {
  // Server status
  serverOnline: boolean;
  setServerOnline: (v: boolean) => void;
  serverCwd: string;
  setServerCwd: (v: string) => void;

  // Projects
  projects: Project[];
  selectedProject: Project | null;
  setProjects: (p: Project[]) => void;
  setSelectedProject: (p: Project | null) => void;
  addProject: (p: Project) => void;
  removeProject: (id: number) => void;

  // Analysis
  currentJob: AnalysisJob | null;
  currentAnalysis: AnalysisResult | null;
  analysisHistory: AnalysisSummary[];
  setCurrentJob: (j: AnalysisJob | null) => void;
  setCurrentAnalysis: (a: AnalysisResult | null) => void;
  setAnalysisHistory: (h: AnalysisSummary[]) => void;

  // Navigation
  activePage: string;
  setActivePage: (p: string) => void;

  // Settings
  settings: AppSettings;
  setSettings: (s: Partial<AppSettings>) => void;

  // UI
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (v: boolean) => void;
  isAnalyzing: boolean;
  setIsAnalyzing: (v: boolean) => void;
}

const DEFAULT_SETTINGS: AppSettings = {
  theme: 'dark',
  language: 'en',
  report_output_dir: '',
  auto_save: true,
  analysis_on_open: false,
  max_workers: 4,
  show_info_issues: true,
  default_report_format: 'html',
};

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // Server
      serverOnline: false,
      setServerOnline: (v) => set({ serverOnline: v }),
      serverCwd: '',
      setServerCwd: (v) => set({ serverCwd: v }),

      // Projects
      projects: [],
      selectedProject: null,
      setProjects: (projects) => set({ projects }),
      setSelectedProject: (selectedProject) => set({ selectedProject }),
      addProject: (p) => set((s) => ({ projects: [p, ...s.projects.filter(x => x.id !== p.id)] })),
      removeProject: (id) => set((s) => ({
        projects: s.projects.filter(p => p.id !== id),
        selectedProject: s.selectedProject?.id === id ? null : s.selectedProject,
      })),

      // Analysis
      currentJob: null,
      currentAnalysis: null,
      analysisHistory: [],
      setCurrentJob: (currentJob) => set({ currentJob }),
      setCurrentAnalysis: (currentAnalysis) => set({ currentAnalysis }),
      setAnalysisHistory: (analysisHistory) => set({ analysisHistory }),

      // Navigation
      activePage: 'dashboard',
      setActivePage: (activePage) => set({ activePage }),

      // Settings
      settings: DEFAULT_SETTINGS,
      setSettings: (s) => set((state) => ({ settings: { ...state.settings, ...s } })),

      // UI
      sidebarCollapsed: false,
      setSidebarCollapsed: (sidebarCollapsed) => set({ sidebarCollapsed }),
      isAnalyzing: false,
      setIsAnalyzing: (isAnalyzing) => set({ isAnalyzing }),
    }),
    {
      name: 'code-review-app-store',
      partialize: (state) => ({
        settings: state.settings,
        selectedProject: state.selectedProject,
        sidebarCollapsed: state.sidebarCollapsed,
      }),
    }
  )
);
