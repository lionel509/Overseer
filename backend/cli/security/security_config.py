"""
Security Configuration for Overseer

This module defines security policies, thresholds, and configurations
for the Overseer system based on the comprehensive security analysis.
"""

import os
import json
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

class SecurityLevel(Enum):
    """Security levels for different operations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PermissionLevel(Enum):
    """User permission levels"""
    READ_ONLY = "read_only"
    LIMITED = "limited"
    STANDARD = "standard"
    ADMIN = "admin"

@dataclass
class CommandPolicy:
    """Policy for command execution"""
    whitelist: Set[str] = field(default_factory=set)
    blacklist: Set[str] = field(default_factory=set)
    require_confirmation: Set[str] = field(default_factory=set)
    require_admin: Set[str] = field(default_factory=set)
    timeout_seconds: int = 60
    max_output_size: int = 1024 * 1024  # 1MB

@dataclass
class SystemProtection:
    """System protection settings"""
    protected_paths: Set[str] = field(default_factory=set)
    protected_files: Set[str] = field(default_factory=set)
    max_file_operations: int = 1000
    max_concurrent_operations: int = 5
    backup_before_changes: bool = True

@dataclass
class NetworkSecurity:
    """Network security settings"""
    allowed_domains: Set[str] = field(default_factory=set)
    blocked_domains: Set[str] = field(default_factory=set)
    require_ssl: bool = True
    max_download_size: int = 100 * 1024 * 1024  # 100MB
    rate_limit_requests: int = 100  # requests per minute

@dataclass
class AuditSettings:
    """Audit logging configuration"""
    enabled: bool = True
    log_file: str = "overseer_audit.log"
    log_level: str = "INFO"
    retention_days: int = 90
    sensitive_fields: Set[str] = field(default_factory=set)

@dataclass
class EncryptionSettings:
    """Encryption configuration"""
    enabled: bool = True
    algorithm: str = "AES-256-GCM"
    key_rotation_days: int = 30
    encrypt_config: bool = True
    encrypt_logs: bool = False

class SecurityConfig:
    """Main security configuration class"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.expanduser("~/.overseer/security_config.json")
        self.security_level = SecurityLevel.MEDIUM
        self.permission_level = PermissionLevel.STANDARD
        
        # Initialize security policies
        self.command_policy = self._init_command_policy()
        self.system_protection = self._init_system_protection()
        self.network_security = self._init_network_security()
        self.audit_settings = self._init_audit_settings()
        self.encryption_settings = self._init_encryption_settings()
        
        # Load configuration from file
        self.load_config()
    
    def _init_command_policy(self) -> CommandPolicy:
        """Initialize command execution policy"""
        return CommandPolicy(
            whitelist={
                "ls", "cat", "head", "tail", "grep", "find", "locate",
                "ps", "top", "htop", "df", "du", "free", "who", "w",
                "git", "docker", "kubectl", "helm", "terraform"
            },
            blacklist={
                "rm -rf /", "dd if=/dev/zero", "mkfs", "fdisk",
                "chmod 777", "chown root", "passwd", "useradd",
                "systemctl stop", "service stop", "kill -9"
            },
            require_confirmation={
                "rm", "mv", "cp", "mkdir", "touch", "chmod", "chown",
                "sudo", "apt", "snap", "pip", "npm", "docker run",
                "kubectl apply", "terraform apply"
            },
            require_admin={
                "sudo", "apt", "snap", "systemctl", "service",
                "useradd", "userdel", "passwd", "chown root"
            }
        )
    
    def _init_system_protection(self) -> SystemProtection:
        """Initialize system protection settings"""
        return SystemProtection(
            protected_paths={
                "/etc", "/var", "/usr", "/bin", "/sbin", "/lib",
                "/boot", "/dev", "/proc", "/sys", "/root"
            },
            protected_files={
                "/etc/passwd", "/etc/shadow", "/etc/sudoers",
                "/etc/fstab", "/etc/hosts", "/etc/resolv.conf"
            }
        )
    
    def _init_network_security(self) -> NetworkSecurity:
        """Initialize network security settings"""
        return NetworkSecurity(
            allowed_domains={
                "api.openai.com", "generativelanguage.googleapis.com",
                "huggingface.co", "github.com", "pypi.org"
            },
            blocked_domains={
                "malicious-site.com", "phishing-example.com"
            }
        )
    
    def _init_audit_settings(self) -> AuditSettings:
        """Initialize audit settings"""
        return AuditSettings(
            sensitive_fields={
                "password", "token", "key", "secret", "credential"
            }
        )
    
    def _init_encryption_settings(self) -> EncryptionSettings:
        """Initialize encryption settings"""
        return EncryptionSettings()
    
    def load_config(self):
        """Load security configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                    self._apply_config(config_data)
        except Exception as e:
            print(f"Warning: Could not load security config: {e}")
    
    def save_config(self):
        """Save security configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            config_data = self._serialize_config()
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save security config: {e}")
    
    def _apply_config(self, config_data: Dict):
        """Apply configuration from dictionary"""
        if 'security_level' in config_data:
            self.security_level = SecurityLevel(config_data['security_level'])
        if 'permission_level' in config_data:
            self.permission_level = PermissionLevel(config_data['permission_level'])
        
        # Apply command policy
        if 'command_policy' in config_data:
            cp = config_data['command_policy']
            if 'whitelist' in cp:
                self.command_policy.whitelist.update(cp['whitelist'])
            if 'blacklist' in cp:
                self.command_policy.blacklist.update(cp['blacklist'])
            if 'require_confirmation' in cp:
                self.command_policy.require_confirmation.update(cp['require_confirmation'])
            if 'require_admin' in cp:
                self.command_policy.require_admin.update(cp['require_admin'])
    
    def _serialize_config(self) -> Dict:
        """Serialize configuration to dictionary"""
        return {
            'security_level': self.security_level.value,
            'permission_level': self.permission_level.value,
            'command_policy': {
                'whitelist': list(self.command_policy.whitelist),
                'blacklist': list(self.command_policy.blacklist),
                'require_confirmation': list(self.command_policy.require_confirmation),
                'require_admin': list(self.command_policy.require_admin),
                'timeout_seconds': self.command_policy.timeout_seconds,
                'max_output_size': self.command_policy.max_output_size
            },
            'system_protection': {
                'protected_paths': list(self.system_protection.protected_paths),
                'protected_files': list(self.system_protection.protected_files),
                'max_file_operations': self.system_protection.max_file_operations,
                'max_concurrent_operations': self.system_protection.max_concurrent_operations,
                'backup_before_changes': self.system_protection.backup_before_changes
            },
            'network_security': {
                'allowed_domains': list(self.network_security.allowed_domains),
                'blocked_domains': list(self.network_security.blocked_domains),
                'require_ssl': self.network_security.require_ssl,
                'max_download_size': self.network_security.max_download_size,
                'rate_limit_requests': self.network_security.rate_limit_requests
            },
            'audit_settings': {
                'enabled': self.audit_settings.enabled,
                'log_file': self.audit_settings.log_file,
                'log_level': self.audit_settings.log_level,
                'retention_days': self.audit_settings.retention_days,
                'sensitive_fields': list(self.audit_settings.sensitive_fields)
            },
            'encryption_settings': {
                'enabled': self.encryption_settings.enabled,
                'algorithm': self.encryption_settings.algorithm,
                'key_rotation_days': self.encryption_settings.key_rotation_days,
                'encrypt_config': self.encryption_settings.encrypt_config,
                'encrypt_logs': self.encryption_settings.encrypt_logs
            }
        }
    
    def is_command_allowed(self, command: str) -> bool:
        """Check if a command is allowed based on current policy"""
        # Check blacklist first
        for blocked in self.command_policy.blacklist:
            if blocked in command:
                return False
        
        # Check whitelist if security level is high
        if self.security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
            if not any(allowed in command for allowed in self.command_policy.whitelist):
                return False
        
        return True
    
    def requires_confirmation(self, command: str) -> bool:
        """Check if command requires user confirmation"""
        return any(conf in command for conf in self.command_policy.require_confirmation)
    
    def requires_admin(self, command: str) -> bool:
        """Check if command requires admin privileges"""
        return any(admin in command for admin in self.command_policy.require_admin)
    
    def is_path_protected(self, path: str) -> bool:
        """Check if a path is protected"""
        normalized_path = os.path.normpath(path)
        return any(protected in normalized_path for protected in self.system_protection.protected_paths)
    
    def is_file_protected(self, file_path: str) -> bool:
        """Check if a file is protected"""
        normalized_path = os.path.normpath(file_path)
        return normalized_path in self.system_protection.protected_files 