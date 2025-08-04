# Machine Learning Integration Guide

## 🧠 Overview

The `machine_learning_integration.py` module provides core ML capabilities for the Overseer system, including:

- **Anomaly Detection**: Identify unusual system behavior patterns
- **Performance Prediction**: Forecast system performance trends
- **Pattern Analysis**: Analyze system behavior patterns over time
- **Intelligent Optimization**: ML-driven system optimization recommendations

## 🏗️ Architecture

### Core Components

```python
class MachineLearningIntegration:
    """
    Core ML integration with the following capabilities:
    - Real-time system metrics collection
    - Anomaly detection using Isolation Forest
    - Performance prediction using Random Forest
    - Pattern analysis using clustering
    - Model training and persistence
    """
```

### Data Structures

#### MLPrediction
```python
@dataclass
class MLPrediction:
    prediction_type: str      # Type of prediction (performance, resource, etc.)
    value: Union[float, int, str]  # Predicted value
    confidence: float         # Confidence score (0-1)
    timestamp: datetime       # When prediction was made
    features: Dict[str, Any] # Features used for prediction
    explanation: str          # Human-readable explanation
    recommendations: List[str] # Suggested actions
```

#### AnomalyDetection
```python
@dataclass
class AnomalyDetection:
    is_anomaly: bool         # Whether anomaly was detected
    severity: str            # Severity level (none, medium, high, critical)
    confidence: float        # Confidence score (0-1)
    timestamp: datetime      # When anomaly was detected
    features: Dict[str, Any] # System metrics at detection time
    description: str         # Human-readable description
    suggested_actions: List[str] # Recommended actions
```

#### PatternAnalysis
```python
@dataclass
class PatternAnalysis:
    pattern_type: str        # Type of pattern (stable, trending, volatile)
    pattern_strength: float  # Strength of the pattern (0-1)
    periodicity: Optional[str] # Periodic patterns if detected
    trend: str              # Trend direction (increasing, decreasing, stable)
    confidence: float       # Confidence score (0-1)
    features: Dict[str, Any] # Pattern features
    insights: List[str]     # Generated insights
```

## 🚀 Usage Examples

### Basic Usage

```python
from machine_learning_integration import MachineLearningIntegration

# Initialize ML integration
ml_integration = MachineLearningIntegration()

# Collect system metrics
metrics = ml_integration.collect_system_metrics(system_monitor)

# Detect anomalies
anomaly = ml_integration.detect_anomalies(metrics)
if anomaly.is_anomaly:
    print(f"Anomaly detected: {anomaly.description}")
    print(f"Suggested actions: {anomaly.suggested_actions}")

# Predict performance
prediction = ml_integration.predict_performance()
print(f"Performance prediction: {prediction.value}")
print(f"Explanation: {prediction.explanation}")

# Analyze patterns
pattern = ml_integration.analyze_patterns()
print(f"Pattern type: {pattern.pattern_type}")
print(f"Trend: {pattern.trend}")
print(f"Insights: {pattern.insights}")
```

### Comprehensive Analysis

```python
# Run all ML analyses at once
results = ml_integration.run_comprehensive_analysis(system_monitor)

print(f"Current metrics: {results['metrics']}")
print(f"Anomaly: {results['anomaly']}")
print(f"Prediction: {results['prediction']}")
print(f"Pattern: {results['pattern']}")
```

### Model Training

```python
# Train ML models with collected data
ml_integration.train_models()

# Force retrain models
ml_integration.train_models(force_retrain=True)
```

### Analytics and Monitoring

```python
# Get comprehensive ML analytics
analytics = ml_integration.get_ml_analytics()

# Display formatted analytics
ml_integration.display_ml_analytics(analytics)
```

## 📊 ML Capabilities

### 1. Anomaly Detection

**Purpose**: Identify unusual system behavior patterns that may indicate problems.

