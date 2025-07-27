# Overseer CLI Tool

The CLI codebase is organized for clarity and modularity:

## Structure

- `core/` - Core logic and orchestration
- `features/` - Individual assistant features (tool recommendation, command correction, file search)
- `db/` - Encrypted database modules (tool DB, filesystem DB, etc.)
- `inference/` - Inference backend stubs (local, Gemini)
- `keygen/` - Key generation utility
- `overseer_cli.py` - Main CLI entry point

## Usage

- Run the CLI: `overseer --mode local --prompt "Find my Python files about machine learning"`
- Generate a key: `python -m keygen.keygen`
- See each folder for feature-specific tests and code.

See the main project README for install and setup instructions. 