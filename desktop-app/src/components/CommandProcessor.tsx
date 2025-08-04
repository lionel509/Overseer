import React, { useState, useEffect, useRef } from 'react'
import { useAppDispatch, useAppSelector } from '../store/hooks'
import { executePythonCommand } from '../store/pythonSlice'
import { 
  Terminal, 
  Play, 
  Stop, 
  RotateCcw, 
  Copy, 
  Download,
  AlertTriangle,
  CheckCircle,
  Clock,
  Command
} from 'lucide-react'

interface CommandResult {
  id: string
  command: string
  output: string
  error?: string
  timestamp: Date
  status: 'running' | 'completed' | 'error'
  duration?: number
}

interface CommandHistory {
  id: string
  command: string
  timestamp: Date
  success: boolean
}

const CommandProcessor: React.FC = () => {
  const dispatch = useAppDispatch()
  const { isConnected } = useAppSelector(state => state.python)
  const [inputCommand, setInputCommand] = useState('')
  const [commandHistory, setCommandHistory] = useState<CommandHistory[]>([])
  const [currentResults, setCurrentResults] = useState<CommandResult[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [autoComplete, setAutoComplete] = useState<string[]>([])
  const [showHistory, setShowHistory] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  // Common commands for auto-complete
  const commonCommands = [
    'ls', 'dir', 'pwd', 'cd', 'mkdir', 'rmdir',
    'cp', 'mv', 'rm', 'touch', 'cat', 'head', 'tail',
    'find', 'grep', 'wc', 'sort', 'uniq', 'cut', 'paste',
    'ps', 'top', 'kill', 'system_info', 'memory_usage',
    'disk_usage', 'network_status', 'process_list',
    'file_search', 'open_terminal', 'start_monitoring'
  ]

  // Command categories
  const commandCategories = {
    'File Operations': ['ls', 'dir', 'pwd', 'cd', 'mkdir', 'rmdir', 'cp', 'mv', 'rm', 'touch', 'cat', 'head', 'tail'],
    'Search & Filter': ['find', 'grep', 'wc', 'sort', 'uniq', 'cut', 'paste'],
    'System Info': ['ps', 'top', 'kill', 'system_info', 'memory_usage', 'disk_usage', 'network_status', 'process_list'],
    'Overseer Commands': ['file_search', 'open_terminal', 'start_monitoring', 'stop_monitoring']
  }

  useEffect(() => {
    // Focus input on mount
    if (inputRef.current) {
      inputRef.current.focus()
    }
  }, [])

  const handleInputChange = (value: string) => {
    setInputCommand(value)
    
    // Auto-complete suggestions
    if (value.trim()) {
      const suggestions = commonCommands.filter(cmd => 
        cmd.toLowerCase().includes(value.toLowerCase())
      ).slice(0, 5)
      setAutoComplete(suggestions)
    } else {
      setAutoComplete([])
    }
  }

  const handleCommandSubmit = async (command: string) => {
    if (!command.trim() || !isConnected) return

    const commandId = Date.now().toString()
    const startTime = Date.now()

    // Add to history
    const historyItem: CommandHistory = {
      id: commandId,
      command: command,
      timestamp: new Date(),
      success: false
    }
    setCommandHistory(prev => [historyItem, ...prev.slice(0, 49)]) // Keep last 50

    // Add to current results
    const result: CommandResult = {
      id: commandId,
      command: command,
      output: '',
      timestamp: new Date(),
      status: 'running'
    }
    setCurrentResults(prev => [result, ...prev.slice(0, 9)]) // Keep last 10

    setIsProcessing(true)

    try {
      // Parse command and arguments
      const parts = command.trim().split(' ')
      const cmd = parts[0]
      const args = parts.slice(1)

      // Execute command
      const response = await dispatch(executePythonCommand({ 
        command: cmd, 
        args: args 
      }))

      const duration = Date.now() - startTime

      // Update result
      setCurrentResults(prev => prev.map(r => 
        r.id === commandId 
          ? {
              ...r,
              output: response.payload?.data ? JSON.stringify(response.payload.data, null, 2) : '',
              error: response.payload?.error,
              status: response.payload?.success ? 'completed' : 'error',
              duration
            }
          : r
      ))

      // Update history
      setCommandHistory(prev => prev.map(h => 
        h.id === commandId 
          ? { ...h, success: response.payload?.success || false }
          : h
      ))

    } catch (error) {
      const duration = Date.now() - startTime
      
      setCurrentResults(prev => prev.map(r => 
        r.id === commandId 
          ? {
              ...r,
              error: error instanceof Error ? error.message : 'Unknown error',
              status: 'error',
              duration
            }
          : r
      ))

      setCommandHistory(prev => prev.map(h => 
        h.id === commandId 
          ? { ...h, success: false }
          : h
      ))
    } finally {
      setIsProcessing(false)
      setInputCommand('')
      setAutoComplete([])
    }
  }

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      event.preventDefault()
      handleCommandSubmit(inputCommand)
    } else if (event.key === 'ArrowUp') {
      event.preventDefault()
      if (commandHistory.length > 0) {
        setInputCommand(commandHistory[0].command)
      }
    } else if (event.key === 'Tab' && autoComplete.length > 0) {
      event.preventDefault()
      setInputCommand(autoComplete[0])
      setAutoComplete([])
    }
  }

  const handleAutoCompleteClick = (suggestion: string) => {
    setInputCommand(suggestion)
    setAutoComplete([])
  }

  const clearResults = () => {
    setCurrentResults([])
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const formatDuration = (ms: number): string => {
    if (ms < 1000) return `${ms}ms`
    return `${(ms / 1000).toFixed(1)}s`
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <Clock className="w-4 h-4 text-blue-500 animate-spin" />
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'error':
        return <AlertTriangle className="w-4 h-4 text-red-500" />
      default:
        return <Command className="w-4 h-4 text-gray-500" />
    }
  }

  if (!isConnected) {
    return (
      <div className="p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-yellow-600" />
            <span className="text-yellow-800">Python backend not connected</span>
          </div>
          <p className="text-yellow-700 mt-2">
            Connect to the Python backend to use command processing.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Command Processor</h1>
          <p className="text-gray-600">Execute system commands and Python operations</p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={clearResults}
            className="flex items-center space-x-1 px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Clear</span>
          </button>
        </div>
      </div>

      {/* Command Input */}
      <div className="bg-white rounded-lg shadow border p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Terminal className="w-6 h-6 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Command Input</h3>
        </div>
        
        <div className="relative">
          <div className="flex items-center space-x-2">
            <span className="text-green-500 font-mono">$</span>
            <input
              ref={inputRef}
              type="text"
              value={inputCommand}
              onChange={(e) => handleInputChange(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Enter command (e.g., ls, system_info, file_search)..."
              className="flex-1 p-2 border border-gray-300 rounded font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isProcessing}
            />
            <button
              onClick={() => handleCommandSubmit(inputCommand)}
              disabled={!inputCommand.trim() || isProcessing}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isProcessing ? (
                <div className="flex items-center space-x-1">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Running</span>
                </div>
              ) : (
                <div className="flex items-center space-x-1">
                  <Play className="w-4 h-4" />
                  <span>Run</span>
                </div>
              )}
            </button>
          </div>

          {/* Auto-complete suggestions */}
          {autoComplete.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded shadow-lg z-10">
              {autoComplete.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleAutoCompleteClick(suggestion)}
                  className="w-full text-left px-3 py-2 hover:bg-gray-100 text-sm font-mono"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Command categories */}
        <div className="mt-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Common Commands:</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(commandCategories).map(([category, commands]) => (
              <div key={category} className="space-y-1">
                <h5 className="text-xs font-medium text-gray-600 uppercase tracking-wide">{category}</h5>
                <div className="flex flex-wrap gap-1">
                  {commands.slice(0, 4).map((cmd) => (
                    <button
                      key={cmd}
                      onClick={() => setInputCommand(cmd)}
                      className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors font-mono"
                    >
                      {cmd}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Command History */}
      <div className="bg-white rounded-lg shadow border p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Clock className="w-6 h-6 text-purple-600" />
            <h3 className="text-lg font-semibold text-gray-900">Command History</h3>
          </div>
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="text-sm text-gray-600 hover:text-gray-800"
          >
            {showHistory ? 'Hide' : 'Show'}
          </button>
        </div>

        {showHistory && (
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {commandHistory.map((item) => (
              <div
                key={item.id}
                className="flex items-center justify-between p-2 bg-gray-50 rounded"
              >
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-mono text-gray-700">{item.command}</span>
                  <span className="text-xs text-gray-500">
                    {item.timestamp.toLocaleTimeString()}
                  </span>
                </div>
                <div className="flex items-center space-x-1">
                  {item.success ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-red-500" />
                  )}
                  <button
                    onClick={() => setInputCommand(item.command)}
                    className="text-xs text-blue-600 hover:text-blue-800"
                  >
                    Reuse
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Command Results */}
      <div className="bg-white rounded-lg shadow border p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Terminal className="w-6 h-6 text-green-600" />
            <h3 className="text-lg font-semibold text-gray-900">Command Results</h3>
          </div>
          <span className="text-sm text-gray-500">
            {currentResults.length} result{currentResults.length !== 1 ? 's' : ''}
          </span>
        </div>

        <div className="space-y-4">
          {currentResults.map((result) => (
            <div key={result.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  {getStatusIcon(result.status)}
                  <span className="font-mono text-sm text-gray-700">{result.command}</span>
                  {result.duration && (
                    <span className="text-xs text-gray-500">
                      {formatDuration(result.duration)}
                    </span>
                  )}
                </div>
                <div className="flex items-center space-x-1">
                  {result.output && (
                    <button
                      onClick={() => copyToClipboard(result.output)}
                      className="p-1 text-gray-500 hover:text-gray-700"
                      title="Copy output"
                    >
                      <Copy className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>

              {result.error && (
                <div className="mb-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-800">
                  <div className="flex items-center space-x-1">
                    <AlertTriangle className="w-4 h-4" />
                    <span>Error: {result.error}</span>
                  </div>
                </div>
              )}

              {result.output && (
                <div className="bg-gray-900 text-green-400 p-3 rounded font-mono text-sm overflow-x-auto">
                  <pre>{result.output}</pre>
                </div>
              )}
            </div>
          ))}

          {currentResults.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <Terminal className="w-12 h-12 mx-auto mb-2 text-gray-300" />
              <p>No commands executed yet</p>
              <p className="text-sm">Enter a command above to see results</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default CommandProcessor 