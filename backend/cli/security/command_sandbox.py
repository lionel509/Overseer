"""
Command Sandbox System

This module provides a sandbox environment for safely testing commands
before they are executed in the real system.
"""

import os
import tempfile
import shutil
import subprocess
import time
import json
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

class SandboxMode(Enum):
    """Different sandbox modes for command testing"""
    DRY_RUN = "dry_run"           # Just show what would happen
    SIMULATION = "simulation"      # Simulate the command
    ISOLATED = "isolated"          # Run in isolated environment
    VALIDATION = "validation"      # Validate command structure

@dataclass
class SandboxResult:
    """Result of sandbox command execution"""
    success: bool
    output: str
    error: Optional[str] = None
    warnings: Optional[List[str]] = None
    files_created: Optional[List[str]] = None
    files_modified: Optional[List[str]] = None
    files_deleted: Optional[List[str]] = None
    system_changes: Optional[List[str]] = None
    execution_time: float = 0.0
    risk_level: str = "low"
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.files_created is None:
            self.files_created = []
        if self.files_modified is None:
            self.files_modified = []
        if self.files_deleted is None:
            self.files_deleted = []
        if self.system_changes is None:
            self.system_changes = []

class CommandSandbox:
    """Sandbox environment for safe command testing"""
    
    def __init__(self, mode: SandboxMode = SandboxMode.DRY_RUN):
        self.mode = mode
        self.temp_dir = None
        self.original_cwd = os.getcwd()
        self.file_snapshot = {}
        self.process_snapshot = {}
        
    def __enter__(self):
        """Context manager entry"""
        self._setup_sandbox()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self._cleanup_sandbox()
    
    def _setup_sandbox(self):
        """Set up the sandbox environment"""
        if self.mode == SandboxMode.ISOLATED:
            # Create temporary directory for isolated execution
            self.temp_dir = tempfile.mkdtemp(prefix="overseer_sandbox_")
            os.chdir(self.temp_dir)
            
            # Create a minimal environment
            self._create_minimal_environment()
        
        # Take snapshots for comparison
        self._take_system_snapshot()
    
    def _cleanup_sandbox(self):
        """Clean up the sandbox environment"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except Exception as e:
                print(f"Warning: Could not clean up sandbox: {e}")
        
        # Restore original working directory
        os.chdir(self.original_cwd)
    
    def _create_minimal_environment(self):
        """Create a minimal environment for isolated execution"""
        # Create basic directory structure
        os.makedirs("bin", exist_ok=True)
        os.makedirs("tmp", exist_ok=True)
        os.makedirs("home", exist_ok=True)
        
        # Create mock files for testing
        with open("test_file.txt", "w") as f:
            f.write("This is a test file for sandbox testing\n")
        
        # Create mock executables
        self._create_mock_executables()
    
    def _create_mock_executables(self):
        """Create mock executable scripts for testing"""
        mock_scripts = {
            "ls": "#!/bin/bash\necho 'file1.txt file2.txt dir1/'\n",
            "cat": "#!/bin/bash\necho 'File contents'\n",
            "echo": "#!/bin/bash\necho \"$@\"\n",
            "mkdir": "#!/bin/bash\necho 'Created directory: $1'\n",
            "touch": "#!/bin/bash\necho 'Created file: $1'\n",
            "rm": "#!/bin/bash\necho 'Removed: $1'\n",
            "mv": "#!/bin/bash\necho 'Moved $1 to $2'\n",
            "cp": "#!/bin/bash\necho 'Copied $1 to $2'\n",
        }
        
        for name, content in mock_scripts.items():
            script_path = os.path.join("bin", name)
            with open(script_path, "w") as f:
                f.write(content)
            os.chmod(script_path, 0o755)
    
    def _take_system_snapshot(self):
        """Take a snapshot of the current system state"""
        # Snapshot current directory contents
        self.file_snapshot = {}
        for root, dirs, files in os.walk("."):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    stat = os.stat(file_path)
                    self.file_snapshot[file_path] = {
                        'size': stat.st_size,
                        'mtime': stat.st_mtime,
                        'exists': True
                    }
                except OSError:
                    pass
        
        # Snapshot running processes (basic)
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=5)
            self.process_snapshot = result.stdout
        except Exception:
            self.process_snapshot = "Unable to get process snapshot"
    
    def _analyze_changes(self) -> Dict[str, Any]:
        """Analyze changes made during sandbox execution"""
        changes = {
            'files_created': [],
            'files_modified': [],
            'files_deleted': [],
            'system_changes': []
        }
        
        # Compare file snapshots
        current_files = {}
        for root, dirs, files in os.walk("."):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    stat = os.stat(file_path)
                    current_files[file_path] = {
                        'size': stat.st_size,
                        'mtime': stat.st_mtime,
                        'exists': True
                    }
                except OSError:
                    pass
        
        # Find created files
        for file_path in current_files:
            if file_path not in self.file_snapshot:
                changes['files_created'].append(file_path)
        
        # Find modified files
        for file_path in current_files:
            if file_path in self.file_snapshot:
                old_stat = self.file_snapshot[file_path]
                new_stat = current_files[file_path]
                if (old_stat['size'] != new_stat['size'] or 
                    abs(old_stat['mtime'] - new_stat['mtime']) > 1):
                    changes['files_modified'].append(file_path)
        
        # Find deleted files
        for file_path in self.file_snapshot:
            if file_path not in current_files:
                changes['files_deleted'].append(file_path)
        
        return changes
    
    def execute_command(self, command: str, timeout: int = 30) -> SandboxResult:
        """Execute a command in the sandbox environment"""
        start_time = time.time()
        
        try:
            if self.mode == SandboxMode.DRY_RUN:
                return self._dry_run_command(command)
            elif self.mode == SandboxMode.SIMULATION:
                return self._simulate_command(command)
            elif self.mode == SandboxMode.ISOLATED:
                return self._isolated_execution(command, timeout)
            elif self.mode == SandboxMode.VALIDATION:
                return self._validate_command(command)
            else:
                raise ValueError(f"Unknown sandbox mode: {self.mode}")
                
        except Exception as e:
            return SandboxResult(
                success=False,
                output="",
                error=str(e),
                warnings=["Sandbox execution failed"],
                execution_time=time.time() - start_time,
                risk_level="high"
            )
    
    def _dry_run_command(self, command: str) -> SandboxResult:
        """Perform a dry run of the command"""
        warnings = []
        
        # Analyze command for potential issues
        if any(dangerous in command.lower() for dangerous in ['rm -rf', 'sudo', 'chmod 777']):
            warnings.append("Command contains potentially dangerous operations")
        
        if '&&' in command or ';' in command:
            warnings.append("Command contains multiple operations")
        
        # Simulate what the command would do
        output_lines = []
        output_lines.append(f"[DRY RUN] Would execute: {command}")
        
        # Predict file operations
        if 'mkdir' in command:
            dir_name = command.split()[-1] if len(command.split()) > 1 else "new_directory"
            output_lines.append(f"[DRY RUN] Would create directory: {dir_name}")
        
        if 'touch' in command:
            file_name = command.split()[-1] if len(command.split()) > 1 else "new_file"
            output_lines.append(f"[DRY RUN] Would create file: {file_name}")
        
        if 'rm' in command:
            file_name = command.split()[-1] if len(command.split()) > 1 else "file"
            output_lines.append(f"[DRY RUN] Would remove: {file_name}")
        
        risk_level = "high" if warnings else "low"
        
        return SandboxResult(
            success=True,
            output="\n".join(output_lines),
            warnings=warnings,
            execution_time=0.0,
            risk_level=risk_level
        )
    
    def _simulate_command(self, command: str) -> SandboxResult:
        """Simulate command execution"""
        output_lines = []
        warnings = []
        
        # Parse command to understand what it would do
        parts = command.split()
        if not parts:
            return SandboxResult(
                success=False,
                output="",
                error="Empty command",
                execution_time=0.0
            )
        
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # Simulate common commands
        if cmd == 'ls':
            output_lines.append("file1.txt")
            output_lines.append("file2.txt")
            output_lines.append("directory1/")
        elif cmd == 'cat':
            if args:
                output_lines.append(f"Contents of {args[0]}")
            else:
                output_lines.append("No file specified")
        elif cmd == 'mkdir':
            if args:
                output_lines.append(f"Created directory: {args[0]}")
            else:
                output_lines.append("No directory name specified")
        elif cmd == 'touch':
            if args:
                output_lines.append(f"Created file: {args[0]}")
            else:
                output_lines.append("No file name specified")
        elif cmd == 'rm':
            if args:
                output_lines.append(f"Removed: {args[0]}")
            else:
                output_lines.append("No file specified")
        else:
            output_lines.append(f"Simulated execution of: {command}")
            warnings.append("Command simulation may not be accurate")
        
        return SandboxResult(
            success=True,
            output="\n".join(output_lines),
            warnings=warnings,
            execution_time=0.1,
            risk_level="low"
        )
    
    def _isolated_execution(self, command: str, timeout: int) -> SandboxResult:
        """Execute command in isolated environment"""
        try:
            # Set up isolated environment variables
            env = os.environ.copy()
            env['PATH'] = f"{os.path.abspath('bin')}:{env.get('PATH', '')}"
            env['HOME'] = os.path.abspath('home')
            env['TMPDIR'] = os.path.abspath('tmp')
            
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
                cwd=os.getcwd()
            )
            
            # Analyze changes
            changes = self._analyze_changes()
            
            # Determine risk level
            risk_level = "low"
            if changes['files_deleted'] or 'rm' in command.lower():
                risk_level = "medium"
            if 'sudo' in command.lower() or 'chmod' in command.lower():
                risk_level = "high"
            
            return SandboxResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr if result.stderr else None,
                files_created=changes['files_created'],
                files_modified=changes['files_modified'],
                files_deleted=changes['files_deleted'],
                execution_time=time.time() - time.time(),
                risk_level=risk_level
            )
            
        except subprocess.TimeoutExpired:
            return SandboxResult(
                success=False,
                output="",
                error="Command timed out",
                warnings=["Command execution exceeded timeout limit"],
                execution_time=timeout,
                risk_level="medium"
            )
        except Exception as e:
            return SandboxResult(
                success=False,
                output="",
                error=str(e),
                warnings=["Isolated execution failed"],
                execution_time=0.0,
                risk_level="high"
            )
    
    def _validate_command(self, command: str) -> SandboxResult:
        """Validate command structure and safety"""
        warnings = []
        risk_level = "low"
        
        # Check for dangerous patterns
        dangerous_patterns = [
            r'rm\s+-rf?\s+/',
            r'dd\s+if=/dev/zero',
            r'mkfs\s+',
            r'chmod\s+777',
            r'sudo\s+.*\s+chmod',
            r'kill\s+-9',
        ]
        
        import re
        for pattern in dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                warnings.append(f"Dangerous pattern detected: {pattern}")
                risk_level = "high"
        
        # Check for command injection
        if any(char in command for char in [';', '&&', '||', '|', '>', '<']):
            warnings.append("Command contains shell operators")
            risk_level = "medium"
        
        # Check for network operations
        if any(cmd in command.lower() for cmd in ['wget', 'curl', 'ssh', 'scp']):
            warnings.append("Command performs network operations")
        
        # Validate command structure
        try:
            import shlex
            shlex.split(command)
        except ValueError as e:
            return SandboxResult(
                success=False,
                output="",
                error=f"Invalid command syntax: {e}",
                warnings=warnings,
                execution_time=0.0,
                risk_level="high"
            )
        
        return SandboxResult(
            success=True,
            output=f"Command validation passed: {command}",
            warnings=warnings,
            execution_time=0.0,
            risk_level=risk_level
        )

def sandbox_execute(command: str, mode: SandboxMode = SandboxMode.DRY_RUN, 
                   timeout: int = 30) -> SandboxResult:
    """Convenience function to execute a command in sandbox"""
    with CommandSandbox(mode) as sandbox:
        return sandbox.execute_command(command, timeout) 