"""
Performance Optimizer for system performance analysis and optimization
Provides concrete, actionable advice to speed up your system.
"""

import os
import platform
import psutil
import subprocess
from datetime import datetime

class PerformanceOptimizer:
    """System performance optimizer with concrete recommendations"""
    
    def __init__(self):
        self.console_available = True
        try:
            from rich.console import Console
            from rich.table import Table
            self.console = Console()
            self.table = Table
        except ImportError:
            self.console_available = False
    
    def _print(self, message: str, style: str = ""):
        """Print message with or without rich formatting"""
        if self.console_available and style:
            self.console.print(message, style=style)
        else:
            print(message)
    
    def get_system_metrics(self) -> dict:
        """Get detailed system performance metrics"""
        try:
            # CPU information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            load_avg = os.getloadavg()
            
            # Memory information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk information
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network information
            network_io = psutil.net_io_counters()
            
            # Process information
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except psutil.NoSuchProcess:
                    pass
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'frequency': cpu_freq.current if cpu_freq else None,
                    'load_avg': load_avg
                },
                'memory': {
                    'total_gb': round(memory.total / (1024**3), 2),
                    'used_percent': memory.percent,
                    'available_gb': round(memory.available / (1024**3), 2),
                    'swap_used_percent': swap.percent
                },
                'disk': {
                    'total_gb': round(disk.total / (1024**3), 2),
                    'used_percent': round((disk.used / disk.total) * 100, 1),
                    'free_gb': round(disk.free / (1024**3), 2),
                    'read_mb': round(disk_io.read_bytes / (1024**2), 2) if disk_io else 0,
                    'write_mb': round(disk_io.write_bytes / (1024**2), 2) if disk_io else 0
                },
                'network': {
                    'bytes_sent_mb': round(network_io.bytes_sent / (1024**2), 2) if network_io else 0,
                    'bytes_recv_mb': round(network_io.bytes_recv / (1024**2), 2) if network_io else 0
                },
                'top_processes': processes[:10],
                'platform': platform.system(),
                'uptime': datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            return {'error': f"Could not gather metrics: {e}"}
    
    def analyze_performance(self, action: str = "analyze") -> str:
        """Analyze system performance and provide optimization recommendations"""
        metrics = self.get_system_metrics()
        
        if 'error' in metrics:
            return f"Performance analysis unavailable: {metrics['error']}"
        
        analysis = []
        
        # Header
        analysis.append("🚀 PERFORMANCE OPTIMIZER - System Analysis")
        analysis.append("=" * 50)
        analysis.append("")
        
        # System Overview
        analysis.append("📊 System Overview:")
        analysis.append(f"  Platform: {metrics['platform']}")
        analysis.append(f"  CPU Cores: {metrics['cpu']['count']}")
        analysis.append(f"  Memory: {metrics['memory']['total_gb']}GB")
        analysis.append(f"  Storage: {metrics['disk']['total_gb']}GB")
        analysis.append(f"  System Uptime: Since {metrics['uptime']}")
        analysis.append("")
        
        # Current Performance Metrics
        analysis.append("📈 Current Performance Metrics:")
        analysis.append(f"  • CPU Usage: {metrics['cpu']['percent']:.1f}%")
        analysis.append(f"  • Memory Usage: {metrics['memory']['used_percent']:.1f}%")
        analysis.append(f"  • Disk Usage: {metrics['disk']['used_percent']:.1f}%")
        analysis.append(f"  • Load Average: {metrics['cpu']['load_avg'][0]:.2f}")
        if metrics['cpu']['frequency']:
            analysis.append(f"  • CPU Frequency: {metrics['cpu']['frequency']:.0f} MHz")
        analysis.append("")
        
        # Performance Issues & Recommendations
        issues_found = []
        recommendations = []
        
        # CPU Analysis
        if metrics['cpu']['percent'] > 80:
            issues_found.append("🔴 HIGH CPU USAGE")
            recommendations.extend([
                "💡 CPU Optimization:",
                "   → Check top CPU-consuming processes below",
                "   → Close unnecessary applications",
                "   → Consider upgrading CPU if consistently high",
                "   → Check for malware or runaway processes",
                ""
            ])
        elif metrics['cpu']['percent'] > 60:
            issues_found.append("🟡 MODERATE CPU USAGE")
            recommendations.extend([
                "💡 CPU Optimization:",
                "   → Monitor CPU usage patterns",
                "   → Consider closing non-essential applications",
                ""
            ])
        
        # Memory Analysis
        if metrics['memory']['used_percent'] > 85:
            issues_found.append("🔴 HIGH MEMORY USAGE")
            recommendations.extend([
                "💡 Memory Optimization:",
                "   → Restart memory-heavy applications",
                "   → Close unused browser tabs",
                "   → Consider adding more RAM",
                f"   → Only {metrics['memory']['available_gb']:.1f}GB available",
                ""
            ])
        elif metrics['memory']['used_percent'] > 70:
            issues_found.append("🟡 MODERATE MEMORY USAGE")
            recommendations.extend([
                "💡 Memory Optimization:",
                "   → Monitor memory usage",
                f"   → {metrics['memory']['available_gb']:.1f}GB still available",
                ""
            ])
        
        # Disk Analysis
        if metrics['disk']['used_percent'] > 90:
            issues_found.append("🔴 LOW DISK SPACE")
            recommendations.extend([
                "💡 Disk Space Optimization:",
                "   → Delete unnecessary files immediately",
                "   → Empty trash/recycle bin",
                "   → Clear browser cache and downloads",
                f"   → Only {metrics['disk']['free_gb']:.1f}GB free space left",
                "   → Use: du -sh /* | sort -hr | head -10",
                ""
            ])
        elif metrics['disk']['used_percent'] > 80:
            issues_found.append("🟡 LIMITED DISK SPACE")
            recommendations.extend([
                "💡 Disk Space Maintenance:",
                "   → Clean up old files and logs",
                f"   → {metrics['disk']['free_gb']:.1f}GB free space remaining",
                ""
            ])
        
        # Load Average Analysis
        load_threshold = metrics['cpu']['count'] * 1.5
        if metrics['cpu']['load_avg'][0] > load_threshold:
            issues_found.append("🔴 HIGH SYSTEM LOAD")
            recommendations.extend([
                "💡 System Load Optimization:",
                f"   → Load average ({metrics['cpu']['load_avg'][0]:.2f}) is high for {metrics['cpu']['count']} cores",
                "   → Check I/O-intensive processes",
                "   → Consider reducing concurrent tasks",
                ""
            ])
        
        # Display issues found
        if issues_found:
            analysis.append("⚠️  Issues Detected:")
            for issue in issues_found:
                analysis.append(f"  {issue}")
            analysis.append("")
        else:
            analysis.append("✅ No major performance issues detected!")
            analysis.append("")
        
        # Add recommendations
        if recommendations:
            analysis.append("🎯 Optimization Recommendations:")
            analysis.extend(recommendations)
        
        # Top Processes Analysis
        analysis.append("🔝 Top CPU-Consuming Processes:")
        for i, proc in enumerate(metrics['top_processes'][:5], 1):
            cpu_pct = proc['cpu_percent'] or 0
            mem_pct = proc['memory_percent'] or 0
            analysis.append(f"  {i}. {proc['name']} (PID: {proc['pid']}) - CPU: {cpu_pct:.1f}%, Memory: {mem_pct:.1f}%")
        analysis.append("")
        
        # Quick Commands
        analysis.append("🛠️  Quick Performance Commands:")
        analysis.append("   → htop                    # Interactive process viewer")
        analysis.append("   → ps aux --sort=-%cpu     # CPU-sorted processes")
        analysis.append("   → df -h                   # Disk usage summary")
        analysis.append("   → free -h                 # Memory usage summary")
        analysis.append("   → iotop                   # I/O monitoring")
        analysis.append("")
        
        # Performance Score
        score = self._calculate_performance_score(metrics)
        analysis.append(f"🎯 Overall Performance Score: {score}/100")
        if score >= 80:
            analysis.append("   Status: ✅ Excellent")
        elif score >= 60:
            analysis.append("   Status: 🟡 Good")
        elif score >= 40:
            analysis.append("   Status: 🟠 Fair - Optimization recommended")
        else:
            analysis.append("   Status: 🔴 Poor - Immediate optimization needed")
        
        return '\n'.join(analysis)
    
    def _calculate_performance_score(self, metrics: dict) -> int:
        """Calculate an overall performance score (0-100)"""
        score = 100
        
        # CPU penalty
        cpu_pct = metrics['cpu']['percent']
        if cpu_pct > 80:
            score -= 30
        elif cpu_pct > 60:
            score -= 15
        elif cpu_pct > 40:
            score -= 5
        
        # Memory penalty
        mem_pct = metrics['memory']['used_percent']
        if mem_pct > 85:
            score -= 25
        elif mem_pct > 70:
            score -= 10
        elif mem_pct > 50:
            score -= 5
        
        # Disk penalty
        disk_pct = metrics['disk']['used_percent']
        if disk_pct > 90:
            score -= 20
        elif disk_pct > 80:
            score -= 10
        elif disk_pct > 70:
            score -= 5
        
        # Load average penalty
        load_avg = metrics['cpu']['load_avg'][0]
        cpu_count = metrics['cpu']['count']
        if load_avg > cpu_count * 2:
            score -= 15
        elif load_avg > cpu_count * 1.5:
            score -= 8
        
        return max(0, score)
    
    def run_once(self, action: str):
        """Run performance optimization once (alias for run_optimization)"""
        self.run_optimization(action)
    
    def run_optimization(self, action: str):
        """Run performance optimization based on action"""
        if action == "analyze":
            result = self.analyze_performance(action)
            self._print(result)
        else:
            self._print(f"Unknown action: {action}. Available actions: analyze")

if __name__ == "__main__":
    import sys
    optimizer = PerformanceOptimizer()
    
    action = sys.argv[1] if len(sys.argv) > 1 else "analyze"
    optimizer.run_optimization(action)
