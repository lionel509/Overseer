# Training Safeguards System

This document explains the training safeguards system implemented to prevent memory runaway and provide checkpoint management for the Overseer training pipeline.

## Overview

The training safeguards system provides:
- **Memory Monitoring**: Real-time monitoring of RAM, GPU memory, and swap usage
- **Automatic Checkpointing**: Regular saving of training progress for recovery
- **Training Recovery**: Ability to resume training from the last checkpoint
- **Emergency Handling**: Graceful handling of training interruptions

## Components

### 1. Training Safeguards (`training_safeguards.py`)

The main safeguards system that integrates memory monitoring and checkpoint management.

**Key Features:**
- `MemoryMonitor`: Monitors system and GPU memory usage
- `CheckpointManager`: Manages training checkpoints and recovery
- `TrainingSafeguards`: Main class that coordinates all safeguards

### 2. Memory Monitor (`memory_monitor.py`)

Standalone memory monitoring script that can be run independently.

**Usage:**
```bash
# Start monitoring (30-second intervals)
python memory_monitor.py

# Custom interval
python memory_monitor.py --interval 60

# Analyze existing logs
python memory_monitor.py --analyze

# Monitor without logging to file
python memory_monitor.py --no-log
```

### 3. Configuration (`training_config.py`)

Updated configuration with memory and checkpoint settings:

```python
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
```

## Usage

### Basic Training with Safeguards

The safeguards are automatically integrated into the training pipeline:

```bash
# Run training with all safeguards enabled
python main_training.py --download-data --continuous-learning
```

### Memory Monitoring

Run memory monitoring in a separate terminal:

```bash
# In a separate terminal
cd training
python memory_monitor.py --interval 30
```

### Checkpoint Management

Checkpoints are automatically created during training. To resume from a checkpoint:

```bash
# Training will automatically resume from the latest checkpoint
python main_training.py --download-data --continuous-learning
```

## Configuration Options

### Memory Thresholds

Adjust memory limits in `training_config.py`:

```python
# Conservative settings (recommended for limited resources)
max_ram_percent: float = 75.0
max_gpu_memory_percent: float = 80.0
max_swap_percent: float = 30.0

# Aggressive settings (for high-end systems)
max_ram_percent: float = 90.0
max_gpu_memory_percent: float = 95.0
max_swap_percent: float = 70.0
```

### Checkpoint Settings

```python
# Frequent checkpoints (more disk space, better recovery)
checkpoint_save_frequency: int = 250
max_checkpoints: int = 10

# Less frequent checkpoints (less disk space)
checkpoint_save_frequency: int = 1000
max_checkpoints: int = 3
```

## Emergency Procedures

### Training Interruption

If training is interrupted (Ctrl+C, system crash, etc.):

1. **Automatic Recovery**: Training will automatically resume from the latest checkpoint
2. **Emergency Checkpoint**: An emergency checkpoint is created before the interruption
3. **Memory Cleanup**: Garbage collection is performed to free memory

### Memory Issues

If memory usage becomes critical:

1. **Automatic Garbage Collection**: The system forces garbage collection
2. **Warning System**: Warnings are logged when memory usage is high
3. **Training Pause**: Training can be paused if memory becomes critical

## Monitoring and Logging

### Memory Logs

Memory monitoring creates detailed logs in JSON format:

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "memory": {
    "total_gb": 32.0,
    "used_gb": 28.5,
    "percent": 89.1
  },
  "gpu": {
    "memory_allocated_gb": 12.3,
    "memory_total_gb": 16.0,
    "memory_percent": 76.9
  }
}
```

### Checkpoint Metadata

Checkpoint information is stored in `checkpoints/checkpoint_metadata.json`:

```json
{
  "checkpoints": [
    {
      "step": 1000,
      "epoch": 1.5,
      "timestamp": "2024-01-15T10:30:00",
      "checkpoint_path": "./checkpoints/checkpoint_step_1000_20240115_103000"
    }
  ],
  "latest_checkpoint": {...}
}
```

## Troubleshooting

### High Memory Usage

1. **Reduce batch size**: Lower `batch_size` in `training_config.py`
2. **Enable gradient checkpointing**: Add to training arguments
3. **Use mixed precision**: Ensure `mixed_precision: True`
4. **Monitor in separate terminal**: Use `memory_monitor.py`

### Checkpoint Issues

1. **Check disk space**: Ensure sufficient space for checkpoints
2. **Verify checkpoint integrity**: Check `checkpoint_metadata.json`
3. **Manual cleanup**: Remove old checkpoints if needed

### Training Recovery

1. **Automatic resume**: Training automatically resumes from latest checkpoint
2. **Manual resume**: Specify checkpoint path in training arguments
3. **Fresh start**: Delete checkpoint directory to start fresh

## Best Practices

1. **Monitor Resources**: Run memory monitoring during training
2. **Regular Checkpoints**: Use frequent checkpoints for long training runs
3. **Disk Space**: Ensure sufficient space for checkpoints and logs
4. **Backup Important Checkpoints**: Copy important checkpoints to safe location
5. **Test Recovery**: Verify checkpoint recovery works before long training runs

## Dependencies

The safeguards system requires:

```bash
pip install psutil
```

This is automatically installed by the setup script.

## Integration with Existing Code

The safeguards are seamlessly integrated into the existing training pipeline:

- **No code changes required** for existing training scripts
- **Automatic activation** when using `OverseerTrainer`
- **Configurable behavior** through `TrainingConfig`
- **Backward compatible** with existing training workflows 