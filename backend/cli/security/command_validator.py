"""
Command Validation and Sanitization

This module provides comprehensive command validation, sanitization,
and security checks for the Overseer system.
"""

import re
import shlex
import os
from typing import Dict, List, Optional, Tuple, Set
from urllib.parse import urlparse
from .security_config import SecurityConfig, SecurityLevel, PermissionLevel

class CommandValidator:
    """Validates and sanitizes commands before execution"""
    
    def __init__(self, security_config: SecurityConfig):
        self.security_config = security_config
        self.dangerous_patterns = self._init_dangerous_patterns()
        self.injection_patterns = self._init_injection_patterns()
        self.path_traversal_patterns = self._init_path_traversal_patterns()
    
    def _init_dangerous_patterns(self) -> List[re.Pattern]:
        """Initialize dangerous command patterns"""
        patterns = [
            # Destructive file operations
            r'rm\s+-rf?\s+/\s*$',  # rm -rf /
            r'dd\s+if=/dev/zero',  # dd if=/dev/zero
            r'mkfs\s+',  # mkfs commands
            r'fdisk\s+',  # fdisk commands
            
            # Privilege escalation
            r'sudo\s+.*\s+chmod\s+777',  # sudo chmod 777
            r'sudo\s+.*\s+chown\s+root',  # sudo chown root
            r'sudo\s+.*\s+passwd',  # sudo passwd
            
            # System modification
            r'systemctl\s+stop\s+',  # systemctl stop
            r'service\s+stop\s+',  # service stop
            r'kill\s+-9\s+',  # kill -9
            
            # Network attacks
            r'wget\s+.*\s+\|\s+bash',  # wget | bash
            r'curl\s+.*\s+\|\s+bash',  # curl | bash
            
            # Package manager abuse
            r'apt\s+install\s+.*\s+&&\s+',  # apt install && command
            r'pip\s+install\s+.*\s+&&\s+',  # pip install && command
        ]
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def _init_injection_patterns(self) -> List[re.Pattern]:
        """Initialize command injection patterns"""
        patterns = [
            # Command injection
            r'[;&|`]',  # Command separators
            r'\$\{.*\}',  # Variable expansion
            r'`.*`',  # Command substitution
            r'\(\s*\$',  # Process substitution
            r'\\\s*[;&|`]',  # Escaped separators
            
            # SQL injection
            r';\s*DROP\s+TABLE',  # SQL injection
            r';\s*DELETE\s+FROM',  # SQL injection
            r';\s*UPDATE\s+',  # SQL injection
            
            # Path injection
            r'\.\./',  # Directory traversal
            r'\.\.\\',  # Windows directory traversal
        ]
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def _init_path_traversal_patterns(self) -> List[re.Pattern]:
        """Initialize path traversal patterns"""
        patterns = [
            r'\.\./',  # Unix path traversal
            r'\.\.\\',  # Windows path traversal
            r'%2e%2e%2f',  # URL encoded
            r'%2e%2e%5c',  # URL encoded Windows
            r'\.\.%2f',  # Mixed encoding
            r'\.\.%5c',  # Mixed encoding Windows
        ]
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def validate_command(self, command: str, user_input: str = "") -> Tuple[bool, str, Dict]:
        """
        Validate a command for security issues
        
        Returns:
            Tuple of (is_valid, error_message, security_info)
        """
        security_info = {
            'risk_level': 'low',
            'warnings': [],
            'blocked_reason': None,
            'requires_confirmation': False,
            'requires_admin': False
        }
        
        # Basic sanitization
        sanitized_command = self._sanitize_command(command)
        if sanitized_command != command:
            security_info['warnings'].append("Command was sanitized")
        
        # Check if command is allowed
        if not self.security_config.is_command_allowed(sanitized_command):
            security_info['blocked_reason'] = "Command is blacklisted"
            return False, "Command is not allowed", security_info
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if pattern.search(sanitized_command):
                security_info['risk_level'] = 'critical'
                security_info['blocked_reason'] = f"Matches dangerous pattern: {pattern.pattern}"
                return False, f"Command matches dangerous pattern: {pattern.pattern}", security_info
        
        # Check for injection patterns
        for pattern in self.injection_patterns:
            if pattern.search(sanitized_command):
                security_info['risk_level'] = 'high'
                security_info['warnings'].append(f"Potential injection detected: {pattern.pattern}")
        
        # Check for path traversal
        for pattern in self.path_traversal_patterns:
            if pattern.search(sanitized_command):
                security_info['risk_level'] = 'high'
                security_info['warnings'].append(f"Path traversal detected: {pattern.pattern}")
        
        # Check if command requires confirmation
        if self.security_config.requires_confirmation(sanitized_command):
            security_info['requires_confirmation'] = True
            security_info['risk_level'] = 'medium'
        
        # Check if command requires admin privileges
        if self.security_config.requires_admin(sanitized_command):
            security_info['requires_admin'] = True
            security_info['risk_level'] = 'high'
        
        # Check for protected paths
        if self._contains_protected_paths(sanitized_command):
            security_info['risk_level'] = 'high'
            security_info['warnings'].append("Command accesses protected system paths")
        
        # Check for network operations
        if self._contains_network_operations(sanitized_command):
            security_info['warnings'].append("Command performs network operations")
        
        # Validate arguments
        arg_validation = self._validate_arguments(sanitized_command)
        if not arg_validation[0]:
            return False, arg_validation[1], security_info
        
        return True, "", security_info
    
    def _sanitize_command(self, command: str) -> str:
        """Sanitize command to prevent injection attacks"""
        # Remove null bytes
        command = command.replace('\x00', '')
        
        # Remove control characters
        command = re.sub(r'[\x00-\x1f\x7f]', '', command)
        
        # Normalize whitespace
        command = re.sub(r'\s+', ' ', command).strip()
        
        # Remove multiple command separators
        command = re.sub(r'[;&|]{2,}', ';', command)
        
        return command
    
    def _contains_protected_paths(self, command: str) -> bool:
        """Check if command contains protected paths"""
        # Extract file paths from command
        paths = re.findall(r'[\'"`]?([^\s\'"`]+\.(?:txt|conf|cfg|ini|json|xml|yaml|yml))[\'"`]?', command)
        paths.extend(re.findall(r'[\'"`]?([^\s\'"`]+/etc/[^\s\'"`]*)[\'"`]?', command))
        paths.extend(re.findall(r'[\'"`]?([^\s\'"`]+/var/[^\s\'"`]*)[\'"`]?', command))
        
        for path in paths:
            if self.security_config.is_path_protected(path):
                return True
            if self.security_config.is_file_protected(path):
                return True
        
        return False
    
    def _contains_network_operations(self, command: str) -> bool:
        """Check if command contains network operations"""
        network_commands = [
            'wget', 'curl', 'scp', 'rsync', 'ssh', 'telnet', 'ftp',
            'nc', 'netcat', 'nmap', 'ping', 'traceroute', 'dig'
        ]
        return any(cmd in command.lower() for cmd in network_commands)
    
    def _validate_arguments(self, command: str) -> Tuple[bool, str]:
        """Validate command arguments"""
        try:
            # Parse command into parts
            parts = shlex.split(command)
            if not parts:
                return False, "Empty command"
            
            # Check for excessive arguments
            if len(parts) > 50:
                return False, "Too many arguments"
            
            # Check for suspicious argument patterns
            for part in parts:
                if len(part) > 1000:
                    return False, "Argument too long"
                
                # Check for suspicious patterns in arguments
                if re.search(r'[;&|`]', part):
                    return False, "Suspicious characters in arguments"
                
                # Check for path traversal in arguments
                for pattern in self.path_traversal_patterns:
                    if pattern.search(part):
                        return False, "Path traversal detected in arguments"
            
            return True, ""
            
        except Exception as e:
            return False, f"Error parsing command: {e}"
    
    def validate_url(self, url: str) -> Tuple[bool, str]:
        """Validate URL for security"""
        try:
            parsed = urlparse(url)
            
            # Check if domain is blocked
            if parsed.netloc in self.security_config.network_security.blocked_domains:
                return False, f"Domain {parsed.netloc} is blocked"
            
            # Check if SSL is required
            if self.security_config.network_security.require_ssl:
                if parsed.scheme not in ['https', 'wss']:
                    return False, "HTTPS is required"
            
            # Check if domain is allowed (if whitelist is enforced)
            if self.security_config.security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
                if parsed.netloc not in self.security_config.network_security.allowed_domains:
                    return False, f"Domain {parsed.netloc} is not in allowed list"
            
            return True, ""
            
        except Exception as e:
            return False, f"Invalid URL: {e}"
    
    def validate_file_path(self, file_path: str) -> Tuple[bool, str]:
        """Validate file path for security"""
        try:
            # Normalize path
            normalized_path = os.path.normpath(file_path)
            
            # Check for path traversal
            if '..' in normalized_path:
                return False, "Path traversal detected"
            
            # Check if path is protected
            if self.security_config.is_path_protected(normalized_path):
                return False, "Path is protected"
            
            if self.security_config.is_file_protected(normalized_path):
                return False, "File is protected"
            
            # Check for suspicious patterns
            if re.search(r'[;&|`]', normalized_path):
                return False, "Suspicious characters in path"
            
            return True, ""
            
        except Exception as e:
            return False, f"Invalid file path: {e}"
    
    def get_command_risk_assessment(self, command: str) -> Dict:
        """Get comprehensive risk assessment for a command"""
        is_valid, error_msg, security_info = self.validate_command(command)
        
        assessment = {
            'is_valid': is_valid,
            'error_message': error_msg,
            'risk_level': security_info['risk_level'],
            'warnings': security_info['warnings'],
            'requires_confirmation': security_info['requires_confirmation'],
            'requires_admin': security_info['requires_admin'],
            'recommendations': []
        }
        
        # Add recommendations based on risk level
        if security_info['risk_level'] == 'critical':
            assessment['recommendations'].append("Do not execute this command")
        elif security_info['risk_level'] == 'high':
            assessment['recommendations'].append("Review command carefully before execution")
            assessment['recommendations'].append("Consider running in a sandbox environment")
        elif security_info['requires_confirmation']:
            assessment['recommendations'].append("Requires user confirmation")
        elif security_info['requires_admin']:
            assessment['recommendations'].append("Requires administrative privileges")
        
        return assessment 