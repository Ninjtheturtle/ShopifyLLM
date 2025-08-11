#!/usr/bin/env python3
"""
Test the updated keyword detection
"""

def test_keyword_detection():
    # Updated logic from chat_assistant.py
    def detect_request_type(user_input):
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
            return "EDIT_REQUEST"
        elif is_store_request and not is_edit_request:
            return "STORE_REQUEST"
        else:
            return "OTHER"
    
    # Test cases
    test_cases = [
        "add some workout clothes for men and women",
        "create a store that sells premium water bottles",
        "edit the lavender candle product",
        "add products to the store",
        "build a shop for electronics",
        "setup a store for fashion items",
        "i want to change the product description"
    ]
    
    print("🧪 TESTING KEYWORD DETECTION")
    print("="*50)
    
    for test_case in test_cases:
        result = detect_request_type(test_case)
        print(f"📝 Input: '{test_case}'")
        print(f"🎯 Result: {result}")
        print("-" * 30)

if __name__ == "__main__":
    test_keyword_detection()
