#!/usr/bin/env python3
"""
Real-Time Stats Tool for Overseer CLI
Provides real-time system monitoring and performance data collection
"""

import psutil
import time
import json
import threading
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from collections import deque
import platform

class RealTimeStatsTool:
    def __init__(self, max_data_points: int = 100):
        self.max_data_points = max_data_points
        self.stats_history = deque(maxlen=max_data_points)
        self.is_monitoring = False
        self.monitoring_thread = None
        self.update_interval = 2.0  # seconds
        self.callbacks = []
        self.alert_thresholds = {
            'cpu': {'warning': 60, 'critical': 80},
            'memory': {'warning': 70, 'critical': 85},
            'disk': {'warning': 80, 'critical': 90}
        }
        
    def start_monitoring(self, interval: float = 2.0, callback: Optional[Callable] = None):
        """Start real-time monitoring"""
        if self.is_monitoring:
            return {"success": False, "error": "Monitoring already active"}
        
        self.update_interval = interval
        if callback:
            self.callbacks.append(callback)
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        return {
            "success": True,
            "message": f"Started monitoring with {interval}s interval"
        }
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        if not self.is_monitoring:
            return {"success": False, "error": "Monitoring not active"}
        
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1)
        
        return {
            "success": True,
            "message": "Stopped monitoring"
        }
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                stats = self._collect_system_stats()
                self.stats_history.append(stats)
                
                # Check for alerts
                alerts = self._check_alerts(stats)
                if alerts:
                    self._trigger_alerts(alerts)
                
                # Call callbacks
                for callback in self.callbacks:
                    try:
                        callback(stats)
                    except Exception as e:
                        print(f"Callback error: {e}")
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(self.update_interval)
    
    def _collect_system_stats(self) -> Dict[str, Any]:
        """Collect current system statistics"""
        try:
            # CPU stats
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()
            cpu_count = psutil.cpu_count()
            
            # Memory stats
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk stats
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network stats
            network = psutil.net_io_counters()
            
            # Process stats
            processes = list(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']))
            process_stats = {
                'total': len(processes),
                'running': len([p for p in processes if p.info['status'] == 'running']),
                'sleeping': len([p for p in processes if p.info['status'] == 'sleeping']),
                'stopped': len([p for p in processes if p.info['status'] == 'stopped']),
                'zombie': len([p for p in processes if p.info['status'] == 'zombie'])
            }
            
            # Load average (if available)
            try:
                load_avg = psutil.getloadavg()
                load_average = {
                    'one_min': load_avg[0],
                    'five_min': load_avg[1],
                    'fifteen_min': load_avg[2]
                }
            except AttributeError:
                load_average = {'one_min': 0, 'five_min': 0, 'fifteen_min': 0}
            
            stats = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'usage': cpu_percent,
                    'cores': cpu_count,
                    'frequency': cpu_freq.current if cpu_freq else None,
                    'frequency_min': cpu_freq.min if cpu_freq else None,
                    'frequency_max': cpu_freq.max if cpu_freq else None
                },
                'memory': {
                    'total': memory.total,
                    'used': memory.used,
                    'available': memory.available,
                    'free': memory.free,
                    'percent': memory.percent,
                    'swap': {
                        'total': swap.total,
                        'used': swap.used,
                        'free': swap.free,
                        'percent': swap.percent
                    }
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent,
                    'read_bytes': disk_io.read_bytes if disk_io else 0,
                    'write_bytes': disk_io.write_bytes if disk_io else 0
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'processes': process_stats,
                'load_average': load_average,
                'platform': platform.system(),
                'hostname': platform.node()
            }
            
            return stats
            
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _check_alerts(self, stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for alert conditions"""
        alerts = []
        
        try:
            # CPU alerts
            cpu_usage = stats['cpu']['usage']
            if cpu_usage >= self.alert_thresholds['cpu']['critical']:
                alerts.append({
                    'type': 'critical',
                    'metric': 'cpu',
                    'value': cpu_usage,
                    'threshold': self.alert_thresholds['cpu']['critical'],
                    'message': f"Critical CPU usage: {cpu_usage:.1f}%"
                })
            elif cpu_usage >= self.alert_thresholds['cpu']['warning']:
                alerts.append({
                    'type': 'warning',
                    'metric': 'cpu',
                    'value': cpu_usage,
                    'threshold': self.alert_thresholds['cpu']['warning'],
                    'message': f"High CPU usage: {cpu_usage:.1f}%"
                })
            
            # Memory alerts
            memory_usage = stats['memory']['percent']
            if memory_usage >= self.alert_thresholds['memory']['critical']:
                alerts.append({
                    'type': 'critical',
                    'metric': 'memory',
                    'value': memory_usage,
                    'threshold': self.alert_thresholds['memory']['critical'],
                    'message': f"Critical memory usage: {memory_usage:.1f}%"
                })
            elif memory_usage >= self.alert_thresholds['memory']['warning']:
                alerts.append({
                    'type': 'warning',
                    'metric': 'memory',
                    'value': memory_usage,
                    'threshold': self.alert_thresholds['memory']['warning'],
                    'message': f"High memory usage: {memory_usage:.1f}%"
                })
            
            # Disk alerts
            disk_usage = stats['disk']['percent']
            if disk_usage >= self.alert_thresholds['disk']['critical']:
                alerts.append({
                    'type': 'critical',
                    'metric': 'disk',
                    'value': disk_usage,
                    'threshold': self.alert_thresholds['disk']['critical'],
                    'message': f"Critical disk usage: {disk_usage:.1f}%"
                })
            elif disk_usage >= self.alert_thresholds['disk']['warning']:
                alerts.append({
                    'type': 'warning',
                    'metric': 'disk',
                    'value': disk_usage,
                    'threshold': self.alert_thresholds['disk']['warning'],
                    'message': f"High disk usage: {disk_usage:.1f}%"
                })
                
        except Exception as e:
            alerts.append({
                'type': 'error',
                'message': f"Error checking alerts: {str(e)}"
            })
        
        return alerts
    
    def _trigger_alerts(self, alerts: List[Dict[str, Any]]):
        """Trigger alert notifications"""
        for alert in alerts:
            print(f"ALERT [{alert['type'].upper()}]: {alert['message']}")
            # Here you could send notifications, log to file, etc.
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        return self._collect_system_stats()
    
    def get_stats_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get historical statistics"""
        if limit is None:
            limit = len(self.stats_history)
        
        return list(self.stats_history)[-limit:]
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """Get summary statistics from history"""
        if not self.stats_history:
            return {"error": "No statistics available"}
        
        stats_list = list(self.stats_history)
        
        # Calculate averages
        cpu_values = [s['cpu']['usage'] for s in stats_list if 'cpu' in s]
        memory_values = [s['memory']['percent'] for s in stats_list if 'memory' in s]
        disk_values = [s['disk']['percent'] for s in stats_list if 'disk' in s]
        
        summary = {
            'total_samples': len(stats_list),
            'time_range': {
                'start': stats_list[0]['timestamp'],
                'end': stats_list[-1]['timestamp']
            },
            'averages': {
                'cpu': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                'memory': sum(memory_values) / len(memory_values) if memory_values else 0,
                'disk': sum(disk_values) / len(disk_values) if disk_values else 0
            },
            'peaks': {
                'cpu': max(cpu_values) if cpu_values else 0,
                'memory': max(memory_values) if memory_values else 0,
                'disk': max(disk_values) if disk_values else 0
            },
            'lows': {
                'cpu': min(cpu_values) if cpu_values else 0,
                'memory': min(memory_values) if memory_values else 0,
                'disk': min(disk_values) if disk_values else 0
            }
        }
        
        return summary
    
    def set_alert_thresholds(self, thresholds: Dict[str, Dict[str, float]]):
        """Set alert thresholds"""
        self.alert_thresholds.update(thresholds)
    
    def get_alert_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Get current alert thresholds"""
        return self.alert_thresholds.copy()
    
    def add_callback(self, callback: Callable):
        """Add a callback function to be called with each stats update"""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable):
        """Remove a callback function"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def clear_history(self):
        """Clear statistics history"""
        self.stats_history.clear()
    
    def is_monitoring_active(self) -> bool:
        """Check if monitoring is currently active"""
        return self.is_monitoring
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get monitoring status information"""
        return {
            'is_active': self.is_monitoring,
            'update_interval': self.update_interval,
            'max_data_points': self.max_data_points,
            'current_data_points': len(self.stats_history),
            'callbacks_count': len(self.callbacks)
        }

def main():
    """CLI interface for real-time stats tool"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Real-Time Stats Tool")
    parser.add_argument("--start", action="store_true", help="Start monitoring")
    parser.add_argument("--stop", action="store_true", help="Stop monitoring")
    parser.add_argument("--status", action="store_true", help="Show monitoring status")
    parser.add_argument("--current", action="store_true", help="Show current stats")
    parser.add_argument("--history", type=int, metavar="N", help="Show last N stats")
    parser.add_argument("--summary", action="store_true", help="Show stats summary")
    parser.add_argument("--interval", type=float, default=2.0, help="Update interval in seconds")
    parser.add_argument("--thresholds", action="store_true", help="Show alert thresholds")
    parser.add_argument("--set-threshold", nargs=3, metavar=("METRIC", "LEVEL", "VALUE"), 
                       help="Set alert threshold (e.g., cpu warning 60)")
    
    args = parser.parse_args()
    
    tool = RealTimeStatsTool()
    
    if args.start:
        result = tool.start_monitoring(args.interval)
        print(f"Start result: {result}")
    
    elif args.stop:
        result = tool.stop_monitoring()
        print(f"Stop result: {result}")
    
    elif args.status:
        status = tool.get_monitoring_status()
        print("Monitoring Status:")
        print(json.dumps(status, indent=2))
    
    elif args.current:
        stats = tool.get_current_stats()
        print("Current Stats:")
        print(json.dumps(stats, indent=2))
    
    elif args.history:
        history = tool.get_stats_history(args.history)
        print(f"Last {len(history)} Stats:")
        for i, stat in enumerate(history):
            print(f"  {i+1}. {stat['timestamp']}: CPU={stat['cpu']['usage']:.1f}%, "
                  f"Mem={stat['memory']['percent']:.1f}%, Disk={stat['disk']['percent']:.1f}%")
    
    elif args.summary:
        summary = tool.get_stats_summary()
        print("Stats Summary:")
        print(json.dumps(summary, indent=2))
    
    elif args.thresholds:
        thresholds = tool.get_alert_thresholds()
        print("Alert Thresholds:")
        print(json.dumps(thresholds, indent=2))
    
    elif args.set_threshold:
        metric, level, value = args.set_threshold
        try:
            value = float(value)
            current_thresholds = tool.get_alert_thresholds()
            if metric in current_thresholds and level in current_thresholds[metric]:
                current_thresholds[metric][level] = value
                tool.set_alert_thresholds(current_thresholds)
                print(f"Set {metric} {level} threshold to {value}")
            else:
                print(f"Invalid metric '{metric}' or level '{level}'")
        except ValueError:
            print("Invalid threshold value")
    
    else:
        # Default: show current stats
        stats = tool.get_current_stats()
        print("Current System Stats:")
        print(f"  CPU: {stats['cpu']['usage']:.1f}%")
        print(f"  Memory: {stats['memory']['percent']:.1f}%")
        print(f"  Disk: {stats['disk']['percent']:.1f}%")
        print(f"  Processes: {stats['processes']['total']}")

if __name__ == "__main__":
    main() 