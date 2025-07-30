"""
Performance Optimizer - Phase 6 Optimization
Provides system optimization, resource management, and performance tuning capabilities.
"""

import os
import sys
import time
import json
import psutil
import threading
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from system_monitor import SystemMonitor
from advanced_process_manager import AdvancedProcessManager
from predictive_analytics import PredictiveAnalytics

@dataclass
class OptimizationTarget:
    """Optimization target data structure"""
    target_type: str  # 'cpu', 'memory', 'disk', 'network', 'process'
    current_value: float
    target_value: float
    priority: str  # 'high', 'medium', 'low'
    description: str
    optimization_method: str
    estimated_impact: str

@dataclass
class OptimizationAction:
    """Optimization action data structure"""
    action_type: str  # 'kill_process', 'suspend_process', 'cleanup_memory', 'optimize_disk'
    target_id: str
    description: str
    priority: str
    estimated_benefit: float
    risk_level: str  # 'low', 'medium', 'high'
    execution_time: float

@dataclass
class PerformanceProfile:
    """Performance profile data structure"""
    profile_name: str
    cpu_threshold: float
    memory_threshold: float
    disk_threshold: float
    network_threshold: float
    optimization_rules: List[Dict]
    auto_optimize: bool
    created_at: float

class PerformanceOptimizer:
    """Performance optimization engine"""
    
    def __init__(self, config: Dict = None):
        """Initialize performance optimizer"""
        self.console = Console() if RICH_AVAILABLE else None
        self.config = config or {}
        
        # Initialize components
        self.system_monitor = SystemMonitor()
        self.process_manager = AdvancedProcessManager()
        self.predictive_analytics = PredictiveAnalytics()
        
        # Optimization settings
        self.optimization_dir = self.config.get('optimization_dir', 'optimizations')
        self.auto_optimize = self.config.get('auto_optimize', False)
        self.optimization_threshold = self.config.get('optimization_threshold', 0.8)
        
        # Create directories
        os.makedirs(self.optimization_dir, exist_ok=True)
        
        # Database paths
        self.optimizer_db = os.path.join(os.path.dirname(__file__), '../../db/performance_optimizer.db')
        
        # Performance profiles
        self.performance_profiles = {}
        self.current_profile = None
        
        # Optimization history
        self.optimization_history = []
        self.max_history_size = 100
        
        # Initialize database
        self._init_database()
        self._load_performance_profiles()
    
    def _init_database(self):
        """Initialize performance optimizer database"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.optimizer_db)
            cursor = conn.cursor()
            
            # Create optimization targets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS optimization_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_type TEXT NOT NULL,
                    current_value REAL,
                    target_value REAL,
                    priority TEXT,
                    description TEXT,
                    optimization_method TEXT,
                    estimated_impact TEXT,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            ''')
            
            # Create optimization actions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS optimization_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_type TEXT NOT NULL,
                    target_id TEXT,
                    description TEXT,
                    priority TEXT,
                    estimated_benefit REAL,
                    risk_level TEXT,
                    execution_time REAL,
                    status TEXT DEFAULT 'pending',
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            ''')
            
            # Create performance profiles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_name TEXT NOT NULL,
                    cpu_threshold REAL,
                    memory_threshold REAL,
                    disk_threshold REAL,
                    network_threshold REAL,
                    optimization_rules TEXT,
                    auto_optimize BOOLEAN,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            ''')
            
            # Create optimization history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS optimization_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    optimization_type TEXT NOT NULL,
                    target_component TEXT,
                    before_value REAL,
                    after_value REAL,
                    improvement_percentage REAL,
                    execution_time REAL,
                    status TEXT,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error initializing optimizer database: {e}[/red]")
    
    def _load_performance_profiles(self):
        """Load performance profiles from database"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.optimizer_db)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM performance_profiles')
            rows = cursor.fetchall()
            conn.close()
            
            for row in rows:
                profile = PerformanceProfile(
                    profile_name=row[1],
                    cpu_threshold=row[2],
                    memory_threshold=row[3],
                    disk_threshold=row[4],
                    network_threshold=row[5],
                    optimization_rules=json.loads(row[6]) if row[6] else [],
                    auto_optimize=bool(row[7]),
                    created_at=row[8]
                )
                self.performance_profiles[profile.profile_name] = profile
            
            # Set default profile if none exists
            if not self.performance_profiles:
                self._create_default_profile()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error loading performance profiles: {e}[/red]")
    
    def _create_default_profile(self):
        """Create default performance profile"""
        default_profile = PerformanceProfile(
            profile_name="balanced",
            cpu_threshold=80.0,
            memory_threshold=85.0,
            disk_threshold=90.0,
            network_threshold=70.0,
            optimization_rules=[
                {"type": "cpu", "action": "kill_process", "threshold": 90, "priority": "high"},
                {"type": "memory", "action": "cleanup_memory", "threshold": 85, "priority": "medium"},
                {"type": "disk", "action": "cleanup_disk", "threshold": 95, "priority": "high"}
            ],
            auto_optimize=False,
            created_at=time.time()
        )
        
        self.performance_profiles["balanced"] = default_profile
        self._save_performance_profile(default_profile)
    
    def analyze_system_performance(self) -> List[OptimizationTarget]:
        """Analyze system performance and identify optimization targets"""
        targets = []
        
        try:
            # Get current system metrics
            metrics = self.system_monitor.collect_metrics()
            if not metrics:
                return targets
            
            # Analyze CPU usage
            if metrics.cpu_percent > 70:
                target = OptimizationTarget(
                    target_type='cpu',
                    current_value=metrics.cpu_percent,
                    target_value=60.0,
                    priority='high' if metrics.cpu_percent > 90 else 'medium',
                    description=f"High CPU usage ({metrics.cpu_percent:.1f}%)",
                    optimization_method='process_optimization',
                    estimated_impact='Reduce CPU usage by 20-30%'
                )
                targets.append(target)
            
            # Analyze memory usage
            if metrics.memory_percent > 80:
                target = OptimizationTarget(
                    target_type='memory',
                    current_value=metrics.memory_percent,
                    target_value=70.0,
                    priority='high' if metrics.memory_percent > 90 else 'medium',
                    description=f"High memory usage ({metrics.memory_percent:.1f}%)",
                    optimization_method='memory_cleanup',
                    estimated_impact='Free up 10-20% of memory'
                )
                targets.append(target)
            
            # Analyze disk usage
            if metrics.disk_percent > 85:
                target = OptimizationTarget(
                    target_type='disk',
                    current_value=metrics.disk_percent,
                    target_value=80.0,
                    priority='high' if metrics.disk_percent > 95 else 'medium',
                    description=f"High disk usage ({metrics.disk_percent:.1f}%)",
                    optimization_method='disk_cleanup',
                    estimated_impact='Free up 5-15% of disk space'
                )
                targets.append(target)
            
            # Analyze process performance
            process_issues = self._analyze_process_performance()
            targets.extend(process_issues)
            
            # Save targets to database
            for target in targets:
                self._save_optimization_target(target)
            
            return targets
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error analyzing system performance: {e}[/red]")
            return []
    
    def _analyze_process_performance(self) -> List[OptimizationTarget]:
        """Analyze individual process performance"""
        targets = []
        
        try:
            # Get top processes
            processes = self.process_manager.get_top_processes(limit=10)
            
            for process in processes:
                # Check for high CPU processes
                if process.cpu_percent > 50:
                    target = OptimizationTarget(
                        target_type='process',
                        current_value=process.cpu_percent,
                        target_value=30.0,
                        priority='high' if process.cpu_percent > 80 else 'medium',
                        description=f"High CPU process: {process.name} (PID: {process.pid})",
                        optimization_method='process_optimization',
                        estimated_impact=f'Reduce CPU usage by {process.cpu_percent - 30:.1f}%'
                    )
                    targets.append(target)
                
                # Check for high memory processes
                if process.memory_percent > 10:
                    target = OptimizationTarget(
                        target_type='process',
                        current_value=process.memory_percent,
                        target_value=5.0,
                        priority='medium',
                        description=f"High memory process: {process.name} (PID: {process.pid})",
                        optimization_method='memory_optimization',
                        estimated_impact=f'Reduce memory usage by {process.memory_percent - 5:.1f}%'
                    )
                    targets.append(target)
            
            return targets
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error analyzing process performance: {e}[/red]")
            return []
    
    def generate_optimization_plan(self, targets: List[OptimizationTarget]) -> List[OptimizationAction]:
        """Generate optimization plan based on targets"""
        actions = []
        
        try:
            for target in targets:
                if target.target_type == 'cpu':
                    actions.extend(self._generate_cpu_optimizations(target))
                elif target.target_type == 'memory':
                    actions.extend(self._generate_memory_optimizations(target))
                elif target.target_type == 'disk':
                    actions.extend(self._generate_disk_optimizations(target))
                elif target.target_type == 'process':
                    actions.extend(self._generate_process_optimizations(target))
            
            # Sort actions by priority and estimated benefit
            actions.sort(key=lambda x: (x.priority == 'high', x.estimated_benefit), reverse=True)
            
            # Save actions to database
            for action in actions:
                self._save_optimization_action(action)
            
            return actions
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error generating optimization plan: {e}[/red]")
            return []
    
    def _generate_cpu_optimizations(self, target: OptimizationTarget) -> List[OptimizationAction]:
        """Generate CPU optimization actions"""
        actions = []
        
        try:
            # Get high CPU processes
            processes = self.process_manager.get_top_processes(limit=5)
            high_cpu_processes = [p for p in processes if p.cpu_percent > 30]
            
            for process in high_cpu_processes:
                if process.cpu_percent > 80:
                    # Kill extremely high CPU processes
                    action = OptimizationAction(
                        action_type='kill_process',
                        target_id=str(process.pid),
                        description=f"Kill high CPU process: {process.name} (PID: {process.pid})",
                        priority='high',
                        estimated_benefit=process.cpu_percent,
                        risk_level='medium',
                        execution_time=1.0
                    )
                else:
                    # Suspend high CPU processes
                    action = OptimizationAction(
                        action_type='suspend_process',
                        target_id=str(process.pid),
                        description=f"Suspend high CPU process: {process.name} (PID: {process.pid})",
                        priority='medium',
                        estimated_benefit=process.cpu_percent * 0.5,
                        risk_level='low',
                        execution_time=0.5
                    )
                
                actions.append(action)
            
            return actions
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error generating CPU optimizations: {e}[/red]")
            return []
    
    def _generate_memory_optimizations(self, target: OptimizationTarget) -> List[OptimizationAction]:
        """Generate memory optimization actions"""
        actions = []
        
        try:
            # Memory cleanup action
            action = OptimizationAction(
                action_type='cleanup_memory',
                target_id='system_memory',
                description="Perform memory cleanup and garbage collection",
                priority='medium',
                estimated_benefit=10.0,  # Estimated 10% memory improvement
                risk_level='low',
                execution_time=2.0
            )
            actions.append(action)
            
            # Get high memory processes
            processes = self.process_manager.get_top_processes(limit=5)
            high_memory_processes = [p for p in processes if p.memory_percent > 5]
            
            for process in high_memory_processes:
                if process.memory_percent > 20:
                    # Kill extremely high memory processes
                    action = OptimizationAction(
                        action_type='kill_process',
                        target_id=str(process.pid),
                        description=f"Kill high memory process: {process.name} (PID: {process.pid})",
                        priority='high',
                        estimated_benefit=process.memory_percent,
                        risk_level='medium',
                        execution_time=1.0
                    )
                else:
                    # Suspend high memory processes
                    action = OptimizationAction(
                        action_type='suspend_process',
                        target_id=str(process.pid),
                        description=f"Suspend high memory process: {process.name} (PID: {process.pid})",
                        priority='medium',
                        estimated_benefit=process.memory_percent * 0.5,
                        risk_level='low',
                        execution_time=0.5
                    )
                
                actions.append(action)
            
            return actions
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error generating memory optimizations: {e}[/red]")
            return []
    
    def _generate_disk_optimizations(self, target: OptimizationTarget) -> List[OptimizationAction]:
        """Generate disk optimization actions"""
        actions = []
        
        try:
            # Disk cleanup action
            action = OptimizationAction(
                action_type='cleanup_disk',
                target_id='system_disk',
                description="Perform disk cleanup and temporary file removal",
                priority='high',
                estimated_benefit=5.0,  # Estimated 5% disk space improvement
                risk_level='low',
                execution_time=5.0
            )
            actions.append(action)
            
            return actions
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error generating disk optimizations: {e}[/red]")
            return []
    
    def _generate_process_optimizations(self, target: OptimizationTarget) -> List[OptimizationAction]:
        """Generate process optimization actions"""
        actions = []
        
        try:
            # Extract PID from target description
            import re
            pid_match = re.search(r'PID: (\d+)', target.description)
            if pid_match:
                pid = int(pid_match.group(1))
                
                if target.current_value > 80:
                    # Kill high resource process
                    action = OptimizationAction(
                        action_type='kill_process',
                        target_id=str(pid),
                        description=f"Kill high resource process (PID: {pid})",
                        priority='high',
                        estimated_benefit=target.current_value,
                        risk_level='medium',
                        execution_time=1.0
                    )
                else:
                    # Suspend process
                    action = OptimizationAction(
                        action_type='suspend_process',
                        target_id=str(pid),
                        description=f"Suspend high resource process (PID: {pid})",
                        priority='medium',
                        estimated_benefit=target.current_value * 0.5,
                        risk_level='low',
                        execution_time=0.5
                    )
                
                actions.append(action)
            
            return actions
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error generating process optimizations: {e}[/red]")
            return []
    
    def execute_optimization_actions(self, actions: List[OptimizationAction]) -> Dict:
        """Execute optimization actions"""
        results = {
            'executed': 0,
            'successful': 0,
            'failed': 0,
            'total_benefit': 0.0,
            'execution_time': 0.0,
            'details': []
        }
        
        start_time = time.time()
        
        try:
            for action in actions:
                try:
                    result = self._execute_single_action(action)
                    results['executed'] += 1
                    
                    if result['success']:
                        results['successful'] += 1
                        results['total_benefit'] += action.estimated_benefit
                    else:
                        results['failed'] += 1
                    
                    results['details'].append(result)
                    
                    # Update action status
                    self._update_action_status(action, result['success'])
                    
                except Exception as e:
                    results['failed'] += 1
                    results['details'].append({
                        'action': action.description,
                        'success': False,
                        'error': str(e)
                    })
            
            results['execution_time'] = time.time() - start_time
            
            # Log optimization history
            self._log_optimization_history(results)
            
            return results
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error executing optimization actions: {e}[/red]")
            return results
    
    def _execute_single_action(self, action: OptimizationAction) -> Dict:
        """Execute a single optimization action"""
        result = {
            'action': action.description,
            'success': False,
            'before_value': None,
            'after_value': None,
            'improvement': 0.0
        }
        
        try:
            if action.action_type == 'kill_process':
                result = self._execute_kill_process(action)
            elif action.action_type == 'suspend_process':
                result = self._execute_suspend_process(action)
            elif action.action_type == 'cleanup_memory':
                result = self._execute_memory_cleanup(action)
            elif action.action_type == 'cleanup_disk':
                result = self._execute_disk_cleanup(action)
            else:
                result['error'] = f"Unknown action type: {action.action_type}"
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def _execute_kill_process(self, action: OptimizationAction) -> Dict:
        """Execute kill process action"""
        result = {
            'action': action.description,
            'success': False,
            'before_value': None,
            'after_value': None,
            'improvement': 0.0
        }
        
        try:
            pid = int(action.target_id)
            
            # Get process info before killing
            process = psutil.Process(pid)
            result['before_value'] = process.cpu_percent()
            
            # Kill the process
            process.kill()
            
            result['success'] = True
            result['after_value'] = 0.0
            result['improvement'] = result['before_value']
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def _execute_suspend_process(self, action: OptimizationAction) -> Dict:
        """Execute suspend process action"""
        result = {
            'action': action.description,
            'success': False,
            'before_value': None,
            'after_value': None,
            'improvement': 0.0
        }
        
        try:
            pid = int(action.target_id)
            
            # Get process info before suspending
            process = psutil.Process(pid)
            result['before_value'] = process.cpu_percent()
            
            # Suspend the process
            process.suspend()
            
            result['success'] = True
            result['after_value'] = 0.0
            result['improvement'] = result['before_value']
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def _execute_memory_cleanup(self, action: OptimizationAction) -> Dict:
        """Execute memory cleanup action"""
        result = {
            'action': action.description,
            'success': False,
            'before_value': None,
            'after_value': None,
            'improvement': 0.0
        }
        
        try:
            # Get memory before cleanup
            memory_before = psutil.virtual_memory().percent
            result['before_value'] = memory_before
            
            # Perform memory cleanup (garbage collection)
            import gc
            gc.collect()
            
            # Get memory after cleanup
            memory_after = psutil.virtual_memory().percent
            result['after_value'] = memory_after
            result['improvement'] = memory_before - memory_after
            result['success'] = True
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def _execute_disk_cleanup(self, action: OptimizationAction) -> Dict:
        """Execute disk cleanup action"""
        result = {
            'action': action.description,
            'success': False,
            'before_value': None,
            'after_value': None,
            'improvement': 0.0
        }
        
        try:
            # Get disk usage before cleanup
            disk_before = psutil.disk_usage('/').percent
            result['before_value'] = disk_before
            
            # Perform disk cleanup (remove temp files)
            import tempfile
            import shutil
            
            # Clean temp directory
            temp_dir = tempfile.gettempdir()
            for item in os.listdir(temp_dir):
                item_path = os.path.join(temp_dir, item)
                try:
                    if os.path.isfile(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception:
                    pass  # Ignore errors for individual files
            
            # Get disk usage after cleanup
            disk_after = psutil.disk_usage('/').percent
            result['after_value'] = disk_after
            result['improvement'] = disk_before - disk_after
            result['success'] = True
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def _save_optimization_target(self, target: OptimizationTarget):
        """Save optimization target to database"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.optimizer_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO optimization_targets 
                (target_type, current_value, target_value, priority, description, optimization_method, estimated_impact)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                target.target_type,
                target.current_value,
                target.target_value,
                target.priority,
                target.description,
                target.optimization_method,
                target.estimated_impact
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error saving optimization target: {e}[/red]")
    
    def _save_optimization_action(self, action: OptimizationAction):
        """Save optimization action to database"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.optimizer_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO optimization_actions 
                (action_type, target_id, description, priority, estimated_benefit, risk_level, execution_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                action.action_type,
                action.target_id,
                action.description,
                action.priority,
                action.estimated_benefit,
                action.risk_level,
                action.execution_time
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error saving optimization action: {e}[/red]")
    
    def _update_action_status(self, action: OptimizationAction, success: bool):
        """Update action status in database"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.optimizer_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE optimization_actions 
                SET status = ? 
                WHERE target_id = ? AND action_type = ?
            ''', ('completed' if success else 'failed', action.target_id, action.action_type))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error updating action status: {e}[/red]")
    
    def _save_performance_profile(self, profile: PerformanceProfile):
        """Save performance profile to database"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.optimizer_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_profiles 
                (profile_name, cpu_threshold, memory_threshold, disk_threshold, network_threshold, optimization_rules, auto_optimize)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                profile.profile_name,
                profile.cpu_threshold,
                profile.memory_threshold,
                profile.disk_threshold,
                profile.network_threshold,
                json.dumps(profile.optimization_rules),
                profile.auto_optimize
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error saving performance profile: {e}[/red]")
    
    def _log_optimization_history(self, results: Dict):
        """Log optimization history"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.optimizer_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO optimization_history 
                (optimization_type, target_component, before_value, after_value, improvement_percentage, execution_time, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                'batch_optimization',
                'system',
                results.get('total_benefit', 0),
                results.get('total_benefit', 0),
                results.get('total_benefit', 0),
                results.get('execution_time', 0),
                'completed' if results['successful'] > results['failed'] else 'partial'
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Error logging optimization history: {e}[/red]")
    
    def display_optimization_status(self):
        """Display optimization status"""
        if not RICH_AVAILABLE:
            print("Rich library required for formatted display")
            return
        
        # Create status table
        status_table = Table(title="Performance Optimizer Status")
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="green")
        status_table.add_column("Current Value", style="yellow")
        status_table.add_column("Target Value", style="magenta")
        status_table.add_column("Optimization", style="blue")
        
        # Get current system metrics
        metrics = self.system_monitor.collect_metrics()
        if metrics:
            # CPU status
            cpu_status = "⚠️ High" if metrics.cpu_percent > 80 else "✅ Normal"
            status_table.add_row(
                "CPU Usage",
                cpu_status,
                f"{metrics.cpu_percent:.1f}%",
                "60%",
                "Process optimization" if metrics.cpu_percent > 80 else "None needed"
            )
            
            # Memory status
            memory_status = "⚠️ High" if metrics.memory_percent > 85 else "✅ Normal"
            status_table.add_row(
                "Memory Usage",
                memory_status,
                f"{metrics.memory_percent:.1f}%",
                "70%",
                "Memory cleanup" if metrics.memory_percent > 85 else "None needed"
            )
            
            # Disk status
            disk_status = "⚠️ High" if metrics.disk_percent > 90 else "✅ Normal"
            status_table.add_row(
                "Disk Usage",
                disk_status,
                f"{metrics.disk_percent:.1f}%",
                "80%",
                "Disk cleanup" if metrics.disk_percent > 90 else "None needed"
            )
        
        self.console.print(status_table)

def main():
    """Main function for standalone testing"""
    optimizer = PerformanceOptimizer()
    
    print("⚡ Performance Optimizer - Phase 6 Optimization")
    print("=" * 60)
    
    # Display status
    optimizer.display_optimization_status()
    
    # Analyze system performance
    print("\n🔍 Analyzing system performance...")
    targets = optimizer.analyze_system_performance()
    print(f"Found {len(targets)} optimization targets")
    
    # Generate optimization plan
    print("\n📋 Generating optimization plan...")
    actions = optimizer.generate_optimization_plan(targets)
    print(f"Generated {len(actions)} optimization actions")
    
    # Execute optimizations (demo mode - don't actually execute)
    print("\n🚀 Optimization ready (demo mode - not executing)")
    for action in actions[:3]:  # Show first 3 actions
        print(f"  - {action.description} (Priority: {action.priority})")
    
    print("\n✅ Performance optimizer test completed!")

if __name__ == "__main__":
    main() 