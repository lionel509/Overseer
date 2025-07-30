"""
Unified System Monitor - Phase 6 Integration
Integrates all previous phases into a single comprehensive system with optimized performance.
"""

import os
import sys
import time
import json
import threading
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.live import Live
    from rich.layout import Layout
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Import all previous phase components
from system_monitor import SystemMonitor
from enhanced_tool_recommender import EnhancedToolRecommender
from alert_manager import AlertManager
from monitoring_dashboard import MonitoringDashboard
from predictive_analytics import PredictiveAnalytics
from advanced_process_manager import AdvancedProcessManager
from custom_alert_rules import CustomAlertRules
from export_reporting import ExportReporting
from machine_learning_integration import MachineLearningIntegration
from advanced_analytics import AdvancedAnalytics

@dataclass
class SystemState:
    """Unified system state data structure"""
    timestamp: float
    metrics: Optional[Dict] = None
    alerts: List[Dict] = None
    recommendations: List[str] = None
    predictions: Optional[Dict] = None
    insights: List[Dict] = None
    health_score: float = 0.0
    performance_score: float = 0.0
    security_score: float = 0.0

@dataclass
class IntegrationConfig:
    """Integration configuration data structure"""
    enable_monitoring: bool = True
    enable_analytics: bool = True
    enable_ml: bool = True
    enable_export: bool = True
    enable_dashboard: bool = True
    enable_alerts: bool = True
    enable_process_management: bool = True
    refresh_interval: float = 2.0
    max_threads: int = 4
    cache_duration: float = 30.0
    log_level: str = 'INFO'

