#!/usr/bin/env python3
"""
Fixed Fine-Tuned Model Loader
Properly handles the tokenizer size mismatch by resizing embeddings
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

class FixedShopifyAssistant:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.load_model()
    
    def load_model(self):
        print("🛍️ Loading Fixed Shopify Assistant...")
        
        model_id = "EleutherAI/gpt-neo-1.3B"
        
        try:
            # Load the fine-tuned tokenizer first
            print("📥 Loading fine-tuned tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained("./premium_shopify_v3/")
            print(f"✅ Fine-tuned tokenizer loaded (vocab size: {len(self.tokenizer)})")
            
            # Load base model
            print("📥 Loading base model...")
            base_model = AutoModelForCausalLM.from_pretrained(
                model_id, 
                torch_dtype=torch.float16,
                device_map="auto"
            )
            
            # Resize token embeddings to match fine-tuned tokenizer
            original_size = base_model.config.vocab_size
            new_size = len(self.tokenizer)
            
            if original_size != new_size:
                print(f"🔧 Resizing embeddings: {original_size} → {new_size}")
                base_model.resize_token_embeddings(new_size)
            
            # Now load the fine-tuned adapter
            print("📥 Loading fine-tuned adapter...")
            self.model = PeftModel.from_pretrained(base_model, "./premium_shopify_v3/")
            print("✅ Fine-tuned model loaded successfully!")
            
        except Exception as e:
            print(f"❌ Fine-tuned loading failed: {e}")
            print("🔄 Falling back to base model...")
            
            # Fallback to base model
            self.tokenizer = AutoTokenizer.from_pretrained(model_id)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id, 
                torch_dtype=torch.float16,
                device_map="auto"
            )
    
    def respond(self, user_input):
        """Generate a response to user input"""
        try:
            # Create a proper prompt for product description generation
            if any(word in user_input.lower() for word in ['create', 'write', 'generate', 'description']):
                system_prompt = "You are an expert e-commerce copywriter who creates compelling, premium product descriptions with strong SEO optimization and persuasive marketing copy. Focus on benefits over features, use sensory language, and create emotional connections with customers."
                
                prompt = f"System: {system_prompt}\n\nUser: {user_input}\n\nAssistant:"
            else:
                # For store creation requests
                prompt = f"Create a comprehensive Shopify store for: {user_input}\n\nStore Details:"
            
            # Tokenize
            inputs = self.tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=512)
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=200,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1
                )
            
            # Decode
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract assistant response
            if "Assistant:" in response:
                assistant_response = response.split("Assistant:")[-1].strip()
            else:
                assistant_response = response[len(prompt):].strip()
            
            # Clean up response
            if assistant_response:
                # Remove any remaining system prompts or formatting
                lines = assistant_response.split('\n')
                clean_lines = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('Store Name:') and not line.startswith('System:'):
                        clean_lines.append(line)
                        if len(clean_lines) >= 3:  # Limit to first few sentences
                            break
                
                return ' '.join(clean_lines) if clean_lines else assistant_response
            
            return "High-quality product with premium features and exceptional value."
            
        except Exception as e:
            print(f"⚠️ Generation error: {e}")
            return "Premium product featuring superior quality and professional craftsmanship."

# Test the fixed model
if __name__ == "__main__":
    print("🧪 TESTING FIXED FINE-TUNED MODEL")
    print("="*50)
    
    assistant = FixedShopifyAssistant()
    
    test_prompts = [
        "Create a premium product description for an iPhone 16 Pro with A18 Pro chip and titanium design",
        "Write SEO-optimized copy for premium water bottles with 30oz capacity",
        "Generate luxury product copy for sustainable bamboo toilet paper"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n🔹 Test {i}: {prompt[:50]}...")
        response = assistant.respond(prompt)
        print(f"📝 Response: {response}")
        print("-" * 30)
