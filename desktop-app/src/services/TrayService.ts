import { useAppDispatch } from '../store/hooks'
import { openCommandPalette } from '../store/commandPaletteSlice'

class TrayService {
  private static instance: TrayService
  private isInitialized = false

  private constructor() {}

  static getInstance(): TrayService {
    if (!TrayService.instance) {
      TrayService.instance = new TrayService()
    }
    return TrayService.instance
  }

  initialize(): void {
    if (this.isInitialized) return

    // Listen for navigation events from tray
    window.electronAPI.tray.onNavigate((path: string) => {
      // Navigate to the specified path
      window.location.hash = path
    })

    // Listen for command palette events from tray
    window.electronAPI.tray.onOpenCommandPalette(() => {
      // This will be handled by the App component
      window.dispatchEvent(new CustomEvent('open-command-palette'))
    })

    this.isInitialized = true
  }

  showWindow(): Promise<boolean> {
    return window.electronAPI.tray.showWindow()
  }

  hideWindow(): Promise<boolean> {
    return window.electronAPI.tray.hideWindow()
  }

  updateIcon(iconPath: string): Promise<boolean> {
    return window.electronAPI.tray.updateIcon(iconPath)
  }

  // Show system notification
  showNotification(title: string, body: string, options?: NotificationOptions): void {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, {
        body,
        icon: '/icon.png',
        ...options
      })
    }
  }

  // Request notification permission
  async requestNotificationPermission(): Promise<boolean> {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission()
      return permission === 'granted'
    }
    return false
  }

  // Show system alert
  showAlert(message: string, type: 'info' | 'warning' | 'error' = 'info'): void {
    // Create a custom alert that works with Electron
    const alertDiv = document.createElement('div')
    alertDiv.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
      type === 'error' ? 'bg-red-500 text-white' :
      type === 'warning' ? 'bg-yellow-500 text-white' :
      'bg-blue-500 text-white'
    }`
    alertDiv.textContent = message
    
    document.body.appendChild(alertDiv)
    
    // Remove after 3 seconds
    setTimeout(() => {
      if (alertDiv.parentNode) {
        alertDiv.parentNode.removeChild(alertDiv)
      }
    }, 3000)
  }

  // Update tray tooltip
  updateTooltip(tooltip: string): void {
    // This would require additional IPC communication
    // For now, we'll use the existing tray API
    console.log('Tray tooltip updated:', tooltip)
  }

  // Get system metrics for tray display
  async getSystemMetrics(): Promise<{
    cpu: number
    memory: number
    disk: number
  } | null> {
    try {
      const result = await window.electronAPI.python.execute('get_metrics')
      if (result.success && result.data) {
        return {
          cpu: result.data.cpu_percent || 0,
          memory: result.data.memory_percent || 0,
          disk: result.data.disk_usage || 0
        }
      }
    } catch (error) {
      console.error('Failed to get system metrics for tray:', error)
    }
    return null
  }

  // Show system metrics in tray tooltip
  async updateTrayWithMetrics(): Promise<void> {
    const metrics = await this.getSystemMetrics()
    if (metrics) {
      const tooltip = `Overseer Desktop
CPU: ${metrics.cpu.toFixed(1)}%
Memory: ${metrics.memory.toFixed(1)}%
Disk: ${metrics.disk.toFixed(1)}%`
      
      this.updateTooltip(tooltip)
    }
  }
}

export default TrayService 