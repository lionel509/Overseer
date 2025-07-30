"""
Export and Reporting for System Monitoring
Provides data export capabilities, historical report generation, and performance trend analysis.
"""

import os
import sys
import json
import csv
import time
import sqlite3
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from system_monitor import SystemMonitor
from predictive_analytics import PredictiveAnalytics
from alert_manager import AlertManager

@dataclass
class ReportConfig:
    """Report configuration data structure"""
    report_type: str  # 'system_health', 'performance_trends', 'alert_summary', 'custom'
    time_range: str  # '1h', '6h', '24h', '7d', '30d', 'custom'
    start_time: Optional[float]
    end_time: Optional[float]
    metrics: List[str]
    format: str  # 'json', 'csv', 'html', 'pdf'
    include_charts: bool
    include_recommendations: bool

@dataclass
class ExportData:
    """Export data structure"""
    data_type: str
    timestamp: float
    data: Dict[str, Any]
    metadata: Dict[str, Any]

class ExportReporting:
    """Export and reporting engine for system monitoring data"""
    
    def __init__(self, config: Dict = None):
        """Initialize export and reporting"""
        self.console = Console() if RICH_AVAILABLE else None
        self.config = config or {}
        
        # Initialize components
        self.system_monitor = SystemMonitor()
        self.predictive_analytics = PredictiveAnalytics()
        self.alert_manager = AlertManager()
        
        # Export settings
        self.export_dir = self.config.get('export_dir', 'exports')
        self.report_dir = self.config.get('report_dir', 'reports')
        
        # Create directories
        os.makedirs(self.export_dir, exist_ok=True)
        os.makedirs(self.report_dir, exist_ok=True)
        
        # Database paths
        self.system_db = os.path.join(os.path.dirname(__file__), '../../db/system_metrics.db')
        self.alerts_db = os.path.join(os.path.dirname(__file__), '../../db/system_alerts.db')
        self.predictive_db = os.path.join(os.path.dirname(__file__), '../../db/predictive_analytics.db')
    
    def export_system_metrics(self, start_time: float = None, end_time: float = None, 
                            format: str = 'json') -> str:
        """Export system metrics data"""
        if start_time is None:
            start_time = time.time() - (24 * 3600)  # Last 24 hours
        if end_time is None:
            end_time = time.time()
        
        try:
            conn = sqlite3.connect(self.system_db)
            cursor = conn.cursor()
            
            # Get metrics data
            cursor.execute('''
                SELECT * FROM system_metrics 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            ''', (start_time, end_time))
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return "No data found for the specified time range"
            
            # Convert to structured data
            metrics_data = []
            for row in rows:
                metrics_data.append({
                    'timestamp': row[1],
                    'cpu_percent': row[2],
                    'memory_percent': row[3],
                    'disk_percent': row[4],
                    'network_sent_mb': row[5],
                    'network_recv_mb': row[6],
                    'process_count': row[7],
                    'load_average_1': row[8],
                    'load_average_5': row[9],
                    'load_average_15': row[10],
                    'temperature': row[11],
                    'battery_percent': row[12],
                    'battery_plugged': row[13]
                })
            
            # Export based on format
            if format == 'json':
                return self._export_json(metrics_data, 'system_metrics')
            elif format == 'csv':
                return self._export_csv(metrics_data, 'system_metrics')
            elif format == 'html':
                return self._export_html(metrics_data, 'system_metrics')
            else:
                return f"Unsupported format: {format}"
                
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error exporting system metrics: {e}[/red]")
            return f"Error: {e}"
    
    def export_alerts(self, start_time: float = None, end_time: float = None,
                     format: str = 'json') -> str:
        """Export alert data"""
        if start_time is None:
            start_time = time.time() - (24 * 3600)  # Last 24 hours
        if end_time is None:
            end_time = time.time()
        
        try:
            conn = sqlite3.connect(self.alerts_db)
            cursor = conn.cursor()
            
            # Get alerts data
            cursor.execute('''
                SELECT * FROM system_alerts 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
            ''', (start_time, end_time))
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return "No alerts found for the specified time range"
            
            # Convert to structured data
            alerts_data = []
            for row in rows:
                alerts_data.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'alert_type': row[2],
                    'metric_name': row[3],
                    'metric_value': row[4],
                    'threshold': row[5],
                    'severity': row[6],
                    'message': row[7],
                    'acknowledged': bool(row[8]),
                    'acknowledged_by': row[9],
                    'acknowledged_at': row[10]
                })
            
            # Export based on format
            if format == 'json':
                return self._export_json(alerts_data, 'system_alerts')
            elif format == 'csv':
                return self._export_csv(alerts_data, 'system_alerts')
            elif format == 'html':
                return self._export_html(alerts_data, 'system_alerts')
            else:
                return f"Unsupported format: {format}"
                
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error exporting alerts: {e}[/red]")
            return f"Error: {e}"
    
    def export_predictive_data(self, start_time: float = None, end_time: float = None,
                              format: str = 'json') -> str:
        """Export predictive analytics data"""
        if start_time is None:
            start_time = time.time() - (24 * 3600)  # Last 24 hours
        if end_time is None:
            end_time = time.time()
        
        try:
            conn = sqlite3.connect(self.predictive_db)
            cursor = conn.cursor()
            
            # Get trend analysis data
            cursor.execute('''
                SELECT * FROM trend_analysis 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
            ''', (start_time, end_time))
            
            trend_rows = cursor.fetchall()
            
            # Get anomalies data
            cursor.execute('''
                SELECT * FROM anomalies 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
            ''', (start_time, end_time))
            
            anomaly_rows = cursor.fetchall()
            
            # Get forecasts data
            cursor.execute('''
                SELECT * FROM performance_forecasts 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
            ''', (start_time, end_time))
            
            forecast_rows = cursor.fetchall()
            
            conn.close()
            
            # Combine all predictive data
            predictive_data = {
                'trends': [],
                'anomalies': [],
                'forecasts': []
            }
            
            for row in trend_rows:
                predictive_data['trends'].append({
                    'metric_name': row[1],
                    'current_value': row[2],
                    'trend_direction': row[3],
                    'trend_strength': row[4],
                    'change_rate': row[5],
                    'prediction_1h': row[6],
                    'prediction_6h': row[7],
                    'prediction_24h': row[8],
                    'confidence': row[9],
                    'timestamp': row[10]
                })
            
            for row in anomaly_rows:
                predictive_data['anomalies'].append({
                    'metric_name': row[1],
                    'timestamp': row[2],
                    'value': row[3],
                    'expected_value': row[4],
                    'deviation': row[5],
                    'severity': row[6],
                    'anomaly_type': row[7],
                    'confidence': row[8]
                })
            
            for row in forecast_rows:
                predictive_data['forecasts'].append({
                    'metric_name': row[1],
                    'forecast_horizon': row[2],
                    'predicted_value': row[3],
                    'confidence_lower': row[4],
                    'confidence_upper': row[5],
                    'trend_analysis': row[6],
                    'recommendations': row[7],
                    'timestamp': row[8]
                })
            
            # Export based on format
            if format == 'json':
                return self._export_json(predictive_data, 'predictive_analytics')
            elif format == 'csv':
                return self._export_csv(predictive_data, 'predictive_analytics')
            elif format == 'html':
                return self._export_html(predictive_data, 'predictive_analytics')
            else:
                return f"Unsupported format: {format}"
                
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error exporting predictive data: {e}[/red]")
            return f"Error: {e}"
    
    def _export_json(self, data: Any, data_type: str) -> str:
        """Export data as JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{data_type}_{timestamp}.json"
        filepath = os.path.join(self.export_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            return f"✅ Exported {data_type} to {filepath}"
            
        except Exception as e:
            return f"Error exporting JSON: {e}"
    
    def _export_csv(self, data: List[Dict], data_type: str) -> str:
        """Export data as CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{data_type}_{timestamp}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        try:
            if not data:
                return "No data to export"
            
            # Get fieldnames from first item
            fieldnames = list(data[0].keys())
            
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            return f"✅ Exported {data_type} to {filepath}"
            
        except Exception as e:
            return f"Error exporting CSV: {e}"
    
    def _export_html(self, data: Any, data_type: str) -> str:
        """Export data as HTML report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{data_type}_{timestamp}.html"
        filepath = os.path.join(self.export_dir, filename)
        
        try:
            html_content = self._generate_html_report(data, data_type)
            
            with open(filepath, 'w') as f:
                f.write(html_content)
            
            return f"✅ Exported {data_type} to {filepath}"
            
        except Exception as e:
            return f"Error exporting HTML: {e}"
    
    def _generate_html_report(self, data: Any, data_type: str) -> str:
        """Generate HTML report content"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{data_type.title()} Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; }}
        .data-table {{ width: 100%; border-collapse: collapse; }}
        .data-table th, .data-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .data-table th {{ background-color: #f2f2f2; }}
        .summary {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{data_type.title()} Report</h1>
        <p>Generated on: {timestamp}</p>
    </div>
    
    <div class="section">
        <h2>Data Summary</h2>
        <div class="summary">
            <p><strong>Data Type:</strong> {data_type}</p>
            <p><strong>Records:</strong> {len(data) if isinstance(data, list) else 'Multiple sections'}</p>
        </div>
    </div>
    
    <div class="section">
        <h2>Data Details</h2>
        <pre>{json.dumps(data, indent=2, default=str)}</pre>
    </div>
</body>
</html>
        """
        
        return html_template
    
    def generate_system_health_report(self, time_range: str = '24h', 
                                    include_recommendations: bool = True) -> str:
        """Generate comprehensive system health report"""
        try:
            # Calculate time range
            end_time = time.time()
            if time_range == '1h':
                start_time = end_time - 3600
            elif time_range == '6h':
                start_time = end_time - (6 * 3600)
            elif time_range == '24h':
                start_time = end_time - (24 * 3600)
            elif time_range == '7d':
                start_time = end_time - (7 * 24 * 3600)
            elif time_range == '30d':
                start_time = end_time - (30 * 24 * 3600)
            else:
                start_time = end_time - (24 * 3600)  # Default to 24h
            
            # Collect current metrics
            current_metrics = self.system_monitor.collect_metrics()
            health_summary = self.system_monitor.get_system_summary()
            
            # Get historical data
            conn = sqlite3.connect(self.system_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM system_metrics 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            ''', (start_time, end_time))
            
            historical_data = cursor.fetchall()
            conn.close()
            
            # Generate report
            report_data = {
                'report_type': 'system_health',
                'time_range': time_range,
                'generated_at': time.time(),
                'current_metrics': asdict(current_metrics) if current_metrics else {},
                'health_summary': health_summary,
                'historical_data': historical_data,
                'recommendations': []
            }
            
            # Add recommendations if requested
            if include_recommendations and current_metrics:
                recommendations = self._generate_health_recommendations(current_metrics, health_summary)
                report_data['recommendations'] = recommendations
            
            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"system_health_report_{time_range}_{timestamp}.json"
            filepath = os.path.join(self.report_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            return f"✅ Generated system health report: {filepath}"
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error generating system health report: {e}[/red]")
            return f"Error: {e}"
    
    def generate_performance_trend_report(self, time_range: str = '7d') -> str:
        """Generate performance trend analysis report"""
        try:
            # Calculate time range
            end_time = time.time()
            if time_range == '24h':
                start_time = end_time - (24 * 3600)
            elif time_range == '7d':
                start_time = end_time - (7 * 24 * 3600)
            elif time_range == '30d':
                start_time = end_time - (30 * 24 * 3600)
            else:
                start_time = end_time - (7 * 24 * 3600)  # Default to 7d
            
            # Get historical data
            conn = sqlite3.connect(self.system_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM system_metrics 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            ''', (start_time, end_time))
            
            historical_data = cursor.fetchall()
            conn.close()
            
            # Analyze trends
            trends = self._analyze_performance_trends(historical_data)
            
            # Generate report
            report_data = {
                'report_type': 'performance_trends',
                'time_range': time_range,
                'generated_at': time.time(),
                'trends': trends,
                'historical_data': historical_data
            }
            
            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_trends_report_{time_range}_{timestamp}.json"
            filepath = os.path.join(self.report_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            return f"✅ Generated performance trends report: {filepath}"
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error generating performance trends report: {e}[/red]")
            return f"Error: {e}"
    
    def _analyze_performance_trends(self, historical_data: List) -> Dict:
        """Analyze performance trends from historical data"""
        if not historical_data:
            return {}
        
        # Calculate averages and trends for key metrics
        trends = {}
        
        # CPU trends
        cpu_values = [row[2] for row in historical_data if row[2] is not None]
        if cpu_values:
            trends['cpu'] = {
                'average': sum(cpu_values) / len(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values),
                'trend': 'increasing' if cpu_values[-1] > cpu_values[0] else 'decreasing' if cpu_values[-1] < cpu_values[0] else 'stable'
            }
        
        # Memory trends
        memory_values = [row[3] for row in historical_data if row[3] is not None]
        if memory_values:
            trends['memory'] = {
                'average': sum(memory_values) / len(memory_values),
                'max': max(memory_values),
                'min': min(memory_values),
                'trend': 'increasing' if memory_values[-1] > memory_values[0] else 'decreasing' if memory_values[-1] < memory_values[0] else 'stable'
            }
        
        # Disk trends
        disk_values = [row[4] for row in historical_data if row[4] is not None]
        if disk_values:
            trends['disk'] = {
                'average': sum(disk_values) / len(disk_values),
                'max': max(disk_values),
                'min': min(disk_values),
                'trend': 'increasing' if disk_values[-1] > disk_values[0] else 'decreasing' if disk_values[-1] < disk_values[0] else 'stable'
            }
        
        return trends
    
    def _generate_health_recommendations(self, metrics, health_summary: Dict) -> List[str]:
        """Generate health recommendations based on current metrics"""
        recommendations = []
        
        # CPU recommendations
        if metrics.cpu_percent > 80:
            recommendations.append("High CPU usage detected. Consider optimizing applications or upgrading CPU.")
        elif metrics.cpu_percent > 60:
            recommendations.append("Moderate CPU usage. Monitor for potential performance issues.")
        
        # Memory recommendations
        if metrics.memory_percent > 85:
            recommendations.append("High memory usage detected. Consider increasing RAM or optimizing memory usage.")
        elif metrics.memory_percent > 70:
            recommendations.append("Moderate memory usage. Monitor memory consumption trends.")
        
        # Disk recommendations
        if metrics.disk_percent > 90:
            recommendations.append("Critical disk space usage. Immediate cleanup required.")
        elif metrics.disk_percent > 80:
            recommendations.append("High disk usage. Consider cleanup or storage expansion.")
        
        # Temperature recommendations
        if metrics.temperature and metrics.temperature > 80:
            recommendations.append("High CPU temperature detected. Check cooling system and reduce load.")
        
        # Battery recommendations
        if metrics.battery_percent is not None and metrics.battery_percent < 20:
            recommendations.append("Low battery level. Connect to power source.")
        
        # Overall health recommendations
        health_score = health_summary.get('health_score', 0)
        if health_score < 50:
            recommendations.append("System health is poor. Immediate attention required.")
        elif health_score < 70:
            recommendations.append("System health is fair. Monitor for improvements.")
        
        return recommendations
    
    def display_export_options(self):
        """Display available export options"""
        if not RICH_AVAILABLE:
            print("Rich library required for formatted display")
            return
        
        options_table = Table(title="Export and Reporting Options")
        options_table.add_column("Option", style="cyan")
        options_table.add_column("Description", style="green")
        options_table.add_column("Format", style="yellow")
        options_table.add_column("Time Range", style="magenta")
        
        options_table.add_row(
            "System Metrics",
            "Export system monitoring data",
            "JSON, CSV, HTML",
            "Custom time range"
        )
        options_table.add_row(
            "Alerts",
            "Export alert history",
            "JSON, CSV, HTML",
            "Custom time range"
        )
        options_table.add_row(
            "Predictive Data",
            "Export analytics data",
            "JSON, CSV, HTML",
            "Custom time range"
        )
        options_table.add_row(
            "System Health Report",
            "Generate health report",
            "JSON",
            "1h, 6h, 24h, 7d, 30d"
        )
        options_table.add_row(
            "Performance Trends",
            "Generate trends report",
            "JSON",
            "24h, 7d, 30d"
        )
        
        self.console.print(options_table)

def main():
    """Main function for standalone testing"""
    exporter = ExportReporting()
    
    print("📊 Export and Reporting Engine")
    print("=" * 50)
    
    # Display options
    exporter.display_export_options()
    
    # Test exports
    print("\n🧪 Testing exports...")
    
    # Export system metrics
    result = exporter.export_system_metrics(format='json')
    print(f"System Metrics: {result}")
    
    # Export alerts
    result = exporter.export_alerts(format='json')
    print(f"Alerts: {result}")
    
    # Generate system health report
    result = exporter.generate_system_health_report(time_range='24h')
    print(f"System Health Report: {result}")
    
    # Generate performance trends report
    result = exporter.generate_performance_trend_report(time_range='7d')
    print(f"Performance Trends Report: {result}")
    
    print("\n✅ Export and reporting tests completed!")

if __name__ == "__main__":
    main() 