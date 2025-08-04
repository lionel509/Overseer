import React, { useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import { useAppDispatch } from './store/hooks'
import { initializeApp } from './store/appSlice'
import { initializePythonBackend } from './store/pythonSlice'
import { openCommandPalette } from './store/commandPaletteSlice'
import CommandPalette from './components/CommandPalette'
import TrayService from './services/TrayService'
import Dashboard from './components/Dashboard'
import SystemDashboard from './components/SystemDashboard'
import CommandProcessor from './components/CommandProcessor'
import FileSearch from './components/FileSearch'
import ToolRecommender from './components/ToolRecommender'
import RealTimeStats from './components/RealTimeStats'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import './App.css'

function App() {
  const dispatch = useAppDispatch()

  useEffect(() => {
    // Initialize the application
    dispatch(initializeApp())
    dispatch(initializePythonBackend())

    // Initialize tray service
    const trayService = TrayService.getInstance()
    trayService.initialize()

    // Handle tray events
    const handleOpenCommandPalette = () => {
      dispatch(openCommandPalette())
    }

    window.addEventListener('open-command-palette', handleOpenCommandPalette)

    // Request notification permission
    trayService.requestNotificationPermission()

    return () => {
      window.removeEventListener('open-command-palette', handleOpenCommandPalette)
    }
  }, [dispatch])

  return (
    <div className="app">
      <Header />
      <div className="app-content">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/files" element={<FileSearch />} />
            <Route path="/commands" element={<CommandProcessor />} />
            <Route path="/tools" element={<ToolRecommender />} />
            <Route path="/stats" element={<RealTimeStats />} />
            <Route path="/settings" element={<div>Settings</div>} />
            <Route path="/monitoring" element={<SystemDashboard />} />
          </Routes>
        </main>
      </div>
      <CommandPalette />
    </div>
  )
}

export default App 