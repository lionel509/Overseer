#!/usr/bin/env python3
"""
Command Processor Tool for Overseer CLI
Provides command execution, history management, and system operations
"""

import subprocess
import os
import sys
import json
import shlex
from typing import List, Dict, Any, Optional
from datetime import datetime
import psutil
import platform

class CommandProcessorTool:
    def __init__(self):
        self.command_history = []
        self.max_history_size = 100
        self.supported_commands = {
            'system_info': self._get_system_info,
            'memory_usage': self._get_memory_usage,
            'disk_usage': self._get_disk_usage,
            'network_status': self._get_network_status,
            'process_list': self._get_process_list,
            'file_search': self._file_search,
            'open_terminal': self._open_terminal,
            'start_monitoring': self._start_monitoring,
            'stop_monitoring': self._stop_monitoring,
            'get_metrics': self._get_metrics
        }
        
    def execute_command(self, command: str, args: List[str] = None) -> Dict[str, Any]:
        """
        Execute a command and return results
        
        Args:
            command: Command to execute
            args: Command arguments
            
        Returns:
            Dictionary with command results
        """
        try:
            args = args or []
            full_command = f"{command} {' '.join(args)}"
            
            # Add to history
            self._add_to_history(full_command, "pending")
            
            # Check if it's a built-in command
            if command in self.supported_commands:
                result = self.supported_commands[command](args)
                self._update_history(full_command, "completed", result)
                return result
            
            # Execute system command
            result = self._execute_system_command(command, args)
            self._update_history(full_command, "completed", result)
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "command": command,
                "args": args
            }
            self._update_history(full_command, "error", error_result)
            return error_result
    
    def _execute_system_command(self, command: str, args: List[str]) -> Dict[str, Any]:
        """Execute a system command using subprocess"""
        try:
            # Prepare command
            cmd_list = [command] + args
            
            # Execute command
            process = subprocess.run(
                cmd_list,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            return {
                "success": process.returncode == 0,
                "data": {
                    "stdout": process.stdout,
                    "stderr": process.stderr,
                    "returncode": process.returncode,
                    "command": cmd_list
                },
                "metadata": {
                    "execution_time": datetime.now().isoformat(),
                    "command_type": "system"
                }
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 30 seconds",
                "command": command,
                "args": args
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": f"Command not found: {command}",
                "command": command,
                "args": args
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command,
                "args": args
            }
    
    def _get_system_info(self, args: List[str]) -> Dict[str, Any]:
        """Get system information"""
        try:
            info = {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "hostname": platform.node(),
                "python_version": sys.version,
                "cpu_count": psutil.cpu_count(),
                "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
            }
            
            return {
                "success": True,
                "data": info,
                "metadata": {
                    "command_type": "system_info",
                    "execution_time": datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_memory_usage(self, args: List[str]) -> Dict[str, Any]:
        """Get memory usage information"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            info = {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "free": memory.free,
                "percent": memory.percent,
                "swap": {
                    "total": swap.total,
                    "used": swap.used,
                    "free": swap.free,
                    "percent": swap.percent
                }
            }
            
            return {
                "success": True,
                "data": info,
                "metadata": {
                    "command_type": "memory_usage",
                    "execution_time": datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_disk_usage(self, args: List[str]) -> Dict[str, Any]:
        """Get disk usage information"""
        try:
            partitions = psutil.disk_partitions()
            disk_info = []
            
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "filesystem": partition.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent
                    })
                except PermissionError:
                    continue
            
            return {
                "success": True,
                "data": disk_info,
                "metadata": {
                    "command_type": "disk_usage",
                    "execution_time": datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_network_status(self, args: List[str]) -> Dict[str, Any]:
        """Get network status information"""
        try:
            # Network interfaces
            interfaces = psutil.net_if_addrs()
            network_info = {}
            
            for interface, addresses in interfaces.items():
                network_info[interface] = []
                for addr in addresses:
                    network_info[interface].append({
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast
                    })
            
            # Network I/O counters
            io_counters = psutil.net_io_counters()
            
            # Network connections
            connections = []
            for conn in psutil.net_connections():
                if conn.status == 'ESTABLISHED':
                    connections.append({
                        "local_address": f"{conn.laddr.ip}:{conn.laddr.port}",
                        "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        "status": conn.status,
                        "pid": conn.pid
                    })
            
            return {
                "success": True,
                "data": {
                    "interfaces": network_info,
                    "io_counters": {
                        "bytes_sent": io_counters.bytes_sent,
                        "bytes_recv": io_counters.bytes_recv,
                        "packets_sent": io_counters.packets_sent,
                        "packets_recv": io_counters.packets_recv
                    },
                    "connections": connections
                },
                "metadata": {
                    "command_type": "network_status",
                    "execution_time": datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_process_list(self, args: List[str]) -> Dict[str, Any]:
        """Get list of running processes"""
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "username": proc.info['username'],
                        "cpu_percent": proc.info['cpu_percent'],
                        "memory_percent": proc.info['memory_percent'],
                        "status": proc.info['status']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            
            return {
                "success": True,
                "data": processes[:50],  # Return top 50 processes
                "metadata": {
                    "command_type": "process_list",
                    "total_processes": len(processes),
                    "execution_time": datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _file_search(self, args: List[str]) -> Dict[str, Any]:
        """File search command"""
        try:
            from .file_search_tool import FileSearchTool
            
            tool = FileSearchTool()
            query = args[0] if args else "*"
            base_path = args[1] if len(args) > 1 else "/"
            filters = json.loads(args[2]) if len(args) > 2 else {}
            
            result = tool.search_files(query, base_path, filters)
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _open_terminal(self, args: List[str]) -> Dict[str, Any]:
        """Open terminal command"""
        try:
            if platform.system() == "Darwin":  # macOS
                subprocess.run(["open", "-a", "Terminal"])
            elif platform.system() == "Windows":
                subprocess.run(["cmd", "/c", "start", "cmd"])
            else:  # Linux
                subprocess.run(["gnome-terminal", "--"])
            
            return {
                "success": True,
                "data": {"message": "Terminal opened"},
                "metadata": {
                    "command_type": "open_terminal",
                    "execution_time": datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _start_monitoring(self, args: List[str]) -> Dict[str, Any]:
        """Start system monitoring"""
        try:
            return {
                "success": True,
                "data": {"message": "System monitoring started"},
                "metadata": {
                    "command_type": "start_monitoring",
                    "execution_time": datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _stop_monitoring(self, args: List[str]) -> Dict[str, Any]:
        """Stop system monitoring"""
        try:
            return {
                "success": True,
                "data": {"message": "System monitoring stopped"},
                "metadata": {
                    "command_type": "stop_monitoring",
                    "execution_time": datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_metrics(self, args: List[str]) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "timestamp": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "data": metrics,
                "metadata": {
                    "command_type": "get_metrics",
                    "execution_time": datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _add_to_history(self, command: str, status: str):
        """Add command to history"""
        self.command_history.append({
            "command": command,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "result": None
        })
        
        # Keep only recent commands
        if len(self.command_history) > self.max_history_size:
            self.command_history = self.command_history[-self.max_history_size:]
    
    def _update_history(self, command: str, status: str, result: Dict[str, Any]):
        """Update command history with result"""
        for entry in self.command_history:
            if entry["command"] == command and entry["status"] == "pending":
                entry["status"] = status
                entry["result"] = result
                break
    
    def get_command_history(self) -> List[Dict[str, Any]]:
        """Get command history"""
        return self.command_history
    
    def clear_command_history(self):
        """Clear command history"""
        self.command_history = []
    
    def get_supported_commands(self) -> List[str]:
        """Get list of supported commands"""
        return list(self.supported_commands.keys())

def main():
    """CLI interface for command processor tool"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Command Processor Tool")
    parser.add_argument("command", help="Command to execute")
    parser.add_argument("args", nargs="*", help="Command arguments")
    parser.add_argument("--history", action="store_true", help="Show command history")
    parser.add_argument("--clear-history", action="store_true", help="Clear command history")
    parser.add_argument("--supported", action="store_true", help="Show supported commands")
    
    args = parser.parse_args()
    
    tool = CommandProcessorTool()
    
    if args.history:
        history = tool.get_command_history()
        print("Command History:")
        for entry in history[-10:]:  # Show last 10
            print(f"  {entry['timestamp']}: {entry['command']} ({entry['status']})")
        return
    
    if args.clear_history:
        tool.clear_command_history()
        print("Command history cleared")
        return
    
    if args.supported:
        commands = tool.get_supported_commands()
        print("Supported Commands:")
        for cmd in commands:
            print(f"  {cmd}")
        return
    
    # Execute command
    result = tool.execute_command(args.command, args.args)
    
    if result["success"]:
        print("Command executed successfully")
        if "data" in result:
            print(json.dumps(result["data"], indent=2))
    else:
        print(f"Command failed: {result['error']}")

if __name__ == "__main__":
    main() 