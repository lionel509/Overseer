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
    # Training Parameters
    learning_rate: float = 1e-4
    batch_size: int = 16
    num_epochs: int = 3
    warmup_steps: int = 100
    gradient_accumulation_steps: int = 4
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

    @staticmethod
    def generate_output_dir():
        now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        base_model_name = "gemma3n"
        return os.path.join("./models", f"{base_model_name}_{now}") 