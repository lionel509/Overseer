"""
Threat Detection System

This module provides real-time threat detection and monitoring
for the Overseer system, identifying suspicious patterns and potential attacks.
"""

import re
import time
import threading
from typing import Dict, List, Optional, Set, Callable
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from .security_config import SecurityConfig

@dataclass
class ThreatPattern:
    """Represents a threat pattern to monitor"""
    name: str
    pattern: str
    risk_level: str
    description: str
    action: str = "alert"  # alert, block, log

@dataclass
class ThreatEvent:
    """Represents a detected threat event"""
    timestamp: datetime
    threat_type: str
    description: str
    risk_level: str
    source: str
    details: Dict
    action_taken: str

class ThreatDetector:
    """Real-time threat detection and monitoring system"""
    
    def __init__(self, security_config: SecurityConfig):
        self.security_config = security_config
        self.threat_patterns = self._init_threat_patterns()
        self.rate_limiters = defaultdict(lambda: deque(maxlen=100))
        self.alert_callbacks: List[Callable] = []
        self.blocked_sources: Set[str] = set()
        self.monitoring_active = True
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def _init_threat_patterns(self) -> List[ThreatPattern]:
        """Initialize threat patterns to monitor"""
        patterns = [
            # Command injection patterns
            ThreatPattern(
                name="command_injection",
                pattern=r'[;&|`]\s*\w+',
                risk_level="high",
                description="Potential command injection detected",
                action="block"
            ),
            
            # Path traversal patterns
            ThreatPattern(
                name="path_traversal",
                pattern=r'\.\./|\.\.\\',
                risk_level="high",
                description="Path traversal attempt detected",
                action="block"
            ),
            
            # Privilege escalation patterns
            ThreatPattern(
                name="privilege_escalation",
                pattern=r'sudo\s+.*\s+chmod\s+777|sudo\s+.*\s+chown\s+root',
                risk_level="critical",
                description="Privilege escalation attempt detected",
                action="block"
            ),
            
            # Destructive command patterns
            ThreatPattern(
                name="destructive_command",
                pattern=r'rm\s+-rf\s+/|dd\s+if=/dev/zero|mkfs\s+',
                risk_level="critical",
                description="Destructive system command detected",
                action="block"
            ),
            
            # Network attack patterns
            ThreatPattern(
                name="network_attack",
                pattern=r'wget\s+.*\s+\|\s+bash|curl\s+.*\s+\|\s+bash',
                risk_level="high",
                description="Potential network-based attack detected",
                action="block"
            ),
            
            # SQL injection patterns
            ThreatPattern(
                name="sql_injection",
                pattern=r';\s*(DROP|DELETE|UPDATE|INSERT)\s+',
                risk_level="high",
                description="SQL injection attempt detected",
                action="block"
            ),
            
            # Suspicious file operations
            ThreatPattern(
                name="suspicious_file_op",
                pattern=r'chmod\s+777|chown\s+root',
                risk_level="medium",
                description="Suspicious file permission change",
                action="alert"
            ),
            
            # Rapid command execution
            ThreatPattern(
                name="rapid_execution",
                pattern=r'.*',  # Will be checked by rate limiting
                risk_level="medium",
                description="Rapid command execution detected",
                action="alert"
            ),
            
            # Unusual command patterns
            ThreatPattern(
                name="unusual_command",
                pattern=r'(systemctl|service)\s+(stop|disable)',
                risk_level="high",
                description="System service manipulation detected",
                action="alert"
            ),
        ]
        return patterns
    
    def add_alert_callback(self, callback: Callable[[ThreatEvent], None]) -> None:
        """Add a callback function to be called when threats are detected"""
        self.alert_callbacks.append(callback)
    
    def check_command(self, command: str, user_id: str = "system") -> List[ThreatEvent]:
        """Check a command for potential threats"""
        threats = []
        
        # Check against threat patterns
        for pattern in self.threat_patterns:
            if re.search(pattern.pattern, command, re.IGNORECASE):
                threat = ThreatEvent(
                    timestamp=datetime.utcnow(),
                    threat_type=pattern.name,
                    description=pattern.description,
                    risk_level=pattern.risk_level,
                    source=user_id,
                    details={'command': command, 'pattern': pattern.pattern},
                    action_taken=pattern.action
                )
                threats.append(threat)
                
                # Take action based on pattern
                if pattern.action == "block":
                    self._block_source(user_id)
                elif pattern.action == "alert":
                    self._trigger_alert(threat)
        
        # Check rate limiting
        rate_limit_threat = self._check_rate_limiting(user_id, command)
        if rate_limit_threat:
            threats.append(rate_limit_threat)
        
        # Check for unusual patterns
        unusual_threat = self._check_unusual_patterns(command, user_id)
        if unusual_threat:
            threats.append(unusual_threat)
        
        return threats
    
    def check_file_operation(self, operation: str, file_path: str, user_id: str = "system") -> List[ThreatEvent]:
        """Check file operations for potential threats"""
        threats = []
        
        # Check for protected file access
        if self.security_config.is_file_protected(file_path):
            threat = ThreatEvent(
                timestamp=datetime.utcnow(),
                threat_type="protected_file_access",
                description=f"Attempt to access protected file: {file_path}",
                risk_level="high",
                source=user_id,
                details={'operation': operation, 'file_path': file_path},
                action_taken="alert"
            )
            threats.append(threat)
        
        # Check for path traversal
        if '..' in file_path:
            threat = ThreatEvent(
                timestamp=datetime.utcnow(),
                threat_type="path_traversal",
                description=f"Path traversal attempt: {file_path}",
                risk_level="high",
                source=user_id,
                details={'operation': operation, 'file_path': file_path},
                action_taken="block"
            )
            threats.append(threat)
        
        return threats
    
    def check_network_operation(self, url: str, user_id: str = "system") -> List[ThreatEvent]:
        """Check network operations for potential threats"""
        threats = []
        
        # Check for blocked domains
        from urllib.parse import urlparse
        parsed = urlparse(url)
        
        if parsed.netloc in self.security_config.network_security.blocked_domains:
            threat = ThreatEvent(
                timestamp=datetime.utcnow(),
                threat_type="blocked_domain",
                description=f"Attempt to access blocked domain: {parsed.netloc}",
                risk_level="medium",
                source=user_id,
                details={'url': url, 'domain': parsed.netloc},
                action_taken="block"
            )
            threats.append(threat)
        
        # Check for non-HTTPS connections if required
        if self.security_config.network_security.require_ssl:
            if parsed.scheme not in ['https', 'wss']:
                threat = ThreatEvent(
                    timestamp=datetime.utcnow(),
                    threat_type="insecure_connection",
                    description=f"Insecure connection attempt: {url}",
                    risk_level="medium",
                    source=user_id,
                    details={'url': url, 'scheme': parsed.scheme},
                    action_taken="alert"
                )
                threats.append(threat)
        
        return threats
    
    def _check_rate_limiting(self, user_id: str, command: str) -> Optional[ThreatEvent]:
        """Check for rapid command execution"""
        current_time = time.time()
        user_commands = self.rate_limiters[user_id]
        
        # Add current command
        user_commands.append(current_time)
        
        # Check if too many commands in short time
        if len(user_commands) >= 10:
            time_span = current_time - user_commands[0]
            if time_span < 60:  # More than 10 commands in 1 minute
                return ThreatEvent(
                    timestamp=datetime.utcnow(),
                    threat_type="rapid_execution",
                    description=f"Rapid command execution by {user_id}",
                    risk_level="medium",
                    source=user_id,
                    details={'command_count': len(user_commands), 'time_span': time_span},
                    action_taken="alert"
                )
        
        return None
    
    def _check_unusual_patterns(self, command: str, user_id: str) -> Optional[ThreatEvent]:
        """Check for unusual command patterns"""
        # Check for commands that are rarely used
        unusual_commands = [
            'mkfs', 'fdisk', 'dd', 'kill -9', 'systemctl stop',
            'service stop', 'useradd', 'userdel', 'passwd'
        ]
        
        for unusual_cmd in unusual_commands:
            if unusual_cmd in command.lower():
                return ThreatEvent(
                    timestamp=datetime.utcnow(),
                    threat_type="unusual_command",
                    description=f"Unusual command detected: {unusual_cmd}",
                    risk_level="medium",
                    source=user_id,
                    details={'command': command, 'unusual_part': unusual_cmd},
                    action_taken="alert"
                )
        
        return None
    
    def _block_source(self, source: str) -> None:
        """Block a source from further operations"""
        self.blocked_sources.add(source)
        
        # Log the blocking action
        threat = ThreatEvent(
            timestamp=datetime.utcnow(),
            threat_type="source_blocked",
            description=f"Source blocked due to security threat: {source}",
            risk_level="high",
            source=source,
            details={'reason': 'security_threat'},
            action_taken="block"
        )
        self._trigger_alert(threat)
    
    def _trigger_alert(self, threat: ThreatEvent) -> None:
        """Trigger alert callbacks for a threat"""
        for callback in self.alert_callbacks:
            try:
                callback(threat)
            except Exception as e:
                print(f"Error in threat alert callback: {e}")
    
    def is_source_blocked(self, source: str) -> bool:
        """Check if a source is blocked"""
        return source in self.blocked_sources
    
    def unblock_source(self, source: str) -> None:
        """Unblock a source"""
        self.blocked_sources.discard(source)
    
    def get_threat_summary(self, hours: int = 24) -> Dict:
        """Get summary of threats detected in the specified time period"""
        # This would typically query a database or log file
        # For now, return a basic structure
        return {
            'total_threats': 0,
            'threats_by_type': {},
            'threats_by_risk_level': {},
            'blocked_sources': list(self.blocked_sources),
            'time_period_hours': hours
        }
    
    def _monitor_loop(self) -> None:
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Perform periodic security checks
                self._periodic_security_checks()
                
                # Sleep for a short interval
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Error in threat monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _periodic_security_checks(self) -> None:
        """Perform periodic security checks"""
        # Check for blocked sources that should be unblocked
        # (implement time-based unblocking if needed)
        
        # Check system resources for anomalies
        # (implement resource monitoring if needed)
        
        # Check for unusual network activity
        # (implement network monitoring if needed)
        
        pass
    
    def stop_monitoring(self) -> None:
        """Stop the monitoring thread"""
        self.monitoring_active = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
    
    def get_security_status(self) -> Dict:
        """Get current security status"""
        return {
            'monitoring_active': self.monitoring_active,
            'blocked_sources_count': len(self.blocked_sources),
            'blocked_sources': list(self.blocked_sources),
            'alert_callbacks_count': len(self.alert_callbacks),
            'threat_patterns_count': len(self.threat_patterns)
        } 