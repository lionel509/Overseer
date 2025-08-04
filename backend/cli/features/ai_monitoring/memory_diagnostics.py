"""
Memory Diagnostics Tool
Provides detailed analysis of memory usage and specific recommendations for fixing memory issues.
"""

import psutil
import subprocess
import os
import time
from typing import Dict, List, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from db.system_monitoring_db import system_monitoring_db

console = Console()

class MemoryDiagnostics:
    """Advanced memory diagnostics and troubleshooting"""
    
    def __init__(self):
        self.console = Console()
    
    def get_detailed_memory_info(self) -> Dict:
        """Get comprehensive memory information"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total_gb': memory.total / (1024**3),
            'available_gb': memory.available / (1024**3),
            'used_gb': memory.used / (1024**3),
            'percent': memory.percent,
            'swap_total_gb': swap.total / (1024**3),
            'swap_used_gb': swap.used / (1024**3),
            'swap_percent': swap.percent,
            'swap_free_gb': swap.free / (1024**3)
        }
    
    def get_top_memory_processes(self, top_n: int = 15) -> List[Dict]:
        """Get top memory-consuming processes with detailed info"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'memory_info', 'cpu_percent', 'status', 'create_time']):
            try:
                # Handle None values
                memory_percent = proc.info['memory_percent'] or 0.0
                cpu_percent = proc.info['cpu_percent'] or 0.0
                memory_mb = (proc.info['memory_info'].rss / 1024 / 1024) if proc.info['memory_info'] else 0.0
                
                # Calculate process age
                create_time = proc.info['create_time']
                age_hours = (psutil.time.time() - create_time) / 3600 if create_time else 0
                
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'memory_percent': memory_percent,
                    'memory_mb': memory_mb,
                    'cpu_percent': cpu_percent,
                    'status': proc.info['status'],
                    'age_hours': age_hours
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort by memory usage
        processes.sort(key=lambda x: x['memory_percent'], reverse=True)
        return processes[:top_n]
    
    def analyze_memory_patterns(self) -> Dict:
        """Analyze memory usage patterns and identify potential issues"""
        memory_info = self.get_detailed_memory_info()
        processes = self.get_top_memory_processes(20)
        
        analysis = {
            'total_memory_gb': memory_info['total_gb'],
            'used_memory_gb': memory_info['used_gb'],
            'memory_percent': memory_info['percent'],
            'swap_usage': memory_info['swap_percent'],
            'high_memory_processes': [],
            'potential_memory_leaks': [],
            'browser_processes': [],
            'system_processes': [],
            'user_processes': []
        }
        
        # Categorize processes
        for proc in processes:
            if proc['memory_percent'] > 5:  # High memory processes
                analysis['high_memory_processes'].append(proc)
            
            # Check for potential memory leaks (high memory + long running)
            if proc['memory_percent'] > 3 and proc['age_hours'] > 24:
                analysis['potential_memory_leaks'].append(proc)
            
            # Categorize by type
            name = proc['name'].lower()
            if any(browser in name for browser in ['chrome', 'firefox', 'safari', 'edge', 'brave']):
                analysis['browser_processes'].append(proc)
            elif any(sys_proc in name for sys_proc in ['system', 'kernel', 'init', 'systemd']):
                analysis['system_processes'].append(proc)
            else:
                analysis['user_processes'].append(proc)
        
        return analysis
    
    def get_memory_recommendations(self, analysis: Dict) -> List[str]:
        """Generate specific recommendations based on memory analysis"""
        recommendations = []
        
        # Overall memory status
        if analysis['memory_percent'] > 90:
            recommendations.append("🔴 CRITICAL: Memory usage is dangerously high!")
            recommendations.append("   Immediate actions needed:")
            recommendations.append("   • Close all non-essential applications")
            recommendations.append("   • Restart your computer if possible")
            recommendations.append("   • Check for memory-intensive processes below")
        
        elif analysis['memory_percent'] > 80:
            recommendations.append("🟡 WARNING: Memory usage is high")
            recommendations.append("   Consider these actions:")
            recommendations.append("   • Close browser tabs and applications")
            recommendations.append("   • Restart applications with high memory usage")
        
        # Browser-specific recommendations
        if analysis['browser_processes']:
            browser_memory = sum(p['memory_mb'] for p in analysis['browser_processes'])
            if browser_memory > 2000:  # More than 2GB in browsers
                recommendations.append("")
                recommendations.append("🌐 Browser Memory Usage:")
                recommendations.append(f"   • Browsers using {browser_memory:.0f}MB of memory")
                recommendations.append("   • Close unused browser tabs")
                recommendations.append("   • Restart browser if memory usage is high")
        
        # Potential memory leaks
        if analysis['potential_memory_leaks']:
            recommendations.append("")
            recommendations.append("⚠️  Potential Memory Leaks Detected:")
            for proc in analysis['potential_memory_leaks'][:3]:
                recommendations.append(f"   • {proc['name']} (PID: {proc['pid']}) - {proc['memory_percent']:.1f}% for {proc['age_hours']:.1f}h")
                recommendations.append(f"     Consider restarting this process")
        
        # Swap usage
        if analysis['swap_usage'] > 50:
            recommendations.append("")
            recommendations.append("💾 High Swap Usage:")
            recommendations.append("   • System is using swap memory extensively")
            recommendations.append("   • This indicates insufficient RAM")
            recommendations.append("   • Consider closing applications or upgrading RAM")
        
        # Specific troubleshooting commands
        recommendations.append("")
        recommendations.append("🔧 Troubleshooting Commands:")
        recommendations.append("   • Check memory usage: free -h")
        recommendations.append("   • Top memory processes: ps aux --sort=-%mem | head -10")
        recommendations.append("   • Monitor memory: watch -n 1 'free -h && echo \"---\" && ps aux --sort=-%mem | head -5'")
        
        return recommendations
    
    def _save_memory_pattern(self, analysis: Dict):
        """Save memory pattern to database"""
        try:
            memory_info = self.get_detailed_memory_info()
            
            pattern = {
                'timestamp': time.time(),
                'total_memory_gb': memory_info['total_gb'],
                'used_memory_gb': memory_info['used_gb'],
                'available_memory_gb': memory_info['available_gb'],
                'memory_percent': memory_info['percent'],
                'swap_percent': memory_info['swap_percent'],
                'swap_used_gb': memory_info['swap_used_gb'],
                'high_memory_processes': len(analysis.get('high_memory_processes', [])),
                'potential_memory_leaks': len(analysis.get('potential_memory_leaks', [])),
                'long_running_processes': len(analysis.get('long_running_processes', []))
            }
            
            system_monitoring_db.save_memory_pattern(pattern)
            
        except Exception as e:
            console.print(f"[red]Error saving memory pattern: {e}[/red]")
    
    def display_memory_diagnostics(self):
        """Display comprehensive memory diagnostics"""
        console.print(Panel.fit("🔍 Memory Diagnostics", style="bold blue"))
        
        # Get memory analysis
        analysis = self.analyze_memory_patterns()
        
        # Memory overview
        memory_table = Table(title="Memory Overview", show_header=True, header_style="bold magenta")
        memory_table.add_column("Metric", style="cyan")
        memory_table.add_column("Value", style="green")
        memory_table.add_column("Status", style="yellow")
        
        memory_info = self.get_detailed_memory_info()
        
        # Determine memory status
        if memory_info['percent'] > 90:
            status = "🔴 Critical"
        elif memory_info['percent'] > 80:
            status = "🟡 Warning"
        else:
            status = "🟢 Good"
        
        memory_table.add_row("Total RAM", f"{memory_info['total_gb']:.1f}GB", "")
        memory_table.add_row("Used RAM", f"{memory_info['used_gb']:.1f}GB ({memory_info['percent']:.1f}%)", status)
        memory_table.add_row("Available RAM", f"{memory_info['available_gb']:.1f}GB", "")
        memory_table.add_row("Swap Used", f"{memory_info['swap_used_gb']:.1f}GB ({memory_info['swap_percent']:.1f}%)", "")
        
        console.print(memory_table)
        
        # Top memory processes
        processes = self.get_top_memory_processes(10)
        if processes:
            proc_table = Table(title="Top Memory-Using Processes", show_header=True, header_style="bold magenta")
            proc_table.add_column("PID", style="cyan")
            proc_table.add_column("Name", style="green")
            proc_table.add_column("Memory %", style="blue")
            proc_table.add_column("Memory (MB)", style="yellow")
            proc_table.add_column("CPU %", style="red")
            proc_table.add_column("Age (h)", style="white")
            
            for proc in processes:
                # Highlight high memory processes
                memory_style = "bold red" if proc['memory_percent'] > 10 else "bold yellow" if proc['memory_percent'] > 5 else ""
                proc_table.add_row(
                    str(proc['pid']),
                    proc['name'][:25],
                    f"{proc['memory_percent']:.1f}%",
                    f"{proc['memory_mb']:.1f}",
                    f"{proc['cpu_percent']:.1f}%",
                    f"{proc['age_hours']:.1f}"
                )
            
            console.print(proc_table)
        
        # Save memory pattern to database
        self._save_memory_pattern(analysis)
        
        # Recommendations
        recommendations = self.get_memory_recommendations(analysis)
        if recommendations:
            console.print("\n[bold yellow]Recommendations:[/bold yellow]")
            for rec in recommendations:
                console.print(rec)

def main():
    """Run memory diagnostics"""
    diagnostics = MemoryDiagnostics()
    diagnostics.display_memory_diagnostics()

if __name__ == "__main__":
    main() 