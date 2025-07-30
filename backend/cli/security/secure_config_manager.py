"""
Secure Configuration Manager

This module provides secure configuration file handling with automatic
permission protection (chmod 600) for sensitive files containing API keys
and other secrets.
"""

import os
import json
import stat
import tempfile
import shutil
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

class ConfigSecurityLevel(Enum):
    """Security levels for configuration files"""
    PUBLIC = "public"      # No sensitive data
    PRIVATE = "private"    # Contains sensitive data (API keys, etc.)
    SECRET = "secret"      # Highly sensitive data (passwords, tokens)

@dataclass
class ConfigFile:
    """Configuration file metadata"""
    path: str
    security_level: ConfigSecurityLevel
    sensitive_fields: List[str]
    description: str

class SecureConfigManager:
    """Manages configuration files with automatic security protection"""
    
    def __init__(self, config_dir: str = None):
        self.config_dir = config_dir or os.path.expanduser("~/.overseer")
        self.sensitive_files: Dict[str, ConfigFile] = {}
        self._init_sensitive_files()
        self._auto_fix_enabled = True  # Enable automatic fixing
    
    def _init_sensitive_files(self):
        """Initialize list of sensitive configuration files"""
        self.sensitive_files = {
            "config.json": ConfigFile(
                path=os.path.join(self.config_dir, "config.json"),
                security_level=ConfigSecurityLevel.PRIVATE,
                sensitive_fields=["gemini_api_key", "openai_api_key", "password", "token"],
                description="Main Overseer configuration file"
            ),
            "security_config.json": ConfigFile(
                path=os.path.join(self.config_dir, "security_config.json"),
                security_level=ConfigSecurityLevel.SECRET,
                sensitive_fields=["encryption_key", "master_password", "auth_tokens"],
                description="Security configuration file"
            ),
            "permissions.json": ConfigFile(
                path=os.path.join(self.config_dir, "permissions.json"),
                security_level=ConfigSecurityLevel.PRIVATE,
                sensitive_fields=["user_tokens", "session_keys"],
                description="User permissions and access control"
            ),
            "api_keys.json": ConfigFile(
                path=os.path.join(self.config_dir, "api_keys.json"),
                security_level=ConfigSecurityLevel.SECRET,
                sensitive_fields=["*"],  # All fields are sensitive
                description="API keys and credentials"
            ),
            "credentials.json": ConfigFile(
                path=os.path.join(self.config_dir, "credentials.json"),
                security_level=ConfigSecurityLevel.SECRET,
                sensitive_fields=["*"],  # All fields are sensitive
                description="User credentials and passwords"
            )
        }
    
    def disable_auto_fix(self):
        """Disable automatic security fixing"""
        self._auto_fix_enabled = False
    
    def enable_auto_fix(self):
        """Enable automatic security fixing"""
        self._auto_fix_enabled = True
    
    def is_auto_fix_enabled(self) -> bool:
        """Check if auto-fix is enabled"""
        return self._auto_fix_enabled

    def secure_file_permissions(self, file_path: str, security_level: ConfigSecurityLevel = None):
        """Apply secure permissions to a file"""
        try:
            if not os.path.exists(file_path):
                return False
            
            # Determine permissions based on security level
            if security_level == ConfigSecurityLevel.SECRET:
                # 600: Owner read/write only
                mode = stat.S_IRUSR | stat.S_IWUSR
            elif security_level == ConfigSecurityLevel.PRIVATE:
                # 600: Owner read/write only
                mode = stat.S_IRUSR | stat.S_IWUSR
            else:
                # 644: Owner read/write, group/others read
                mode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
            
            # Apply permissions
            os.chmod(file_path, mode)
            return True
            
        except Exception as e:
            print(f"Warning: Could not secure file permissions for {file_path}: {e}")
            return False
    
    def check_file_security(self, file_path: str) -> Dict[str, Any]:
        """Check the security status of a file"""
        if not os.path.exists(file_path):
            return {
                "exists": False,
                "secure": False,
                "permissions": None,
                "issues": ["File does not exist"]
            }
        
        try:
            # Get current permissions
            stat_info = os.stat(file_path)
            mode = stat_info.st_mode
            
            # Check if file is secure (600 permissions)
            is_secure = (
                bool(mode & stat.S_IRUSR) and  # Owner can read
                bool(mode & stat.S_IWUSR) and  # Owner can write
                not bool(mode & stat.S_IRGRP) and  # Group cannot read
                not bool(mode & stat.S_IWGRP) and  # Group cannot write
                not bool(mode & stat.S_IROTH) and  # Others cannot read
                not bool(mode & stat.S_IWOTH)      # Others cannot write
            )
            
            issues = []
            if not is_secure:
                issues.append("File permissions are too permissive")
            
            # Check if file is in a secure directory
            parent_dir = os.path.dirname(file_path)
            parent_stat = os.stat(parent_dir)
            parent_mode = parent_stat.st_mode
            
            if bool(parent_mode & stat.S_IWOTH):
                issues.append("Parent directory is world-writable")
            
            return {
                "exists": True,
                "secure": is_secure and len(issues) == 0,
                "permissions": oct(mode)[-3:],
                "issues": issues
            }
            
        except Exception as e:
            return {
                "exists": True,
                "secure": False,
                "permissions": None,
                "issues": [f"Error checking file: {e}"]
            }
    
    def load_config(self, file_name: str) -> Optional[Dict[str, Any]]:
        """Load configuration from a file with security checks and automatic fixing"""
        if file_name not in self.sensitive_files:
            # For non-sensitive files, load normally
            file_path = os.path.join(self.config_dir, file_name)
            if not os.path.exists(file_path):
                return None
            
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config {file_name}: {e}")
                return None
        
        # For sensitive files, check security first
        config_file = self.sensitive_files[file_name]
        security_status = self.check_file_security(config_file.path)
        
        if not security_status["secure"] and self._auto_fix_enabled:
            # Automatically fix security issues on first load
            print(f"🔧 Auto-fixing security issues for {file_name}...")
            fix_success = self.secure_file_permissions(config_file.path, config_file.security_level)
            
            if fix_success:
                print(f"✅ Security issues fixed for {file_name}")
                # Re-check security
                security_status = self.check_file_security(config_file.path)
            else:
                print(f"⚠️  Could not auto-fix {file_name}, continuing anyway")
        
        elif not security_status["secure"]:
            # Show warning only if auto-fix is disabled
            print(f"Warning: {file_name} has security issues:")
            for issue in security_status["issues"]:
                print(f"  - {issue}")
            
            # Ask user if they want to continue
            try:
                import questionary
                continue_anyway = questionary.confirm(
                    f"Continue loading {file_name} despite security issues?"
                ).ask()
            except ImportError:
                continue_anyway = input(
                    f"Continue loading {file_name} despite security issues? (y/n): "
                ).strip().lower() in ('y', 'yes')
            
            if not continue_anyway:
                return None
        
        # Load the file
        try:
            with open(config_file.path, 'r') as f:
                config = json.load(f)
            
            # Mask sensitive fields in logs
            masked_config = self._mask_sensitive_fields(config, config_file.sensitive_fields)
            print(f"Loaded config: {masked_config}")
            
            return config
            
        except Exception as e:
            print(f"Error loading config {file_name}: {e}")
            return None
    
    def save_config(self, file_name: str, config_data: Dict[str, Any], 
                   security_level: ConfigSecurityLevel = None) -> bool:
        """Save configuration to a file with automatic security protection"""
        
        # Determine security level
        if security_level is None:
            if file_name in self.sensitive_files:
                security_level = self.sensitive_files[file_name].security_level
            else:
                security_level = ConfigSecurityLevel.PUBLIC
        
        # Create config directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Use temporary file for atomic write
        temp_file = None
        try:
            # Create temporary file
            temp_fd, temp_file = tempfile.mkstemp(
                dir=self.config_dir,
                prefix=f"{file_name}.tmp.",
                suffix=".json"
            )
            
            # Write data to temporary file
            with os.fdopen(temp_fd, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            # Apply secure permissions to temporary file
            self.secure_file_permissions(temp_file, security_level)
            
            # Move temporary file to final location
            final_path = os.path.join(self.config_dir, file_name)
            shutil.move(temp_file, final_path)
            
            # Ensure final file has correct permissions
            self.secure_file_permissions(final_path, security_level)
            
            print(f"✅ Configuration saved securely to {final_path}")
            
            # Verify security
            security_status = self.check_file_security(final_path)
            if security_status["secure"]:
                print(f"✅ File permissions verified: {security_status['permissions']}")
            else:
                print(f"⚠️  Security warning: {security_status['issues']}")
            
            return True
            
        except Exception as e:
            print(f"Error saving config {file_name}: {e}")
            
            # Clean up temporary file if it exists
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except Exception:
                    pass
            
            return False
    
    def _mask_sensitive_fields(self, config: Dict[str, Any], sensitive_fields: List[str]) -> Dict[str, Any]:
        """Mask sensitive fields in configuration for logging"""
        masked = config.copy()
        
        for field in sensitive_fields:
            if field == "*":
                # Mask all fields
                for key in masked:
                    if isinstance(masked[key], str) and len(masked[key]) > 0:
                        masked[key] = "***MASKED***"
            elif field in masked:
                if isinstance(masked[field], str) and len(masked[field]) > 0:
                    masked[field] = "***MASKED***"
        
        return masked
    
    def audit_config_files(self) -> Dict[str, Dict[str, Any]]:
        """Audit all configuration files for security issues"""
        results = {}
        
        print("🔒 Auditing configuration file security...")
        print("=" * 50)
        
        for file_name, config_file in self.sensitive_files.items():
            security_status = self.check_file_security(config_file.path)
            results[file_name] = security_status
            
            status_icon = "✅" if security_status["secure"] else "⚠️"
            print(f"{status_icon} {file_name}: {config_file.description}")
            print(f"   Path: {config_file.path}")
            print(f"   Security Level: {config_file.security_level.value}")
            print(f"   Permissions: {security_status['permissions']}")
            
            if not security_status["secure"]:
                print(f"   Issues:")
                for issue in security_status["issues"]:
                    print(f"     - {issue}")
            
            print()
        
        return results
    
    def fix_config_security(self, file_name: str = None) -> bool:
        """Fix security issues for configuration files"""
        if file_name:
            # Fix specific file
            if file_name not in self.sensitive_files:
                print(f"Error: {file_name} is not a known sensitive file")
                return False
            
            config_file = self.sensitive_files[file_name]
            if not os.path.exists(config_file.path):
                print(f"Error: {file_name} does not exist")
                return False
            
            # Load and resave to apply correct permissions
            config = self.load_config(file_name)
            if config is None:
                return False
            
            return self.save_config(file_name, config, config_file.security_level)
        
        else:
            # Fix all sensitive files
            print("🔧 Fixing security for all configuration files...")
            success_count = 0
            
            for file_name, config_file in self.sensitive_files.items():
                if os.path.exists(config_file.path):
                    print(f"Fixing {file_name}...")
                    if self.fix_config_security(file_name):
                        success_count += 1
                        print(f"✅ Fixed {file_name}")
                    else:
                        print(f"❌ Failed to fix {file_name}")
                else:
                    print(f"⏭️  Skipping {file_name} (does not exist)")
            
            print(f"\nFixed {success_count}/{len(self.sensitive_files)} files")
            return success_count == len(self.sensitive_files)

def secure_config_save(file_path: str, config_data: Dict[str, Any], 
                      security_level: ConfigSecurityLevel = ConfigSecurityLevel.PRIVATE) -> bool:
    """Convenience function to save config with security protection"""
    manager = SecureConfigManager()
    file_name = os.path.basename(file_path)
    return manager.save_config(file_name, config_data, security_level)

def secure_config_load(file_path: str) -> Optional[Dict[str, Any]]:
    """Convenience function to load config with security checks"""
    manager = SecureConfigManager()
    file_name = os.path.basename(file_path)
    return manager.load_config(file_name) 