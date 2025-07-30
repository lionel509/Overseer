# Overseer CLI Master Guide

## Table of Contents
1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Chat Mode Features](#chat-mode-features)
4. [Plan-Based Execution](#plan-based-execution)
5. [Security Features](#security-features)
6. [Sandbox Command Execution](#sandbox-command-execution)
7. [Auto-Organize Feature](#auto-organize-feature)
8. [Best Practices](#best-practices)

## Overview

Overseer CLI is an intelligent system assistant that provides:
- **Natural Language Interface**: Chat with the system using plain English
- **Plan-Based Execution**: Complex tasks broken into step-by-step plans
- **Security-First Design**: Sandbox protection and secure configuration management
- **File Organization**: AI-powered file categorization and organization
- **Token Efficiency**: Optimized to minimize API costs

## Getting Started

### Installation
```bash
cd backend/cli
python -m overseer_cli
```

### Basic Commands
```bash
# Start chat mode
python -m overseer_cli

# Exit
exit

# Clear screen
clear

# Undo last command
undo

# Open settings
settings
```

## Chat Mode Features

### Natural Language Interface
All features are accessible through natural language:

```bash
# File Organization
"organize my downloads" → Auto-organize with safety
"sort my documents" → Sort by type
"find my tax file" → Search files

# Security
"check my config security" → Security audit
"fix my config security" → Automatic security fixes
"check permissions on my config file" → File permission analysis

# Commands
"check my git status" → Safe command execution
"install numpy with pip" → Package installation
"list Docker containers" → System commands
```

### Example Session
```
user: organize my downloads
overseer: ACTION: auto_organize folders=~/Downloads

📁 Organizing 15 files in ~/Downloads...
Preview of moves in ~/Downloads:
  document.pdf -> Documents/
  photo.jpg -> Images/
  video.mp4 -> Videos/
  archive.zip -> Archives/

Move 4 files in ~/Downloads? (yes/no/always/never): yes
✅ All files organized successfully
```

## Plan-Based Execution

### How It Works

**Simple Tasks** → Direct execution:
```
User: "check my git status"
LLM: ACTION: run_command command="git status"
```

**Complex Tasks** → Plan with confirmations:
```
User: "set up my development environment"
LLM: PLAN: check_permissions path=~/.ssh/id_rsa | run_command command="git config --global user.name" | run_command command="pip install numpy pandas matplotlib"

I have a 3-step plan for you:
  1. check_permissions path=~/.ssh/id_rsa
  2. run_command command="git config --global user.name"
  3. run_command command="pip install numpy pandas matplotlib"

Should I proceed with this plan? (y/n): y

Step 1/3: check_permissions path=~/.ssh/id_rsa
Execute step 1? (y/n): y
✅ ~/.ssh/id_rsa: Secure

Step 2/3: run_command command="git config --global user.name"
Execute step 2? (y/n): y
🔍 Validating command in sandbox...
✅ Command executed successfully

Step 3/3: run_command command="pip install numpy pandas matplotlib"
Execute step 3? (y/n): y
🔍 Validating command in sandbox...
⚠️  Warnings: Command performs network operations
Risk Level: MEDIUM
Are you sure you want to execute it? (y/n): y
🚀 Executing command...
✅ Command executed successfully

Plan completed!
```

### Benefits
- **Token Efficiency**: 30-70% reduction in token usage
- **User Control**: Full visibility and granular control
- **Error Recovery**: Retry/skip/abort for each step
- **Context Awareness**: Maintains state across steps

## Security Features

### Configuration Security Audit
```bash
user: check my config security
overseer: ACTION: audit_config

🔒 Auditing configuration file security...
==================================================
✅ config.json: Main Overseer configuration file
   Path: ~/.overseer/config.json
   Security Level: private
   Permissions: 600

⚠️  api_keys.json: API keys and credentials
   Path: ~/.overseer/api_keys.json
   Security Level: secret
   Permissions: 644
   Issues:
     - File permissions are too permissive

Configuration security audit completed.
1/2 files are secure.
1 files have security issues.
Use "fix my config security" to resolve issues.
```

### Automatic Security Fixes
```bash
user: fix my config security
overseer: ACTION: fix_config_security

🔧 Fixing security for all configuration files...
Fixing api_keys.json...
✅ Fixed api_keys.json

Fixed 1/1 files
All configuration files are now secure.
```

### File Permission Analysis
```bash
user: check permissions on my config file
overseer: ACTION: check_permissions path=~/.overseer/config.json

✅ ~/.overseer/config.json
Permissions: 600
Status: Secure
```

## Sandbox Command Execution

### Multi-Layer Protection
All commands are executed with multiple safety layers:

1. **Validation**: Checks command syntax and dangerous patterns
2. **Dry Run**: Shows what the command would do
3. **Risk Assessment**: Evaluates danger level
4. **Confirmation**: Asks for approval if risky
5. **Isolated Testing**: Tests dangerous commands in safe environment
6. **Execution**: Runs the command if approved

### Example Session
```
user: check my git status
overseer: ACTION: run_command command="git status"

🔍 Validating command in sandbox...
✅ Validation passed

🔍 Performing dry run...
📋 Dry Run Results:
[DRY RUN] Would execute: git status

Risk Level: LOW

🚀 Executing command...
✅ Command executed successfully
```

### Dangerous Command Protection
```
user: install numpy with pip
overseer: ACTION: run_command command="pip install numpy"

🔍 Validating command in sandbox...
✅ Validation passed

🔍 Performing dry run...
📋 Dry Run Results:
[DRY RUN] Would execute: pip install numpy

⚠️  Warnings:
• Command performs network operations

Risk Level: MEDIUM

🚨 This command has medium risk level.
Command: pip install numpy
Are you sure you want to execute it? (y/n): y

🚀 Executing command...
✅ Command executed successfully
```

## Auto-Organize Feature

### Safe File Organization
```bash
user: organize my downloads
overseer: ACTION: auto_organize folders=~/Downloads

📁 Organizing 15 files in ~/Downloads...
Preview of moves in ~/Downloads:
  document.pdf -> Documents/
  photo.jpg -> Images/
  video.mp4 -> Videos/
  archive.zip -> Archives/

Move 4 files in ~/Downloads? (yes/no/always/never): yes
✅ All files organized successfully
```

### Features
- **AI-Powered Categorization**: Intelligent file sorting
- **Preview Mode**: See what will be moved before execution
- **Confirmation Prompts**: User approval for all moves
- **Risk Assessment**: Warnings for dangerous operations
- **Fallback Options**: Type-based sorting if AI fails

### Safety Measures
- **Default Limits**: Maximum 100 files per folder
- **Safe Defaults**: Only organizes ~/Downloads by default
- **Permission Protection**: Applies chmod 600 to new folders
- **Error Recovery**: Graceful handling of failures

## Best Practices

### For Users
1. **Be Specific**: "set up Python environment" vs "setup"
2. **Review Plans**: Always review the plan before approving
3. **Use Skip**: Skip steps you don't need
4. **Monitor Progress**: Watch each step execute
5. **Handle Errors**: Use retry/skip/abort appropriately

### For Complex Tasks
1. **Break Down**: Complex tasks are automatically broken into steps
2. **Confirm Each Step**: Don't skip confirmation unless in full control mode
3. **Monitor Results**: Check the output of each step
4. **Use Abort**: Stop if something goes wrong

### Security Best Practices
1. **Regular Audits**: Run security audits periodically
2. **Permission Checks**: Verify file permissions regularly
3. **Sandbox Usage**: Always use sandbox for unknown commands
4. **Configuration Security**: Keep sensitive files protected

### Token Efficiency
1. **Use Plans**: Let the system generate plans for complex tasks
2. **Be Concise**: Clear, specific requests work better
3. **Batch Operations**: Combine related tasks when possible
4. **Review Output**: Check results to avoid repeated calls

## Quick Reference

### File Organization
```bash
organize my downloads          # Auto-organize Downloads
sort my documents             # Sort by type
tag file.pdf as important    # Add tags
find my tax file             # Search files
```

### Security
```bash
check my config security     # Audit all configs
fix my config security       # Fix security issues
check permissions on file    # Analyze specific file
```

### Commands
```bash
check my git status          # Safe command execution
install package with pip     # Package installation
list Docker containers       # System commands
```

### Complex Tasks
```bash
set up my development environment    # Multi-step setup
audit my entire system security     # Comprehensive audit
organize my entire system           # Complete organization
```

## Troubleshooting

### Common Issues
1. **Permission Denied**: Run security audit and fix permissions
2. **Command Failed**: Check sandbox logs and retry
3. **Plan Errors**: Use skip/abort to handle problematic steps
4. **Token Limits**: Use plans for complex tasks to reduce token usage

### Getting Help
- Use `settings` to configure the system
- Check logs in `logs/` directory
- Run tests in `tests/` directory
- Review documentation in `docs/` directory

Overseer CLI provides a powerful, secure, and user-friendly interface for system management with intelligent automation and comprehensive safety features! 