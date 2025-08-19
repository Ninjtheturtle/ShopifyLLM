import json
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments, 
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType
from datasets import Dataset
import os

class ShopifyFineTuner:
    def __init__(self, model_name="EleutherAI/gpt-neo-1.3B", output_dir="premium_shopify_v3"):
        self.model_name = model_name
        self.output_dir = output_dir
        self.tokenizer = None
        self.model = None
        
    def load_model_and_tokenizer(self):
        """Load the base model and tokenizer"""
        print(f"Loading model: {self.model_name}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        
        # Configure LoRA
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=16,  # Low rank
            lora_alpha=32,
            lora_dropout=0.1,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj"]
        )
        
        # Apply LoRA to model
        self.model = get_peft_model(self.model, lora_config)
        print(f"Model loaded with LoRA adapters")
        
    def load_dataset(self, dataset_path="dataset.jsonl"):
        """Load and preprocess the training dataset"""
        print(f"Loading dataset from: {dataset_path}")
        
        # Load JSONL data
        data = []
        with open(dataset_path, 'r', encoding='utf-8') as f:
            for line in f:
                item = json.loads(line.strip())
                data.append(item)
        
        print(f"Loaded {len(data)} training examples")
        
        # Convert to training format
        training_texts = []
        for item in data:
            # Format: User: {prompt} Assistant: {response}
            if 'user' in item and 'assistant' in item:
                training_text = f"User: {item['user']}\nAssistant: {item['assistant']}<|endoftext|>"
            elif 'prompt' in item and 'completion' in item:
                training_text = f"User: {item['prompt']}\nAssistant: {item['completion']}<|endoftext|>"
            else:
                # Handle other formats
                training_text = f"{json.dumps(item)}<|endoftext|>"
                
            training_texts.append(training_text)
        
        # Tokenize
        def tokenize_function(examples):
            return self.tokenizer(
                examples['text'],
                truncation=True,
                padding=True,
                max_length=512,
                return_tensors="pt"
            )
        
        # Create dataset
        dataset = Dataset.from_dict({"text": training_texts})
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        
        return tokenized_dataset
    
    def train(self, dataset_path="dataset.jsonl", epochs=3, learning_rate=2e-4):
        """Fine-tune the model"""
        print("Starting fine-tuning process...")
        
        # Load model and dataset
        self.load_model_and_tokenizer()
        train_dataset = self.load_dataset(dataset_path)
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            overwrite_output_dir=True,
            num_train_epochs=epochs,
            per_device_train_batch_size=2,
            gradient_accumulation_steps=8,
            warmup_steps=100,
            learning_rate=learning_rate,
            fp16=True,
            logging_steps=10,
            save_steps=500,
            eval_steps=500,
            save_total_limit=2,
            prediction_loss_only=True,
            remove_unused_columns=False,
            dataloader_pin_memory=False,
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,
        )
        
        # Initialize trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            data_collator=data_collator,
        )
        
        # Train
        print("Training started...")
        trainer.train()
        
        # Save model
        print(f"Saving fine-tuned model to {self.output_dir}")
        trainer.save_model()
        self.tokenizer.save_pretrained(self.output_dir)
        
        print("Fine-tuning completed!")
        
    def test_model(self, prompt="Create a premium product description for workout clothes"):
        """Test the fine-tuned model"""
        if self.model is None or self.tokenizer is None:
            print("Loading model for testing...")
            self.load_model_and_tokenizer()
            
        # Format prompt
        formatted_prompt = f"User: {prompt}\nAssistant:"
        
        # Tokenize
        inputs = self.tokenizer(formatted_prompt, return_tensors="pt")
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=150,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"Prompt: {prompt}")
        print(f"Response: {response}")
        
        return response

def main():
    """Main training function"""
    print("🚀 Starting Shopify Premium Product Description Fine-Tuning")
    
    # Initialize fine-tuner
    trainer = ShopifyFineTuner()
    
    # Check if dataset exists
    if not os.path.exists("dataset.jsonl"):
        print("❌ dataset.jsonl not found! Please ensure training data exists.")
        return
    
    # Start training
    try:
        trainer.train(
            dataset_path="dataset.jsonl",
            epochs=3,
            learning_rate=2e-4
        )
        
        # Test the model
        print("\n🧪 Testing fine-tuned model...")
        trainer.test_model("Create a premium workout shirt description")
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()