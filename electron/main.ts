/**
 * Electron Main Process
 * =====================
 * Creates the browser window, spawns the Python backend,
 * and manages the application lifecycle.
 */

import { app, BrowserWindow, ipcMain, dialog, shell, Menu, Tray, nativeImage } from 'electron'
import * as path from 'path'
import * as fs from 'fs'
import { spawn, ChildProcess } from 'child_process'

let mainWindow: BrowserWindow | null = null
let pythonProcess: ChildProcess | null = null
let tray: Tray | null = null

const isDev  = process.env.NODE_ENV === 'development' || !app.isPackaged
const PORT   = 5000
const DEV_URL = `http://localhost:5173`

// ── Create Window ─────────────────────────────────────────────────────────────

function createWindow(): void {
  mainWindow = new BrowserWindow({
    width:  1280,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    title: 'Code Review Assistant',
    backgroundColor: '#0f172a',
    show: false,
    frame: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: false,
    },
  })

  // Hide menu bar
  mainWindow.setMenuBarVisibility(false)

  // Load app
  if (isDev) {
    mainWindow.loadURL(DEV_URL)
    mainWindow.webContents.openDevTools({ mode: 'detach' })
  } else {
    mainWindow.loadFile(path.join(__dirname, '../../client/dist/index.html'))
  }

  // Show window when ready to avoid flash
  mainWindow.once('ready-to-show', () => {
    mainWindow?.show()
    mainWindow?.focus()
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

// ── Python Backend ─────────────────────────────────────────────────────────────

function startPythonBackend(): void {
  const serverPath = isDev
    ? path.join(process.cwd(), 'server', 'app.py')
    : path.join(process.resourcesPath, 'server', 'app.py')

  if (!fs.existsSync(serverPath)) {
    console.error(`Server not found: ${serverPath}`)
    return
  }

  const pythonExecutable = process.platform === 'win32' ? 'python' : 'python3'
  const rootDir = isDev ? process.cwd() : path.join(process.resourcesPath)

  pythonProcess = spawn(pythonExecutable, [serverPath, '--port', String(PORT)], {
    cwd: rootDir,
    env: {
      ...process.env,
      PYTHONPATH: rootDir,
      FLASK_ENV: 'production',
    },
    stdio: ['pipe', 'pipe', 'pipe'],
  })

  pythonProcess.stdout?.on('data', (data: Buffer) => {
    console.log('[Python]', data.toString().trim())
  })

  pythonProcess.stderr?.on('data', (data: Buffer) => {
    console.error('[Python Error]', data.toString().trim())
  })

  pythonProcess.on('close', (code: number | null) => {
    console.log(`[Python] Process exited with code ${code}`)
    pythonProcess = null
  })

  pythonProcess.on('error', (err: Error) => {
    console.error('[Python] Failed to start:', err.message)
  })

  console.log(`[Python] Backend started (PID: ${pythonProcess.pid})`)
}

function stopPythonBackend(): void {
  if (pythonProcess) {
    pythonProcess.kill('SIGTERM')
    pythonProcess = null
    console.log('[Python] Backend stopped')
  }
}

// ── IPC Handlers ──────────────────────────────────────────────────────────────

function registerIpcHandlers(): void {
  // Open folder dialog
  ipcMain.handle('dialog:openFolder', async () => {
    const result = await dialog.showOpenDialog(mainWindow!, {
      properties: ['openDirectory'],
      title: 'Select Project Folder',
    })
    if (result.canceled || result.filePaths.length === 0) return null
    return result.filePaths[0]
  })

  // Save file dialog
  ipcMain.handle('dialog:saveFile', async (_, { defaultName, filters }: { defaultName: string; filters: any[] }) => {
    const result = await dialog.showSaveDialog(mainWindow!, {
      defaultPath: defaultName,
      filters,
    })
    if (result.canceled) return null
    return result.filePath
  })

  // Open external link
  ipcMain.handle('shell:openExternal', (_, url: string) => {
    shell.openExternal(url)
  })

  // Open file in system explorer
  ipcMain.handle('shell:showItemInFolder', (_, filePath: string) => {
    shell.showItemInFolder(filePath)
  })

  // Get app version
  ipcMain.handle('app:getVersion', () => app.getVersion())

  // Minimize / maximize / close window
  ipcMain.handle('window:minimize', () => mainWindow?.minimize())
  ipcMain.handle('window:maximize', () => {
    if (mainWindow?.isMaximized()) mainWindow.unmaximize()
    else mainWindow?.maximize()
  })
  ipcMain.handle('window:close', () => mainWindow?.close())
}

// ── App Lifecycle ─────────────────────────────────────────────────────────────

app.whenReady().then(() => {
  registerIpcHandlers()
  startPythonBackend()

  // Wait for backend to start before creating window
  setTimeout(createWindow, isDev ? 500 : 2000)

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', () => {
  stopPythonBackend()
  if (process.platform !== 'darwin') app.quit()
})

app.on('before-quit', () => {
  stopPythonBackend()
})

// Prevent multiple instances
const gotTheLock = app.requestSingleInstanceLock()
if (!gotTheLock) {
  app.quit()
} else {
  app.on('second-instance', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore()
      mainWindow.focus()
    }
  })
}

// Security: disable navigation to untrusted URLs
app.on('web-contents-created', (_, contents) => {
  contents.on('will-navigate', (event, navigationUrl) => {
    const parsedUrl = new URL(navigationUrl)
    if (parsedUrl.origin !== `http://localhost:5173` && !isDev) {
      event.preventDefault()
    }
  })
})
