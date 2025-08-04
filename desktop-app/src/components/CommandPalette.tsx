import React, { useEffect, useRef, useState } from 'react'
import { useAppDispatch, useAppSelector } from '../store/hooks'
import {
  openCommandPalette,
  closeCommandPalette,
  setSearchQuery,
  selectNext,
  selectPrevious,
  selectCommand,
  addRecentCommand
} from '../store/commandPaletteSlice'
import { executePythonCommand } from '../store/pythonSlice'
import { Search, Command, ArrowUp, ArrowDown, Enter, X } from 'lucide-react'

const CommandPalette: React.FC = () => {
  const dispatch = useAppDispatch()
  const {
    isOpen,
    searchQuery,
    selectedIndex,
    filteredCommands,
    recentCommands
  } = useAppSelector(state => state.commandPalette)
  
  const inputRef = useRef<HTMLInputElement>(null)
  const [isInitialized, setIsInitialized] = useState(false)

  // Initialize default commands
  useEffect(() => {
    if (!isInitialized) {
      initializeDefaultCommands()
      setIsInitialized(true)
    }
  }, [isInitialized])

  // Focus input when opened
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Cmd/Ctrl + K to open command palette
      if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
        event.preventDefault()
        dispatch(openCommandPalette())
      }

      // Escape to close command palette
      if (event.key === 'Escape' && isOpen) {
        event.preventDefault()
        dispatch(closeCommandPalette())
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [dispatch, isOpen])

  const initializeDefaultCommands = () => {
    const defaultCommands = [
      {
        id: 'system-info',
        title: 'System Information',
        description: 'Get detailed system information',
        category: 'System',
        keywords: ['system', 'info', 'details', 'platform'],
        action: async () => {
          const result = await dispatch(executePythonCommand({ 
            command: 'system_info' 
          }))
          console.log('System info:', result)
        }
      },
      {
        id: 'file-search',
        title: 'Search Files',
        description: 'Search for files in the system',
        category: 'Files',
        keywords: ['search', 'files', 'find', 'locate'],
        action: async () => {
          const result = await dispatch(executePythonCommand({ 
            command: 'file_search',
            args: [searchQuery]
          }))
          console.log('File search:', result)
        }
      },
      {
        id: 'process-list',
        title: 'List Processes',
        description: 'Show running processes',
        category: 'System',
        keywords: ['process', 'list', 'running', 'tasks'],
        action: async () => {
          const result = await dispatch(executePythonCommand({ 
            command: 'process_list' 
          }))
          console.log('Process list:', result)
        }
      },
      {
        id: 'network-status',
        title: 'Network Status',
        description: 'Check network connectivity and status',
        category: 'Network',
        keywords: ['network', 'connectivity', 'status', 'ping'],
        action: async () => {
          const result = await dispatch(executePythonCommand({ 
            command: 'network_status' 
          }))
          console.log('Network status:', result)
        }
      },
      {
        id: 'disk-usage',
        title: 'Disk Usage',
        description: 'Show disk usage information',
        category: 'System',
        keywords: ['disk', 'usage', 'storage', 'space'],
        action: async () => {
          const result = await dispatch(executePythonCommand({ 
            command: 'disk_usage' 
          }))
          console.log('Disk usage:', result)
        }
      },
      {
        id: 'memory-usage',
        title: 'Memory Usage',
        description: 'Show memory usage information',
        category: 'System',
        keywords: ['memory', 'ram', 'usage', 'stats'],
        action: async () => {
          const result = await dispatch(executePythonCommand({ 
            command: 'memory_usage' 
          }))
          console.log('Memory usage:', result)
        }
      },
      {
        id: 'open-terminal',
        title: 'Open Terminal',
        description: 'Open system terminal',
        category: 'System',
        keywords: ['terminal', 'console', 'shell', 'open'],
        action: async () => {
          const result = await dispatch(executePythonCommand({ 
            command: 'open_terminal' 
          }))
          console.log('Open terminal:', result)
        }
      },
      {
        id: 'settings',
        title: 'Open Settings',
        description: 'Open application settings',
        category: 'Application',
        keywords: ['settings', 'preferences', 'config', 'options'],
        action: () => {
          // Navigate to settings
          console.log('Opening settings...')
        }
      }
    ]

    defaultCommands.forEach(command => {
      // Add command to store
      // Note: In a real implementation, you'd dispatch these to the store
      console.log('Adding command:', command.title)
    })
  }

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    dispatch(setSearchQuery(event.target.value))
  }

  const handleKeyDown = (event: React.KeyboardEvent) => {
    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault()
        dispatch(selectNext())
        break
      case 'ArrowUp':
        event.preventDefault()
        dispatch(selectPrevious())
        break
      case 'Enter':
        event.preventDefault()
        executeSelectedCommand()
        break
      case 'Escape':
        event.preventDefault()
        dispatch(closeCommandPalette())
        break
    }
  }

  const executeSelectedCommand = () => {
    const selectedCommand = filteredCommands[selectedIndex]
    if (selectedCommand) {
      dispatch(addRecentCommand(selectedCommand.id))
      selectedCommand.action()
      dispatch(closeCommandPalette())
    }
  }

  const handleCommandClick = (index: number) => {
    dispatch(selectCommand(index))
    executeSelectedCommand()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="w-full max-w-2xl mx-4 bg-white rounded-lg shadow-2xl border border-gray-200">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <Search className="w-5 h-5 text-gray-400" />
            <input
              ref={inputRef}
              type="text"
              placeholder="Search commands..."
              value={searchQuery}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              className="flex-1 text-lg outline-none placeholder-gray-400"
            />
          </div>
          <button
            onClick={() => dispatch(closeCommandPalette())}
            className="p-1 hover:bg-gray-100 rounded"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Command List */}
        <div className="max-h-96 overflow-y-auto">
          {filteredCommands.length === 0 ? (
            <div className="p-4 text-center text-gray-500">
              No commands found
            </div>
          ) : (
            <div className="py-2">
              {filteredCommands.map((command, index) => (
                <div
                  key={command.id}
                  className={`flex items-center px-4 py-3 cursor-pointer hover:bg-gray-50 ${
                    index === selectedIndex ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                  }`}
                  onClick={() => handleCommandClick(index)}
                >
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <Command className="w-4 h-4 text-gray-400" />
                      <span className="font-medium text-gray-900">
                        {command.title}
                      </span>
                      {command.shortcut && (
                        <span className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">
                          {command.shortcut}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      {command.description}
                    </p>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">
                        {command.category}
                      </span>
                      {recentCommands.includes(command.id) && (
                        <span className="text-xs text-blue-600 bg-blue-100 px-2 py-1 rounded">
                          Recent
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-1 text-gray-400">
                    {index === selectedIndex && (
                      <>
                        <ArrowUp className="w-4 h-4" />
                        <ArrowDown className="w-4 h-4" />
                        <Enter className="w-4 h-4" />
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-4 border-t border-gray-200 text-sm text-gray-500">
          <div className="flex items-center space-x-4">
            <span>Use ↑↓ to navigate</span>
            <span>Enter to select</span>
            <span>Esc to close</span>
          </div>
          <div>
            {filteredCommands.length} command{filteredCommands.length !== 1 ? 's' : ''}
          </div>
        </div>
      </div>
    </div>
  )
}

export default CommandPalette 