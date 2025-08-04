import React, { useEffect } from 'react'
import { useAppDispatch, useAppSelector } from '../store/hooks'
import { getSystemInfo } from '../store/systemSlice'
import { startPythonBackend, stopPythonBackend } from '../store/pythonSlice'
import { openCommandPalette } from '../store/commandPaletteSlice'
import { 
  Monitor, 
  Server, 
  Activity, 
  HardDrive, 
  Memory, 
  Network, 
  Play, 
  Square,
  Command
} from 'lucide-react'
import TrayStatus from './TrayStatus'

const Dashboard: React.FC = () => {
  const dispatch = useAppDispatch()
  const { info, isLoading } = useAppSelector(state => state.system)
  const { isRunning, isConnected, output, error } = useAppSelector(state => state.python)

  useEffect(() => {
    dispatch(getSystemInfo())
  }, [dispatch])

  const handleStartPython = () => {
    dispatch(startPythonBackend())
  }

  const handleStopPython = () => {
    dispatch(stopPythonBackend())
  }

  const handleOpenCommandPalette = () => {
    dispatch(openCommandPalette())
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Overseer Dashboard</h1>
          <p className="text-gray-600">AI-powered system management</p>
        </div>
        <button
          onClick={handleOpenCommandPalette}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Command className="w-4 h-4" />
          <span>Open Command Palette</span>
        </button>
      </div>

      {/* System Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex items-center space-x-3">
            <Monitor className="w-8 h-8 text-blue-600" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900">System Info</h3>
              <p className="text-sm text-gray-600">Platform details</p>
            </div>
          </div>
          {info && (
            <div className="mt-4 space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Platform:</span>
                <span className="font-medium">{info.platform}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Architecture:</span>
                <span className="font-medium">{info.arch}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Node Version:</span>
                <span className="font-medium">{info.nodeVersion}</span>
              </div>
            </div>
          )}
        </div>

        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex items-center space-x-3">
            <Server className="w-8 h-8 text-green-600" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Python Backend</h3>
              <p className="text-sm text-gray-600">AI system status</p>
            </div>
          </div>
          <div className="mt-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Status:</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                isRunning ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {isRunning ? 'Running' : 'Stopped'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Connection:</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                isConnected ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
              }`}>
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={handleStartPython}
                disabled={isRunning}
                className="flex items-center space-x-1 px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Play className="w-3 h-3" />
                <span>Start</span>
              </button>
              <button
                onClick={handleStopPython}
                disabled={!isRunning}
                className="flex items-center space-x-1 px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Square className="w-3 h-3" />
                <span>Stop</span>
              </button>
            </div>
          </div>
        </div>

        <TrayStatus />
      </div>

      {/* Quick Actions Card */}
      <div className="bg-white p-6 rounded-lg shadow border">
        <div className="flex items-center space-x-3">
          <Activity className="w-8 h-8 text-purple-600" />
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Quick Actions</h3>
            <p className="text-sm text-gray-600">Common tasks</p>
          </div>
        </div>
        <div className="mt-4 space-y-2">
          <button
            onClick={handleOpenCommandPalette}
            className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded"
          >
            • System Information
          </button>
          <button
            onClick={handleOpenCommandPalette}
            className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded"
          >
            • File Search
          </button>
          <button
            onClick={handleOpenCommandPalette}
            className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded"
          >
            • Process List
          </button>
          <button
            onClick={handleOpenCommandPalette}
            className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded"
          >
            • Network Status
          </button>
        </div>
      </div>
      </div>

      {/* Python Output */}
      {isRunning && (
        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex items-center space-x-3 mb-4">
            <Server className="w-6 h-6 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">Python Backend Output</h3>
          </div>
          <div className="bg-gray-900 text-green-400 p-4 rounded font-mono text-sm max-h-64 overflow-y-auto">
            {output.length === 0 ? (
              <div className="text-gray-500">No output yet...</div>
            ) : (
              output.map((line, index) => (
                <div key={index} className="whitespace-pre-wrap">{line}</div>
              ))
            )}
          </div>
          {error && (
            <div className="mt-4 p-3 bg-red-100 text-red-800 rounded text-sm">
              Error: {error}
            </div>
          )}
        </div>
      )}

      {/* System Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex items-center space-x-3">
            <HardDrive className="w-6 h-6 text-blue-600" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Disk Usage</h3>
              <p className="text-sm text-gray-600">Storage information</p>
            </div>
          </div>
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-blue-600 h-2 rounded-full" style={{ width: '45%' }}></div>
            </div>
            <div className="flex justify-between text-sm text-gray-600 mt-2">
              <span>45% used</span>
              <span>2.3 GB / 5.1 GB</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex items-center space-x-3">
            <Memory className="w-6 h-6 text-green-600" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Memory Usage</h3>
              <p className="text-sm text-gray-600">RAM information</p>
            </div>
          </div>
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-green-600 h-2 rounded-full" style={{ width: '68%' }}></div>
            </div>
            <div className="flex justify-between text-sm text-gray-600 mt-2">
              <span>68% used</span>
              <span>8.2 GB / 12 GB</span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex items-center space-x-3">
            <Network className="w-6 h-6 text-purple-600" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Network</h3>
              <p className="text-sm text-gray-600">Connection status</p>
            </div>
          </div>
          <div className="mt-4 space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Status:</span>
              <span className="text-green-600 font-medium">Connected</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Speed:</span>
              <span className="font-medium">100 Mbps</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Latency:</span>
              <span className="font-medium">12ms</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard 