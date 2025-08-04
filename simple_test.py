# Simple test of the trained model

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import json

def test_model():
    print("Loading model...")
    
    # Load base model and tokenizer
    model_id = "EleutherAI/gpt-neo-1.3B"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load base model
    base_model = AutoModelForCausalLM.from_pretrained(
        model_id, 
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    # Load trained adapters
    model = PeftModel.from_pretrained(base_model, "./shopify_llama_8b_finetuned/")
    print("✅ Model loaded!")
    
    # Test questions
    test_questions = [
        "Create a store for selling books and reading accessories",
        "I want to sell yoga equipment", 
        "How do I create product bundles?"
    ]
    
    for question in test_questions:
        print(f"\n🔹 Question: {question}")
        
        # Format exactly like training data
        prompt = '{"messages": [{"role": "user", "content": "' + question + '"}, {"role": "assistant", "content": "'
        
        # Tokenize
        inputs = tokenizer(prompt, return_tensors="pt", max_length=300, truncation=True)
        
        # Move to device
        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Generate
        with torch.no_grad():
            outputs = model.generate(
                inputs['input_ids'],
                max_new_tokens=200,
                temperature=0.2,
                do_sample=True,
                repetition_penalty=1.2,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Decode
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the response part
        assistant_response = response.replace(prompt, "")
        
        # Clean up
        if '"}]}' in assistant_response:
            assistant_response = assistant_response.split('"}]}')[0]
        
        print(f"🔹 Response: {assistant_response[:300]}...")
        print("-" * 60)

if __name__ == "__main__":
    test_model()
