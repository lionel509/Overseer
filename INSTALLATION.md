# Overseer CLI Installation Guide

## 🚀 Quick Installation

### Option 1: One-Line Installation (Recommended)
```bash
# Clone and install in one go
git clone https://github.com/your-username/overseer.git
cd Overseer
pip install -e ./backend/
```

### Option 2: Using the Installation Script
```bash
# Clone the repository
git clone https://github.com/your-username/overseer.git
cd Overseer

# Run the installation script
./install.sh
```

### Option 3: Manual Installation
```bash
# Clone the repository
git clone https://github.com/your-username/overseer.git
cd Overseer

# Install the CLI package
pip install -e ./backend/

# Install desktop app dependencies (optional)
cd desktop-app && npm install
```

## ✅ Verification

After installation, verify it works:
```bash
overseer --help
```

You should see:
```
usage: overseer [-h] [--version] [--stats] [--ai]

Overseer Optimized CLI

options:
  -h, --help  show this help message and exit
  --version   Show version
  --stats     Show performance stats
  --fast      Force fast mode only
  --ai        Force AI mode
```

## 🎯 Usage

### Interactive Mode
```bash
overseer
```

### Command Mode
```bash
overseer --ai "install nvitop"
```

### Help
```bash
overseer --help
```

## 🔧 Troubleshooting

### If you get "command not found"
Make sure you're in the correct conda environment:
```bash
conda activate overseer
```

### If installation fails
Try installing with pip3:
```bash
pip3 install -e ./backend/
```

### If you get permission errors
Use the `--user` flag:
```bash
pip install --user -e ./backend/
```

## 📦 What Gets Installed

The installation includes:
- ✅ Overseer CLI command (`overseer`)
- ✅ All required dependencies
- ✅ AI model integration
- ✅ System monitoring tools
- ✅ File organization features

## 🎉 Success!

Once installed, you can:
- Use `overseer` command from anywhere
- Run interactive AI chat mode
- Execute system commands with AI assistance
- Monitor system performance
- Organize files intelligently

The package is installed in editable mode, so any changes to the code will be immediately available without reinstalling. 