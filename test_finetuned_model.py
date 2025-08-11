#!/usr/bin/env python3
"""
Test the Fine-Tuned Model Directly
Quick test to see if our fine-tuned model is working properly
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import json

def test_finetuned_model():
    """Test the fine-tuned model with some sample prompts"""
    print("🧪 TESTING FINE-TUNED MODEL")
    print("="*50)
    
    try:
        model_id = "EleutherAI/gpt-neo-1.3B" 
        print(f"📥 Loading base model: {model_id}")
        
        # Load base tokenizer first
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Load base model
        base_model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        
        print(f"🔧 Original vocab size: {base_model.config.vocab_size}")
        
        # Try to load the fine-tuned model
        try:
            print("📥 Loading fine-tuned model...")
            model = PeftModel.from_pretrained(base_model, "./premium_shopify_v3/")
            print("✅ Fine-tuned model loaded successfully!")
            use_finetuned = True
        except Exception as e:
            print(f"❌ Failed to load fine-tuned model: {e}")
            print("🔄 Using base model for testing...")
            model = base_model
            use_finetuned = False
        
        # Test prompts
        test_prompts = [
            "Create a premium product description for an iPhone 16 Pro with A18 Pro chip and titanium design",
            "Write SEO-optimized copy for premium water bottles with 30oz capacity",
            "Generate luxury product copy for Nike Air Max running shoes with ZoomX foam",
            "Create eco-friendly description for sustainable bamboo toilet paper"
        ]
        
        print(f"\n🎯 Testing {'Fine-Tuned' if use_finetuned else 'Base'} Model:")
        print("-" * 50)
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n🔹 Test {i}: {prompt[:50]}...")
            
            # Tokenize input
            system_prompt = "You are an expert e-commerce copywriter who creates compelling, premium product descriptions with strong SEO optimization and persuasive marketing copy."
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}\n\nAssistant:"
            
            inputs = tokenizer(full_prompt, return_tensors="pt", padding=True, truncation=True, max_length=512)
            inputs = {k: v.to(model.device) for k, v in inputs.items()}
            
            # Generate response
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=150,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id
                )
            
            # Decode response
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract just the assistant's response
            if "Assistant:" in response:
                assistant_response = response.split("Assistant:")[-1].strip()
            else:
                assistant_response = response[len(full_prompt):].strip()
            
            print(f"📝 Response: {assistant_response[:200]}...")
            print("-" * 30)
        
        print(f"\n✅ Model testing completed!")
        print(f"🎯 Model used: {'Fine-Tuned LoRA' if use_finetuned else 'Base GPT-Neo-1.3B'}")
        
        return use_finetuned
        
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_finetuned_model()
