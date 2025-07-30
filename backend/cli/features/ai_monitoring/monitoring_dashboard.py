"""
Terminal-based Monitoring Dashboard
A 'top'-like interface for real-time system monitoring, alerts, and tool recommendations.
"""

import os
import sys
import time
import signal
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import curses
    CURSES_AVAILABLE = True
except ImportError:
    CURSES_AVAILABLE = False

from system_monitor import SystemMonitor
from enhanced_tool_recommender import EnhancedToolRecommender
from alert_manager import AlertManager, AlertSeverity

@dataclass
class DashboardState:
    """State management for the dashboard"""
    current_view: str = "overview"  # overview, alerts, tools, processes
    refresh_rate: int = 2  # seconds
    show_help: bool = False
    paused: bool = False
    sort_by: str = "cpu"  # cpu, memory, name
    sort_reverse: bool = True
    selected_process: Optional[int] = None
    filter_text: str = ""

class MonitoringDashboard:
    """Terminal-based monitoring dashboard similar to 'top'"""
    
    def __init__(self, config: Dict = None):
        """Initialize the monitoring dashboard"""
        if not PSUTIL_AVAILABLE:
            raise RuntimeError("psutil is required for monitoring dashboard")
        if not CURSES_AVAILABLE:
            raise RuntimeError("curses is required for terminal interface")
        
        self.config = config or {}
        self.state = DashboardState()
        
        # Initialize components
        self.system_monitor = SystemMonitor()
        self.tool_recommender = EnhancedToolRecommender(system_monitor=self.system_monitor)
        self.alert_manager = AlertManager()
        
        # Dashboard data
        self.metrics = None
        self.alerts = []
        self.processes = []
        self.recommendations = []
        self.last_update = 0
        
        # Threading for background updates
        self.running = False
        self.update_thread = None
        
        # Signal handling
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle termination signals"""
        self.running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1)
        sys.exit(0)
    
    def _update_data(self):
        """Update dashboard data in background"""
        try:
            # Update system metrics
            self.metrics = self.system_monitor.collect_metrics()
            
            # Update alerts
            if self.metrics:
                alerts = self.alert_manager.check_metrics({
                    'cpu_percent': self.metrics.cpu_percent,
                    'memory_percent': self.metrics.memory_percent,
                    'disk_percent': self.metrics.disk_percent,
                    'temperature': self.metrics.temperature or 0.0
                })
                if alerts:
                    self.alert_manager.save_alerts(alerts)
                    self.alerts.extend(alerts)
            
            # Update processes
            self.processes = self._get_top_processes()
            
            # Update recommendations if there are alerts
            if self.alerts and len(self.alerts) > 0:
                latest_alert = self.alerts[-1]
                query = f"fix {latest_alert.metric_name} {latest_alert.alert_type}"
                self.recommendations = self.tool_recommender.recommend_tools(query)
            
            self.last_update = time.time()
            
        except Exception as e:
            # Log error but don't crash
            pass
    
    def _get_top_processes(self, limit: int = 20) -> List[Dict]:
        """Get top processes by resource usage"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] > 0 or proc_info['memory_percent'] > 0:
                        processes.append({
                            'pid': proc_info['pid'],
                            'name': proc_info['name'][:20],
                            'cpu_percent': proc_info['cpu_percent'],
                            'memory_percent': proc_info['memory_percent'],
                            'status': proc_info['status']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by current sort criteria
            reverse = self.state.sort_reverse
            if self.state.sort_by == 'cpu':
                processes.sort(key=lambda x: x['cpu_percent'], reverse=reverse)
            elif self.state.sort_by == 'memory':
                processes.sort(key=lambda x: x['memory_percent'], reverse=reverse)
            elif self.state.sort_by == 'name':
                processes.sort(key=lambda x: x['name'].lower(), reverse=reverse)
            
            return processes[:limit]
            
        except Exception:
            return []
    
    def _draw_header(self, stdscr, max_y: int, max_x: int):
        """Draw the dashboard header"""
        # Title
        title = "Overseer System Monitor Dashboard"
        stdscr.addstr(0, (max_x - len(title)) // 2, title, curses.A_BOLD)
        
        # Status bar
        status_line = f"View: {self.state.current_view.upper()} | "
        status_line += f"Refresh: {self.state.refresh_rate}s | "
        status_line += f"Sort: {self.state.sort_by.upper()}"
        if self.state.paused:
            status_line += " | PAUSED"
        
        stdscr.addstr(1, 0, status_line, curses.A_REVERSE)
        
        # Last update time
        update_time = datetime.fromtimestamp(self.last_update).strftime("%H:%M:%S")
        stdscr.addstr(1, max_x - len(update_time) - 1, update_time)
    
    def _draw_overview(self, stdscr, max_y: int, max_x: int):
        """Draw the overview screen"""
        if not self.metrics:
            stdscr.addstr(3, 0, "No metrics available")
            return
        
        # System metrics section
        stdscr.addstr(3, 0, "System Metrics", curses.A_BOLD)
        
        # CPU
        cpu_color = curses.color_pair(1) if self.metrics.cpu_percent < 70 else curses.color_pair(2)
        stdscr.addstr(4, 0, f"CPU Usage: {self.metrics.cpu_percent:6.1f}%", cpu_color)
        
        # Memory
        mem_color = curses.color_pair(1) if self.metrics.memory_percent < 80 else curses.color_pair(2)
        stdscr.addstr(5, 0, f"Memory:    {self.metrics.memory_percent:6.1f}% ({self.metrics.memory_used_gb:.1f}GB / {self.metrics.memory_total_gb:.1f}GB)", mem_color)
        
        # Disk
        disk_color = curses.color_pair(1) if self.metrics.disk_percent < 85 else curses.color_pair(2)
        stdscr.addstr(6, 0, f"Disk:      {self.metrics.disk_percent:6.1f}% ({self.metrics.disk_used_gb:.1f}GB / {self.metrics.disk_total_gb:.1f}GB)", disk_color)
        
        # Network
        stdscr.addstr(7, 0, f"Network:   Sent: {self.metrics.network_sent_mb:.1f}MB, Recv: {self.metrics.network_recv_mb:.1f}MB")
        
        # Processes
        stdscr.addstr(8, 0, f"Processes: {self.metrics.process_count}")
        
        # Load average
        stdscr.addstr(9, 0, f"Load Avg:  {self.metrics.load_average[0]:.2f}, {self.metrics.load_average[1]:.2f}, {self.metrics.load_average[2]:.2f}")
        
        # Temperature (if available)
        if self.metrics.temperature:
            temp_color = curses.color_pair(1) if self.metrics.temperature < 70 else curses.color_pair(2)
            stdscr.addstr(10, 0, f"Temperature: {self.metrics.temperature:.1f}°C", temp_color)
        
        # Battery (if available)
        if self.metrics.battery_percent is not None:
            battery_icon = "🔌" if self.metrics.battery_plugged else "🔋"
            stdscr.addstr(11, 0, f"Battery: {self.metrics.battery_percent:.1f}% {battery_icon}")
        
        # Health score
        health_score = self.system_monitor.get_system_summary()['health_score']
        health_color = curses.color_pair(1) if health_score > 70 else curses.color_pair(2)
        stdscr.addstr(12, 0, f"Health Score: {health_score}/100", health_color)
        
        # Recent alerts
        if self.alerts:
            stdscr.addstr(14, 0, "Recent Alerts:", curses.A_BOLD)
            for i, alert in enumerate(self.alerts[-3:]):  # Show last 3 alerts
                alert_color = curses.color_pair(2) if alert.severity == AlertSeverity.CRITICAL else curses.color_pair(3)
                alert_text = f"  {alert.alert_type}: {alert.metric_value:.1f} (threshold: {alert.threshold:.1f})"
                stdscr.addstr(15 + i, 0, alert_text, alert_color)
    
    def _draw_processes(self, stdscr, max_y: int, max_x: int):
        """Draw the processes screen"""
        # Header
        header = f"{'PID':>6} {'NAME':<20} {'CPU%':>6} {'MEM%':>6} {'STATUS':<10}"
        stdscr.addstr(3, 0, header, curses.A_BOLD)
        
        # Process list
        start_y = 4
        for i, proc in enumerate(self.processes):
            if start_y + i >= max_y - 2:
                break
            
            # Highlight selected process
            attr = curses.A_REVERSE if proc['pid'] == self.state.selected_process else curses.A_NORMAL
            
            # Color based on resource usage
            color = curses.color_pair(1)
            if proc['cpu_percent'] > 50 or proc['memory_percent'] > 10:
                color = curses.color_pair(2)
            
            line = f"{proc['pid']:>6} {proc['name']:<20} {proc['cpu_percent']:>6.1f} {proc['memory_percent']:>6.1f} {proc['status']:<10}"
            stdscr.addstr(start_y + i, 0, line, attr | color)
    
    def _draw_alerts(self, stdscr, max_y: int, max_x: int):
        """Draw the alerts screen"""
        # Header
        header = f"{'TIME':<8} {'TYPE':<15} {'METRIC':<12} {'VALUE':>8} {'THRESHOLD':>10} {'SEVERITY':<10}"
        stdscr.addstr(3, 0, header, curses.A_BOLD)
        
        # Alert list
        start_y = 4
        for i, alert in enumerate(self.alerts[-max_y + 6:]):  # Show recent alerts
            if start_y + i >= max_y - 2:
                break
            
            # Color based on severity
            color = curses.color_pair(1)
            if alert.severity == AlertSeverity.CRITICAL:
                color = curses.color_pair(2)
            elif alert.severity == AlertSeverity.WARNING:
                color = curses.color_pair(3)
            
            time_str = datetime.fromtimestamp(alert.timestamp).strftime("%H:%M:%S")
            line = f"{time_str:<8} {alert.alert_type:<15} {alert.metric_name:<12} {alert.metric_value:>8.1f} {alert.threshold:>10.1f} {alert.severity.value.upper():<10}"
            stdscr.addstr(start_y + i, 0, line, color)
    
    def _draw_tools(self, stdscr, max_y: int, max_x: int):
        """Draw the tool recommendations screen"""
        # Header
        header = f"{'TOOL':<15} {'CATEGORY':<12} {'CONFIDENCE':>10} {'REASON':<30}"
        stdscr.addstr(3, 0, header, curses.A_BOLD)
        
        # Recommendations list
        start_y = 4
        for i, rec in enumerate(self.recommendations):
            if start_y + i >= max_y - 2:
                break
            
            # Color based on confidence
            color = curses.color_pair(1)
            if rec.confidence_score > 0.8:
                color = curses.color_pair(2)
            elif rec.confidence_score > 0.6:
                color = curses.color_pair(3)
            
            line = f"{rec.name:<15} {rec.category:<12} {rec.confidence_score:>10.1%} {rec.reason:<30}"
            stdscr.addstr(start_y + i, 0, line, color)
    
    def _draw_help(self, stdscr, max_y: int, max_x: int):
        """Draw the help screen"""
        help_text = [
            "Overseer System Monitor Dashboard - Help",
            "",
            "Navigation:",
            "  Tab          - Switch between views (overview, processes, alerts, tools)",
            "  Space        - Pause/resume updates",
            "  q            - Quit",
            "  h            - Show/hide this help",
            "",
            "Process View:",
            "  Up/Down      - Navigate processes",
            "  Enter        - Select process",
            "  c            - Sort by CPU usage",
            "  m            - Sort by memory usage",
            "  n            - Sort by name",
            "  r            - Reverse sort order",
            "",
            "General:",
            "  +/-          - Increase/decrease refresh rate",
            "  f            - Filter processes (type to filter)",
            "",
            "Press any key to return to dashboard"
        ]
        
        for i, line in enumerate(help_text):
            if 3 + i < max_y - 1:
                stdscr.addstr(3 + i, 0, line)
    
    def _handle_input(self, stdscr, key: int) -> bool:
        """Handle user input"""
        if key == ord('q'):
            return False  # Quit
        
        elif key == ord('\t'):
            # Switch views
            views = ['overview', 'processes', 'alerts', 'tools']
            current_idx = views.index(self.state.current_view)
            self.state.current_view = views[(current_idx + 1) % len(views)]
        
        elif key == ord(' '):
            # Pause/resume
            self.state.paused = not self.state.paused
        
        elif key == ord('h'):
            # Toggle help
            self.state.show_help = not self.state.show_help
        
        elif key == ord('+') or key == ord('='):
            # Increase refresh rate
            self.state.refresh_rate = min(self.state.refresh_rate + 1, 10)
        
        elif key == ord('-'):
            # Decrease refresh rate
            self.state.refresh_rate = max(self.state.refresh_rate - 1, 1)
        
        elif key == ord('c'):
            # Sort by CPU
            if self.state.sort_by == 'cpu':
                self.state.sort_reverse = not self.state.sort_reverse
            else:
                self.state.sort_by = 'cpu'
                self.state.sort_reverse = True
        
        elif key == ord('m'):
            # Sort by memory
            if self.state.sort_by == 'memory':
                self.state.sort_reverse = not self.state.sort_reverse
            else:
                self.state.sort_by = 'memory'
                self.state.sort_reverse = True
        
        elif key == ord('n'):
            # Sort by name
            if self.state.sort_by == 'name':
                self.state.sort_reverse = not self.state.sort_reverse
            else:
                self.state.sort_by = 'name'
                self.state.sort_reverse = False
        
        elif key == ord('r'):
            # Reverse sort
            self.state.sort_reverse = not self.state.sort_reverse
        
        elif key == curses.KEY_UP:
            # Navigate up in process view
            if self.state.current_view == 'processes' and self.processes:
                if self.state.selected_process is None:
                    self.state.selected_process = self.processes[0]['pid']
                else:
                    # Find current process and move up
                    current_idx = next((i for i, p in enumerate(self.processes) if p['pid'] == self.state.selected_process), 0)
                    if current_idx > 0:
                        self.state.selected_process = self.processes[current_idx - 1]['pid']
        
        elif key == curses.KEY_DOWN:
            # Navigate down in process view
            if self.state.current_view == 'processes' and self.processes:
                if self.state.selected_process is None:
                    self.state.selected_process = self.processes[0]['pid']
                else:
                    # Find current process and move down
                    current_idx = next((i for i, p in enumerate(self.processes) if p['pid'] == self.state.selected_process), 0)
                    if current_idx < len(self.processes) - 1:
                        self.state.selected_process = self.processes[current_idx + 1]['pid']
        
        return True  # Continue
    
    def _init_curses(self):
        """Initialize curses colors"""
        curses.start_color()
        curses.use_default_colors()
        
        # Define color pairs
        curses.init_pair(1, curses.COLOR_GREEN, -1)   # Normal
        curses.init_pair(2, curses.COLOR_RED, -1)     # Warning/Critical
        curses.init_pair(3, curses.COLOR_YELLOW, -1)  # Warning
        curses.init_pair(4, curses.COLOR_BLUE, -1)    # Info
    
    def run(self):
        """Run the monitoring dashboard"""
        if not CURSES_AVAILABLE:
            print("Error: curses library not available")
            return
        
        self.running = True
        
        # Start background update thread
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
        try:
            curses.wrapper(self._main_loop)
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            if self.update_thread and self.update_thread.is_alive():
                self.update_thread.join(timeout=1)
    
    def _update_loop(self):
        """Background update loop"""
        while self.running:
            if not self.state.paused:
                self._update_data()
            time.sleep(self.state.refresh_rate)
    
    def _main_loop(self, stdscr):
        """Main curses loop"""
        # Initialize curses
        curses.curs_set(0)  # Hide cursor
        self._init_curses()
        
        # Main loop
        while self.running:
            try:
                # Get screen dimensions
                max_y, max_x = stdscr.getmaxyx()
                
                # Clear screen
                stdscr.clear()
                
                # Draw header
                self._draw_header(stdscr, max_y, max_x)
                
                # Draw content based on current view
                if self.state.show_help:
                    self._draw_help(stdscr, max_y, max_x)
                elif self.state.current_view == 'overview':
                    self._draw_overview(stdscr, max_y, max_x)
                elif self.state.current_view == 'processes':
                    self._draw_processes(stdscr, max_y, max_x)
                elif self.state.current_view == 'alerts':
                    self._draw_alerts(stdscr, max_y, max_x)
                elif self.state.current_view == 'tools':
                    self._draw_tools(stdscr, max_y, max_x)
                
                # Draw footer
                footer = "Press 'h' for help, 'q' to quit"
                stdscr.addstr(max_y - 1, 0, footer, curses.A_DIM)
                
                # Refresh screen
                stdscr.refresh()
                
                # Handle input (non-blocking)
                stdscr.timeout(100)  # 100ms timeout
                try:
                    key = stdscr.getch()
                    if key != -1:  # -1 means no input
                        if not self._handle_input(stdscr, key):
                            break
                except curses.error:
                    pass
                
            except curses.error:
                # Screen resize or other curses error
                pass

def main():
    """Main function for standalone testing"""
    try:
        dashboard = MonitoringDashboard()
        print("Starting Overseer System Monitor Dashboard...")
        print("Press Ctrl+C to exit")
        dashboard.run()
    except KeyboardInterrupt:
        print("\nDashboard stopped by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 