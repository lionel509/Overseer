"""
Predictive Analytics for System Monitoring
Provides trend analysis, forecasting, and anomaly detection for system performance.
"""

import os
import sys
import json
import time
import sqlite3
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import deque

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from system_monitor import SystemMonitor

@dataclass
class TrendAnalysis:
    """Trend analysis data structure"""
    metric_name: str
    current_value: float
    trend_direction: str  # 'increasing', 'decreasing', 'stable'
    trend_strength: float  # 0.0 to 1.0
    change_rate: float  # percentage change per hour
    prediction_1h: float
    prediction_6h: float
    prediction_24h: float
    confidence: float

@dataclass
class AnomalyDetection:
    """Anomaly detection data structure"""
    metric_name: str
    timestamp: float
    value: float
    expected_value: float
    deviation: float
    severity: str  # 'low', 'medium', 'high', 'critical'
    anomaly_type: str  # 'spike', 'drop', 'trend_break', 'seasonal'
    confidence: float

@dataclass
class PerformanceForecast:
    """Performance forecast data structure"""
    metric_name: str
    forecast_horizon: str  # '1h', '6h', '24h', '7d'
    predicted_value: float
    confidence_interval: Tuple[float, float]
    trend_analysis: str
    recommendations: List[str]

class PredictiveAnalytics:
    """Predictive analytics engine for system performance"""
    
    def __init__(self, db_path: str = None, config: Dict = None):
        """Initialize predictive analytics"""
        self.console = Console() if RICH_AVAILABLE else None
        self.config = config or {}
        
        # Initialize components
        self.system_monitor = SystemMonitor()
        
        # Database setup
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '../../db/predictive_analytics.db')
        self.db_path = db_path
        self._init_database()
        
        # Analytics settings
        self.trend_window = self.config.get('trend_window', 24)  # hours
        self.anomaly_threshold = self.config.get('anomaly_threshold', 2.0)  # standard deviations
        self.forecast_horizons = [1, 6, 24, 168]  # hours: 1h, 6h, 24h, 7d
        
        # Data storage for real-time analysis
        self.metric_history = {
            'cpu_percent': deque(maxlen=1000),
            'memory_percent': deque(maxlen=1000),
            'disk_percent': deque(maxlen=1000),
            'network_sent_mb': deque(maxlen=1000),
            'network_recv_mb': deque(maxlen=1000),
            'load_average_1': deque(maxlen=1000),
            'process_count': deque(maxlen=1000)
        }
        
        # Anomaly detection models
        self.anomaly_models = {}
        self._init_anomaly_models()
    
    def _init_database(self):
        """Initialize predictive analytics database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Trend analysis table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trend_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT,
                current_value REAL,
                trend_direction TEXT,
                trend_strength REAL,
                change_rate REAL,
                prediction_1h REAL,
                prediction_6h REAL,
                prediction_24h REAL,
                confidence REAL,
                timestamp REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Anomaly detection table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anomalies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT,
                timestamp REAL,
                value REAL,
                expected_value REAL,
                deviation REAL,
                severity TEXT,
                anomaly_type TEXT,
                confidence REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Performance forecasts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_forecasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT,
                forecast_horizon TEXT,
                predicted_value REAL,
                confidence_lower REAL,
                confidence_upper REAL,
                trend_analysis TEXT,
                recommendations TEXT,
                timestamp REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Historical data for analysis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT,
                value REAL,
                timestamp REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _init_anomaly_models(self):
        """Initialize anomaly detection models"""
        # Simple statistical models for each metric
        for metric in self.metric_history.keys():
            self.anomaly_models[metric] = {
                'mean': 0.0,
                'std': 1.0,
                'min': float('inf'),
                'max': float('-inf'),
                'last_values': deque(maxlen=100)
            }
    
    def collect_metrics(self):
        """Collect current metrics and update history"""
        try:
            metrics = self.system_monitor.collect_metrics()
            
            # Update metric history
            current_time = time.time()
            
            self.metric_history['cpu_percent'].append((current_time, metrics.cpu_percent))
            self.metric_history['memory_percent'].append((current_time, metrics.memory_percent))
            self.metric_history['disk_percent'].append((current_time, metrics.disk_percent))
            self.metric_history['network_sent_mb'].append((current_time, metrics.network_sent_mb))
            self.metric_history['network_recv_mb'].append((current_time, metrics.network_recv_mb))
            self.metric_history['load_average_1'].append((current_time, metrics.load_average[0]))
            self.metric_history['process_count'].append((current_time, metrics.process_count))
            
            # Save to database
            self._save_metrics_to_db(metrics, current_time)
            
            # Update anomaly models
            self._update_anomaly_models()
            
            return metrics
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error collecting metrics: {e}[/red]")
            return None
    
    def _save_metrics_to_db(self, metrics, timestamp):
        """Save metrics to database for historical analysis"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Save current metrics
            metrics_data = [
                ('cpu_percent', metrics.cpu_percent, timestamp),
                ('memory_percent', metrics.memory_percent, timestamp),
                ('disk_percent', metrics.disk_percent, timestamp),
                ('network_sent_mb', metrics.network_sent_mb, timestamp),
                ('network_recv_mb', metrics.network_recv_mb, timestamp),
                ('load_average_1', metrics.load_average[0], timestamp),
                ('process_count', metrics.process_count, timestamp)
            ]
            
            cursor.executemany('''
                INSERT INTO historical_metrics (metric_name, value, timestamp)
                VALUES (?, ?, ?)
            ''', metrics_data)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error saving metrics: {e}[/red]")
    
    def _update_anomaly_models(self):
        """Update anomaly detection models with new data"""
        for metric_name, history in self.metric_history.items():
            if len(history) < 10:  # Need minimum data points
                continue
            
            values = [value for _, value in history]
            model = self.anomaly_models[metric_name]
            
            # Update statistical measures
            model['mean'] = np.mean(values)
            model['std'] = np.std(values) if len(values) > 1 else 1.0
            model['min'] = min(values)
            model['max'] = max(values)
            model['last_values'].extend(values[-10:])  # Keep last 10 values
    
    def analyze_trends(self) -> List[TrendAnalysis]:
        """Analyze trends for all metrics"""
        trends = []
        
        for metric_name, history in self.metric_history.items():
            if len(history) < 20:  # Need sufficient data
                continue
            
            trend = self._analyze_single_trend(metric_name, history)
            if trend:
                trends.append(trend)
        
        return trends
    
    def _analyze_single_trend(self, metric_name: str, history: deque) -> Optional[TrendAnalysis]:
        """Analyze trend for a single metric"""
        if len(history) < 20:
            return None
        
        # Extract time series data
        timestamps, values = zip(*list(history)[-50:])  # Last 50 points
        
        # Calculate trend direction and strength
        if len(values) >= 2:
            # Simple linear regression for trend
            x = np.array(timestamps)
            y = np.array(values)
            
            # Normalize time to hours from start
            x_normalized = (x - x[0]) / 3600  # Convert to hours
            
            # Linear regression
            coeffs = np.polyfit(x_normalized, y, 1)
            slope = coeffs[0]
            
            # Calculate trend direction
            if abs(slope) < 0.1:  # Small slope
                direction = 'stable'
                strength = 0.1
            elif slope > 0:
                direction = 'increasing'
                strength = min(abs(slope) / 10.0, 1.0)  # Normalize strength
            else:
                direction = 'decreasing'
                strength = min(abs(slope) / 10.0, 1.0)
            
            # Calculate change rate (percentage per hour)
            if values[0] != 0:
                change_rate = ((values[-1] - values[0]) / values[0]) * 100 / (len(values) - 1)
            else:
                change_rate = 0.0
            
            # Simple predictions
            current_value = values[-1]
            prediction_1h = current_value + (slope * 1)
            prediction_6h = current_value + (slope * 6)
            prediction_24h = current_value + (slope * 24)
            
            # Confidence based on data consistency
            confidence = min(0.9, max(0.1, 1.0 - np.std(values) / np.mean(values) if np.mean(values) > 0 else 0.5))
            
            return TrendAnalysis(
                metric_name=metric_name,
                current_value=current_value,
                trend_direction=direction,
                trend_strength=strength,
                change_rate=change_rate,
                prediction_1h=prediction_1h,
                prediction_6h=prediction_6h,
                prediction_24h=prediction_24h,
                confidence=confidence
            )
        
        return None
    
    def detect_anomalies(self) -> List[AnomalyDetection]:
        """Detect anomalies in current metrics"""
        anomalies = []
        
        for metric_name, history in self.metric_history.items():
            if len(history) < 10:
                continue
            
            current_value = history[-1][1]  # Latest value
            model = self.anomaly_models[metric_name]
            
            # Calculate expected value and deviation
            expected_value = model['mean']
            deviation = abs(current_value - expected_value)
            
            # Check if this is an anomaly
            if model['std'] > 0:
                z_score = deviation / model['std']
                
                if z_score > self.anomaly_threshold:
                    # Determine anomaly type
                    anomaly_type = self._classify_anomaly(metric_name, current_value, expected_value, history)
                    
                    # Determine severity
                    if z_score > 4.0:
                        severity = 'critical'
                    elif z_score > 3.0:
                        severity = 'high'
                    elif z_score > 2.0:
                        severity = 'medium'
                    else:
                        severity = 'low'
                    
                    # Calculate confidence
                    confidence = min(0.95, z_score / 5.0)
                    
                    anomaly = AnomalyDetection(
                        metric_name=metric_name,
                        timestamp=time.time(),
                        value=current_value,
                        expected_value=expected_value,
                        deviation=deviation,
                        severity=severity,
                        anomaly_type=anomaly_type,
                        confidence=confidence
                    )
                    
                    anomalies.append(anomaly)
        
        return anomalies
    
    def _classify_anomaly(self, metric_name: str, current_value: float, expected_value: float, history: deque) -> str:
        """Classify the type of anomaly"""
        if len(history) < 5:
            return 'unknown'
        
        recent_values = [value for _, value in list(history)[-5:]]
        
        # Check for spikes
        if current_value > expected_value * 1.5:
            return 'spike'
        
        # Check for drops
        if current_value < expected_value * 0.5:
            return 'drop'
        
        # Check for trend breaks
        if len(recent_values) >= 3:
            trend_1 = recent_values[-1] - recent_values[-2]
            trend_2 = recent_values[-2] - recent_values[-3]
            
            if (trend_1 > 0 and trend_2 < 0) or (trend_1 < 0 and trend_2 > 0):
                return 'trend_break'
        
        return 'deviation'
    
    def generate_forecasts(self) -> List[PerformanceForecast]:
        """Generate performance forecasts for all metrics"""
        forecasts = []
        
        for metric_name, history in self.metric_history.items():
            if len(history) < 20:
                continue
            
            for horizon in self.forecast_horizons:
                forecast = self._generate_single_forecast(metric_name, history, horizon)
                if forecast:
                    forecasts.append(forecast)
        
        return forecasts
    
    def _generate_single_forecast(self, metric_name: str, history: deque, horizon_hours: int) -> Optional[PerformanceForecast]:
        """Generate forecast for a single metric and horizon"""
        if len(history) < 20:
            return None
        
        # Extract recent data
        timestamps, values = zip(*list(history)[-30:])  # Last 30 points
        
        # Simple linear regression for forecasting
        x = np.array(timestamps)
        y = np.array(values)
        
        # Normalize time
        x_normalized = (x - x[0]) / 3600  # Convert to hours
        
        # Linear regression
        coeffs = np.polyfit(x_normalized, y, 1)
        slope = coeffs[0]
        intercept = coeffs[1]
        
        # Generate prediction
        current_time = timestamps[-1]
        future_time = current_time + (horizon_hours * 3600)
        time_normalized = (future_time - x[0]) / 3600
        
        predicted_value = slope * time_normalized + intercept
        
        # Calculate confidence interval
        residuals = y - (slope * x_normalized + intercept)
        std_error = np.std(residuals)
        confidence_lower = predicted_value - (1.96 * std_error)  # 95% CI
        confidence_upper = predicted_value + (1.96 * std_error)
        
        # Generate trend analysis
        if slope > 0.1:
            trend_analysis = f"Strong upward trend ({slope:.2f} units/hour)"
        elif slope < -0.1:
            trend_analysis = f"Strong downward trend ({abs(slope):.2f} units/hour)"
        else:
            trend_analysis = "Stable trend"
        
        # Generate recommendations
        recommendations = self._generate_forecast_recommendations(metric_name, predicted_value, slope)
        
        return PerformanceForecast(
            metric_name=metric_name,
            forecast_horizon=f"{horizon_hours}h",
            predicted_value=predicted_value,
            confidence_interval=(confidence_lower, confidence_upper),
            trend_analysis=trend_analysis,
            recommendations=recommendations
        )
    
    def _generate_forecast_recommendations(self, metric_name: str, predicted_value: float, slope: float) -> List[str]:
        """Generate recommendations based on forecast"""
        recommendations = []
        
        if metric_name == 'cpu_percent':
            if predicted_value > 90:
                recommendations.append("Consider scaling up CPU resources")
                recommendations.append("Optimize application performance")
            elif predicted_value > 70:
                recommendations.append("Monitor CPU usage closely")
                recommendations.append("Consider load balancing")
        
        elif metric_name == 'memory_percent':
            if predicted_value > 95:
                recommendations.append("Immediate memory upgrade recommended")
                recommendations.append("Check for memory leaks")
            elif predicted_value > 80:
                recommendations.append("Consider increasing RAM")
                recommendations.append("Optimize memory usage")
        
        elif metric_name == 'disk_percent':
            if predicted_value > 95:
                recommendations.append("Critical: Disk space will be exhausted")
                recommendations.append("Immediate cleanup required")
            elif predicted_value > 85:
                recommendations.append("Disk cleanup recommended")
                recommendations.append("Consider storage expansion")
        
        elif metric_name == 'load_average_1':
            if predicted_value > 10:
                recommendations.append("System overload predicted")
                recommendations.append("Consider adding more servers")
            elif predicted_value > 5:
                recommendations.append("High load expected")
                recommendations.append("Optimize system performance")
        
        return recommendations
    
    def display_analytics(self, trends: List[TrendAnalysis], anomalies: List[AnomalyDetection], forecasts: List[PerformanceForecast]):
        """Display predictive analytics results"""
        if not RICH_AVAILABLE:
            print("Rich library required for formatted display")
            return
        
        # Display trends
        if trends:
            self.console.print("\n[bold]📈 Trend Analysis:[/bold]")
            trend_table = Table(title="System Trends")
            trend_table.add_column("Metric", style="cyan")
            trend_table.add_column("Current", style="green")
            trend_table.add_column("Trend", style="yellow")
            trend_table.add_column("Strength", style="magenta")
            trend_table.add_column("Change Rate", style="blue")
            trend_table.add_column("1h Forecast", style="red")
            
            for trend in trends:
                trend_color = "green" if trend.trend_direction == "decreasing" else "red" if trend.trend_direction == "increasing" else "yellow"
                trend_table.add_row(
                    trend.metric_name.replace('_', ' ').title(),
                    f"{trend.current_value:.1f}",
                    f"[{trend_color}]{trend.trend_direction}[/{trend_color}]",
                    f"{trend.trend_strength:.1%}",
                    f"{trend.change_rate:+.1f}%/h",
                    f"{trend.prediction_1h:.1f}"
                )
            
            self.console.print(trend_table)
        
        # Display anomalies
        if anomalies:
            self.console.print("\n[bold]🚨 Anomaly Detection:[/bold]")
            anomaly_table = Table(title="Detected Anomalies")
            anomaly_table.add_column("Metric", style="cyan")
            anomaly_table.add_column("Value", style="green")
            anomaly_table.add_column("Expected", style="yellow")
            anomaly_table.add_column("Deviation", style="magenta")
            anomaly_table.add_column("Severity", style="red")
            anomaly_table.add_column("Type", style="blue")
            
            for anomaly in anomalies:
                severity_color = "red" if anomaly.severity == "critical" else "yellow" if anomaly.severity == "high" else "green"
                anomaly_table.add_row(
                    anomaly.metric_name.replace('_', ' ').title(),
                    f"{anomaly.value:.1f}",
                    f"{anomaly.expected_value:.1f}",
                    f"{anomaly.deviation:.1f}",
                    f"[{severity_color}]{anomaly.severity.upper()}[/{severity_color}]",
                    anomaly.anomaly_type
                )
            
            self.console.print(anomaly_table)
        
        # Display forecasts
        if forecasts:
            self.console.print("\n[bold]🔮 Performance Forecasts:[/bold]")
            forecast_table = Table(title="System Forecasts")
            forecast_table.add_column("Metric", style="cyan")
            forecast_table.add_column("Horizon", style="green")
            forecast_table.add_column("Predicted", style="yellow")
            forecast_table.add_column("Confidence", style="magenta")
            forecast_table.add_column("Trend", style="blue")
            
            for forecast in forecasts:
                forecast_table.add_row(
                    forecast.metric_name.replace('_', ' ').title(),
                    forecast.forecast_horizon,
                    f"{forecast.predicted_value:.1f}",
                    f"{forecast.confidence_interval[0]:.1f}-{forecast.confidence_interval[1]:.1f}",
                    forecast.trend_analysis[:30] + "..." if len(forecast.trend_analysis) > 30 else forecast.trend_analysis
                )
            
            self.console.print(forecast_table)
    
    def run_analysis(self):
        """Run complete predictive analytics analysis"""
        # Collect current metrics
        metrics = self.collect_metrics()
        if not metrics:
            return None
        
        # Run analyses
        trends = self.analyze_trends()
        anomalies = self.detect_anomalies()
        forecasts = self.generate_forecasts()
        
        # Display results
        self.display_analytics(trends, anomalies, forecasts)
        
        return {
            'trends': trends,
            'anomalies': anomalies,
            'forecasts': forecasts,
            'timestamp': time.time()
        }

def main():
    """Main function for standalone testing"""
    analytics = PredictiveAnalytics()
    
    print("🔮 Predictive Analytics Engine")
    print("=" * 50)
    
    # Run analysis
    results = analytics.run_analysis()
    
    if results:
        print(f"\n✅ Analysis completed:")
        print(f"   Trends analyzed: {len(results['trends'])}")
        print(f"   Anomalies detected: {len(results['anomalies'])}")
        print(f"   Forecasts generated: {len(results['forecasts'])}")
    else:
        print("❌ Analysis failed")

if __name__ == "__main__":
    main() 