**Algorithm**: Isolation Forest
- **Advantages**: Fast, handles high-dimensional data, no need for labeled data
- **Parameters**: contamination=0.1, n_estimators=100
- **Features**: CPU%, Memory%, Disk%, Network I/O, Process Count, Load Average

**Severity Levels**:
- **None**: Normal system behavior
- **Medium**: Minor anomalies, continue monitoring
- **High**: Significant anomalies, investigate further
- **Critical**: Severe anomalies, immediate action required

**Example Output**:
```
Anomaly detected: High anomaly: High CPU usage; High memory usage
Severity: high
Confidence: 0.85
Suggested actions: ['Monitor system performance', 'Check for resource-intensive processes']
```

### 2. Performance Prediction

**Purpose**: Forecast system performance trends to enable proactive optimization.

**Algorithm**: Random Forest Regressor
- **Advantages**: Handles non-linear relationships, robust to outliers
- **Parameters**: n_estimators=100, max_depth=10
- **Features**: Historical system metrics (last 10 data points)
- **Target**: Future performance score (average of CPU and memory)

**Prediction Types**:
- **Performance Score**: 0-100 scale indicating expected system performance
- **Time Horizon**: 60 seconds (configurable)
- **Confidence**: Model confidence in prediction

**Example Output**:
```
Performance prediction: 75.2
Confidence: 0.82
Explanation: Based on current trends (CPU: 68.5%, Memory: 72.3%), performance may be affected
Recommendations: ['Monitor system performance', 'Check for optimization opportunities']
```

### 3. Pattern Analysis

**Purpose**: Identify and analyze system behavior patterns over time.

**Algorithm**: Trend analysis with polynomial fitting
- **Features**: CPU and memory trends over time window
- **Pattern Types**: stable, trending, volatile
- **Trends**: increasing, decreasing, stable, unstable

**Pattern Types**:
- **Stable**: Consistent system behavior
- **Trending**: Clear upward or downward trends
- **Volatile**: Highly variable performance

**Example Output**:
```
Pattern type: trending
Pattern strength: 0.75
Trend: increasing
Insights: ['System load is trending upward', 'High CPU usage may require optimization']
```

## 🗄️ Database Schema

### System Metrics Table
```sql
CREATE TABLE system_metrics (
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
);
```

### Predictions Table
```sql
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME,
    prediction_type TEXT,
    value REAL,
    confidence REAL,
    features TEXT,
    explanation TEXT
);
```

### Anomalies Table
```sql
CREATE TABLE anomalies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME,
    anomaly_type TEXT,
    severity TEXT,
    confidence REAL,
    features TEXT,
    description TEXT,
    resolved BOOLEAN DEFAULT FALSE
);
```

### Patterns Table
```sql
CREATE TABLE patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME,
    pattern_type TEXT,
    strength REAL,
    periodicity TEXT,
    trend TEXT,
    confidence REAL,
    features TEXT
);
```

### Model Metadata Table
```sql
CREATE TABLE model_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT,
    model_type TEXT,
    version TEXT,
    accuracy REAL,
    last_updated DATETIME,
    parameters TEXT
);
```

## 🔧 Configuration

### Dependencies

**Required**:
- `scikit-learn` - Core ML algorithms
- `numpy` - Numerical computations
- `pandas` - Data manipulation
- `sqlite3` - Database storage

**Optional**:
- `torch` - PyTorch for advanced ML
- `transformers` - Hugging Face transformers
- `rich` - Formatted output

### Model Storage

Models are stored in the `models/` directory:
- `anomaly_detector.pkl` - Trained anomaly detection model
- `performance_predictor.pkl` - Trained performance prediction model
- `feature_scaler.pkl` - Feature scaling parameters

### Database Location

Default database location: `backend/db/ml_integration.db`

## 📈 Performance Considerations

### Memory Usage
- **Metrics History**: Limited to 1000 data points (configurable)
- **Anomaly History**: Limited to 100 anomalies (configurable)
- **Model Size**: ~1-5MB per model

