#!/usr/bin/env python3
"""
Minimal Training Test Script
Runs a few training steps to verify the setup works before full training
"""

import json
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType

def run_mini_training():
    """Run a minimal training test with just a few examples and steps"""
    
    print("🧪 MINI TRAINING TEST")
    print("Running 10 training steps to verify setup...")
    print("=" * 50)
    
    try:
        # Load just 10 examples for testing
        print("📚 Loading mini dataset...")
        examples = []
        with open("premium_ecommerce_300_examples.jsonl", 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= 10:  # Only use 10 examples
                    break
                example = json.loads(line)
                messages = example["messages"]
                
                # Convert to training format
                system_msg = messages[0]["content"]
                user_msg = messages[1]["content"]
                assistant_msg = messages[2]["content"]
                
                training_text = f"### System:\n{system_msg}\n\n### User:\n{user_msg}\n\n### Assistant:\n{assistant_msg}<|endoftext|>"
                
                examples.append({
                    "text": training_text,
                    "brand": example.get("brand", ""),
                    "category": example.get("category", "")
                })
        
        print(f"✅ Loaded {len(examples)} examples for testing")
        
        # Setup model
        print("🤖 Loading model...")
        model_name = "EleutherAI/gpt-neo-1.3B"
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )
        
        # Apply LoRA
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=8,
            lora_alpha=16,
            lora_dropout=0.1,
            target_modules=["c_attn", "c_proj"],
            bias="none"
        )
        
        model = get_peft_model(model, lora_config)
        
        # Enable training mode and ensure gradients
        model.train()
        model.enable_input_require_grads()
        
        print("✅ Model loaded with LoRA")
        
        # Verify trainable parameters
        trainable_params = 0
        all_param = 0
        for _, param in model.named_parameters():
            all_param += param.numel()
            if param.requires_grad:
                trainable_params += param.numel()
        
        print(f"📊 Trainable: {trainable_params:,} / {all_param:,} parameters")
        
        # Prepare dataset
        print("📊 Preparing dataset...")
        def tokenize_function(batch):
            tokenized = tokenizer(
                batch["text"],
                truncation=True,
                max_length=512,
                padding="max_length",
                return_tensors=None
            )
            tokenized["labels"] = tokenized["input_ids"].copy()
            return tokenized
        
        dataset = Dataset.from_list(examples)
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=["text", "brand", "category"]
        )
        
        print("✅ Dataset prepared")
        
        # Minimal training arguments
        training_args = TrainingArguments(
            output_dir="./mini_test_output",
            num_train_epochs=1,
            per_device_train_batch_size=1,
            gradient_accumulation_steps=2,
            gradient_checkpointing=False,  # Disable gradient checkpointing
            warmup_steps=2,
            max_steps=10,  # Just 10 steps
            learning_rate=2e-4,
            fp16=True if torch.cuda.is_available() else False,
            logging_steps=2,
            save_steps=5,
            save_total_limit=1,
            save_strategy="steps",
            report_to=None,
            remove_unused_columns=False,
            dataloader_pin_memory=False
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
            train_dataset=tokenized_dataset,
            data_collator=data_collator,
        )
        
        print("🔥 Starting mini training...")
        print("This should take about 1-2 minutes...")
        
        # Record initial memory
        if torch.cuda.is_available():
            initial_memory = torch.cuda.memory_allocated() / 1024**3
            print(f"📊 Initial GPU memory: {initial_memory:.2f} GB")
        
        # Start training
        trainer.train()
        
        # Save the model properly
        trainer.save_model()
        print("✅ Model saved successfully!")
        
        # Final memory check
        if torch.cuda.is_available():
            final_memory = torch.cuda.memory_allocated() / 1024**3
            peak_memory = torch.cuda.max_memory_allocated() / 1024**3
            print(f"📊 Final GPU memory: {final_memory:.2f} GB")
            print(f"📊 Peak GPU memory: {peak_memory:.2f} GB")
        
        print("✅ Mini training completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Mini training failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_model_output():
    """Test the model output after mini training"""
    
    print("\n🎯 TESTING MODEL OUTPUT")
    print("=" * 40)
    
    try:
        from peft import PeftModel
        
        # Load the base model
        model_name = "EleutherAI/gpt-neo-1.3B"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        base_model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        # Load the trained LoRA model
        model = PeftModel.from_pretrained(base_model, "./mini_test_output")
        print("✅ Mini-trained model loaded")
        
        # Test generation
        test_prompt = "### System:\nYou are an expert e-commerce copywriter who creates compelling, premium product descriptions.\n\n### User:\nCreate a product description for Apple iPhone with advanced camera and premium design\n\n### Assistant:\n"
        
        inputs = tokenizer(test_prompt, return_tensors="pt")
        
        # Move inputs to the same device as model
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
        
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = generated_text.replace(test_prompt, "").strip()
        
        print("📝 Model output sample:")
        print("-" * 30)
        print(response)
        print("-" * 30)
        
        return True
        
    except Exception as e:
        print(f"❌ Model output test failed: {str(e)}")
        return False

def cleanup():
    """Clean up test files"""
    import shutil
    import os
    
    if os.path.exists("./mini_test_output"):
        shutil.rmtree("./mini_test_output")
        print("🧹 Cleaned up test files")

def main():
    """Main function"""
    
    print("🧪 MINIMAL TRAINING TEST")
    print("This will verify your setup with a quick training run")
    print("=" * 50)
    
    # Run mini training
    success = run_mini_training()
    
    if success:
        print("\n✅ MINI TRAINING SUCCESSFUL!")
        print("Your setup is working correctly!")
        
        # Test model output
        output_success = test_model_output()
        
        if output_success:
            print("\n🎉 EVERYTHING WORKING!")
            print("Ready to run full training:")
            print("   python train_premium_simple.py")
        
    else:
        print("\n❌ Mini training failed")
        print("Please check the error messages above")
    
    # Always cleanup
    cleanup()

if __name__ == "__main__":
    main()
