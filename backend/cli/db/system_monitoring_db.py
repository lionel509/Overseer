"""
System Monitoring Database Manager
Centralized database management for all system monitoring features.
"""

import os
import sqlite3
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class SystemMonitoringDB:
    """Centralized database manager for system monitoring"""
    
    def __init__(self):
        # Database paths - all stored in the db/ directory
        self.db_dir = os.path.join(os.path.dirname(__file__), '../../db')
        os.makedirs(self.db_dir, exist_ok=True)
        
        # System monitoring databases
        self.system_metrics_db = os.path.join(self.db_dir, 'system_metrics.db')
        self.system_alerts_db = os.path.join(self.db_dir, 'system_alerts.db')
        self.advanced_analytics_db = os.path.join(self.db_dir, 'advanced_analytics.db')
        self.custom_alert_rules_db = os.path.join(self.db_dir, 'custom_alert_rules.db')
        self.unified_system_db = os.path.join(self.db_dir, 'unified_system.db')
        self.memory_analytics_db = os.path.join(self.db_dir, 'memory_analytics.db')
        self.performance_baselines_db = os.path.join(self.db_dir, 'performance_baselines.db')
        
        # Initialize all databases
        self._init_all_databases()
    
    def _init_all_databases(self):
        """Initialize all system monitoring databases"""
        self._init_system_metrics_db()
        self._init_system_alerts_db()
        self._init_advanced_analytics_db()
        self._init_custom_alert_rules_db()
        self._init_unified_system_db()
        self._init_memory_analytics_db()
        self._init_performance_baselines_db()
    
    def _init_system_metrics_db(self):
        """Initialize system metrics database"""
        try:
            conn = sqlite3.connect(self.system_metrics_db)
            cursor = conn.cursor()
            
            # System metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    cpu_percent REAL,
                    memory_percent REAL,
                    memory_used_gb REAL,
                    memory_total_gb REAL,
                    disk_percent REAL,
                    disk_used_gb REAL,
                    disk_total_gb REAL,
                    swap_percent REAL,
                    swap_used_gb REAL,
                    swap_total_gb REAL,
                    network_sent_mb REAL,
                    network_recv_mb REAL,
                    process_count INTEGER,
                    load_average_1 REAL,
                    load_average_5 REAL,
                    load_average_15 REAL,
                    temperature REAL,
                    battery_percent REAL,
                    battery_plugged INTEGER
                )
            ''')
            
            # Add missing columns if they don't exist
            try:
                cursor.execute('ALTER TABLE system_metrics ADD COLUMN swap_percent REAL')
            except Exception:
                pass  # Column already exists
            try:
                cursor.execute('ALTER TABLE system_metrics ADD COLUMN swap_used_gb REAL')
            except Exception:
                pass  # Column already exists
            try:
                cursor.execute('ALTER TABLE system_metrics ADD COLUMN swap_total_gb REAL')
            except Exception:
                pass  # Column already exists
            try:
                cursor.execute('ALTER TABLE system_metrics ADD COLUMN network_sent_mb REAL')
            except Exception:
                pass  # Column already exists
            try:
                cursor.execute('ALTER TABLE system_metrics ADD COLUMN network_recv_mb REAL')
            except Exception:
                pass  # Column already exists
            try:
                cursor.execute('ALTER TABLE system_metrics ADD COLUMN process_count INTEGER')
            except Exception:
                pass  # Column already exists
            try:
                cursor.execute('ALTER TABLE system_metrics ADD COLUMN load_average_1 REAL')
            except Exception:
                pass  # Column already exists
            try:
                cursor.execute('ALTER TABLE system_metrics ADD COLUMN load_average_5 REAL')
            except Exception:
                pass  # Column already exists
            try:
                cursor.execute('ALTER TABLE system_metrics ADD COLUMN load_average_15 REAL')
            except Exception:
                pass  # Column already exists
            try:
                cursor.execute('ALTER TABLE system_metrics ADD COLUMN temperature REAL')
            except Exception:
                pass  # Column already exists
            try:
                cursor.execute('ALTER TABLE system_metrics ADD COLUMN battery_percent REAL')
            except Exception:
                pass  # Column already exists
            try:
                cursor.execute('ALTER TABLE system_metrics ADD COLUMN battery_plugged INTEGER')
            except Exception:
                pass  # Column already exists
            
            # Process metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS process_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    pid INTEGER,
                    name TEXT,
                    memory_percent REAL,
                    memory_mb REAL,
                    cpu_percent REAL,
                    status TEXT,
                    age_hours REAL,
                    threads INTEGER
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error initializing system metrics database: {e}")
    
    def _init_system_alerts_db(self):
        """Initialize system alerts database"""
        try:
            conn = sqlite3.connect(self.system_alerts_db)
            cursor = conn.cursor()
            
            # System alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    alert_type TEXT,
                    severity TEXT,
                    message TEXT,
                    metric_name TEXT,
                    metric_value REAL,
                    threshold REAL,
                    resolved INTEGER DEFAULT 0,
                    resolution_time REAL
                )
            ''')
            
            # Alert history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alert_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id INTEGER,
                    timestamp REAL,
                    action TEXT,
                    details TEXT,
                    FOREIGN KEY (alert_id) REFERENCES system_alerts (id)
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error initializing system alerts database: {e}")
    
    def _init_advanced_analytics_db(self):
        """Initialize advanced analytics database"""
        try:
            conn = sqlite3.connect(self.advanced_analytics_db)
            cursor = conn.cursor()
            
            # Performance insights table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    insight_type TEXT,
                    severity TEXT,
                    description TEXT,
                    metric_name TEXT,
                    metric_value REAL,
                    baseline_value REAL,
                    deviation_percent REAL,
                    recommendation TEXT
                )
            ''')
            
            # Add missing columns if they don't exist
            try:
                cursor.execute('ALTER TABLE performance_insights ADD COLUMN metric_value REAL')
            except Exception:
                pass  # Column already exists
            try:
                cursor.execute('ALTER TABLE performance_insights ADD COLUMN baseline_value REAL')
            except Exception:
                pass  # Column already exists
            try:
                cursor.execute('ALTER TABLE performance_insights ADD COLUMN deviation_percent REAL')
            except Exception:
                pass  # Column already exists
            try:
                cursor.execute('ALTER TABLE performance_insights ADD COLUMN recommendation TEXT')
            except Exception:
                pass  # Column already exists
            
            # System correlations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_correlations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    metric1 TEXT,
                    metric2 TEXT,
                    correlation_coefficient REAL,
                    significance_level REAL,
                    description TEXT
                )
            ''')
            
            # Performance baselines table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_baselines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT,
                    baseline_value REAL,
                    min_value REAL,
                    max_value REAL,
                    std_deviation REAL,
                    sample_count INTEGER,
                    last_updated REAL
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error initializing advanced analytics database: {e}")
    
    def _init_custom_alert_rules_db(self):
        """Initialize custom alert rules database"""
        try:
            conn = sqlite3.connect(self.custom_alert_rules_db)
            cursor = conn.cursor()
            
            # Custom alert rules table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS custom_alert_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    description TEXT,
                    metric_name TEXT,
                    operator TEXT,
                    threshold REAL,
                    severity TEXT,
                    enabled INTEGER DEFAULT 1,
                    created_at REAL,
                    last_triggered REAL
                )
            ''')
            
            # Complex rules table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS complex_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    description TEXT,
                    rule_expression TEXT,
                    severity TEXT,
                    enabled INTEGER DEFAULT 1,
                    created_at REAL,
                    last_triggered REAL
                )
            ''')
            
            # Rule escalations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rule_escalations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_id INTEGER,
                    escalation_type TEXT,
                    action TEXT,
                    parameters TEXT,
                    delay_minutes INTEGER,
                    enabled INTEGER DEFAULT 1,
                    FOREIGN KEY (rule_id) REFERENCES custom_alert_rules (id)
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error initializing custom alert rules database: {e}")
    
    def _init_unified_system_db(self):
        """Initialize unified system database"""
        try:
            conn = sqlite3.connect(self.unified_system_db)
            cursor = conn.cursor()
            
            # Unified system state table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS unified_system_state (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    cpu_usage REAL,
                    memory_usage REAL,
                    disk_usage REAL,
                    network_usage REAL,
                    temperature REAL,
                    battery_level REAL,
                    system_load REAL,
                    process_count INTEGER,
                    alert_count INTEGER,
                    performance_score REAL
                )
            ''')
            
            # System events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    event_type TEXT,
                    severity TEXT,
                    description TEXT,
                    affected_components TEXT,
                    resolution_status TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error initializing unified system database: {e}")
    
    def _init_memory_analytics_db(self):
        """Initialize memory analytics database"""
        try:
            conn = sqlite3.connect(self.memory_analytics_db)
            cursor = conn.cursor()
            
            # Memory usage patterns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    total_memory_gb REAL,
                    used_memory_gb REAL,
                    available_memory_gb REAL,
                    memory_percent REAL,
                    swap_percent REAL,
                    swap_used_gb REAL,
                    high_memory_processes INTEGER,
                    potential_memory_leaks INTEGER,
                    long_running_processes INTEGER
                )
            ''')
            
            # Memory leak detection table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory_leak_detection (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    process_name TEXT,
                    pid INTEGER,
                    memory_percent REAL,
                    memory_mb REAL,
                    age_hours REAL,
                    leak_probability REAL,
                    recommendation TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error initializing memory analytics database: {e}")
    
    def _init_performance_baselines_db(self):
        """Initialize performance baselines database"""
        try:
            conn = sqlite3.connect(self.performance_baselines_db)
            cursor = conn.cursor()
            
            # Performance baselines table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_baselines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT,
                    baseline_value REAL,
                    min_value REAL,
                    max_value REAL,
                    std_deviation REAL,
                    sample_count INTEGER,
                    last_updated REAL,
                    baseline_type TEXT
                )
            ''')
            
            # Performance thresholds table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_thresholds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT,
                    warning_threshold REAL,
                    critical_threshold REAL,
                    excellent_threshold REAL,
                    good_threshold REAL,
                    fair_threshold REAL,
                    poor_threshold REAL
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error initializing performance baselines database: {e}")
    
    def save_system_metrics(self, metrics: Dict):
        """Save system metrics to database"""
        try:
            conn = sqlite3.connect(self.system_metrics_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_metrics (
                    timestamp, cpu_percent, memory_percent, memory_used_gb, memory_total_gb,
                    disk_percent, disk_used_gb, disk_total_gb, swap_percent, swap_used_gb, swap_total_gb,
                    network_sent_mb, network_recv_mb, process_count, load_average_1, load_average_5, load_average_15,
                    temperature, battery_percent, battery_plugged
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.get('timestamp', time.time()),
                metrics.get('cpu_percent', 0),
                metrics.get('memory_percent', 0),
                metrics.get('memory_used_gb', 0),
                metrics.get('memory_total_gb', 0),
                metrics.get('disk_percent', 0),
                metrics.get('disk_used_gb', 0),
                metrics.get('disk_total_gb', 0),
                metrics.get('swap_percent', 0),
                metrics.get('swap_used_gb', 0),
                metrics.get('swap_total_gb', 0),
                metrics.get('network_sent_mb', 0),
                metrics.get('network_recv_mb', 0),
                metrics.get('process_count', 0),
                metrics.get('load_average_1', 0),
                metrics.get('load_average_5', 0),
                metrics.get('load_average_15', 0),
                metrics.get('temperature', 0),
                metrics.get('battery_percent', 0),
                metrics.get('battery_plugged', 0)
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving system metrics: {e}")
    
    def save_process_metrics(self, processes: List[Dict]):
        """Save process metrics to database"""
        try:
            conn = sqlite3.connect(self.system_metrics_db)
            cursor = conn.cursor()
            timestamp = time.time()
            
            for process in processes:
                cursor.execute('''
                    INSERT INTO process_metrics (
                        timestamp, pid, name, memory_percent, memory_mb, cpu_percent, status, age_hours, threads
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    timestamp,
                    process.get('pid', 0),
                    process.get('name', ''),
                    process.get('memory_percent', 0),
                    process.get('memory_mb', 0),
                    process.get('cpu_percent', 0),
                    process.get('status', ''),
                    process.get('age_hours', 0),
                    process.get('threads', 0)
                ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving process metrics: {e}")
    
    def save_system_alert(self, alert: Dict):
        """Save system alert to database"""
        try:
            conn = sqlite3.connect(self.system_alerts_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_alerts (
                    timestamp, alert_type, severity, message, metric_name, metric_value, threshold
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert.get('timestamp', time.time()),
                alert.get('alert_type', ''),
                alert.get('severity', ''),
                alert.get('message', ''),
                alert.get('metric_name', ''),
                alert.get('metric_value', 0),
                alert.get('threshold', 0)
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving system alert: {e}")
    
    def save_performance_insight(self, insight: Dict):
        """Save performance insight to database"""
        try:
            conn = sqlite3.connect(self.advanced_analytics_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_insights (
                    timestamp, insight_type, severity, description, metric_name, metric_value, baseline_value, deviation_percent, recommendation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                insight.get('timestamp', time.time()),
                insight.get('insight_type', ''),
                insight.get('severity', ''),
                insight.get('description', ''),
                insight.get('metric_name', ''),
                insight.get('metric_value', 0),
                insight.get('baseline_value', 0),
                insight.get('deviation_percent', 0),
                insight.get('recommendation', '')
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving performance insight: {e}")
    
    def save_memory_pattern(self, pattern: Dict):
        """Save memory usage pattern to database"""
        try:
            conn = sqlite3.connect(self.memory_analytics_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO memory_patterns (
                    timestamp, total_memory_gb, used_memory_gb, available_memory_gb, memory_percent,
                    swap_percent, swap_used_gb, high_memory_processes, potential_memory_leaks, long_running_processes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pattern.get('timestamp', time.time()),
                pattern.get('total_memory_gb', 0),
                pattern.get('used_memory_gb', 0),
                pattern.get('available_memory_gb', 0),
                pattern.get('memory_percent', 0),
                pattern.get('swap_percent', 0),
                pattern.get('swap_used_gb', 0),
                pattern.get('high_memory_processes', 0),
                pattern.get('potential_memory_leaks', 0),
                pattern.get('long_running_processes', 0)
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving memory pattern: {e}")
    
    def get_recent_system_metrics(self, hours: int = 24) -> List[Dict]:
        """Get recent system metrics from database"""
        try:
            conn = sqlite3.connect(self.system_metrics_db)
            cursor = conn.cursor()
            
            cutoff_time = time.time() - (hours * 3600)
            cursor.execute('''
                SELECT * FROM system_metrics 
                WHERE timestamp > ? 
                ORDER BY timestamp DESC
            ''', (cutoff_time,))
            
            columns = [description[0] for description in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            conn.close()
            return results
        except Exception as e:
            print(f"Error getting recent system metrics: {e}")
            return []
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict]:
        """Get recent system alerts from database"""
        try:
            conn = sqlite3.connect(self.system_alerts_db)
            cursor = conn.cursor()
            
            cutoff_time = time.time() - (hours * 3600)
            cursor.execute('''
                SELECT * FROM system_alerts 
                WHERE timestamp > ? 
                ORDER BY timestamp DESC
            ''', (cutoff_time,))
            
            columns = [description[0] for description in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            conn.close()
            return results
        except Exception as e:
            print(f"Error getting recent alerts: {e}")
            return []
    
    def get_performance_baselines(self) -> Dict:
        """Get performance baselines from database"""
        try:
            conn = sqlite3.connect(self.performance_baselines_db)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM performance_baselines')
            columns = [description[0] for description in cursor.description]
            results = {}
            for row in cursor.fetchall():
                row_dict = dict(zip(columns, row))
                results[row_dict['metric_name']] = row_dict
            
            conn.close()
            return results
        except Exception as e:
            print(f"Error getting performance baselines: {e}")
            return {}

# Global database manager instance
system_monitoring_db = SystemMonitoringDB() 