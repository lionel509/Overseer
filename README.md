# Overseer

**AI-native Ubuntu interface for natural language command execution with comprehensive LLM integration**

---

## 🎯 Purpose

**Overseer** is a comprehensive AI-powered system management platform that makes Linux system administration accessible and intuitive for everyone. Powered by local AI models (Gemma 3n, Ollama) and advanced machine learning, Overseer translates natural language into safe, executable Linux commands while providing intelligent system monitoring, optimization, and automation.

**How it helps humans:**
- **Lowers the barrier to entry:** Anyone can manage their system, regardless of technical background
- **Saves time:** No need to search for the right command syntax—just ask in plain English
- **Reduces errors:** Built-in safety checks and LLM-powered validation prevent dangerous commands
- **Boosts productivity:** Power users can automate and chain complex tasks with simple prompts
- **Enhances learning:** Users can see the actual shell commands generated, helping them learn Linux over time
- **Intelligent monitoring:** AI-powered system monitoring with predictive analytics and proactive alerts
- **Seamless integration:** Works natively on Ubuntu, available instantly via CLI, desktop app, or keyboard shortcut

---

## 🚀 Key Features

### 🤖 AI-Powered Core Features

- **LLM Integration**: Direct integration with Gemma 3n, Ollama, and other local AI models
- **Natural Language Processing**: Advanced NLP for understanding user intent and context
- **Intelligent Command Generation**: AI-powered command translation with safety validation
- **Context Awareness**: Maintains conversation context and system state across sessions

### 📊 Advanced System Monitoring

- **Real-time Analytics**: Live system metrics with AI-driven insights
- **Predictive Analytics**: ML-powered performance prediction and trend analysis
- **Intelligent Alerts**: LLM-based alert severity assessment and custom alert rules
- **Unified Dashboard**: Comprehensive system monitoring with AI recommendations

### 🧠 Machine Learning Integration

- **Pattern Recognition**: AI-powered system behavior analysis
- **Anomaly Detection**: ML-based detection of unusual system patterns
- **Performance Optimization**: AI-assisted system optimization recommendations
- **Continuous Learning**: User interaction data improves AI performance over time

### 🔧 AI-Enhanced Tools

- **Smart File Organization**: AI-powered file categorization and sorting
- **Intelligent Search**: Semantic file search with content understanding
- **Tool Recommendations**: Context-aware tool suggestions based on system state
- **Command Correction**: AI-assisted command validation and correction

### 🌐 REST API System

- **FastAPI Framework**: High-performance async REST API with auto-generated documentation
- **Comprehensive Tool Endpoints**: Full API access to all CLI tools and system features
- **Real-time WebSocket**: Live system monitoring and status updates
- **Cross-Platform Integration**: CORS support for web clients and desktop integration

### 🛡️ Security & Safety

- **Multi-layered Sandbox**: Secure command execution environment
- **Permission Management**: Granular system access control
- **Audit Logging**: Comprehensive security event tracking
- **Data Encryption**: Sensitive data encrypted at rest

---

## 🏗️ Architecture

```
Overseer/
├── backend/           # Core AI engine and system integration
│   ├── cli/          # Command-line interface with LLM integration
│   ├── core/         # Core AI and system functionality
│   ├── db/           # Database and knowledge stores
│   └── interfaces/   # API and communication layers
├── desktop-app/      # Modern React/Electron desktop interface
├── training/         # AI model training and continuous learning
└── data/            # Training data and system knowledge
```

---

## 🚀 Quick Start

### Installation

#### Quick Install (Recommended)
```bash
# Clone and install in one go
git clone https://github.com/your-username/overseer.git
cd Overseer
pip install -e ./backend/
```

#### Using Installation Script
```bash
git clone https://github.com/your-username/overseer.git
cd Overseer
python install.py
```

### Basic Usage

```bash
# CLI mode with local LLM
overseer --mode local --prompt "install nvitop"

# CLI mode with Gemini API
overseer --mode gemini --prompt "fix broken packages"

# Interactive chat mode
overseer

# Desktop app
cd desktop-app && npm run dev

# REST API server
cd backend && python -m api.main
```

### REST API Usage

```bash
# Start the API server
cd backend
python -m api.main

# File search via API
curl -X POST "http://localhost:8000/api/tools/file-search/search" \
  -H "Content-Type: application/json" \
  -d '{"pattern": "*.py", "search_content": true}'

# System monitoring via API
curl "http://localhost:8000/api/tools/real-time-stats/current"

# Command execution via API
curl -X POST "http://localhost:8000/api/tools/command-processor/execute" \
  -H "Content-Type: application/json" \
  -d '{"command": "system_info"}'
```

### Shell Integration

Add to your `.bashrc` or `.zshrc`:
```bash
alias overseer='python3 /path/to/overseer/backend/cli/overseer_cli.py'
```

---

## 🧠 AI Model Integration

### Supported Models
- **Gemma 3n**: Local inference via Ollama
- **Gemini API**: Google's Gemini model via API
- **Custom Models**: Support for custom fine-tuned models
- **Hybrid Mode**: Combine multiple models for enhanced performance

### Model Configuration
```bash
# Configure local model
overseer --settings --llm-model gemma3n

# Configure API model
overseer --settings --llm-api-key YOUR_API_KEY

# Test model integration
overseer --test-llm
```

---

## 📊 System Monitoring Features

