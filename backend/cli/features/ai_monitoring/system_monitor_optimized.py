#!/usr/bin/env python3
"""
Optimized System Monitor for Overseer CLI
"""
import psutil
import time
import json
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class OptimizedSystemMonitor:
    """Optimized system monitoring with lazy loading"""
    
    def __init__(self):
        self._cpu_history = []
        self._memory_history = []
        self._disk_history = []
        self._network_history = []
        self._last_update = time.time()
        
    def get_system_stats(self) -> Dict:
        """Get current system statistics"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory
            memory = psutil.virtual_memory()
            
            # Disk
            disk = psutil.disk_usage('/')
            
            # Network
            network = psutil.net_io_counters()
            
            stats = {
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'load_avg': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'timestamp': time.time()
            }
            
            # Update history
            self._update_history(stats)
            
            return stats
            
        except Exception as e:
            console.print(f"[red]Error getting system stats: {e}[/red]")
            return {}
    
    def _update_history(self, stats: Dict):
        """Update historical data"""
        max_history = 60  # Keep 60 data points
        
        self._cpu_history.append(stats['cpu']['percent'])
        self._memory_history.append(stats['memory']['percent'])
        self._disk_history.append(stats['disk']['percent'])
        
        # Trim history
        if len(self._cpu_history) > max_history:
            self._cpu_history = self._cpu_history[-max_history:]
            self._memory_history = self._memory_history[-max_history:]
            self._disk_history = self._disk_history[-max_history:]
    
    def get_process_stats(self, top_n: int = 10) -> List[Dict]:
        """Get top processes by resource usage"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': proc.info['cpu_percent'],
                        'memory_percent': proc.info['memory_percent'],
                        'status': proc.info['status']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            return processes[:top_n]
            
        except Exception as e:
            console.print(f"[red]Error getting process stats: {e}[/red]")
            return []
    
    def display_system_dashboard(self):
        """Display comprehensive system dashboard"""
        stats = self.get_system_stats()
        if not stats:
            return
        
        # Create dashboard
        dashboard = Table(title="System Dashboard", show_header=True, header_style="bold magenta")
        dashboard.add_column("Metric", style="cyan")
        dashboard.add_column("Current", style="green")
        dashboard.add_column("Status", style="yellow")
        dashboard.add_column("Trend", style="blue")
        
        # CPU
        cpu_status = "🟢 Good" if stats['cpu']['percent'] < 70 else "🟡 Warning" if stats['cpu']['percent'] < 90 else "🔴 Critical"
        cpu_trend = self._get_trend(self._cpu_history)
        dashboard.add_row(
            "CPU Usage",
            f"{stats['cpu']['percent']:.1f}%",
            cpu_status,
            cpu_trend
        )
        
        # Memory
        memory_status = "🟢 Good" if stats['memory']['percent'] < 70 else "🟡 Warning" if stats['memory']['percent'] < 90 else "🔴 Critical"
        memory_trend = self._get_trend(self._memory_history)
        dashboard.add_row(
            "Memory Usage",
            f"{stats['memory']['percent']:.1f}%",
            memory_status,
            memory_trend
        )
        
        # Disk
        disk_status = "🟢 Good" if stats['disk']['percent'] < 70 else "🟡 Warning" if stats['disk']['percent'] < 90 else "🔴 Critical"
        disk_trend = self._get_trend(self._disk_history)
        dashboard.add_row(
            "Disk Usage",
            f"{stats['disk']['percent']:.1f}%",
            disk_status,
            disk_trend
        )
        
        console.print(dashboard)
        
        # Process table
        processes = self.get_process_stats(5)
        if processes:
            proc_table = Table(title="Top Processes", show_header=True, header_style="bold magenta")
            proc_table.add_column("PID", style="cyan")
            proc_table.add_column("Name", style="green")
            proc_table.add_column("CPU %", style="yellow")
            proc_table.add_column("Memory %", style="blue")
            proc_table.add_column("Status", style="red")
            
            for proc in processes:
                proc_table.add_row(
                    str(proc['pid']),
                    proc['name'][:20],
                    f"{proc['cpu_percent']:.1f}%",
                    f"{proc['memory_percent']:.1f}%",
                    proc['status']
                )
            
            console.print(proc_table)
    
    def _get_trend(self, history: List[float]) -> str:
        """Calculate trend from history"""
        if len(history) < 2:
            return "➖"
        
        recent_avg = sum(history[-5:]) / min(5, len(history[-5:]))
        older_avg = sum(history[-10:-5]) / min(5, len(history[-10:-5])) if len(history) >= 10 else history[0]
        
        if recent_avg > older_avg * 1.1:
            return "📈"
        elif recent_avg < older_avg * 0.9:
            return "📉"
        else:
            return "➖"
    
    def get_recommendations(self) -> List[str]:
        """Get system recommendations based on current stats"""
        stats = self.get_system_stats()
        if not stats:
            return []
        
        recommendations = []
        
        # CPU recommendations
        if stats['cpu']['percent'] > 90:
            recommendations.append("🔴 CPU usage is critical. Consider closing unnecessary applications.")
        elif stats['cpu']['percent'] > 70:
            recommendations.append("🟡 CPU usage is high. Monitor resource-intensive processes.")
        
        # Memory recommendations
        if stats['memory']['percent'] > 90:
            recommendations.append("🔴 Memory usage is critical. Consider restarting applications.")
        elif stats['memory']['percent'] > 70:
            recommendations.append("🟡 Memory usage is high. Check for memory leaks.")
        
        # Disk recommendations
        if stats['disk']['percent'] > 90:
            recommendations.append("🔴 Disk space is critical. Clean up unnecessary files.")
        elif stats['disk']['percent'] > 70:
            recommendations.append("🟡 Disk space is getting low. Consider cleanup.")
        
        return recommendations

def get_system_monitor():
    """Lazy load system monitor"""
    return OptimizedSystemMonitor()

def show_system_stats():
    """Show system statistics"""
    monitor = get_system_monitor()
    monitor.display_system_dashboard()
    
    # Show recommendations
    recommendations = monitor.get_recommendations()
    if recommendations:
        console.print("\n[bold yellow]Recommendations:[/bold yellow]")
        for rec in recommendations:
            console.print(f"• {rec}")

if __name__ == "__main__":
    show_system_stats() 