"""
Advanced Analytics for System Monitoring
Provides sophisticated data analysis, correlation detection, and performance optimization insights.
"""

import os
import sys
import json
import time
import sqlite3
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter

try:
    from scipy import stats
    from scipy.stats import pearsonr, spearmanr, kendalltau
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

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
from machine_learning_integration import MachineLearningIntegration

@dataclass
class CorrelationAnalysis:
    """Correlation analysis data structure"""
    metric1: str
    metric2: str
    correlation_type: str  # 'pearson', 'spearman', 'kendall'
    correlation_value: float
    p_value: float
    significance: str  # 'strong', 'moderate', 'weak', 'none'
    sample_size: int

@dataclass
class PerformanceInsight:
    """Performance insight data structure"""
    insight_type: str  # 'bottleneck', 'optimization', 'trend', 'anomaly'
    metric_name: str
    description: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    confidence: float
    recommendations: List[str]
    timestamp: float

@dataclass
class SystemCorrelation:
    """System correlation data structure"""
    correlation_id: str
    metrics: List[str]
    correlation_strength: float
    correlation_type: str
    description: str
    impact_level: str  # 'high', 'medium', 'low'
    recommendations: List[str]

class AdvancedAnalytics:
    """Advanced analytics engine for system monitoring"""
    
    def __init__(self, config: Dict = None):
        """Initialize advanced analytics"""
        self.console = Console() if RICH_AVAILABLE else None
        self.config = config or {}
        
        # Initialize components
        self.system_monitor = SystemMonitor()
        self.predictive_analytics = PredictiveAnalytics()
        self.ml_integration = MachineLearningIntegration()
        
        # Analytics settings
        self.analysis_dir = self.config.get('analysis_dir', 'analytics')
        self.correlation_threshold = self.config.get('correlation_threshold', 0.7)
        self.insight_confidence_threshold = self.config.get('insight_confidence_threshold', 0.8)
        
        # Create directories
        os.makedirs(self.analysis_dir, exist_ok=True)
        
        # Database paths
        self.system_db = os.path.join(os.path.dirname(__file__), '../../db/system_metrics.db')
        self.analytics_db = os.path.join(os.path.dirname(__file__), '../../db/advanced_analytics.db')
        
        # Initialize database
        self._init_database()
        
        if not SCIPY_AVAILABLE:
            if self.console:
                self.console.print("[yellow]Warning: scipy not available. Advanced statistical analysis will be limited.[/yellow]")
    
    def _init_database(self):
        """Initialize advanced analytics database"""
        try:
            conn = sqlite3.connect(self.analytics_db)
            cursor = conn.cursor()
            
            # Create correlations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS correlations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric1 TEXT NOT NULL,
                    metric2 TEXT NOT NULL,
                    correlation_type TEXT NOT NULL,
                    correlation_value REAL,
                    p_value REAL,
                    significance TEXT,
                    sample_size INTEGER,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            ''')
            
            # Create insights table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    insight_type TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    description TEXT,
                    severity TEXT,
                    confidence REAL,
                    recommendations TEXT,
                    timestamp REAL,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            ''')
            
            # Create system correlations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_correlations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    correlation_id TEXT NOT NULL,
                    metrics TEXT NOT NULL,
                    correlation_strength REAL,
                    correlation_type TEXT,
                    description TEXT,
                    impact_level TEXT,
                    recommendations TEXT,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            ''')
            
            # Create performance baselines table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_baselines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    baseline_type TEXT NOT NULL,
                    baseline_value REAL,
                    standard_deviation REAL,
                    sample_count INTEGER,
                    time_period TEXT,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error initializing analytics database: {e}[/red]")
    
    def analyze_correlations(self, time_range: str = '7d') -> List[CorrelationAnalysis]:
        """Analyze correlations between system metrics"""
        if not SCIPY_AVAILABLE:
            return []
        
        try:
            # Get historical data
            end_time = time.time()
            if time_range == '24h':
                start_time = end_time - (24 * 3600)
            elif time_range == '7d':
                start_time = end_time - (7 * 24 * 3600)
            elif time_range == '30d':
                start_time = end_time - (30 * 24 * 3600)
            else:
                start_time = end_time - (7 * 24 * 3600)  # Default to 7d
            
            conn = sqlite3.connect(self.system_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM system_metrics 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            ''', (start_time, end_time))
            
            rows = cursor.fetchall()
            conn.close()
            
            if len(rows) < 50:  # Need sufficient data
                return []
            
            # Extract metrics
            metrics_data = {
                'cpu_percent': [row[2] for row in rows],
                'memory_percent': [row[3] for row in rows],
                'disk_percent': [row[4] for row in rows],
                'network_sent_mb': [row[5] for row in rows],
                'network_recv_mb': [row[6] for row in rows],
                'process_count': [row[7] for row in rows],
                'load_average_1': [row[8] for row in rows],
                'load_average_5': [row[9] for row in rows],
                'load_average_15': [row[10] for row in rows]
            }
            
            # Calculate correlations
            correlations = []
            metric_names = list(metrics_data.keys())
            
            for i in range(len(metric_names)):
                for j in range(i + 1, len(metric_names)):
                    metric1 = metric_names[i]
                    metric2 = metric_names[j]
                    
                    # Get data for these metrics
                    data1 = np.array(metrics_data[metric1])
                    data2 = np.array(metrics_data[metric2])
                    
                    # Remove any NaN values
                    valid_indices = ~(np.isnan(data1) | np.isnan(data2))
                    if np.sum(valid_indices) < 10:  # Need minimum data points
                        continue
                    
                    data1_clean = data1[valid_indices]
                    data2_clean = data2[valid_indices]
                    
                    # Calculate different correlation types
                    correlation_types = [
                        ('pearson', pearsonr),
                        ('spearman', spearmanr),
                        ('kendall', kendalltau)
                    ]
                    
                    for corr_type, corr_func in correlation_types:
                        try:
                            corr_value, p_value = corr_func(data1_clean, data2_clean)
                            
                            # Determine significance
                            if abs(corr_value) >= 0.8:
                                significance = 'strong'
                            elif abs(corr_value) >= 0.6:
                                significance = 'moderate'
                            elif abs(corr_value) >= 0.4:
                                significance = 'weak'
                            else:
                                significance = 'none'
                            
                            correlation = CorrelationAnalysis(
                                metric1=metric1,
                                metric2=metric2,
                                correlation_type=corr_type,
                                correlation_value=corr_value,
                                p_value=p_value,
                                significance=significance,
                                sample_size=len(data1_clean)
                            )
                            
                            correlations.append(correlation)
                            
                            # Save to database
                            self._save_correlation(correlation)
                            
                        except Exception as e:
                            if self.console:
                                self.console.print(f"[red]Error calculating {corr_type} correlation: {e}[/red]")
            
            return correlations
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error analyzing correlations: {e}[/red]")
            return []
    
    def generate_performance_insights(self, time_range: str = '7d') -> List[PerformanceInsight]:
        """Generate performance insights from system data"""
        try:
            # Get historical data
            end_time = time.time()
            if time_range == '24h':
                start_time = end_time - (24 * 3600)
            elif time_range == '7d':
                start_time = end_time - (7 * 24 * 3600)
            elif time_range == '30d':
                start_time = end_time - (30 * 24 * 3600)
            else:
                start_time = end_time - (7 * 24 * 3600)  # Default to 7d
            
            conn = sqlite3.connect(self.system_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM system_metrics 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            ''', (start_time, end_time))
            
            rows = cursor.fetchall()
            conn.close()
            
            if len(rows) < 20:
                return []
            
            insights = []
            
            # Extract metrics
            cpu_values = [row[2] for row in rows if row[2] is not None]
            memory_values = [row[3] for row in rows if row[3] is not None]
            disk_values = [row[4] for row in rows if row[4] is not None]
            process_counts = [row[7] for row in rows if row[7] is not None]
            
            # CPU insights
            if cpu_values:
                avg_cpu = np.mean(cpu_values)
                max_cpu = np.max(cpu_values)
                cpu_std = np.std(cpu_values)
                
                if avg_cpu > 70:
                    insight = PerformanceInsight(
                        insight_type='bottleneck',
                        metric_name='cpu_percent',
                        description=f"High average CPU usage ({avg_cpu:.1f}%) with peak of {max_cpu:.1f}%",
                        severity='high' if avg_cpu > 80 else 'medium',
                        confidence=0.9,
                        recommendations=[
                            "Consider CPU-intensive process optimization",
                            "Monitor for runaway processes",
                            "Evaluate CPU upgrade if pattern persists"
                        ],
                        timestamp=time.time()
                    )
                    insights.append(insight)
                
                elif avg_cpu < 20 and cpu_std < 10:
                    insight = PerformanceInsight(
                        insight_type='optimization',
                        metric_name='cpu_percent',
                        description=f"Low CPU utilization ({avg_cpu:.1f}%) - potential for optimization",
                        severity='low',
                        confidence=0.8,
                        recommendations=[
                            "Consider running more CPU-intensive tasks",
                            "Evaluate if current workload is optimal"
                        ],
                        timestamp=time.time()
                    )
                    insights.append(insight)
            
            # Memory insights
            if memory_values:
                avg_memory = np.mean(memory_values)
                max_memory = np.max(memory_values)
                
                if avg_memory > 80:
                    insight = PerformanceInsight(
                        insight_type='bottleneck',
                        metric_name='memory_percent',
                        description=f"High memory usage ({avg_memory:.1f}%) with peak of {max_memory:.1f}%",
                        severity='critical' if avg_memory > 90 else 'high',
                        confidence=0.95,
                        recommendations=[
                            "Check for memory leaks",
                            "Consider increasing RAM",
                            "Optimize memory-intensive applications"
                        ],
                        timestamp=time.time()
                    )
                    insights.append(insight)
            
            # Disk insights
            if disk_values:
                avg_disk = np.mean(disk_values)
                max_disk = np.max(disk_values)
                
                if avg_disk > 85:
                    insight = PerformanceInsight(
                        insight_type='bottleneck',
                        metric_name='disk_percent',
                        description=f"Critical disk usage ({avg_disk:.1f}%) with peak of {max_disk:.1f}%",
                        severity='critical',
                        confidence=0.95,
                        recommendations=[
                            "Immediate disk cleanup required",
                            "Consider disk expansion",
                            "Archive old files"
                        ],
                        timestamp=time.time()
                    )
                    insights.append(insight)
            
            # Process count insights
            if process_counts:
                avg_processes = np.mean(process_counts)
                max_processes = np.max(process_counts)
                
                if avg_processes > 200:
                    insight = PerformanceInsight(
                        insight_type='trend',
                        metric_name='process_count',
                        description=f"High process count ({avg_processes:.0f} average, {max_processes:.0f} peak)",
                        severity='medium',
                        confidence=0.8,
                        recommendations=[
                            "Review running processes",
                            "Check for zombie processes",
                            "Consider process cleanup"
                        ],
                        timestamp=time.time()
                    )
                    insights.append(insight)
            
            # Save insights to database
            for insight in insights:
                self._save_insight(insight)
            
            return insights
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error generating performance insights: {e}[/red]")
            return []
    
    def identify_system_correlations(self, time_range: str = '7d') -> List[SystemCorrelation]:
        """Identify complex system correlations"""
        try:
            # Get correlations
            correlations = self.analyze_correlations(time_range)
            
            # Group by significance
            strong_correlations = [c for c in correlations if c.significance == 'strong']
            moderate_correlations = [c for c in correlations if c.significance == 'moderate']
            
            system_correlations = []
            
            # Analyze strong correlations
            for corr in strong_correlations:
                impact_level = 'high' if abs(corr.correlation_value) > 0.9 else 'medium'
                
                # Generate recommendations based on correlation type
                recommendations = self._generate_correlation_recommendations(corr)
                
                correlation = SystemCorrelation(
                    correlation_id=f"corr_{corr.metric1}_{corr.metric2}",
                    metrics=[corr.metric1, corr.metric2],
                    correlation_strength=abs(corr.correlation_value),
                    correlation_type=corr.correlation_type,
                    description=f"Strong {corr.correlation_type} correlation ({corr.correlation_value:.3f}) between {corr.metric1} and {corr.metric2}",
                    impact_level=impact_level,
                    recommendations=recommendations
                )
                
                system_correlations.append(correlation)
                self._save_system_correlation(correlation)
            
            return system_correlations
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error identifying system correlations: {e}[/red]")
            return []
    
    def _generate_correlation_recommendations(self, correlation: CorrelationAnalysis) -> List[str]:
        """Generate recommendations based on correlation analysis"""
        recommendations = []
        
        # CPU-Memory correlation
        if 'cpu_percent' in [correlation.metric1, correlation.metric2] and 'memory_percent' in [correlation.metric1, correlation.metric2]:
            if correlation.correlation_value > 0.8:
                recommendations.append("CPU and memory usage are strongly correlated. Optimize both resources together.")
            elif correlation.correlation_value < -0.5:
                recommendations.append("CPU and memory show inverse correlation. Check for memory swapping.")
        
        # CPU-Load correlation
        if 'cpu_percent' in [correlation.metric1, correlation.metric2] and 'load_average' in correlation.metric1 or 'load_average' in correlation.metric2:
            if correlation.correlation_value > 0.7:
                recommendations.append("CPU usage correlates with system load. Monitor load averages for CPU optimization.")
        
        # Network correlations
        if 'network_sent_mb' in [correlation.metric1, correlation.metric2] or 'network_recv_mb' in [correlation.metric1, correlation.metric2]:
            if correlation.correlation_value > 0.6:
                recommendations.append("Network activity correlates with system metrics. Monitor network impact on performance.")
        
        # Process count correlations
        if 'process_count' in [correlation.metric1, correlation.metric2]:
            if correlation.correlation_value > 0.5:
                recommendations.append("Process count correlates with system performance. Review process management.")
        
        return recommendations
    
    def calculate_performance_baselines(self, time_range: str = '7d') -> Dict[str, Dict]:
        """Calculate performance baselines for system metrics"""
        try:
            # Get historical data
            end_time = time.time()
            if time_range == '24h':
                start_time = end_time - (24 * 3600)
            elif time_range == '7d':
                start_time = end_time - (7 * 24 * 3600)
            elif time_range == '30d':
                start_time = end_time - (30 * 24 * 3600)
            else:
                start_time = end_time - (7 * 24 * 3600)  # Default to 7d
            
            conn = sqlite3.connect(self.system_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM system_metrics 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            ''', (start_time, end_time))
            
            rows = cursor.fetchall()
            conn.close()
            
            if len(rows) < 20:
                return {}
            
            baselines = {}
            
            # Calculate baselines for each metric
            metrics = {
                'cpu_percent': [row[2] for row in rows if row[2] is not None],
                'memory_percent': [row[3] for row in rows if row[3] is not None],
                'disk_percent': [row[4] for row in rows if row[4] is not None],
                'network_sent_mb': [row[5] for row in rows if row[5] is not None],
                'network_recv_mb': [row[6] for row in rows if row[6] is not None],
                'process_count': [row[7] for row in rows if row[7] is not None]
            }
            
            for metric_name, values in metrics.items():
                if len(values) > 0:
                    baseline = {
                        'mean': np.mean(values),
                        'median': np.median(values),
                        'std': np.std(values),
                        'min': np.min(values),
                        'max': np.max(values),
                        'percentile_95': np.percentile(values, 95),
                        'percentile_99': np.percentile(values, 99),
                        'sample_count': len(values)
                    }
                    
                    baselines[metric_name] = baseline
                    
                    # Save baseline to database
                    self._save_baseline(metric_name, baseline, time_range)
            
            return baselines
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error calculating performance baselines: {e}[/red]")
            return {}
    
    def detect_performance_anomalies(self, current_metrics, baselines: Dict = None) -> List[Dict]:
        """Detect performance anomalies using statistical analysis"""
        try:
            if not baselines:
                baselines = self.calculate_performance_baselines('7d')
            
            anomalies = []
            
            # Check each metric against its baseline
            metrics_to_check = {
                'cpu_percent': current_metrics.cpu_percent,
                'memory_percent': current_metrics.memory_percent,
                'disk_percent': current_metrics.disk_percent,
                'network_sent_mb': current_metrics.network_sent_mb,
                'network_recv_mb': current_metrics.network_recv_mb,
                'process_count': current_metrics.process_count
            }
            
            for metric_name, current_value in metrics_to_check.items():
                if metric_name in baselines and current_value is not None:
                    baseline = baselines[metric_name]
                    mean = baseline['mean']
                    std = baseline['std']
                    
                    # Calculate z-score
                    if std > 0:
                        z_score = abs(current_value - mean) / std
                        
                        # Detect anomalies (z-score > 2)
                        if z_score > 2:
                            anomaly = {
                                'metric_name': metric_name,
                                'current_value': current_value,
                                'baseline_mean': mean,
                                'z_score': z_score,
                                'severity': 'high' if z_score > 3 else 'medium',
                                'description': f"{metric_name} is {z_score:.2f} standard deviations from baseline",
                                'timestamp': time.time()
                            }
                            anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error detecting performance anomalies: {e}[/red]")
            return []
    
    def _save_correlation(self, correlation: CorrelationAnalysis):
        """Save correlation analysis to database"""
        try:
            conn = sqlite3.connect(self.analytics_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO correlations (metric1, metric2, correlation_type, correlation_value, p_value, significance, sample_size)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                correlation.metric1,
                correlation.metric2,
                correlation.correlation_type,
                correlation.correlation_value,
                correlation.p_value,
                correlation.significance,
                correlation.sample_size
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error saving correlation: {e}[/red]")
    
    def _save_insight(self, insight: PerformanceInsight):
        """Save performance insight to database"""
        try:
            conn = sqlite3.connect(self.analytics_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_insights (insight_type, metric_name, description, severity, confidence, recommendations, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                insight.insight_type,
                insight.metric_name,
                insight.description,
                insight.severity,
                insight.confidence,
                json.dumps(insight.recommendations),
                insight.timestamp
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error saving insight: {e}[/red]")
    
    def _save_system_correlation(self, correlation: SystemCorrelation):
        """Save system correlation to database"""
        try:
            conn = sqlite3.connect(self.analytics_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_correlations (correlation_id, metrics, correlation_strength, correlation_type, description, impact_level, recommendations)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                correlation.correlation_id,
                json.dumps(correlation.metrics),
                correlation.correlation_strength,
                correlation.correlation_type,
                correlation.description,
                correlation.impact_level,
                json.dumps(correlation.recommendations)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error saving system correlation: {e}[/red]")
    
    def _save_baseline(self, metric_name: str, baseline: Dict, time_period: str):
        """Save performance baseline to database"""
        try:
            conn = sqlite3.connect(self.analytics_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_baselines (metric_name, baseline_type, baseline_value, standard_deviation, sample_count, time_period)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                metric_name,
                'mean',
                baseline['mean'],
                baseline['std'],
                baseline['sample_count'],
                time_period
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error saving baseline: {e}[/red]")
    
    def display_analytics_summary(self):
        """Display analytics summary"""
        if not RICH_AVAILABLE:
            print("Rich library required for formatted display")
            return
        
        # Get recent correlations
        conn = sqlite3.connect(self.analytics_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT metric1, metric2, correlation_type, correlation_value, significance
            FROM correlations
            WHERE significance IN ('strong', 'moderate')
            ORDER BY created_at DESC
            LIMIT 10
        ''')
        
        correlations = cursor.fetchall()
        
        # Get recent insights
        cursor.execute('''
            SELECT insight_type, metric_name, severity, description
            FROM performance_insights
            ORDER BY created_at DESC
            LIMIT 10
        ''')
        
        insights = cursor.fetchall()
        
        conn.close()
        
        # Create summary table
        summary_table = Table(title="Advanced Analytics Summary")
        summary_table.add_column("Analysis Type", style="cyan")
        summary_table.add_column("Count", style="green")
        summary_table.add_column("Latest Findings", style="yellow")
        
        summary_table.add_row(
            "Strong Correlations",
            str(len([c for c in correlations if c[4] == 'strong'])),
            f"{len(correlations)} significant correlations found"
        )
        
        summary_table.add_row(
            "Performance Insights",
            str(len(insights)),
            f"{len([i for i in insights if i[2] in ['critical', 'high']])} high-severity insights"
        )
        
        self.console.print(summary_table)
        
        # Display scipy availability
        scipy_status = "✅ Available" if SCIPY_AVAILABLE else "❌ Not Available"
        self.console.print(f"\n[bold]scipy Status:[/bold] {scipy_status}")

def main():
    """Main function for standalone testing"""
    analytics = AdvancedAnalytics()
    
    print("📊 Advanced Analytics Engine")
    print("=" * 50)
    
    # Display summary
    analytics.display_analytics_summary()
    
    # Test analytics features
    print("\n🧪 Testing advanced analytics...")
    
    # Test correlation analysis
    correlations = analytics.analyze_correlations('7d')
    print(f"Correlation Analysis: {len(correlations)} correlations found")
    
    # Test performance insights
    insights = analytics.generate_performance_insights('7d')
    print(f"Performance Insights: {len(insights)} insights generated")
    
    # Test system correlations
    system_correlations = analytics.identify_system_correlations('7d')
    print(f"System Correlations: {len(system_correlations)} identified")
    
    # Test baseline calculation
    baselines = analytics.calculate_performance_baselines('7d')
    print(f"Performance Baselines: {len(baselines)} baselines calculated")
    
    # Test anomaly detection
    current_metrics = analytics.system_monitor.collect_metrics()
    if current_metrics:
        anomalies = analytics.detect_performance_anomalies(current_metrics, baselines)
        print(f"Performance Anomalies: {len(anomalies)} anomalies detected")
    
    print("\n✅ Advanced analytics tests completed!")

if __name__ == "__main__":
    main() 