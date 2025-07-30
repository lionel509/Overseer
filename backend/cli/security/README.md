# Overseer Security System

## Overview

The Overseer Security System provides comprehensive protection for the Overseer CLI, implementing multiple layers of security to ensure safe operation in system administration tasks.

## 🔒 Security Features

### 1. Command Validation & Sanitization
- **Pattern-based validation**: Detects dangerous command patterns
- **Injection prevention**: Blocks command injection attempts
- **Path traversal protection**: Prevents directory traversal attacks
- **Argument validation**: Validates command arguments for security
- **Whitelist/Blacklist**: Configurable command allow/deny lists

### 7. Undo System
- **Command undo**: Reverse any command execution
- **File operation undo**: Restore deleted or modified files
- **Directory operation undo**: Restore deleted directories
- **Permission undo**: Restore original file permissions
- **Configuration undo**: Reverse configuration changes
- **Automatic backups**: Creates backups before destructive operations
- **Operation history**: Complete audit trail of all operations

### 2. Threat Detection & Monitoring
- **Real-time monitoring**: Continuous threat detection
- **Pattern recognition**: Identifies suspicious command patterns
- **Rate limiting**: Prevents rapid-fire command execution
- **Anomaly detection**: Detects unusual system behavior
- **Automatic blocking**: Blocks sources with critical threats

### 3. Audit Logging
- **Comprehensive logging**: All activities are logged
- **Sensitive data protection**: Automatically redacts sensitive information
- **Retention management**: Configurable log retention policies
- **Security event tracking**: Special tracking for security events
- **Performance monitoring**: Tracks command execution times

### 4. Permission Management
- **Role-based access control**: Different permission levels
- **Session management**: Secure session handling
- **Permission validation**: Checks permissions before operations
- **User management**: Create, modify, and delete users
- **Session timeout**: Automatic session expiration

### 5. Data Encryption
- **Configuration encryption**: Encrypts sensitive config data
- **Key management**: Secure key generation and rotation
- **Password hashing**: Secure password storage
- **Memory protection**: Clears sensitive data from memory

### 6. Network Security
- **Domain filtering**: Blocks malicious domains
- **SSL enforcement**: Requires HTTPS for network operations
- **Download limits**: Prevents large malicious downloads
- **Rate limiting**: Prevents network abuse

## 🛡️ Security Levels

### SecurityLevel Enum
- **LOW**: Minimal restrictions, basic protection
- **MEDIUM**: Standard protection (default)
- **HIGH**: Strict validation, extensive logging
- **CRITICAL**: Maximum security, minimal allowed operations

### PermissionLevel Enum
- **READ_ONLY**: Can only read files and view logs
- **LIMITED**: Can read/write files and execute basic commands
- **STANDARD**: Full file operations and command execution
- **ADMIN**: Full system access including dangerous commands

## 📁 File Structure

```
security/
├── __init__.py              # Module initialization
├── security_config.py       # Security configuration management
├── command_validator.py     # Command validation and sanitization
├── audit_logger.py         # Comprehensive audit logging
├── threat_detector.py      # Real-time threat detection
├── encryption_manager.py   # Data encryption and key management
├── permission_manager.py   # User permissions and access control
├── security_manager.py     # Unified security interface
├── undo_manager.py         # Undo system for operations
├── test_security.py        # Security system test script
├── test_undo.py            # Undo system test script
└── README.md              # This documentation
```

## 🚀 Quick Start

### Basic Usage

```python
from security.security_manager import SecurityManager, SecurityContext

# Initialize security manager
security_manager = SecurityManager()

# Create security context
context = SecurityContext(
    user_id="user123",
    session_id="session456",
    ip_address="192.168.1.100"
)

# Validate and execute command
result = security_manager.validate_and_execute_command("ls -la", context)
if result['success']:
    print("Command executed successfully")
else:
    print(f"Command blocked: {result['error']}")
```

### Testing the Security System

```bash
cd backend/cli
python security/test_security.py
```

## ⚙️ Configuration

### Security Configuration File
Located at `~/.overseer/security_config.json`

```json
{
  "security_level": "medium",
  "permission_level": "standard",
  "command_policy": {
    "whitelist": ["ls", "cat", "grep", "find"],
    "blacklist": ["rm -rf /", "dd if=/dev/zero"],
    "require_confirmation": ["rm", "mv", "sudo"],
    "require_admin": ["sudo", "apt", "systemctl"]
  },
  "system_protection": {
    "protected_paths": ["/etc", "/var", "/usr"],
    "protected_files": ["/etc/passwd", "/etc/shadow"],
    "backup_before_changes": true
  },
  "network_security": {
    "allowed_domains": ["api.github.com", "pypi.org"],
    "blocked_domains": ["malicious-site.com"],
    "require_ssl": true
  },
  "audit_settings": {
    "enabled": true,
    "log_file": "overseer_audit.log",
    "retention_days": 90
  },
  "encryption_settings": {
    "enabled": true,
    "algorithm": "AES-256-GCM",
    "encrypt_config": true
  }
}
```

## 🔍 Security Monitoring

### Audit Logs
Audit logs are stored in `~/.overseer/overseer_audit.log` and contain:
- Command executions with timestamps
- Security events and threats
- File operations
- Network operations
- Authentication events
- Configuration changes

### Security Status
Get current security status:

