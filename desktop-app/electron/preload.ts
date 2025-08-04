import { contextBridge, ipcRenderer } from 'electron'

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Python backend communication
  python: {
    execute: (command: string, args: any[] = []) => 
      ipcRenderer.invoke('python:execute', command, args),
    start: () => ipcRenderer.invoke('python:start'),
    stop: () => ipcRenderer.invoke('python:stop'),
    onOutput: (callback: (data: string) => void) => 
      ipcRenderer.on('python:output', (event, data) => callback(data)),
    onError: (callback: (error: string) => void) => 
      ipcRenderer.on('python:error', (event, error) => callback(error)),
    onExited: (callback: (code: number) => void) => 
      ipcRenderer.on('python:exited', (event, code) => callback(code))
  },

  // System operations
  system: {
    getInfo: () => ipcRenderer.invoke('system:get-info'),
    openFile: (filePath: string) => ipcRenderer.invoke('system:open-file', filePath),
    showDialog: (options: any) => ipcRenderer.invoke('system:show-dialog', options)
  },

  // Settings management
  settings: {
    get: (key: string) => ipcRenderer.invoke('settings:get', key),
    set: (key: string, value: any) => ipcRenderer.invoke('settings:set', key, value)
  },

  // File system operations
  fs: {
    readFile: (filePath: string) => ipcRenderer.invoke('fs:read-file', filePath),
    writeFile: (filePath: string, content: string) => 
      ipcRenderer.invoke('fs:write-file', filePath, content),
    exists: (filePath: string) => ipcRenderer.invoke('fs:exists', filePath)
  },

  // Process management
  process: {
    spawn: (command: string, args: string[] = []) => 
      ipcRenderer.invoke('process:spawn', command, args)
  },

  // WebSocket communication
  websocket: {
    connect: (url: string) => ipcRenderer.invoke('websocket:connect', url),
    onConnected: (callback: (url: string) => void) => 
      ipcRenderer.on('websocket:connected', (event, url) => callback(url)),
    onMessage: (callback: (message: string) => void) => 
      ipcRenderer.on('websocket:message', (event, message) => callback(message)),
    onError: (callback: (error: string) => void) => 
      ipcRenderer.on('websocket:error', (event, error) => callback(error)),
    onClosed: (callback: (url: string) => void) => 
      ipcRenderer.on('websocket:closed', (event, url) => callback(url))
  },

  // Remove event listeners
  removeAllListeners: (channel: string) => {
    ipcRenderer.removeAllListeners(channel)
  },

  // System tray
  tray: {
    showWindow: () => ipcRenderer.invoke('tray:show-window'),
    hideWindow: () => ipcRenderer.invoke('tray:hide-window'),
    updateIcon: (iconPath: string) => ipcRenderer.invoke('tray:update-icon', iconPath),
    onNavigate: (callback: (path: string) => void) => 
      ipcRenderer.on('navigate', (event, path) => callback(path)),
    onOpenCommandPalette: (callback: () => void) => 
      ipcRenderer.on('open-command-palette', (event) => callback())
  }
})

// Type definitions for TypeScript
declare global {
  interface Window {
    electronAPI: {
      python: {
        execute: (command: string, args?: any[]) => Promise<any>
        start: () => Promise<boolean>
        stop: () => Promise<boolean>
        onOutput: (callback: (data: string) => void) => void
        onError: (callback: (error: string) => void) => void
        onExited: (callback: (code: number) => void) => void
      }
      system: {
        getInfo: () => Promise<any>
        openFile: (filePath: string) => Promise<boolean>
        showDialog: (options: any) => Promise<any>
      }
      settings: {
        get: (key: string) => Promise<any>
        set: (key: string, value: any) => Promise<boolean>
      }
      fs: {
        readFile: (filePath: string) => Promise<string>
        writeFile: (filePath: string, content: string) => Promise<boolean>
        exists: (filePath: string) => Promise<boolean>
      }
      process: {
        spawn: (command: string, args?: string[]) => Promise<any>
      }
      websocket: {
        connect: (url: string) => Promise<boolean>
        onConnected: (callback: (url: string) => void) => void
        onMessage: (callback: (message: string) => Promise<void>) => void
        onError: (callback: (error: string) => void) => void
        onClosed: (callback: (url: string) => void) => void
      }
      removeAllListeners: (channel: string) => void
    }
    tray: {
      showWindow: () => Promise<boolean>
      hideWindow: () => Promise<boolean>
      updateIcon: (iconPath: string) => Promise<boolean>
      onNavigate: (callback: (path: string) => void) => void
      onOpenCommandPalette: (callback: () => void) => void
    }
  }
} 