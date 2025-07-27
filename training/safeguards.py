import os
import time
import logging
from typing import Optional

try:
    import psutil
except ImportError:
    psutil = None

try:
    import torch
except ImportError:
    torch = None

class MemoryMonitor:
    def __init__(self, max_ram_gb: float = 16.0, max_gpu_gb: float = 12.0):
        self.max_ram_gb = max_ram_gb
        self.max_gpu_gb = max_gpu_gb

    def check_memory(self) -> bool:
        """Return True if memory usage is within limits, False if exceeded."""
        if psutil:
            ram_gb = psutil.virtual_memory().used / 1e9
            if ram_gb > self.max_ram_gb:
                logging.warning(f"RAM usage exceeded: {ram_gb:.2f} GB > {self.max_ram_gb} GB")
                return False
        if torch and torch.cuda.is_available():
            gpu_gb = torch.cuda.memory_allocated() / 1e9
            if gpu_gb > self.max_gpu_gb:
                logging.warning(f"GPU usage exceeded: {gpu_gb:.2f} GB > {self.max_gpu_gb} GB")
                return False
        return True

class OOMHandler:
    def __init__(self, min_batch_size: int = 1):
        self.min_batch_size = min_batch_size

    def handle_oom(self, current_batch_size: int) -> int:
        """Reduce batch size on OOM, but not below min_batch_size."""
        new_batch_size = max(self.min_batch_size, current_batch_size // 2)
        logging.warning(f"OOM detected. Reducing batch size from {current_batch_size} to {new_batch_size}")
        return new_batch_size

class EarlyStopping:
    def __init__(self, patience: int = 3):
        self.patience = patience
        self.best_loss = float('inf')
        self.counter = 0

    def step(self, val_loss: float) -> bool:
        if val_loss < self.best_loss:
            self.best_loss = val_loss
            self.counter = 0
        else:
            self.counter += 1
        if self.counter >= self.patience:
            logging.info(f"Early stopping triggered after {self.patience} epochs without improvement.")
            return True
        return False

class SafeguardLogger:
    def __init__(self, log_file: Optional[str] = None):
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s'
        )
    def log(self, message: str, level: str = 'info'):
        getattr(logging, level)(message) 