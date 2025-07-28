# Overseer Training Flags

This document describes the available training flags for the Overseer model training script.

## Available Flags

### `--mac`
Enables Mac/Apple Silicon optimizations for training on Apple Silicon Macs.

**Features:**
- Disables FP16 mixed precision (not supported on MPS)
- Uses MPS device for GPU acceleration
- Optimized memory management for Apple Silicon
- Ultra-conservative batch size (1) with increased gradient accumulation (32)
- Reduced sequence length (256) for memory efficiency
- Lower memory thresholds (RAM 60%, GPU 70%)

**Usage:**
```bash
python3 main_training.py --mac
```

### `--resource-efficient`
Enables resource-efficient mode for systems with limited resources.

**Features:**
- Reduced batch size (4) with increased gradient accumulation (16)
- Lower learning rate (5e-5) for stable training
- Reduced sequence length (1024) for memory efficiency
- Lower memory thresholds (RAM 70%, GPU 75%)
- More frequent evaluation and saving

**Usage:**
```bash
python3 main_training.py --resource-efficient
```

### `--cpu-only`
Forces CPU-only training for systems with very limited GPU memory.

**Features:**
- Disables GPU usage entirely
- Ultra-conservative batch size (1) with high gradient accumulation (64)
- Very low learning rate (1e-5) for stable training
- Minimal sequence length (128) for memory efficiency
- Lowest memory thresholds (RAM 50%, no GPU usage)
- Most frequent evaluation and saving

**Usage:**
```bash
python3 main_training.py --cpu-only
```

### `--download-data`
Downloads fresh training data from Kaggle.

**Usage:**
```bash
python3 main_training.py --mac --download-data
```

### `--use-existing-data`
Uses existing processed data instead of downloading fresh data.

**Usage:**
```bash
python3 main_training.py --mac --use-existing-data
```

### `--continuous-learning`
Includes user interaction data in training.

**Usage:**
```bash
python3 main_training.py --mac --continuous-learning
```

### `--resume-from-checkpoint`
Resumes training from a specific checkpoint.

**Usage:**
```bash
python3 main_training.py --mac --resume-from-checkpoint ./checkpoints/checkpoint-1000
```

## Flag Precedence

The flags have the following precedence order (highest to lowest):
1. `--mac` (takes precedence over `--resource-efficient`)
2. `--cpu-only` (takes precedence over `--resource-efficient`)
3. `--resource-efficient`
4. Default mode

## Recommended Usage

### For Apple Silicon Macs
```bash
# Basic Mac training
python3 main_training.py --mac

# Mac training with fresh data
python3 main_training.py --mac --download-data

# Mac training with continuous learning
python3 main_training.py --mac --continuous-learning
```

### For Systems with Limited Memory
```bash
# Resource-efficient training
python3 main_training.py --resource-efficient

# CPU-only training (if GPU memory is insufficient)
python3 main_training.py --cpu-only
```

### For Development/Testing
```bash
# Quick test with existing data
python3 main_training.py --mac --use-existing-data
```

## Memory Management

The training script includes built-in memory safeguards:
- Automatic memory monitoring
- Early stopping if memory usage exceeds thresholds
- Checkpoint saving for recovery
- Graceful handling of out-of-memory errors

## Troubleshooting

### Memory Issues
If you encounter memory issues:
1. Try `--cpu-only` mode
2. Reduce the model size in `training_config.py`
3. Close other applications to free up memory
4. Consider using a smaller base model

### Performance Issues
- Mac mode is optimized for Apple Silicon but may be slower than GPU training
- CPU-only mode is significantly slower but uses minimal memory
- Resource-efficient mode provides a balance between speed and memory usage

## Configuration Details

All training parameters can be modified in `training_config.py`:
- Batch sizes
- Learning rates
- Memory thresholds
- Sequence lengths
- Evaluation frequencies 