```python
status = security_manager.get_security_status()
print(f"Security Level: {status['security_config']['security_level']}")
print(f"Active Sessions: {status['permissions']['active_sessions']}")
print(f"Blocked Sources: {status['threat_detection']['blocked_sources_count']}")
```

### Security Summary
Get security summary for the last 24 hours:

```python
summary = security_manager.get_security_summary(hours=24)
print(f"Total Events: {summary['audit_summary']['total_events']}")
print(f"High Risk Events: {summary['audit_summary']['high_risk_events']}")
print(f"Critical Events: {summary['audit_summary']['critical_events']}")
```

## 🛠️ Advanced Features

### Custom Threat Patterns
Add custom threat detection patterns:

```python
from security.threat_detector import ThreatPattern

# Add custom pattern
custom_pattern = ThreatPattern(
    name="custom_threat",
    pattern=r"custom_pattern",
    risk_level="high",
    description="Custom threat description",
    action="block"
)
```

### Custom Permissions
Create custom permission levels:

```python
from security.permission_manager import Permission

# Check specific permission
has_permission = permission_manager.check_permission(
    session_id, Permission.EXECUTE_COMMANDS
)
```

### Encryption Operations
Encrypt sensitive data:

```python
# Encrypt configuration data
encrypted_config = encryption_manager.encrypt_config_data(config_data)

# Decrypt configuration data
decrypted_config = encryption_manager.decrypt_config_data(encrypted_config)
```

## 🚨 Threat Response

### Automatic Responses
- **Critical threats**: Immediate source blocking
- **High risk threats**: Enhanced logging and monitoring
- **Medium risk threats**: User notification and confirmation
- **Low risk threats**: Standard logging

### Manual Responses
- **Unblock sources**: `threat_detector.unblock_source(source_id)`
- **View threats**: `threat_detector.get_threat_summary(hours=24)`
- **Clean logs**: `audit_logger.cleanup_old_logs()`

## 🔧 Integration with Overseer CLI

The security system is automatically integrated into the Overseer CLI:

1. **Command validation**: All commands are validated before execution
2. **Threat detection**: Real-time monitoring of all operations
3. **Audit logging**: Comprehensive logging of all activities
4. **Permission checking**: Role-based access control
5. **Encryption**: Automatic encryption of sensitive data

### Enhanced Command Execution
The `run_command_with_sandbox` function now includes:
- Security validation before execution
- Threat detection and blocking
- Comprehensive audit logging
- Permission checking
- Automatic cleanup

## 📊 Security Metrics

### Key Performance Indicators
- **Command success rate**: Percentage of commands executed successfully
- **Threat detection rate**: Number of threats detected and blocked
- **Audit log size**: Volume of security events logged
- **Session duration**: Average session length and timeout compliance
- **Permission violations**: Number of permission denied events

### Monitoring Dashboard
The security system provides real-time monitoring:
- Active sessions count
- Blocked sources list
- Recent security events
- System health status
- Performance metrics

## 🛡️ Best Practices

### Configuration
1. **Start with MEDIUM security level** for most environments
2. **Use HIGH security level** for production systems
3. **Configure whitelists** for restricted environments
4. **Enable encryption** for sensitive data
5. **Set appropriate retention** for audit logs

### Monitoring
1. **Regular log review**: Check audit logs weekly
2. **Threat analysis**: Review threat summaries monthly
3. **Performance monitoring**: Track system impact
4. **User management**: Regular permission reviews
5. **Key rotation**: Periodic encryption key updates

### Maintenance
1. **Log cleanup**: Regular audit log maintenance
2. **Session cleanup**: Automatic expired session removal
3. **Threat pattern updates**: Keep threat patterns current
4. **Configuration backups**: Regular security config backups
5. **System updates**: Keep security dependencies updated

## 🔐 Security Compliance

### Data Protection
- **Local processing**: All security operations run locally
- **Encrypted storage**: Sensitive data encrypted at rest
- **Memory protection**: Sensitive data cleared from memory
- **No telemetry**: No external data transmission

### Privacy
- **User consent**: Clear consent for data collection
- **Data minimization**: Only collect necessary information
- **Retention policies**: Automatic data cleanup
- **Anonymization**: PII removal from logs

## 🚀 Future Enhancements

### Planned Features
- **Machine learning threat detection**: AI-powered threat recognition
- **Behavioral analysis**: User behavior pattern analysis
- **Integration with SIEM**: Security information and event management
- **Advanced encryption**: Post-quantum cryptography support
- **Zero-trust architecture**: Enhanced access control

### Extensibility
The security system is designed for easy extension:
- **Plugin architecture**: Add custom security modules
- **API integration**: Connect to external security services
- **Custom validators**: Implement custom validation rules
- **Event handlers**: Custom threat response actions

## 📞 Support

For security-related issues or questions:
- **Documentation**: Check this README and inline code comments
- **Testing**: Use the provided test script
- **Configuration**: Review the security configuration file
- **Logs**: Check audit logs for detailed information

## 🔄 Version History

### v1.0.0 - Initial Release
- Basic command validation
- Threat detection patterns
- Audit logging system
- Permission management
- Data encryption
- Security configuration

---

**Note**: This security system is designed to provide comprehensive protection while maintaining usability. Regular updates and monitoring are recommended for optimal security posture. 