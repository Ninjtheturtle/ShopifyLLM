#!/usr/bin/env python3
"""Quick test of AI response generation"""

from chat_assistant import ShopifyAssistant
import json

def test_ai_generation():
    assistant = ShopifyAssistant()
    
    # Test prompts
    prompts = [
        "Create a store selling Rubik's cubes speedcubes",
        "I want to sell candles and home fragrance",
        "Create a yoga and meditation supplies store"
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n🧪 Test {i}: {prompt}")
        print("=" * 60)
        
        try:
            response = assistant.respond(prompt)
            print(f"📝 Full Response:\n{response}")
            print(f"\n📊 Response Stats:")
            print(f"   Length: {len(response)} characters")
            print(f"   Lines: {len(response.split('\n'))}")
            print(f"   Contains 'store': {'store' in response.lower()}")
            print(f"   Contains '$': {'$' in response}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ai_generation()
