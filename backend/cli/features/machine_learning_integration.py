"""
Machine Learning Integration for System Monitoring
Provides ML-powered system analysis, pattern recognition, and intelligent recommendations.
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

try:
    from sklearn.ensemble import RandomForestClassifier, IsolationForest
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    from sklearn.linear_model import LinearRegression
    from sklearn.decomposition import PCA
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

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
class MLModel:
    """Machine learning model data structure"""
    model_type: str  # 'anomaly_detection', 'performance_prediction', 'pattern_recognition'
    model_name: str
    accuracy: float
    training_date: float
    features: List[str]
    parameters: Dict[str, Any]
    status: str  # 'trained', 'training', 'error'

@dataclass
class MLPrediction:
    """ML prediction data structure"""
    timestamp: float
    model_type: str
    prediction: Any
    confidence: float
    features_used: List[str]
    metadata: Dict[str, Any]

@dataclass
class SystemPattern:
    """System pattern data structure"""
    pattern_type: str  # 'usage_pattern', 'performance_pattern', 'anomaly_pattern'
    pattern_id: str
    description: str
    confidence: float
    features: List[str]
    frequency: float
    severity: str

class MachineLearningIntegration:
    """Machine learning integration for system monitoring"""
    
    def __init__(self, config: Dict = None):
        """Initialize ML integration"""
        self.console = Console() if RICH_AVAILABLE else None
        self.config = config or {}
        
        # Initialize components
        self.system_monitor = SystemMonitor()
        self.predictive_analytics = PredictiveAnalytics()
        self.alert_manager = AlertManager()
        
        # ML settings
        self.models_dir = self.config.get('models_dir', 'ml_models')
        self.features_dir = self.config.get('features_dir', 'ml_features')
        
        # Create directories
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.features_dir, exist_ok=True)
        
        # Database paths
        self.system_db = os.path.join(os.path.dirname(__file__), '../../db/system_metrics.db')
        self.alerts_db = os.path.join(os.path.dirname(__file__), '../../db/system_alerts.db')
        self.ml_db = os.path.join(os.path.dirname(__file__), '../../db/ml_integration.db')
        
        # Initialize ML models
        self.models = {}
        self.scalers = {}
        self.feature_names = []
        
        # Initialize database
        self._init_database()
        
        if not SKLEARN_AVAILABLE:
            if self.console:
                self.console.print("[yellow]Warning: scikit-learn not available. ML features will be limited.[/yellow]")
    
    def _init_database(self):
        """Initialize ML integration database"""
        try:
            conn = sqlite3.connect(self.ml_db)
            cursor = conn.cursor()
            
            # Create models table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ml_models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_type TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    accuracy REAL,
                    training_date REAL,
                    features TEXT,
                    parameters TEXT,
                    status TEXT DEFAULT 'training',
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            ''')
            
            # Create predictions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ml_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    model_type TEXT NOT NULL,
                    prediction TEXT,
                    confidence REAL,
                    features_used TEXT,
                    metadata TEXT,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            ''')
            
            # Create patterns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT NOT NULL,
                    pattern_id TEXT NOT NULL,
                    description TEXT,
                    confidence REAL,
                    features TEXT,
                    frequency REAL,
                    severity TEXT,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            ''')
            
            # Create feature engineering table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feature_engineering (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feature_name TEXT NOT NULL,
                    feature_type TEXT NOT NULL,
                    calculation_method TEXT,
                    parameters TEXT,
                    status TEXT DEFAULT 'active',
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error initializing ML database: {e}[/red]")
    
    def collect_training_data(self, time_range: str = '7d') -> np.ndarray:
        """Collect training data for ML models"""
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
            
            # Get system metrics
            conn = sqlite3.connect(self.system_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM system_metrics 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            ''', (start_time, end_time))
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return np.array([])
            
            # Extract features
            features = []
            for row in rows:
                feature_vector = [
                    row[2],  # cpu_percent
                    row[3],  # memory_percent
                    row[4],  # disk_percent
                    row[5],  # network_sent_mb
                    row[6],  # network_recv_mb
                    row[7],  # process_count
                    row[8],  # load_average_1
                    row[9],  # load_average_5
                    row[10], # load_average_15
                    row[11] if row[11] else 0,  # temperature
                    row[12] if row[12] else 0,  # battery_percent
                    1 if row[13] else 0  # battery_plugged
                ]
                features.append(feature_vector)
            
            return np.array(features)
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error collecting training data: {e}[/red]")
            return np.array([])
    
    def train_anomaly_detection_model(self, time_range: str = '7d') -> str:
        """Train anomaly detection model using Isolation Forest"""
        if not SKLEARN_AVAILABLE:
            return "scikit-learn not available for anomaly detection"
        
        try:
            # Collect training data
            features = self.collect_training_data(time_range)
            
            if len(features) == 0:
                return "No training data available"
            
            # Prepare features
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            # Train Isolation Forest
            model = IsolationForest(
                contamination=0.1,
                random_state=42,
                n_estimators=100
            )
            
            model.fit(features_scaled)
            
            # Save model and scaler
            self.models['anomaly_detection'] = model
            self.scalers['anomaly_detection'] = scaler
            self.feature_names = [
                'cpu_percent', 'memory_percent', 'disk_percent',
                'network_sent_mb', 'network_recv_mb', 'process_count',
                'load_average_1', 'load_average_5', 'load_average_15',
                'temperature', 'battery_percent', 'battery_plugged'
            ]
            
            # Save model info to database
            self._save_model_info('anomaly_detection', 'IsolationForest', 
                                features=self.feature_names,
                                parameters={'contamination': 0.1, 'n_estimators': 100})
            
            return "✅ Anomaly detection model trained successfully"
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error training anomaly detection model: {e}[/red]")
            return f"Error: {e}"
    
    def train_performance_prediction_model(self, time_range: str = '7d') -> str:
        """Train performance prediction model using Random Forest"""
        if not SKLEARN_AVAILABLE:
            return "scikit-learn not available for performance prediction"
        
        try:
            # Collect training data
            features = self.collect_training_data(time_range)
            
            if len(features) < 100:  # Need sufficient data
                return "Insufficient training data (need at least 100 samples)"
            
            # Create target variables (predict next hour's CPU and memory)
            X = features[:-1]  # All but last sample
            y_cpu = features[1:, 0]  # CPU of next sample
            y_memory = features[1:, 1]  # Memory of next sample
            
            # Prepare features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Train CPU prediction model
            cpu_model = RandomForestClassifier(n_estimators=100, random_state=42)
            cpu_bins = np.digitize(y_cpu, bins=[0, 25, 50, 75, 100])
            cpu_model.fit(X_scaled, cpu_bins)
            
            # Train memory prediction model
            memory_model = RandomForestClassifier(n_estimators=100, random_state=42)
            memory_bins = np.digitize(y_memory, bins=[0, 25, 50, 75, 100])
            memory_model.fit(X_scaled, memory_bins)
            
            # Save models
            self.models['cpu_prediction'] = cpu_model
            self.models['memory_prediction'] = memory_model
            self.scalers['performance_prediction'] = scaler
            
            # Save model info
            self._save_model_info('cpu_prediction', 'RandomForestClassifier', 
                                features=self.feature_names,
                                parameters={'n_estimators': 100})
            self._save_model_info('memory_prediction', 'RandomForestClassifier', 
                                features=self.feature_names,
                                parameters={'n_estimators': 100})
            
            return "✅ Performance prediction models trained successfully"
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error training performance prediction model: {e}[/red]")
            return f"Error: {e}"
    
    def detect_anomalies(self, current_metrics) -> Dict[str, Any]:
        """Detect anomalies using trained model"""
        if not SKLEARN_AVAILABLE or 'anomaly_detection' not in self.models:
            return {"anomalies": [], "message": "ML model not available"}
        
        try:
            # Prepare current features
            features = [
                current_metrics.cpu_percent,
                current_metrics.memory_percent,
                current_metrics.disk_percent,
                current_metrics.network_sent_mb,
                current_metrics.network_recv_mb,
                current_metrics.process_count,
                current_metrics.load_average[0],
                current_metrics.load_average[1],
                current_metrics.load_average[2],
                current_metrics.temperature or 0,
                current_metrics.battery_percent or 0,
                1 if current_metrics.battery_plugged else 0
            ]
            
            # Scale features
            scaler = self.scalers['anomaly_detection']
            features_scaled = scaler.transform([features])
            
            # Predict anomaly
            model = self.models['anomaly_detection']
            prediction = model.predict(features_scaled)[0]
            score = model.decision_function(features_scaled)[0]
            
            # -1 indicates anomaly, 1 indicates normal
            is_anomaly = prediction == -1
            confidence = abs(score)
            
            result = {
                "is_anomaly": is_anomaly,
                "confidence": confidence,
                "score": score,
                "features": features,
                "timestamp": time.time()
            }
            
            # Save prediction
            self._save_prediction('anomaly_detection', result)
            
            return result
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error detecting anomalies: {e}[/red]")
            return {"anomalies": [], "error": str(e)}
    
    def predict_performance(self, current_metrics) -> Dict[str, Any]:
        """Predict future performance using trained models"""
        if not SKLEARN_AVAILABLE or 'cpu_prediction' not in self.models:
            return {"predictions": {}, "message": "ML models not available"}
        
        try:
            # Prepare current features
            features = [
                current_metrics.cpu_percent,
                current_metrics.memory_percent,
                current_metrics.disk_percent,
                current_metrics.network_sent_mb,
                current_metrics.network_recv_mb,
                current_metrics.process_count,
                current_metrics.load_average[0],
                current_metrics.load_average[1],
                current_metrics.load_average[2],
                current_metrics.temperature or 0,
                current_metrics.battery_percent or 0,
                1 if current_metrics.battery_plugged else 0
            ]
            
            # Scale features
            scaler = self.scalers['performance_prediction']
            features_scaled = scaler.transform([features])
            
            # Make predictions
            cpu_model = self.models['cpu_prediction']
            memory_model = self.models['memory_prediction']
            
            cpu_prediction = cpu_model.predict(features_scaled)[0]
            memory_prediction = memory_model.predict(features_scaled)[0]
            
            # Convert bin predictions back to ranges
            cpu_ranges = ['0-25%', '25-50%', '50-75%', '75-100%']
            memory_ranges = ['0-25%', '25-50%', '50-75%', '75-100%']
            
            cpu_confidence = max(cpu_model.predict_proba(features_scaled)[0])
            memory_confidence = max(memory_model.predict_proba(features_scaled)[0])
            
            predictions = {
                "cpu_prediction": {
                    "range": cpu_ranges[cpu_prediction - 1],
                    "confidence": cpu_confidence
                },
                "memory_prediction": {
                    "range": memory_ranges[memory_prediction - 1],
                    "confidence": memory_confidence
                },
                "timestamp": time.time()
            }
            
            # Save prediction
            self._save_prediction('performance_prediction', predictions)
            
            return predictions
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error predicting performance: {e}[/red]")
            return {"predictions": {}, "error": str(e)}
    
    def identify_patterns(self, time_range: str = '7d') -> List[SystemPattern]:
        """Identify system patterns using clustering"""
        if not SKLEARN_AVAILABLE:
            return []
        
        try:
            # Collect data
            features = self.collect_training_data(time_range)
            
            if len(features) < 50:
                return []
            
            # Use PCA for dimensionality reduction
            pca = PCA(n_components=3)
            features_reduced = pca.fit_transform(features)
            
            # Apply K-means clustering
            kmeans = KMeans(n_clusters=5, random_state=42)
            clusters = kmeans.fit_predict(features_reduced)
            
            # Analyze patterns
            patterns = []
            unique_clusters = set(clusters)
            
            for cluster_id in unique_clusters:
                cluster_data = features[clusters == cluster_id]
                
                # Calculate pattern characteristics
                avg_cpu = np.mean(cluster_data[:, 0])
                avg_memory = np.mean(cluster_data[:, 1])
                avg_disk = np.mean(cluster_data[:, 4])
                
                # Determine pattern type
                if avg_cpu > 70:
                    pattern_type = "high_cpu_usage"
                    severity = "high"
                elif avg_memory > 80:
                    pattern_type = "high_memory_usage"
                    severity = "high"
                elif avg_disk > 85:
                    pattern_type = "high_disk_usage"
                    severity = "medium"
                else:
                    pattern_type = "normal_usage"
                    severity = "low"
                
                # Calculate frequency
                frequency = len(cluster_data) / len(features)
                
                # Create pattern
                pattern = SystemPattern(
                    pattern_type=pattern_type,
                    pattern_id=f"pattern_{cluster_id}",
                    description=f"Cluster {cluster_id}: CPU={avg_cpu:.1f}%, Memory={avg_memory:.1f}%, Disk={avg_disk:.1f}%",
                    confidence=0.8,
                    features=['cpu_percent', 'memory_percent', 'disk_percent'],
                    frequency=frequency,
                    severity=severity
                )
                
                patterns.append(pattern)
                
                # Save pattern to database
                self._save_pattern(pattern)
            
            return patterns
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error identifying patterns: {e}[/red]")
            return []
    
    def generate_ml_recommendations(self, current_metrics, predictions: Dict = None) -> List[str]:
        """Generate ML-based recommendations"""
        recommendations = []
        
        try:
            # Anomaly-based recommendations
            anomaly_result = self.detect_anomalies(current_metrics)
            if anomaly_result.get("is_anomaly", False):
                confidence = anomaly_result.get("confidence", 0)
                if confidence > 0.7:
                    recommendations.append(f"🚨 ML detected system anomaly (confidence: {confidence:.2f}). Investigate immediately.")
                else:
                    recommendations.append(f"⚠️ Potential system anomaly detected (confidence: {confidence:.2f}). Monitor closely.")
            
            # Performance prediction recommendations
            if predictions:
                cpu_pred = predictions.get("cpu_prediction", {})
                memory_pred = predictions.get("memory_prediction", {})
                
                if cpu_pred.get("range") == "75-100%" and cpu_pred.get("confidence", 0) > 0.6:
                    recommendations.append("📈 ML predicts high CPU usage. Consider resource optimization.")
                
                if memory_pred.get("range") == "75-100%" and memory_pred.get("confidence", 0) > 0.6:
                    recommendations.append("📈 ML predicts high memory usage. Consider memory cleanup.")
            
            # Pattern-based recommendations
            patterns = self.identify_patterns('24h')
            high_severity_patterns = [p for p in patterns if p.severity == "high"]
            
            if high_severity_patterns:
                recommendations.append(f"🔍 ML identified {len(high_severity_patterns)} high-severity usage patterns. Review system behavior.")
            
            return recommendations
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error generating ML recommendations: {e}[/red]")
            return ["Error generating ML recommendations"]
    
    def _save_model_info(self, model_type: str, model_name: str, accuracy: float = None,
                        features: List[str] = None, parameters: Dict = None):
        """Save model information to database"""
        try:
            conn = sqlite3.connect(self.ml_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO ml_models (model_type, model_name, accuracy, training_date, features, parameters, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                model_type,
                model_name,
                accuracy,
                time.time(),
                json.dumps(features) if features else None,
                json.dumps(parameters) if parameters else None,
                'trained'
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error saving model info: {e}[/red]")
    
    def _save_prediction(self, model_type: str, prediction_data: Dict):
        """Save prediction to database"""
        try:
            conn = sqlite3.connect(self.ml_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO ml_predictions (timestamp, model_type, prediction, confidence, features_used, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                prediction_data.get('timestamp', time.time()),
                model_type,
                json.dumps(prediction_data),
                prediction_data.get('confidence', 0.0),
                json.dumps(self.feature_names),
                json.dumps(prediction_data.get('metadata', {}))
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error saving prediction: {e}[/red]")
    
    def _save_pattern(self, pattern: SystemPattern):
        """Save pattern to database"""
        try:
            conn = sqlite3.connect(self.ml_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_patterns (pattern_type, pattern_id, description, confidence, features, frequency, severity)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                pattern.pattern_type,
                pattern.pattern_id,
                pattern.description,
                pattern.confidence,
                json.dumps(pattern.features),
                pattern.frequency,
                pattern.severity
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error saving pattern: {e}[/red]")
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all ML models"""
        try:
            conn = sqlite3.connect(self.ml_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT model_type, model_name, accuracy, status, training_date
                FROM ml_models
                ORDER BY training_date DESC
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            models = {}
            for row in rows:
                models[row[0]] = {
                    'model_name': row[1],
                    'accuracy': row[2],
                    'status': row[3],
                    'training_date': row[4]
                }
            
            return models
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error getting model status: {e}[/red]")
            return {}
    
    def display_ml_status(self):
        """Display ML integration status"""
        if not RICH_AVAILABLE:
            print("Rich library required for formatted display")
            return
        
        # Get model status
        models = self.get_model_status()
        
        # Create status table
        status_table = Table(title="Machine Learning Integration Status")
        status_table.add_column("Model Type", style="cyan")
        status_table.add_column("Model Name", style="green")
        status_table.add_column("Status", style="yellow")
        status_table.add_column("Accuracy", style="magenta")
        status_table.add_column("Last Trained", style="blue")
        
        for model_type, info in models.items():
            status_color = "green" if info['status'] == 'trained' else "red"
            accuracy = f"{info['accuracy']:.2f}" if info['accuracy'] else "N/A"
            training_date = datetime.fromtimestamp(info['training_date']).strftime("%Y-%m-%d %H:%M") if info['training_date'] else "N/A"
            
            status_table.add_row(
                model_type,
                info['model_name'],
                f"[{status_color}]{info['status']}[/{status_color}]",
                accuracy,
                training_date
            )
        
        self.console.print(status_table)
        
        # Display scikit-learn availability
        sklearn_status = "✅ Available" if SKLEARN_AVAILABLE else "❌ Not Available"
        self.console.print(f"\n[bold]scikit-learn Status:[/bold] {sklearn_status}")

def main():
    """Main function for standalone testing"""
    ml_integration = MachineLearningIntegration()
    
    print("🤖 Machine Learning Integration")
    print("=" * 50)
    
    # Display status
    ml_integration.display_ml_status()
    
    # Test ML features
    print("\n🧪 Testing ML features...")
    
    # Train models
    result = ml_integration.train_anomaly_detection_model()
    print(f"Anomaly Detection: {result}")
    
    result = ml_integration.train_performance_prediction_model()
    print(f"Performance Prediction: {result}")
    
    # Test with current metrics
    current_metrics = ml_integration.system_monitor.collect_metrics()
    if current_metrics:
        # Test anomaly detection
        anomaly_result = ml_integration.detect_anomalies(current_metrics)
        print(f"Anomaly Detection Result: {anomaly_result}")
        
        # Test performance prediction
        prediction_result = ml_integration.predict_performance(current_metrics)
        print(f"Performance Prediction: {prediction_result}")
        
        # Test pattern identification
        patterns = ml_integration.identify_patterns('24h')
        print(f"Identified Patterns: {len(patterns)}")
        
        # Test ML recommendations
        recommendations = ml_integration.generate_ml_recommendations(current_metrics, prediction_result)
        print(f"ML Recommendations: {recommendations}")
    
    print("\n✅ Machine learning integration tests completed!")

if __name__ == "__main__":
    main() 