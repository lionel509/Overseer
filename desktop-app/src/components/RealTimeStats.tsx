import React, { useState, useEffect, useRef } from 'react'
import { useAppDispatch, useAppSelector } from '../store/hooks'
import { executePythonCommand } from '../store/pythonSlice'
import { 
  Activity, 
  Cpu, 
  Memory, 
  HardDrive, 
  Network, 
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Clock,
  RefreshCw,
  Play,
  Pause,
  Settings,
  BarChart3,
  LineChart,
  PieChart
} from 'lucide-react'

interface SystemStats {
  timestamp: Date
  cpu: {
    usage: number
    cores: number
    temperature?: number
    frequency?: number
  }
  memory: {
    total: number
    used: number
    available: number
    percent: number
    swap?: {
      total: number
      used: number
      percent: number
    }
  }
  disk: {
    total: number
    used: number
    free: number
    percent: number
    readBytes: number
    writeBytes: number
  }
  network: {
    bytesSent: number
    bytesRecv: number
    packetsSent: number
    packetsRecv: number
    connections: number
  }
  processes: {
    total: number
    running: number
    sleeping: number
    stopped: number
    zombie: number
  }
  loadAverage: {
    oneMin: number
    fiveMin: number
    fifteenMin: number
  }
}

interface ChartData {
  labels: string[]
  datasets: {
    label: string
    data: number[]
    borderColor: string
    backgroundColor: string
    tension: number
  }[]
}

