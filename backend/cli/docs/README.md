# Overseer CLI Documentation

The CLI codebase is organized for clarity, modularity, and comprehensive AI integration:

## 🏗️ Structure

- `core/` - Core AI logic and LLM processing
- `features/` - AI-powered assistant features (LLM advisor, tool recommendation, command correction, file search)
- `db/` - AI-enhanced database modules (tool DB, filesystem DB, ML analytics)
- `inference/` - Advanced LLM integration (local models, Gemini API, hybrid mode)
- `security/` - AI-powered security and sandbox systems
- `overseer_cli.py` - Main CLI entry point with comprehensive AI integration

## 🧠 AI Integration

### LLM Models Supported
- **Local Models**: Gemma 3n via Ollama (recommended for privacy)
- **API Models**: Gemini API for enhanced capabilities
- **Hybrid Mode**: Combine multiple models for optimal performance
- **Custom Models**: Support for fine-tuned models

### AI Features
- **LLM Advisor**: AI-powered system problem diagnosis and solutions
- **Enhanced Tool Recommender**: Context-aware tool suggestions using LLM analysis
- **Machine Learning Integration**: ML-powered system analysis with LLM integration
- **Predictive Analytics**: AI-driven performance prediction and trend analysis

## 🚀 Usage

### Basic AI Usage
```bash
# Run with local LLM
overseer --mode local --prompt "Find my Python files about machine learning"

# Run with Gemini API
overseer --mode gemini --prompt "I need nvidia monitoring tools"

# Interactive AI chat mode
overseer

# Test AI integration
overseer --test-llm
```

### AI Feature Usage
```bash
# Use LLM advisor for system problems
overseer --feature llm_advisor --prompt "My system is slow"

# Get AI-powered tool recommendations
overseer --feature enhanced_tool_recommender --prompt "I need monitoring tools"

# Run ML-powered analytics
overseer --feature machine_learning_integration --action analyze_patterns
```

## 📚 Documentation

- **[Master Guide](MASTER_GUIDE.md)** - Complete AI feature documentation
- **[Settings Guide](SETTINGS_GUIDE.md)** - Comprehensive LLM configuration options
- **[Features Overview](../features/README.md)** - Complete feature categorization and LLM integration

## 🔧 Configuration

### AI Model Settings
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

## 🧪 Testing

### AI Feature Testing
```bash
# Test specific AI features
python -m overseer_cli --mode testing

# Test LLM integration
python -m overseer_cli --test-llm

# Test AI model performance
python -m overseer_cli --test-ai-performance
```

## 📊 Performance

### AI Response Times
- **Simple Commands**: < 100ms
- **Complex Analysis**: < 500ms
- **AI Processing**: < 2s for complex queries
- **File Operations**: < 200ms for indexed searches

### AI Resource Usage
- **Memory**: < 1GB baseline, < 2GB with AI model
- **CPU**: < 10% for monitoring, < 30% for AI processing
- **Storage**: < 100MB for core system, < 1GB with full features

## 🤝 Contributing

When adding new AI features:
1. **LLM Integration**: Ensure proper AI model integration
2. **Testing**: Add comprehensive AI feature tests
3. **Documentation**: Update AI documentation and examples
4. **Security**: Include AI-powered security validation
5. **Performance**: Optimize AI processing for speed and efficiency

See the main project README for install and setup instructions. 