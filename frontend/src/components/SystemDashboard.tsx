import React, { useState, useEffect, useRef, useMemo } from 'react'
import { Line } from 'react-chartjs-2';
import { Chart, LineController, LineElement, PointElement, LinearScale, Title, CategoryScale, Tooltip, Filler } from 'chart.js';
Chart.register(LineController, LineElement, PointElement, LinearScale, Title, CategoryScale, Tooltip, Filler);

interface ProcessInfo {
  pid: number
  name: string
  memory_percent: number
  memory_mb: number
  cpu_percent: number
  status: string
}

interface ProcessTableProps {
  processes: ProcessInfo[]
  title: string
}

const ProcessTable: React.FC<ProcessTableProps> = ({ processes, title }) => {
  const [sortConfig, setSortConfig] = useState<{
    key: keyof ProcessInfo | null;
    direction: 'asc' | 'desc';
  }>({ key: null, direction: 'asc' });

  const getStatusBadge = (status: string) => (
    <span className={`process-status ${
      status === 'Running' 
        ? 'status-running' 
        : 'status-sleeping'
    }`}>
      {status}
    </span>
  );

  const getCpuClass = (cpuPercent: number) => {
    if (cpuPercent > 20) return 'process-cpu cpu-high';
    if (cpuPercent > 10) return 'process-cpu cpu-medium';
    return 'process-cpu cpu-low';
  };

  const handleSort = (key: keyof ProcessInfo) => {
    let direction: 'asc' | 'desc' = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const sortedProcesses = useMemo(() => {
    if (!sortConfig.key) return processes;

    return [...processes].sort((a, b) => {
      const aValue = a[sortConfig.key!];
      const bValue = b[sortConfig.key!];

      if (typeof aValue === 'string' && typeof bValue === 'string') {
        // String comparison (for name and status)
        return sortConfig.direction === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      } else if (typeof aValue === 'number' && typeof bValue === 'number') {
        // Numeric comparison (for pid, memory_percent, memory_mb, cpu_percent)
        return sortConfig.direction === 'asc' 
          ? aValue - bValue
          : bValue - aValue;
      }
      return 0;
    });
  }, [processes, sortConfig]);

  const getSortClass = (columnKey: keyof ProcessInfo) => {
    if (sortConfig.key !== columnKey) return 'sortable';
    return sortConfig.direction === 'asc' ? 'sortable sort-asc' : 'sortable sort-desc';
  };

  return (
    <div className="process-table-container" style={{ marginTop: '-30rem' }}>
      <h3 className="process-table-title">{title}</h3>
      <div className="process-table-wrapper">
        <table className="process-table">
          <thead className="process-table-header">
            <tr>
              <th className={getSortClass('pid')} onClick={() => handleSort('pid')}>PID</th>
              <th className={getSortClass('name')} onClick={() => handleSort('name')}>Name</th>
              <th className={getSortClass('memory_percent')} onClick={() => handleSort('memory_percent')}>Memory %</th>
              <th className={getSortClass('memory_mb')} onClick={() => handleSort('memory_mb')}>Memory (MB)</th>
              <th className={getSortClass('cpu_percent')} onClick={() => handleSort('cpu_percent')}>CPU %</th>
              <th onClick={() => handleSort('status')}>Status</th>
            </tr>
          </thead>
          <tbody>
            {sortedProcesses.map((process) => (
              <tr key={process.pid} className="process-table-row">
                <td className="process-table-cell">
                  <span className="process-pid">{process.pid}</span>
                </td>
                <td className="process-table-cell">
                  <span className="process-name">{process.name}</span>
                </td>
                <td className="process-table-cell">
                  <span className="process-memory">{process.memory_percent.toFixed(1)}%</span>
                </td>
                <td className="process-table-cell">
                  <span className="process-memory">{process.memory_mb.toFixed(0)} MB</span>
                </td>
                <td className="process-table-cell">
                  <span className={getCpuClass(process.cpu_percent)}>
                    {process.cpu_percent.toFixed(1)}%
                  </span>
                </td>
                <td className="process-table-cell">
                  {getStatusBadge(process.status)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const SystemDashboard: React.FC = () => {
  const [processes, setProcesses] = useState<ProcessInfo[]>([]);
  const [cpuHistory, setCpuHistory] = useState<number[]>([]);
  const [memoryHistory, setMemoryHistory] = useState<number[]>([]);
  const [diskHistory, setDiskHistory] = useState<number[]>([]);
  const [cpuTimestamps, setCpuTimestamps] = useState<string[]>([]);
  const cpuChartRef = useRef<any>(null);

  // Simulate real-time metrics
  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date();
      const timeLabel = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      
      // Generate new metrics data
      const newCpuValue = Math.random() * 100;
      const newMemoryValue = Math.random() * 100;
      const newDiskValue = Math.random() * 100;
      
      // Only add new data if timestamp is new
      const lastTimestamp = cpuTimestamps[cpuTimestamps.length - 1];
      const MAX_POINTS = 60;
      if (cpuTimestamps.length === 0 || lastTimestamp !== timeLabel) {
        setCpuTimestamps(t => [...t.slice(-MAX_POINTS + 1), timeLabel]);
        setCpuHistory(h => [...h.slice(-MAX_POINTS + 1), newCpuValue]);
        setMemoryHistory(h => [...h.slice(-MAX_POINTS + 1), newMemoryValue]);
        setDiskHistory(h => [...h.slice(-MAX_POINTS + 1), newDiskValue]);
      }
      
      // Generate mock process data
      const processNames = ['chrome.exe', 'code.exe', 'python.exe', 'node.exe', 'firefox.exe', 'discord.exe', 'spotify.exe', 'teams.exe'];
      const statuses = ['Running', 'Sleeping', 'Running', 'Sleeping', 'Running'];
      
      const newProcesses: ProcessInfo[] = processNames.map((name, index) => ({
        pid: 1000 + index + Math.floor(Math.random() * 100),
        name: name,
        memory_percent: Math.random() * 25,
        memory_mb: Math.random() * 1024 + 100,
        cpu_percent: Math.random() * 50,
        status: statuses[Math.floor(Math.random() * statuses.length)]
      })).sort((a, b) => b.cpu_percent - a.cpu_percent); // Sort by CPU usage descending
      
      setProcesses(newProcesses);
    }, 1000)
    return () => clearInterval(interval)
  }, [cpuTimestamps])

  const chartOptions = (label: string) => ({
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: {
        enabled: true,
        callbacks: {
          label: function(context: any) {
            const value = context.parsed.y;
            return `${label}: ${value.toFixed(1)}%`;
          }
        }
      }
    },
    scales: {
      y: {
        min: 0,
        max: 100,
        ticks: {
          stepSize: 10, // Show ticks every 10%
          callback: function(tickValue: string | number) {
            return `${tickValue}%`;
          }
        }
      }
    }
  });

  return (
    <div className="p-8 h-screen overflow-y-auto">
      <div className="mb-2 text-center">
        <h2 className="text-4xl font-bold text-gray-800 mb-2" style={{ textAlign: 'center' }}>System Dashboard</h2>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-1 gap-0 mb-0" style={{ marginTop: '0.5em' }}>
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200" style={{ marginTop: '0', marginBottom: '0', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <h3 className="text-lg font-semibold text-gray-800 mb-8 pb-2">System Usage</h3>
          <div className="chart-scroll-x" style={{height: '700px', overflowX: 'auto', width: '100%', display: 'block'}}>
            <div style={{width: `${Math.max(1200, cpuTimestamps.length * 40)}px`, minWidth: '1200px'}}>
              <Line
                ref={cpuChartRef}
                data={{
                  labels: cpuTimestamps,
                  datasets: [
                    { label: 'CPU Usage', data: cpuHistory, borderColor: '#3b82f6', backgroundColor: 'rgba(59,130,246,0.1)', fill: false },
                    { label: 'Memory Usage', data: memoryHistory, borderColor: '#10b981', backgroundColor: 'rgba(16,185,129,0.1)', fill: false },
                    { label: 'Disk Usage', data: diskHistory, borderColor: '#f59e0b', backgroundColor: 'rgba(245,158,11,0.1)', fill: false }
                  ]
                }}
                options={{
                  ...chartOptions('Usage'),
                  maintainAspectRatio: false,
                  plugins: {
                    legend: { display: true, position: 'top' },
                    tooltip: {
                      enabled: true,
                      callbacks: {
                        label: function(context: any) {
                          const value = context.parsed.y;
                          return `${context.dataset.label}: ${value.toFixed(1)}%`;
                        }
                      }
                    }
                  }
                }}
              />
            </div>
          </div>
        </div>
      </div>
      
      {/* Processes Table - React Component */}
      <ProcessTable processes={processes} title="Running Processes" />
    </div>
  )
}

export default SystemDashboard