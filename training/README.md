# Overseer Training Framework

This directory contains the AI training framework for the Overseer system, completely restructured for better organization and enhanced functionality.

## 📁 Directory Structure

```
training/
├── README.md                    # This file - main training guide
├── QUICK_REFERENCE.md           # Quick reference for training commands
├── ORGANIZATION_SUMMARY.md      # Complete organizational overview
├── setup.sh                    # Training environment setup script
├── scripts/                    # Python training scripts
│   ├── main_training.py         # Main training entry point
│   ├── fine_tuning.py           # Model fine-tuning logic
│   ├── continuous_learning.py   # Continuous learning system
│   ├── data_preparation.py      # Data preprocessing
│   ├── evaluation.py            # Model evaluation
│   ├── memory_monitor.py        # Memory usage monitoring
│   ├── kaggle_data_collector.py # Data collection from Kaggle
│   ├── training_safeguards.py   # Training safety measures
│   ├── safeguards.py            # Additional safety features
│   ├── test_config.py           # Configuration testing
│   └── test_continuous_learning.py # Continuous learning tests
├── configs/                     # Configuration files
│   ├── training_config.py       # Main training configuration
│   └── requirements.txt         # Python dependencies
├── notebooks/                   # Jupyter notebooks
│   └── overseer_training_notebook.ipynb # Interactive training notebook
├── docs/                        # Documentation
│   ├── README_training_flags.md # Training flags documentation
│   ├── README_resource_efficient.md # Resource-efficient training guide
│   └── README_safeguards.md     # Safety features documentation
├── data/                        # Training data (created during training)
├── models/                      # Trained models (created during training)
└── logs/                        # Training logs (created during training)
```

**Note**: This is a complete restructure from the previous training setup. The old Python files and shell scripts have been moved to the `scripts/` directory for better organization and the `docs/` subdirectory now contains comprehensive documentation.

## 🚀 Quick Start

### 1. Setup Training Environment
```bash
cd training
./setup.sh
```

### 2. Run Training
```bash
# Basic training
python scripts/main_training.py

# Resource-efficient training (removed - check docs/ for alternatives)
# python scripts/run_resource_efficient_training.py

# Interactive notebook (if available)
jupyter notebook notebooks/overseer_training_notebook.ipynb
```

### 3. Monitor Training
```bash
# Monitor memory usage
python scripts/memory_monitor.py

# Check training progress
tail -f logs/training.log
```

## 📚 Documentation

- **[Training Flags Guide](docs/README_training_flags.md)** - Complete guide to training parameters
- **[Resource-Efficient Training](docs/README_resource_efficient.md)** - How to train with limited resources
- **[Safety Features](docs/README_safeguards.md)** - Training safety and safeguards

## 🔧 Configuration

### Training Configuration
Edit `configs/training_config.py` to customize:
- Model parameters
- Training hyperparameters
- Data sources
- Output settings

### Environment Setup
The training environment is configured in:
- `configs/requirements.txt` - Python dependencies
- `scripts/setup_training.sh` - Environment setup script

## 🎯 Training Modes

### 1. Standard Training
```bash
python scripts/main_training.py
```

### 2. Resource-Efficient Training
```bash
python scripts/run_resource_efficient_training.py
```

### 3. Continuous Learning
```bash
python scripts/continuous_learning.py
```

### 4. Fine-Tuning
```bash
python scripts/fine_tuning.py --model path/to/model
```

## 📊 Monitoring

### Memory Monitoring
```bash
python scripts/memory_monitor.py --interval 30
```

### Training Progress
- Check `logs/training.log` for detailed logs
- Monitor `data/` for training data
- Check `models/` for saved models

## 🛡️ Safety Features

The training framework includes multiple safety measures:
- **Memory monitoring** - Prevents OOM errors
- **Training safeguards** - Validates training parameters
- **Resource limits** - Prevents system overload
- **Data validation** - Ensures data quality

## 🔍 Testing

### Test Configuration
```bash
python scripts/test_config.py
```

### Test Continuous Learning
```bash
python scripts/test_continuous_learning.py
```

## 📈 Performance Tips

1. **Use resource-efficient mode** for limited hardware
2. **Monitor memory usage** during training
3. **Use continuous learning** for incremental improvements
4. **Validate data** before training
5. **Check logs** for issues

## 🆘 Troubleshooting

### Common Issues
1. **Out of Memory**: Use resource-efficient training mode
2. **Configuration Errors**: Run `test_config.py`
3. **Data Issues**: Check data validation in `data_preparation.py`

### Getting Help
- Check the documentation in `docs/`
- Review training logs in `logs/`
- Test configuration with `test_config.py`

## 🎉 Success Metrics

Training is successful when:
- ✅ Models are saved in `models/`
- ✅ Training logs show convergence
- ✅ Memory usage stays within limits
- ✅ Evaluation metrics improve

---

**Happy Training! 🚀** 