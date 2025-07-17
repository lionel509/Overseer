# Core Engine
## Central AI and System Processing Components

### 🎯 **Purpose**
The core directory contains the fundamental building blocks of Overseer's intelligence:
- **AI Engine**: Gemma 3n model integration and conversation management
- **System Integration**: Real-time system monitoring and analysis
- **Natural Language Processing**: Command interpretation and response generation
- **File Intelligence**: Content analysis and semantic understanding

### 📁 **Components**

#### **gemma_engine.py**
- **Gemma 3n Integration**: Direct integration with local Gemma 3n model via Ollama
- **Model Management**: Load, optimize, and manage AI model lifecycle
- **Inference Pipeline**: Process natural language queries and generate responses
- **Performance Optimization**: Memory management and response caching

#### **conversation_manager.py**
- **Context Management**: Maintain conversation history and system context
- **Memory System**: Remember user preferences and past interactions
- **Session Handling**: Manage multiple conversation threads
- **Personalization**: Adapt responses based on user behavior

#### **system_monitor.py**
- **Real-time Monitoring**: CPU, memory, disk, and network monitoring
- **Process Management**: Track running processes and system resources
- **Performance Analysis**: Identify bottlenecks and optimization opportunities
- **Health Diagnostics**: System health checks and alerts

#### **file_indexer.py**
- **Content Analysis**: Index and analyze file contents using AI
- **Semantic Search**: Enable natural language file searching
- **Metadata Extraction**: Extract and store file metadata
- **Classification**: Automatically categorize files by content and purpose

#### **command_parser.py**
- **Natural Language Processing**: Parse user commands and extract intent
- **Command Translation**: Convert natural language to system commands
- **Context Understanding**: Understand system state and user context
- **Error Handling**: Graceful handling of ambiguous or invalid commands

### 🔧 **Key Technologies**
- **Ollama**: Local AI model serving and optimization
- **psutil**: System monitoring and process management
- **SQLite**: Local data storage for indexing and caching
- **asyncio**: Asynchronous processing for responsiveness
- **watchdog**: File system monitoring and change detection

### 🚀 **Core Features**
- **Local AI Processing**: All inference happens on-device for privacy
- **Real-time Monitoring**: Instant system status and performance metrics
- **Intelligent Indexing**: Smart file organization and search capabilities
- **Context Awareness**: Understanding of system state and user intent
- **Performance Optimization**: Efficient resource usage and caching

### 📡 **Integration Points**
- **Modules**: Provides AI and system services to feature modules
- **Interfaces**: Serves data to API and WebSocket endpoints
- **Desktop App**: Powers the frontend through backend services
- **Knowledge Base**: Integrates with tools and system knowledge

### 🛡️ **Security & Privacy**
- **Local Processing**: No data leaves the device
- **Encrypted Storage**: Sensitive data encrypted at rest
- **Permission Management**: Controlled system access
- **Audit Logging**: Track all system operations

### 🎯 **Development Guidelines**
- **Async/Await**: Use asynchronous programming for responsiveness
- **Error Handling**: Comprehensive error handling and logging
- **Testing**: Unit tests for all core components
- **Documentation**: Clear docstrings and code comments
- **Performance**: Optimize for speed and memory efficiency

### 📊 **Performance Targets**
- **AI Response Time**: < 200ms for common queries
- **System Monitoring**: < 1% CPU usage for continuous monitoring
- **File Indexing**: < 5 seconds for average directory
- **Memory Usage**: < 512MB for core components
- **Startup Time**: < 3 seconds for full initialization

The core engine is the intelligent heart of Overseer, providing the foundational AI and system integration capabilities that power all other features.
