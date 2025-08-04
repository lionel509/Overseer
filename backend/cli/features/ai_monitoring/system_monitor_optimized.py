#!/usr/bin/env python3
"""
Optimized System Monitor for Overseer CLI with LLM Integration
"""
import psutil
import time
import json
import re
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from db.system_monitoring_db import system_monitoring_db

console = Console()

class OptimizedSystemMonitor:
    """Optimized system monitoring with LLM-powered recommendations"""
    
    def __init__(self):
        self._cpu_history = []
        self._memory_history = []
        self._disk_history = []
        self._network_history = []
        self._last_update = time.time()
        self.llm_backend = None
        self._load_llm_backend()
    
    def _load_llm_backend(self):
        """Load LLM backend for intelligent recommendations"""
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            
            from overseer_cli import get_llm_backend, load_config
            config = load_config()
            self.llm_backend = get_llm_backend(config)
            
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load LLM backend: {e}[/yellow]")
            self.llm_backend = None
        
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
            
            # Save to database
            self._save_to_database(stats)
            
            return stats
            
        except Exception as e:
            console.print(f"[red]Error getting system stats: {e}[/red]")
            return {}
    
    def _save_to_database(self, stats: Dict):
        """Save system stats to database"""
        try:
            # Prepare metrics for database
            metrics = {
                'timestamp': stats['timestamp'],
                'cpu_percent': stats['cpu']['percent'],
                'memory_percent': stats['memory']['percent'],
                'memory_used_gb': stats['memory']['used'] / (1024**3),
                'memory_total_gb': stats['memory']['total'] / (1024**3),
                'disk_percent': stats['disk']['percent'],
                'disk_used_gb': stats['disk']['used'] / (1024**3),
                'disk_total_gb': stats['disk']['total'] / (1024**3),
                'network_sent_mb': stats['network']['bytes_sent'] / (1024**2),
                'network_recv_mb': stats['network']['bytes_recv'] / (1024**2),
                'process_count': len(psutil.pids()),
                'load_average_1': stats['cpu']['load_avg'][0] if stats['cpu']['load_avg'] else 0,
                'load_average_5': stats['cpu']['load_avg'][1] if stats['cpu']['load_avg'] else 0,
                'load_average_15': stats['cpu']['load_avg'][2] if stats['cpu']['load_avg'] else 0
            }
            
            # Save system metrics
            system_monitoring_db.save_system_metrics(metrics)
            
            # Get and save process metrics
            processes = self.get_process_stats(20)  # Top 20 processes
            if processes:
                system_monitoring_db.save_process_metrics(processes)
                
        except Exception as e:
            console.print(f"[red]Error saving to database: {e}[/red]")
    
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
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'memory_info']):
                try:
                    # Handle None values from psutil
                    cpu_percent = proc.info['cpu_percent'] or 0.0
                    memory_percent = proc.info['memory_percent'] or 0.0
                    memory_mb = (proc.info['memory_info'].rss / 1024 / 1024) if proc.info['memory_info'] else 0.0
                    
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': cpu_percent,
                        'memory_percent': memory_percent,
                        'memory_mb': memory_mb,
                        'status': proc.info['status']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by memory usage (most important for memory diagnostics)
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)
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
        
        # Memory with more details
        memory_status = "🟢 Good" if stats['memory']['percent'] < 70 else "🟡 Warning" if stats['memory']['percent'] < 90 else "🔴 Critical"
        memory_trend = self._get_trend(self._memory_history)
        used_gb = stats['memory']['used'] / (1024**3)
        total_gb = stats['memory']['total'] / (1024**3)
        memory_details = f"{stats['memory']['percent']:.1f}% ({used_gb:.1f}GB / {total_gb:.1f}GB)"
        dashboard.add_row(
            "Memory Usage",
            memory_details,
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
        
        # Enhanced process table with memory focus
        processes = self.get_process_stats(10)  # Show more processes for memory analysis
        if processes:
            proc_table = Table(title="Top Memory-Using Processes", show_header=True, header_style="bold magenta")
            proc_table.add_column("PID", style="cyan")
            proc_table.add_column("Name", style="green")
            proc_table.add_column("Memory %", style="blue")
            proc_table.add_column("Memory (MB)", style="yellow")
            proc_table.add_column("CPU %", style="red")
            proc_table.add_column("Status", style="white")
            
            for proc in processes:
                # Highlight high memory processes
                memory_style = "bold red" if proc['memory_percent'] > 10 else "bold yellow" if proc['memory_percent'] > 5 else "white"
                proc_table.add_row(
                    str(proc['pid']),
                    proc['name'][:25],
                    f"{proc['memory_percent']:.1f}%",
                    f"{proc['memory_mb']:.1f}",
                    f"{proc['cpu_percent']:.1f}%",
                    proc['status']
                )
            
            console.print(proc_table)
        
        # Show LLM-powered recommendations
        self.display_llm_recommendations(stats)
    
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
        
        # Enhanced memory recommendations
        if stats['memory']['percent'] > 90:
            recommendations.append("🔴 Memory usage is critical! Consider:")
            recommendations.append("  • Restart memory-intensive applications")
            recommendations.append("  • Close browser tabs and applications")
            recommendations.append("  • Check for memory leaks in running processes")
        elif stats['memory']['percent'] > 70:
            recommendations.append("🟡 Memory usage is high. Check for memory leaks.")
            recommendations.append("  • Monitor top memory-using processes above")
            recommendations.append("  • Consider restarting applications with high memory usage")
            recommendations.append("  • Check if any applications are consuming excessive memory")
        
        # Disk recommendations
        if stats['disk']['percent'] > 90:
            recommendations.append("🔴 Disk space is critical. Clean up unnecessary files.")
        elif stats['disk']['percent'] > 70:
            recommendations.append("🟡 Disk space is getting low. Consider cleanup.")
        
        # Add specific memory troubleshooting steps
        if stats['memory']['percent'] > 70:
            recommendations.append("")
            recommendations.append("💡 Memory Troubleshooting Steps:")
            recommendations.append("  • Run 'ps aux --sort=-%mem | head -10' to see top memory users")
            recommendations.append("  • Check for zombie processes: 'ps aux | grep -w Z'")
            recommendations.append("  • Monitor memory usage over time: 'watch -n 1 free -h'")
            recommendations.append("  • Consider increasing swap space if available")
        
        return recommendations
    
    def generate_llm_command_recommendations(self, stats: Dict) -> List[Dict]:
        """Generate LLM-powered command recommendations based on system issues"""
        if not self.llm_backend:
            return []
        
        try:
            # Create analysis prompt
            prompt = self._create_issue_analysis_prompt(stats)
            
            # Get LLM response
            response = self.llm_backend.run(prompt)
            
            # Parse commands from response
            commands = self._parse_llm_commands(response)
            
            return commands
            
        except Exception as e:
            console.print(f"[red]Error generating LLM recommendations: {e}[/red]")
            return []
    
    def _create_issue_analysis_prompt(self, stats: Dict) -> str:
        """Create prompt for LLM to analyze issues and recommend commands"""
        cpu_percent = stats.get('cpu', {}).get('percent', 0)
        memory_percent = stats.get('memory', {}).get('percent', 0)
        disk_percent = stats.get('disk', {}).get('percent', 0)
        
        # Get top processes for context
        processes = self.get_process_stats(5)
        process_info = ""
        if processes:
            process_info = "\nTop Memory Processes:\n"
            for proc in processes[:3]:
                process_info += f"- {proc['name']}: {proc['memory_percent']:.1f}% memory, {proc['cpu_percent']:.1f}% CPU\n"
        
        prompt = f"""
You are a system administration expert. Analyze the current system state and identify any issues that need attention.

Current System State:
- CPU Usage: {cpu_percent:.1f}%
- Memory Usage: {memory_percent:.1f}%
- Disk Usage: {disk_percent:.1f}%{process_info}

Based on this system state, identify any issues and recommend 3-5 specific commands that would help diagnose or fix these issues.

Focus on:
1. Commands to diagnose the root cause of any problems
2. Commands to monitor the situation
3. Commands to potentially fix issues (if safe)

For each command, provide:
- A descriptive name
- The exact command to run
- A brief description of what it does
- Priority level (high/medium/low)

Format your response as a JSON array of objects:
[
  {{
    "name": "Command Name",
    "command": "exact command to run",
    "description": "what this command does",
    "priority": "high/medium/low"
  }}
]

Focus on macOS-compatible commands. Only recommend safe commands (no rm -rf, sudo, etc.).
If there are no issues, recommend general monitoring commands.

Respond with ONLY the JSON array, no additional text.
"""
        return prompt
    
    def _parse_llm_commands(self, response: str) -> List[Dict]:
        """Parse LLM response into structured command list"""
        try:
            # Clean the response
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            # Parse JSON
            commands = json.loads(cleaned_response)
            
            # Validate and filter commands
            valid_commands = []
            for cmd in commands:
                if isinstance(cmd, dict) and all(key in cmd for key in ['name', 'command', 'description', 'priority']):
                    if self._is_safe_command(cmd['command']):
                        valid_commands.append(cmd)
            
            return valid_commands
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            console.print(f"[red]Error parsing LLM response: {e}[/red]")
            return []
    
    def _is_safe_command(self, command: str) -> bool:
        """Check if command is safe to execute"""
        dangerous_patterns = [
            r'\brm\s+-rf\b',  # rm -rf
            r'\bmkfs\b',      # format filesystem
            r'\bdd\b',        # dd command
            r'\bchmod\s+777\b',  # dangerous chmod
            r'\bchown\s+root\b', # dangerous chown
            r'\bsudo\b',      # sudo commands
            r'\bsu\b',        # su commands
            r'\bkillall\b',   # killall
            r'\bshutdown\b',  # shutdown
            r'\breboot\b',    # reboot
            r'\bhalt\b',      # halt
            r'\bpoweroff\b',  # poweroff
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return False
        
        return True
    
    def display_llm_recommendations(self, stats: Dict):
        """Display LLM-powered command recommendations"""
        if not self.llm_backend:
            console.print("[yellow]LLM not available for intelligent recommendations[/yellow]")
            return
        
        console.print("\n[bold cyan]🤖 AI-Powered Command Recommendations:[/bold cyan]")
        console.print("[cyan]Analyzing system issues and generating recommendations...[/cyan]")
        
        commands = self.generate_llm_command_recommendations(stats)
        
        if not commands:
            console.print("[yellow]No specific recommendations generated[/yellow]")
            return
        
        # Display commands in a table
        cmd_table = Table(title="Recommended Commands", show_header=True, header_style="bold magenta")
        cmd_table.add_column("#", style="cyan", width=3)
        cmd_table.add_column("Command", style="green", width=30)
        cmd_table.add_column("Description", style="yellow", width=50)
        cmd_table.add_column("Priority", style="red", width=8)
        
        for i, cmd in enumerate(commands, 1):
            priority_style = "bold red" if cmd['priority'] == 'high' else "bold yellow" if cmd['priority'] == 'medium' else "white"
            cmd_table.add_row(
                str(i),
                cmd['command'],
                cmd['description'],
                cmd['priority'],
                style=priority_style
            )
        
        console.print(cmd_table)
        
        # Ask if user wants to execute any commands
        if Confirm.ask("\n[cyan]Would you like to execute any of these commands?"):
            self._interactive_command_execution(commands)
    
    def _interactive_command_execution(self, commands: List[Dict]):
        """Allow user to select and execute recommended commands"""
        while True:
            try:
                choice = input("\n[cyan]Enter command number (1-{}) or 'q' to quit: [/cyan]".format(len(commands)))
                
                if choice.lower() == 'q':
                    break
                
                try:
                    cmd_num = int(choice)
                    if 1 <= cmd_num <= len(commands):
                        selected_cmd = commands[cmd_num - 1]
                        
                        console.print(f"\n[green]Executing:[/green] {selected_cmd['command']}")
                        console.print(f"[yellow]Description:[/yellow] {selected_cmd['description']}")
                        
                        if Confirm.ask("Proceed?"):
                            import subprocess
                            try:
                                result = subprocess.run(
                                    selected_cmd['command'], 
                                    shell=True, 
                                    capture_output=True, 
                                    text=True, 
                                    timeout=30
                                )
                                
                                if result.returncode == 0:
                                    console.print(f"\n[green]Command executed successfully:[/green]")
                                    console.print(Panel(result.stdout, title="Output", border_style="green"))
                                else:
                                    console.print(f"\n[red]Command failed:[/red]")
                                    console.print(Panel(result.stderr, title="Error", border_style="red"))
                                    
                            except subprocess.TimeoutExpired:
                                console.print(f"\n[red]Command timed out after 30 seconds[/red]")
                            except Exception as e:
                                console.print(f"\n[red]Error executing command: {e}[/red]")
                        else:
                            console.print("[yellow]Command execution cancelled[/yellow]")
                    else:
                        console.print(f"[red]Invalid command number. Please enter 1-{len(commands)}[/red]")
                except ValueError:
                    console.print("[red]Invalid input. Please enter a number or 'q'[/red]")
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]Command selection cancelled[/yellow]")
                break

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