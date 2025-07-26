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
    
    # Training Parameters
    learning_rate: float = 1e-4
    batch_size: int = 16
    num_epochs: int = 3
    warmup_steps: int = 100
    gradient_accumulation_steps: int = 4
    
    # Resource Efficient Mode Overrides
    def __post_init__(self):
        if self.resource_efficient_mode:
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
<<<<<<< HEAD

    @staticmethod
    def generate_output_dir():
        now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        base_model_name = "gemma3n"
        return os.path.join("./models", f"{base_model_name}_{now}") 
=======
    
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
>>>>>>> 6dbc57b5c429104813d2331756c724e071791c43
