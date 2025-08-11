#!/usr/bin/env python3
"""
Simple Premium Dataset Training Script
Uses your existing GPT-Neo + LoRA configuration with the new premium dataset
"""

import json
import torch
import time
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

class ProgressCallback(TrainerCallback):
    """Custom callback to show training progress"""
    
    def __init__(self):
        self.start_time = None
        self.step_times = []
    
    def on_train_begin(self, args, state, control, **kwargs):
        self.start_time = time.time()
        print("🚀 Training started!")
        
    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs:
            current_time = time.time()
            elapsed = current_time - self.start_time
            
            # Calculate ETA
            if state.global_step > 0:
                avg_step_time = elapsed / state.global_step
                remaining_steps = state.max_steps - state.global_step
                eta = remaining_steps * avg_step_time
                eta_str = f"{eta/60:.1f} min"
            else:
                eta_str = "calculating..."
            
            print(f"⚡ Step {state.global_step}/{state.max_steps} | "
                  f"Loss: {logs.get('train_loss', 0):.4f} | "
                  f"ETA: {eta_str}")
    
    def on_save(self, args, state, control, **kwargs):
        print(f"💾 Checkpoint saved at step {state.global_step}")
    
    def on_train_end(self, args, state, control, **kwargs):
        total_time = time.time() - self.start_time
        print(f"✅ Training completed in {total_time/60:.1f} minutes!")

def convert_premium_dataset():
    """Convert the premium dataset to training format"""
    
    print("🔄 Converting premium dataset for training...")
    
    # Load the premium dataset
    examples = []
    with open("premium_ecommerce_300_examples.jsonl", 'r', encoding='utf-8') as f:
        for line in f:
            example = json.loads(line)
            messages = example["messages"]
            
            # Extract components
            system_msg = messages[0]["content"]
            user_msg = messages[1]["content"]
            assistant_msg = messages[2]["content"]
            
            # Create training text in instruction format
            training_text = f"### System:\n{system_msg}\n\n### User:\n{user_msg}\n\n### Assistant:\n{assistant_msg}<|endoftext|>"
            
            examples.append({
                "text": training_text,
                "brand": example.get("brand", ""),
                "category": example.get("category", "")
            })
    
    print(f"✅ Converted {len(examples)} premium examples")
    return examples

def setup_model():
    """Setup your existing GPT-Neo model with LoRA"""
    
    print("🤖 Setting up GPT-Neo-1.3B with LoRA...")
    
    model_name = "EleutherAI/gpt-neo-1.3B"
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None
    )
    
    # Use your existing LoRA configuration
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=8,  # Same as your existing config
        lora_alpha=16,  # Same as your existing config
        lora_dropout=0.1,  # Same as your existing config
        target_modules=["c_attn", "c_proj"],  # Same as your existing config
        bias="none"
    )
    
    # Apply LoRA
    model = get_peft_model(model, lora_config)
    
    # Enable training mode and ensure gradients
    model.train()
    model.enable_input_require_grads()
    
    print("📊 Trainable parameters:")
    model.print_trainable_parameters()
    
    return model, tokenizer

def prepare_dataset(examples, tokenizer):
    """Prepare the dataset for training"""
    
    print("📚 Preparing dataset...")
    
    def tokenize_function(batch):
        # Tokenize the text batch
        tokenized = tokenizer(
            batch["text"],
            truncation=True,
            max_length=512,
            padding="max_length",
            return_tensors=None
        )
        
        # For causal LM, labels are the same as input_ids
        tokenized["labels"] = tokenized["input_ids"].copy()
        return tokenized
    
    # Create dataset
    dataset = Dataset.from_list(examples)
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=["text", "brand", "category"]
    )
    
    # Split into train/eval (90/10 split)
    train_size = int(0.9 * len(tokenized_dataset))
    eval_size = len(tokenized_dataset) - train_size
    
    train_dataset = tokenized_dataset.select(range(train_size))
    eval_dataset = tokenized_dataset.select(range(train_size, train_size + eval_size))
    
    print(f"✅ Dataset prepared:")
    print(f"   Training examples: {len(train_dataset)}")
    print(f"   Evaluation examples: {len(eval_dataset)}")
    
    return train_dataset, eval_dataset

