#!/usr/bin/env python3
"""
Migration script to transition from setup.py to pyproject.toml
This script helps clean up the old installation and set up the new one.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("=== Overseer CLI Migration to Modern Packaging ===")
    print()
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("Error: pyproject.toml not found. Please run this script from the backend directory.")
        sys.exit(1)
    
    print("This script will:")
    print("1. Uninstall the old editable installation")
    print("2. Install the new package using modern standards")
    print("3. Verify the installation")
    print()
    
    response = input("Continue? (y/N): ").strip().lower()
    if response != 'y':
        print("Migration cancelled.")
        return
    
    # Step 1: Uninstall old installation
    print("\n--- Step 1: Uninstalling old installation ---")
    if not run_command("pip uninstall overseer-cli -y", "Uninstalling old package"):
        print("Warning: Could not uninstall old package. This might be expected if it wasn't installed.")
    
    # Step 2: Install new package
    print("\n--- Step 2: Installing new package ---")
    if not run_command("pip install -e .", "Installing new package in editable mode"):
        print("Error: Failed to install new package.")
        sys.exit(1)
    
    # Step 3: Verify installation
    print("\n--- Step 3: Verifying installation ---")
    if not run_command("overseer --help", "Testing overseer command"):
        print("Error: Overseer command not working properly.")
        sys.exit(1)
    
    print("\n=== Migration completed successfully! ===")
    print("The deprecation warning should now be resolved.")
    print("You can now use 'overseer' command without warnings.")

if __name__ == "__main__":
    main() 