#!/usr/bin/env python3
"""
Training launcher with monitoring for Shopify Llama-8B fine-tuning
"""

import os
import time
import subprocess
import sys
from datetime import datetime

def check_gpu():
    """Check if CUDA is available"""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"🚀 GPU Available: {gpu_name} ({gpu_memory:.1f}GB)")
            return True
        else:
            print("⚠️  No GPU detected. Training will use CPU (much slower)")
            return False
    except ImportError:
        print("❌ PyTorch not installed")
        return False

def estimate_training_time(has_gpu=False):
    """Estimate training time based on hardware"""
    if has_gpu:
        return "30-60 minutes"
    else:
        return "3-6 hours"

def main():
    print("🤖 Shopify Llama-8B Training Launcher")
    print("=" * 50)
    
    # Check system requirements
    has_gpu = check_gpu()
    estimated_time = estimate_training_time(has_gpu)
    
    print(f"\n📊 Training Configuration:")
    print(f"  Dataset: comprehensive_shopify_data.jsonl (110 examples)")
    print(f"  Model: Llama-3.2-8B-Instruct with LoRA")
    print(f"  Estimated time: {estimated_time}")
    print(f"  Output: ./shopify_llama_8b_finetuned/")
    
    # Confirm training
    response = input(f"\n🚀 Start training? (y/n): ")
    if response.lower() != 'y':
        print("Training cancelled.")
        return
    
    # Start training
    start_time = datetime.now()
    print(f"\n⏰ Training started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("📝 Monitor progress in the terminal...")
    print("📁 Logs will be saved to: ./logs/")
    print("💾 Model checkpoints: ./shopify_llama_8b_results/")
    
    try:
        # Run training script
        result = subprocess.run([
            sys.executable, "train.py"
        ], capture_output=False, text=True)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print(f"\n🎉 Training completed successfully!")
            print(f"⏱️  Total time: {duration}")
            print(f"📁 Model saved to: ./shopify_llama_8b_finetuned/")
            print(f"\n🚀 Next steps:")
            print(f"  1. Test your model with: python inference.py")
            print(f"  2. Try generating stores with different prompts")
            print(f"  3. Deploy to your Shopify application")
        else:
            print(f"\n❌ Training failed with exit code: {result.returncode}")
            print(f"Check the logs for error details.")
    
    except KeyboardInterrupt:
        print(f"\n⏹️  Training interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during training: {str(e)}")

if __name__ == "__main__":
    main()