### Real-time Monitoring
- **CPU/Memory/Disk**: Live resource monitoring with AI insights
- **Process Analysis**: Intelligent process identification and management
- **Network Monitoring**: Bandwidth and connection analysis
- **GPU Monitoring**: NVIDIA GPU monitoring with AI optimization

### Predictive Analytics
- **Performance Prediction**: ML-based performance forecasting
- **Anomaly Detection**: AI-powered detection of unusual patterns
- **Trend Analysis**: Long-term system behavior analysis
- **Capacity Planning**: Intelligent resource planning recommendations

### Intelligent Alerts
- **Smart Severity**: LLM-based alert severity assessment
- **Custom Rules**: AI-assisted custom alert rule creation
- **Proactive Notifications**: Predictive alert generation
- **Context-Aware**: Alerts with relevant context and solutions

---

## 🔧 Advanced Features

### AI-Powered Organization
```bash
# Auto-organize files with AI
overseer --feature auto_organize --path ~/Downloads

# Smart file search
overseer --feature file_search --query "machine learning projects"

# Intelligent folder sorting
overseer --feature folder_sorter --path ~/Documents
```

### Performance Optimization
```bash
# AI-assisted performance optimization
overseer --feature performance_optimizer --action optimize

# ML-powered analytics
overseer --feature machine_learning_integration --action analyze_patterns

# Predictive maintenance
overseer --feature predictive_analytics --action forecast
```

### Tool Recommendations
```bash
# Get AI-powered tool recommendations
overseer --feature enhanced_tool_recommender --prompt "I need monitoring tools"

# Context-aware suggestions
overseer --feature llm_advisor --prompt "My system is slow"
```

---

## 🛡️ Security Features

### Multi-layered Protection
- **Command Sandbox**: Secure execution environment
- **Permission Validation**: Granular access control
- **Risk Assessment**: AI-powered command risk analysis
- **Audit Trail**: Comprehensive security logging

### Data Protection
- **Local Processing**: All AI inference runs on-device
- **Data Encryption**: Sensitive data encrypted at rest
- **Privacy Controls**: Granular data collection preferences
- **Secure Communication**: Encrypted API and WebSocket communication

---

## 🎨 Desktop Application

The desktop app provides a modern, intuitive interface with:
- **Real-time Dashboard**: Live system monitoring with AI insights
- **Chat Interface**: Natural language interaction with AI assistant
- **Task Management**: AI-powered task creation and scheduling
- **Settings Management**: Comprehensive configuration interface

### Desktop App Features
- **Cross-platform**: Windows, macOS, and Linux support
- **Real-time Updates**: WebSocket-based live data streaming
- **Modern UI**: React-based responsive interface
- **Accessibility**: Full keyboard navigation and screen reader support

---

## 🧪 Training & Continuous Learning

### Model Training
```bash
# Train on various platforms
cd training
./setup.sh

# Standard training
python scripts/main_training.py

# Monitor training progress
python scripts/memory_monitor.py
```

### Continuous Learning
- **User Interaction Data**: Learning from user behavior patterns
- **Performance Feedback**: Model improvement based on system performance
- **Adaptive Responses**: Personalized AI responses based on user preferences
- **Knowledge Updates**: Continuous knowledge base updates

---

## 📚 Documentation

- **[CLI Documentation](backend/cli/README.md)** - Complete CLI feature documentation
- **[Backend API Reference](backend/api/README.md)** - RESTful API endpoints and integration guide
- **[Desktop App Guide](desktop-app/README.md)** - Desktop application documentation
- **[Training Guide](training/README.md)** - AI model training and continuous learning
- **[Backend Service](backend/README.md)** - Core backend architecture and features
- **[Comprehensive Summary](backend/COMPREHENSIVE_SUMMARY.md)** - Complete system overview
- **[Features Documentation](backend/cli/FEATURES_DOCUMENTATION.md)** - Complete feature analysis
- **[ML Integration Guide](backend/cli/features/ai_core/ML_INTEGRATION_GUIDE.md)** - Machine learning integration

---

## 🔧 Configuration

### Environment Variables
```bash
export OVERSEER_LLM_MODEL=gemma3n
export OVERSEER_API_KEY=your_api_key
export OVERSEER_MODE=local
```

### Settings Menu
```bash
# Access interactive settings
overseer --settings

# Configure specific features
overseer --settings --feature llm_advisor
```

---

## 🚀 Performance

### Response Times
- **Simple Commands**: < 100ms
- **Complex Analysis**: < 500ms
- **AI Processing**: < 2s for complex queries
- **File Operations**: < 200ms for indexed searches

### Resource Usage
- **Memory**: < 1GB baseline, < 2GB with AI model
- **CPU**: < 10% for monitoring, < 30% for AI processing
- **Storage**: < 100MB for core system, < 1GB with full features

---

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Add LLM integration**: Ensure new features have appropriate AI integration
4. **Add tests**: Include comprehensive test coverage
5. **Update documentation**: Keep READMEs and docs current
6. **Submit a pull request**: With detailed description of changes

### Development Guidelines
- **LLM Integration**: All new features should consider AI integration
- **Testing**: Comprehensive test coverage required
- **Documentation**: Detailed documentation for all features
- **Security**: Security review for all system-level features

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Gemma 3n**: Google's open-source language model
- **Ollama**: Local AI model serving
- **FastAPI**: High-performance async API framework
- **React/Electron**: Modern desktop application framework

---

**Overseer** - Intelligent system management powered by AI 🤖