const RealTimeStats: React.FC = () => {
  const dispatch = useAppDispatch()
  const { isConnected } = useAppSelector(state => state.python)
  const [stats, setStats] = useState<SystemStats[]>([])
  const [isMonitoring, setIsMonitoring] = useState(false)
  const [updateInterval, setUpdateInterval] = useState(2000) // 2 seconds
  const [maxDataPoints, setMaxDataPoints] = useState(50)
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(['cpu', 'memory', 'disk'])
  const [showCharts, setShowCharts] = useState(true)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  const metrics = [
    { id: 'cpu', name: 'CPU Usage', icon: Cpu, color: 'text-blue-600' },
    { id: 'memory', name: 'Memory Usage', icon: Memory, color: 'text-green-600' },
    { id: 'disk', name: 'Disk Usage', icon: HardDrive, color: 'text-purple-600' },
    { id: 'network', name: 'Network Activity', icon: Network, color: 'text-orange-600' },
    { id: 'processes', name: 'Processes', icon: Activity, color: 'text-red-600' }
  ]

  useEffect(() => {
    if (isMonitoring && isConnected) {
      startMonitoring()
    } else {
      stopMonitoring()
    }

    return () => stopMonitoring()
  }, [isMonitoring, isConnected, updateInterval])

  const startMonitoring = () => {
    stopMonitoring()
    fetchStats()
    intervalRef.current = setInterval(fetchStats, updateInterval)
  }

  const stopMonitoring = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }

  const fetchStats = async () => {
    if (!isConnected) return

    try {
      const [cpuResult, memoryResult, diskResult, networkResult, processResult] = await Promise.all([
        dispatch(executePythonCommand({ command: 'get_metrics' })),
        dispatch(executePythonCommand({ command: 'memory_usage' })),
        dispatch(executePythonCommand({ command: 'disk_usage' })),
        dispatch(executePythonCommand({ command: 'network_status' })),
        dispatch(executePythonCommand({ command: 'process_list' }))
      ])

      const newStats: SystemStats = {
        timestamp: new Date(),
        cpu: {
          usage: cpuResult.payload?.data?.cpu_percent || 0,
          cores: 12, // This could be dynamic
          temperature: cpuResult.payload?.data?.temperature,
          frequency: cpuResult.payload?.data?.frequency
        },
        memory: {
          total: memoryResult.payload?.data?.total || 0,
          used: memoryResult.payload?.data?.used || 0,
          available: memoryResult.payload?.data?.available || 0,
          percent: memoryResult.payload?.data?.percent || 0,
          swap: memoryResult.payload?.data?.swap
        },
        disk: {
          total: diskResult.payload?.data?.[0]?.total || 0,
          used: diskResult.payload?.data?.[0]?.used || 0,
          free: diskResult.payload?.data?.[0]?.free || 0,
          percent: diskResult.payload?.data?.[0]?.percent || 0,
          readBytes: diskResult.payload?.data?.[0]?.read_bytes || 0,
          writeBytes: diskResult.payload?.data?.[0]?.write_bytes || 0
        },
        network: {
          bytesSent: networkResult.payload?.data?.io_counters?.bytes_sent || 0,
          bytesRecv: networkResult.payload?.data?.io_counters?.bytes_recv || 0,
          packetsSent: networkResult.payload?.data?.io_counters?.packets_sent || 0,
          packetsRecv: networkResult.payload?.data?.io_counters?.packets_recv || 0,
          connections: networkResult.payload?.data?.connections?.length || 0
        },
        processes: {
          total: processResult.payload?.data?.length || 0,
          running: processResult.payload?.data?.filter((p: any) => p.status === 'running')?.length || 0,
          sleeping: processResult.payload?.data?.filter((p: any) => p.status === 'sleeping')?.length || 0,
          stopped: processResult.payload?.data?.filter((p: any) => p.status === 'stopped')?.length || 0,
          zombie: processResult.payload?.data?.filter((p: any) => p.status === 'zombie')?.length || 0
        },
        loadAverage: {
          oneMin: 0, // This would need additional implementation
          fiveMin: 0,
          fifteenMin: 0
        }
      }

      setStats(prev => {
        const newStatsArray = [...prev, newStats]
        return newStatsArray.slice(-maxDataPoints)
      })
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    }
  }

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatTime = (date: Date): string => {
    return date.toLocaleTimeString()
  }

  const getStatusColor = (value: number, thresholds: { warning: number; critical: number }): string => {
    if (value >= thresholds.critical) return 'text-red-600'
    if (value >= thresholds.warning) return 'text-yellow-600'
    return 'text-green-600'
  }

  const getTrendIcon = (current: number, previous: number) => {
    if (current > previous) return <TrendingUp className="w-4 h-4 text-red-500" />
    if (current < previous) return <TrendingDown className="w-4 h-4 text-green-500" />
    return <div className="w-4 h-4" />
  }

  const getChartData = (metric: string): ChartData => {
    const labels = stats.map(s => formatTime(s.timestamp))
    const data = stats.map(s => {
      switch (metric) {
        case 'cpu': return s.cpu.usage
        case 'memory': return s.memory.percent
        case 'disk': return s.disk.percent
        case 'network': return (s.network.bytesSent + s.network.bytesRecv) / 1024 / 1024 // MB
        case 'processes': return s.processes.total
        default: return 0
      }
    })

    const colors = {
      cpu: { border: '#3B82F6', background: 'rgba(59, 130, 246, 0.1)' },
      memory: { border: '#10B981', background: 'rgba(16, 185, 129, 0.1)' },
      disk: { border: '#8B5CF6', background: 'rgba(139, 92, 246, 0.1)' },
      network: { border: '#F59E0B', background: 'rgba(245, 158, 11, 0.1)' },
      processes: { border: '#EF4444', background: 'rgba(239, 68, 68, 0.1)' }
    }

    return {
      labels,
      datasets: [{
        label: metrics.find(m => m.id === metric)?.name || metric,
        data,
        borderColor: colors[metric as keyof typeof colors]?.border || '#6B7280',
        backgroundColor: colors[metric as keyof typeof colors]?.background || 'rgba(107, 114, 128, 0.1)',
        tension: 0.4
      }]
    }
  }

  const clearStats = () => {
    setStats([])
  }

  const toggleMonitoring = () => {
    setIsMonitoring(!isMonitoring)
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
            Connect to the Python backend to view real-time system stats.
          </p>
        </div>
      </div>
    )
  }

  const currentStats = stats[stats.length - 1]
  const previousStats = stats[stats.length - 2]

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Real-Time System Stats</h1>
          <p className="text-gray-600">Live system performance monitoring and analytics</p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={toggleMonitoring}
            className={`flex items-center space-x-1 px-3 py-1 text-sm rounded transition-colors ${
              isMonitoring 
                ? 'bg-red-600 text-white hover:bg-red-700' 
                : 'bg-green-600 text-white hover:bg-green-700'
            }`}
          >
            {isMonitoring ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            <span>{isMonitoring ? 'Stop' : 'Start'} Monitoring</span>
          </button>
          <button
            onClick={clearStats}
            className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
          >
            Clear
          </button>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow border p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Settings className="w-6 h-6 text-purple-600" />
            <h3 className="text-lg font-semibold text-gray-900">Monitoring Controls</h3>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Update interval */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Update Interval</label>
            <select
              value={updateInterval}
              onChange={(e) => setUpdateInterval(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={1000}>1 second</option>
              <option value={2000}>2 seconds</option>
              <option value={5000}>5 seconds</option>
              <option value={10000}>10 seconds</option>
            </select>
          </div>

          {/* Max data points */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Max Data Points</label>
            <select
              value={maxDataPoints}
              onChange={(e) => setMaxDataPoints(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={25}>25 points</option>
              <option value={50}>50 points</option>
              <option value={100}>100 points</option>
              <option value={200}>200 points</option>
            </select>
          </div>

          {/* Show charts toggle */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Display Options</label>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={showCharts}
                onChange={(e) => setShowCharts(e.target.checked)}
                className="rounded"
              />
              <span className="text-sm text-gray-600">Show charts</span>
            </label>
          </div>
        </div>
      </div>

      {/* Current Stats */}
      {currentStats && (
        <div className="bg-white rounded-lg shadow border p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Activity className="w-6 h-6 text-blue-600" />
              <h3 className="text-lg font-semibold text-gray-900">Current System Stats</h3>
            </div>
            <span className="text-sm text-gray-500">
              Last updated: {formatTime(currentStats.timestamp)}
            </span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* CPU */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <Cpu className="w-5 h-5 text-blue-600" />
                  <span className="font-semibold text-gray-900">CPU</span>
                </div>
                {previousStats && getTrendIcon(currentStats.cpu.usage, previousStats.cpu.usage)}
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Usage:</span>
                  <span className={getStatusColor(currentStats.cpu.usage, { warning: 60, critical: 80 })}>
                    {currentStats.cpu.usage.toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-300 ${
                      currentStats.cpu.usage >= 80 ? 'bg-red-500' : 
                      currentStats.cpu.usage >= 60 ? 'bg-yellow-500' : 'bg-blue-500'
                    }`}
                    style={{ width: `${Math.min(currentStats.cpu.usage, 100)}%` }}
                  ></div>
                </div>
                <div className="text-xs text-gray-500">
                  {currentStats.cpu.cores} cores
                  {currentStats.cpu.temperature && ` • ${currentStats.cpu.temperature}°C`}
                </div>
              </div>
            </div>

            {/* Memory */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <Memory className="w-5 h-5 text-green-600" />
                  <span className="font-semibold text-gray-900">Memory</span>
                </div>
                {previousStats && getTrendIcon(currentStats.memory.percent, previousStats.memory.percent)}
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Usage:</span>
                  <span className={getStatusColor(currentStats.memory.percent, { warning: 70, critical: 85 })}>
                    {currentStats.memory.percent.toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-300 ${
                      currentStats.memory.percent >= 85 ? 'bg-red-500' : 
                      currentStats.memory.percent >= 70 ? 'bg-yellow-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${Math.min(currentStats.memory.percent, 100)}%` }}
                  ></div>
                </div>
                <div className="text-xs text-gray-500">
                  {formatBytes(currentStats.memory.used)} / {formatBytes(currentStats.memory.total)}
                </div>
              </div>
            </div>

            {/* Disk */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <HardDrive className="w-5 h-5 text-purple-600" />
                  <span className="font-semibold text-gray-900">Disk</span>
                </div>
                {previousStats && getTrendIcon(currentStats.disk.percent, previousStats.disk.percent)}
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Usage:</span>
                  <span className={getStatusColor(currentStats.disk.percent, { warning: 80, critical: 90 })}>
                    {currentStats.disk.percent.toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-300 ${
                      currentStats.disk.percent >= 90 ? 'bg-red-500' : 
                      currentStats.disk.percent >= 80 ? 'bg-yellow-500' : 'bg-purple-500'
                    }`}
                    style={{ width: `${Math.min(currentStats.disk.percent, 100)}%` }}
                  ></div>
                </div>
                <div className="text-xs text-gray-500">
                  {formatBytes(currentStats.disk.used)} / {formatBytes(currentStats.disk.total)}
                </div>
              </div>
            </div>

            {/* Network */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <Network className="w-5 h-5 text-orange-600" />
                  <span className="font-semibold text-gray-900">Network</span>
                </div>
                <Activity className="w-4 h-4 text-orange-500" />
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Sent:</span>
                  <span className="text-gray-800">{formatBytes(currentStats.network.bytesSent)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Received:</span>
                  <span className="text-gray-800">{formatBytes(currentStats.network.bytesRecv)}</span>
                </div>
                <div className="text-xs text-gray-500">
                  {currentStats.network.connections} connections
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Charts */}
      {showCharts && stats.length > 1 && (
        <div className="bg-white rounded-lg shadow border p-6">
          <div className="flex items-center space-x-2 mb-4">
            <BarChart3 className="w-6 h-6 text-indigo-600" />
            <h3 className="text-lg font-semibold text-gray-900">Performance Trends</h3>
          </div>
          
          <div className="space-y-6">
            {selectedMetrics.map(metric => {
              const chartData = getChartData(metric)
              const metricInfo = metrics.find(m => m.id === metric)
              
              return (
                <div key={metric} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-3">
                    {metricInfo?.icon && <metricInfo.icon className="w-5 h-5" />}
                    <h4 className="font-semibold text-gray-900">{metricInfo?.name}</h4>
                  </div>
                  
                  {/* Simple chart representation */}
                  <div className="h-32 bg-gray-50 rounded flex items-end space-x-1 p-2">
                    {chartData.datasets[0].data.map((value, index) => {
                      const maxValue = Math.max(...chartData.datasets[0].data)
                      const height = maxValue > 0 ? (value / maxValue) * 100 : 0
                      
                      return (
                        <div
                          key={index}
                          className="flex-1 bg-blue-500 rounded-t"
                          style={{ height: `${height}%` }}
                          title={`${formatTime(stats[index].timestamp)}: ${value.toFixed(1)}`}
                        />
                      )
                    })}
                  </div>
                  
                  <div className="mt-2 text-xs text-gray-500">
                    {stats.length} data points • {formatTime(stats[0].timestamp)} - {formatTime(stats[stats.length - 1].timestamp)}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Stats History */}
      {stats.length > 0 && (
        <div className="bg-white rounded-lg shadow border p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Clock className="w-6 h-6 text-gray-600" />
              <h3 className="text-lg font-semibold text-gray-900">Stats History</h3>
            </div>
            <span className="text-sm text-gray-500">
              {stats.length} data points
            </span>
          </div>
          
          <div className="max-h-64 overflow-y-auto">
            <div className="space-y-2">
              {stats.slice(-10).reverse().map((stat, index) => (
                <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded text-sm">
                  <span className="text-gray-600">{formatTime(stat.timestamp)}</span>
                  <div className="flex items-center space-x-4">
                    <span className="text-blue-600">CPU: {stat.cpu.usage.toFixed(1)}%</span>
                    <span className="text-green-600">Mem: {stat.memory.percent.toFixed(1)}%</span>
                    <span className="text-purple-600">Disk: {stat.disk.percent.toFixed(1)}%</span>
                    <span className="text-orange-600">Proc: {stat.processes.total}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default RealTimeStats 