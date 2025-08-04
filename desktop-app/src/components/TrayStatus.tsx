import React, { useState, useEffect } from 'react'
import { 
  Monitor, 
  Eye, 
  EyeOff, 
  Bell, 
  BellOff,
  Settings,
  Info
} from 'lucide-react'
import TrayService from '../services/TrayService'

const TrayStatus: React.FC = () => {
  const [isVisible, setIsVisible] = useState(true)
  const [notificationsEnabled, setNotificationsEnabled] = useState(false)
  const [trayService] = useState(TrayService.getInstance())

  useEffect(() => {
    // Check notification permission on mount
    const checkNotificationPermission = async () => {
      const hasPermission = await trayService.requestNotificationPermission()
      setNotificationsEnabled(hasPermission)
    }
    
    checkNotificationPermission()
  }, [trayService])

  const handleToggleVisibility = async () => {
    if (isVisible) {
      await trayService.hideWindow()
      setIsVisible(false)
    } else {
      await trayService.showWindow()
      setIsVisible(true)
    }
  }

  const handleToggleNotifications = async () => {
    if (notificationsEnabled) {
      setNotificationsEnabled(false)
    } else {
      const hasPermission = await trayService.requestNotificationPermission()
      setNotificationsEnabled(hasPermission)
    }
  }

  const handleShowNotification = () => {
    trayService.showNotification(
      'Overseer Desktop',
      'System monitoring is active and running smoothly.',
      { silent: false }
    )
  }

  const handleShowAlert = () => {
    trayService.showAlert('System tray is working correctly!', 'info')
  }

  return (
    <div className="bg-white rounded-lg shadow border p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Monitor className="w-6 h-6 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">System Tray</h3>
        </div>
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${isVisible ? 'bg-green-500' : 'bg-gray-400'}`}></div>
          <span className="text-sm text-gray-600">
            {isVisible ? 'Window Visible' : 'Window Hidden'}
          </span>
        </div>
      </div>

      <div className="space-y-4">
        {/* Visibility Controls */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {isVisible ? <Eye className="w-4 h-4 text-gray-600" /> : <EyeOff className="w-4 h-4 text-gray-600" />}
            <span className="text-sm text-gray-700">Window Visibility</span>
          </div>
          <button
            onClick={handleToggleVisibility}
            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            {isVisible ? 'Hide' : 'Show'}
          </button>
        </div>

        {/* Notification Controls */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {notificationsEnabled ? <Bell className="w-4 h-4 text-gray-600" /> : <BellOff className="w-4 h-4 text-gray-600" />}
            <span className="text-sm text-gray-700">Notifications</span>
          </div>
          <button
            onClick={handleToggleNotifications}
            className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
          >
            {notificationsEnabled ? 'Disable' : 'Enable'}
          </button>
        </div>

        {/* Test Controls */}
        <div className="pt-4 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Info className="w-4 h-4 text-gray-600" />
              <span className="text-sm text-gray-700">Test Functions</span>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={handleShowNotification}
                className="px-3 py-1 text-sm bg-purple-600 text-white rounded hover:bg-purple-700 transition-colors"
              >
                Test Notification
              </button>
              <button
                onClick={handleShowAlert}
                className="px-3 py-1 text-sm bg-orange-600 text-white rounded hover:bg-orange-700 transition-colors"
              >
                Test Alert
              </button>
            </div>
          </div>
        </div>

        {/* Tray Info */}
        <div className="pt-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 space-y-1">
            <p>• Right-click the tray icon for quick access</p>
            <p>• Click tray icon to show/hide window</p>
            <p>• System metrics are displayed in tray tooltip</p>
            <p>• Notifications for system alerts</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TrayStatus 