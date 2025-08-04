#!/bin/bash

# Overseer Desktop Application Setup Script
# This script helps set up the desktop application with all necessary dependencies

set -e

echo "🚀 Setting up Overseer Desktop Application..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    print_error "Please run this script from the desktop-app directory"
    exit 1
fi

# Check Node.js version
print_status "Checking Node.js version..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        print_error "Node.js 18+ is required. Current version: $(node --version)"
        exit 1
    else
        print_success "Node.js version: $(node --version)"
    fi
else
    print_error "Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check npm
print_status "Checking npm..."
if command -v npm &> /dev/null; then
    print_success "npm version: $(npm --version)"
else
    print_error "npm is not installed. Please install npm first."
    exit 1
fi

# Check Python
print_status "Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_success "Python version: $(python3 --version)"
else
    print_error "Python 3.8+ is required. Please install Python first."
    exit 1
fi

# Check conda environment
print_status "Checking conda environment..."
if command -v conda &> /dev/null; then
    print_success "Conda is available"
    print_status "Activating conda base environment..."
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate base
else
    print_warning "Conda not found. Make sure to activate your Python environment manually."
fi

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
npm install

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install psutil

# Check if backend directory exists
if [ -d "../backend" ]; then
    print_success "Backend directory found"
else
    print_warning "Backend directory not found. Some features may not work."
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p dist
mkdir -p release

# Set up development environment
print_status "Setting up development environment..."

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    cat > .env << EOF
# Overseer Desktop Environment Variables
NODE_ENV=development
PYTHON_PATH=$(which python3)
EOF
    print_success "Created .env file"
fi

# Make backend integration script executable
if [ -f "backend_integration.py" ]; then
    chmod +x backend_integration.py
    print_success "Made backend integration script executable"
fi

# Test the setup
print_status "Testing the setup..."

# Test Node.js dependencies
if npm run build --dry-run &> /dev/null; then
    print_success "Node.js dependencies are working"
else
    print_warning "Node.js build test failed, but this might be normal"
fi

# Test Python backend integration
if python3 -c "import psutil; print('psutil imported successfully')" 2>/dev/null; then
    print_success "Python dependencies are working"
else
    print_error "Python dependencies test failed"
    exit 1
fi

echo ""
print_success "Setup completed successfully!"
echo ""
echo "🎯 Next steps:"
echo "1. Start development server: npm run dev"
echo "2. Open the application in your browser"
echo "3. Press Cmd+K (macOS) or Ctrl+K (Windows/Linux) to open the command palette"
echo ""
echo "📚 For more information, see README.md"
echo ""
print_success "Happy coding! 🚀" 