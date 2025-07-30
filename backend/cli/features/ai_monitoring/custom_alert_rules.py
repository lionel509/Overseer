"""
Custom Alert Rules for System Monitoring
Allows users to define custom alert thresholds, complex alert conditions, and alert escalation chains.
"""

import os
import sys
import json
import time
import sqlite3
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from alert_manager import AlertManager, AlertSeverity

class AlertCondition(Enum):
    """Alert condition types"""
    GREATER_THAN = ">"
    LESS_THAN = "<"
    EQUAL_TO = "=="
    NOT_EQUAL_TO = "!="
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"

class EscalationLevel(Enum):
    """Escalation levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class CustomAlertRule:
    """Custom alert rule data structure"""
    id: Optional[int]
    name: str
    description: str
    metric_name: str
    condition: AlertCondition
    threshold: float
    severity: AlertSeverity
    enabled: bool
    escalation_enabled: bool
    escalation_delay: int  # minutes
    escalation_levels: List[EscalationLevel]
    notification_channels: List[str]
    custom_message: Optional[str]
    created_at: float
    last_triggered: Optional[float]

@dataclass
class ComplexAlertRule:
    """Complex alert rule with multiple conditions"""
    id: Optional[int]
    name: str
    description: str
    conditions: List[Dict]  # List of condition dictionaries
    operator: str  # 'AND' or 'OR'
    severity: AlertSeverity
    enabled: bool
    escalation_enabled: bool
    escalation_delay: int
    escalation_levels: List[EscalationLevel]
    notification_channels: List[str]
    custom_message: Optional[str]
    created_at: float
    last_triggered: Optional[float]

@dataclass
class AlertEscalation:
    """Alert escalation data structure"""
    id: Optional[int]
    alert_id: int
    rule_name: str
    escalation_level: EscalationLevel
    triggered_at: float
    message: str
    notification_sent: bool
    acknowledged: bool
    acknowledged_by: Optional[str]
    acknowledged_at: Optional[float]

class CustomAlertRules:
    """Custom alert rules manager"""
    
    def __init__(self, db_path: str = None, config: Dict = None):
        """Initialize custom alert rules"""
        self.console = Console() if RICH_AVAILABLE else None
        self.config = config or {}
        
        # Initialize components
        self.alert_manager = AlertManager()
        
        # Database setup
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '../../db/custom_alert_rules.db')
        self.db_path = db_path
        self._init_database()
        
        # Notification channels
        self.notification_channels = {
            'console': self._console_notification,
            'email': self._email_notification,
            'slack': self._slack_notification,
            'webhook': self._webhook_notification
        }
    
    def _init_database(self):
        """Initialize custom alert rules database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Custom alert rules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_alert_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                description TEXT,
                metric_name TEXT,
                condition TEXT,
                threshold REAL,
                severity TEXT,
                enabled INTEGER DEFAULT 1,
                escalation_enabled INTEGER DEFAULT 0,
                escalation_delay INTEGER DEFAULT 5,
                escalation_levels TEXT,
                notification_channels TEXT,
                custom_message TEXT,
                created_at REAL,
                last_triggered REAL
            )
        ''')
        
        # Complex alert rules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS complex_alert_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                description TEXT,
                conditions TEXT,
                operator TEXT,
                severity TEXT,
                enabled INTEGER DEFAULT 1,
                escalation_enabled INTEGER DEFAULT 0,
                escalation_delay INTEGER DEFAULT 5,
                escalation_levels TEXT,
                notification_channels TEXT,
                custom_message TEXT,
                created_at REAL,
                last_triggered REAL
            )
        ''')
        
        # Alert escalations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_escalations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id INTEGER,
                rule_name TEXT,
                escalation_level TEXT,
                triggered_at REAL,
                message TEXT,
                notification_sent INTEGER DEFAULT 0,
                acknowledged INTEGER DEFAULT 0,
                acknowledged_by TEXT,
                acknowledged_at REAL
            )
        ''')
        
        # Notification history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notification_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_name TEXT,
                alert_id INTEGER,
                channel TEXT,
                message TEXT,
                sent_at REAL,
                success INTEGER DEFAULT 0,
                error_message TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_custom_rule(self, name: str, description: str, metric_name: str, 
                          condition: AlertCondition, threshold: float, severity: AlertSeverity,
                          escalation_enabled: bool = False, escalation_delay: int = 5,
                          escalation_levels: List[EscalationLevel] = None,
                          notification_channels: List[str] = None,
                          custom_message: str = None) -> CustomAlertRule:
        """Create a new custom alert rule"""
        
        if escalation_levels is None:
            escalation_levels = [EscalationLevel.WARNING, EscalationLevel.CRITICAL]
        
        if notification_channels is None:
            notification_channels = ['console']
        
        rule = CustomAlertRule(
            id=None,
            name=name,
            description=description,
            metric_name=metric_name,
            condition=condition,
            threshold=threshold,
            severity=severity,
            enabled=True,
            escalation_enabled=escalation_enabled,
            escalation_delay=escalation_delay,
            escalation_levels=escalation_levels,
            notification_channels=notification_channels,
            custom_message=custom_message,
            created_at=time.time(),
            last_triggered=None
        )
        
        # Save to database
        self._save_custom_rule(rule)
        
        return rule
    
    def _save_custom_rule(self, rule: CustomAlertRule):
        """Save custom rule to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO custom_alert_rules (
                    name, description, metric_name, condition, threshold, severity,
                    enabled, escalation_enabled, escalation_delay, escalation_levels,
                    notification_channels, custom_message, created_at, last_triggered
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                rule.name, rule.description, rule.metric_name, rule.condition.value,
                rule.threshold, rule.severity.value, rule.enabled, rule.escalation_enabled,
                rule.escalation_delay, json.dumps([level.value for level in rule.escalation_levels]),
                json.dumps(rule.notification_channels), rule.custom_message,
                rule.created_at, rule.last_triggered
            ))
            
            rule.id = cursor.lastrowid
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error saving custom rule: {e}[/red]")
    
    def create_complex_rule(self, name: str, description: str, conditions: List[Dict],
                           operator: str, severity: AlertSeverity,
                           escalation_enabled: bool = False, escalation_delay: int = 5,
                           escalation_levels: List[EscalationLevel] = None,
                           notification_channels: List[str] = None,
                           custom_message: str = None) -> ComplexAlertRule:
        """Create a new complex alert rule with multiple conditions"""
        
        if escalation_levels is None:
            escalation_levels = [EscalationLevel.WARNING, EscalationLevel.CRITICAL]
        
        if notification_channels is None:
            notification_channels = ['console']
        
        rule = ComplexAlertRule(
            id=None,
            name=name,
            description=description,
            conditions=conditions,
            operator=operator,
            severity=severity,
            enabled=True,
            escalation_enabled=escalation_enabled,
            escalation_delay=escalation_delay,
            escalation_levels=escalation_levels,
            notification_channels=notification_channels,
            custom_message=custom_message,
            created_at=time.time(),
            last_triggered=None
        )
        
        # Save to database
        self._save_complex_rule(rule)
        
        return rule
    
    def _save_complex_rule(self, rule: ComplexAlertRule):
        """Save complex rule to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO complex_alert_rules (
                    name, description, conditions, operator, severity,
                    enabled, escalation_enabled, escalation_delay, escalation_levels,
                    notification_channels, custom_message, created_at, last_triggered
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                rule.name, rule.description, json.dumps(rule.conditions),
                rule.operator, rule.severity.value, rule.enabled, rule.escalation_enabled,
                rule.escalation_delay, json.dumps([level.value for level in rule.escalation_levels]),
                json.dumps(rule.notification_channels), rule.custom_message,
                rule.created_at, rule.last_triggered
            ))
            
            rule.id = cursor.lastrowid
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error saving complex rule: {e}[/red]")
    
    def get_custom_rules(self) -> List[CustomAlertRule]:
        """Get all custom alert rules"""
        rules = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM custom_alert_rules ORDER BY created_at DESC')
            rows = cursor.fetchall()
            
            for row in rows:
                rule = CustomAlertRule(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    metric_name=row[3],
                    condition=AlertCondition(row[4]),
                    threshold=row[5],
                    severity=AlertSeverity(row[6]),
                    enabled=bool(row[7]),
                    escalation_enabled=bool(row[8]),
                    escalation_delay=row[9],
                    escalation_levels=[EscalationLevel(level) for level in json.loads(row[10])],
                    notification_channels=json.loads(row[11]),
                    custom_message=row[12],
                    created_at=row[13],
                    last_triggered=row[14]
                )
                rules.append(rule)
            
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error getting custom rules: {e}[/red]")
        
        return rules
    
    def get_complex_rules(self) -> List[ComplexAlertRule]:
        """Get all complex alert rules"""
        rules = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM complex_alert_rules ORDER BY created_at DESC')
            rows = cursor.fetchall()
            
            for row in rows:
                rule = ComplexAlertRule(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    conditions=json.loads(row[3]),
                    operator=row[4],
                    severity=AlertSeverity(row[5]),
                    enabled=bool(row[6]),
                    escalation_enabled=bool(row[7]),
                    escalation_delay=row[8],
                    escalation_levels=[EscalationLevel(level) for level in json.loads(row[9])],
                    notification_channels=json.loads(row[10]),
                    custom_message=row[11],
                    created_at=row[12],
                    last_triggered=row[13]
                )
                rules.append(rule)
            
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error getting complex rules: {e}[/red]")
        
        return rules
    
    def check_custom_rules(self, metrics: Dict[str, float]) -> List[Dict]:
        """Check custom rules against current metrics"""
        triggered_rules = []
        custom_rules = self.get_custom_rules()
        
        for rule in custom_rules:
            if not rule.enabled:
                continue
            
            if rule.metric_name not in metrics:
                continue
            
            current_value = metrics[rule.metric_name]
            triggered = self._evaluate_condition(current_value, rule.condition, rule.threshold)
            
            if triggered:
                # Create alert
                alert = {
                    'rule_name': rule.name,
                    'metric_name': rule.metric_name,
                    'current_value': current_value,
                    'threshold': rule.threshold,
                    'condition': rule.condition.value,
                    'severity': rule.severity,
                    'message': rule.custom_message or f"{rule.description}: {current_value} {rule.condition.value} {rule.threshold}",
                    'timestamp': time.time()
                }
                
                triggered_rules.append(alert)
                
                # Update last triggered time
                self._update_rule_last_triggered(rule.id, time.time())
                
                # Send notifications
                self._send_notifications(rule, alert)
                
                # Handle escalation
                if rule.escalation_enabled:
                    self._handle_escalation(rule, alert)
        
        return triggered_rules
    
    def check_complex_rules(self, metrics: Dict[str, float]) -> List[Dict]:
        """Check complex rules against current metrics"""
        triggered_rules = []
        complex_rules = self.get_complex_rules()
        
        for rule in complex_rules:
            if not rule.enabled:
                continue
            
            # Evaluate all conditions
            condition_results = []
            for condition in rule.conditions:
                metric_name = condition['metric_name']
                if metric_name not in metrics:
                    continue
                
                current_value = metrics[metric_name]
                condition_result = self._evaluate_condition(
                    current_value, 
                    AlertCondition(condition['condition']), 
                    condition['threshold']
                )
                condition_results.append(condition_result)
            
            # Apply operator (AND/OR)
            if rule.operator == 'AND':
                triggered = all(condition_results)
            else:  # OR
                triggered = any(condition_results)
            
            if triggered:
                # Create alert
                alert = {
                    'rule_name': rule.name,
                    'conditions': rule.conditions,
                    'operator': rule.operator,
                    'severity': rule.severity,
                    'message': rule.custom_message or f"Complex rule '{rule.name}' triggered",
                    'timestamp': time.time()
                }
                
                triggered_rules.append(alert)
                
                # Update last triggered time
                self._update_complex_rule_last_triggered(rule.id, time.time())
                
                # Send notifications
                self._send_complex_notifications(rule, alert)
                
                # Handle escalation
                if rule.escalation_enabled:
                    self._handle_complex_escalation(rule, alert)
        
        return triggered_rules
    
    def _evaluate_condition(self, value: float, condition: AlertCondition, threshold: float) -> bool:
        """Evaluate a single condition"""
        if condition == AlertCondition.GREATER_THAN:
            return value > threshold
        elif condition == AlertCondition.LESS_THAN:
            return value < threshold
        elif condition == AlertCondition.EQUAL_TO:
            return value == threshold
        elif condition == AlertCondition.NOT_EQUAL_TO:
            return value != threshold
        elif condition == AlertCondition.GREATER_EQUAL:
            return value >= threshold
        elif condition == AlertCondition.LESS_EQUAL:
            return value <= threshold
        else:
            return False
    
    def _update_rule_last_triggered(self, rule_id: int, timestamp: float):
        """Update rule's last triggered time"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE custom_alert_rules 
                SET last_triggered = ? 
                WHERE id = ?
            ''', (timestamp, rule_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error updating rule: {e}[/red]")
    
    def _update_complex_rule_last_triggered(self, rule_id: int, timestamp: float):
        """Update complex rule's last triggered time"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE complex_alert_rules 
                SET last_triggered = ? 
                WHERE id = ?
            ''', (timestamp, rule_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error updating complex rule: {e}[/red]")
    
    def _send_notifications(self, rule: CustomAlertRule, alert: Dict):
        """Send notifications for triggered rule"""
        for channel in rule.notification_channels:
            if channel in self.notification_channels:
                try:
                    self.notification_channels[channel](rule, alert)
                except Exception as e:
                    if self.console:
                        self.console.print(f"[red]Error sending {channel} notification: {e}[/red]")
    
    def _send_complex_notifications(self, rule: ComplexAlertRule, alert: Dict):
        """Send notifications for triggered complex rule"""
        for channel in rule.notification_channels:
            if channel in self.notification_channels:
                try:
                    self.notification_channels[channel](rule, alert)
                except Exception as e:
                    if self.console:
                        self.console.print(f"[red]Error sending {channel} notification: {e}[/red]")
    
    def _handle_escalation(self, rule: CustomAlertRule, alert: Dict):
        """Handle alert escalation"""
        escalation = AlertEscalation(
            id=None,
            alert_id=alert.get('id', 0),
            rule_name=rule.name,
            escalation_level=rule.escalation_levels[0],  # Start with first level
            triggered_at=time.time(),
            message=alert['message'],
            notification_sent=False,
            acknowledged=False,
            acknowledged_by=None,
            acknowledged_at=None
        )
        
        self._save_escalation(escalation)
    
    def _handle_complex_escalation(self, rule: ComplexAlertRule, alert: Dict):
        """Handle complex alert escalation"""
        escalation = AlertEscalation(
            id=None,
            alert_id=alert.get('id', 0),
            rule_name=rule.name,
            escalation_level=rule.escalation_levels[0],  # Start with first level
            triggered_at=time.time(),
            message=alert['message'],
            notification_sent=False,
            acknowledged=False,
            acknowledged_by=None,
            acknowledged_at=None
        )
        
        self._save_escalation(escalation)
    
    def _save_escalation(self, escalation: AlertEscalation):
        """Save escalation to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alert_escalations (
                    alert_id, rule_name, escalation_level, triggered_at,
                    message, notification_sent, acknowledged, acknowledged_by, acknowledged_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                escalation.alert_id, escalation.rule_name, escalation.escalation_level.value,
                escalation.triggered_at, escalation.message, escalation.notification_sent,
                escalation.acknowledged, escalation.acknowledged_by, escalation.acknowledged_at
            ))
            
            escalation.id = cursor.lastrowid
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error saving escalation: {e}[/red]")
    
    # Notification methods
    def _console_notification(self, rule, alert):
        """Console notification"""
        if self.console:
            severity_color = "red" if rule.severity == AlertSeverity.CRITICAL else "yellow"
            self.console.print(f"[{severity_color}]🚨 ALERT: {alert['message']}[/{severity_color}]")
    
    def _email_notification(self, rule, alert):
        """Email notification (placeholder)"""
        # In a real implementation, this would send actual emails
        if self.console:
            self.console.print(f"[blue]📧 Email notification: {alert['message']}[/blue]")
    
    def _slack_notification(self, rule, alert):
        """Slack notification (placeholder)"""
        # In a real implementation, this would send to Slack
        if self.console:
            self.console.print(f"[blue]💬 Slack notification: {alert['message']}[/blue]")
    
    def _webhook_notification(self, rule, alert):
        """Webhook notification (placeholder)"""
        # In a real implementation, this would send webhook requests
        if self.console:
            self.console.print(f"[blue]🔗 Webhook notification: {alert['message']}[/blue]")
    
    def display_rules(self):
        """Display all custom and complex rules"""
        if not RICH_AVAILABLE:
            print("Rich library required for formatted display")
            return
        
        # Display custom rules
        custom_rules = self.get_custom_rules()
        if custom_rules:
            self.console.print("\n[bold]📋 Custom Alert Rules:[/bold]")
            custom_table = Table(title="Custom Rules")
            custom_table.add_column("Name", style="cyan")
            custom_table.add_column("Metric", style="green")
            custom_table.add_column("Condition", style="yellow")
            custom_table.add_column("Threshold", style="magenta")
            custom_table.add_column("Severity", style="red")
            custom_table.add_column("Enabled", style="blue")
            
            for rule in custom_rules:
                enabled_color = "green" if rule.enabled else "red"
                custom_table.add_row(
                    rule.name,
                    rule.metric_name,
                    rule.condition.value,
                    str(rule.threshold),
                    rule.severity.value.upper(),
                    f"[{enabled_color}]{'YES' if rule.enabled else 'NO'}[/{enabled_color}]"
                )
            
            self.console.print(custom_table)
        
        # Display complex rules
        complex_rules = self.get_complex_rules()
        if complex_rules:
            self.console.print("\n[bold]🔗 Complex Alert Rules:[/bold]")
            complex_table = Table(title="Complex Rules")
            complex_table.add_column("Name", style="cyan")
            complex_table.add_column("Conditions", style="green")
            complex_table.add_column("Operator", style="yellow")
            complex_table.add_column("Severity", style="red")
            complex_table.add_column("Enabled", style="blue")
            
            for rule in complex_rules:
                enabled_color = "green" if rule.enabled else "red"
                conditions_str = f"{len(rule.conditions)} conditions"
                complex_table.add_row(
                    rule.name,
                    conditions_str,
                    rule.operator,
                    rule.severity.value.upper(),
                    f"[{enabled_color}]{'YES' if rule.enabled else 'NO'}[/{enabled_color}]"
                )
            
            self.console.print(complex_table)

