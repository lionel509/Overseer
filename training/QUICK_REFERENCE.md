# Training Quick Reference

## 🚀 Quick Commands

### Setup
```bash
./setup.sh                    # Setup training environment
```

### Training
```bash
python scripts/main_training.py                    # Standard training
python scripts/run_resource_efficient_training.py  # Resource-efficient
python scripts/continuous_learning.py              # Continuous learning
python scripts/fine_tuning.py --model path/to/model # Fine-tuning
```

### Monitoring
```bash
python scripts/memory_monitor.py                   # Monitor memory
tail -f logs/training.log                         # Watch logs
```

### Testing
```bash
python scripts/test_config.py                      # Test configuration
python scripts/test_continuous_learning.py         # Test continuous learning
```

### Interactive
```bash
jupyter notebook notebooks/overseer_training_notebook.ipynb
```

## 📁 Key Files

### Configuration
- `configs/training_config.py` - Main training settings
- `configs/requirements.txt` - Python dependencies

### Main Scripts
- `scripts/main_training.py` - Training entry point
- `scripts/fine_tuning.py` - Model fine-tuning
- `scripts/continuous_learning.py` - Continuous learning
- `scripts/memory_monitor.py` - Memory monitoring

### Documentation
- `README.md` - Main training guide
- `docs/README_training_flags.md` - Training parameters
- `docs/README_resource_efficient.md` - Resource optimization
- `docs/README_safeguards.md` - Safety features

## 🎯 Common Workflows

### 1. First Time Setup
```bash
cd training
./setup.sh
python scripts/test_config.py
```

### 2. Standard Training
```bash
python scripts/main_training.py
tail -f logs/training.log
```

### 3. Resource-Limited Training
```bash
python scripts/run_resource_efficient_training.py
python scripts/memory_monitor.py
```

### 4. Model Fine-Tuning
```bash
python scripts/fine_tuning.py --model models/previous_model
```

### 5. Continuous Learning
```bash
python scripts/continuous_learning.py --data new_data.csv
```

## 🔧 Configuration Tips

### Memory Issues
- Use `run_resource_efficient_training.py`
- Monitor with `memory_monitor.py`
- Reduce batch size in `training_config.py`

### Performance Issues
- Check `logs/training.log` for errors
- Run `test_config.py` to validate settings
- Use continuous learning for incremental improvements

### Data Issues
- Validate data with `data_preparation.py`
- Check data format in `training_config.py`
- Use `kaggle_data_collector.py` for data collection

## 📊 Monitoring Commands

```bash
# Watch training progress
tail -f logs/training.log

# Monitor memory usage
python scripts/memory_monitor.py --interval 30

# Check model files
ls -la models/

# Check data files
ls -la data/
```

## 🆘 Troubleshooting

### Common Errors
1. **Out of Memory**: Use resource-efficient mode
2. **Config Errors**: Run `test_config.py`
3. **Import Errors**: Check `requirements.txt`
4. **Data Errors**: Validate with `data_preparation.py`

### Quick Fixes
```bash
# Reinstall dependencies
pip install -r configs/requirements.txt

# Test configuration
python scripts/test_config.py

# Check logs
cat logs/training.log | tail -20
```

## 🎉 Success Indicators

- ✅ Models saved in `models/`
- ✅ Training logs show convergence
- ✅ Memory usage within limits
- ✅ Evaluation metrics improving 