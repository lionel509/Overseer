#!/bin/bash

# GitHub repository maintenance script
# This script helps with common repository maintenance tasks

echo "🔧 Repository Maintenance Script"
echo "=================================="

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Function to check for updates
check_updates() {
    echo "📦 Checking for updates..."
    
    # Check if there are any uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        echo "⚠️  Warning: You have uncommitted changes"
        git status --porcelain
    fi
    
    # Fetch latest changes
    git fetch origin
    
    # Check if local branch is behind
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse @{u})
    
    if [ "$LOCAL" != "$REMOTE" ]; then
        echo "📥 Your branch is behind the remote. Consider pulling latest changes."
    else
        echo "✅ Your branch is up to date"
    fi
}

# Function to clean up branches
cleanup_branches() {
    echo "🧹 Cleaning up merged branches..."
    
    # Delete merged branches (except main/master)
    git branch --merged | grep -v "\*\|main\|master" | xargs -n 1 git branch -d
    
    echo "✅ Cleanup complete"
}

# Function to check GitHub Actions status
check_actions() {
    echo "⚙️  Checking GitHub Actions status..."
    
    # This would require gh CLI to be installed
    if command -v gh &> /dev/null; then
        gh run list --limit 5
    else
        echo "ℹ️  Install GitHub CLI (gh) to check Actions status"
    fi
}

# Main menu
case "${1:-help}" in
    "update")
        check_updates
        ;;
    "cleanup")
        cleanup_branches
        ;;
    "actions")
        check_actions
        ;;
    "all")
        check_updates
        cleanup_branches
        check_actions
        ;;
    "help"|*)
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  update   - Check for repository updates"
        echo "  cleanup  - Clean up merged branches"
        echo "  actions  - Check GitHub Actions status"
        echo "  all      - Run all maintenance tasks"
        echo "  help     - Show this help message"
        ;;
esac
