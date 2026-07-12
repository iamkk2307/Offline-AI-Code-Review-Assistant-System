/**
 * Electron Preload Script
 * =======================
 * Securely exposes a limited API to the renderer process
 * using contextBridge. This is the only way the renderer
 * can communicate with the main process.
 */

import { contextBridge, ipcRenderer } from 'electron'

// Expose safe API to renderer
contextBridge.exposeInMainWorld('electronAPI', {
  // Dialogs
  openFolder:       () => ipcRenderer.invoke('dialog:openFolder'),
  saveFile:         (opts: { defaultName: string; filters: any[] }) =>
                      ipcRenderer.invoke('dialog:saveFile', opts),
  
  // Shell
  openExternal:     (url: string) => ipcRenderer.invoke('shell:openExternal', url),
  showInFolder:     (path: string) => ipcRenderer.invoke('shell:showItemInFolder', path),
  
  // App
  getVersion:       () => ipcRenderer.invoke('app:getVersion'),
  
  // Window controls
  minimize:         () => ipcRenderer.invoke('window:minimize'),
  maximize:         () => ipcRenderer.invoke('window:maximize'),
  closeWindow:      () => ipcRenderer.invoke('window:close'),
})

// Type declaration for renderer use
declare global {
  interface Window {
    electronAPI: {
      openFolder:    () => Promise<string | null>
      saveFile:      (opts: { defaultName: string; filters: any[] }) => Promise<string | null>
      openExternal:  (url: string) => Promise<void>
      showInFolder:  (path: string) => Promise<void>
      getVersion:    () => Promise<string>
      minimize:      () => Promise<void>
      maximize:      () => Promise<void>
      closeWindow:   () => Promise<void>
    }
  }
}
