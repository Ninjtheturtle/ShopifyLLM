#!/usr/bin/env python3
"""
IMPROVED Premium Dataset Training Script
Enhanced with better progress tracking, memory optimization, and error handling
"""

import json
import torch
import time
import os
import sys
from datetime import datetime, timedelta
from tqdm import tqdm
from datasets import Dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    TrainerCallback
)
from peft import LoraConfig, get_peft_model, TaskType
import gc

class DetailedProgressCallback(TrainerCallback):
    """Enhanced callback with detailed progress tracking and GPU monitoring"""
    
    def __init__(self):
        self.start_time = None
        self.step_times = []
        self.best_loss = float('inf')
        self.last_loss_update = 0
        self.loss_history = []
        self.gpu_available = torch.cuda.is_available()
        
    def get_gpu_memory_info(self):
        """Get GPU memory usage information"""
        if not self.gpu_available:
            return "", ""
        
        try:
            allocated = torch.cuda.memory_allocated(0) / 1024**3  # GB
            cached = torch.cuda.memory_reserved(0) / 1024**3     # GB
            total = torch.cuda.get_device_properties(0).total_memory / 1024**3
            return f"{allocated:.1f}GB", f"{cached:.1f}GB"
        except:
            return "", ""
    
    def format_eta(self, seconds):
        """Format ETA in a human-readable way"""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            return f"{seconds/60:.0f}m {seconds%60:.0f}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours:.0f}h {minutes:.0f}m"
    
    def on_train_begin(self, args, state, control, **kwargs):
        self.start_time = time.time()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print("\n" + "="*80)
        print("🚀 PREMIUM SHOPIFY TRAINING STARTED!")
        print(f"� Start Time: {current_time}")
        print(f"�📊 Total Steps: {state.max_steps:,}")
        print(f"📈 Epochs: {args.num_train_epochs}")
        print(f"🔋 Batch Size: {args.per_device_train_batch_size}")
        print(f"🧠 Learning Rate: {args.learning_rate:.2e}")
        
        if self.gpu_available:
            gpu_name = torch.cuda.get_device_name(0)
            total_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"🎮 GPU: {gpu_name} ({total_memory:.1f}GB)")
        else:
            print("💻 Device: CPU (No CUDA available)")
            
        print("="*80 + "\n")
        
    def on_step_begin(self, args, state, control, **kwargs):
        # Record step start time for throughput calculation
        if len(self.step_times) == 0 or state.global_step % 10 == 0:
            self.step_times.append(time.time())
            if len(self.step_times) > 20:  # Keep only recent times
                self.step_times.pop(0)
        
    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs and state.global_step > 0:
            current_time = time.time()
            elapsed = current_time - self.start_time
            
            # Calculate progress
            progress = state.global_step / state.max_steps * 100
            
            # Calculate throughput (steps/minute)
            if len(self.step_times) >= 2:
                recent_time = current_time - self.step_times[0]
                throughput = (len(self.step_times) - 1) / (recent_time / 60) if recent_time > 0 else 0
            else:
                throughput = 0
            
            # Calculate ETA
            if state.global_step >= 5:  # More accurate after a few steps
                avg_step_time = elapsed / state.global_step
                remaining_steps = state.max_steps - state.global_step
                eta_seconds = remaining_steps * avg_step_time
            else:
                eta_seconds = 0
            
            # Get current metrics
            train_loss = logs.get('train_loss', 0)
            lr = logs.get('learning_rate', 0)
            
            # Track loss history and best loss
            if train_loss > 0:
                self.loss_history.append(train_loss)
                if len(self.loss_history) > 50:  # Keep recent history
                    self.loss_history.pop(0)
                    
                if train_loss < self.best_loss:
                    self.best_loss = train_loss
                    best_indicator = "🏆 NEW BEST"
                    improvement = True
                else:
                    best_indicator = "          "
                    improvement = False
            else:
                best_indicator = "          "
                improvement = False
            
            # Calculate loss trend
            loss_trend = ""
            if len(self.loss_history) >= 10:
                recent_avg = sum(self.loss_history[-5:]) / 5
                older_avg = sum(self.loss_history[-10:-5]) / 5
                if recent_avg < older_avg:
                    loss_trend = "↓"  # Improving
                elif recent_avg > older_avg:
                    loss_trend = "↑"  # Getting worse
                else:
                    loss_trend = "→"  # Stable
            
            # Get GPU memory info
            gpu_mem, gpu_cache = self.get_gpu_memory_info()
            gpu_info = f"GPU: {gpu_mem}" if gpu_mem else ""
            
            # Create enhanced progress bar
            bar_length = 40
            filled_length = int(bar_length * progress // 100)
            bar = "█" * filled_length + "░" * (bar_length - filled_length)
            
            # Format the progress line
            progress_line = (
                f"\r{best_indicator} [{bar}] {progress:5.1f}% | "
                f"Step {state.global_step:3d}/{state.max_steps} | "
                f"Loss: {train_loss:6.4f} {loss_trend} | "
                f"LR: {lr:.1e} | "
            )
            
            # Add throughput and ETA
            if throughput > 0:
                progress_line += f"Speed: {throughput:.1f} step/min | "
            if eta_seconds > 0:
                progress_line += f"ETA: {self.format_eta(eta_seconds)} | "
            
            # Add GPU memory if available
            if gpu_info:
                progress_line += f"{gpu_info} | "
            
            # Add elapsed time
            elapsed_str = self.format_eta(elapsed)
            progress_line += f"Elapsed: {elapsed_str}"
            
            # Print with padding to clear previous line
            print(progress_line.ljust(120), end="", flush=True)
            
            # Special handling for milestones
            if state.global_step % 50 == 0 or improvement:
                print()  # New line for milestone
                if improvement:
                    print(f"🎯 Loss improved to {train_loss:.6f} at step {state.global_step}")
    
    def on_evaluate(self, args, state, control, logs=None, **kwargs):
        if logs:
            eval_loss = logs.get('eval_loss', 0)
            print(f"\n� EVALUATION | Step {state.global_step} | Eval Loss: {eval_loss:.6f}")
            if eval_loss < self.best_loss:
                print(f"🏆 New best evaluation loss: {eval_loss:.6f}")
    
    def on_save(self, args, state, control, **kwargs):
        print(f"\n💾 Checkpoint saved at step {state.global_step}")
    
    def on_train_end(self, args, state, control, **kwargs):
        total_time = time.time() - self.start_time
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n\n🎉 TRAINING COMPLETED!")
        print(f"📅 End Time: {end_time}")
        print(f"⏱️  Total Time: {self.format_eta(total_time)}")
        print(f"🏆 Best Loss: {self.best_loss:.6f}")
        
        if len(self.loss_history) > 1:
            loss_improvement = self.loss_history[0] - self.loss_history[-1]
            improvement_pct = (loss_improvement / self.loss_history[0]) * 100
            print(f"📈 Loss Improvement: {loss_improvement:.6f} ({improvement_pct:.1f}%)")
        
        avg_step_time = total_time / state.max_steps if state.max_steps > 0 else 0
        print(f"⚡ Average Speed: {60/avg_step_time:.1f} steps/min ({avg_step_time:.2f}s/step)")
        print("="*80)
        print(f"\n\n🎉 TRAINING COMPLETED!")
        print(f"⏱️  Total Time: {total_time/60:.1f} minutes")
        print(f"🏆 Best Loss: {self.best_loss:.4f}")
        print("="*60)

def check_system_requirements():
    """Check if system is ready for training"""
    print("🔍 Checking system requirements...")
    
    # Check CUDA
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        memory_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"✅ GPU: {device_name} ({memory_gb:.1f}GB)")
        
        # Clear GPU cache
        torch.cuda.empty_cache()
        gc.collect()
    else:
        print("⚠️  No CUDA available - training will be very slow on CPU")
    
    # Check dataset
    if os.path.exists("premium_ecommerce_clean_300.jsonl"):
        print("✅ Clean premium dataset found")
    else:
        print("❌ Clean premium dataset not found!")
        return False
    
    return True

