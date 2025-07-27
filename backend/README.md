# Backend Service
## Python FastAPI Backend for Overseer

### 🎯 **Purpose**
The backend service is the core engine of Overseer, responsible for:
- **AI Processing**: Gemma 3n model integration and inference
- **System Integration**: Direct access to system resources and processes
- **Data Management**: File indexing, system monitoring, and knowledge base
- **API Services**: RESTful endpoints and WebSocket communication for the desktop app

### 🏗️ **Architecture**
```
backend/
├── core/           # Core AI and system functionality
├── modules/        # Feature-specific modules
├── interfaces/     # API and communication layers
├── knowledge/      # Knowledge base and data stores
├── main.py         # FastAPI application entry point
├── requirements.txt # Python dependencies
└── config.py       # Configuration management
```

### 🚀 **Key Features**
- **Gemma 3n Integration**: Local AI model inference with Ollama
- **System Monitoring**: Real-time CPU, memory, disk, and process tracking
- **File Intelligence**: Content analysis, semantic search, and organization
- **Command Processing**: Natural language to system command translation
- **Security Scanning**: Vulnerability detection and system health checks

### 🔧 **Technology Stack**
- **Framework**: FastAPI for high-performance async API
- **AI Integration**: Ollama for local Gemma 3n model serving
- **System APIs**: psutil for system monitoring and control
- **Database**: SQLite for local data storage
- **WebSocket**: Real-time communication with desktop app

### 📡 **Communication**
- **REST API**: Standard HTTP endpoints for commands and queries
- **WebSocket**: Real-time system monitoring and status updates
- **IPC Bridge**: Secure communication with Electron desktop app
- **Message Queue**: Asynchronous task processing

### 🛡️ **Security**
- **Local Processing**: All AI inference runs on-device
- **Data Encryption**: Sensitive data encrypted at rest
- **Permission Management**: Granular system access control
- **Audit Logging**: Track all system modifications

### 🎯 **Development**
- **Environment**: Python 3.9+ with virtual environment
- **Dependencies**: See requirements.txt for full list
- **Testing**: pytest for unit and integration testing
- **Documentation**: Auto-generated OpenAPI/Swagger docs

### 🚀 **Getting Started**
```bash
# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the development server
python main.py
```

### 📊 **Performance Targets**
- **Response Time**: < 200ms for common queries
- **Memory Usage**: < 1GB baseline, < 2GB with AI model
- **Concurrent Users**: Support for multiple desktop app instances
- **Uptime**: 99.9% availability for system monitoring

The backend service is designed to be the intelligent brain of Overseer, providing powerful AI capabilities while maintaining privacy and performance through local processing.

## Overseer CLI Tool

The Overseer CLI tool provides a command-line interface to interact with the Overseer system assistant. It supports two modes:

- **Local Mode**: Uses a local LLM (e.g., Gemma 3n via Hugging Face Transformers) for inference.
- **Gemini API Mode**: Uses the Google Gemini API for inference (requires API key).

### Usage

```bash
# Local mode (requires local model download)
python -m backend.cli.overseer_cli --mode local --prompt "Find my Python files about machine learning"

# Gemini API mode (requires API key)
python -m backend.cli.overseer_cli --mode gemini --prompt "I need nvidia monitoring tools"
```

You can also run in interactive mode (REPL) by omitting the --prompt argument.

See `backend/cli/README.md` for more details.

# Quick CLI Install

1. Clone the repo and enter the backend directory:
   ```bash
   git clone <repo-url>
   cd Overseer/backend
   ```
2. (Optional) Activate your conda environment:
   ```bash
   conda activate <your-env>
   ```
3. Run the install script:
   ```bash
   bash install_cli.sh
   ```
   Or manually:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```
4. Run the CLI from anywhere:
   ```bash
   overseer --mode local --prompt "Find my Python files about machine learning"
   ```

See backend/cli/README.md for more details.
