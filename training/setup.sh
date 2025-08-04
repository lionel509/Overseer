#!/bin/bash

# Overseer Training Environment Setup
# This script sets up the training environment with the new organized structure

set -e

echo "🚀 Setting up Overseer Training Environment..."

# Check if we're in the training directory
if [ ! -f "README.md" ] || [ ! -d "scripts" ]; then
    echo "❌ Error: Please run this script from the training directory"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data models logs

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x scripts/*.sh

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r configs/requirements.txt

# Setup training environment
echo "⚙️ Setting up training environment..."
if [ -f "scripts/setup_training.sh" ]; then
    ./scripts/setup_training.sh
fi

# Create log directory
echo "📝 Setting up logging..."
mkdir -p logs
touch logs/training.log

echo "✅ Training environment setup completed!"
echo ""
echo "🎯 Next steps:"
echo "1. Review configuration: configs/training_config.py"
echo "2. Start training: python scripts/main_training.py"
echo "3. Monitor progress: tail -f logs/training.log"
echo ""
echo "📚 Documentation:"
echo "- Main guide: README.md"
echo "- Training flags: docs/README_training_flags.md"
echo "- Resource-efficient: docs/README_resource_efficient.md"
echo "- Safety features: docs/README_safeguards.md" 