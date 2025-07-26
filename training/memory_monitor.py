#!/usr/bin/env python3
"""
Standalone memory monitoring script for training sessions.
Can be run in a separate terminal to monitor system resources.
"""

import psutil
import torch
import time
import json
from datetime import datetime
from pathlib import Path
import argparse

class TrainingMemoryMonitor:
    def __init__(self, log_file: str = "memory_log.json"):
        self.log_file = Path(log_file)
        self.monitoring = False
        
    def get_system_stats(self):
        """Get comprehensive system statistics"""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disk
        disk = psutil.disk_usage('/')
        
        # Network
        network = psutil.net_io_counters()
        
        stats = {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'percent': cpu_percent,
                'count': cpu_count
            },
            'memory': {
                'total_gb': memory.total / (1024**3),
                'available_gb': memory.available / (1024**3),
                'used_gb': memory.used / (1024**3),
                'percent': memory.percent
            },
            'swap': {
                'total_gb': swap.total / (1024**3),
                'used_gb': swap.used / (1024**3),
                'percent': swap.percent
            },
            'disk': {
                'total_gb': disk.total / (1024**3),
                'used_gb': disk.used / (1024**3),
                'free_gb': disk.free / (1024**3),
                'percent': (disk.used / disk.total) * 100
            },
            'network': {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv
            }
        }
        
        # GPU stats if available
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.memory_stats()
            stats['gpu'] = {
                'memory_allocated_gb': gpu_memory['allocated_bytes.all.current'] / (1024**3),
                'memory_reserved_gb': gpu_memory['reserved_bytes.all.current'] / (1024**3),
                'memory_free_gb': (torch.cuda.get_device_properties(0).total_memory - 
                                 gpu_memory['reserved_bytes.all.current']) / (1024**3),
                'memory_total_gb': torch.cuda.get_device_properties(0).total_memory / (1024**3),
                'memory_percent': (gpu_memory['allocated_bytes.all.current'] / 
                                 torch.cuda.get_device_properties(0).total_memory) * 100
            }
        
        return stats
    
    def log_stats(self, stats):
        """Log statistics to file"""
        if not self.log_file.exists():
            with open(self.log_file, 'w') as f:
                json.dump([stats], f, indent=2)
        else:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            logs.append(stats)
            with open(self.log_file, 'w') as f:
                json.dump(logs, f, indent=2)
    
    def print_stats(self, stats):
        """Print formatted statistics to console"""
        print(f"\n=== System Monitor - {stats['timestamp']} ===")
        print(f"CPU: {stats['cpu']['percent']:.1f}% ({stats['cpu']['count']} cores)")
        print(f"RAM: {stats['memory']['used_gb']:.1f}GB / {stats['memory']['total_gb']:.1f}GB ({stats['memory']['percent']:.1f}%)")
        print(f"Swap: {stats['swap']['used_gb']:.1f}GB / {stats['swap']['total_gb']:.1f}GB ({stats['swap']['percent']:.1f}%)")
        print(f"Disk: {stats['disk']['used_gb']:.1f}GB / {stats['disk']['total_gb']:.1f}GB ({stats['disk']['percent']:.1f}%)")
        
        if 'gpu' in stats:
            print(f"GPU Memory: {stats['gpu']['memory_allocated_gb']:.1f}GB / {stats['gpu']['memory_total_gb']:.1f}GB ({stats['gpu']['memory_percent']:.1f}%)")
        
        # Check for warnings
        warnings = []
        if stats['memory']['percent'] > 85:
            warnings.append("High RAM usage")
        if stats['swap']['percent'] > 50:
            warnings.append("High swap usage")
        if 'gpu' in stats and stats['gpu']['memory_percent'] > 90:
            warnings.append("High GPU memory usage")
        
        if warnings:
            print(f"⚠️  Warnings: {', '.join(warnings)}")
    
    def start_monitoring(self, interval: int = 30, log_to_file: bool = True):
        """Start continuous monitoring"""
        self.monitoring = True
        print(f"Starting memory monitoring (interval: {interval}s, logging: {log_to_file})")
        print("Press Ctrl+C to stop monitoring")
        
        try:
            while self.monitoring:
                stats = self.get_system_stats()
                self.print_stats(stats)
                
                if log_to_file:
                    self.log_stats(stats)
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
            self.monitoring = False
    
    def analyze_logs(self):
        """Analyze logged statistics"""
        if not self.log_file.exists():
            print("No log file found")
            return
        
        with open(self.log_file, 'r') as f:
            logs = json.load(f)
        
        if not logs:
            print("No data in log file")
            return
        
        print(f"\n=== Memory Log Analysis ({len(logs)} entries) ===")
        
        # Calculate averages
        ram_percentages = [log['memory']['percent'] for log in logs]
        swap_percentages = [log['swap']['percent'] for log in logs]
        
        print(f"Average RAM usage: {sum(ram_percentages) / len(ram_percentages):.1f}%")
        print(f"Average swap usage: {sum(swap_percentages) / len(swap_percentages):.1f}%")
        print(f"Max RAM usage: {max(ram_percentages):.1f}%")
        print(f"Max swap usage: {max(swap_percentages):.1f}%")
        
        # Check for GPU stats
        gpu_logs = [log for log in logs if 'gpu' in log]
        if gpu_logs:
            gpu_percentages = [log['gpu']['memory_percent'] for log in gpu_logs]
            print(f"Average GPU memory usage: {sum(gpu_percentages) / len(gpu_percentages):.1f}%")
            print(f"Max GPU memory usage: {max(gpu_percentages):.1f}%")

def main():
    parser = argparse.ArgumentParser(description='Monitor system resources during training')
    parser.add_argument('--interval', type=int, default=30, help='Monitoring interval in seconds')
    parser.add_argument('--log-file', type=str, default='memory_log.json', help='Log file path')
    parser.add_argument('--no-log', action='store_true', help='Disable logging to file')
    parser.add_argument('--analyze', action='store_true', help='Analyze existing logs instead of monitoring')
    
    args = parser.parse_args()
    
    monitor = TrainingMemoryMonitor(args.log_file)
    
    if args.analyze:
        monitor.analyze_logs()
    else:
        monitor.start_monitoring(args.interval, not args.no_log)

if __name__ == "__main__":
    main() 