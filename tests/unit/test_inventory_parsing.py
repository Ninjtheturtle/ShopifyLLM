#!/usr/bin/env python3
"""Test inventory parsing functionality"""

import re

def test_inventory_parsing():
    """Test that inventory parsing works correctly"""
    
    # Test prompts
    test_prompts = [
        "make a store that sells stainless steel waterbottles make sure theres 70 in stock and they are black",
        "create toilet paper store with 25 inventory",
        "sell candles with 100 pieces",
        "make sure there are 150 units of headphones"
    ]
    
    for prompt in test_prompts:
        print(f"\n🧪 Testing: '{prompt}'")
        
        prompt_lower = prompt.lower()
        inventory = 50  # default
        
        # Parse inventory requirements (same logic as store_builder.py)
        inventory_patterns = [
            r'(\d+)\s*in\s*stock',
            r'stock\s*of\s*(\d+)',
            r'(\d+)\s*inventory',
            r'theres?\s*(\d+)',
            r'make\s*sure\s*theres?\s*(\d+)',
            r'(\d+)\s*pieces',
            r'(\d+)\s*units'
        ]
        
        for pattern in inventory_patterns:
            inventory_match = re.search(pattern, prompt_lower)
            if inventory_match:
                inventory = int(inventory_match.group(1))
                print(f"   ✅ Found inventory: {inventory} (pattern: {pattern})")
                break
        
        if inventory == 50:
            print(f"   ⚠️  Using default inventory: {inventory}")
        
        print(f"   📦 Final inventory: {inventory}")

if __name__ == "__main__":
    test_inventory_parsing()
