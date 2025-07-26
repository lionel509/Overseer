# Resource-Efficient Training Mode

This document explains how to use the resource-efficient training mode for Overseer, which trades training speed for lower system resource usage.

## Overview

The resource-efficient mode is designed for systems with limited resources or when you need to run other applications during training. It implements several optimizations to reduce memory and CPU usage while maintaining training quality.

## Key Features

### Memory Optimizations
- **Reduced Batch Size**: 4 instead of 16 (75% reduction)
- **Gradient Accumulation**: 16 steps to maintain effective batch size
- **Shorter Sequences**: 1024 tokens instead of 2048 (50% reduction)
- **Lower Memory Thresholds**: 70% RAM, 75% GPU (vs 85%/90%)
- **Gradient Checkpointing**: Enabled for memory efficiency
- **FP16 Precision**: Forced for memory efficiency

### CPU Optimizations
- **Fewer DataLoader Workers**: 1 instead of 4 (75% reduction)
- **Disabled Pin Memory**: Reduces memory usage
- **More Frequent Monitoring**: Better resource tracking

### Training Stability
- **Lower Learning Rate**: 5e-5 instead of 1e-4 (50% reduction)
- **More Frequent Checkpoints**: Every 200 steps instead of 500
- **More Frequent Evaluation**: Every 50 steps instead of 100
- **More Frequent Memory Checks**: Every 15 seconds instead of 30

## Usage

### Method 1: Direct Command
```bash
python main_training.py --resource-efficient [other-options]
```

### Method 2: Convenience Script
```bash
python run_resource_efficient_training.py [other-options]
```

### Method 3: Setup Script
```bash
./setup_resource_efficient_training.sh
```

## Examples

### Basic Resource-Efficient Training
```bash
python main_training.py --resource-efficient
```

### Resource-Efficient Training with Fresh Data
```bash
python main_training.py --resource-efficient --download-data
```

### Resource-Efficient Training with Continuous Learning
```bash
python main_training.py --resource-efficient --continuous-learning
```

### Complete Resource-Efficient Pipeline
```bash
python run_resource_efficient_training.py --download-data --continuous-learning
```

## System Requirements

### Recommended for Resource-Efficient Mode
- **RAM**: 8GB minimum, 16GB recommended
- **GPU Memory**: 4GB minimum, 8GB recommended
- **CPU**: Any modern multi-core processor
- **Storage**: 10GB free space

### When to Use Resource-Efficient Mode
- ✅ Systems with limited RAM (< 16GB)
- ✅ Systems with limited GPU memory (< 8GB)
- ✅ Need to run other applications during training
- ✅ Training on laptops or older hardware
- ✅ Running multiple training sessions
- ✅ Development/testing environments

### When to Use Standard Mode
- ✅ High-end systems with 32GB+ RAM
- ✅ Systems with 16GB+ GPU memory
- ✅ Dedicated training machines
- ✅ Production training runs
- ✅ Need maximum training speed

## Performance Comparison

| Metric | Standard Mode | Resource-Efficient Mode | Change |
|--------|---------------|------------------------|---------|
| Batch Size | 16 | 4 | -75% |
| Sequence Length | 2048 | 1024 | -50% |
| DataLoader Workers | 4 | 1 | -75% |
| Learning Rate | 1e-4 | 5e-5 | -50% |
| Memory Threshold | 85%/90% | 70%/75% | -15% |
| Training Speed | ~100% | ~40-60% | -40-60% |
| Memory Usage | ~100% | ~50-70% | -30-50% |

## Monitoring

The resource-efficient mode includes enhanced monitoring:

- **Memory Usage**: More frequent checks (every 15 seconds)
- **Training Progress**: More frequent logging (every 25 steps)
- **Model Checkpoints**: More frequent saves (every 200 steps)
- **Evaluation**: More frequent evaluation (every 50 steps)

## Troubleshooting

### Out of Memory Errors
If you still encounter memory issues:
1. Reduce `max_sequence_length` further (e.g., to 512)
2. Reduce `batch_size` to 2
3. Increase `gradient_accumulation_steps` to 32
4. Disable mixed precision by setting `mixed_precision = False`

### Slow Training
If training is too slow:
1. Consider using standard mode if resources allow
2. Reduce `gradient_accumulation_steps` (but increase `batch_size` proportionally)
3. Increase `learning_rate` slightly (e.g., to 7e-5)

### System Still Overwhelmed
If the system is still overwhelmed:
1. Close other applications
2. Use CPU-only training (set `use_gpu = False`)
3. Consider using a smaller model variant
4. Train on a subset of data first

## Configuration

You can customize the resource-efficient mode by modifying `training_config.py`:

```python
# Custom resource-efficient settings
config = TrainingConfig()
config.resource_efficient_mode = True
config.batch_size = 2  # Even smaller batch size
config.max_sequence_length = 512  # Even shorter sequences
config.max_ram_percent = 60.0  # Even lower memory threshold
```

## Best Practices

1. **Start Small**: Begin with resource-efficient mode to test your system
2. **Monitor Resources**: Use system monitoring tools during training
3. **Gradual Scaling**: If resources allow, gradually increase batch size
4. **Checkpoint Frequently**: Resource-efficient mode saves more frequently
5. **Use SSD Storage**: Faster I/O for frequent checkpointing
6. **Close Other Apps**: Free up resources for training
7. **Monitor Temperature**: Ensure system doesn't overheat during long training

## Support

If you encounter issues with resource-efficient training:
1. Check the system requirements above
2. Review the troubleshooting section
3. Monitor system resources during training
4. Consider using standard mode if resources allow
5. Report issues with system specifications included 