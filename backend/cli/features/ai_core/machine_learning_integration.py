"""
Machine Learning Integration Module
Core ML capabilities for the Overseer system including pattern recognition, 
predictive analytics, anomaly detection, and intelligent system optimization.
"""

import os
import json
import sqlite3
import time
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
import pandas as pd
from collections import defaultdict, deque

try:
    import torch
    import torch.nn as nn
    from transformers import AutoTokenizer, AutoModel
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from sklearn.ensemble import IsolationForest, RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    from sklearn.metrics import mean_squared_error, mean_absolute_error
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MLPrediction:
    """Machine learning prediction result"""
    prediction_type: str
    value: Union[float, int, str]
    confidence: float
    timestamp: datetime
    features: Dict[str, Any]
    explanation: str
    recommendations: List[str]

@dataclass
class AnomalyDetection:
    """Anomaly detection result"""
    is_anomaly: bool
    severity: str
    confidence: float
    timestamp: datetime
    features: Dict[str, Any]
    description: str
    suggested_actions: List[str]

@dataclass
class PatternAnalysis:
    """Pattern analysis result"""
    pattern_type: str
    pattern_strength: float
    periodicity: Optional[str]
    trend: str
    confidence: float
    features: Dict[str, Any]
    insights: List[str]

class MachineLearningIntegration:
    """
    Core machine learning integration for Overseer system.
    Provides pattern recognition, predictive analytics, anomaly detection,
    and intelligent system optimization capabilities.
    """
    
    def __init__(self, db_path: str = None, model_dir: str = None):
        """Initialize ML integration module"""
        self.console = Console() if RICH_AVAILABLE else None
        
        # Database setup
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '../../db/ml_integration.db')
        self.db_path = db_path
        self._init_database()
        
        # Model directory
        if model_dir is None:
            model_dir = os.path.join(os.path.dirname(__file__), '../../../models')
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        # Initialize ML components
        self._init_ml_components()
        
        # Data storage for real-time analysis
        self.system_metrics_history = deque(maxlen=1000)
        self.performance_patterns = defaultdict(list)
        self.anomaly_history = deque(maxlen=100)
        
        # ML models
        self.anomaly_detector = None
        self.performance_predictor = None
        self.pattern_analyzer = None
        self.resource_optimizer = None
        
        # Load or initialize models
        self._load_models()
    
    def _init_database(self):
        """Initialize the ML integration database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create system metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                cpu_percent REAL,
                memory_percent REAL,
                disk_percent REAL,
                network_io REAL,
                temperature REAL,
                process_count INTEGER,
                load_average REAL,
                metadata TEXT
            )
        ''')
        
        # Create predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                prediction_type TEXT,
                value REAL,
                confidence REAL,
                features TEXT,
                explanation TEXT
            )
        ''')
        
        # Create anomalies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anomalies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                anomaly_type TEXT,
                severity TEXT,
                confidence REAL,
                features TEXT,
                description TEXT,
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Create patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                pattern_type TEXT,
                strength REAL,
                periodicity TEXT,
                trend TEXT,
                confidence REAL,
                features TEXT
            )
        ''')
        
        # Create model metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT,
                model_type TEXT,
                version TEXT,
                accuracy REAL,
                last_updated DATETIME,
                parameters TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _init_ml_components(self):
        """Initialize machine learning components"""
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available. Some ML features will be disabled.")
            return
        
        # Initialize anomaly detection
        self.anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        
        # Initialize performance prediction
        self.performance_predictor = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            max_depth=10
        )
        
        # Initialize pattern analysis
        self.pattern_analyzer = KMeans(
            n_clusters=5,
            random_state=42
        )
        
        # Initialize scalers
        self.feature_scaler = StandardScaler()
        self.target_scaler = StandardScaler()
    
    def _load_models(self):
        """Load trained models from disk"""
        try:
            # Load anomaly detector
            anomaly_model_path = self.model_dir / "anomaly_detector.pkl"
            if anomaly_model_path.exists():
                import joblib
                self.anomaly_detector = joblib.load(anomaly_model_path)
                logger.info("Loaded anomaly detection model")
            
            # Load performance predictor
            predictor_model_path = self.model_dir / "performance_predictor.pkl"
            if predictor_model_path.exists():
                import joblib
                self.performance_predictor = joblib.load(predictor_model_path)
                logger.info("Loaded performance prediction model")
            
            # Load scalers
            scaler_path = self.model_dir / "feature_scaler.pkl"
            if scaler_path.exists():
                import joblib
                self.feature_scaler = joblib.load(scaler_path)
                logger.info("Loaded feature scaler")
            
        except Exception as e:
            logger.warning(f"Could not load models: {e}")
    
    def _save_models(self):
        """Save trained models to disk"""
        try:
            import joblib
            
            # Save anomaly detector
            joblib.dump(self.anomaly_detector, self.model_dir / "anomaly_detector.pkl")
            
            # Save performance predictor
            joblib.dump(self.performance_predictor, self.model_dir / "performance_predictor.pkl")
            
            # Save scalers
            joblib.dump(self.feature_scaler, self.model_dir / "feature_scaler.pkl")
            
            logger.info("Models saved successfully")
            
        except Exception as e:
            logger.error(f"Could not save models: {e}")
    
    def collect_system_metrics(self, system_monitor=None) -> Dict[str, Any]:
        """Collect current system metrics for ML analysis"""
        metrics = {
            'timestamp': datetime.now(),
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'disk_percent': 0.0,
            'network_io': 0.0,
            'temperature': 0.0,
            'process_count': 0,
            'load_average': 0.0
        }
        
        if system_monitor:
            try:
                # Get system metrics from monitor
                system_info = system_monitor.get_system_info()
                metrics.update({
                    'cpu_percent': system_info.get('cpu_percent', 0.0),
                    'memory_percent': system_info.get('memory_percent', 0.0),
                    'disk_percent': system_info.get('disk_percent', 0.0),
                    'network_io': system_info.get('network_io', 0.0),
                    'temperature': system_info.get('temperature', 0.0),
                    'process_count': system_info.get('process_count', 0),
                    'load_average': system_info.get('load_average', 0.0)
                })
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
        
        # Store in history
        self.system_metrics_history.append(metrics)
        
        # Store in database
        self._store_metrics(metrics)
        
        return metrics
    
    def _store_metrics(self, metrics: Dict[str, Any]):
        """Store metrics in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_metrics 
                (timestamp, cpu_percent, memory_percent, disk_percent, 
                 network_io, temperature, process_count, load_average, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics['timestamp'],
                metrics['cpu_percent'],
                metrics['memory_percent'],
                metrics['disk_percent'],
                metrics['network_io'],
                metrics['temperature'],
                metrics['process_count'],
                metrics['load_average'],
                json.dumps(metrics.get('metadata', {}))
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing metrics: {e}")
    
    def detect_anomalies(self, metrics: Dict[str, Any] = None) -> AnomalyDetection:
        """Detect anomalies in system behavior"""
        if not SKLEARN_AVAILABLE or not self.anomaly_detector:
            return AnomalyDetection(
                is_anomaly=False,
                severity="unknown",
                confidence=0.0,
                timestamp=datetime.now(),
                features={},
                description="ML models not available",
                suggested_actions=[]
            )
        
        if metrics is None:
            metrics = self.collect_system_metrics()
        
        # Prepare features for anomaly detection
        features = np.array([
            metrics['cpu_percent'],
            metrics['memory_percent'],
            metrics['disk_percent'],
            metrics['network_io'],
            metrics['process_count'],
            metrics['load_average']
        ]).reshape(1, -1)
        
        # Scale features
        features_scaled = self.feature_scaler.transform(features)
        
        # Detect anomaly
        anomaly_score = self.anomaly_detector.decision_function(features_scaled)[0]
        is_anomaly = self.anomaly_detector.predict(features_scaled)[0] == -1
        
        # Determine severity
        if is_anomaly:
            if anomaly_score < -0.5:
                severity = "critical"
            elif anomaly_score < -0.3:
                severity = "high"
            else:
                severity = "medium"
        else:
            severity = "none"
        
        # Generate description and suggestions
        description = self._generate_anomaly_description(metrics, is_anomaly, severity)
        suggested_actions = self._generate_anomaly_suggestions(metrics, severity)
        
        # Store anomaly
        if is_anomaly:
            self._store_anomaly(metrics, severity, abs(anomaly_score), description)
        
        return AnomalyDetection(
            is_anomaly=is_anomaly,
            severity=severity,
            confidence=abs(anomaly_score),
            timestamp=datetime.now(),
            features=metrics,
            description=description,
            suggested_actions=suggested_actions
        )
    
    def _generate_anomaly_description(self, metrics: Dict[str, Any], is_anomaly: bool, severity: str) -> str:
        """Generate human-readable anomaly description"""
        if not is_anomaly:
            return "System behavior is normal"
        
        descriptions = []
        
        if metrics['cpu_percent'] > 90:
            descriptions.append("Extremely high CPU usage")
        elif metrics['cpu_percent'] > 80:
            descriptions.append("High CPU usage")
        
        if metrics['memory_percent'] > 95:
            descriptions.append("Critical memory usage")
        elif metrics['memory_percent'] > 85:
            descriptions.append("High memory usage")
        
        if metrics['disk_percent'] > 95:
            descriptions.append("Critical disk space usage")
        elif metrics['disk_percent'] > 90:
            descriptions.append("High disk space usage")
        
        if metrics['load_average'] > 10:
            descriptions.append("Extremely high system load")
        elif metrics['load_average'] > 5:
            descriptions.append("High system load")
        
        if not descriptions:
            descriptions.append("Unusual system behavior detected")
        
        return f"{severity.title()} anomaly: {'; '.join(descriptions)}"
    
    def _generate_anomaly_suggestions(self, metrics: Dict[str, Any], severity: str) -> List[str]:
        """Generate suggested actions for anomalies"""
        suggestions = []
        
        if severity == "critical":
            suggestions.extend([
                "Immediately check system processes",
                "Consider restarting critical services",
                "Monitor system logs for errors",
                "Check for hardware issues"
            ])
        elif severity == "high":
            suggestions.extend([
                "Monitor system performance",
                "Check for resource-intensive processes",
                "Consider system optimization",
                "Review recent system changes"
            ])
        elif severity == "medium":
            suggestions.extend([
                "Continue monitoring",
                "Check system logs",
                "Review performance trends"
            ])
        
        return suggestions
    
    def _store_anomaly(self, metrics: Dict[str, Any], severity: str, confidence: float, description: str):
        """Store anomaly in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO anomalies 
                (timestamp, anomaly_type, severity, confidence, features, description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                "system_behavior",
                severity,
                confidence,
                json.dumps(metrics),
                description
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing anomaly: {e}")
    
    def predict_performance(self, time_horizon: int = 60) -> MLPrediction:
        """Predict system performance for the next time period"""
        if not SKLEARN_AVAILABLE or not self.performance_predictor:
            return MLPrediction(
                prediction_type="performance",
                value=0.0,
                confidence=0.0,
                timestamp=datetime.now(),
                features={},
                explanation="ML models not available",
                recommendations=[]
            )
        
        # Get recent metrics for prediction
        recent_metrics = list(self.system_metrics_history)[-50:]
        if len(recent_metrics) < 10:
            return MLPrediction(
                prediction_type="performance",
                value=0.0,
                confidence=0.0,
                timestamp=datetime.now(),
                features={},
                explanation="Insufficient data for prediction",
                recommendations=[]
            )
        
        # Prepare features for prediction
        features = []
        for metric in recent_metrics[-10:]:  # Use last 10 data points
            features.extend([
                metric['cpu_percent'],
                metric['memory_percent'],
                metric['disk_percent'],
                metric['network_io'],
                metric['process_count'],
                metric['load_average']
            ])
        
        features_array = np.array(features).reshape(1, -1)
        
        # Make prediction
        try:
            prediction = self.performance_predictor.predict(features_array)[0]
            confidence = 0.8  # Placeholder confidence score
            
            # Generate explanation
            explanation = self._generate_performance_explanation(recent_metrics, prediction)
            recommendations = self._generate_performance_recommendations(prediction)
            
            # Store prediction
            self._store_prediction("performance", prediction, confidence, features, explanation)
            
            return MLPrediction(
                prediction_type="performance",
                value=prediction,
                confidence=confidence,
                timestamp=datetime.now(),
                features={'recent_metrics': len(recent_metrics)},
                explanation=explanation,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error making performance prediction: {e}")
            return MLPrediction(
                prediction_type="performance",
                value=0.0,
                confidence=0.0,
                timestamp=datetime.now(),
                features={},
                explanation=f"Prediction error: {str(e)}",
                recommendations=[]
            )
    
    def _generate_performance_explanation(self, recent_metrics: List[Dict], prediction: float) -> str:
        """Generate explanation for performance prediction"""
        avg_cpu = np.mean([m['cpu_percent'] for m in recent_metrics])
        avg_memory = np.mean([m['memory_percent'] for m in recent_metrics])
        
        if prediction > 80:
            trend = "performance is expected to degrade"
        elif prediction > 60:
            trend = "performance may be affected"
        else:
            trend = "performance is expected to remain stable"
        
        return f"Based on current trends (CPU: {avg_cpu:.1f}%, Memory: {avg_memory:.1f}%), {trend}"
    
    def _generate_performance_recommendations(self, prediction: float) -> List[str]:
        """Generate recommendations based on performance prediction"""
        recommendations = []
        
        if prediction > 80:
            recommendations.extend([
                "Consider reducing system load",
                "Monitor resource-intensive processes",
                "Check for memory leaks",
                "Review system configuration"
            ])
        elif prediction > 60:
            recommendations.extend([
                "Monitor system performance",
                "Check for optimization opportunities",
                "Review recent changes"
            ])
        else:
            recommendations.append("Continue current system management")
        
        return recommendations
    
    def _store_prediction(self, prediction_type: str, value: float, confidence: float, features: Dict, explanation: str):
        """Store prediction in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO predictions 
                (timestamp, prediction_type, value, confidence, features, explanation)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                prediction_type,
                value,
                confidence,
                json.dumps(features),
                explanation
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing prediction: {e}")
    
    def analyze_patterns(self, time_window: int = 3600) -> PatternAnalysis:
        """Analyze patterns in system behavior"""
        if not SKLEARN_AVAILABLE:
            return PatternAnalysis(
                pattern_type="unknown",
                pattern_strength=0.0,
                periodicity=None,
                trend="unknown",
                confidence=0.0,
                features={},
                insights=[]
            )
        
        # Get metrics from time window
        cutoff_time = datetime.now() - timedelta(seconds=time_window)
        recent_metrics = [m for m in self.system_metrics_history if m['timestamp'] > cutoff_time]
        
        if len(recent_metrics) < 10:
            return PatternAnalysis(
                pattern_type="insufficient_data",
                pattern_strength=0.0,
                periodicity=None,
                trend="unknown",
                confidence=0.0,
                features={},
                insights=["Insufficient data for pattern analysis"]
            )
        
        # Analyze patterns
        cpu_values = [m['cpu_percent'] for m in recent_metrics]
        memory_values = [m['memory_percent'] for m in recent_metrics]
        
        # Calculate trends
        cpu_trend = np.polyfit(range(len(cpu_values)), cpu_values, 1)[0]
        memory_trend = np.polyfit(range(len(memory_values)), memory_values, 1)[0]
        
        # Determine pattern type
        if abs(cpu_trend) > 5 or abs(memory_trend) > 5:
            pattern_type = "trending"
            trend = "increasing" if (cpu_trend + memory_trend) / 2 > 0 else "decreasing"
        elif np.std(cpu_values) > 20 or np.std(memory_values) > 20:
            pattern_type = "volatile"
            trend = "unstable"
        else:
            pattern_type = "stable"
            trend = "stable"
        
        # Calculate pattern strength
        pattern_strength = min(1.0, (abs(cpu_trend) + abs(memory_trend)) / 10)
        
        # Generate insights
        insights = self._generate_pattern_insights(cpu_values, memory_values, pattern_type, trend)
        
        # Store pattern
        self._store_pattern(pattern_type, pattern_strength, None, trend, 0.8, {'cpu_trend': cpu_trend, 'memory_trend': memory_trend})
        
        return PatternAnalysis(
            pattern_type=pattern_type,
            pattern_strength=pattern_strength,
            periodicity=None,
            trend=trend,
            confidence=0.8,
            features={'cpu_trend': cpu_trend, 'memory_trend': memory_trend},
            insights=insights
        )
    
    def _generate_pattern_insights(self, cpu_values: List[float], memory_values: List[float], pattern_type: str, trend: str) -> List[str]:
        """Generate insights from pattern analysis"""
        insights = []
        
        avg_cpu = np.mean(cpu_values)
        avg_memory = np.mean(memory_values)
        
        if pattern_type == "trending":
            if trend == "increasing":
                insights.append("System load is trending upward")
                if avg_cpu > 70:
                    insights.append("High CPU usage may require optimization")
                if avg_memory > 80:
                    insights.append("Memory usage is high and increasing")
            else:
                insights.append("System load is trending downward")
                insights.append("Performance is improving")
        
        elif pattern_type == "volatile":
            insights.append("System performance is highly variable")
            insights.append("Consider investigating performance fluctuations")
        
        else:  # stable
            insights.append("System performance is stable")
            if avg_cpu < 50 and avg_memory < 70:
                insights.append("System is running efficiently")
        
        return insights
    
    def _store_pattern(self, pattern_type: str, strength: float, periodicity: str, trend: str, confidence: float, features: Dict):
        """Store pattern in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO patterns 
                (timestamp, pattern_type, strength, periodicity, trend, confidence, features)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(),
                pattern_type,
                strength,
                periodicity,
                trend,
                confidence,
                json.dumps(features)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing pattern: {e}")
    
    def train_models(self, force_retrain: bool = False):
        """Train or retrain ML models"""
        if not SKLEARN_AVAILABLE:
            logger.error("scikit-learn not available for training")
            return
        
        # Get training data from database
        training_data = self._get_training_data()
        
        if len(training_data) < 100:
            logger.warning("Insufficient data for training. Need at least 100 data points.")
            return
        
        # Prepare features and targets
        features = []
        targets = []
        
        for i in range(len(training_data) - 1):
            current_metrics = training_data[i]
            next_metrics = training_data[i + 1]
            
            # Features: current system state
            features.append([
                current_metrics['cpu_percent'],
                current_metrics['memory_percent'],
                current_metrics['disk_percent'],
                current_metrics['network_io'],
                current_metrics['process_count'],
                current_metrics['load_average']
            ])
            
            # Target: next period's performance (average of CPU and memory)
            target = (next_metrics['cpu_percent'] + next_metrics['memory_percent']) / 2
            targets.append(target)
        
        features_array = np.array(features)
        targets_array = np.array(targets)
        
        # Split data
        split_idx = int(len(features_array) * 0.8)
        X_train = features_array[:split_idx]
        y_train = targets_array[:split_idx]
        X_test = features_array[split_idx:]
        y_test = targets_array[split_idx:]
        
        # Train models
        try:
            # Train anomaly detector
            self.anomaly_detector.fit(X_train)
            
            # Train performance predictor
            self.performance_predictor.fit(X_train, y_train)
            
            # Train scalers
            self.feature_scaler.fit(X_train)
            
            # Evaluate models
            y_pred = self.performance_predictor.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            logger.info(f"Model training completed. MSE: {mse:.4f}, MAE: {mae:.4f}")
            
            # Save models
            self._save_models()
            
            # Update model metadata
            self._update_model_metadata(mse, mae)
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
    
    def _get_training_data(self) -> List[Dict[str, Any]]:
        """Get training data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, cpu_percent, memory_percent, disk_percent,
                       network_io, temperature, process_count, load_average
                FROM system_metrics
                ORDER BY timestamp
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'timestamp': datetime.fromisoformat(row[0]),
                    'cpu_percent': row[1],
                    'memory_percent': row[2],
                    'disk_percent': row[3],
                    'network_io': row[4],
                    'temperature': row[5],
                    'process_count': row[6],
                    'load_average': row[7]
                }
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"Error getting training data: {e}")
            return []
    
    def _update_model_metadata(self, mse: float, mae: float):
        """Update model metadata in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO model_metadata 
                (model_name, model_type, version, accuracy, last_updated, parameters)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                "performance_predictor",
                "RandomForestRegressor",
                "1.0",
                1.0 - mse / 100,  # Simple accuracy metric
                datetime.now(),
                json.dumps({
                    'mse': mse,
                    'mae': mae,
                    'n_estimators': 100,
                    'max_depth': 10
                })
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating model metadata: {e}")
    
    def get_ml_analytics(self) -> Dict[str, Any]:
        """Get comprehensive ML analytics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get recent predictions
            cursor.execute('''
                SELECT prediction_type, value, confidence, timestamp
                FROM predictions
                ORDER BY timestamp DESC
                LIMIT 10
            ''')
            predictions = cursor.fetchall()
            
            # Get recent anomalies
            cursor.execute('''
                SELECT anomaly_type, severity, confidence, timestamp, resolved
                FROM anomalies
                ORDER BY timestamp DESC
                LIMIT 10
            ''')
            anomalies = cursor.fetchall()
            
            # Get recent patterns
            cursor.execute('''
                SELECT pattern_type, strength, trend, confidence, timestamp
                FROM patterns
                ORDER BY timestamp DESC
                LIMIT 10
            ''')
            patterns = cursor.fetchall()
            
            # Get model metadata
            cursor.execute('''
                SELECT model_name, accuracy, last_updated
                FROM model_metadata
                ORDER BY last_updated DESC
            ''')
            models = cursor.fetchall()
            
            conn.close()
            
            return {
                'predictions': predictions,
                'anomalies': anomalies,
                'patterns': patterns,
                'models': models,
                'total_metrics': len(self.system_metrics_history),
                'last_update': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting ML analytics: {e}")
            return {}
    
    def display_ml_analytics(self, analytics: Dict[str, Any] = None):
        """Display ML analytics in a formatted way"""
        if not RICH_AVAILABLE:
            print("Rich not available for formatted display")
            return
        
        if analytics is None:
            analytics = self.get_ml_analytics()
        
        # Create analytics panel
        self.console.print(Panel(
            f"[bold blue]Machine Learning Analytics[/bold blue]\n"
            f"Total Metrics: {analytics.get('total_metrics', 0)}\n"
            f"Last Update: {analytics.get('last_update', 'Unknown')}",
            title="ML Integration Status"
        ))
        
        # Display recent predictions
        if analytics.get('predictions'):
            table = Table(title="Recent Predictions")
            table.add_column("Type", style="cyan")
            table.add_column("Value", style="green")
            table.add_column("Confidence", style="yellow")
            table.add_column("Timestamp", style="blue")
            
            for pred in analytics['predictions'][:5]:
                table.add_row(
                    pred[0],
                    f"{pred[1]:.2f}",
                    f"{pred[2]:.2f}",
                    pred[3][:19]
                )
            
            self.console.print(table)
        
        # Display recent anomalies
        if analytics.get('anomalies'):
            table = Table(title="Recent Anomalies")
            table.add_column("Type", style="cyan")
            table.add_column("Severity", style="red")
            table.add_column("Confidence", style="yellow")
            table.add_column("Resolved", style="green")
            
            for anomaly in analytics['anomalies'][:5]:
                severity_color = "red" if anomaly[1] in ["critical", "high"] else "yellow"
                table.add_row(
                    anomaly[0],
                    f"[{severity_color}]{anomaly[1]}[/{severity_color}]",
                    f"{anomaly[2]:.2f}",
                    "✓" if anomaly[4] else "✗"
                )
            
            self.console.print(table)
    
    def run_comprehensive_analysis(self, system_monitor=None) -> Dict[str, Any]:
        """Run comprehensive ML analysis"""
        # Collect current metrics
        metrics = self.collect_system_metrics(system_monitor)
        
        # Run all analyses
        anomaly_result = self.detect_anomalies(metrics)
        prediction_result = self.predict_performance()
        pattern_result = self.analyze_patterns()
        
        return {
            'metrics': metrics,
            'anomaly': anomaly_result,
            'prediction': prediction_result,
            'pattern': pattern_result,
            'timestamp': datetime.now()
        }

def main():
    """Main function for testing ML integration"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Machine Learning Integration Test')
    parser.add_argument('--analyze', action='store_true', help='Run comprehensive analysis')
    parser.add_argument('--train', action='store_true', help='Train models')
    parser.add_argument('--anomaly', action='store_true', help='Test anomaly detection')
    parser.add_argument('--predict', action='store_true', help='Test performance prediction')
    parser.add_argument('--patterns', action='store_true', help='Test pattern analysis')
    parser.add_argument('--analytics', action='store_true', help='Show ML analytics')
    
    args = parser.parse_args()
    
    ml_integration = MachineLearningIntegration()
    
    if args.analyze:
        print("Running comprehensive ML analysis...")
        results = ml_integration.run_comprehensive_analysis()
        print(f"Analysis complete: {results}")
    
    elif args.train:
        print("Training ML models...")
        ml_integration.train_models()
    
    elif args.anomaly:
        print("Testing anomaly detection...")
        anomaly = ml_integration.detect_anomalies()
        print(f"Anomaly detected: {anomaly.is_anomaly}, Severity: {anomaly.severity}")
    
    elif args.predict:
        print("Testing performance prediction...")
        prediction = ml_integration.predict_performance()
        print(f"Prediction: {prediction.value}, Confidence: {prediction.confidence}")
    
    elif args.patterns:
        print("Testing pattern analysis...")
        pattern = ml_integration.analyze_patterns()
        print(f"Pattern type: {pattern.pattern_type}, Trend: {pattern.trend}")
    
    elif args.analytics:
        print("Showing ML analytics...")
        ml_integration.display_ml_analytics()
    
    else:
        print("Machine Learning Integration Module")
        print("Use --help for available options")

if __name__ == "__main__":
    main() 