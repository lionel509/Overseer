import { app, BrowserWindow, ipcMain, dialog, shell, Tray, Menu, nativeImage } from 'electron'
import { spawn, ChildProcess } from 'child_process'
import * as path from 'path'
import * as fs from 'fs'
import Store from 'electron-store'

// Initialize electron store for settings
const store = new Store()

interface PythonResponse {
  success: boolean
  data?: any
  error?: string
}

class OverseerDesktop {
  private mainWindow: BrowserWindow | null = null
  private pythonProcess: ChildProcess | null = null
  private systemTray: Tray | null = null
  private isDevelopment = process.env.NODE_ENV === 'development'

  constructor() {
    this.initializeApp()
  }

  private initializeApp(): void {
    app.whenReady().then(() => {
      this.createMainWindow()
      this.setupSystemTray()
      this.setupIPC()
      this.startPythonBackend()
    })

    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') {
        app.quit()
      }
    })

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        this.createMainWindow()
      }
    })

    app.on('before-quit', () => {
      this.cleanup()
    })

    // Prevent app from closing when window is closed (keep in tray)
    app.on('window-all-closed', (event) => {
      if (process.platform !== 'darwin') {
        event.preventDefault()
      }
    })
  }

  private createMainWindow(): void {
    this.mainWindow = new BrowserWindow({
      width: 1200,
      height: 800,
      minWidth: 800,
      minHeight: 600,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, 'preload.js'),
        webSecurity: true
      },
      titleBarStyle: 'default',
      show: false,
      icon: path.join(__dirname, '../public/icon.png')
    })

    // Load the app
    if (this.isDevelopment) {
      this.mainWindow.loadURL('http://localhost:3000')
      this.mainWindow.webContents.openDevTools()
    } else {
      this.mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
    }

    this.mainWindow.once('ready-to-show', () => {
      this.mainWindow?.show()
    })

    this.mainWindow.on('closed', () => {
      this.mainWindow = null
    })

    // Handle external links
    this.mainWindow.webContents.setWindowOpenHandler(({ url }) => {
      shell.openExternal(url)
      return { action: 'deny' }
    })
  }

  private setupSystemTray(): void {
    // Create tray icon
    const iconPath = path.join(__dirname, '../public/icon.png')
    const icon = nativeImage.createFromPath(iconPath)
    
    // Fallback to a simple icon if the file doesn't exist
    if (icon.isEmpty()) {
      // Create a simple icon programmatically
      const canvas = document.createElement('canvas')
      canvas.width = 16
      canvas.height = 16
      const ctx = canvas.getContext('2d')
      if (ctx) {
        ctx.fillStyle = '#3B82F6'
        ctx.fillRect(0, 0, 16, 16)
        ctx.fillStyle = 'white'
        ctx.font = '12px Arial'
        ctx.fillText('O', 4, 12)
      }
      const dataURL = canvas.toDataURL()
      const icon = nativeImage.createFromDataURL(dataURL)
    }

    this.systemTray = new Tray(icon)
    this.systemTray.setToolTip('Overseer Desktop')

    // Create tray menu
    const contextMenu = Menu.buildFromTemplate([
      {
        label: 'Show/Hide Overseer',
        click: () => {
          if (this.mainWindow?.isVisible()) {
            this.mainWindow.hide()
          } else {
            this.mainWindow?.show()
            this.mainWindow?.focus()
          }
        }
      },
      {
        label: 'System Dashboard',
        click: () => {
          this.mainWindow?.show()
          this.mainWindow?.focus()
          this.mainWindow?.webContents.send('navigate', '/monitoring')
        }
      },
      {
        label: 'Command Palette',
        click: () => {
          this.mainWindow?.show()
          this.mainWindow?.focus()
          this.mainWindow?.webContents.send('open-command-palette')
        }
      },
      { type: 'separator' },
      {
        label: 'Start Python Backend',
        click: () => {
          this.startPythonBackend()
        }
      },
      {
        label: 'Stop Python Backend',
        click: () => {
          this.stopPythonBackend()
        }
      },
      { type: 'separator' },
      {
        label: 'Quit Overseer',
        click: () => {
          app.quit()
        }
      }
    ])

    this.systemTray.setContextMenu(contextMenu)

    // Handle tray icon click
    this.systemTray.on('click', () => {
      if (this.mainWindow?.isVisible()) {
        this.mainWindow.hide()
      } else {
        this.mainWindow?.show()
        this.mainWindow?.focus()
      }
    })
  }

  private setupIPC(): void {
    // Python backend communication
    ipcMain.handle('python:execute', async (event, command: string, args: any[] = []) => {
      return this.executePythonCommand(command, args)
    })

    ipcMain.handle('python:start', async () => {
      return this.startPythonBackend()
    })

    ipcMain.handle('python:stop', async () => {
      return this.stopPythonBackend()
    })

    // System operations
    ipcMain.handle('system:get-info', async () => {
      return this.getSystemInfo()
    })

    ipcMain.handle('system:open-file', async (event, filePath: string) => {
      return this.openFile(filePath)
    })

    ipcMain.handle('system:show-dialog', async (event, options: any) => {
      return this.showDialog(options)
    })

    // Settings management
    ipcMain.handle('settings:get', async (event, key: string) => {
      return store.get(key)
    })

    ipcMain.handle('settings:set', async (event, key: string, value: any) => {
      store.set(key, value)
      return true
    })

    // File system operations
    ipcMain.handle('fs:read-file', async (event, filePath: string) => {
      return this.readFile(filePath)
    })

    ipcMain.handle('fs:write-file', async (event, filePath: string, content: string) => {
      return this.writeFile(filePath, content)
    })

    ipcMain.handle('fs:exists', async (event, filePath: string) => {
      return fs.existsSync(filePath)
    })

    // Process management
    ipcMain.handle('process:spawn', async (event, command: string, args: string[] = []) => {
      return this.spawnProcess(command, args)
    })

    // WebSocket communication
    ipcMain.handle('websocket:connect', async (event, url: string) => {
      return this.connectWebSocket(url)
    })

    // System tray actions
    ipcMain.handle('tray:show-window', async () => {
      this.mainWindow?.show()
      this.mainWindow?.focus()
      return true
    })

    ipcMain.handle('tray:hide-window', async () => {
      this.mainWindow?.hide()
      return true
    })

    ipcMain.handle('tray:update-icon', async (event, iconPath: string) => {
      if (this.systemTray) {
        const icon = nativeImage.createFromPath(iconPath)
        this.systemTray.setImage(icon)
      }
      return true
    })
  }

  private async executePythonCommand(command: string, args: any[] = []): Promise<PythonResponse> {
    try {
      if (!this.pythonProcess) {
        throw new Error('Python backend not running')
      }

      const message = JSON.stringify({ command, args })
      this.pythonProcess.stdin?.write(message + '\n')

      return new Promise((resolve) => {
        const timeout = setTimeout(() => {
          resolve({ success: false, error: 'Command timeout' })
        }, 30000)

        const handler = (data: Buffer) => {
          try {
            const response = JSON.parse(data.toString())
            clearTimeout(timeout)
            this.pythonProcess?.stdout?.removeListener('data', handler)
            resolve(response)
          } catch (error) {
            // Continue waiting for valid JSON
          }
        }

        this.pythonProcess?.stdout?.on('data', handler)
      })
    } catch (error) {
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' }
    }
  }

  private startPythonBackend(): boolean {
    try {
      const pythonPath = this.getPythonPath()
      const scriptPath = path.join(__dirname, '../../backend/cli/overseer_cli.py')
      
      if (!fs.existsSync(scriptPath)) {
        console.error('Python script not found:', scriptPath)
        return false
      }

      this.pythonProcess = spawn(pythonPath, [scriptPath, '--desktop-mode'], {
        stdio: ['pipe', 'pipe', 'pipe'],
        cwd: path.join(__dirname, '../../backend')
      })

      this.pythonProcess.on('error', (error) => {
        console.error('Python process error:', error)
        this.mainWindow?.webContents.send('python:error', error.message)
      })

      this.pythonProcess.on('exit', (code) => {
        console.log('Python process exited with code:', code)
        this.pythonProcess = null
        this.mainWindow?.webContents.send('python:exited', code)
      })

      this.pythonProcess.stdout?.on('data', (data) => {
        this.mainWindow?.webContents.send('python:output', data.toString())
      })

      this.pythonProcess.stderr?.on('data', (data) => {
        console.error('Python stderr:', data.toString())
        this.mainWindow?.webContents.send('python:error', data.toString())
      })

      return true
    } catch (error) {
      console.error('Failed to start Python backend:', error)
      return false
    }
  }

  private stopPythonBackend(): boolean {
    if (this.pythonProcess) {
      this.pythonProcess.kill()
      this.pythonProcess = null
      return true
    }
    return false
  }

  private getPythonPath(): string {
    // Try to find Python in common locations
    const pythonPaths = [
      'python3',
      'python',
      '/usr/bin/python3',
      '/usr/local/bin/python3',
      'C:\\Python39\\python.exe',
      'C:\\Python310\\python.exe'
    ]

    for (const pythonPath of pythonPaths) {
      try {
        const result = require('child_process').spawnSync(pythonPath, ['--version'])
        if (result.status === 0) {
          return pythonPath
        }
      } catch (error) {
        // Continue to next path
      }
    }

    throw new Error('Python not found. Please install Python 3.8+ and ensure it\'s in your PATH')
  }

  private getSystemInfo(): any {
    return {
      platform: process.platform,
      arch: process.arch,
      version: process.version,
      electronVersion: process.versions.electron,
      chromeVersion: process.versions.chrome,
      nodeVersion: process.versions.node
    }
  }

  private async openFile(filePath: string): Promise<boolean> {
    try {
      await shell.openPath(filePath)
      return true
    } catch (error) {
      console.error('Failed to open file:', error)
      return false
    }
  }

  private async showDialog(options: any): Promise<any> {
    try {
      const result = await dialog.showOpenDialog(this.mainWindow!, options)
      return result
    } catch (error) {
      console.error('Dialog error:', error)
      return { canceled: true, error: error instanceof Error ? error.message : 'Unknown error' }
    }
  }

  private async readFile(filePath: string): Promise<string> {
    try {
      return fs.readFileSync(filePath, 'utf8')
    } catch (error) {
      throw new Error(`Failed to read file: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  private async writeFile(filePath: string, content: string): Promise<boolean> {
    try {
      fs.writeFileSync(filePath, content, 'utf8')
      return true
    } catch (error) {
      console.error('Failed to write file:', error)
      return false
    }
  }

  private async spawnProcess(command: string, args: string[] = []): Promise<any> {
    try {
      const child = spawn(command, args, {
        stdio: ['pipe', 'pipe', 'pipe']
      })

      return new Promise((resolve) => {
        let stdout = ''
        let stderr = ''

        child.stdout?.on('data', (data) => {
          stdout += data.toString()
        })

        child.stderr?.on('data', (data) => {
          stderr += data.toString()
        })

        child.on('close', (code) => {
          resolve({
            success: code === 0,
            stdout,
            stderr,
            code
          })
        })
      })
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  private async connectWebSocket(url: string): Promise<boolean> {
    try {
      const WebSocket = require('ws')
      const ws = new WebSocket(url)

      ws.on('open', () => {
        this.mainWindow?.webContents.send('websocket:connected', url)
      })

      ws.on('message', (data: Buffer) => {
        this.mainWindow?.webContents.send('websocket:message', data.toString())
      })

      ws.on('error', (error: Error) => {
        this.mainWindow?.webContents.send('websocket:error', error.message)
      })

      ws.on('close', () => {
        this.mainWindow?.webContents.send('websocket:closed', url)
      })

      return true
    } catch (error) {
      console.error('WebSocket connection failed:', error)
      return false
    }
  }

  private cleanup(): void {
    this.stopPythonBackend()
    if (this.systemTray) {
      this.systemTray.destroy()
      this.systemTray = null
    }
  }
}

// Start the application
new OverseerDesktop() 