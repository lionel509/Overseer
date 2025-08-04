import React, { useEffect, useState } from 'react'
import { useAppDispatch, useAppSelector } from '../store/hooks'
import { executePythonCommand } from '../store/pythonSlice'
import { 
  Activity, 
  Cpu, 
  HardDrive, 
  Memory, 
  Network, 
  Thermometer,
  Clock,
  TrendingUp,
  AlertTriangle,
  CheckCircle
} from 'lucide-react'

interface SystemMetrics {
  cpu: {
    usage: number
    cores: number
    temperature?: number
  }
  memory: {
    total: number
    used: number
    available: number
    percent: number
  }
  disk: {
    total: number
    used: number
    free: number
    percent: number
  }
  network: {
    bytes_sent: number
    bytes_recv: number
    packets_sent: number
    packets_recv: number
  }
  processes: {
    total: number
    running: number
  }
  uptime: number
}

const SystemDashboard: React.FC = () => {
  const dispatch = useAppDispatch()
  const { isRunning, isConnected } = useAppSelector(state => state.python)
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Update metrics every 5 seconds
  useEffect(() => {
    const updateMetrics = async () => {
      if (!isConnected) return

      setIsLoading(true)
      setError(null)

      try {
        const [cpuResult, memoryResult, diskResult, networkResult, processResult] = await Promise.all([
          dispatch(executePythonCommand({ command: 'get_metrics' })),
          dispatch(executePythonCommand({ command: 'memory_usage' })),
          dispatch(executePythonCommand({ command: 'disk_usage' })),
          dispatch(executePythonCommand({ command: 'network_status' })),
          dispatch(executePythonCommand({ command: 'process_list' }))
        ])

        if (cpuResult.payload?.success && memoryResult.payload?.success) {
          const newMetrics: SystemMetrics = {
            cpu: {
              usage: cpuResult.payload.data?.cpu_percent || 0,
              cores: 12, // This could be dynamic
              temperature: cpuResult.payload.data?.temperature
            },
            memory: {
              total: memoryResult.payload.data?.total || 0,
              used: memoryResult.payload.data?.used || 0,
              available: memoryResult.payload.data?.available || 0,
              percent: memoryResult.payload.data?.percent || 0
            },
            disk: {
              total: diskResult.payload.data?.[0]?.total || 0,
              used: diskResult.payload.data?.[0]?.used || 0,
              free: diskResult.payload.data?.[0]?.free || 0,
              percent: diskResult.payload.data?.[0]?.percent || 0
            },
            network: {
              bytes_sent: networkResult.payload.data?.io_counters?.bytes_sent || 0,
              bytes_recv: networkResult.payload.data?.io_counters?.bytes_recv || 0,
              packets_sent: networkResult.payload.data?.io_counters?.packets_sent || 0,
              packets_recv: networkResult.payload.data?.io_counters?.packets_recv || 0
            },
            processes: {
              total: processResult.payload.data?.length || 0,
              running: processResult.payload.data?.filter((p: any) => p.status === 'running')?.length || 0
            },
            uptime: Date.now() // This could be more sophisticated
          }
          setMetrics(newMetrics)
          setLastUpdate(new Date())
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to update metrics')
      } finally {
        setIsLoading(false)
      }
    }

    // Initial load
    updateMetrics()

    // Set up interval
    const interval = setInterval(updateMetrics, 5000)

    return () => clearInterval(interval)
  }, [dispatch, isConnected])

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatUptime = (ms: number): string => {
    const seconds = Math.floor(ms / 1000)
    const minutes = Math.floor(seconds / 60)
    const hours = Math.floor(minutes / 60)
    const days = Math.floor(hours / 24)
    
    if (days > 0) return `${days}d ${hours % 24}h`
    if (hours > 0) return `${hours}h ${minutes % 60}m`
    if (minutes > 0) return `${minutes}m ${seconds % 60}s`
    return `${seconds}s`
  }

  const getStatusColor = (percent: number): string => {
    if (percent < 50) return 'text-green-600'
    if (percent < 80) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getStatusIcon = (percent: number) => {
    if (percent < 50) return <CheckCircle className="w-4 h-4 text-green-600" />
    if (percent < 80) return <AlertTriangle className="w-4 h-4 text-yellow-600" />
    return <AlertTriangle className="w-4 h-4 text-red-600" />
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
            Connect to the Python backend to view system metrics.
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
          <h1 className="text-3xl font-bold text-gray-900">System Dashboard</h1>
          <p className="text-gray-600">Real-time system monitoring and metrics</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-sm text-gray-600">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          <div className="text-sm text-gray-500">
            Last update: {lastUpdate.toLocaleTimeString()}
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <span className="text-red-800">Error: {error}</span>
          </div>
        </div>
      )}

      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Updating metrics...</span>
        </div>
      )}

      {metrics && (
        <>
          {/* CPU and Memory Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* CPU Card */}
            <div className="bg-white rounded-lg shadow border p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <Cpu className="w-6 h-6 text-blue-600" />
                  <h3 className="text-lg font-semibold text-gray-900">CPU Usage</h3>
                </div>
                {getStatusIcon(metrics.cpu.usage)}
              </div>
              
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>Usage</span>
                    <span className={getStatusColor(metrics.cpu.usage)}>
                      {metrics.cpu.usage.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-300 ${
                        metrics.cpu.usage < 50 ? 'bg-green-500' : 
                        metrics.cpu.usage < 80 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${metrics.cpu.usage}%` }}
                    ></div>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Cores:</span>
                    <span className="ml-2 font-medium">{metrics.cpu.cores}</span>
                  </div>
                  {metrics.cpu.temperature && (
                    <div>
                      <span className="text-gray-600">Temperature:</span>
                      <span className="ml-2 font-medium">{metrics.cpu.temperature}°C</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Memory Card */}
            <div className="bg-white rounded-lg shadow border p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <Memory className="w-6 h-6 text-green-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Memory Usage</h3>
                </div>
                {getStatusIcon(metrics.memory.percent)}
              </div>
              
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>Usage</span>
                    <span className={getStatusColor(metrics.memory.percent)}>
                      {metrics.memory.percent.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-300 ${
                        metrics.memory.percent < 50 ? 'bg-green-500' : 
                        metrics.memory.percent < 80 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${metrics.memory.percent}%` }}
                    ></div>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Used:</span>
                    <span className="ml-2 font-medium">{formatBytes(metrics.memory.used)}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Total:</span>
                    <span className="ml-2 font-medium">{formatBytes(metrics.memory.total)}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Disk and Network Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Disk Card */}
            <div className="bg-white rounded-lg shadow border p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <HardDrive className="w-6 h-6 text-purple-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Disk Usage</h3>
                </div>
                {getStatusIcon(metrics.disk.percent)}
              </div>
              
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>Usage</span>
                    <span className={getStatusColor(metrics.disk.percent)}>
                      {metrics.disk.percent.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-300 ${
                        metrics.disk.percent < 50 ? 'bg-green-500' : 
                        metrics.disk.percent < 80 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${metrics.disk.percent}%` }}
                    ></div>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Used:</span>
                    <span className="ml-2 font-medium">{formatBytes(metrics.disk.used)}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Free:</span>
                    <span className="ml-2 font-medium">{formatBytes(metrics.disk.free)}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Network Card */}
            <div className="bg-white rounded-lg shadow border p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <Network className="w-6 h-6 text-indigo-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Network Activity</h3>
                </div>
                <TrendingUp className="w-5 h-5 text-indigo-600" />
              </div>
              
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Sent:</span>
                    <span className="ml-2 font-medium">{formatBytes(metrics.network.bytes_sent)}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Received:</span>
                    <span className="ml-2 font-medium">{formatBytes(metrics.network.bytes_recv)}</span>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Packets Sent:</span>
                    <span className="ml-2 font-medium">{metrics.network.packets_sent.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Packets Recv:</span>
                    <span className="ml-2 font-medium">{metrics.network.packets_recv.toLocaleString()}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* System Info Row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Processes Card */}
            <div className="bg-white rounded-lg shadow border p-6">
              <div className="flex items-center space-x-2 mb-4">
                <Activity className="w-6 h-6 text-orange-600" />
                <h3 className="text-lg font-semibold text-gray-900">Processes</h3>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Total:</span>
                  <span className="font-medium">{metrics.processes.total}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Running:</span>
                  <span className="font-medium">{metrics.processes.running}</span>
                </div>
              </div>
            </div>

            {/* Uptime Card */}
            <div className="bg-white rounded-lg shadow border p-6">
              <div className="flex items-center space-x-2 mb-4">
                <Clock className="w-6 h-6 text-teal-600" />
                <h3 className="text-lg font-semibold text-gray-900">Uptime</h3>
              </div>
              
              <div className="text-2xl font-bold text-teal-600">
                {formatUptime(metrics.uptime)}
              </div>
            </div>

            {/* Temperature Card */}
            <div className="bg-white rounded-lg shadow border p-6">
              <div className="flex items-center space-x-2 mb-4">
                <Thermometer className="w-6 h-6 text-red-600" />
                <h3 className="text-lg font-semibold text-gray-900">Temperature</h3>
              </div>
              
              <div className="text-2xl font-bold text-red-600">
                {metrics.cpu.temperature ? `${metrics.cpu.temperature}°C` : 'N/A'}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default SystemDashboard 