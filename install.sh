#!/bin/bash

# Overseer CLI Installation Script
# This script installs the Overseer CLI package

set -e

echo "🚀 Installing Overseer CLI..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Please run this script from the project root directory."
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "❌ Error: pip is not installed or not in PATH"
    echo "Please install pip first: https://pip.pypa.io/en/stable/installation/"
    exit 1
fi

echo "📦 Installing Overseer CLI package..."
python3 -m pip install -e ./backend/

echo "✅ Installation completed successfully!"
echo ""
echo "🎉 You can now use the overseer command:"
echo "   overseer --help"
echo ""
echo "💡 For interactive mode, simply run:"
echo "   overseer"
echo ""
echo "📚 For more information, see the README.md file" 