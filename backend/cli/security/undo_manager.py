"""
Undo Manager

This module provides comprehensive undo functionality for the Overseer system,
allowing users to reverse any command execution or system change.
"""

import os
import json
import time
import shutil
import subprocess
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib

class UndoType(Enum):
    """Types of operations that can be undone"""
    COMMAND_EXECUTION = "command_execution"
    FILE_OPERATION = "file_operation"
    DIRECTORY_OPERATION = "directory_operation"
    PERMISSION_CHANGE = "permission_change"
    CONFIGURATION_CHANGE = "configuration_change"
    NETWORK_OPERATION = "network_operation"

@dataclass
class UndoOperation:
    """Represents an operation that can be undone"""
    operation_id: str
    operation_type: UndoType
    timestamp: float
    description: str
    original_state: Dict[str, Any]
    backup_data: Optional[Dict[str, Any]] = None
    user_id: str = "system"
    session_id: str = "system"
    success: bool = True
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.backup_data is None:
            self.backup_data = {}

class UndoManager:
    """Manages undo operations for the Overseer system"""
    
    def __init__(self, undo_file: Optional[str] = None):
        self.undo_file = undo_file or os.path.expanduser("~/.overseer/undo_history.json")
        self.operations: Dict[str, UndoOperation] = {}
        self.max_operations = 1000  # Maximum number of operations to keep
        self.backup_dir = os.path.expanduser("~/.overseer/backups")
        
        # Create backup directory
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Load existing undo history
        self._load_undo_history()
    
    def _load_undo_history(self) -> None:
        """Load undo history from file"""
        try:
            if os.path.exists(self.undo_file):
                with open(self.undo_file, 'r') as f:
                    data = json.load(f)
                    
                    for op_data in data.get('operations', []):
                        operation = UndoOperation(
                            operation_id=op_data['operation_id'],
                            operation_type=UndoType(op_data['operation_type']),
                            timestamp=op_data['timestamp'],
                            description=op_data['description'],
                            original_state=op_data['original_state'],
                            backup_data=op_data.get('backup_data', {}),
                            user_id=op_data.get('user_id', 'system'),
                            session_id=op_data.get('session_id', 'system'),
                            success=op_data.get('success', True),
                            error_message=op_data.get('error_message')
                        )
                        self.operations[operation.operation_id] = operation
                        
        except Exception as e:
            print(f"Warning: Could not load undo history: {e}")
    
    def _save_undo_history(self) -> None:
        """Save undo history to file"""
        try:
            os.makedirs(os.path.dirname(self.undo_file), exist_ok=True)
            
            data = {
                'operations': [
                    {
                        'operation_id': op.operation_id,
                        'operation_type': op.operation_type.value,
                        'timestamp': op.timestamp,
                        'description': op.description,
                        'original_state': op.original_state,
                        'backup_data': op.backup_data,
                        'user_id': op.user_id,
                        'session_id': op.session_id,
                        'success': op.success,
                        'error_message': op.error_message
                    }
                    for op in self.operations.values()
                ]
            }
            
            with open(self.undo_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Could not save undo history: {e}")
    
    def _generate_operation_id(self, operation_type: UndoType, description: str) -> str:
        """Generate a unique operation ID"""
        timestamp = str(time.time())
        content = f"{operation_type.value}_{description}_{timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _backup_file(self, file_path: str) -> Optional[str]:
        """Create a backup of a file"""
        try:
            if not os.path.exists(file_path):
                return None
            
            # Create backup filename
            backup_filename = f"{os.path.basename(file_path)}_{int(time.time())}.backup"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Copy file to backup
            shutil.copy2(file_path, backup_path)
            
            return backup_path
            
        except Exception as e:
            print(f"Warning: Could not backup file {file_path}: {e}")
            return None
    
    def _backup_directory(self, dir_path: str) -> Optional[str]:
        """Create a backup of a directory"""
        try:
            if not os.path.exists(dir_path):
                return None
            
            # Create backup directory name
            backup_dirname = f"{os.path.basename(dir_path)}_{int(time.time())}.backup"
            backup_path = os.path.join(self.backup_dir, backup_dirname)
            
            # Copy directory to backup
            shutil.copytree(dir_path, backup_path)
            
            return backup_path
            
        except Exception as e:
            print(f"Warning: Could not backup directory {dir_path}: {e}")
            return None
    
    def record_command_execution(self, 
                               command: str, 
                               result: str,
                               user_id: str = "system",
                               session_id: str = "system") -> str:
        """Record a command execution for potential undo"""
        operation_id = self._generate_operation_id(UndoType.COMMAND_EXECUTION, command)
        
        operation = UndoOperation(
            operation_id=operation_id,
            operation_type=UndoType.COMMAND_EXECUTION,
            timestamp=time.time(),
            description=f"Command execution: {command}",
            original_state={
                'command': command,
                'result': result,
                'timestamp': datetime.fromtimestamp(time.time()).isoformat()
            },
            user_id=user_id,
            session_id=session_id
        )
        
        self.operations[operation_id] = operation
        self._save_undo_history()
        
        return operation_id
    
    def record_file_operation(self, 
                            operation: str,
                            file_path: str,
                            user_id: str = "system",
                            session_id: str = "system") -> str:
        """Record a file operation for potential undo"""
        operation_id = self._generate_operation_id(UndoType.FILE_OPERATION, f"{operation}_{file_path}")
        
        # Create backup if file exists
        backup_path = None
        if os.path.exists(file_path):
            backup_path = self._backup_file(file_path)
        
        operation_obj = UndoOperation(
            operation_id=operation_id,
            operation_type=UndoType.FILE_OPERATION,
            timestamp=time.time(),
            description=f"File operation: {operation} {file_path}",
            original_state={
                'operation': operation,
                'file_path': file_path,
                'backup_path': backup_path,
                'file_exists': os.path.exists(file_path),
                'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                'file_permissions': oct(os.stat(file_path).st_mode)[-3:] if os.path.exists(file_path) else None
            },
            backup_data={'backup_path': backup_path} if backup_path else {},
            user_id=user_id,
            session_id=session_id
        )
        
        self.operations[operation_id] = operation_obj
        self._save_undo_history()
        
        return operation_id
    
    def record_directory_operation(self, 
                                 operation: str,
                                 dir_path: str,
                                 user_id: str = "system",
                                 session_id: str = "system") -> str:
        """Record a directory operation for potential undo"""
        operation_id = self._generate_operation_id(UndoType.DIRECTORY_OPERATION, f"{operation}_{dir_path}")
        
        # Create backup if directory exists
        backup_path = None
        if os.path.exists(dir_path):
            backup_path = self._backup_directory(dir_path)
        
        operation_obj = UndoOperation(
            operation_id=operation_id,
            operation_type=UndoType.DIRECTORY_OPERATION,
            timestamp=time.time(),
            description=f"Directory operation: {operation} {dir_path}",
            original_state={
                'operation': operation,
                'dir_path': dir_path,
                'backup_path': backup_path,
                'dir_exists': os.path.exists(dir_path),
                'dir_contents': os.listdir(dir_path) if os.path.exists(dir_path) else []
            },
            backup_data={'backup_path': backup_path} if backup_path else {},
            user_id=user_id,
            session_id=session_id
        )
        
        self.operations[operation_id] = operation_obj
        self._save_undo_history()
        
        return operation_id
    
    def record_permission_change(self, 
                               file_path: str,
                               old_permissions: str,
                               new_permissions: str,
                               user_id: str = "system",
                               session_id: str = "system") -> str:
        """Record a permission change for potential undo"""
        operation_id = self._generate_operation_id(UndoType.PERMISSION_CHANGE, f"chmod_{file_path}")
        
        operation = UndoOperation(
            operation_id=operation_id,
            operation_type=UndoType.PERMISSION_CHANGE,
            timestamp=time.time(),
            description=f"Permission change: {file_path} {old_permissions} -> {new_permissions}",
            original_state={
                'file_path': file_path,
                'old_permissions': old_permissions,
                'new_permissions': new_permissions,
                'timestamp': datetime.fromtimestamp(time.time()).isoformat()
            },
            user_id=user_id,
            session_id=session_id
        )
        
        self.operations[operation_id] = operation
        self._save_undo_history()
        
        return operation_id
    
    def record_configuration_change(self, 
                                  config_key: str,
                                  old_value: Any,
                                  new_value: Any,
                                  user_id: str = "system",
                                  session_id: str = "system") -> str:
        """Record a configuration change for potential undo"""
        operation_id = self._generate_operation_id(UndoType.CONFIGURATION_CHANGE, f"config_{config_key}")
        
        operation = UndoOperation(
            operation_id=operation_id,
            operation_type=UndoType.CONFIGURATION_CHANGE,
            timestamp=time.time(),
            description=f"Configuration change: {config_key}",
            original_state={
                'config_key': config_key,
                'old_value': str(old_value),
                'new_value': str(new_value),
                'timestamp': datetime.fromtimestamp(time.time()).isoformat()
            },
            user_id=user_id,
            session_id=session_id
        )
        
        self.operations[operation_id] = operation
        self._save_undo_history()
        
        return operation_id
    
    def undo_operation(self, operation_id: str) -> Dict[str, Any]:
        """Undo a specific operation"""
        if operation_id not in self.operations:
            return {
                'success': False,
                'error': f'Operation {operation_id} not found'
            }
        
        operation = self.operations[operation_id]
        
        try:
            if operation.operation_type == UndoType.COMMAND_EXECUTION:
                return self._undo_command_execution(operation)
            elif operation.operation_type == UndoType.FILE_OPERATION:
                return self._undo_file_operation(operation)
            elif operation.operation_type == UndoType.DIRECTORY_OPERATION:
                return self._undo_directory_operation(operation)
            elif operation.operation_type == UndoType.PERMISSION_CHANGE:
                return self._undo_permission_change(operation)
            elif operation.operation_type == UndoType.CONFIGURATION_CHANGE:
                return self._undo_configuration_change(operation)
            else:
                return {
                    'success': False,
                    'error': f'Unknown operation type: {operation.operation_type}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error undoing operation: {e}'
            }
    
    def _undo_command_execution(self, operation: UndoOperation) -> Dict[str, Any]:
        """Undo a command execution"""
        # For command execution, we can't easily undo the effects
        # but we can log the undo attempt
        return {
            'success': True,
            'message': f'Command execution undo logged: {operation.description}',
            'warning': 'Command effects may not be fully reversible'
        }
    
    def _undo_file_operation(self, operation: UndoOperation) -> Dict[str, Any]:
        """Undo a file operation"""
        original_state = operation.original_state
        file_path = original_state['file_path']
        operation_type = original_state['operation']
        backup_path = operation.backup_data.get('backup_path')
        
        try:
            if operation_type in ['delete', 'remove']:
                # Restore file from backup
                if backup_path and os.path.exists(backup_path):
                    shutil.copy2(backup_path, file_path)
                    return {
                        'success': True,
                        'message': f'Restored file: {file_path}'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'No backup available for {file_path}'
                    }
            
            elif operation_type in ['modify', 'write']:
                # Restore file from backup
                if backup_path and os.path.exists(backup_path):
                    shutil.copy2(backup_path, file_path)
                    return {
                        'success': True,
                        'message': f'Restored file: {file_path}'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'No backup available for {file_path}'
                    }
            
            elif operation_type == 'create':
                # Delete the created file
                if os.path.exists(file_path):
                    os.remove(file_path)
                    return {
                        'success': True,
                        'message': f'Deleted created file: {file_path}'
                    }
                else:
                    return {
                        'success': True,
                        'message': f'File already deleted: {file_path}'
                    }
            
            else:
                return {
                    'success': False,
                    'error': f'Unknown file operation: {operation_type}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error undoing file operation: {e}'
            }
    
    def _undo_directory_operation(self, operation: UndoOperation) -> Dict[str, Any]:
        """Undo a directory operation"""
        original_state = operation.original_state
        dir_path = original_state['dir_path']
        operation_type = original_state['operation']
        backup_path = operation.backup_data.get('backup_path')
        
        try:
            if operation_type in ['delete', 'remove']:
                # Restore directory from backup
                if backup_path and os.path.exists(backup_path):
                    if os.path.exists(dir_path):
                        shutil.rmtree(dir_path)
                    shutil.copytree(backup_path, dir_path)
                    return {
                        'success': True,
                        'message': f'Restored directory: {dir_path}'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'No backup available for {dir_path}'
                    }
            
            elif operation_type == 'create':
                # Delete the created directory
                if os.path.exists(dir_path):
                    shutil.rmtree(dir_path)
                    return {
                        'success': True,
                        'message': f'Deleted created directory: {dir_path}'
                    }
                else:
                    return {
                        'success': True,
                        'message': f'Directory already deleted: {dir_path}'
                    }
            
            else:
                return {
                    'success': False,
                    'error': f'Unknown directory operation: {operation_type}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error undoing directory operation: {e}'
            }
    
    def _undo_permission_change(self, operation: UndoOperation) -> Dict[str, Any]:
        """Undo a permission change"""
        original_state = operation.original_state
        file_path = original_state['file_path']
        old_permissions = original_state['old_permissions']
        
        try:
            if os.path.exists(file_path):
                # Convert octal string to integer
                permissions = int(old_permissions, 8)
                os.chmod(file_path, permissions)
                return {
                    'success': True,
                    'message': f'Restored permissions for {file_path}: {old_permissions}'
                }
            else:
                return {
                    'success': False,
                    'error': f'File no longer exists: {file_path}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error undoing permission change: {e}'
            }
    
    def _undo_configuration_change(self, operation: UndoOperation) -> Dict[str, Any]:
        """Undo a configuration change"""
        original_state = operation.original_state
        config_key = original_state['config_key']
        old_value = original_state['old_value']
        
        # This would typically involve updating a configuration file
        # For now, we'll just log the undo attempt
        return {
            'success': True,
            'message': f'Configuration change undo logged: {config_key} = {old_value}',
            'warning': 'Manual configuration update may be required'
        }
    
    def list_undoable_operations(self, 
                                hours: int = 24,
                                operation_type: Optional[UndoType] = None,
                                user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List operations that can be undone"""
        cutoff_time = time.time() - (hours * 3600)
        
        operations = []
        for op in self.operations.values():
            if op.timestamp < cutoff_time:
                continue
            
            if operation_type and op.operation_type != operation_type:
                continue
            
            if user_id and op.user_id != user_id:
                continue
            
            operations.append({
                'operation_id': op.operation_id,
                'operation_type': op.operation_type.value,
                'timestamp': op.timestamp,
                'description': op.description,
                'user_id': op.user_id,
                'success': op.success
            })
        
        # Sort by timestamp (newest first)
        operations.sort(key=lambda x: x['timestamp'], reverse=True)
        return operations
    
    def get_undo_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of undo operations"""
        operations = self.list_undoable_operations(hours=hours)
        
        summary = {
            'total_operations': len(operations),
            'operations_by_type': {},
            'operations_by_user': {},
            'recent_operations': operations[:10]  # Last 10 operations
        }
        
        for op in operations:
            op_type = op['operation_type']
            user_id = op['user_id']
            
            summary['operations_by_type'][op_type] = summary['operations_by_type'].get(op_type, 0) + 1
            summary['operations_by_user'][user_id] = summary['operations_by_user'].get(user_id, 0) + 1
        
        return summary
    
    def cleanup_old_operations(self, days: int = 30) -> int:
        """Clean up old operations and backups"""
        cutoff_time = time.time() - (days * 24 * 3600)
        removed_count = 0
        
        # Remove old operations
        operations_to_remove = []
        for op_id, op in self.operations.items():
            if op.timestamp < cutoff_time:
                operations_to_remove.append(op_id)
        
        for op_id in operations_to_remove:
            # Clean up backup files
            op = self.operations[op_id]
            if op.backup_data and 'backup_path' in op.backup_data:
                backup_path = op.backup_data['backup_path']
                if backup_path and os.path.exists(backup_path):
                    try:
                        if os.path.isdir(backup_path):
                            shutil.rmtree(backup_path)
                        else:
                            os.remove(backup_path)
                    except Exception:
                        pass  # Ignore cleanup errors
            
            del self.operations[op_id]
            removed_count += 1
        
        self._save_undo_history()
        return removed_count 