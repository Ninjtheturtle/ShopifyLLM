# Interactive Shopify Assistant Chat

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

class ShopifyAssistant:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.load_model()
    
    def load_model(self):
        print("🛍️ Loading your trained Shopify Assistant...")
        
        model_id = "EleutherAI/gpt-neo-1.3B"
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        base_model = AutoModelForCausalLM.from_pretrained(
            model_id, 
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        self.model = PeftModel.from_pretrained(base_model, "./shopify_llama_8b_finetuned/")
        print("✅ Shopify Assistant loaded and ready!")
    
    def respond(self, user_input):
        """Generate a response to user input"""
        
        # Determine request type
        edit_keywords = ["edit", "change", "update", "modify", "alter", "for the", "i want to change"]
        store_keywords = ["create", "store", "sell", "selling", "generate", "make a store"]
        
        is_edit_request = any(keyword in user_input.lower() for keyword in edit_keywords)
        is_store_request = any(keyword in user_input.lower() for keyword in store_keywords)
        
        # Handle edit requests differently - these should NOT create new stores
        if is_edit_request and any(word in user_input.lower() for word in ["product", "item", "lavender", "candle"]):
            # This is an edit request, not a store creation request
            print("🔧 Detected product edit request - this should use the product editing feature")
            return "I detected that you want to edit an existing product. Please use the 'Manage Products' section to load your products and edit them individually."
        
        if is_store_request and not is_edit_request:
            if "for selling" in user_input.lower() or "selling" in user_input.lower():
                prompt = f"Create a Shopify store for: {user_input}\n\nStore Details:"
            else:
                prompt = f"Create a Shopify store for: {user_input}\n\nStore Scaffold:"
        else:
            prompt = f"Shopify Question: {user_input}\n\nAnswer:"
        
        # Tokenize with attention mask
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=400, truncation=True, padding=True)
        
        # Move to device
        device = next(self.model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Generate response
        with torch.no_grad():
            outputs = self.model.generate(
                inputs['input_ids'],
                attention_mask=inputs['attention_mask'],
                max_new_tokens=300,
                temperature=0.4,
                do_sample=True,
                repetition_penalty=1.15,
                pad_token_id=self.tokenizer.eos_token_id,
                early_stopping=True
            )
        
        # Decode and clean
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        answer = response.replace(prompt, "").strip()
        
        # Clean up any repetitive patterns
        lines = answer.split('\n')
        cleaned_lines = []
        for line in lines:
            if line.strip() and line not in cleaned_lines[-3:]:  # Avoid immediate repetition
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines[:15])  # Limit to reasonable length

def interactive_chat():
    assistant = ShopifyAssistant()
    
    print("\n🛍️ Shopify Assistant - Interactive Chat")
    print("=" * 50)
    print("Ask me to create stores or answer Shopify business questions!")
    print("Type 'examples' to see sample questions")
    print("Type 'quit' to exit")
    print("-" * 50)
    
    while True:
        user_input = input("\n💬 You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("👋 Thanks for testing the Shopify Assistant!")
            break
        
        if user_input.lower() == 'examples':
            print("\n📝 Try these examples:")
            print("• Create a store for selling vintage clothing")
            print("• I want to sell handmade candles")
            print("• How do I optimize my product photos?")
            print("• What's the best way to handle inventory?")
            print("• Generate a store for pet accessories")
            continue
        
        if not user_input:
            continue
        
        print("\n🤔 Thinking...")
        
        try:
            response = assistant.respond(user_input)
            print(f"\n🤖 Assistant: {response}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Try rephrasing your question.")

if __name__ == "__main__":
    interactive_chat()