### CPU Usage
- **Anomaly Detection**: ~1-5ms per prediction
- **Performance Prediction**: ~5-10ms per prediction
- **Pattern Analysis**: ~10-20ms per analysis
- **Model Training**: ~1-5 seconds (depends on data size)

### Storage Requirements
- **Metrics**: ~100 bytes per data point
- **Predictions**: ~200 bytes per prediction
- **Anomalies**: ~300 bytes per anomaly
- **Patterns**: ~250 bytes per pattern

## 🛡️ Error Handling

### Graceful Degradation
- If ML libraries are not available, features return default values
- Database errors are logged but don't crash the system
- Model loading failures trigger automatic retraining

### Validation
- Input validation for all public methods
- Range checking for confidence scores (0-1)
- Timestamp validation for historical data

### Logging
- Comprehensive logging for debugging
- Error tracking for model failures
- Performance monitoring for slow operations

## 🔍 Testing

### Command Line Testing

```bash
# Test anomaly detection
python machine_learning_integration.py --anomaly

# Test performance prediction
python machine_learning_integration.py --predict

# Test pattern analysis
python machine_learning_integration.py --patterns

# Run comprehensive analysis
python machine_learning_integration.py --analyze

# Train models
python machine_learning_integration.py --train

# Show analytics
python machine_learning_integration.py --analytics
```

### Integration Testing

```python
# Test with system monitor integration
from system_monitor import SystemMonitor

system_monitor = SystemMonitor()
ml_integration = MachineLearningIntegration()

# Run analysis with real system data
results = ml_integration.run_comprehensive_analysis(system_monitor)
```

## 🚀 Advanced Features

### Custom Model Training

```python
# Train models with custom parameters
ml_integration.anomaly_detector = IsolationForest(
    contamination=0.05,  # More sensitive
    n_estimators=200,    # More trees
    random_state=42
)

ml_integration.train_models()
```

### Custom Feature Engineering

```python
# Add custom features to metrics collection
def custom_metrics_collector():
    metrics = ml_integration.collect_system_metrics()
    
    # Add custom features
    metrics['custom_feature'] = calculate_custom_feature()
    metrics['derived_metric'] = metrics['cpu_percent'] * metrics['memory_percent']
    
    return metrics
```

### Real-time Monitoring

```python
import time

# Continuous monitoring loop
while True:
    results = ml_integration.run_comprehensive_analysis()
    
    if results['anomaly'].is_anomaly:
        print(f"🚨 Anomaly detected: {results['anomaly'].description}")
    
    if results['prediction'].value > 80:
        print(f"⚠️ Performance warning: {results['prediction'].explanation}")
    
    time.sleep(30)  # Check every 30 seconds
```

## 🎯 Best Practices

### 1. Data Collection
- Collect metrics regularly (every 30-60 seconds)
- Store historical data for training
- Validate data quality before analysis

### 2. Model Management
- Retrain models periodically (weekly/monthly)
- Monitor model performance
- Keep backup models

### 3. Performance Optimization
- Use appropriate batch sizes for analysis
- Cache frequently accessed data
- Optimize database queries

### 4. Error Handling
- Implement graceful degradation
- Log all errors for debugging
- Provide fallback mechanisms

## 🔮 Future Enhancements

### Planned Features
- **Deep Learning Models**: LSTM for time series prediction
- **Reinforcement Learning**: Adaptive system optimization
- **Federated Learning**: Privacy-preserving model training
- **AutoML**: Automatic model selection and hyperparameter tuning

### Integration Opportunities
- **Alert System**: Integration with alert manager
- **Dashboard**: Real-time ML analytics dashboard
- **API**: REST API for external ML services
- **Export**: Data export for external analysis

---

**The Machine Learning Integration module provides powerful AI-driven insights for system optimization and proactive problem detection.** 🚀 