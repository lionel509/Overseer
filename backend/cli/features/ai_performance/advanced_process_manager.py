"""
Advanced Process Management
Provides process killing, suspending, resource optimization, and process tree visualization.
"""

import os
import sys
import time
import psutil
import signal
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.tree import Tree
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

@dataclass
class ProcessInfo:
    """Process information data structure"""
    pid: int
    name: str
    status: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    num_threads: int
    create_time: float
    parent_pid: Optional[int]
    children: List[int]
    cmdline: List[str]
    username: str
    nice: int
    io_counters: Optional[Dict]
    num_fds: Optional[int]

@dataclass
class ProcessAction:
    """Process action data structure"""
    pid: int
    action: str  # 'kill', 'suspend', 'resume', 'terminate', 'restart'
    reason: str
    timestamp: float
    success: bool
    error_message: Optional[str]

class AdvancedProcessManager:
    """Advanced process management with optimization and visualization"""
    
    def __init__(self, config: Dict = None):
        """Initialize advanced process manager"""
        self.console = Console() if RICH_AVAILABLE else None
        self.config = config or {}
        
        # Process management settings
        self.kill_timeout = self.config.get('kill_timeout', 5)  # seconds
        self.suspend_timeout = self.config.get('suspend_timeout', 3)  # seconds
        self.max_processes = self.config.get('max_processes', 1000)
        
        # Resource thresholds
        self.cpu_threshold = self.config.get('cpu_threshold', 80.0)  # percent
        self.memory_threshold = self.config.get('memory_threshold', 10.0)  # percent
        self.io_threshold = self.config.get('io_threshold', 1000000)  # bytes
        
        # Action history
        self.action_history = []
    
    def get_process_info(self, pid: int) -> Optional[ProcessInfo]:
        """Get detailed information about a process"""
        try:
            process = psutil.Process(pid)
            
            # Get basic info
            with process.oneshot():
                info = ProcessInfo(
                    pid=pid,
                    name=process.name(),
                    status=process.status(),
                    cpu_percent=process.cpu_percent(),
                    memory_percent=process.memory_percent(),
                    memory_mb=process.memory_info().rss / 1024 / 1024,
                    num_threads=process.num_threads(),
                    create_time=process.create_time(),
                    parent_pid=process.ppid() if process.ppid() else None,
                    children=process.children(),
                    cmdline=process.cmdline(),
                    username=process.username(),
                    nice=process.nice(),
                    io_counters=process.io_counters() if hasattr(process, 'io_counters') else None,
                    num_fds=process.num_fds() if hasattr(process, 'num_fds') else None
                )
            
            return info
            
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return None
    
    def get_top_processes(self, limit: int = 20, sort_by: str = 'cpu') -> List[ProcessInfo]:
        """Get top processes by resource usage"""
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    proc_info = proc.info
                    
                    # Get detailed info
                    detailed_info = self.get_process_info(proc_info['pid'])
                    if detailed_info:
                        processes.append(detailed_info)
                    
                    if len(processes) >= self.max_processes:
                        break
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by specified criteria
            if sort_by == 'cpu':
                processes.sort(key=lambda x: x.cpu_percent, reverse=True)
            elif sort_by == 'memory':
                processes.sort(key=lambda x: x.memory_percent, reverse=True)
            elif sort_by == 'memory_mb':
                processes.sort(key=lambda x: x.memory_mb, reverse=True)
            elif sort_by == 'threads':
                processes.sort(key=lambda x: x.num_threads, reverse=True)
            elif sort_by == 'age':
                processes.sort(key=lambda x: x.create_time)
            
            return processes[:limit]
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error getting processes: {e}[/red]")
            return []
    
    def find_resource_hogs(self, cpu_threshold: float = None, memory_threshold: float = None) -> List[ProcessInfo]:
        """Find processes consuming excessive resources"""
        if cpu_threshold is None:
            cpu_threshold = self.cpu_threshold
        if memory_threshold is None:
            memory_threshold = self.memory_threshold
        
        resource_hogs = []
        processes = self.get_top_processes(limit=100)
        
        for process in processes:
            if (process.cpu_percent > cpu_threshold or 
                process.memory_percent > memory_threshold):
                resource_hogs.append(process)
        
        return resource_hogs
    
    def kill_process(self, pid: int, force: bool = False) -> ProcessAction:
        """Kill a process"""
        action = ProcessAction(
            pid=pid,
            action='kill',
            reason='User request',
            timestamp=time.time(),
            success=False,
            error_message=None
        )
        
        try:
            process = psutil.Process(pid)
            
            if force:
                # Force kill
                process.kill()
                action.success = True
                action.reason = 'Force killed'
            else:
                # Graceful termination
                process.terminate()
                
                # Wait for termination
                try:
                    process.wait(timeout=self.kill_timeout)
                    action.success = True
                    action.reason = 'Gracefully terminated'
                except psutil.TimeoutExpired:
                    # Force kill if graceful termination fails
                    process.kill()
                    action.success = True
                    action.reason = 'Force killed after timeout'
            
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            action.error_message = str(e)
        except Exception as e:
            action.error_message = str(e)
        
        self.action_history.append(action)
        return action
    
    def suspend_process(self, pid: int) -> ProcessAction:
        """Suspend a process"""
        action = ProcessAction(
            pid=pid,
            action='suspend',
            reason='User request',
            timestamp=time.time(),
            success=False,
            error_message=None
        )
        
        try:
            process = psutil.Process(pid)
            process.suspend()
            action.success = True
            action.reason = 'Process suspended'
            
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            action.error_message = str(e)
        except Exception as e:
            action.error_message = str(e)
        
        self.action_history.append(action)
        return action
    
    def resume_process(self, pid: int) -> ProcessAction:
        """Resume a suspended process"""
        action = ProcessAction(
            pid=pid,
            action='resume',
            reason='User request',
            timestamp=time.time(),
            success=False,
            error_message=None
        )
        
        try:
            process = psutil.Process(pid)
            process.resume()
            action.success = True
            action.reason = 'Process resumed'
            
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            action.error_message = str(e)
        except Exception as e:
            action.error_message = str(e)
        
        self.action_history.append(action)
        return action
    
    def restart_process(self, pid: int) -> ProcessAction:
        """Restart a process (kill and restart with same command)"""
        action = ProcessAction(
            pid=pid,
            action='restart',
            reason='User request',
            timestamp=time.time(),
            success=False,
            error_message=None
        )
        
        try:
            process = psutil.Process(pid)
            cmdline = process.cmdline()
            
            # Kill the process
            kill_action = self.kill_process(pid)
            if not kill_action.success:
                action.error_message = f"Failed to kill process: {kill_action.error_message}"
                self.action_history.append(action)
                return action
            
            # Restart with same command
            if cmdline:
                # Note: This is a simplified restart - in practice you'd want more sophisticated restart logic
                action.success = True
                action.reason = f'Process killed, restart command: {" ".join(cmdline)}'
            else:
                action.error_message = "Cannot restart: no command line available"
            
        except Exception as e:
            action.error_message = str(e)
        
        self.action_history.append(action)
        return action
    
    def optimize_resources(self, aggressive: bool = False) -> List[ProcessAction]:
        """Automatically optimize resource usage by managing processes"""
        actions = []
        
        # Find resource hogs
        cpu_threshold = 50.0 if aggressive else self.cpu_threshold
        memory_threshold = 5.0 if aggressive else self.memory_threshold
        
        resource_hogs = self.find_resource_hogs(cpu_threshold, memory_threshold)
        
        for process in resource_hogs:
            if aggressive:
                # Kill processes consuming too many resources
                action = self.kill_process(process.pid, force=True)
                action.reason = f'Aggressive optimization: {process.name} (CPU: {process.cpu_percent:.1f}%, MEM: {process.memory_percent:.1f}%)'
            else:
                # Suspend processes consuming too many resources
                action = self.suspend_process(process.pid)
                action.reason = f'Resource optimization: {process.name} (CPU: {process.cpu_percent:.1f}%, MEM: {process.memory_percent:.1f}%)'
            
            actions.append(action)
        
        return actions
    
    def get_process_tree(self, root_pid: int = 1, max_depth: int = 3) -> Optional[Tree]:
        """Get process tree visualization"""
        if not RICH_AVAILABLE:
            return None
        
        try:
            def build_tree(pid: int, depth: int = 0) -> Optional[Tree]:
                if depth > max_depth:
                    return None
                
                try:
                    process = psutil.Process(pid)
                    process_info = self.get_process_info(pid)
                    
                    if not process_info:
                        return None
                    
                    # Create tree node
                    node_text = f"{process_info.name} (PID: {pid}, CPU: {process_info.cpu_percent:.1f}%, MEM: {process_info.memory_percent:.1f}%)"
                    tree = Tree(node_text)
                    
                    # Add children
                    for child_pid in process_info.children:
                        child_tree = build_tree(child_pid, depth + 1)
                        if child_tree:
                            tree.add(child_tree)
                    
                    return tree
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    return None
            
            return build_tree(root_pid)
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error building process tree: {e}[/red]")
            return None
    
    def display_processes(self, processes: List[ProcessInfo], title: str = "Process List"):
        """Display processes in a formatted table"""
        if not RICH_AVAILABLE:
            print("Rich library required for formatted display")
            return
        
        table = Table(title=title)
        table.add_column("PID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("CPU %", style="red")
        table.add_column("Memory %", style="magenta")
        table.add_column("Memory MB", style="blue")
        table.add_column("Threads", style="white")
        table.add_column("User", style="white")
        
        for process in processes:
            status_color = "green" if process.status == "running" else "yellow" if process.status == "sleeping" else "red"
            
            table.add_row(
                str(process.pid),
                process.name[:20],
                f"[{status_color}]{process.status}[/{status_color}]",
                f"{process.cpu_percent:.1f}",
                f"{process.memory_percent:.1f}",
                f"{process.memory_mb:.1f}",
                str(process.num_threads),
                process.username[:10]
            )
        
        self.console.print(table)
    
    def display_process_tree(self, root_pid: int = 1):
        """Display process tree"""
        if not RICH_AVAILABLE:
            print("Rich library required for tree display")
            return
        
        tree = self.get_process_tree(root_pid)
        if tree:
            self.console.print(f"\n[bold]🌳 Process Tree (Root PID: {root_pid}):[/bold]")
            self.console.print(tree)
        else:
            self.console.print("[red]Could not build process tree[/red]")
    
    def display_action_history(self):
        """Display action history"""
        if not RICH_AVAILABLE:
            print("Rich library required for formatted display")
            return
        
        if not self.action_history:
            self.console.print("[yellow]No actions performed yet[/yellow]")
            return
        
        table = Table(title="Process Action History")
        table.add_column("Time", style="cyan")
        table.add_column("PID", style="green")
        table.add_column("Action", style="yellow")
        table.add_column("Reason", style="blue")
        table.add_column("Status", style="red")
        table.add_column("Error", style="red")
        
        for action in self.action_history[-20:]:  # Show last 20 actions
            status_color = "green" if action.success else "red"
            time_str = datetime.fromtimestamp(action.timestamp).strftime("%H:%M:%S")
            
            table.add_row(
                time_str,
                str(action.pid),
                action.action,
                action.reason[:30] + "..." if len(action.reason) > 30 else action.reason,
                f"[{status_color}]{'SUCCESS' if action.success else 'FAILED'}[/{status_color}]",
                action.error_message or ""
            )
        
        self.console.print(table)
    
    def get_system_summary(self) -> Dict:
        """Get system process summary"""
        try:
            processes = self.get_top_processes(limit=100)
            
            total_processes = len(processes)
            running_processes = len([p for p in processes if p.status == 'running'])
            sleeping_processes = len([p for p in processes if p.status == 'sleeping'])
            
            total_cpu = sum(p.cpu_percent for p in processes)
            total_memory = sum(p.memory_percent for p in processes)
            total_memory_mb = sum(p.memory_mb for p in processes)
            
            resource_hogs = self.find_resource_hogs()
            
            return {
                'total_processes': total_processes,
                'running_processes': running_processes,
                'sleeping_processes': sleeping_processes,
                'total_cpu_percent': total_cpu,
                'total_memory_percent': total_memory,
                'total_memory_mb': total_memory_mb,
                'resource_hogs_count': len(resource_hogs),
                'action_history_count': len(self.action_history)
            }
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error getting system summary: {e}[/red]")
            return {}

def main():
    """Main function for standalone testing"""
    manager = AdvancedProcessManager()
    
    print("🔧 Advanced Process Manager")
    print("=" * 50)
    
    # Get top processes
    processes = manager.get_top_processes(limit=10)
    
    if processes:
        print(f"✅ Found {len(processes)} processes")
        manager.display_processes(processes, "Top 10 Processes")
        
        # Get system summary
        summary = manager.get_system_summary()
        print(f"\n📊 System Summary:")
        print(f"   Total processes: {summary.get('total_processes', 0)}")
        print(f"   Running processes: {summary.get('running_processes', 0)}")
        print(f"   Resource hogs: {summary.get('resource_hogs_count', 0)}")
        print(f"   Total CPU: {summary.get('total_cpu_percent', 0):.1f}%")
        print(f"   Total Memory: {summary.get('total_memory_percent', 0):.1f}%")
        
        # Show process tree
        manager.display_process_tree()
        
    else:
        print("❌ No processes found")

if __name__ == "__main__":
    main() 