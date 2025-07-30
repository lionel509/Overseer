#!/usr/bin/env python3
"""
Dashboard Demo
Shows a preview of the monitoring dashboard interface.
"""

import os
import sys
import time
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent.parent.parent
sys.path.append(str(backend_dir))

def demo_dashboard():
    """Demo the dashboard functionality"""
    
    print("🚀 Overseer System Monitor Dashboard - Demo")
    print("=" * 60)
    
    try:
        from cli.features.monitoring_dashboard import MonitoringDashboard
        
        # Initialize dashboard
        dashboard = MonitoringDashboard()
        print("✅ Dashboard initialized")
        
        # Update data
        dashboard._update_data()
        print("✅ Data updated")
        
        # Show current metrics
        if dashboard.metrics:
            print("\n📊 Current System Metrics:")
            print("-" * 30)
            print(f"CPU Usage:     {dashboard.metrics.cpu_percent:6.1f}%")
            print(f"Memory Usage:  {dashboard.metrics.memory_percent:6.1f}% ({dashboard.metrics.memory_used_gb:.1f}GB / {dashboard.metrics.memory_total_gb:.1f}GB)")
            print(f"Disk Usage:    {dashboard.metrics.disk_percent:6.1f}% ({dashboard.metrics.disk_used_gb:.1f}GB / {dashboard.metrics.disk_total_gb:.1f}GB)")
            print(f"Processes:     {dashboard.metrics.process_count}")
            print(f"Load Average:  {dashboard.metrics.load_average[0]:.2f}, {dashboard.metrics.load_average[1]:.2f}, {dashboard.metrics.load_average[2]:.2f}")
            
            if dashboard.metrics.temperature:
                print(f"Temperature:   {dashboard.metrics.temperature:.1f}°C")
            
            if dashboard.metrics.battery_percent is not None:
                battery_icon = "🔌" if dashboard.metrics.battery_plugged else "🔋"
                print(f"Battery:       {dashboard.metrics.battery_percent:.1f}% {battery_icon}")
        
        # Show health score
        health_summary = dashboard.system_monitor.get_system_summary()
        print(f"\n🏥 System Health Score: {health_summary['health_score']}/100 ({health_summary['status']})")
        
        # Show recent alerts
        if dashboard.alerts:
            print(f"\n🚨 Recent Alerts ({len(dashboard.alerts)}):")
            print("-" * 30)
            for alert in dashboard.alerts[-3:]:
                print(f"  {alert.alert_type}: {alert.metric_value:.1f} (threshold: {alert.threshold:.1f}) - {alert.severity.value.upper()}")
        else:
            print("\n✅ No alerts - System is healthy")
        
        # Show top processes
        if dashboard.processes:
            print(f"\n📋 Top Processes (by {dashboard.state.sort_by}):")
            print("-" * 50)
            print(f"{'PID':>6} {'NAME':<20} {'CPU%':>6} {'MEM%':>6} {'STATUS':<10}")
            print("-" * 50)
            for proc in dashboard.processes[:10]:
                print(f"{proc['pid']:>6} {proc['name']:<20} {proc['cpu_percent']:>6.1f} {proc['memory_percent']:>6.1f} {proc['status']:<10}")
        else:
            print("\n⚠️  No process data available")
        
        # Show tool recommendations
        if dashboard.recommendations:
            print(f"\n🔧 Tool Recommendations ({len(dashboard.recommendations)}):")
            print("-" * 50)
            print(f"{'TOOL':<15} {'CATEGORY':<12} {'CONFIDENCE':>10} {'REASON':<30}")
            print("-" * 50)
            for rec in dashboard.recommendations[:5]:
                print(f"{rec.name:<15} {rec.category:<12} {rec.confidence_score:>10.1%} {rec.reason:<30}")
        else:
            print("\n📝 No tool recommendations available")
        
        # Show dashboard controls
        print(f"\n🎮 Dashboard Controls:")
        print("-" * 30)
        print("Tab          - Switch views (overview, processes, alerts, tools)")
        print("Space        - Pause/resume updates")
        print("c/m/n        - Sort by CPU/Memory/Name")
        print("r            - Reverse sort order")
        print("+/-          - Adjust refresh rate")
        print("h            - Show help")
        print("q            - Quit")
        
        print(f"\n📈 Current Settings:")
        print(f"  View: {dashboard.state.current_view}")
        print(f"  Refresh Rate: {dashboard.state.refresh_rate}s")
        print(f"  Sort By: {dashboard.state.sort_by}")
        print(f"  Sort Reverse: {dashboard.state.sort_reverse}")
        print(f"  Paused: {dashboard.state.paused}")
        
        print(f"\n🎯 Dashboard Features:")
        print("✅ Real-time system monitoring")
        print("✅ Process list with sorting")
        print("✅ Alert management")
        print("✅ Tool recommendations")
        print("✅ Interactive terminal interface")
        print("✅ Color-coded status indicators")
        print("✅ Configurable refresh rates")
        print("✅ Multiple view modes")
        
        print(f"\n🚀 To launch the full dashboard:")
        print("  python3 monitoring_dashboard.py")
        print("  python3 dashboard_cli.py --refresh 1 --view processes")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

def demo_cli_interface():
    """Demo the CLI interface"""
    
    print("\n🔧 CLI Interface Demo")
    print("=" * 30)
    
    print("Available commands:")
    print("  python3 dashboard_cli.py")
    print("  python3 dashboard_cli.py --refresh 1")
    print("  python3 dashboard_cli.py --view processes")
    print("  python3 dashboard_cli.py --refresh 1 --view alerts --debug")
    print("  python3 dashboard_cli.py --config my_config.json")
    
    print("\nCommand-line options:")
    print("  --refresh, -r    Refresh rate in seconds (1-10)")
    print("  --view, -v       Initial view (overview, processes, alerts, tools)")
    print("  --config, -c     Configuration file path")
    print("  --no-colors, -n  Disable colors")
    print("  --debug, -d      Enable debug mode")
    print("  --version, -V    Show version")

def main():
    """Run the dashboard demo"""
    
    print("🎬 Overseer Dashboard Demo")
    print("=" * 40)
    
    # Run dashboard demo
    demo_dashboard()
    
    # Run CLI demo
    demo_cli_interface()
    
    print("\n🎉 Demo completed!")
    print("The dashboard is ready for production use!")

if __name__ == "__main__":
    main() 