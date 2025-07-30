"""
Permission Manager

This module provides role-based access control and permission management
for the Overseer system, ensuring users can only perform authorized actions.
"""

import os
import json
import time
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
from .security_config import SecurityConfig, PermissionLevel

class Permission(Enum):
    """Available permissions"""
    READ_FILES = "read_files"
    WRITE_FILES = "write_files"
    DELETE_FILES = "delete_files"
    EXECUTE_COMMANDS = "execute_commands"
    EXECUTE_DANGEROUS_COMMANDS = "execute_dangerous_commands"
    ACCESS_SYSTEM_CONFIG = "access_system_config"
    MODIFY_SYSTEM_CONFIG = "modify_system_config"
    NETWORK_ACCESS = "network_access"
    ADMIN_OPERATIONS = "admin_operations"
    VIEW_LOGS = "view_logs"
    MODIFY_SECURITY = "modify_security"

@dataclass
class UserPermissions:
    """User permissions configuration"""
    user_id: str
    permission_level: PermissionLevel
    permissions: Set[Permission] = field(default_factory=set)
    created_at: float = field(default_factory=time.time)
    last_modified: float = field(default_factory=time.time)
    is_active: bool = True
    session_timeout: int = 3600  # 1 hour in seconds

@dataclass
class Session:
    """User session information"""
    session_id: str
    user_id: str
    created_at: float
    last_activity: float
    permissions: Set[Permission]
    session_timeout: int = 3600  # 1 hour in seconds
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class PermissionManager:
    """Manages user permissions and access control"""
    
    def __init__(self, security_config: SecurityConfig):
        self.security_config = security_config
        self.users: Dict[str, UserPermissions] = {}
        self.active_sessions: Dict[str, Session] = {}
        self.permission_file = os.path.expanduser("~/.overseer/permissions.json")
        
        # Initialize default permissions
        self._init_default_permissions()
        self._load_permissions()
    
    def _init_default_permissions(self) -> None:
        """Initialize default permission mappings"""
        self.default_permissions = {
            PermissionLevel.READ_ONLY: {
                Permission.READ_FILES,
                Permission.VIEW_LOGS
            },
            PermissionLevel.LIMITED: {
                Permission.READ_FILES,
                Permission.WRITE_FILES,
                Permission.EXECUTE_COMMANDS,
                Permission.NETWORK_ACCESS,
                Permission.VIEW_LOGS
            },
            PermissionLevel.STANDARD: {
                Permission.READ_FILES,
                Permission.WRITE_FILES,
                Permission.DELETE_FILES,
                Permission.EXECUTE_COMMANDS,
                Permission.NETWORK_ACCESS,
                Permission.VIEW_LOGS
            },
            PermissionLevel.ADMIN: {
                Permission.READ_FILES,
                Permission.WRITE_FILES,
                Permission.DELETE_FILES,
                Permission.EXECUTE_COMMANDS,
                Permission.EXECUTE_DANGEROUS_COMMANDS,
                Permission.ACCESS_SYSTEM_CONFIG,
                Permission.MODIFY_SYSTEM_CONFIG,
                Permission.NETWORK_ACCESS,
                Permission.ADMIN_OPERATIONS,
                Permission.VIEW_LOGS,
                Permission.MODIFY_SECURITY
            }
        }
    
    def _load_permissions(self) -> None:
        """Load user permissions from file"""
        try:
            if os.path.exists(self.permission_file):
                with open(self.permission_file, 'r') as f:
                    data = json.load(f)
                    
                    for user_data in data.get('users', []):
                        user = UserPermissions(
                            user_id=user_data['user_id'],
                            permission_level=PermissionLevel(user_data['permission_level']),
                            permissions=set(Permission(p) for p in user_data.get('permissions', [])),
                            created_at=user_data.get('created_at', time.time()),
                            last_modified=user_data.get('last_modified', time.time()),
                            is_active=user_data.get('is_active', True),
                            session_timeout=user_data.get('session_timeout', 3600)
                        )
                        self.users[user.user_id] = user
                        
        except Exception as e:
            print(f"Warning: Could not load permissions: {e}")
    
    def _save_permissions(self) -> None:
        """Save user permissions to file"""
        try:
            os.makedirs(os.path.dirname(self.permission_file), exist_ok=True)
            
            data = {
                'users': [
                    {
                        'user_id': user.user_id,
                        'permission_level': user.permission_level.value,
                        'permissions': [p.value for p in user.permissions],
                        'created_at': user.created_at,
                        'last_modified': user.last_modified,
                        'is_active': user.is_active,
                        'session_timeout': user.session_timeout
                    }
                    for user in self.users.values()
                ]
            }
            
            with open(self.permission_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Could not save permissions: {e}")
    
    def create_user(self, user_id: str, permission_level: PermissionLevel) -> bool:
        """Create a new user with specified permission level"""
        if user_id in self.users:
            return False
        
        user = UserPermissions(
            user_id=user_id,
            permission_level=permission_level,
            permissions=self.default_permissions.get(permission_level, set())
        )
        
        self.users[user_id] = user
        self._save_permissions()
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        if user_id not in self.users:
            return False
        
        # Remove user from active sessions
        sessions_to_remove = [
            session_id for session_id, session in self.active_sessions.items()
            if session.user_id == user_id
        ]
        for session_id in sessions_to_remove:
            del self.active_sessions[session_id]
        
        del self.users[user_id]
        self._save_permissions()
        return True
    
    def update_user_permissions(self, user_id: str, permissions: Set[Permission]) -> bool:
        """Update user permissions"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        user.permissions = permissions
        user.last_modified = time.time()
        
        self._save_permissions()
        return True
    
    def create_session(self, user_id: str, session_id: str, 
                      ip_address: Optional[str] = None,
                      user_agent: Optional[str] = None) -> bool:
        """Create a new user session"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        if not user.is_active:
            return False
        
        session = Session(
            session_id=session_id,
            user_id=user_id,
            created_at=time.time(),
            last_activity=time.time(),
            permissions=user.permissions.copy(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.active_sessions[session_id] = session
        return True
    
    def validate_session(self, session_id: str) -> bool:
        """Validate if a session is still active"""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        current_time = time.time()
        
        # Check session timeout
        if current_time - session.last_activity > session.session_timeout:
            del self.active_sessions[session_id]
            return False
        
        # Update last activity
        session.last_activity = current_time
        return True
    
    def end_session(self, session_id: str) -> bool:
        """End a user session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            return True
        return False
    
    def check_permission(self, session_id: str, permission: Permission) -> bool:
        """Check if a session has a specific permission"""
        if not self.validate_session(session_id):
            return False
        
        session = self.active_sessions[session_id]
        return permission in session.permissions
    
    def check_multiple_permissions(self, session_id: str, permissions: Set[Permission]) -> bool:
        """Check if a session has multiple permissions"""
        if not self.validate_session(session_id):
            return False
        
        session = self.active_sessions[session_id]
        return permissions.issubset(session.permissions)
    
    def get_user_permissions(self, user_id: str) -> Optional[Set[Permission]]:
        """Get permissions for a user"""
        if user_id not in self.users:
            return None
        
        return self.users[user_id].permissions.copy()
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a session"""
        if not self.validate_session(session_id):
            return None
        
        session = self.active_sessions[session_id]
        return {
            'session_id': session.session_id,
            'user_id': session.user_id,
            'created_at': session.created_at,
            'last_activity': session.last_activity,
            'permissions': [p.value for p in session.permissions],
            'ip_address': session.ip_address,
            'user_agent': session.user_agent
        }
    
    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions"""
        active_sessions = []
        current_time = time.time()
        
        # Clean up expired sessions
        expired_sessions = []
        for session_id, session in self.active_sessions.items():
            if current_time - session.last_activity > session.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
        
        # Return active sessions
        for session_id, session in self.active_sessions.items():
            active_sessions.append(self.get_session_info(session_id))
        
        return active_sessions
    
    def list_users(self) -> List[Dict[str, Any]]:
        """List all users"""
        return [
            {
                'user_id': user.user_id,
                'permission_level': user.permission_level.value,
                'permissions': [p.value for p in user.permissions],
                'created_at': user.created_at,
                'last_modified': user.last_modified,
                'is_active': user.is_active,
                'session_timeout': user.session_timeout
            }
            for user in self.users.values()
        ]
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        user.is_active = False
        user.last_modified = time.time()
        
        # End all active sessions for this user
        sessions_to_end = [
            session_id for session_id, session in self.active_sessions.items()
            if session.user_id == user_id
        ]
        for session_id in sessions_to_end:
            del self.active_sessions[session_id]
        
        self._save_permissions()
        return True
    
    def activate_user(self, user_id: str) -> bool:
        """Activate a user"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        user.is_active = True
        user.last_modified = time.time()
        
        self._save_permissions()
        return True
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and return count of removed sessions"""
        current_time = time.time()
        expired_count = 0
        
        expired_sessions = []
        for session_id, session in self.active_sessions.items():
            if current_time - session.last_activity > session.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
            expired_count += 1
        
        return expired_count
    
    def get_permission_summary(self) -> Dict[str, Any]:
        """Get summary of permission system"""
        return {
            'total_users': len(self.users),
            'active_users': len([u for u in self.users.values() if u.is_active]),
            'active_sessions': len(self.active_sessions),
            'permission_levels': {
                level.value: len([u for u in self.users.values() if u.permission_level == level])
                for level in PermissionLevel
            }
        } 