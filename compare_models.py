# Test the base model vs fine-tuned model

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

def test_comparison():
    print("Loading base model...")
    
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
    
    print("Loading fine-tuned model...")
    # Load trained adapters
    finetuned_model = PeftModel.from_pretrained(base_model, "./shopify_llama_8b_finetuned/")
    
    question = "Create a store for selling books and reading accessories"
    
    # Test base model
    print(f"\n📚 Question: {question}")
    
    # Simple prompt for base model
    simple_prompt = f"Question: {question}\nAnswer:"
    
    inputs = tokenizer(simple_prompt, return_tensors="pt", max_length=200, truncation=True)
    device = next(base_model.parameters()).device
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    print("\n🔸 Base Model Response:")
    with torch.no_grad():
        outputs = base_model.generate(
            inputs['input_ids'],
            max_new_tokens=150,
            temperature=0.7,
            do_sample=True,
            repetition_penalty=1.1,
            pad_token_id=tokenizer.eos_token_id
        )
    
    base_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    base_answer = base_response.replace(simple_prompt, "").strip()
    print(base_answer[:400])
    
    print("\n🔸 Fine-tuned Model Response:")
    # Try a simpler format for fine-tuned model
    simple_ft_prompt = f"Create a Shopify store for: {question.lower()}\n\nStore Details:"
    
    inputs = tokenizer(simple_ft_prompt, return_tensors="pt", max_length=200, truncation=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = finetuned_model.generate(
            inputs['input_ids'],
            max_new_tokens=150,
            temperature=0.3,
            do_sample=True,
            repetition_penalty=1.2,
            pad_token_id=tokenizer.eos_token_id
        )
    
    ft_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    ft_answer = ft_response.replace(simple_ft_prompt, "").strip()
    print(ft_answer[:400])

if __name__ == "__main__":
    test_comparison()
