import React, { useState, useEffect } from 'react'

interface SystemMetrics {
  cpu: number
  memory: number
  disk: number
  network: {
    upload: number
    download: number
  }
  uptime: string
  temperature: number
}

const SystemDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<SystemMetrics>({
    cpu: 0,
    memory: 0,
    disk: 0,
    network: { upload: 0, download: 0 },
    uptime: '0 days, 0 hours',
    temperature: 0
  })

  // Simulate real-time metrics
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics({
        cpu: Math.random() * 100,
        memory: Math.random() * 100,
        disk: Math.random() * 100,
        network: {
          upload: Math.random() * 100,
          download: Math.random() * 100
        },
        uptime: '2 days, 14 hours',
        temperature: 45 + Math.random() * 20
      })
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  const MetricCard = ({ title, value, unit, color }: { title: string; value: number; unit: string; color: string }) => (
    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 transition-all duration-200 hover:-translate-y-1 hover:shadow-lg">
      <h3 className="text-base font-semibold text-gray-600 mb-2">{title}</h3>
      <div className="text-3xl font-bold mb-4" style={{ color }}>
        {value.toFixed(1)}{unit}
      </div>
      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div 
          className="h-full rounded-full transition-all duration-300" 
          style={{ 
            width: `${Math.min(value, 100)}%`, 
            backgroundColor: color 
          }}
        />
      </div>
    </div>
  )

  return (
    <div className="p-8 h-screen overflow-y-auto">
      <div className="mb-8 text-center">
        <h2 className="text-4xl font-bold text-gray-800 mb-2">System Dashboard</h2>
        <p className="text-gray-600 text-lg">Real-time system monitoring</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard 
          title="CPU Usage" 
          value={metrics.cpu} 
          unit="%" 
          color="#3b82f6"
        />
        <MetricCard 
          title="Memory Usage" 
          value={metrics.memory} 
          unit="%" 
          color="#10b981"
        />
        <MetricCard 
          title="Disk Usage" 
          value={metrics.disk} 
          unit="%" 
          color="#f59e0b"
        />
        <MetricCard 
          title="Temperature" 
          value={metrics.temperature} 
          unit="°C" 
          color="#ef4444"
        />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">System Information</h3>
          <div className="space-y-3">
            <div className="flex justify-between py-2 border-b border-gray-100">
              <span className="text-gray-600">Uptime:</span>
              <span className="font-medium">{metrics.uptime}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-gray-100">
              <span className="text-gray-600">Network Upload:</span>
              <span className="font-medium">{metrics.network.upload.toFixed(1)} MB/s</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-gray-600">Network Download:</span>
              <span className="font-medium">{metrics.network.download.toFixed(1)} MB/s</span>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">Quick Actions</h3>
          <div className="grid grid-cols-2 gap-3">
            <button className="p-3 bg-gray-50 border border-gray-200 rounded-lg text-gray-700 text-sm font-medium cursor-pointer transition-all hover:bg-gray-100 hover:border-gray-300">
              Check System Health
            </button>
            <button className="p-3 bg-gray-50 border border-gray-200 rounded-lg text-gray-700 text-sm font-medium cursor-pointer transition-all hover:bg-gray-100 hover:border-gray-300">
              View Logs
            </button>
            <button className="p-3 bg-gray-50 border border-gray-200 rounded-lg text-gray-700 text-sm font-medium cursor-pointer transition-all hover:bg-gray-100 hover:border-gray-300">
              Update System
            </button>
            <button className="p-3 bg-gray-50 border border-gray-200 rounded-lg text-gray-700 text-sm font-medium cursor-pointer transition-all hover:bg-gray-100 hover:border-gray-300">
              Backup Data
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SystemDashboard 