def convert_premium_dataset():
    """Convert the premium dataset to training format with validation and progress tracking"""
    
    print("🔄 Converting premium dataset for training...")
    
    examples = []
    invalid_count = 0
    line_count = 0
    
    # First pass: count total lines for progress bar
    with open("premium_ecommerce_clean_300.jsonl", 'r', encoding='utf-8') as f:
        total_lines = sum(1 for _ in f)
    
    print(f"📊 Processing {total_lines:,} lines from dataset...")
    
    # Create progress bar for loading
    load_progress = tqdm(
        total=total_lines,
        desc="📖 Converting",
        unit="lines", 
        ncols=100,
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
    )
    
    with open("premium_ecommerce_clean_300.jsonl", 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            load_progress.update(1)
            line_count += 1
            
            try:
                example = json.loads(line)
                messages = example["messages"]
                
                # Validate structure
                if len(messages) != 3:
                    print(f"\n⚠️  Invalid message structure at line {line_num}")
                    invalid_count += 1
                    continue
                
                # Extract components
                system_msg = messages[0]["content"]
                user_msg = messages[1]["content"]
                assistant_msg = messages[2]["content"]
                
                # Validate content
                if not all([system_msg, user_msg, assistant_msg]):
                    print(f"\n⚠️  Empty content at line {line_num}")
                    invalid_count += 1
                    continue
                
                # Create training text in chat format
                training_text = f"<|system|>\n{system_msg}<|endofsystem|>\n<|user|>\n{user_msg}<|endofuser|>\n<|assistant|>\n{assistant_msg}<|endoftext|>"
                
                examples.append({
                    "text": training_text,
                    "brand": example.get("brand", ""),
                    "category": example.get("category", ""),
                    "length": len(training_text)
                })
                
            except json.JSONDecodeError:
                print(f"\n⚠️  JSON decode error at line {line_num}")
                invalid_count += 1
                continue
    
    load_progress.close()
    
    print(f"\n✅ Dataset conversion completed!")
    print(f"   📊 Lines processed: {line_count:,}")
    print(f"   ✅ Valid examples: {len(examples):,}")
    print(f"   ❌ Invalid examples: {invalid_count}")
    print(f"   📈 Success rate: {(len(examples)/line_count)*100:.1f}%")
    
    if invalid_count > 0:
        print(f"⚠️  Note: {invalid_count} examples were skipped due to validation errors")
    
    print(f"✅ Converted {len(examples)} valid premium examples")
    
    # Show statistics
    lengths = [ex["length"] for ex in examples]
    avg_length = sum(lengths) / len(lengths)
    print(f"📊 Average text length: {avg_length:.0f} characters")
    
    return examples

def setup_model_optimized():
    """Setup GPT-Neo model with LoRA and optimizations"""
    
    print("🤖 Setting up GPT-Neo-1.3B with LoRA...")
    
    model_name = "EleutherAI/gpt-neo-1.3B"
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Add special tokens for our format
    special_tokens = ["<|system|>", "<|endofsystem|>", "<|user|>", "<|endofuser|>", "<|assistant|>"]
    tokenizer.add_special_tokens({"additional_special_tokens": special_tokens})
    
    # Load model with optimizations
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
        low_cpu_mem_usage=True
    )
    
    # Resize token embeddings for new special tokens
    model.resize_token_embeddings(len(tokenizer))
    
    # LoRA configuration - optimized for your hardware
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=8,
        lora_alpha=16,
        lora_dropout=0.1,
        target_modules=["c_attn", "c_proj"],
        bias="none",
        inference_mode=False
    )
    
    # Apply LoRA
    model = get_peft_model(model, lora_config)
    
    # Enable training mode and gradients
    model.train()
    model.enable_input_require_grads()
    
    print("📊 Trainable parameters:")
    model.print_trainable_parameters()
    
    return model, tokenizer

