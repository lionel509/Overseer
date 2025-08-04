import React, { useState, useEffect } from 'react'
import { useAppDispatch, useAppSelector } from '../store/hooks'
import { executePythonCommand } from '../store/pythonSlice'
import { 
  Lightbulb, 
  Tool, 
  TrendingUp, 
  Clock, 
  Star,
  Zap,
  Settings,
  Activity,
  HardDrive,
  Memory,
  Cpu,
  Network,
  AlertTriangle,
  CheckCircle,
  Info,
  Play,
  Stop,
  RefreshCw
} from 'lucide-react'

interface ToolRecommendation {
  id: string
  name: string
  description: string
  category: string
  priority: 'high' | 'medium' | 'low'
  reason: string
  action: string
  icon: string
  usageCount: number
  lastUsed?: Date
  isRecommended: boolean
}

interface SystemContext {
  cpuUsage: number
  memoryUsage: number
  diskUsage: number
  networkActivity: boolean
  activeProcesses: number
  recentCommands: string[]
  currentDirectory: string
  timeOfDay: string
}

const ToolRecommender: React.FC = () => {
  const dispatch = useAppDispatch()
  const { isConnected } = useAppSelector(state => state.python)
  const [recommendations, setRecommendations] = useState<ToolRecommendation[]>([])
  const [systemContext, setSystemContext] = useState<SystemContext | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [showUsedTools, setShowUsedTools] = useState(false)

  // Available tools database
  const availableTools = [
    {
      id: 'system_monitor',
      name: 'System Monitor',
      description: 'Real-time system performance monitoring',
      category: 'monitoring',
      action: 'start_monitoring',
      icon: 'Activity'
    },
    {
      id: 'file_search',
      name: 'File Search',
      description: 'Advanced file search and management',
      category: 'files',
      action: 'file_search',
      icon: 'Search'
    },
    {
      id: 'process_manager',
      name: 'Process Manager',
      description: 'View and manage running processes',
      category: 'system',
      action: 'process_list',
      icon: 'Cpu'
    },
    {
      id: 'network_monitor',
      name: 'Network Monitor',
      description: 'Monitor network activity and connections',
      category: 'monitoring',
      action: 'network_status',
      icon: 'Network'
    },
    {
      id: 'disk_analyzer',
      name: 'Disk Analyzer',
      description: 'Analyze disk usage and storage',
      category: 'system',
      action: 'disk_usage',
      icon: 'HardDrive'
    },
    {
      id: 'memory_analyzer',
      name: 'Memory Analyzer',
      description: 'Analyze memory usage and performance',
      category: 'system',
      action: 'memory_usage',
      icon: 'Memory'
    },
    {
      id: 'command_history',
      name: 'Command History',
      description: 'View and reuse previous commands',
      category: 'productivity',
      action: 'command_history',
      icon: 'Clock'
    },
    {
      id: 'quick_actions',
      name: 'Quick Actions',
      description: 'Common system operations',
      category: 'productivity',
      action: 'quick_actions',
      icon: 'Zap'
    }
  ]

  useEffect(() => {
    if (isConnected) {
      loadSystemContext()
      generateRecommendations()
    }
  }, [isConnected])

  const loadSystemContext = async () => {
    try {
      setIsLoading(true)
      
      // Get system metrics
      const [cpuResult, memoryResult, diskResult, networkResult, processResult] = await Promise.all([
        dispatch(executePythonCommand({ command: 'get_metrics' })),
        dispatch(executePythonCommand({ command: 'memory_usage' })),
        dispatch(executePythonCommand({ command: 'disk_usage' })),
        dispatch(executePythonCommand({ command: 'network_status' })),
        dispatch(executePythonCommand({ command: 'process_list' }))
      ])

      const context: SystemContext = {
        cpuUsage: cpuResult.payload?.data?.cpu_percent || 0,
        memoryUsage: memoryResult.payload?.data?.percent || 0,
        diskUsage: diskResult.payload?.data?.[0]?.percent || 0,
        networkActivity: networkResult.payload?.data?.io_counters?.bytes_sent > 0,
        activeProcesses: processResult.payload?.data?.length || 0,
        recentCommands: [], // This would be populated from command history
        currentDirectory: '/',
        timeOfDay: new Date().getHours() < 12 ? 'morning' : new Date().getHours() < 18 ? 'afternoon' : 'evening'
      }

      setSystemContext(context)
    } catch (error) {
      console.error('Failed to load system context:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const generateRecommendations = () => {
    if (!systemContext) return

    const newRecommendations: ToolRecommendation[] = []

    // High CPU usage recommendations
    if (systemContext.cpuUsage > 80) {
      newRecommendations.push({
        ...availableTools.find(t => t.id === 'process_manager')!,
        priority: 'high',
        reason: `High CPU usage detected (${systemContext.cpuUsage.toFixed(1)}%)`,
        usageCount: 0,
        isRecommended: true
      })
    }

    // High memory usage recommendations
    if (systemContext.memoryUsage > 85) {
      newRecommendations.push({
        ...availableTools.find(t => t.id === 'memory_analyzer')!,
        priority: 'high',
        reason: `High memory usage detected (${systemContext.memoryUsage.toFixed(1)}%)`,
        usageCount: 0,
        isRecommended: true
      })
    }

    // High disk usage recommendations
    if (systemContext.diskUsage > 90) {
      newRecommendations.push({
        ...availableTools.find(t => t.id === 'disk_analyzer')!,
        priority: 'high',
        reason: `High disk usage detected (${systemContext.diskUsage.toFixed(1)}%)`,
        usageCount: 0,
        isRecommended: true
      })
    }

    // Network activity recommendations
    if (systemContext.networkActivity) {
      newRecommendations.push({
        ...availableTools.find(t => t.id === 'network_monitor')!,
        priority: 'medium',
        reason: 'Network activity detected',
        usageCount: 0,
        isRecommended: true
      })
    }

    // Time-based recommendations
    if (systemContext.timeOfDay === 'morning') {
      newRecommendations.push({
        ...availableTools.find(t => t.id === 'system_monitor')!,
        priority: 'medium',
        reason: 'Good morning! Start your day with system monitoring',
        usageCount: 0,
        isRecommended: true
      })
    }

    // Always recommend some productivity tools
    newRecommendations.push({
      ...availableTools.find(t => t.id === 'quick_actions')!,
      priority: 'low',
      reason: 'Common system operations',
      usageCount: 0,
      isRecommended: true
    })

    // Add all available tools as non-recommended
    availableTools.forEach(tool => {
      if (!newRecommendations.find(r => r.id === tool.id)) {
        newRecommendations.push({
          ...tool,
          priority: 'low',
          reason: 'Available tool',
          usageCount: 0,
          isRecommended: false
        })
      }
    })

    setRecommendations(newRecommendations)
  }

  const handleToolAction = async (tool: ToolRecommendation) => {
    try {
      // Execute the tool's action
      const response = await dispatch(executePythonCommand({
        command: tool.action,
        args: []
      }))

      if (response.payload?.success) {
        // Update usage count and last used
        setRecommendations(prev => prev.map(r => 
          r.id === tool.id 
            ? { ...r, usageCount: r.usageCount + 1, lastUsed: new Date() }
            : r
        ))
      }
    } catch (error) {
      console.error('Tool action failed:', error)
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-50 border-red-200'
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'low': return 'text-green-600 bg-green-50 border-green-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high': return <AlertTriangle className="w-4 h-4" />
      case 'medium': return <Info className="w-4 h-4" />
      case 'low': return <CheckCircle className="w-4 h-4" />
      default: return <Info className="w-4 h-4" />
    }
  }

  const getToolIcon = (iconName: string) => {
    const iconMap: Record<string, React.ReactNode> = {
      'Activity': <Activity className="w-5 h-5" />,
      'Search': <Tool className="w-5 h-5" />,
      'Cpu': <Cpu className="w-5 h-5" />,
      'Network': <Network className="w-5 h-5" />,
      'HardDrive': <HardDrive className="w-5 h-5" />,
      'Memory': <Memory className="w-5 h-5" />,
      'Clock': <Clock className="w-5 h-5" />,
      'Zap': <Zap className="w-5 h-5" />
    }
    return iconMap[iconName] || <Tool className="w-5 h-5" />
  }

  const filteredRecommendations = recommendations.filter(tool => {
    if (selectedCategory !== 'all' && tool.category !== selectedCategory) return false
    if (!showUsedTools && tool.usageCount > 0) return false
    return true
  })

  const categories = ['all', 'monitoring', 'system', 'files', 'productivity']

  if (!isConnected) {
    return (
      <div className="p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-yellow-600" />
            <span className="text-yellow-800">Python backend not connected</span>
          </div>
          <p className="text-yellow-700 mt-2">
            Connect to the Python backend to use tool recommendations.
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
          <h1 className="text-3xl font-bold text-gray-900">Tool Recommender</h1>
          <p className="text-gray-600">Smart tool suggestions based on system context</p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={loadSystemContext}
            disabled={isLoading}
            className="flex items-center space-x-1 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* System Context */}
      {systemContext && (
        <div className="bg-white rounded-lg shadow border p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Info className="w-6 h-6 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">System Context</h3>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="flex items-center space-x-2">
              <Cpu className="w-4 h-4 text-blue-600" />
              <span className="text-sm text-gray-600">CPU:</span>
              <span className={`text-sm font-medium ${
                systemContext.cpuUsage > 80 ? 'text-red-600' : 
                systemContext.cpuUsage > 60 ? 'text-yellow-600' : 'text-green-600'
              }`}>
                {systemContext.cpuUsage.toFixed(1)}%
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <Memory className="w-4 h-4 text-green-600" />
              <span className="text-sm text-gray-600">Memory:</span>
              <span className={`text-sm font-medium ${
                systemContext.memoryUsage > 85 ? 'text-red-600' : 
                systemContext.memoryUsage > 70 ? 'text-yellow-600' : 'text-green-600'
              }`}>
                {systemContext.memoryUsage.toFixed(1)}%
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <HardDrive className="w-4 h-4 text-purple-600" />
              <span className="text-sm text-gray-600">Disk:</span>
              <span className={`text-sm font-medium ${
                systemContext.diskUsage > 90 ? 'text-red-600' : 
                systemContext.diskUsage > 80 ? 'text-yellow-600' : 'text-green-600'
              }`}>
                {systemContext.diskUsage.toFixed(1)}%
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-orange-600" />
              <span className="text-sm text-gray-600">Processes:</span>
              <span className="text-sm font-medium text-gray-800">
                {systemContext.activeProcesses}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow border p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Settings className="w-6 h-6 text-purple-600" />
            <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          {/* Category filter */}
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">Category:</span>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {categories.map(category => (
                <option key={category} value={category}>
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {/* Show used tools toggle */}
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={showUsedTools}
              onChange={(e) => setShowUsedTools(e.target.checked)}
              className="rounded"
            />
            <span className="text-sm text-gray-600">Show used tools</span>
          </label>
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-white rounded-lg shadow border p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Lightbulb className="w-6 h-6 text-yellow-600" />
            <h3 className="text-lg font-semibold text-gray-900">Tool Recommendations</h3>
          </div>
          <span className="text-sm text-gray-500">
            {filteredRecommendations.length} tools
          </span>
        </div>

        <div className="space-y-4">
          {filteredRecommendations.map((tool) => (
            <div
              key={tool.id}
              className={`p-4 border rounded-lg transition-colors ${
                tool.isRecommended 
                  ? 'border-blue-200 bg-blue-50' 
                  : 'border-gray-200 bg-gray-50'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <div className="flex items-center justify-center w-10 h-10 bg-white rounded-lg shadow-sm">
                    {getToolIcon(tool.icon)}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <h4 className="font-semibold text-gray-900">{tool.name}</h4>
                      {tool.isRecommended && (
                        <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                          Recommended
                        </span>
                      )}
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-2">{tool.description}</p>
                    
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <span className="capitalize">{tool.category}</span>
                      {tool.usageCount > 0 && (
                        <span>Used {tool.usageCount} times</span>
                      )}
                      {tool.lastUsed && (
                        <span>Last used: {tool.lastUsed.toLocaleDateString()}</span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  {/* Priority indicator */}
                  <div className={`flex items-center space-x-1 px-2 py-1 rounded text-xs border ${getPriorityColor(tool.priority)}`}>
                    {getPriorityIcon(tool.priority)}
                    <span className="capitalize">{tool.priority}</span>
                  </div>

                  {/* Action button */}
                  <button
                    onClick={() => handleToolAction(tool)}
                    className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                  >
                    <Play className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Reason */}
              <div className="mt-3 pt-3 border-t border-gray-200">
                <div className="flex items-center space-x-2">
                  <Lightbulb className="w-4 h-4 text-yellow-500" />
                  <span className="text-sm text-gray-600">{tool.reason}</span>
                </div>
              </div>
            </div>
          ))}

          {filteredRecommendations.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <Lightbulb className="w-12 h-12 mx-auto mb-2 text-gray-300" />
              <p>No tools match your current filters</p>
              <p className="text-sm">Try adjusting the category or show used tools</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ToolRecommender 