import { useEffect, useState, useCallback } from 'react'
import { FolderOpen, Trash2, Plus, RefreshCw, Clock, FileCode } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAppStore } from '@/stores/appStore'
import { PageHeader, EmptyState, LoadingShimmer } from '@/components/common'
import api from '@/services/api'
import type { Project } from '@/types'

export default function Projects() {
  const { projects, setProjects, selectedProject, setSelectedProject, addProject, removeProject, setActivePage, serverCwd } = useAppStore()
  const [loading, setLoading] = useState(false)
  const [creating, setCreating] = useState(false)
  const [newPath, setNewPath] = useState('')
  const [newName, setNewName] = useState('')
  const [showForm, setShowForm] = useState(false)
  const isElectron = !!(window as any).electronAPI

  const handleBrowseFolder = async () => {
    const win = window as any
    if (win.electronAPI) {
      const path = await win.electronAPI.openFolder()
      if (path) {
        setNewPath(path)
        const folderName = path.split(/[/\\]/).pop() || ''
        if (folderName) setNewName(folderName)
      }
    } else {
      document.getElementById('browser-folder-input')?.click()
    }
  }

  const handleBrowserFolderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      const firstFile = files[0]
      const relativePath = firstFile.webkitRelativePath
      const folderName = relativePath.split('/')[0]
      if (folderName) {
        setNewName(folderName)
        const separator = serverCwd.includes('/') ? '/' : '\\'
        const baseDir = serverCwd || 'C:\\Users\\default\\Documents'
        setNewPath(`${baseDir}${separator}${folderName}`)
        toast("Folder parsed. Browser mode: please verify/adjust the absolute path so Python can access it.", { icon: '📂', duration: 6000 })
      }
    }
  }

  const loadProjects = useCallback(async () => {
    setLoading(true)
    try {
      const data = await api.projects.list()
      setProjects(data)
    } catch (e: any) {
      toast.error('Failed to load projects: ' + e.message)
    } finally {
      setLoading(false)
    }
  }, [setProjects])

  useEffect(() => { loadProjects() }, [loadProjects])

  const handleCreate = async () => {
    if (!newPath.trim()) { toast.error('Please enter a project path'); return }
    setCreating(true)
    try {
      const project = await api.projects.create(
        newName.trim() || newPath.split(/[/\\]/).pop() || 'Project',
        newPath.trim()
      )
      addProject(project)
      setSelectedProject(project)
      setNewPath(''); setNewName(''); setShowForm(false)
      toast.success(`Project "${project.name}" added!`)
      setActivePage('dashboard')
    } catch (e: any) {
      toast.error(e.message)
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (project: Project) => {
    if (!confirm(`Delete project "${project.name}"? This cannot be undone.`)) return
    try {
      await api.projects.delete(project.id)
      removeProject(project.id)
      toast.success('Project deleted')
    } catch (e: any) {
      toast.error(e.message)
    }
  }

  const handleSelect = (project: Project) => {
    setSelectedProject(project)
    setActivePage('dashboard')
    toast.success(`Switched to "${project.name}"`)
  }

  return (
    <div className="animate-slide-up">
      <PageHeader
        title="Projects"
        subtitle="Manage your code review workspaces"
        actions={
          <div className="flex gap-2">
            <button onClick={loadProjects} className="btn-secondary">
              <RefreshCw size={14} /> Refresh
            </button>
            <button onClick={() => setShowForm(!showForm)} className="btn-primary">
              <Plus size={14} /> Open Project
            </button>
          </div>
        }
      />

      <div className="p-6 space-y-4">
        {/* Add Project Form */}
        {showForm && (
          <div className="glass-card p-5 animate-scale-in border border-primary-500/20">
            <h3 className="text-sm font-semibold text-slate-300 mb-4">Open Project Folder</h3>
            <div className="space-y-3">
              <div className="flex gap-2">
                <input
                  className="input"
                  placeholder="Project path (e.g. C:\Users\you\myproject)"
                  value={newPath}
                  onChange={e => setNewPath(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && handleCreate()}
                />
                <button
                  type="button"
                  onClick={handleBrowseFolder}
                  className="btn-secondary whitespace-nowrap flex-shrink-0"
                  title="Browse local folder"
                >
                  <FolderOpen size={14} /> Browse...
                </button>
                <input
                  type="file"
                  id="browser-folder-input"
                  // @ts-ignore
                  webkitdirectory=""
                  // @ts-ignore
                  directory=""
                  multiple
                  style={{ display: 'none' }}
                  onChange={handleBrowserFolderChange}
                />
              </div>
              {!isElectron && (
                <div className="text-[10px] text-amber-600 dark:text-amber-400 bg-amber-500/5 border border-amber-500/10 p-3 rounded-lg leading-relaxed">
                  ⚠️ <strong>Browser Security Constraint</strong>: Standard browsers cannot auto-detect absolute local paths. Please type or paste your repository's actual local absolute path (e.g. <code>C:\projects\my-app</code>) in the field above.
                </div>
              )}
              <input
                className="input"
                placeholder="Project name (optional — auto-detected from path)"
                value={newName}
                onChange={e => setNewName(e.target.value)}
              />
              <div className="flex gap-2">
                <button onClick={handleCreate} disabled={creating} className="btn-primary">
                  {creating ? <RefreshCw size={14} className="animate-spin" /> : <FolderOpen size={14} />}
                  {creating ? 'Opening...' : 'Open Project'}
                </button>
                <button onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
              </div>
            </div>
          </div>
        )}

        {/* Projects List */}
        {loading && <LoadingShimmer rows={3} height="h-24" />}

        {!loading && projects.length === 0 && (
          <EmptyState
            icon={<FolderOpen size={48} />}
            title="No Projects Yet"
            description="Open a folder containing source code to start analyzing it."
            action={
              <button onClick={() => setShowForm(true)} className="btn-primary">
                <Plus size={14} /> Open First Project
              </button>
            }
          />
        )}

        {!loading && projects.map((project) => (
          <div
            key={project.id}
            className={`glass-card p-5 hover:border-primary-500/20 transition-all duration-200 cursor-pointer ${selectedProject?.id === project.id ? 'border-primary-500/40 bg-primary-500/5' : ''}`}
            onClick={() => handleSelect(project)}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3 min-w-0">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${selectedProject?.id === project.id ? 'bg-primary-600' : 'bg-surface-700'}`}>
                  <FolderOpen size={18} className={selectedProject?.id === project.id ? 'text-white' : 'text-slate-400'} />
                </div>
                <div className="min-w-0">
                  <div className="font-semibold text-slate-200 flex items-center gap-2">
                    {project.name}
                    {selectedProject?.id === project.id && (
                      <span className="text-[10px] bg-primary-600/30 text-primary-400 px-2 py-0.5 rounded-full font-medium">Active</span>
                    )}
                  </div>
                  <div className="text-xs text-slate-500 font-mono truncate mt-0.5">{project.path}</div>
                  <div className="flex items-center gap-3 mt-2 text-xs text-slate-500">
                    <span className="flex items-center gap-1">
                      <FileCode size={10} /> {project.total_files} files
                    </span>
                    {project.last_analyzed && (
                      <span className="flex items-center gap-1">
                        <Clock size={10} /> {new Date(project.last_analyzed).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>
              </div>
              <button
                onClick={e => { e.stopPropagation(); handleDelete(project) }}
                className="btn-danger ml-2 flex-shrink-0"
              >
                <Trash2 size={14} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
