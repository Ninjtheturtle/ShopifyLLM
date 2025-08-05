#!/usr/bin/env python3

# Debug script for product extraction
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from store_builder import CompleteShopifyStoreCreator

def debug_extraction():
    creator = CompleteShopifyStoreCreator()
    prompt = 'create a store with a vanilla candle, lavender candle, and cherry candle'
    
    print(f"Testing prompt: {prompt}")
    print("-" * 50)
    
    # Test the extraction function directly
    try:
        products = creator._extract_products_from_prompt(prompt)
        print(f"Function returned {len(products)} products:")
        for i, p in enumerate(products, 1):
            print(f"  {i}. {p}")
    except Exception as e:
        print(f"Error in extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_extraction()
