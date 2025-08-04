#!/usr/bin/env python3
"""
Overseer Desktop Backend Integration

This script provides a bridge between the Electron desktop application
and the Overseer Python backend system. It handles IPC communication
and provides a clean API for the desktop app to interact with the
Python backend services.
"""

import sys
import json
import subprocess
import os
import signal
import threading
import time
from typing import Dict, Any, Optional, List
import logging

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

try:
    from cli.overseer_cli import OverseerCLI
    from cli.core.core_logic import CoreLogic
    from cli.features.ai_organization.file_search import FileSearch
    from cli.features.ai_monitoring.system_monitor import SystemMonitor
    from cli.features.ai_performance.advanced_process_manager import AdvancedProcessManager
    from cli.tools import FileSearchTool, CommandProcessorTool, ToolRecommenderTool, RealTimeStatsTool
except ImportError as e:
    print(f"Warning: Could not import Overseer modules: {e}")
    print("Running in standalone mode...")

class DesktopBackendIntegration:
    """
    Integration layer between Electron desktop app and Python backend
    """
    
    def __init__(self):
        self.cli = None
        self.core_logic = None
        self.file_search = None
        self.system_monitor = None
        self.process_manager = None
        self.is_running = False
        
        # Initialize new tools
        self.file_search_tool = None
        self.command_processor_tool = None
        self.tool_recommender_tool = None
        self.real_time_stats_tool = None
        
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all backend components"""
        try:
            # Initialize CLI
            self.cli = OverseerCLI()
            
            # Initialize core logic
            self.core_logic = CoreLogic()
            
            # Initialize file search
            self.file_search = FileSearch()
            
            # Initialize system monitor
            self.system_monitor = SystemMonitor()
            
            # Initialize process manager
            self.process_manager = AdvancedProcessManager()
            
            # Initialize new tools
            self.file_search_tool = FileSearchTool()
            self.command_processor_tool = CommandProcessorTool()
            self.tool_recommender_tool = ToolRecommenderTool()
            self.real_time_stats_tool = RealTimeStatsTool()
            
            self.logger.info("All backend components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            # Continue with limited functionality
    
    def handle_command(self, command: str, args: List[Any] = None) -> Dict[str, Any]:
        """
        Handle commands from the Electron app
        
        Args:
            command: Command name
            args: Command arguments
            
        Returns:
            Response dictionary
        """
        try:
            self.logger.info(f"Handling command: {command} with args: {args}")
            
            if command == "system_info":
                return self._get_system_info()
            elif command == "file_search":
                return self._search_files(args[0] if args else "")
            elif command == "process_list":
                return self._get_process_list()
            elif command == "network_status":
                return self._get_network_status()
            elif command == "disk_usage":
                return self._get_disk_usage()
            elif command == "memory_usage":
                return self._get_memory_usage()
            elif command == "open_terminal":
                return self._open_terminal()
            elif command == "start_monitoring":
                return self._start_monitoring()
            elif command == "stop_monitoring":
                return self._stop_monitoring()
            elif command == "get_metrics":
                return self._get_metrics()
            elif command == "tool_recommendations":
                return self._get_tool_recommendations()
            elif command == "start_real_time_monitoring":
                return self._start_real_time_monitoring()
            elif command == "stop_real_time_monitoring":
                return self._stop_real_time_monitoring()
            elif command == "get_real_time_stats":
                return self._get_real_time_stats()
            elif command == "execute_command":
                return self._execute_command(args[0] if args else "", args[1:] if len(args) > 1 else [])
            else:
                return {
                    "success": False,
                    "error": f"Unknown command: {command}"
                }
                
        except Exception as e:
            self.logger.error(f"Error handling command {command}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            import platform
            import psutil
            
            info = {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "disk_partitions": len(psutil.disk_partitions())
            }
            
            return {
                "success": True,
                "data": info
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get system info: {e}"
            }
    
    def _search_files(self, query: str) -> Dict[str, Any]:
        """Search for files"""
        try:
            if not self.file_search:
                return {
                    "success": False,
                    "error": "File search component not available"
                }
            
            results = self.file_search.search_files(query)
            return {
                "success": True,
                "data": results
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to search files: {e}"
            }
    
    def _get_process_list(self) -> Dict[str, Any]:
        """Get list of running processes"""
        try:
            import psutil
            
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return {
                "success": True,
                "data": processes
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get process list: {e}"
            }
    
    def _get_network_status(self) -> Dict[str, Any]:
        """Get network status"""
        try:
            import psutil
            
            network_info = {
                "interfaces": psutil.net_if_addrs(),
                "connections": len(psutil.net_connections()),
                "io_counters": psutil.net_io_counters()._asdict()
            }
            
            return {
                "success": True,
                "data": network_info
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get network status: {e}"
            }
    
    def _get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage information"""
        try:
            import psutil
            
            disk_info = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent
                    })
                except PermissionError:
                    pass
            
            return {
                "success": True,
                "data": disk_info
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get disk usage: {e}"
            }
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage information"""
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            memory_info = {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent,
                "free": memory.free
            }
            
            return {
                "success": True,
                "data": memory_info
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get memory usage: {e}"
            }
    
    def _open_terminal(self) -> Dict[str, Any]:
        """Open system terminal"""
        try:
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                subprocess.Popen(["cmd"], shell=True)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", "-a", "Terminal"])
            else:  # Linux
                subprocess.Popen(["gnome-terminal"])
            
            return {
                "success": True,
                "data": "Terminal opened successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to open terminal: {e}"
            }
    
    def _start_monitoring(self) -> Dict[str, Any]:
        """Start system monitoring"""
        try:
            if self.system_monitor:
                self.system_monitor.start_monitoring()
                self.is_running = True
                return {
                    "success": True,
                    "data": "Monitoring started"
                }
            else:
                return {
                    "success": False,
                    "error": "System monitor not available"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to start monitoring: {e}"
            }
    
    def _stop_monitoring(self) -> Dict[str, Any]:
        """Stop system monitoring"""
        try:
            if self.system_monitor:
                self.system_monitor.stop_monitoring()
                self.is_running = False
                return {
                    "success": True,
                    "data": "Monitoring stopped"
                }
            else:
                return {
                    "success": False,
                    "error": "System monitor not available"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to stop monitoring: {e}"
            }
    
    def _get_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            import psutil
            
            metrics = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "network_io": psutil.net_io_counters()._asdict()
            }
            
            return {
                "success": True,
                "data": metrics
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get metrics: {e}"
            }
    
    def _get_tool_recommendations(self) -> Dict[str, Any]:
        """Get tool recommendations"""
        try:
            if not self.tool_recommender_tool:
                return {
                    "success": False,
                    "error": "Tool recommender not available"
                }
            
            result = self.tool_recommender_tool.generate_recommendations()
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get tool recommendations: {e}"
            }
    
    def _start_real_time_monitoring(self) -> Dict[str, Any]:
        """Start real-time monitoring"""
        try:
            if not self.real_time_stats_tool:
                return {
                    "success": False,
                    "error": "Real-time stats tool not available"
                }
            
            result = self.real_time_stats_tool.start_monitoring()
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to start real-time monitoring: {e}"
            }
    
    def _stop_real_time_monitoring(self) -> Dict[str, Any]:
        """Stop real-time monitoring"""
        try:
            if not self.real_time_stats_tool:
                return {
                    "success": False,
                    "error": "Real-time stats tool not available"
                }
            
            result = self.real_time_stats_tool.stop_monitoring()
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to stop real-time monitoring: {e}"
            }
    
    def _get_real_time_stats(self) -> Dict[str, Any]:
        """Get real-time statistics"""
        try:
            if not self.real_time_stats_tool:
                return {
                    "success": False,
                    "error": "Real-time stats tool not available"
                }
            
            stats = self.real_time_stats_tool.get_current_stats()
            return {
                "success": True,
                "data": stats
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get real-time stats: {e}"
            }
    
    def _execute_command(self, command: str, args: List[str]) -> Dict[str, Any]:
        """Execute a command using the command processor"""
        try:
            if not self.command_processor_tool:
                return {
                    "success": False,
                    "error": "Command processor not available"
                }
            
            result = self.command_processor_tool.execute_command(command, args)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to execute command: {e}"
            }

def main():
    """Main function for IPC communication"""
    integration = DesktopBackendIntegration()
    
    def signal_handler(signum, frame):
        """Handle shutdown signals"""
        print("Shutting down desktop backend integration...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("Desktop backend integration started")
    print("Ready to receive commands from Electron app")
    
    # Main loop for IPC communication
    while True:
        try:
            # Read command from stdin
            line = input()
            if not line:
                continue
            
            # Parse JSON command
            try:
                data = json.loads(line)
                command = data.get('command')
                args = data.get('args', [])
                
                # Handle command
                response = integration.handle_command(command, args)
                
                # Send response
                print(json.dumps(response))
                
            except json.JSONDecodeError:
                print(json.dumps({
                    "success": False,
                    "error": "Invalid JSON format"
                }))
                
        except EOFError:
            break
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(json.dumps({
                "success": False,
                "error": f"Unexpected error: {e}"
            }))

if __name__ == "__main__":
    main() 