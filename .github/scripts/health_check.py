#!/usr/bin/env python3
"""
GitHub Repository Health Check Script

This script checks various aspects of repository health and provides
recommendations for improvements.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and report status."""
    if Path(file_path).exists():
        print(f"✅ {description}: Found")
        return True
    else:
        print(f"❌ {description}: Missing")
        return False

def check_directory_exists(dir_path, description):
    """Check if a directory exists and report status."""
    if Path(dir_path).exists():
        print(f"✅ {description}: Found")
        return True
    else:
        print(f"❌ {description}: Missing")
        return False

def check_github_files():
    """Check for standard GitHub files."""
    print("🔍 Checking GitHub repository files...")
    
    files_to_check = [
        ("README.md", "README file"),
        ("LICENSE", "License file"),
        (".gitignore", "Git ignore file"),
        (".github/CONTRIBUTING.md", "Contributing guidelines"),
        (".github/SECURITY.md", "Security policy"),
        (".github/SUPPORT.md", "Support documentation"),
        (".github/CODEOWNERS", "Code owners file"),
        (".github/pull_request_template.md", "Pull request template"),
    ]
    
    score = 0
    total = len(files_to_check)
    
    for file_path, description in files_to_check:
        if check_file_exists(file_path, description):
            score += 1
    
    print(f"\n📊 Repository health score: {score}/{total} ({score/total*100:.1f}%)")
    
    return score / total

def check_github_directories():
    """Check for standard GitHub directories."""
    print("\n🔍 Checking GitHub repository directories...")
    
    dirs_to_check = [
        (".github", "GitHub configuration directory"),
        (".github/workflows", "GitHub Actions workflows"),
        (".github/ISSUE_TEMPLATE", "Issue templates"),
        (".github/DISCUSSION_TEMPLATE", "Discussion templates"),
    ]
    
    for dir_path, description in dirs_to_check:
        check_directory_exists(dir_path, description)

def check_branch_protection():
    """Check if branch protection is enabled (requires gh CLI)."""
    print("\n🔍 Checking branch protection...")
    
    try:
        result = subprocess.run(
            ["gh", "api", "repos/:owner/:repo/branches/main/protection"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Branch protection: Enabled")
        else:
            print("❌ Branch protection: Not enabled or not accessible")
    except FileNotFoundError:
        print("ℹ️  GitHub CLI not found. Install 'gh' to check branch protection.")

def main():
    """Main function to run all checks."""
    print("🏥 GitHub Repository Health Check")
    print("=" * 40)
    
    # Change to repository root if script is run from .github/scripts
    script_dir = Path(__file__).parent
    if script_dir.name == "scripts" and script_dir.parent.name == ".github":
        os.chdir(script_dir.parent.parent)
    
    # Run all checks
    health_score = check_github_files()
    check_github_directories()
    check_branch_protection()
    
    # Provide recommendations
    print("\n💡 Recommendations:")
    if health_score < 0.8:
        print("- Consider adding missing repository files")
    if not Path(".github/workflows").exists():
        print("- Set up GitHub Actions for CI/CD")
    if not Path(".github/ISSUE_TEMPLATE").exists():
        print("- Add issue templates to improve bug reporting")
    
    print("\n🎉 Health check complete!")

if __name__ == "__main__":
    main()
