"""
Alert Manager for System Monitoring
Handles threshold-based alerts, notifications, and alert management.
"""

import os
import json
import sqlite3
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class Alert:
    """Alert data structure"""
    id: Optional[int]
    timestamp: float
    alert_type: str
    metric_name: str
    metric_value: float
    threshold: float
    severity: AlertSeverity
    message: str
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[float] = None

class AlertManager:
    """Manages system alerts and notifications"""
    
    def __init__(self, db_path: str = None, config: Dict = None):
        """Initialize alert manager"""
        self.console = Console() if RICH_AVAILABLE else None
        self.config = config or {}
        
        # Database setup
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '../../db/system_alerts.db')
        self.db_path = db_path
        self._init_database()
        
        # Alert thresholds
        self.thresholds = {
            'cpu_warning': self.config.get('cpu_warning', 70.0),
            'cpu_critical': self.config.get('cpu_critical', 90.0),
            'memory_warning': self.config.get('memory_warning', 80.0),
            'memory_critical': self.config.get('memory_critical', 95.0),
            'disk_warning': self.config.get('disk_warning', 85.0),
            'disk_critical': self.config.get('disk_critical', 95.0),
            'temperature_warning': self.config.get('temperature_warning', 70.0),
            'temperature_critical': self.config.get('temperature_critical', 85.0),
        }
        
        # Alert history
        self.recent_alerts = []
        self.alert_callbacks = []
    
    def _init_database(self):
        """Initialize the alerts database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                alert_type TEXT,
                metric_name TEXT,
                metric_value REAL,
                threshold REAL,
                severity TEXT,
                message TEXT,
                acknowledged INTEGER DEFAULT 0,
                acknowledged_by TEXT,
                acknowledged_at REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create alert rules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_name TEXT UNIQUE,
                metric_name TEXT,
                threshold REAL,
                severity TEXT,
                enabled INTEGER DEFAULT 1,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create notification settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notification_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT,
                enabled INTEGER DEFAULT 1,
                notification_method TEXT DEFAULT 'console',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Initialize default alert rules
        self._init_default_rules(cursor)
        
        conn.commit()
        conn.close()
    
    def _init_default_rules(self, cursor):
        """Initialize default alert rules"""
        default_rules = [
            ('CPU Warning', 'cpu_percent', 70.0, 'warning', 'CPU usage above 70%'),
            ('CPU Critical', 'cpu_percent', 90.0, 'critical', 'CPU usage above 90%'),
            ('Memory Warning', 'memory_percent', 80.0, 'warning', 'Memory usage above 80%'),
            ('Memory Critical', 'memory_percent', 95.0, 'critical', 'Memory usage above 95%'),
            ('Disk Warning', 'disk_percent', 85.0, 'warning', 'Disk usage above 85%'),
            ('Disk Critical', 'disk_percent', 95.0, 'critical', 'Disk usage above 95%'),
            ('Temperature Warning', 'temperature', 70.0, 'warning', 'CPU temperature above 70°C'),
            ('Temperature Critical', 'temperature', 85.0, 'critical', 'CPU temperature above 85°C'),
        ]
        
        for rule in default_rules:
            cursor.execute('''
                INSERT OR IGNORE INTO alert_rules (rule_name, metric_name, threshold, severity, description)
                VALUES (?, ?, ?, ?, ?)
            ''', rule)
    
    def check_metrics(self, metrics: Dict) -> List[Alert]:
        """Check metrics against thresholds and generate alerts"""
        alerts = []
        
        # Get active alert rules
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT rule_name, metric_name, threshold, severity FROM alert_rules WHERE enabled = 1')
        rules = cursor.fetchall()
        conn.close()
        
        for rule_name, metric_name, threshold, severity in rules:
            if metric_name in metrics:
                metric_value = metrics[metric_name]
                
                # Check if threshold is exceeded
                if metric_value >= threshold:
                    # Check if this alert was already triggered recently (avoid spam)
                    if not self._is_recent_alert(rule_name, metric_value):
                        alert = Alert(
                            id=None,
                            timestamp=time.time(),
                            alert_type=rule_name,
                            metric_name=metric_name,
                            metric_value=metric_value,
                            threshold=threshold,
                            severity=AlertSeverity(severity),
                            message=f"{rule_name}: {metric_name} = {metric_value:.1f} (threshold: {threshold:.1f})"
                        )
                        alerts.append(alert)
        
        return alerts
    
    def _is_recent_alert(self, rule_name: str, metric_value: float) -> bool:
        """Check if this alert was recently triggered to avoid spam"""
        # Simple implementation: check if same rule was triggered in last 5 minutes
        recent_time = time.time() - 300  # 5 minutes
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM alerts 
            WHERE alert_type = ? AND timestamp > ? AND metric_value >= ?
        ''', (rule_name, recent_time, metric_value))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def save_alerts(self, alerts: List[Alert]):
        """Save alerts to database"""
        if not alerts:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for alert in alerts:
            cursor.execute('''
                INSERT INTO alerts (
                    timestamp, alert_type, metric_name, metric_value, 
                    threshold, severity, message
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert.timestamp, alert.alert_type, alert.metric_name, alert.metric_value,
                alert.threshold, alert.severity.value, alert.message
            ))
            
            # Get the inserted alert ID
            alert.id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        # Store in recent alerts
        self.recent_alerts.extend(alerts)
        
        # Keep only last 100 alerts in memory
        if len(self.recent_alerts) > 100:
            self.recent_alerts = self.recent_alerts[-100:]
    
    def display_alerts(self, alerts: List[Alert] = None):
        """Display alerts in a formatted table"""
        if not RICH_AVAILABLE:
            print("Rich library required for formatted display")
            return
        
        if alerts is None:
            alerts = self.recent_alerts[-10:]  # Show last 10 alerts
        
        if not alerts:
            self.console.print("[green]No active alerts[/green]")
            return
        
        # Create alerts table
        table = Table(title="System Alerts")
        table.add_column("Time", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Metric", style="green")
        table.add_column("Value", style="magenta")
        table.add_column("Threshold", style="blue")
        table.add_column("Severity", style="red")
        table.add_column("Status", style="white")
        
        for alert in alerts:
            # Format timestamp
            dt = datetime.fromtimestamp(alert.timestamp)
            time_str = dt.strftime("%H:%M:%S")
            
            # Severity color
            severity_color = {
                AlertSeverity.INFO: "blue",
                AlertSeverity.WARNING: "yellow", 
                AlertSeverity.CRITICAL: "red"
            }.get(alert.severity, "white")
            
            # Status
            status = "✅ Acknowledged" if alert.acknowledged else "⚠️ Active"
            
            table.add_row(
                time_str,
                alert.alert_type,
                alert.metric_name,
                f"{alert.metric_value:.1f}",
                f"{alert.threshold:.1f}",
                f"[{severity_color}]{alert.severity.value.upper()}[/{severity_color}]",
                status
            )
        
        self.console.print(table)
    
    def acknowledge_alert(self, alert_id: int, acknowledged_by: str = "user"):
        """Acknowledge an alert"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE alerts 
            SET acknowledged = 1, acknowledged_by = ?, acknowledged_at = ?
            WHERE id = ?
        ''', (acknowledged_by, time.time(), alert_id))
        
        conn.commit()
        conn.close()
        
        # Update in memory
        for alert in self.recent_alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_by = acknowledged_by
                alert.acknowledged_at = time.time()
                break
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unacknowledged) alerts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, timestamp, alert_type, metric_name, metric_value, 
                   threshold, severity, message, acknowledged, acknowledged_by, acknowledged_at
            FROM alerts 
            WHERE acknowledged = 0
            ORDER BY timestamp DESC
        ''')
        
        alerts = []
        for row in cursor.fetchall():
            alert = Alert(
                id=row[0],
                timestamp=row[1],
                alert_type=row[2],
                metric_name=row[3],
                metric_value=row[4],
                threshold=row[5],
                severity=AlertSeverity(row[6]),
                message=row[7],
                acknowledged=bool(row[8]),
                acknowledged_by=row[9],
                acknowledged_at=row[10]
            )
            alerts.append(alert)
        
        conn.close()
        return alerts
    
    def get_alert_summary(self) -> Dict:
        """Get alert summary statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total alerts
        cursor.execute('SELECT COUNT(*) FROM alerts')
        total_alerts = cursor.fetchone()[0]
        
        # Active alerts
        cursor.execute('SELECT COUNT(*) FROM alerts WHERE acknowledged = 0')
        active_alerts = cursor.fetchone()[0]
        
        # Alerts by severity
        cursor.execute('''
            SELECT severity, COUNT(*) 
            FROM alerts 
            GROUP BY severity
        ''')
        severity_counts = dict(cursor.fetchall())
        
        # Recent alerts (last 24 hours)
        recent_time = time.time() - 86400  # 24 hours
        cursor.execute('SELECT COUNT(*) FROM alerts WHERE timestamp > ?', (recent_time,))
        recent_alerts = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'severity_counts': severity_counts,
            'recent_alerts_24h': recent_alerts
        }
    
    def add_alert_callback(self, callback):
        """Add a callback function to be called when alerts are triggered"""
        self.alert_callbacks.append(callback)
    
    def notify_alerts(self, alerts: List[Alert]):
        """Notify about new alerts using callbacks"""
        for callback in self.alert_callbacks:
            try:
                callback(alerts)
            except Exception as e:
                if self.console:
                    self.console.print(f"[red]Alert callback error: {e}[/red]")
    
    def create_alert_rule(self, rule_name: str, metric_name: str, threshold: float, 
                         severity: AlertSeverity, description: str = ""):
        """Create a new alert rule"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alert_rules (rule_name, metric_name, threshold, severity, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (rule_name, metric_name, threshold, severity.value, description))
        
        conn.commit()
        conn.close()
        
        if self.console:
            self.console.print(f"[green]Created alert rule: {rule_name}[/green]")
    
    def enable_alert_rule(self, rule_name: str, enabled: bool = True):
        """Enable or disable an alert rule"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE alert_rules 
            SET enabled = ? 
            WHERE rule_name = ?
        ''', (1 if enabled else 0, rule_name))
        
        conn.commit()
        conn.close()
        
        status = "enabled" if enabled else "disabled"
        if self.console:
            self.console.print(f"[green]Alert rule '{rule_name}' {status}[/green]")
    
    def get_alert_rules(self) -> List[Dict]:
        """Get all alert rules"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT rule_name, metric_name, threshold, severity, enabled, description
            FROM alert_rules
            ORDER BY rule_name
        ''')
        
        rules = []
        for row in cursor.fetchall():
            rules.append({
                'rule_name': row[0],
                'metric_name': row[1],
                'threshold': row[2],
                'severity': row[3],
                'enabled': bool(row[4]),
                'description': row[5]
            })
        
        conn.close()
        return rules
    
    def display_alert_rules(self):
        """Display alert rules in a formatted table"""
        if not RICH_AVAILABLE:
            print("Rich library required for formatted display")
            return
        
        rules = self.get_alert_rules()
        
        if not rules:
            self.console.print("[yellow]No alert rules configured[/yellow]")
            return
        
        # Create rules table
        table = Table(title="Alert Rules")
        table.add_column("Rule Name", style="cyan")
        table.add_column("Metric", style="green")
        table.add_column("Threshold", style="yellow")
        table.add_column("Severity", style="magenta")
        table.add_column("Status", style="blue")
        table.add_column("Description", style="white")
        
        for rule in rules:
            status = "✅ Enabled" if rule['enabled'] else "❌ Disabled"
            severity_color = {
                'info': 'blue',
                'warning': 'yellow',
                'critical': 'red'
            }.get(rule['severity'], 'white')
            
            table.add_row(
                rule['rule_name'],
                rule['metric_name'],
                f"{rule['threshold']:.1f}",
                f"[{severity_color}]{rule['severity'].upper()}[/{severity_color}]",
                status,
                rule['description']
            )
        
        self.console.print(table)

def main():
    """Main function for standalone testing"""
    alert_manager = AlertManager()
    
    print("🚨 Alert Manager")
    print("=" * 50)
    
    # Display alert rules
    alert_manager.display_alert_rules()
    
    # Display alert summary
    summary = alert_manager.get_alert_summary()
    print(f"\n📊 Alert Summary:")
    print(f"  Total alerts: {summary['total_alerts']}")
    print(f"  Active alerts: {summary['active_alerts']}")
    print(f"  Recent alerts (24h): {summary['recent_alerts_24h']}")
    
    # Display recent alerts
    print(f"\n🔔 Recent Alerts:")
    alert_manager.display_alerts()

if __name__ == "__main__":
    main() 