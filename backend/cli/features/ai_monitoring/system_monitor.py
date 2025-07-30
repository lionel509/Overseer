"""
Real-time System Monitoring Module
Collects and analyzes system metrics for performance monitoring and optimization.
"""

import os
import time
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️  psutil not available. Install with: pip install psutil")

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

@dataclass
class SystemMetrics:
    """System metrics data structure"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    network_sent_mb: float
    network_recv_mb: float
    network_sent_rate: float
    network_recv_rate: float
    process_count: int
    load_average: Tuple[float, float, float]
    temperature: Optional[float] = None
    battery_percent: Optional[float] = None
    battery_plugged: Optional[bool] = None

class SystemMonitor:
    """Real-time system monitoring and metrics collection"""
    
    def __init__(self, db_path: str = None, config: Dict = None):
        """Initialize system monitor with database and configuration"""
        if not PSUTIL_AVAILABLE:
            raise RuntimeError("psutil is required for system monitoring. Install with: pip install psutil")
        
        self.console = Console() if RICH_AVAILABLE else None
        self.config = config or {}
        
        # Database setup
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '../../db/system_metrics.db')
        self.db_path = db_path
        self._init_database()
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_thread = None
        self.last_metrics = None
        self.metrics_history = []
        
        # Performance thresholds
        self.thresholds = {
            'cpu_warning': self.config.get('cpu_warning', 70.0),
            'cpu_critical': self.config.get('cpu_critical', 90.0),
            'memory_warning': self.config.get('memory_warning', 80.0),
            'memory_critical': self.config.get('memory_critical', 95.0),
            'disk_warning': self.config.get('disk_warning', 85.0),
            'disk_critical': self.config.get('disk_critical', 95.0),
        }
    
    def _init_database(self):
        """Initialize the metrics database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                cpu_percent REAL,
                memory_percent REAL,
                memory_used_gb REAL,
                memory_total_gb REAL,
                disk_percent REAL,
                disk_used_gb REAL,
                disk_total_gb REAL,
                network_sent_mb REAL,
                network_recv_mb REAL,
                network_sent_rate REAL,
                network_recv_rate REAL,
                process_count INTEGER,
                load_average_1 REAL,
                load_average_5 REAL,
                load_average_15 REAL,
                temperature REAL,
                battery_percent REAL,
                battery_plugged INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                alert_type TEXT,
                metric_name TEXT,
                metric_value REAL,
                threshold REAL,
                severity TEXT,
                message TEXT,
                acknowledged INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create performance history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                avg_cpu_percent REAL,
                max_cpu_percent REAL,
                avg_memory_percent REAL,
                max_memory_percent REAL,
                avg_disk_percent REAL,
                max_disk_percent REAL,
                total_network_sent_gb REAL,
                total_network_recv_gb REAL,
                peak_process_count INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            load_average = psutil.getloadavg()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = memory.used / (1024**3)
            memory_total_gb = memory.total / (1024**3)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used_gb = disk.used / (1024**3)
            disk_total_gb = disk.total / (1024**3)
            
            # Network metrics
            network = psutil.net_io_counters()
            network_sent_mb = network.bytes_sent / (1024**2)
            network_recv_mb = network.bytes_recv / (1024**2)
            
            # Calculate network rates (simple approach)
            network_sent_rate = 0.0
            network_recv_rate = 0.0
            if self.last_metrics:
                time_diff = time.time() - self.last_metrics.timestamp
                if time_diff > 0:
                    network_sent_rate = (network_sent_mb - self.last_metrics.network_sent_mb) / time_diff
                    network_recv_rate = (network_recv_mb - self.last_metrics.network_recv_mb) / time_diff
            
            # Process count
            process_count = len(psutil.pids())
            
            # Temperature (platform specific)
            temperature = self._get_temperature()
            
            # Battery (if available)
            battery_percent = None
            battery_plugged = None
            try:
                battery = psutil.sensors_battery()
                if battery:
                    battery_percent = battery.percent
                    battery_plugged = battery.power_plugged
            except:
                pass
            
            metrics = SystemMetrics(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_gb=memory_used_gb,
                memory_total_gb=memory_total_gb,
                disk_percent=disk_percent,
                disk_used_gb=disk_used_gb,
                disk_total_gb=disk_total_gb,
                network_sent_mb=network_sent_mb,
                network_recv_mb=network_recv_mb,
                network_sent_rate=network_sent_rate,
                network_recv_rate=network_recv_rate,
                process_count=process_count,
                load_average=load_average,
                temperature=temperature,
                battery_percent=battery_percent,
                battery_plugged=battery_plugged
            )
            
            self.last_metrics = metrics
            return metrics
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error collecting metrics: {e}[/red]")
            raise
    
    def _get_temperature(self) -> Optional[float]:
        """Get CPU temperature (platform specific)"""
        try:
            # macOS
            if os.uname().sysname == 'Darwin':
                import subprocess
                result = subprocess.run(['sudo', 'powermetrics', '-n', '1', '-i', '1000'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'CPU die temperature' in line:
                            temp_str = line.split(':')[1].strip().split()[0]
                            return float(temp_str)
            
            # Linux
            elif os.path.exists('/sys/class/thermal/thermal_zone0/temp'):
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    temp = int(f.read().strip()) / 1000.0
                    return temp
            
            # Windows
            elif os.name == 'nt':
                import wmi
                w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
                temperature_infos = w.Sensor()
                for sensor in temperature_infos:
                    if sensor.SensorType == 'Temperature':
                        return float(sensor.Value)
                        
        except Exception:
            pass
        
        return None
    
    def save_metrics(self, metrics: SystemMetrics):
        """Save metrics to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_metrics (
                    timestamp, cpu_percent, memory_percent, memory_used_gb, memory_total_gb,
                    disk_percent, disk_used_gb, disk_total_gb, network_sent_mb, network_recv_mb,
                    network_sent_rate, network_recv_rate, process_count, load_average_1,
                    load_average_5, load_average_15, temperature, battery_percent, battery_plugged
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.timestamp, metrics.cpu_percent, metrics.memory_percent,
                metrics.memory_used_gb, metrics.memory_total_gb, metrics.disk_percent,
                metrics.disk_used_gb, metrics.disk_total_gb, metrics.network_sent_mb,
                metrics.network_recv_mb, metrics.network_sent_rate, metrics.network_recv_rate,
                metrics.process_count, metrics.load_average[0], metrics.load_average[1],
                metrics.load_average[2], metrics.temperature, metrics.battery_percent,
                1 if metrics.battery_plugged else 0
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error saving metrics: {e}[/red]")
    
    def check_alerts(self, metrics: SystemMetrics) -> List[Dict]:
        """Check for threshold violations and generate alerts"""
        alerts = []
        
        # CPU alerts
        if metrics.cpu_percent >= self.thresholds['cpu_critical']:
            alerts.append({
                'type': 'cpu',
                'severity': 'critical',
                'message': f"CPU usage critical: {metrics.cpu_percent:.1f}%",
                'value': metrics.cpu_percent,
                'threshold': self.thresholds['cpu_critical']
            })
        elif metrics.cpu_percent >= self.thresholds['cpu_warning']:
            alerts.append({
                'type': 'cpu',
                'severity': 'warning',
                'message': f"CPU usage high: {metrics.cpu_percent:.1f}%",
                'value': metrics.cpu_percent,
                'threshold': self.thresholds['cpu_warning']
            })
        
        # Memory alerts
        if metrics.memory_percent >= self.thresholds['memory_critical']:
            alerts.append({
                'type': 'memory',
                'severity': 'critical',
                'message': f"Memory usage critical: {metrics.memory_percent:.1f}%",
                'value': metrics.memory_percent,
                'threshold': self.thresholds['memory_critical']
            })
        elif metrics.memory_percent >= self.thresholds['memory_warning']:
            alerts.append({
                'type': 'memory',
                'severity': 'warning',
                'message': f"Memory usage high: {metrics.memory_percent:.1f}%",
                'value': metrics.memory_percent,
                'threshold': self.thresholds['memory_warning']
            })
        
        # Disk alerts
        if metrics.disk_percent >= self.thresholds['disk_critical']:
            alerts.append({
                'type': 'disk',
                'severity': 'critical',
                'message': f"Disk usage critical: {metrics.disk_percent:.1f}%",
                'value': metrics.disk_percent,
                'threshold': self.thresholds['disk_critical']
            })
        elif metrics.disk_percent >= self.thresholds['disk_warning']:
            alerts.append({
                'type': 'disk',
                'severity': 'warning',
                'message': f"Disk usage high: {metrics.disk_percent:.1f}%",
                'value': metrics.disk_percent,
                'threshold': self.thresholds['disk_warning']
            })
        
        return alerts
    
    def save_alerts(self, alerts: List[Dict]):
        """Save alerts to database"""
        if not alerts:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for alert in alerts:
                cursor.execute('''
                    INSERT INTO system_alerts (
                        timestamp, alert_type, metric_name, metric_value, 
                        threshold, severity, message
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    time.time(), alert['type'], alert['type'], alert['value'],
                    alert['threshold'], alert['severity'], alert['message']
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error saving alerts: {e}[/red]")
    
    def get_system_summary(self) -> Dict:
        """Get current system summary"""
        metrics = self.collect_metrics()
        
        # Calculate health score (0-100, higher is better)
        health_score = 100
        if metrics.cpu_percent > 80:
            health_score -= 20
        elif metrics.cpu_percent > 60:
            health_score -= 10
        
        if metrics.memory_percent > 90:
            health_score -= 25
        elif metrics.memory_percent > 70:
            health_score -= 15
        
        if metrics.disk_percent > 90:
            health_score -= 20
        elif metrics.disk_percent > 80:
            health_score -= 10
        
        health_score = max(0, health_score)
        
        return {
            'health_score': health_score,
            'status': 'healthy' if health_score > 70 else 'warning' if health_score > 40 else 'critical',
            'metrics': asdict(metrics),
            'alerts': self.check_alerts(metrics)
        }
    
    def display_metrics(self, metrics: SystemMetrics = None):
        """Display current metrics in a formatted table"""
        if not RICH_AVAILABLE:
            print("Rich library required for formatted display")
            return
        
        if metrics is None:
            metrics = self.collect_metrics()
        
        # Create metrics table
        table = Table(title="System Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Status", style="yellow")
        
        # CPU
        cpu_status = "🟢" if metrics.cpu_percent < 60 else "🟡" if metrics.cpu_percent < 80 else "🔴"
        table.add_row("CPU Usage", f"{metrics.cpu_percent:.1f}%", cpu_status)
        
        # Memory
        memory_status = "🟢" if metrics.memory_percent < 70 else "🟡" if metrics.memory_percent < 90 else "🔴"
        table.add_row("Memory Usage", f"{metrics.memory_percent:.1f}% ({metrics.memory_used_gb:.1f}GB / {metrics.memory_total_gb:.1f}GB)", memory_status)
        
        # Disk
        disk_status = "🟢" if metrics.disk_percent < 80 else "🟡" if metrics.disk_percent < 90 else "🔴"
        table.add_row("Disk Usage", f"{metrics.disk_percent:.1f}% ({metrics.disk_used_gb:.1f}GB / {metrics.disk_total_gb:.1f}GB)", disk_status)
        
        # Network
        table.add_row("Network Sent", f"{metrics.network_sent_mb:.1f}MB ({metrics.network_sent_rate:.1f}MB/s)", "🟢")
        table.add_row("Network Recv", f"{metrics.network_recv_mb:.1f}MB ({metrics.network_recv_rate:.1f}MB/s)", "🟢")
        
        # Processes
        table.add_row("Processes", str(metrics.process_count), "🟢")
        
        # Load Average
        table.add_row("Load Average", f"{metrics.load_average[0]:.2f}, {metrics.load_average[1]:.2f}, {metrics.load_average[2]:.2f}", "🟢")
        
        # Temperature
        if metrics.temperature:
            temp_status = "🟢" if metrics.temperature < 70 else "🟡" if metrics.temperature < 85 else "🔴"
            table.add_row("Temperature", f"{metrics.temperature:.1f}°C", temp_status)
        
        # Battery
        if metrics.battery_percent is not None:
            battery_status = "🟢" if metrics.battery_percent > 20 else "🟡" if metrics.battery_percent > 10 else "🔴"
            plugged = "🔌" if metrics.battery_plugged else "🔋"
            table.add_row("Battery", f"{metrics.battery_percent:.1f}% {plugged}", battery_status)
        
        self.console.print(table)
    
    def start_monitoring(self, interval: int = 5, save_to_db: bool = True):
        """Start continuous monitoring"""
        if self.is_monitoring:
            if self.console:
                self.console.print("[yellow]Monitoring already running[/yellow]")
            return
        
        self.is_monitoring = True
        
        if self.console:
            self.console.print(f"[green]Starting system monitoring (interval: {interval}s)[/green]")
        
        try:
            while self.is_monitoring:
                metrics = self.collect_metrics()
                
                if save_to_db:
                    self.save_metrics(metrics)
                
                alerts = self.check_alerts(metrics)
                if alerts:
                    self.save_alerts(alerts)
                    for alert in alerts:
                        if self.console:
                            color = "red" if alert['severity'] == 'critical' else "yellow"
                            self.console.print(f"[{color}]{alert['message']}[/{color}]")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            if self.console:
                self.console.print("[yellow]Monitoring stopped by user[/yellow]")
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Monitoring error: {e}[/red]")
        finally:
            self.is_monitoring = False
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.is_monitoring = False
        if self.console:
            self.console.print("[yellow]Stopping system monitoring...[/yellow]")

def main():
    """Main function for standalone testing"""
    monitor = SystemMonitor()
    
    print("🔍 System Monitor - Real-time Metrics")
    print("=" * 50)
    
    # Display current metrics
    monitor.display_metrics()
    
    # Get system summary
    summary = monitor.get_system_summary()
    print(f"\n🏥 System Health Score: {summary['health_score']}/100 ({summary['status']})")
    
    if summary['alerts']:
        print("\n⚠️  Active Alerts:")
        for alert in summary['alerts']:
            print(f"  - {alert['message']}")

if __name__ == "__main__":
    main() 