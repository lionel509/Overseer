# Overseer CLI

A powerful AI-driven command-line interface for intelligent system management, file organization, and automated system administration with comprehensive LLM integration.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run in interactive chat mode with LLM
python -m overseer_cli

# Run with specific AI-powered command
python -m overseer_cli --prompt "organize my downloads with AI"

# Run in testing mode
python -m overseer_cli --mode testing

# Access AI settings menu
python -m overseer_cli --settings
```

## 📚 Documentation

- **[Master Guide](docs/MASTER_GUIDE.md)** - Complete AI feature documentation
- **[Settings Guide](docs/SETTINGS_GUIDE.md)** - Comprehensive LLM configuration options
- **[Security Features](security/README.md)** - Security and sandbox documentation
- **[Features Overview](features/README.md)** - Complete feature categorization and LLM integration

## 🧠 Key AI Features

### 🤖 LLM-Integrated Core Features
- **LLM Advisor**: AI-powered system problem diagnosis and solutions
- **Enhanced Tool Recommender**: Context-aware tool suggestions using LLM analysis
- **Machine Learning Integration**: ML-powered system analysis with LLM integration
- **Predictive Analytics**: AI-driven performance prediction and trend analysis

### 📊 AI-Powered Monitoring
- **Unified System Monitor**: Comprehensive system monitoring with LLM insights
- **Advanced Analytics**: Advanced analytics with AI-driven pattern recognition
- **Intelligent Alert Manager**: LLM-based alert severity assessment
- **Custom Alert Rules**: AI-assisted custom alert rule creation

### 🔧 AI-Enhanced Organization
- **Auto-organize**: AI-powered file categorization and intelligent sorting
- **Smart File Search**: Semantic file search with content understanding
- **Intelligent Folder Sorting**: LLM-based folder organization
- **Filesystem Scanner**: Smart filesystem scanning with content analysis

### ⚡ AI-Assisted Performance
- **Performance Optimizer**: AI-assisted system performance optimization
- **Advanced Process Manager**: Intelligent process management with AI insights
- **System Monitor**: Enhanced monitoring with AI recommendations

## 🏗️ Architecture

```
backend/cli/
├── core/           # Core AI logic and LLM processing
├── features/       # AI-powered feature implementations
├── security/       # Security and sandbox systems
├── inference/      # LLM integration (local, Gemini API)
├── db/            # Database and AI knowledge stores
├── docs/          # Comprehensive documentation
├── tests/         # Test suites for all AI features
└── utils/         # Utilities and AI helpers
```

## 🧪 Testing

```bash
# Run comprehensive AI feature tests
python tests/test_all_features.py

# Test specific AI features
python -m overseer_cli --mode testing

