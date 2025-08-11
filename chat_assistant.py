# Interactive Shopify Assistant Chat

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import json

class ShopifyAssistant:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.load_model()
    
    def load_model(self):
        print("🛍️ Loading your trained Shopify Assistant...")
        
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
        
        # Determine request type
        edit_keywords = ["edit", "change", "update", "modify", "alter", "for the", "i want to change"]
        store_keywords = ["create", "store", "sell", "selling", "generate", "make a store", "add", "build", "setup", "start"]
        
        is_edit_request = any(keyword in user_input.lower() for keyword in edit_keywords)
        is_store_request = any(keyword in user_input.lower() for keyword in store_keywords)
        
        # Special case: if it mentions adding products to store, treat as store creation
        if any(word in user_input.lower() for word in ["add", "build", "setup"]) and any(word in user_input.lower() for word in ["store", "shop", "products", "items"]):
            is_store_request = True
            is_edit_request = False
        
        # Handle edit requests differently - these should NOT create new stores
        if is_edit_request and any(word in user_input.lower() for word in ["product", "item", "lavender", "candle"]) and not is_store_request:
            # This is an edit request, not a store creation request
            print("🔧 Detected product edit request - this should use the product editing feature")
            return "I detected that you want to edit an existing product. Please use the 'Manage Products' section to load your products and edit them individually."
        
        # For product descriptions, use a more specific prompt
        if any(word in user_input.lower() for word in ['create', 'write', 'generate', 'description']):
            system_prompt = "You are an expert e-commerce copywriter who creates compelling, premium product descriptions with strong SEO optimization and persuasive marketing copy."
            prompt = f"System: {system_prompt}\n\nUser: {user_input}\n\nAssistant:"
        elif is_store_request and not is_edit_request:
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
        
        # Generate response with improved parameters
        with torch.no_grad():
            outputs = self.model.generate(
                inputs['input_ids'],
                attention_mask=inputs['attention_mask'],
                max_new_tokens=150,  # Reduced for more focused responses
                temperature=0.7,     # Slightly higher for creativity
                do_sample=True,
                repetition_penalty=1.2,  # Higher to reduce repetition
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                early_stopping=True,
                no_repeat_ngram_size=3  # Prevent 3-gram repetition
            )
        
        # Decode and clean
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the assistant's response
        if "Assistant:" in response:
            answer = response.split("Assistant:")[-1].strip()
        else:
            answer = response.replace(prompt, "").strip()
        
        # Clean up response
        if answer:
            # Remove repetitive patterns and limit length
            sentences = answer.split('.')
            clean_sentences = []
            for sentence in sentences[:3]:  # Limit to first 3 sentences
                sentence = sentence.strip()
                if sentence and sentence not in clean_sentences:
                    clean_sentences.append(sentence)
            
            if clean_sentences:
                return '. '.join(clean_sentences) + '.'
        
        return answer[:200] if answer else "Premium product with exceptional quality and value."

    # New: structured JSON concept generation to avoid parsing failures
    def generate_json_concept(self, user_input: str, max_new_tokens: int = 400):
        """
        Ask the model for a strict JSON concept with fields: store_name, tagline, products.
        Returns a dict on success or None on failure.
        """
        system = (
            "You are an expert Shopify store generator. Return ONLY valid JSON with this exact schema: "
            "{\n  \"store_name\": string,\n  \"tagline\": string,\n  \"products\": [\n    { \"name\": string, \"price\": number, \"inventory\": number, \"description\": string }\n  ]\n}. "
            "No extra text, no markdown, no explanations."
        )
        prompt = f"System: {system}\n\nUser: {user_input}\n\nJSON:"

        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=600, truncation=True, padding=True)
        device = next(self.model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model.generate(
                inputs['input_ids'],
                attention_mask=inputs.get('attention_mask'),
                max_new_tokens=max_new_tokens,
                temperature=0.2,
                do_sample=False,
                repetition_penalty=1.1,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                no_repeat_ngram_size=3
            )

        text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Extract JSON payload heuristically
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            json_str = text[start:end+1]
            try:
                data = json.loads(json_str)
                # Basic validation
                if isinstance(data, dict) and 'products' in data and isinstance(data['products'], list):
                    return data
            except Exception:
                pass
        return None

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
