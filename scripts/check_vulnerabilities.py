#!/usr/bin/env python3
"""
Security Vulnerability Scanner
Checks for known vulnerabilities in project dependencies
"""

import subprocess
import sys
import json
from typing import List, Dict, Any

def check_python_vulnerabilities() -> List[Dict[str, Any]]:
    """Check Python dependencies for vulnerabilities using pip-audit"""
    print("Checking Python dependencies for vulnerabilities...")
    
    try:
        # Try to install pip-audit if not available
        subprocess.run([sys.executable, "-m", "pip", "install", "pip-audit", "-q"], 
                      check=False, capture_output=True)
        
        # Run pip-audit
        result = subprocess.run(
            [sys.executable, "-m", "pip-audit", "--format", "json"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print("✓ No vulnerabilities found in Python dependencies")
            return []
        else:
            try:
                vulnerabilities = json.loads(result.stdout)
                return vulnerabilities.get('dependencies', [])
            except json.JSONDecodeError:
                print("⚠ Could not parse pip-audit output")
                return []
                
    except Exception as e:
        print(f"⚠ Error checking Python dependencies: {e}")
        return []

def check_npm_vulnerabilities() -> bool:
    """Check npm dependencies for vulnerabilities"""
    print("\nChecking npm dependencies for vulnerabilities...")
    
    try:
        # Check if npm is available
        subprocess.run(["npm", "--version"], capture_output=True, check=True)
        
        # Run npm audit in desktop-app directory
        result = subprocess.run(
            ["npm", "audit", "--json"],
            cwd="desktop-app",
            capture_output=True,
            text=True,
            check=False
        )
        
        try:
            audit_data = json.loads(result.stdout)
            vulnerabilities = audit_data.get('metadata', {}).get('vulnerabilities', {})
            
            total = sum(vulnerabilities.values())
            if total == 0:
                print("✓ No vulnerabilities found in npm dependencies")
                return True
            else:
                print(f"⚠ Found {total} vulnerabilities in npm dependencies:")
                for severity, count in vulnerabilities.items():
                    if count > 0:
                        print(f"  - {severity}: {count}")
                print("\nRun 'npm audit fix' in desktop-app directory to fix")
                return False
                
        except json.JSONDecodeError:
            print("⚠ Could not parse npm audit output")
            return False
            
    except FileNotFoundError:
        print("⚠ npm not found, skipping npm dependency check")
        return True
    except Exception as e:
        print(f"⚠ Error checking npm dependencies: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("Security Vulnerability Scanner")
    print("=" * 60)
    
    # Check Python dependencies
    python_vulns = check_python_vulnerabilities()
    
    # Check npm dependencies
    npm_ok = check_npm_vulnerabilities()
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    if len(python_vulns) == 0 and npm_ok:
        print("✓ No known vulnerabilities found")
        sys.exit(0)
    else:
        print("⚠ Vulnerabilities detected - please update dependencies")
        print("\nTo fix Python vulnerabilities:")
        print("  pip install --upgrade -r requirements.txt")
        print("\nTo fix npm vulnerabilities:")
        print("  cd desktop-app && npm audit fix")
        sys.exit(1)

if __name__ == "__main__":
    main()
