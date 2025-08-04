from dataclasses import dataclass, field
from typing import Optional
import datetime
import os

@dataclass
class TrainingConfig:
    # Model Configuration
    base_model: str = "google/gemma-3n-E4B-it"
    use_2b_submodel: bool = True
    enable_mix_and_match: bool = True
    
    # Resource Efficient Mode Configuration
    resource_efficient_mode: bool = False  # Flag for slower but resource-efficient training
    mac_mode: bool = False  # Flag for Mac/Apple Silicon optimizations
    cpu_only_mode: bool = False  # Flag for CPU-only training
    
    # Training Parameters
    learning_rate: float = 1e-4
    batch_size: int = 16
    num_epochs: int = 3
    warmup_steps: int = 100
    gradient_accumulation_steps: int = 4
    
    # Resource Efficient Mode Overrides
    def __post_init__(self):
        if self.mac_mode:
            # Mac mode takes precedence - disable FP16 mixed precision for MPS compatibility
            self.mixed_precision = False
            # Ultra-conservative batch size for Apple Silicon memory constraints
            self.batch_size = 1
            # Increase gradient accumulation to maintain effective batch size
            self.gradient_accumulation_steps = 32
            # Reduce learning rate for more stable training with smaller batches
            self.learning_rate = 3e-5
            # Reduce sequence length for memory efficiency
            self.max_sequence_length = 256
            # Reduce number of workers for MPS compatibility
            self.dataloader_num_workers = 0
            # Lower memory thresholds for Apple Silicon
            self.max_ram_percent = 60.0
            self.max_gpu_memory_percent = 70.0
            self.max_swap_percent = 25.0
            # More frequent memory checks
            self.memory_check_interval = 10
            # More frequent evaluation and saving for better monitoring
            self.save_steps = 100
            self.eval_steps = 25
        elif self.cpu_only_mode:
            # CPU-only mode - ultra-conservative settings
            self.mixed_precision = False
            self.use_gpu = False
            # Very small batch size for CPU training
            self.batch_size = 1
            # Increase gradient accumulation to maintain effective batch size
            self.gradient_accumulation_steps = 64
            # Reduce learning rate for more stable training with smaller batches
            self.learning_rate = 1e-5
            # Reduce sequence length for memory efficiency
            self.max_sequence_length = 128
            # Reduce number of workers for CPU training
            self.dataloader_num_workers = 0
            # Lower memory thresholds for CPU-only
            self.max_ram_percent = 50.0
            self.max_gpu_memory_percent = 0.0
            self.max_swap_percent = 20.0
            # More frequent memory checks
            self.memory_check_interval = 5
            # More frequent evaluation and saving for better monitoring
            self.save_steps = 50
            self.eval_steps = 10
        elif self.resource_efficient_mode:
            # Standard resource-efficient mode (not on Mac)
            # Reduce batch size for lower memory usage
            self.batch_size = 4
            # Increase gradient accumulation to maintain effective batch size
            self.gradient_accumulation_steps = 16
            # Reduce learning rate for more stable training with smaller batches
            self.learning_rate = 5e-5
            # Reduce number of workers for lower CPU usage
            self.dataloader_num_workers = 1
            # Reduce sequence length for lower memory usage
            self.max_sequence_length = 1024
            # More frequent evaluation and saving for better monitoring
            self.save_steps = 200
            self.eval_steps = 50
            # Lower memory thresholds for resource efficiency
            self.max_ram_percent = 70.0
            self.max_gpu_memory_percent = 75.0
            self.max_swap_percent = 30.0
            # More frequent memory checks
            self.memory_check_interval = 15
    
    # Data Configuration
    max_sequence_length: int = 2048
    train_split: float = 0.8
    val_split: float = 0.1
    test_split: float = 0.1
    
    # Output Configuration
    output_dir: str = field(default_factory=lambda: TrainingConfig.generate_output_dir())
    save_steps: int = 500
    eval_steps: int = 100
    
    # Hardware Configuration
    use_gpu: bool = True
    mixed_precision: bool = True
    dataloader_num_workers: int = 4
    
    # Memory Safeguards Configuration
    max_ram_percent: float = 85.0
    max_gpu_memory_percent: float = 90.0
    max_swap_percent: float = 50.0
    memory_check_interval: int = 30
    
    # Checkpoint Configuration
    checkpoint_save_frequency: int = 500
    max_checkpoints: int = 5
    checkpoint_dir: str = "./checkpoints"
    auto_resume: bool = True
    
    @staticmethod
    def generate_output_dir() -> str:
        """Generate a unique output directory name based on current timestamp"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"./models/overseer_gemma_{timestamp}" 
