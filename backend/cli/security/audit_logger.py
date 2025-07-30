"""
Audit Logging System

This module provides comprehensive audit logging for the Overseer system,
tracking all activities, commands, and security events.
"""

import os
import json
import time
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from .security_config import SecurityConfig
import re

@dataclass
class AuditEvent:
    """Represents an audit event"""
    timestamp: str
    event_type: str
    user_id: str
    session_id: str
    command: Optional[str] = None
    result: Optional[str] = None
    risk_level: str = "low"
    warnings: Optional[List[str]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    duration_ms: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()

class AuditLogger:
    """Comprehensive audit logging system"""
    
    def __init__(self, security_config: SecurityConfig):
        self.security_config = security_config
        self.logger = self._setup_logger()
        self.session_id = self._generate_session_id()
        self.event_buffer = []
        self.max_buffer_size = 100
        
    def _setup_logger(self) -> logging.Logger:
        """Setup audit logger"""
        logger = logging.getLogger('overseer_audit')
        logger.setLevel(logging.INFO)
        
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(self.security_config.audit_settings.log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler(self.security_config.audit_settings.log_file)
        file_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        
        return logger
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        timestamp = str(time.time())
        random_data = os.urandom(16).hex()
        return hashlib.sha256(f"{timestamp}{random_data}".encode()).hexdigest()[:16]
    
    def _sanitize_sensitive_data(self, data: str) -> str:
        """Sanitize sensitive data from logs"""
        if not data:
            return data
        
        sanitized = data
        for field in self.security_config.audit_settings.sensitive_fields:
            # Replace sensitive patterns with [REDACTED]
            pattern = re.compile(rf'{field}[=:]\s*[^\s]+', re.IGNORECASE)
            sanitized = pattern.sub(f'{field}=[REDACTED]', sanitized)
        
        return sanitized
    
    def log_command_execution(self, 
                            command: str, 
                            result: str, 
                            user_id: str = "system",
                            risk_level: str = "low",
                            warnings: Optional[List[str]] = None,
                            duration_ms: Optional[int] = None,
                            success: bool = True,
                            error_message: Optional[str] = None) -> None:
        """Log command execution"""
        event = AuditEvent(
            timestamp=datetime.utcnow().isoformat(),
            event_type="command_execution",
            user_id=user_id,
            session_id=self.session_id,
            command=self._sanitize_sensitive_data(command),
            result=self._sanitize_sensitive_data(result),
            risk_level=risk_level,
            warnings=warnings or [],
            duration_ms=duration_ms,
            success=success,
            error_message=error_message
        )
        
        self._log_event(event)
    
    def log_security_event(self, 
                          event_type: str,
                          description: str,
                          user_id: str = "system",
                          risk_level: str = "medium",
                          details: Optional[Dict[str, Any]] = None) -> None:
        """Log security-related events"""
        event = AuditEvent(
            timestamp=datetime.utcnow().isoformat(),
            event_type=f"security_{event_type}",
            user_id=user_id,
            session_id=self.session_id,
            command=description,
            risk_level=risk_level,
            warnings=details.get('warnings', []) if details else []
        )
        
        self._log_event(event)
    
    def log_file_operation(self, 
                          operation: str,
                          file_path: str,
                          user_id: str = "system",
                          success: bool = True,
                          error_message: Optional[str] = None) -> None:
        """Log file operations"""
        event = AuditEvent(
            timestamp=datetime.utcnow().isoformat(),
            event_type=f"file_{operation}",
            user_id=user_id,
            session_id=self.session_id,
            command=file_path,
            success=success,
            error_message=error_message
        )
        
        self._log_event(event)
    
    def log_network_operation(self, 
                             operation: str,
                             url: str,
                             user_id: str = "system",
                             success: bool = True,
                             error_message: Optional[str] = None) -> None:
        """Log network operations"""
        event = AuditEvent(
            timestamp=datetime.utcnow().isoformat(),
            event_type=f"network_{operation}",
            user_id=user_id,
            session_id=self.session_id,
            command=url,
            success=success,
            error_message=error_message
        )
        
        self._log_event(event)
    
    def log_authentication_event(self, 
                                event_type: str,
                                user_id: str,
                                success: bool = True,
                                ip_address: Optional[str] = None,
                                user_agent: Optional[str] = None) -> None:
        """Log authentication events"""
        event = AuditEvent(
            timestamp=datetime.utcnow().isoformat(),
            event_type=f"auth_{event_type}",
            user_id=user_id,
            session_id=self.session_id,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self._log_event(event)
    
    def log_configuration_change(self, 
                                setting: str,
                                old_value: str,
                                new_value: str,
                                user_id: str = "system") -> None:
        """Log configuration changes"""
        event = AuditEvent(
            timestamp=datetime.utcnow().isoformat(),
            event_type="config_change",
            user_id=user_id,
            session_id=self.session_id,
            command=f"{setting}: {old_value} -> {new_value}",
            risk_level="medium"
        )
        
        self._log_event(event)
    
    def _log_event(self, event: AuditEvent) -> None:
        """Internal method to log an audit event"""
        # Add to buffer
        self.event_buffer.append(event)
        
        # Log to file
        log_entry = {
            'timestamp': event.timestamp,
            'event_type': event.event_type,
            'user_id': event.user_id,
            'session_id': event.session_id,
            'risk_level': event.risk_level,
            'success': event.success
        }
        
        if event.command:
            log_entry['command'] = event.command
        if event.result:
            log_entry['result'] = event.result
        if event.warnings:
            log_entry['warnings'] = event.warnings
        if event.duration_ms:
            log_entry['duration_ms'] = event.duration_ms
        if event.error_message:
            log_entry['error_message'] = event.error_message
        if event.ip_address:
            log_entry['ip_address'] = event.ip_address
        if event.user_agent:
            log_entry['user_agent'] = event.user_agent
        
        self.logger.info(json.dumps(log_entry))
        
        # Flush buffer if it's getting large
        if len(self.event_buffer) >= self.max_buffer_size:
            self._flush_buffer()
    
    def _flush_buffer(self) -> None:
        """Flush the event buffer"""
        # This could be used to send events to external systems
        # For now, we just clear the buffer
        self.event_buffer.clear()
    
    def get_recent_events(self, 
                         event_type: Optional[str] = None,
                         user_id: Optional[str] = None,
                         hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent audit events"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        events = []
        try:
            with open(self.security_config.audit_settings.log_file, 'r') as f:
                for line in f:
                    try:
                        # Parse JSON log entry
                        if line.strip():
                            log_entry = json.loads(line.split(' - ')[-1])
                            
                            # Filter by time
                            event_time = datetime.fromisoformat(log_entry['timestamp'])
                            if event_time < cutoff_time:
                                continue
                            
                            # Filter by event type
                            if event_type and log_entry.get('event_type') != event_type:
                                continue
                            
                            # Filter by user
                            if user_id and log_entry.get('user_id') != user_id:
                                continue
                            
                            events.append(log_entry)
                            
                    except (json.JSONDecodeError, KeyError):
                        continue
                        
        except FileNotFoundError:
            pass
        
        return events
    
    def get_security_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get security summary for the specified time period"""
        events = self.get_recent_events(hours=hours)
        
        summary = {
            'total_events': len(events),
            'successful_events': len([e for e in events if e.get('success', True)]),
            'failed_events': len([e for e in events if not e.get('success', True)]),
            'high_risk_events': len([e for e in events if e.get('risk_level') == 'high']),
            'critical_events': len([e for e in events if e.get('risk_level') == 'critical']),
            'event_types': {},
            'users': {},
            'warnings': []
        }
        
        # Count event types
        for event in events:
            event_type = event.get('event_type', 'unknown')
            summary['event_types'][event_type] = summary['event_types'].get(event_type, 0) + 1
            
            user_id = event.get('user_id', 'unknown')
            summary['users'][user_id] = summary['users'].get(user_id, 0) + 1
            
            # Collect warnings
            if event.get('warnings'):
                summary['warnings'].extend(event['warnings'])
        
        return summary
    
    def cleanup_old_logs(self) -> None:
        """Clean up old log entries based on retention policy"""
        if not self.security_config.audit_settings.enabled:
            return
        
        cutoff_time = datetime.utcnow() - timedelta(days=self.security_config.audit_settings.retention_days)
        temp_file = f"{self.security_config.audit_settings.log_file}.tmp"
        
        try:
            with open(self.security_config.audit_settings.log_file, 'r') as infile, \
                 open(temp_file, 'w') as outfile:
                
                for line in infile:
                    try:
                        # Parse timestamp from log line
                        if line.strip():
                            log_entry = json.loads(line.split(' - ')[-1])
                            event_time = datetime.fromisoformat(log_entry['timestamp'])
                            
                            if event_time >= cutoff_time:
                                outfile.write(line)
                                
                    except (json.JSONDecodeError, KeyError):
                        # Keep lines that can't be parsed
                        outfile.write(line)
            
            # Replace original file with filtered version
            os.replace(temp_file, self.security_config.audit_settings.log_file)
            
        except Exception as e:
            # Clean up temp file if it exists
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise e 