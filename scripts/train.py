# train.py

from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from peft import get_peft_model, LoraConfig, TaskType
import torch
import json

# Load the comprehensive dataset from a local JSONL file
print("Loading comprehensive Shopify dataset...")
with open("comprehensive_shopify_data.jsonl", "r", encoding="utf-8") as f:
    data = [json.loads(line) for line in f]

print(f"Loaded {len(data)} training examples")

dataset = Dataset.from_list(data)

# Define prompt formatting
def format_prompt(example):
    messages = example["messages"]
    prompt = ""
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            prompt += f"User: {content}\n"
        elif role == "assistant":
            prompt += f"Assistant: {content}\n"
    return {"text": prompt}

dataset = dataset.map(format_prompt)

# Load tokenizer and model - using GPT-Neo for text generation
model_id = "EleutherAI/gpt-neo-1.3B"  # Good balance of quality and speed
tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=True)

# Add padding token if it doesn't exist
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16)

# Apply LoRA - optimized for GPT-Neo
lora_config = LoraConfig(
    r=8,  # Rank appropriate for 1.3B model
    lora_alpha=16,  # Alpha value
    target_modules=["c_attn", "c_proj"],  # GPT-Neo attention modules
    lora_dropout=0.1,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)
model = get_peft_model(model, lora_config)

# Tokenize dataset with longer max length for comprehensive examples
def tokenize(example):
    # Tokenize the text with longer max length
    tokenized = tokenizer(
        example["text"], 
        truncation=True, 
        padding="max_length", 
        max_length=1024  # Increased for comprehensive store scaffolds
    )
    # For causal language modeling, labels should be the same as input_ids
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized

print("Tokenizing dataset...")
tokenized_dataset = dataset.map(tokenize, batched=True)
tokenized_dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])

print(f"Dataset ready with {len(tokenized_dataset)} examples")
print("Starting training...")

# Training arguments - optimized for 110 examples
training_args = TrainingArguments(
    output_dir="./shopify_llama_8b_results",
    per_device_train_batch_size=1,  # Reduced for better memory management
    gradient_accumulation_steps=4,  # Simulate larger batch size
    num_train_epochs=5,  # More epochs for smaller dataset
    logging_dir="./logs",
    logging_steps=5,  # More frequent logging for small dataset
    save_total_limit=2,
    save_steps=25,  # Save more frequently
    eval_steps=25,
    fp16=True,
    warmup_steps=50,  # Reduced warmup for smaller dataset
    learning_rate=2e-4,  # Slightly lower learning rate
    weight_decay=0.01,
    remove_unused_columns=False,
    dataloader_drop_last=False,  # Keep all data
    report_to=None,  # Disable wandb logging
    seed=42,
    data_seed=42
)

# Data collator
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=data_collator
)

trainer.train()

# Save the final model
model.save_pretrained("./shopify_llama_8b_finetuned")
tokenizer.save_pretrained("./shopify_llama_8b_finetuned")

print("Training completed!")
print("Model saved to: ./shopify_llama_8b_finetuned")
print("You can now use this model for Shopify store generation!")

