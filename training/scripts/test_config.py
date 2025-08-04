#!/usr/bin/env python3
"""
Simple test script to verify training configuration works
"""

import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(__file__))

def test_config():
    """Test the training configuration with different flags"""
    
    # Mock the argument parser
    class MockArgs:
        def __init__(self):
            self.download_data = False
            self.use_existing_data = False
            self.continuous_learning = False
            self.resource_efficient = False
            self.mac = False
            self.cpu_only = False
            self.resume_from_checkpoint = None
    
    print("Testing training configuration...")
    
    # Test 1: Default configuration
    print("\n1. Testing default configuration:")
    args = MockArgs()
    from training_config import TrainingConfig
    config = TrainingConfig()
    print(f"   - Batch size: {config.batch_size}")
    print(f"   - Mixed precision: {config.mixed_precision}")
    print(f"   - Use GPU: {config.use_gpu}")
    
    # Test 2: Mac mode
    print("\n2. Testing Mac mode:")
    args.mac = True
    config = TrainingConfig()
    config.mac_mode = True
    config.__post_init__()
    print(f"   - Batch size: {config.batch_size}")
    print(f"   - Mixed precision: {config.mixed_precision}")
    print(f"   - Use GPU: {config.use_gpu}")
    print(f"   - Max sequence length: {config.max_sequence_length}")
    
    # Test 3: CPU-only mode
    print("\n3. Testing CPU-only mode:")
    args.cpu_only = True
    config = TrainingConfig()
    config.cpu_only_mode = True
    config.__post_init__()
    print(f"   - Batch size: {config.batch_size}")
    print(f"   - Mixed precision: {config.mixed_precision}")
    print(f"   - Use GPU: {config.use_gpu}")
    print(f"   - Max sequence length: {config.max_sequence_length}")
    
    # Test 4: Resource-efficient mode
    print("\n4. Testing resource-efficient mode:")
    args.resource_efficient = True
    config = TrainingConfig()
    config.resource_efficient_mode = True
    config.__post_init__()
    print(f"   - Batch size: {config.batch_size}")
    print(f"   - Mixed precision: {config.mixed_precision}")
    print(f"   - Use GPU: {config.use_gpu}")
    print(f"   - Max sequence length: {config.max_sequence_length}")
    
    print("\n✅ Configuration tests completed successfully!")

if __name__ == "__main__":
    test_config() 