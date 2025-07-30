"""
Security Manager

This module provides a unified interface for all security operations,
integrating command validation, audit logging, threat detection,
encryption, and permission management.
"""

import time
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from .security_config import SecurityConfig
from .command_validator import CommandValidator
from .audit_logger import AuditLogger
from .threat_detector import ThreatDetector, ThreatEvent
from .encryption_manager import EncryptionManager
from .permission_manager import PermissionManager, Permission
from .undo_manager import UndoManager

@dataclass
class SecurityContext:
    """Security context for operations"""
    user_id: str
    session_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class SecurityManager:
    """Unified security management system"""
    
    def __init__(self, config_path: Optional[str] = None):
        # Initialize security configuration
        self.security_config = SecurityConfig(config_path)
        
        # Initialize security components
        self.command_validator = CommandValidator(self.security_config)
        self.audit_logger = AuditLogger(self.security_config)
        self.threat_detector = ThreatDetector(self.security_config)
        self.encryption_manager = EncryptionManager(self.security_config)
        self.permission_manager = PermissionManager(self.security_config)
        self.undo_manager = UndoManager()
        
        # Set up threat detection callbacks
        self.threat_detector.add_alert_callback(self._handle_threat_alert)
        
        # Background cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
    
    def _handle_threat_alert(self, threat: ThreatEvent) -> None:
        """Handle threat alerts"""
        # Log the threat
        self.audit_logger.log_security_event(
            event_type=threat.threat_type,
            description=threat.description,
            user_id=threat.source,
            risk_level=threat.risk_level,
            details=threat.details
        )
        
        # Take action based on threat level
        if threat.risk_level == "critical":
            # Block the source immediately
            self.threat_detector._block_source(threat.source)
        
        # Additional threat handling could be implemented here
        # such as sending notifications, triggering system alerts, etc.
    
    def _cleanup_loop(self) -> None:
        """Background cleanup loop"""
        while True:
            try:
                # Clean up expired sessions
                expired_count = self.permission_manager.cleanup_expired_sessions()
                if expired_count > 0:
                    print(f"Cleaned up {expired_count} expired sessions")
                
                # Clean up old audit logs
                self.audit_logger.cleanup_old_logs()
                
                # Sleep for cleanup interval
                time.sleep(300)  # Run cleanup every 5 minutes
                
            except Exception as e:
                print(f"Error in security cleanup loop: {e}")
                time.sleep(600)  # Wait longer on error
    
    def validate_and_execute_command(self, command: str, context: SecurityContext) -> Dict[str, Any]:
        """Validate and execute a command with full security checks"""
        start_time = time.time()
        
        # Check if source is blocked
        if self.threat_detector.is_source_blocked(context.user_id):
            return {
                'success': False,
                'error': 'Source is blocked due to security threats',
                'blocked': True
            }
        
        # Validate command
        is_valid, error_msg, security_info = self.command_validator.validate_command(command)
        if not is_valid:
            self.audit_logger.log_command_execution(
                command=command,
                result=f"Blocked: {error_msg}",
                user_id=context.user_id,
                risk_level=security_info.get('risk_level', 'high'),
                warnings=security_info.get('warnings', []),
                success=False,
                error_message=error_msg
            )
            return {
                'success': False,
                'error': error_msg,
                'security_info': security_info
            }
        
        # Check permissions
        if not self.permission_manager.check_permission(context.session_id, Permission.EXECUTE_COMMANDS):
            self.audit_logger.log_command_execution(
                command=command,
                result="Permission denied",
                user_id=context.user_id,
                risk_level="medium",
                success=False,
                error_message="Insufficient permissions"
            )
            return {
                'success': False,
                'error': 'Insufficient permissions to execute commands'
            }
        
        # Check for dangerous commands
        if security_info.get('requires_admin', False):
            if not self.permission_manager.check_permission(context.session_id, Permission.EXECUTE_DANGEROUS_COMMANDS):
                self.audit_logger.log_command_execution(
                    command=command,
                    result="Permission denied for dangerous command",
                    user_id=context.user_id,
                    risk_level="high",
                    success=False,
                    error_message="Insufficient permissions for dangerous command"
                )
                return {
                    'success': False,
                    'error': 'Insufficient permissions for dangerous command'
                }
        
        # Check for threats
        threats = self.threat_detector.check_command(command, context.user_id)
        if threats:
            # Log threats
            for threat in threats:
                self.audit_logger.log_security_event(
                    event_type=threat.threat_type,
                    description=threat.description,
                    user_id=context.user_id,
                    risk_level=threat.risk_level,
                    details=threat.details
                )
            
            # Block if any critical threats
            critical_threats = [t for t in threats if t.risk_level == "critical"]
            if critical_threats:
                return {
                    'success': False,
                    'error': 'Command blocked due to security threats',
                    'threats': [t.threat_type for t in threats]
                }
        
        # Execute command (this would be implemented by the calling system)
        # For now, we'll just log the command
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Record command for undo functionality
        undo_operation_id = self.undo_manager.record_command_execution(
            command=command,
            result="Command validated successfully",
            user_id=context.user_id,
            session_id=context.session_id
        )
        
        self.audit_logger.log_command_execution(
            command=command,
            result="Command validated successfully",
            user_id=context.user_id,
            risk_level=security_info.get('risk_level', 'low'),
            warnings=security_info.get('warnings', []),
            duration_ms=duration_ms,
            success=True
        )
        
        return {
            'success': True,
            'command': command,
            'security_info': security_info,
            'threats': [t.threat_type for t in threats] if threats else [],
            'duration_ms': duration_ms,
            'undo_operation_id': undo_operation_id
        }
    
    def validate_file_operation(self, operation: str, file_path: str, context: SecurityContext) -> Dict[str, Any]:
        """Validate a file operation"""
        # Check permissions
        if operation in ['read']:
            permission = Permission.READ_FILES
        elif operation in ['write', 'create', 'modify']:
            permission = Permission.WRITE_FILES
        elif operation in ['delete', 'remove']:
            permission = Permission.DELETE_FILES
        else:
            return {
                'success': False,
                'error': f'Unknown file operation: {operation}'
            }
        
        if not self.permission_manager.check_permission(context.session_id, permission):
            return {
                'success': False,
                'error': f'Insufficient permissions for {operation} operation'
            }
        
        # Check for threats
        threats = self.threat_detector.check_file_operation(operation, file_path, context.user_id)
        if threats:
            for threat in threats:
                self.audit_logger.log_security_event(
                    event_type=threat.threat_type,
                    description=threat.description,
                    user_id=context.user_id,
                    risk_level=threat.risk_level,
                    details=threat.details
                )
            
            critical_threats = [t for t in threats if t.risk_level == "critical"]
            if critical_threats:
                return {
                    'success': False,
                    'error': 'File operation blocked due to security threats',
                    'threats': [t.threat_type for t in threats]
                }
        
        # Log file operation
        self.audit_logger.log_file_operation(
            operation=operation,
            file_path=file_path,
            user_id=context.user_id,
            success=True
        )
        
        return {
            'success': True,
            'operation': operation,
            'file_path': file_path,
            'threats': [t.threat_type for t in threats] if threats else []
        }
    
    def validate_network_operation(self, url: str, context: SecurityContext) -> Dict[str, Any]:
        """Validate a network operation"""
        # Check permissions
        if not self.permission_manager.check_permission(context.session_id, Permission.NETWORK_ACCESS):
            return {
                'success': False,
                'error': 'Insufficient permissions for network access'
            }
        
        # Check for threats
        threats = self.threat_detector.check_network_operation(url, context.user_id)
        if threats:
            for threat in threats:
                self.audit_logger.log_security_event(
                    event_type=threat.threat_type,
                    description=threat.description,
                    user_id=context.user_id,
                    risk_level=threat.risk_level,
                    details=threat.details
                )
            
            critical_threats = [t for t in threats if t.risk_level == "critical"]
            if critical_threats:
                return {
                    'success': False,
                    'error': 'Network operation blocked due to security threats',
                    'threats': [t.threat_type for t in threats]
                }
        
        # Log network operation
        self.audit_logger.log_network_operation(
            operation="access",
            url=url,
            user_id=context.user_id,
            success=True
        )
        
        return {
            'success': True,
            'url': url,
            'threats': [t.threat_type for t in threats] if threats else []
        }
    
    def create_user_session(self, user_id: str, session_id: str, 
                           ip_address: Optional[str] = None,
                           user_agent: Optional[str] = None) -> Dict[str, Any]:
        """Create a new user session"""
        success = self.permission_manager.create_session(
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if success:
            self.audit_logger.log_authentication_event(
                event_type="login",
                user_id=user_id,
                success=True,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            return {
                'success': True,
                'session_id': session_id,
                'user_id': user_id
            }
        else:
            self.audit_logger.log_authentication_event(
                event_type="login_failed",
                user_id=user_id,
                success=False,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            return {
                'success': False,
                'error': 'Failed to create session'
            }
    
    def end_user_session(self, session_id: str) -> Dict[str, Any]:
        """End a user session"""
        session_info = self.permission_manager.get_session_info(session_id)
        if session_info:
            user_id = session_info['user_id']
            success = self.permission_manager.end_session(session_id)
            
            if success:
                self.audit_logger.log_authentication_event(
                    event_type="logout",
                    user_id=user_id,
                    success=True
                )
                
                return {
                    'success': True,
                    'session_id': session_id
                }
        
        return {
            'success': False,
            'error': 'Session not found or already ended'
        }
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get comprehensive security status"""
        return {
            'security_config': {
                'security_level': self.security_config.security_level.value,
                'permission_level': self.security_config.permission_level.value
            },
            'threat_detection': self.threat_detector.get_security_status(),
            'permissions': self.permission_manager.get_permission_summary(),
            'encryption': self.encryption_manager.get_encryption_status(),
            'audit': {
                'enabled': self.security_config.audit_settings.enabled,
                'log_file': self.security_config.audit_settings.log_file
            }
        }
    
    def get_security_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get security summary for the specified time period"""
        return {
            'audit_summary': self.audit_logger.get_security_summary(hours),
            'threat_summary': self.threat_detector.get_threat_summary(hours),
            'permission_summary': self.permission_manager.get_permission_summary(),
            'active_sessions': len(self.permission_manager.list_active_sessions()),
            'blocked_sources': len(self.threat_detector.blocked_sources)
        }
    
    def undo_last_operation(self, user_id: str = "system") -> Dict[str, Any]:
        """Undo the last operation for a user"""
        operations = self.undo_manager.list_undoable_operations(
            hours=24, user_id=user_id
        )
        
        if not operations:
            return {
                'success': False,
                'error': 'No operations found to undo'
            }
        
        # Get the most recent operation
        latest_operation = operations[0]
        operation_id = latest_operation['operation_id']
        
        return self.undo_operation(operation_id)
    
    def undo_operation(self, operation_id: str) -> Dict[str, Any]:
        """Undo a specific operation"""
        result = self.undo_manager.undo_operation(operation_id)
        
        # Log the undo attempt
        if result['success']:
            self.audit_logger.log_security_event(
                event_type="undo_operation",
                description=f"Undo operation: {operation_id}",
                user_id="system",
                risk_level="medium",
                details={'operation_id': operation_id, 'result': result}
            )
        else:
            self.audit_logger.log_security_event(
                event_type="undo_failed",
                description=f"Failed to undo operation: {operation_id}",
                user_id="system",
                risk_level="high",
                details={'operation_id': operation_id, 'error': result.get('error')}
            )
        
        return result
    
    def list_undoable_operations(self, 
                                hours: int = 24,
                                user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List operations that can be undone"""
        return self.undo_manager.list_undoable_operations(hours=hours, user_id=user_id)
    
    def get_undo_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of undo operations"""
        return self.undo_manager.get_undo_summary(hours=hours)
    
    def cleanup(self) -> None:
        """Clean up security resources"""
        # Stop threat detection
        self.threat_detector.stop_monitoring()
        
        # Clean up encryption
        self.encryption_manager.cleanup()
        
        # Stop cleanup thread
        if self.cleanup_thread.is_alive():
            # This is a daemon thread, so it will be cleaned up automatically
            pass 