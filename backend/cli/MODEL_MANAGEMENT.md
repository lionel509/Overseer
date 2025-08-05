# AI Model Management System

This system allows you to download, install, and manage AI models for Overseer without bundling them with the repository.

## Features

- 🤖 **Multiple Model Support**: Gemma 3n models in different sizes
- 📥 **Automatic Downloads**: Download models from Hugging Face during installation
- 💾 **Disk Space Management**: Check available space before downloads
- ⚙️ **Dependency Management**: Automatically install required packages
- 🔧 **CLI Interface**: Easy command-line model management
- 📊 **Model Verification**: Verify model integrity after download

## Quick Start

### During Installation

When you run the main installer, you'll be prompted to select which AI models to download:

```bash
python install.py
# Choose option 2 or 3 to include AI models
```

### Manual Model Management

```bash
# List available models
python -m backend.cli.model_manager list

# Interactive setup
python -m backend.cli.model_manager setup

# Install specific model
python -m backend.cli.model_cli install gemma-3n-2b

# Remove model
python -m backend.cli.model_cli remove gemma-3n-2b

# Verify model
python -m backend.cli.model_cli verify gemma-3n-2b
```

## Available Models

| Model | Size | Description | Recommended |
|-------|------|-------------|-------------|
| gemma-3n-2b | 2.1GB | Lightweight model for basic AI tasks | ✅ Yes |
| gemma-3n-9b | 8.7GB | Full-featured model for advanced tasks | ⚪ No |
| gemma-3n-27b | 25.2GB | Enterprise-grade model for complex tasks | ⚪ No |

## Model Storage

Models are stored in:
```
~/.overseer/models/
├── gemma-3n-2b/
│   ├── config.json
│   ├── pytorch_model.bin
│   ├── tokenizer.json
│   └── ...
└── model_config.json
```

## Configuration

The system automatically configures Overseer to use downloaded models. Configuration is stored in:
```
~/.overseer/model_config.json
```

## Requirements

- Python 3.8+
- Git (for Hugging Face downloads)
- At least 5GB free disk space (for smallest model)
- Internet connection for downloads

## Dependencies

Core dependencies are automatically installed:
- `transformers>=4.35.0`
- `torch>=2.0.0` 
- `huggingface-hub>=0.17.0`
- `requests>=2.31.0`
- `rich>=13.0.0`

## Troubleshooting

### Model Download Issues

1. **Git not found**: Install git and git-lfs
   ```bash
   # macOS
   brew install git git-lfs
   
   # Linux
   sudo apt-get install git git-lfs
   ```

2. **Authentication required**: Some models may require Hugging Face authentication
   ```bash
   huggingface-cli login
   ```

3. **Disk space issues**: Clear space or choose smaller model
   ```bash
   python -m backend.cli.model_cli list  # Check sizes
   ```

### Model Loading Issues

1. **Model not found**: Verify installation
   ```bash
   python -m backend.cli.model_cli verify gemma-3n-2b
   ```

2. **Out of memory**: Try smaller model or use CPU-only mode
   ```bash
   # Edit config to use CPU
   # Set CUDA_VISIBLE_DEVICES="" environment variable
   ```

3. **Dependencies missing**: Reinstall model dependencies
   ```bash
   pip install -r backend/cli/model_requirements.txt
   ```

## Advanced Usage

### Custom Model Directory

```bash
python -m backend.cli.model_manager --models-dir /custom/path setup
```

### Environment Variables

```bash
export OVERSEER_MODELS_DIR="/custom/models/path"
export OVERSEER_LLM_MODEL="gemma-3n-2b"
```

### Integration with Overseer

```python
from backend.cli.inference.inference_local import LocalLLM

# The system automatically uses downloaded models
llm = LocalLLM()
response = llm.run("Hello, how can I help you?")
```

## Benefits Over Bundled Models

1. **Smaller Repository**: Reduces repo size from ~10GB to ~100MB
2. **User Choice**: Users select which models they want
3. **Up-to-date Models**: Always download latest model versions
4. **Flexible Storage**: Models stored in user directory, not repo
5. **Easier Updates**: Update models independently of code
6. **Multiple Versions**: Support different model sizes/types

## Development

### Adding New Models

1. Add model configuration to `model_manager.py`:
   ```python
   "new-model-id": {
       "name": "New Model Name",
       "description": "Model description",
       "size": "X.XGB",
       "url": "https://huggingface.co/model/path",
       "files": ["config.json", "pytorch_model.bin", ...],
       "recommended": False,
       "requirements": ["transformers>=4.35.0"]
   }
   ```

2. Test the new model:
   ```bash
   python -m backend.cli.model_cli install new-model-id
   python -m backend.cli.model_cli verify new-model-id
   ```

### Model Manager API

```python
from backend.cli.model_manager import ModelManager

manager = ModelManager()

# Check available models
print(manager.available_models)

# Install model programmatically
success = manager.download_models(["gemma-3n-2b"])

# List installed models
installed = manager.list_installed_models()
```

This system provides a robust, user-friendly way to manage AI models without bloating the repository size.
