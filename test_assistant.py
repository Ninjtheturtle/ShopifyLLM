# Interactive Shopify Assistant - Properly formatted

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

class ShopifyAssistant:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.load_model()
    
    def load_model(self):
        print("🛍️ Loading Shopify Assistant...")
        
        # Load base model and tokenizer
        model_id = "EleutherAI/gpt-neo-1.3B"
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load base model
        base_model = AutoModelForCausalLM.from_pretrained(
            model_id, 
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        # Load fine-tuned adapters
        self.model = PeftModel.from_pretrained(base_model, "./shopify_llama_8b_finetuned/")
        print("✅ Shopify Assistant ready!")
    
    def generate_store_scaffold(self, business_idea):
        """Generate a store scaffold for a business idea"""
        
        # Format as a store creation request
        prompt = f"Create a Shopify store for: {business_idea}\n\nStore Scaffold:"
        
        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=300, truncation=True)
        
        # Move to device
        device = next(self.model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                inputs['input_ids'],
                max_new_tokens=300,
                temperature=0.4,
                do_sample=True,
                repetition_penalty=1.1,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode and clean
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        answer = response.replace(prompt, "").strip()
        
        return answer
    
    def answer_business_question(self, question):
        """Answer a general business question"""
        
        prompt = f"Shopify Business Question: {question}\n\nAnswer:"
        
        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=300, truncation=True)
        
        # Move to device
        device = next(self.model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                inputs['input_ids'],
                max_new_tokens=250,
                temperature=0.3,
                do_sample=True,
                repetition_penalty=1.2,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode and clean
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        answer = response.replace(prompt, "").strip()
        
        return answer

def main():
    assistant = ShopifyAssistant()
    
    print("\n🛍️ Shopify Assistant - Trained Model Test")
    print("=" * 50)
    
    # Test store creation prompts
    store_ideas = [
        "selling handmade jewelry and accessories",
        "yoga and fitness equipment",
        "children's educational toys",
        "organic skincare products"
    ]
    
    print("\n📋 STORE GENERATION TESTS:")
    print("-" * 30)
    
    for i, idea in enumerate(store_ideas, 1):
        print(f"\n{i}. Business Idea: {idea}")
        response = assistant.generate_store_scaffold(idea)
        print(f"   Response: {response[:200]}...")
        print()
    
    # Test business questions
    business_questions = [
        "How do I price my products competitively?",
        "What are effective email marketing strategies?",
        "How do I handle customer returns?"
    ]
    
    print("\n❓ BUSINESS QUESTION TESTS:")
    print("-" * 30)
    
    for i, question in enumerate(business_questions, 1):
        print(f"\n{i}. Question: {question}")
        response = assistant.answer_business_question(question)
        print(f"   Response: {response[:200]}...")
        print()

if __name__ == "__main__":
    main()
