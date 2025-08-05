#!/usr/bin/env python3
"""Test script for product name extraction"""

from store_builder import CompleteShopifyStoreCreator

def test_product_extraction():
    creator = CompleteShopifyStoreCreator()
    
    # Test prompts
    test_prompts = [
        "Create a store that sells premium water bottles with 30oz capacity, make sure there's 70 in stock",
        "I want a store selling speed cubes for speedcubing competitions",
        "Build a store for eco-friendly yoga mats and meditation accessories",
        "Create a store that sells organic coffee beans from different regions",
        "Make a store that sells toilet paper",
        "Create a store selling wireless headphones"
    ]
    
    print("Testing product name extraction:")
    print("=" * 50)
    
    for prompt in test_prompts:
        print(f"\nPrompt: {prompt}")
        print("-" * 30)
        
        products = creator._extract_products_from_prompt(prompt)
        
        if products:
            for i, product in enumerate(products, 1):
                print(f"Product {i}:")
                print(f"  Name: '{product['name']}'")
                print(f"  Price: ${product['price']}")
                print(f"  Inventory: {product['inventory']}")
        else:
            print("No products extracted")

if __name__ == "__main__":
    test_product_extraction()
