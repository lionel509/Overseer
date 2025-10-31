# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in Overseer, please report it by emailing the maintainers directly. Please do not create public GitHub issues for security vulnerabilities.

## Security Best Practices

### 1. Environment Variables

Always use environment variables for sensitive data:

```bash
# Required for Gemini API
export GEMINI_API_KEY=your_api_key_here

# Required for encrypted database
export OVERSEER_DB_KEY=your_db_key_here

# For Kaggle integration
export KAGGLE_USERNAME=your_username
export KAGGLE_KEY=your_key

# For Hugging Face models
export HF_TOKEN=your_token
```

**Never commit `.env` files to version control!**

### 2. CORS Configuration

For production deployments, configure allowed origins:

```bash
# Set allowed origins (comma-separated)
export OVERSEER_ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

The default allows only `localhost:5173` and `localhost:3000` for development.

### 3. File Permissions

The application automatically sets secure file permissions:

- Encryption keys: `0o600` (owner read/write only)
- Config files: `0o600` when secure mode is enabled
- Database files: `0o600` recommended

### 4. API Security

#### Rate Limiting
Consider implementing rate limiting for production:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

#### Authentication
For production use, implement authentication:

```python
from fastapi import Depends, HTTPException, Header

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != os.environ.get("OVERSEER_API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key
```

### 5. Database Security

- Always use parameterized queries (already implemented)
- Enable encryption with `OVERSEER_DB_KEY`
- Restrict database file permissions
- Regular backups

### 6. Command Execution

The application includes multiple security layers:

- Command validation
- Sandbox execution modes
- Permission management
- Audit logging
- Threat detection

**Always review commands before execution in production!**

### 7. Path Traversal Protection

File operations are protected against path traversal attacks:

- All paths are normalized to absolute paths
- Access to system directories is restricted
- Path validation ensures operations stay within allowed directories

### 8. Input Validation

- File size limits prevent DoS attacks (10MB default for content search)
- Query patterns are sanitized
- User input is validated before processing

### 9. Secure Configuration

Enable secure configuration mode:

```python
from backend.cli.security import SecurityConfig, SecurityLevel

config = SecurityConfig()
config.security_level = SecurityLevel.HIGH
config.enable_encryption = True
```

## Security Features

### Built-in Security Components

1. **Command Validator**: Validates commands before execution
2. **Audit Logger**: Comprehensive logging of security events
3. **Threat Detector**: Real-time threat detection and blocking
4. **Encryption Manager**: Handles sensitive data encryption
5. **Permission Manager**: Granular permission control
6. **Sandbox Execution**: Multiple isolation levels

### Security Levels

- **LOW**: Minimal restrictions (development only)
- **MEDIUM**: Balanced security (default)
- **HIGH**: Maximum security (production recommended)

## Production Deployment Checklist

- [ ] Set strong `OVERSEER_DB_KEY` using secrets manager
- [ ] Configure `OVERSEER_ALLOWED_ORIGINS` for your domain
- [ ] Enable HTTPS/TLS for all API endpoints
- [ ] Implement API authentication
- [ ] Enable rate limiting
- [ ] Set up audit log monitoring
- [ ] Use secure file permissions (0o600)
- [ ] Regular security updates
- [ ] Monitor security logs
- [ ] Backup encryption keys securely

## Dependency Security

Regularly update dependencies to patch vulnerabilities:

```bash
pip install --upgrade -r requirements.txt
npm audit fix  # For desktop app
```

## Security Monitoring

Review audit logs regularly:

```bash
# Check security summary
overseer --security-summary --hours 24

# View audit logs
cat ~/.overseer/logs/audit.log
```

## Incident Response

If a security incident occurs:

1. Immediately revoke compromised credentials
2. Review audit logs for unauthorized access
3. Check for compromised files
4. Update all API keys and tokens
5. Notify affected users if applicable

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

## Version History

- v1.0.0 (2024-10-31): Initial security policy
  - CORS restrictions
  - File permission hardening
  - Path traversal protection
  - File size limits
