# Overseer CLI

A powerful command-line interface for file management, system automation, and AI-assisted organization.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run in chat mode
python -m overseer_cli

# Run with specific command
python -m overseer_cli --prompt "organize my downloads"

# Run in testing mode
python -m overseer_cli --mode testing

# Access settings menu
python -m overseer_cli --settings
```

## 📚 Documentation

- **[Master Guide](docs/MASTER_GUIDE.md)** - Complete feature documentation
- **[Settings Guide](docs/SETTINGS_GUIDE.md)** - Comprehensive configuration options
- **[Security Features](security/README.md)** - Security and sandbox documentation

## 🎯 Key Features

### 🤖 AI-Powered Organization
- **Auto-organize**: Intelligent file categorization and sorting
- **LLM Integration**: Gemini API or local model support
- **Smart Suggestions**: Context-aware file management recommendations

### 🔒 Security & Safety
- **Command Sandbox**: Multi-layered command execution protection
- **Secure Config**: Automatic `chmod 600` for sensitive files
- **Permission Management**: Granular control over system access

### 📁 File Management
- **Fast Search**: Indexed file search with fuzzy matching
- **Batch Operations**: Efficient multi-file processing
- **Backup Protection**: Automatic backups before file moves

### ⚙️ Flexible Configuration
- **50+ Settings**: Comprehensive configuration options
- **Interactive Editor**: User-friendly settings management
- **Profile Support**: Different settings for different use cases

## 🏗️ Architecture

```
backend/cli/
├── core/           # Core logic and processing
├── features/       # Feature implementations
├── security/       # Security and sandbox systems
├── inference/      # LLM integration
├── db/            # Database and indexing
├── docs/          # Documentation
├── tests/         # Test suites
└── utils/         # Utilities and helpers
```

## 🧪 Testing

```bash
# Run comprehensive tests
python tests/test_all_features.py

# Test specific features
python -m overseer_cli --mode testing
```

## 🔧 Configuration

The system uses a comprehensive settings system with **50+ configuration options** across 10 categories:

- **LLM Configuration**: Model selection, API keys, parameters
- **Security Settings**: Sandbox modes, timeouts, permissions
- **File Management**: Indexing, organization, backup options
- **Performance**: Threading, caching, memory limits
- **UI/UX**: Display options, notifications, interaction modes

See **[Settings Guide](docs/SETTINGS_GUIDE.md)** for complete documentation.

## 🛡️ Security Features

- **Multi-layered Sandbox**: DRY_RUN → SIMULATION → ISOLATED → VALIDATION
- **Automatic Permissions**: `chmod 600` for sensitive config files
- **Command Validation**: Risk assessment before execution
- **Timeout Protection**: Prevents hanging commands
- **Change Tracking**: Monitors file system modifications

## 📈 Performance

- **Indexed Search**: Fast file location with metadata
- **Batch Processing**: Efficient multi-file operations
- **Caching System**: Reduces redundant operations
- **Threading Support**: Configurable concurrent processing
- **Memory Management**: Configurable limits and cleanup

## 🎨 User Experience

- **Interactive Prompts**: User-friendly confirmation dialogs
- **Progress Tracking**: Visual feedback for long operations
- **Error Handling**: Graceful failure with recovery options
- **Auto-completion**: Command and path suggestions
- **Color Output**: Enhanced readability with syntax highlighting

## 🔄 Plan-Based Execution

Complex tasks are broken into steps with individual confirmation:

```
User: "organize my entire system"
Overseer: PLAN: audit_config | auto_organize folders=~/Downloads,~/Documents | fix_config_security
```

## 📊 Monitoring & Logging

- **Audit Logs**: Track all system changes
- **Performance Metrics**: Monitor operation efficiency
- **Error Reporting**: Detailed failure analysis
- **Security Events**: Log suspicious activities

## 🤝 Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Ensure security compliance

## 📄 License

See [LICENSE](../LICENSE) for details.

---

**Overseer CLI** - Intelligent file management with AI assistance 