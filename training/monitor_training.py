#!/usr/bin/env python3
"""
Training Monitor Script
Monitors the progress of Llama + LoRA fine-tuning and runs training
"""

import os
import time
import json
import subprocess
import sys
from pathlib import Path

def monitor_training_progress():
    """Monitor the training progress by checking output directory"""
    
    print("📊 Monitoring Premium Dataset Training...")
    print("=" * 40)
    
    output_dir = "./premium_shopify_v2"
    
    while True:
        try:
            # Check if output directory exists
            if os.path.exists(output_dir):
                print(f"✅ Training directory found: {output_dir}")
                
                # List checkpoints
                checkpoints = []
                for item in os.listdir(output_dir):
                    if item.startswith("checkpoint-"):
                        checkpoints.append(item)
                
                if checkpoints:
                    checkpoints.sort(key=lambda x: int(x.split('-')[1]))
                    print(f"📁 Checkpoints found: {len(checkpoints)}")
                    for cp in checkpoints:
                        print(f"   - {cp}")
                    
                    latest_checkpoint = checkpoints[-1]
                    print(f"🎯 Latest checkpoint: {latest_checkpoint}")
                    
                    # Check for trainer_state.json in latest checkpoint
                    state_file = os.path.join(output_dir, latest_checkpoint, "trainer_state.json")
                    if os.path.exists(state_file):
                        with open(state_file, 'r') as f:
                            state = json.load(f)
                        
                        current_step = state.get("global_step", 0)
                        max_steps = state.get("max_steps", 400)
                        epoch = state.get("epoch", 0)
                        
                        progress = (current_step / max_steps) * 100
                        print(f"📈 Progress: {current_step}/{max_steps} steps ({progress:.1f}%)")
                        print(f"🔄 Epoch: {epoch:.2f}")
                        
                        if current_step >= max_steps:
                            print("🎉 Training completed!")
                            break
                else:
                    print("⏳ Training started but no checkpoints yet...")
            else:
                print("⏳ Waiting for training to start...")
            
            print("-" * 40)
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped by user")
            break
        except Exception as e:
            print(f"⚠️ Error monitoring: {e}")
            time.sleep(10)

def check_gpu_usage():
    """Check GPU usage during training"""
    try:
        import torch
        if torch.cuda.is_available():
            print("🔥 GPU Information:")
            print(f"   Device: {torch.cuda.get_device_name()}")
            print(f"   Memory allocated: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
            print(f"   Memory cached: {torch.cuda.memory_reserved() / 1024**3:.2f} GB")
        else:
            print("💻 Using CPU training")
    except ImportError:
        print("⚠️ PyTorch not available for GPU check")

def run_training_with_monitoring():
    """Run the training script with real-time monitoring"""
    
    print("🎯 STARTING LLAMA + LORA FINE-TUNING")
    print("=" * 50)
    print("📊 Training Configuration:")
    print("   Model: GPT-Neo-1.3B")
    print("   Method: LoRA (r=8, alpha=16)")
    print("   Dataset: 300 premium e-commerce examples")
    print("   Expected time: 30-90 minutes (CPU)")
    print("   Output: ./premium_shopify_v2/")
    print("=" * 50)
    
    # Confirm before starting
    print("\n⚠️  IMPORTANT:")
    print("   Training will use CPU (no CUDA detected)")
    print("   This will take significantly longer than GPU training")
    print("   The model will consume significant CPU resources")
    
    response = input("\nProceed with CPU training? (y/n): ")
    if response.lower() != 'y':
        print("Training cancelled.")
        return
    
    # Start training
    print("\n🚀 Starting training...")
    print("📝 Training logs will appear below:")
    print("-" * 50)
    
    try:
        # Run the training script and capture output
        process = subprocess.Popen(
            [sys.executable, "train_premium_simple.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Real-time output monitoring
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        # Get final return code
        return_code = process.poll()
        
        if return_code == 0:
            print("\n🎉 TRAINING COMPLETED SUCCESSFULLY!")
            print("=" * 50)
            
            # Check if model was saved
            if os.path.exists("./premium_shopify_v2"):
                print("✅ Model saved to: ./premium_shopify_v2/")
                
                # List saved files
                files = os.listdir("./premium_shopify_v2")
                print(f"📁 Saved files ({len(files)} files):")
                for file in sorted(files):
                    print(f"   {file}")
                
                print("\n📝 Next Steps:")
                print("1. Test the model with: python chat_assistant.py")
                print("2. Update chat_assistant.py to use new model path")
                print("3. Compare old vs new model outputs")
                
            else:
                print("⚠️  Model directory not found - check for errors above")
                
        else:
            print(f"\n❌ Training failed with exit code: {return_code}")
            print("Check the error messages above for details")
            
    except KeyboardInterrupt:
        print("\n⏹️  Training interrupted by user")
        if process:
            process.terminate()
    except Exception as e:
        print(f"\n❌ Error running training: {e}")

def check_model_comparison():
    """Compare old and new models if both exist"""
    
    old_model = "./shopify_llama_8b_finetuned/"
    new_model = "./premium_shopify_v2/"
    
    if os.path.exists(old_model) and os.path.exists(new_model):
        print("\n🔍 MODEL COMPARISON AVAILABLE")
        print("=" * 40)
        print(f"✅ Old model: {old_model}")
        print(f"✅ New model: {new_model}")
        print("\nTo compare models:")
        print("1. Load both models in chat_assistant.py")
        print("2. Test same prompts with both models")
        print("3. Compare output quality")

def main():
    """Main function"""
    
    # Pre-flight checks
    if not os.path.exists("premium_ecommerce_300_examples.jsonl"):
        print("❌ Dataset not found: premium_ecommerce_300_examples.jsonl")
        print("Please run: python generate_premium_dataset.py")
        return
    
    if not os.path.exists("train_premium_simple.py"):
        print("❌ Training script not found: train_premium_simple.py")
        return
    
    print("✅ All required files found")
    
    # Choose between monitoring existing training or starting new training
    print("\nOptions:")
    print("1. Start new training with monitoring")
    print("2. Monitor existing training progress")
    
    choice = input("Choose option (1 or 2): ")
    
    if choice == "1":
        run_training_with_monitoring()
    elif choice == "2":
        monitor_training_progress()
    else:
        print("Invalid choice. Exiting.")
        return
    
    # Check for model comparison
    check_model_comparison()

if __name__ == "__main__":
    main()
