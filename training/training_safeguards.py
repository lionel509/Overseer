import os
import psutil
import torch
import gc
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MemoryThresholds:
    """Memory usage thresholds for training safeguards"""
    max_ram_percent: float = 85.0  # Maximum RAM usage percentage
    max_gpu_memory_percent: float = 90.0  # Maximum GPU memory usage percentage
    max_swap_percent: float = 50.0  # Maximum swap usage percentage
    memory_check_interval: int = 30  # Check memory every N seconds

@dataclass
class CheckpointConfig:
    """Checkpoint configuration for training recovery"""
    save_frequency: int = 500  # Save checkpoint every N steps
    max_checkpoints: int = 5  # Maximum number of checkpoints to keep
    checkpoint_dir: str = "./checkpoints"
    auto_resume: bool = True  # Automatically resume from latest checkpoint

class MemoryMonitor:
    """Monitors system and GPU memory usage during training"""
    
    def __init__(self, thresholds: MemoryThresholds):
        self.thresholds = thresholds
        self.last_check = time.time()
        self.warning_count = 0
        self.max_warnings = 3
        
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics"""
        # System memory
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        memory_stats = {
            'ram_percent': memory.percent,
            'ram_used_gb': memory.used / (1024**3),
            'ram_total_gb': memory.total / (1024**3),
            'swap_percent': swap.percent,
            'swap_used_gb': swap.used / (1024**3),
        }
        
        # GPU memory (if available)
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.memory_stats()
            memory_stats.update({
                'gpu_memory_percent': (gpu_memory['allocated_bytes.all.current'] / 
                                      torch.cuda.get_device_properties(0).total_memory) * 100,
                'gpu_memory_used_gb': gpu_memory['allocated_bytes.all.current'] / (1024**3),
                'gpu_memory_total_gb': torch.cuda.get_device_properties(0).total_memory / (1024**3),
            })
        
        return memory_stats
    
    def check_memory_limits(self) -> Tuple[bool, Dict[str, Any]]:
        """Check if memory usage is within acceptable limits"""
        current_time = time.time()
        if current_time - self.last_check < self.thresholds.memory_check_interval:
            return True, {}
        
        self.last_check = current_time
        memory_stats = self.get_memory_usage()
        
        warnings = []
        critical = False
        
        # Check RAM usage
        if memory_stats['ram_percent'] > self.thresholds.max_ram_percent:
            warnings.append(f"RAM usage high: {memory_stats['ram_percent']:.1f}%")
            if memory_stats['ram_percent'] > 95:
                critical = True
        
        # Check swap usage
        if memory_stats['swap_percent'] > self.thresholds.max_swap_percent:
            warnings.append(f"Swap usage high: {memory_stats['swap_percent']:.1f}%")
            if memory_stats['swap_percent'] > 80:
                critical = True
        
        # Check GPU memory usage
        if 'gpu_memory_percent' in memory_stats:
            if memory_stats['gpu_memory_percent'] > self.thresholds.max_gpu_memory_percent:
                warnings.append(f"GPU memory usage high: {memory_stats['gpu_memory_percent']:.1f}%")
                if memory_stats['gpu_memory_percent'] > 95:
                    critical = True
        
        if warnings:
            self.warning_count += 1
            logger.warning(f"Memory warnings ({self.warning_count}/{self.max_warnings}): {'; '.join(warnings)}")
            
            if critical or self.warning_count >= self.max_warnings:
                logger.error("Critical memory usage detected! Training should be paused.")
                return False, {'warnings': warnings, 'critical': critical, 'stats': memory_stats}
        
        return True, {'warnings': warnings, 'stats': memory_stats}
    
    def force_garbage_collection(self):
        """Force garbage collection to free memory"""
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("Forced garbage collection completed")

class CheckpointManager:
    """Manages training checkpoints for recovery and resumption"""
    
    def __init__(self, config: CheckpointConfig):
        self.config = config
        self.checkpoint_dir = Path(config.checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
        self.checkpoint_metadata_file = self.checkpoint_dir / "checkpoint_metadata.json"
        self.load_metadata()
    
    def load_metadata(self):
        """Load checkpoint metadata from file"""
        if self.checkpoint_metadata_file.exists():
            with open(self.checkpoint_metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {
                'checkpoints': [],
                'latest_checkpoint': None,
                'training_state': {}
            }
    
    def save_metadata(self):
        """Save checkpoint metadata to file"""
        with open(self.checkpoint_metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def create_checkpoint(self, trainer, step: int, metrics: Dict[str, float]) -> str:
        """Create a new checkpoint"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_name = f"checkpoint_step_{step}_{timestamp}"
        checkpoint_path = self.checkpoint_dir / checkpoint_name
        
        # Save model and optimizer state
        trainer.save_model(str(checkpoint_path))
        
        # Save training state
        training_state = {
            'step': step,
            'epoch': getattr(trainer.state, 'epoch', 0),
            'metrics': metrics,
            'timestamp': timestamp,
            'checkpoint_path': str(checkpoint_path)
        }
        
        # Update metadata
        self.metadata['checkpoints'].append(training_state)
        self.metadata['latest_checkpoint'] = training_state
        
        # Clean up old checkpoints
        self._cleanup_old_checkpoints()
        
        # Save metadata
        self.save_metadata()
        
        logger.info(f"Checkpoint saved: {checkpoint_name}")
        return str(checkpoint_path)
    
    def _cleanup_old_checkpoints(self):
        """Remove old checkpoints to save disk space"""
        if len(self.metadata['checkpoints']) > self.config.max_checkpoints:
            # Remove oldest checkpoints
            checkpoints_to_remove = self.metadata['checkpoints'][:-self.config.max_checkpoints]
            for checkpoint in checkpoints_to_remove:
                checkpoint_path = Path(checkpoint['checkpoint_path'])
                if checkpoint_path.exists():
                    import shutil
                    shutil.rmtree(checkpoint_path)
                    logger.info(f"Removed old checkpoint: {checkpoint_path}")
            
            # Update metadata
            self.metadata['checkpoints'] = self.metadata['checkpoints'][-self.config.max_checkpoints:]
    
    def get_latest_checkpoint(self) -> Optional[Dict[str, Any]]:
        """Get the latest checkpoint information"""
        return self.metadata.get('latest_checkpoint')
    
    def resume_from_checkpoint(self, trainer, checkpoint_path: str) -> bool:
        """Resume training from a checkpoint"""
        try:
            checkpoint_path = Path(checkpoint_path)
            if not checkpoint_path.exists():
                logger.error(f"Checkpoint not found: {checkpoint_path}")
                return False
            
            # Load the model
            trainer.model = trainer.model.from_pretrained(str(checkpoint_path))
            logger.info(f"Resumed training from checkpoint: {checkpoint_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume from checkpoint: {e}")
            return False