def train_premium_model():
    """Train the model with premium dataset"""
    
    print("🚀 Starting Premium Dataset Training...")
    print("=" * 50)
    
    # Convert dataset
    examples = convert_premium_dataset()
    
    # Setup model and tokenizer
    model, tokenizer = setup_model()
    
    # Prepare dataset
    train_dataset, eval_dataset = prepare_dataset(examples, tokenizer)
    
    # Training arguments (optimized for your hardware)
    training_args = TrainingArguments(
        output_dir="./premium_shopify_v2",
        num_train_epochs=3,
        per_device_train_batch_size=2,  # Small batch size for memory efficiency
        gradient_accumulation_steps=8,  # Effective batch size = 2 * 8 = 16
        gradient_checkpointing=False,  # Disable gradient checkpointing for stability
        warmup_steps=50,
        max_steps=400,  # Adjusted for 300 examples
        learning_rate=2e-4,
        fp16=True if torch.cuda.is_available() else False,
        logging_steps=10,
        save_steps=50,
        save_total_limit=3,
        save_strategy="steps",
        eval_strategy="steps",
        eval_steps=50,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        report_to=None,
        remove_unused_columns=False,
        dataloader_pin_memory=False,
        logging_dir="./logs"
    )
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
        pad_to_multiple_of=8
    )
    
    # Create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
        callbacks=[ProgressCallback()]
    )
    
    # Start training
    print("🔥 Training started...")
    print("💡 This will take approximately 1-2 hours depending on your GPU")
    
    # Clear GPU cache before training
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        print(f"🔥 GPU Memory before training: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
    
    try:
        print("🚀 Starting actual training process...")
        trainer.train()
        
        # Save the final model
        trainer.save_model()
        print("✅ Training completed successfully!")
        print("📁 Model saved to: ./premium_shopify_v2")
        
        return True
        
    except Exception as e:
        print(f"❌ Training failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def update_chat_assistant():
    """Show how to update chat_assistant.py to use the new model"""
    
    update_code = '''
# Update your chat_assistant.py to use the new premium model:

# Change this line:
# self.model = PeftModel.from_pretrained(base_model, "./shopify_llama_8b_finetuned/")

# To this:
self.model = PeftModel.from_pretrained(base_model, "./premium_shopify_v2/")
'''
    
    print(update_code)
    
    # Also create a backup suggestion
    backup_code = '''
# To keep both models and switch between them:

def load_model(self, use_premium=True):
    if use_premium:
        self.model = PeftModel.from_pretrained(base_model, "./premium_shopify_v2/")
        print("✅ Premium model loaded!")
    else:
        self.model = PeftModel.from_pretrained(base_model, "./shopify_llama_8b_finetuned/")
        print("✅ Original model loaded!")
'''
    
    print(backup_code)

def main():
    """Main function"""
    
    print("🎯 PREMIUM DATASET FINE-TUNING")
    print("Using your existing GPT-Neo + LoRA setup")
    print("=" * 40)
    
    # Check if premium dataset exists
    if not os.path.exists("premium_ecommerce_300_examples.jsonl"):
        print("❌ Premium dataset not found!")
        print("Please run: python comprehensive_premium_dataset.py")
        return
    
    # Start training
    success = train_premium_model()
    
    if success:
        print("\n🎉 TRAINING COMPLETE!")
        print("=" * 30)
        print("Expected improvements:")
        print("✅ Much better product descriptions")
        print("✅ Premium brand voice consistency")
        print("✅ SEO-optimized copy")
        print("✅ Conversion-focused language")
        print("✅ Reduced generic descriptions")
        
        print("\n📝 Next steps:")
        update_chat_assistant()
    else:
        print("\n💡 Training tips:")
        print("- Make sure you have enough GPU memory")
        print("- Try reducing batch_size if you get OOM errors")
        print("- Ensure CUDA is properly installed")

if __name__ == "__main__":
    import os
    main()