def main():
    """Main function for standalone testing"""
    rules_manager = CustomAlertRules()
    
    print("⚙️ Custom Alert Rules Manager")
    print("=" * 50)
    
    # Create some example rules
    print("Creating example rules...")
    
    # Custom rule for high CPU
    cpu_rule = rules_manager.create_custom_rule(
        name="High CPU Usage",
        description="Alert when CPU usage exceeds threshold",
        metric_name="cpu_percent",
        condition=AlertCondition.GREATER_THAN,
        threshold=80.0,
        severity=AlertSeverity.WARNING,
        escalation_enabled=True,
        notification_channels=['console', 'email']
    )
    
    # Custom rule for high memory
    memory_rule = rules_manager.create_custom_rule(
        name="High Memory Usage",
        description="Alert when memory usage exceeds threshold",
        metric_name="memory_percent",
        condition=AlertCondition.GREATER_THAN,
        threshold=85.0,
        severity=AlertSeverity.CRITICAL,
        escalation_enabled=True,
        notification_channels=['console', 'slack']
    )
    
    # Complex rule for system stress
    complex_rule = rules_manager.create_complex_rule(
        name="System Stress",
        description="Alert when both CPU and memory are high",
        conditions=[
            {'metric_name': 'cpu_percent', 'condition': '>', 'threshold': 70.0},
            {'metric_name': 'memory_percent', 'condition': '>', 'threshold': 80.0}
        ],
        operator='AND',
        severity=AlertSeverity.CRITICAL,
        escalation_enabled=True,
        notification_channels=['console', 'webhook']
    )
    
    print("✅ Example rules created")
    
    # Display rules
    rules_manager.display_rules()
    
    # Test rules with sample metrics
    print("\nTesting rules with sample metrics...")
    sample_metrics = {
        'cpu_percent': 85.0,
        'memory_percent': 90.0,
        'disk_percent': 75.0
    }
    
    triggered_custom = rules_manager.check_custom_rules(sample_metrics)
    triggered_complex = rules_manager.check_complex_rules(sample_metrics)
    
    print(f"✅ Custom rules triggered: {len(triggered_custom)}")
    print(f"✅ Complex rules triggered: {len(triggered_complex)}")

if __name__ == "__main__":
    main() 