class TrainingSafeguards:
    """Main class for managing training safeguards"""
    
    def __init__(self, 
                 memory_thresholds: Optional[MemoryThresholds] = None,
                 checkpoint_config: Optional[CheckpointConfig] = None):
        
        self.memory_thresholds = memory_thresholds or MemoryThresholds()
        self.checkpoint_config = checkpoint_config or CheckpointConfig()
        
        self.memory_monitor = MemoryMonitor(self.memory_thresholds)
        self.checkpoint_manager = CheckpointManager(self.checkpoint_config)
        
        self.training_start_time = None
        self.last_safeguard_check = 0
        
    def start_training_session(self):
        """Initialize training session"""
        self.training_start_time = time.time()
        logger.info("Training safeguards initialized")
        
        # Check initial memory state
        memory_ok, memory_info = self.memory_monitor.check_memory_limits()
        if not memory_ok:
            logger.warning("Memory usage is high at training start")
    
    def check_safeguards(self, trainer, step: int, metrics: Dict[str, float]) -> bool:
        """Check all training safeguards"""
        current_time = time.time()
        
        # Check memory limits
        memory_ok, memory_info = self.memory_monitor.check_memory_limits()
        
        if not memory_ok:
            logger.warning("Memory limits exceeded, forcing garbage collection")
            self.memory_monitor.force_garbage_collection()
            
            # Re-check memory after garbage collection
            memory_ok, memory_info = self.memory_monitor.check_memory_limits()
            
            if not memory_ok:
                logger.error("Memory still critical after garbage collection")
                return False
        
        # Create checkpoint if needed
        if step % self.checkpoint_config.save_frequency == 0:
            self.checkpoint_manager.create_checkpoint(trainer, step, metrics)
        
        return True
    
    def handle_training_interruption(self, trainer, step: int, metrics: Dict[str, float]):
        """Handle training interruption gracefully"""
        logger.info("Training interruption detected, creating emergency checkpoint")
        
        # Force garbage collection
        self.memory_monitor.force_garbage_collection()
        
        # Create emergency checkpoint
        emergency_checkpoint = self.checkpoint_manager.create_checkpoint(trainer, step, metrics)
        
        logger.info(f"Emergency checkpoint created: {emergency_checkpoint}")
        return emergency_checkpoint
    
    def get_training_summary(self) -> Dict[str, Any]:
        """Get training session summary"""
        if self.training_start_time is None:
            return {}
        
        duration = time.time() - self.training_start_time
        memory_stats = self.memory_monitor.get_memory_usage()
        
        return {
            'training_duration_seconds': duration,
            'memory_stats': memory_stats,
            'latest_checkpoint': self.checkpoint_manager.get_latest_checkpoint()
        } 