# Test LLM integration
python -m overseer_cli --test-llm
```

## 🔧 AI Configuration

The system uses a comprehensive AI settings system with **50+ configuration options** across 10 categories:

- **LLM Configuration**: Model selection, API keys, parameters, context management
- **AI Features**: Machine learning, predictive analytics, pattern recognition
- **Security Settings**: AI-powered risk assessment, sandbox modes, timeouts
- **File Management**: AI-powered indexing, organization, content analysis
- **Performance**: AI optimization, threading, caching, memory limits
- **UI/UX**: AI-enhanced display options, notifications, interaction modes

See **[Settings Guide](docs/SETTINGS_GUIDE.md)** for complete AI configuration documentation.

## 🛡️ AI-Enhanced Security Features

- **AI Risk Assessment**: LLM-powered command risk analysis before execution
- **Multi-layered Sandbox**: DRY_RUN → SIMULATION → ISOLATED → VALIDATION
- **Intelligent Permissions**: AI-assisted permission management and validation
- **Timeout Protection**: AI-monitored command execution with automatic termination
- **Change Tracking**: AI-powered monitoring of file system modifications

## 📈 AI Performance

- **Indexed Search**: AI-enhanced file location with semantic understanding
- **Batch Processing**: AI-optimized multi-file operations
- **Caching System**: AI-powered caching reduces redundant operations
- **Threading Support**: Configurable concurrent AI processing
- **Memory Management**: AI-optimized memory limits and cleanup

## 🎨 AI-Enhanced User Experience

- **Intelligent Prompts**: AI-powered user-friendly confirmation dialogs
- **Progress Tracking**: AI-enhanced visual feedback for long operations
- **Error Handling**: AI-assisted graceful failure with recovery options
- **Auto-completion**: AI-powered command and path suggestions
- **Color Output**: AI-enhanced readability with syntax highlighting

## 🔄 AI Plan-Based Execution

Complex tasks are broken into AI-optimized steps with individual confirmation:

```
User: "organize my entire system with AI"
Overseer: AI_PLAN: audit_config | ai_auto_organize folders=~/Downloads,~/Documents | ai_optimize_performance
```

## 📊 AI Monitoring & Logging

- **AI Audit Logs**: Track all AI-powered system changes
- **Performance Metrics**: AI-monitored operation efficiency
- **Error Reporting**: AI-enhanced failure analysis
- **Security Events**: AI-powered suspicious activity detection

## 🧠 LLM Integration Examples

### Local LLM (Gemma 3n via Ollama)
```bash
# Use local AI model for system analysis
overseer --mode local --prompt "analyze my system performance with AI"

# Get AI-powered tool recommendations
overseer --mode local --prompt "I need monitoring tools for my GPU"

# AI-assisted file organization
overseer --mode local --prompt "organize my downloads intelligently"
```

### Gemini API Integration
```bash
# Use Gemini API for enhanced capabilities
overseer --mode gemini --prompt "diagnose my system issues"

# AI-powered performance optimization
overseer --mode gemini --prompt "optimize my system performance"

# Intelligent file search
overseer --mode gemini --prompt "find my machine learning projects"
```

### Hybrid AI Mode
```bash
# Combine multiple AI models for optimal results
overseer --mode hybrid --prompt "comprehensive system analysis"

# AI-enhanced monitoring dashboard
overseer --mode hybrid --feature monitoring_dashboard
```

## 🔧 AI Feature Configuration

### LLM Model Settings
```bash
# Configure local model
overseer --settings --llm-model gemma3n

# Configure API model
overseer --settings --llm-api-key YOUR_API_KEY

# Configure hybrid mode
overseer --settings --llm-hybrid true
```

### AI Feature Settings
```bash
# Enable machine learning features
overseer --settings --ml-enabled true

# Configure predictive analytics
overseer --settings --predictive-analytics true

# Enable AI-powered monitoring
overseer --settings --ai-monitoring true
```

## 📚 AI Documentation

### Feature-Specific Documentation
- **[LLM Advisor](features/llm_advisor.py)** - AI-powered system advisor
- **[Enhanced Tool Recommender](features/enhanced_tool_recommender.py)** - AI tool recommendations
- **[Machine Learning Integration](features/machine_learning_integration.py)** - ML-powered analytics
- **[Predictive Analytics](features/predictive_analytics.py)** - AI-driven predictions

### AI Integration Guides
- **[Local LLM Setup](docs/LOCAL_LLM_SETUP.md)** - Ollama and local model configuration
- **[API Integration](docs/API_INTEGRATION.md)** - Gemini API and external AI services
- **[Hybrid Mode](docs/HYBRID_MODE.md)** - Multi-model AI integration
- **[AI Training](docs/AI_TRAINING.md)** - Custom model training and fine-tuning

## 🤝 Contributing

When adding new AI features:
1. **LLM Integration**: Ensure proper AI model integration
2. **Testing**: Add comprehensive AI feature tests
3. **Documentation**: Update AI documentation and examples
4. **Security**: Include AI-powered security validation
5. **Performance**: Optimize AI processing for speed and efficiency

## 📄 License

See [LICENSE](../LICENSE) for details.

---

**Overseer CLI** - Intelligent system management powered by AI 🤖 