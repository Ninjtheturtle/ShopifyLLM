# app.py - Simple web interface for Shopify Assistant

import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import time

@st.cache_resource
def load_model():
    """Load the model once and cache it"""
    with st.spinner("Loading Shopify Assistant..."):
        model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        base_model = AutoModelForCausalLM.from_pretrained(
            model_id, 
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        model = PeftModel.from_pretrained(base_model, "./fine_tuned_model")
        
    return model, tokenizer

def generate_response(model, tokenizer, question):
    """Generate response from the model"""
    prompt = f"User: {question}\nAssistant:"
    
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=256,
            num_return_sequences=1,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id
        )
    
    full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    if "Assistant:" in full_response:
        response = full_response.split("Assistant:")[-1].strip()
    else:
        response = full_response.replace(prompt, "").strip()
    
    return response

def main():
    st.set_page_config(
        page_title="Shopify Assistant",
        page_icon="🛍️",
        layout="wide"
    )
    
    st.title("🛍️ Shopify Assistant")
    st.subline("Your AI-powered guide to setting up and managing your Shopify store")
    
    # Load model
    model, tokenizer = load_model()
    
    # Sidebar with example questions
    with st.sidebar:
        st.header("💡 Try asking:")
        example_questions = [
            "How do I add a product to my store?",
            "What payment methods should I enable?",
            "How do I set up shipping rates?",
            "How can I improve my product photos?",
            "What's the best way to handle returns?",
            "How do I optimize my store for SEO?"
        ]
        
        for question in example_questions:
            if st.button(question, key=question):
                st.session_state.user_input = question
    
    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about Shopify..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_response(model, tokenizer, prompt)
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using TinyLlama and LoRA fine-tuning")

if __name__ == "__main__":
    main()
