# Overseer Desktop Application

A modern, AI-powered desktop application built with Electron and React, providing an intuitive interface for the Overseer AI system assistant.

## 🚀 Features

### Core Features
- **Command Palette**: Press `Cmd+K` (macOS) or `Ctrl+K` (Windows/Linux) to open the command palette
- **Python Backend Integration**: Seamless communication with the Overseer Python backend
- **System Monitoring**: Real-time system metrics and monitoring
- **File Management**: Advanced file search and organization
- **Process Management**: View and manage running processes
- **Network Monitoring**: Network status and connectivity information

### IPC Communication
- **Secure IPC**: Context-isolated communication between Electron and Python
- **Real-time Updates**: Live system metrics and backend output
- **Error Handling**: Comprehensive error handling and recovery
- **Process Management**: Start/stop Python backend from the UI

### UI/UX Features
- **Modern Design**: Clean, responsive interface with Tailwind CSS
- **Dark/Light Theme**: Theme switching support
- **Responsive Layout**: Adapts to different screen sizes
- **Keyboard Shortcuts**: Full keyboard navigation support
- **Accessibility**: ARIA labels and keyboard navigation

## 🛠️ Installation

### Prerequisites
- Node.js 18+ 
- Python 3.8+
- npm or yarn

### Setup

1. **Install Dependencies**
   ```bash
   cd desktop-app
   npm install
   ```

2. **Install Python Dependencies**
   ```bash
   # Activate your conda environment first
   conda activate base
   
   # Install Python dependencies
   pip install psutil
   ```

3. **Development Mode**
   ```bash
   npm run dev
   ```

4. **Build for Production**
   ```bash
   npm run build
   npm run dist
   ```

## 🏗️ Architecture

### Project Structure
```
desktop-app/
├── electron/              # Electron main process
│   ├── main.ts           # Main process entry point
│   └── preload.ts        # Preload script for IPC
├── src/                   # React application
│   ├── components/        # UI components
│   ├── store/            # Redux store and slices
│   ├── App.tsx           # Main app component
│   └── main.tsx          # React entry point
├── backend_integration.py # Python backend bridge
└── package.json          # Dependencies and scripts
```

### IPC Communication Flow
```
Electron Main Process
    ↓ (spawns Python process)
Python Backend Integration
    ↓ (JSON over stdin/stdout)
Overseer Python Backend
    ↓ (system operations)
System APIs
```

## 🎯 Usage

### Command Palette
The command palette is the primary interface for interacting with the system:

1. **Open Command Palette**: Press `Cmd+K` or `Ctrl+K`
2. **Search Commands**: Type to filter available commands
3. **Navigate**: Use arrow keys to navigate
4. **Execute**: Press Enter to execute selected command

### Available Commands
- **System Information**: Get detailed system info
- **File Search**: Search for files in the system
- **Process List**: View running processes
- **Network Status**: Check network connectivity
- **Disk Usage**: View disk usage information
- **Memory Usage**: Check memory usage
- **Open Terminal**: Launch system terminal

### Python Backend Control
- **Start Backend**: Click "Start" in the Python Backend card
- **Stop Backend**: Click "Stop" to terminate the backend
- **View Output**: Real-time output is displayed in the dashboard
- **Error Handling**: Errors are shown with detailed messages

## 🔧 Configuration

### Environment Variables
```bash
# Development mode
NODE_ENV=development

# Python path (optional)
PYTHON_PATH=/usr/bin/python3
```

### Settings
The application stores settings in the Electron store:
- Theme preferences
- Window size and position
- Recent commands
- User preferences

## 🧪 Development

### Development Commands
```bash
# Start development server
npm run dev

# Build for production
npm run build

# Package for distribution
npm run dist

# Platform-specific builds
npm run dist:mac
npm run dist:win
npm run dist:linux
```

### Debugging
1. **Electron DevTools**: Available in development mode
2. **Python Logging**: Check console for Python backend logs
3. **Redux DevTools**: Available in browser dev tools

### Adding New Commands
1. **Add to Command Palette**: Update `CommandPalette.tsx`
2. **Add to Python Backend**: Update `backend_integration.py`
3. **Add to Redux Store**: Update relevant slices
4. **Test**: Verify IPC communication works

## 🔒 Security

### IPC Security
- **Context Isolation**: Enabled by default
- **Preload Script**: Secure API exposure
- **Input Validation**: All inputs are validated
- **Error Boundaries**: Comprehensive error handling

### File System Access
- **Limited Access**: Only necessary directories
- **User Permissions**: Respects system permissions
- **Sandboxing**: Process isolation

## 🚀 Deployment

### Building for Distribution
```bash
# Build the application
npm run build

# Create distributable
npm run dist

# Platform-specific builds
npm run dist:mac    # macOS
npm run dist:win    # Windows
npm run dist:linux  # Linux
```

### Distribution Files
- **macOS**: `.dmg` file
- **Windows**: `.exe` installer
- **Linux**: `.AppImage` file

## 🐛 Troubleshooting

### Common Issues

1. **Python Backend Not Starting**
   - Check Python installation: `python3 --version`
   - Verify dependencies: `pip list | grep psutil`
   - Check file permissions

2. **IPC Communication Errors**
   - Restart the application
   - Check Python process in Activity Monitor
   - Verify JSON format in communication

3. **Build Errors**
   - Clear node_modules: `rm -rf node_modules && npm install`
   - Update dependencies: `npm update`
   - Check Node.js version

4. **Performance Issues**
   - Monitor memory usage
   - Check for memory leaks
   - Optimize bundle size

### Debug Mode
```bash
# Enable debug logging
DEBUG=* npm run dev

# Check Python backend logs
tail -f ~/.overseer/desktop.log
```

## 🤝 Contributing

### Development Guidelines
1. **TypeScript**: Use strict type checking
2. **ESLint**: Follow code style guidelines
3. **Testing**: Add tests for new features
4. **Documentation**: Update docs for changes

### Code Style
- **React**: Functional components with hooks
- **TypeScript**: Strict type annotations
- **Redux**: Use RTK for state management
- **CSS**: Tailwind CSS for styling

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Electron**: Cross-platform desktop framework
- **React**: UI library
- **Redux Toolkit**: State management
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Icon library

---

For more information about the Overseer project, see the main [README.md](../README.md).