def prepare_dataset_optimized(examples, tokenizer):
    """Prepare dataset with better tokenization"""
    
    print("📚 Preparing dataset...")
    
    def tokenize_function(batch):
        # Tokenize with attention to special tokens
        tokenized = tokenizer(
            batch["text"],
            truncation=True,
            max_length=512,
            padding="max_length",
            return_tensors=None,
            add_special_tokens=False  # We already have them in our text
        )
        
        # Labels are the same as input_ids for causal LM
        tokenized["labels"] = tokenized["input_ids"].copy()
        return tokenized
    
    # Create dataset
    print(f"📦 Creating dataset from {len(examples)} examples...")
    dataset = Dataset.from_list(examples)
    
    # Tokenize with enhanced progress bar
    print("🔄 Tokenizing dataset...")
    
    # Create progress bar for tokenization
    tokenize_progress = tqdm(
        total=len(examples),
        desc="🔤 Tokenizing",
        unit="examples",
        ncols=100,
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
    )
    
    def tokenize_with_progress(examples):
        result = tokenize_function(examples)
        tokenize_progress.update(len(examples['text']))
        return result
    
    tokenized_dataset = dataset.map(
        tokenize_with_progress,
        batched=True,
        batch_size=32,  # Process in smaller batches for better progress tracking
        remove_columns=dataset.column_names,
        desc="Tokenizing"
    )
    
    tokenize_progress.close()
    
    # Split dataset
    train_size = int(0.9 * len(tokenized_dataset))
    
    train_dataset = tokenized_dataset.select(range(train_size))
    eval_dataset = tokenized_dataset.select(range(train_size, len(tokenized_dataset)))
    
    print(f"✅ Dataset prepared:")
    print(f"   Training examples: {len(train_dataset)}")
    print(f"   Evaluation examples: {len(eval_dataset)}")
    
    return train_dataset, eval_dataset

