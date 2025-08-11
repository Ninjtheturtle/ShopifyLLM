#!/usr/bin/env python3

import re

def test_workout_parsing():
    """Test parsing 'add some workout clothes for men and women to the store'"""
    
    prompt = "add some workout clothes for men and women to the store"
    prompt_lower = prompt.lower()
    
    # Test the new regex patterns
    patterns = [
        r'sells?\s+(?:a\s+)?([^,\n]+)',
        r'selling\s+(?:a\s+)?([^,\n]+)', 
        r'store\s+for\s+([^,\n]+)',
        r'shop\s+for\s+([^,\n]+)',
        r'add\s+(?:some\s+)?(.+?)(?:\s+to\s+the\s+store|$)',
        r'stock\s+(?:the\s+store\s+with\s+)?([^,\n]+)',
        r'put\s+([^,\n]+?)\s+in\s+the\s+store',
        r'include\s+([^,\n]+)'
    ]
    
    print(f"Testing prompt: '{prompt}'")
    print("-" * 50)
    
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, prompt_lower)
        if match:
            product_text = match.group(1).strip()
            print(f"✅ Pattern {i+1} matched: '{pattern}'")
            print(f"   Extracted: '{product_text}'")
            
            # Test gender parsing
            if 'for men and women' in product_text:
                base_product = product_text.replace('for men and women', '').strip()
                print(f"   Base product: '{base_product}'")
                print(f"   Would create: Men's {base_product.title()} + Women's {base_product.title()}")
            
            break
        else:
            print(f"❌ Pattern {i+1} no match: '{pattern}'")
    
    # Test the product indicators from _extract_products_from_prompt
    product_indicators = [
        'sells', 'selling', 'store that', 'store selling', 'shop that', 'shop selling',
        'business that', 'business selling', 'want to sell', 'i want to sell', 'store for', 'shop for',
        'create a store with', 'store with', 'build a store with', 'make a store with',
        'with a', 'with an', 'add', 'add some', 'add to the store', 'to the store',
        'stock', 'stock the store with', 'put in the store', 'include'
    ]
    
    print("\nTesting product indicators:")
    found_indicators = []
    for indicator in product_indicators:
        if indicator in prompt_lower:
            found_indicators.append(indicator)
    
    if found_indicators:
        print(f"✅ Found indicators: {found_indicators}")
        
        # Test the extraction logic
        for indicator in found_indicators:
            parts = prompt_lower.split(indicator, 1)
            if len(parts) > 1:
                product_text = parts[1].strip()
                print(f"   After '{indicator}': '{product_text}'")
    else:
        print("❌ No indicators found!")

if __name__ == "__main__":
    test_workout_parsing()
