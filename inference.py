# inference.py - Test your fine-tuned Shopify assistant

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

def load_shopify_assistant():
    """Load the fine-tuned Shopify assistant model"""
    print("Loading Shopify Assistant...")
    
    # Load base model and tokenizer
    model_id = "EleutherAI/gpt-neo-1.3B"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    
    # Add padding token if it doesn't exist
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load base model
    base_model = AutoModelForCausalLM.from_pretrained(
        model_id, 
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    # Load LoRA adapters from your trained model
    model = PeftModel.from_pretrained(base_model, "./shopify_llama_8b_finetuned/")
    
    print("✅ Shopify Assistant loaded successfully!")
    return model, tokenizer

def generate_response(model, tokenizer, user_question, max_length=400):
    """Generate a response to a user question"""
    
    # Use the exact same format as the training data
    formatted_input = '{\"messages\": [{\"role\": \"user\", \"content\": \"' + user_question + '\"}, {\"role\": \"assistant\", \"content\": \"'
    
    # Tokenize
    inputs = tokenizer(formatted_input, return_tensors="pt", truncation=True, max_length=400)
    
    # Move to device
    device = next(model.parameters()).device
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    # Generate with very conservative settings
    with torch.no_grad():
        outputs = model.generate(
            inputs['input_ids'],
            attention_mask=inputs['attention_mask'],
            max_new_tokens=max_length,
            temperature=0.1,
            do_sample=True,
            top_p=0.9,
            repetition_penalty=1.3,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id
        )
    
    # Decode
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract response
    response = generated_text.replace(formatted_input, "").strip()
    
    # Clean up JSON artifacts
    if '\"}]}' in response:
        response = response.split('\"}]}')[0]
    elif '\"}}' in response:
        response = response.split('\"}}')[0]
    elif '"}' in response:
        response = response.split('"}')[0]
    
    return response.strip()

def interactive_chat():
    """Run an interactive chat session with the Shopify assistant"""
    model, tokenizer = load_shopify_assistant()
    
    print("\n🛍️ Shopify Assistant Ready!")
    print("Ask me anything about setting up and managing your Shopify store.")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("👋 Thanks for using Shopify Assistant!")
            break
        
        if not user_input:
            continue
        
        print("🤔 Thinking...")
        response = generate_response(model, tokenizer, user_input)
        print(f"Assistant: {response}\n")

def test_predefined_questions():
    """Test the model with some predefined questions"""
    model, tokenizer = load_shopify_assistant()
    
    test_questions = [
        "Create a store for selling books and reading accessories",
        "I want to sell garden tools and outdoor plants", 
        "How do I build an effective customer loyalty program?",
        "How do I create compelling product bundles that increase sales?",
        "Generate a store for selling yoga and fitness equipment",
        "How do I handle international shipping and customs?",
        "Create a store for selling handmade soaps and natural skincare"
    ]
    
    print("\n🧪 Testing Shopify Assistant with sample questions:\n")
    
    for i, question in enumerate(test_questions, 1):
        print(f"Q{i}: {question}")
        response = generate_response(model, tokenizer, question)
        print(f"A{i}: {response}\n")
        print("-" * 80 + "\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_predefined_questions()
    else:
        interactive_chat()