class UnifiedSystemMonitor:
    """Unified system monitor integrating all previous phases"""
    
    def __init__(self, config: IntegrationConfig = None):
        """Initialize unified system monitor"""
        self.console = Console() if RICH_AVAILABLE else None
        self.config = config or IntegrationConfig()
        
        # Initialize all components
        self.system_monitor = SystemMonitor()
        self.tool_recommender = EnhancedToolRecommender()
        self.alert_manager = AlertManager()
        self.predictive_analytics = PredictiveAnalytics()
        self.process_manager = AdvancedProcessManager()
        self.custom_alerts = CustomAlertRules()
        self.export_reporter = ExportReporting()
        self.ml_integration = MachineLearningIntegration()
        self.advanced_analytics = AdvancedAnalytics()
        
        # State management
        self.current_state = SystemState(timestamp=time.time())
        self.state_history = []
        self.max_history_size = 1000
        
        # Performance optimization
        self.cache = {}
        self.cache_timestamps = {}
        self.thread_pool = ThreadPoolExecutor(max_workers=self.config.max_threads)
        
        # Event callbacks
        self.callbacks = {
            'state_update': [],
            'alert_triggered': [],
            'recommendation_generated': [],
            'performance_anomaly': [],
            'security_issue': []
        }
        
        # Monitoring thread
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Database paths
        self.unified_db = os.path.join(os.path.dirname(__file__), '../../db/unified_system.db')
        self._init_unified_database()
    
    def _init_unified_database(self):
        """Initialize unified system database"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.unified_db)
            cursor = conn.cursor()
            
            # Create unified system state table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS unified_system_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    health_score REAL,
                    performance_score REAL,
                    security_score REAL,
                    metrics_data TEXT,
                    alerts_data TEXT,
                    recommendations_data TEXT,
                    predictions_data TEXT,
                    insights_data TEXT,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            ''')
            
            # Create performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    component_name TEXT NOT NULL,
                    operation_name TEXT NOT NULL,
                    execution_time REAL,
                    memory_usage REAL,
                    cpu_usage REAL,
                    timestamp REAL,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            ''')
            
            # Create integration events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS integration_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    event_data TEXT,
                    severity TEXT,
                    component_name TEXT,
                    timestamp REAL,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error initializing unified database: {e}[/red]")
    
    def start_monitoring(self):
        """Start unified system monitoring"""
        if self.monitoring_active:
            return "Monitoring already active"
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        if self.console:
            self.console.print("[green]✅ Unified system monitoring started[/green]")
        
        return "Unified monitoring started"
    
    def stop_monitoring(self):
        """Stop unified system monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        if self.console:
            self.console.print("[yellow]🛑 Unified system monitoring stopped[/yellow]")
        
        return "Unified monitoring stopped"
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                start_time = time.time()
                
                # Collect system state
                new_state = self._collect_system_state()
                
                # Update current state
                self.current_state = new_state
                
                # Store in history
                self.state_history.append(new_state)
                if len(self.state_history) > self.max_history_size:
                    self.state_history.pop(0)
                
                # Save to database
                self._save_system_state(new_state)
                
                # Trigger callbacks
                self._trigger_callbacks('state_update', new_state)
                
                # Performance tracking
                execution_time = time.time() - start_time
                self._track_performance('unified_monitor', 'state_collection', execution_time)
                
                # Wait for next cycle
                time.sleep(self.config.refresh_interval)
                
            except Exception as e:
                if self.console:
                    self.console.print(f"[red]Error in monitoring loop: {e}[/red]")
                self._log_integration_event('error', f"Monitoring loop error: {e}", 'high', 'unified_monitor')
    
    def _collect_system_state(self) -> SystemState:
        """Collect comprehensive system state from all components"""
        state = SystemState(timestamp=time.time())
        
        try:
            # Collect basic metrics
            if self.config.enable_monitoring:
                state.metrics = self._get_cached_or_fresh('metrics', self.system_monitor.collect_metrics)
                state.health_score = self._calculate_health_score(state.metrics)
                state.performance_score = self._calculate_performance_score(state.metrics)
            
            # Collect alerts
            if self.config.enable_alerts:
                state.alerts = self._get_cached_or_fresh('alerts', self.alert_manager.get_active_alerts)
            
            # Collect recommendations
            if state.metrics:
                state.recommendations = self._get_cached_or_fresh('recommendations', 
                    lambda: self.tool_recommender.recommend_tools("system optimization", state.metrics))
            
            # Collect predictions
            if self.config.enable_analytics and state.metrics:
                state.predictions = self._get_cached_or_fresh('predictions', 
                    lambda: self.predictive_analytics.generate_forecast(state.metrics))
            
            # Collect insights
            if self.config.enable_analytics:
                state.insights = self._get_cached_or_fresh('insights', 
                    lambda: self.advanced_analytics.generate_performance_insights('24h'))
            
            # Calculate security score
            state.security_score = self._calculate_security_score(state)
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error collecting system state: {e}[/red]")
            self._log_integration_event('error', f"State collection error: {e}", 'high', 'unified_monitor')
        
        return state
    
    def _get_cached_or_fresh(self, key: str, getter_func: Callable) -> Any:
        """Get cached data or fetch fresh data"""
        current_time = time.time()
        cache_duration = self.config.cache_duration
        
        # Check if we have valid cached data
        if key in self.cache and key in self.cache_timestamps:
            if current_time - self.cache_timestamps[key] < cache_duration:
                return self.cache[key]
        
        # Fetch fresh data
        try:
            fresh_data = getter_func()
            self.cache[key] = fresh_data
            self.cache_timestamps[key] = current_time
            return fresh_data
        except Exception as e:
            # Return cached data if available, otherwise None
            return self.cache.get(key)
    
    def _calculate_health_score(self, metrics: Dict) -> float:
        """Calculate overall system health score"""
        if not metrics:
            return 0.0
        
        try:
            # Calculate health based on key metrics
            cpu_score = max(0, 100 - metrics.get('cpu_percent', 0))
            memory_score = max(0, 100 - metrics.get('memory_percent', 0))
            disk_score = max(0, 100 - metrics.get('disk_percent', 0))
            
            # Weighted average
            health_score = (cpu_score * 0.4 + memory_score * 0.4 + disk_score * 0.2)
            
            return min(100, max(0, health_score))
            
        except Exception:
            return 50.0  # Default score
    
    def _calculate_performance_score(self, metrics: Dict) -> float:
        """Calculate system performance score"""
        if not metrics:
            return 0.0
        
        try:
            # Performance indicators
            load_avg = metrics.get('load_average', [0, 0, 0])
            avg_load = sum(load_avg) / len(load_avg) if load_avg else 0
            
            # Calculate performance score
            if avg_load < 1.0:
                performance_score = 100
            elif avg_load < 2.0:
                performance_score = 80
            elif avg_load < 5.0:
                performance_score = 60
            else:
                performance_score = 40
            
            return performance_score
            
        except Exception:
            return 50.0  # Default score
    
    def _calculate_security_score(self, state: SystemState) -> float:
        """Calculate system security score"""
        try:
            security_score = 100.0
            
            # Check for critical alerts
            if state.alerts:
                critical_alerts = [a for a in state.alerts if a.get('severity') == 'critical']
                security_score -= len(critical_alerts) * 10
            
            # Check for performance anomalies
            if state.insights:
                security_insights = [i for i in state.insights if 'security' in i.get('description', '').lower()]
                security_score -= len(security_insights) * 5
            
            return max(0, security_score)
            
        except Exception:
            return 75.0  # Default score
    
    def get_comprehensive_report(self) -> Dict:
        """Generate comprehensive system report"""
        try:
            report = {
                'timestamp': time.time(),
                'system_state': asdict(self.current_state),
                'component_status': self._get_component_status(),
                'performance_metrics': self._get_performance_metrics(),
                'recommendations': self._generate_comprehensive_recommendations(),
                'alerts_summary': self._get_alerts_summary(),
                'predictions': self._get_predictions_summary(),
                'insights': self._get_insights_summary()
            }
            
            return report
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error generating comprehensive report: {e}[/red]")
            return {'error': str(e)}
    
    def _get_component_status(self) -> Dict:
        """Get status of all integrated components"""
        return {
            'system_monitor': 'active' if self.config.enable_monitoring else 'disabled',
            'tool_recommender': 'active',
            'alert_manager': 'active' if self.config.enable_alerts else 'disabled',
            'predictive_analytics': 'active' if self.config.enable_analytics else 'disabled',
            'process_manager': 'active' if self.config.enable_process_management else 'disabled',
            'custom_alerts': 'active' if self.config.enable_alerts else 'disabled',
            'export_reporter': 'active' if self.config.enable_export else 'disabled',
            'ml_integration': 'active' if self.config.enable_ml else 'disabled',
            'advanced_analytics': 'active' if self.config.enable_analytics else 'disabled'
        }
    
    def _get_performance_metrics(self) -> Dict:
        """Get performance metrics for all components"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.unified_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT component_name, AVG(execution_time), COUNT(*)
                FROM performance_metrics
                WHERE timestamp > ?
                GROUP BY component_name
            ''', (time.time() - 3600,))  # Last hour
            
            metrics = {}
            for row in cursor.fetchall():
                metrics[row[0]] = {
                    'avg_execution_time': row[1],
                    'operation_count': row[2]
                }
            
            conn.close()
            return metrics
            
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_comprehensive_recommendations(self) -> List[str]:
        """Generate comprehensive system recommendations"""
        recommendations = []
        
        try:
            # System health recommendations
            if self.current_state.health_score < 70:
                recommendations.append("System health is below optimal levels. Consider resource optimization.")
            
            if self.current_state.performance_score < 60:
                recommendations.append("Performance issues detected. Review running processes and resource usage.")
            
            if self.current_state.security_score < 80:
                recommendations.append("Security concerns identified. Review system alerts and access patterns.")
            
            # Add component-specific recommendations
            if self.current_state.recommendations:
                recommendations.extend(self.current_state.recommendations)
            
            # Add ML-based recommendations
            if self.config.enable_ml and self.current_state.metrics:
                ml_recommendations = self.ml_integration.generate_ml_recommendations(
                    self.current_state.metrics, self.current_state.predictions)
                recommendations.extend(ml_recommendations)
            
            return recommendations[:10]  # Limit to top 10 recommendations
            
        except Exception as e:
            return [f"Error generating recommendations: {e}"]
    
    def _get_alerts_summary(self) -> Dict:
        """Get summary of current alerts"""
        if not self.current_state.alerts:
            return {'total': 0, 'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        summary = {'total': len(self.current_state.alerts)}
        for alert in self.current_state.alerts:
            severity = alert.get('severity', 'low')
            summary[severity] = summary.get(severity, 0) + 1
        
        return summary
    
    def _get_predictions_summary(self) -> Dict:
        """Get summary of current predictions"""
        if not self.current_state.predictions:
            return {'available': False}
        
        return {
            'available': True,
            'prediction_count': len(self.current_state.predictions),
            'horizons': list(self.current_state.predictions.keys()) if isinstance(self.current_state.predictions, dict) else []
        }
    
    def _get_insights_summary(self) -> Dict:
        """Get summary of current insights"""
        if not self.current_state.insights:
            return {'total': 0, 'high_severity': 0}
        
        high_severity = len([i for i in self.current_state.insights 
                           if i.get('severity') in ['critical', 'high']])
        
        return {
            'total': len(self.current_state.insights),
            'high_severity': high_severity
        }
    
    def add_callback(self, event_type: str, callback: Callable):
        """Add event callback"""
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
    
    def _trigger_callbacks(self, event_type: str, data: Any):
        """Trigger event callbacks"""
        if event_type in self.callbacks:
            for callback in self.callbacks[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    if self.console:
                        self.console.print(f"[red]Callback error: {e}[/red]")
    
    def _save_system_state(self, state: SystemState):
        """Save system state to database"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.unified_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO unified_system_states 
                (timestamp, health_score, performance_score, security_score, 
                 metrics_data, alerts_data, recommendations_data, predictions_data, insights_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                state.timestamp,
                state.health_score,
                state.performance_score,
                state.security_score,
                json.dumps(state.metrics) if state.metrics else None,
                json.dumps(state.alerts) if state.alerts else None,
                json.dumps(state.recommendations) if state.recommendations else None,
                json.dumps(state.predictions) if state.predictions else None,
                json.dumps(state.insights) if state.insights else None
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error saving system state: {e}[/red]")
    
    def _track_performance(self, component: str, operation: str, execution_time: float):
        """Track component performance"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.unified_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_metrics 
                (component_name, operation_name, execution_time, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (component, operation, execution_time, time.time()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error tracking performance: {e}[/red]")
    
    def _log_integration_event(self, event_type: str, event_data: str, severity: str, component: str):
        """Log integration event"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.unified_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO integration_events 
                (event_type, event_data, severity, component_name, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (event_type, event_data, severity, component, time.time()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error logging integration event: {e}[/red]")
    
    def display_unified_status(self):
        """Display unified system status"""
        if not RICH_AVAILABLE:
            print("Rich library required for formatted display")
            return
        
        # Create status table
        status_table = Table(title="Unified System Monitor Status")
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="green")
        status_table.add_column("Health Score", style="yellow")
        status_table.add_column("Performance", style="magenta")
        status_table.add_column("Last Update", style="blue")
        
        # Get component status
        component_status = self._get_component_status()
        performance_metrics = self._get_performance_metrics()
        
        for component, status in component_status.items():
            health_score = self.current_state.health_score if component == 'system_monitor' else 'N/A'
            performance = performance_metrics.get(component, {}).get('avg_execution_time', 'N/A')
            if isinstance(performance, (int, float)):
                performance = f"{performance:.3f}s"
            
            status_color = "green" if status == 'active' else "red"
            status_table.add_row(
                component.replace('_', ' ').title(),
                f"[{status_color}]{status}[/{status_color}]",
                f"{health_score:.1f}%" if isinstance(health_score, (int, float)) else str(health_score),
                performance,
                datetime.now().strftime("%H:%M:%S")
            )
        
        self.console.print(status_table)
        
        # Display system scores
        scores_panel = Panel(
            f"Health: {self.current_state.health_score:.1f}% | "
            f"Performance: {self.current_state.performance_score:.1f}% | "
            f"Security: {self.current_state.security_score:.1f}%",
            title="System Scores",
            border_style="blue"
        )
        self.console.print(scores_panel)

def main():
    """Main function for standalone testing"""
    config = IntegrationConfig(
        enable_monitoring=True,
        enable_analytics=True,
        enable_ml=True,
        enable_export=True,
        enable_dashboard=True,
        enable_alerts=True,
        enable_process_management=True,
        refresh_interval=3.0,
        max_threads=4,
        cache_duration=30.0
    )
    
    unified_monitor = UnifiedSystemMonitor(config)
    
    print("🔗 Unified System Monitor - Phase 6 Integration")
    print("=" * 60)
    
    # Start monitoring
    result = unified_monitor.start_monitoring()
    print(f"Monitoring: {result}")
    
    # Display status
    unified_monitor.display_unified_status()
    
    # Generate comprehensive report
    report = unified_monitor.get_comprehensive_report()
    print(f"\nComprehensive Report Generated: {len(report)} sections")
    
    # Stop monitoring after demo
    time.sleep(5)
    result = unified_monitor.stop_monitoring()
    print(f"Monitoring: {result}")
    
    print("\n✅ Unified system monitor test completed!")

if __name__ == "__main__":
    main() 