def train_with_premium_dataset():
    """Main training function with all optimizations"""
    
    # Check requirements
    if not check_system_requirements():
        return False
    
    # Convert dataset
    examples = convert_premium_dataset()
    if not examples:
        print("❌ No valid examples found!")
        return False
    
    # Setup model
    model, tokenizer = setup_model_optimized()
    
    # Prepare dataset
    train_dataset, eval_dataset = prepare_dataset_optimized(examples, tokenizer)
    
    # Optimized training arguments
    training_args = TrainingArguments(
        output_dir="./premium_shopify_v3",
        num_train_epochs=3,
        per_device_train_batch_size=1,  # Reduced for stability
        gradient_accumulation_steps=16,  # Increased to maintain effective batch size
        gradient_checkpointing=True,  # Enable to save memory
        warmup_steps=25,
        max_steps=300,  # Reduced steps for faster training
        learning_rate=1e-4,  # Slightly lower learning rate
        fp16=torch.cuda.is_available(),
        logging_steps=5,  # More frequent logging
        save_steps=25,
        save_total_limit=3,
        save_strategy="steps",
        eval_strategy="steps",
        eval_steps=25,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        report_to=None,
        remove_unused_columns=False,
        dataloader_pin_memory=False,
        logging_dir="./logs",
        push_to_hub=False,
        resume_from_checkpoint=None,
        dataloader_num_workers=0  # Avoid multiprocessing issues
    )
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
        pad_to_multiple_of=8
    )
    
    # Create trainer with detailed callback
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
        callbacks=[DetailedProgressCallback()]
    )
    
    # Start training
    print("\n🔥 Starting Premium Dataset Training...")
    
    try:
        # Run training
        trainer.train()
        
        # Save the final model
        trainer.save_model()
        print(f"\n✅ Training completed successfully!")
        print(f"📁 Model saved to: ./premium_shopify_v3")
        
        # Test the model
        test_model(model, tokenizer)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Training failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_model(model, tokenizer):
    """Quick test of the trained model"""
    print("\n🧪 Testing trained model...")
    
    test_prompt = "<|system|>\nYou are an expert e-commerce copywriter who creates compelling, premium product descriptions.<|endofsystem|>\n<|user|>\nCreate a premium description for wireless headphones with noise cancellation<|endofuser|>\n<|assistant|>\n"
    
    inputs = tokenizer(test_prompt, return_tensors="pt")
    if torch.cuda.is_available():
        inputs = {k: v.cuda() for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    response = tokenizer.decode(outputs[0][len(inputs['input_ids'][0]):], skip_special_tokens=True)
    print(f"📝 Model response: {response[:200]}...")

def main():
    """Main execution function"""
    print("🎯 PREMIUM DATASET FINE-TUNING (IMPROVED)")
    print("Enhanced with better progress tracking and optimization")
    print("="*60)
    
    success = train_with_premium_dataset()
    
    if success:
        print("\n🎉 Training pipeline completed successfully!")
        print("Your premium e-commerce model is ready to use!")
    else:
        print("\n❌ Training failed. Please check the logs above.")
    
    return success

if __name__ == "__main__":
    main()
