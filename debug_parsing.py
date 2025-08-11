def debug_parsing():
    prompt = "add some workout clothes for men and women to the store"
    prompt_lower = prompt.lower()
    
    product_indicators = [
        'sells', 'selling', 'store that', 'store selling', 'shop that', 'shop selling',
        'business that', 'business selling', 'want to sell', 'i want to sell', 'store for', 'shop for',
        'create a store with', 'store with', 'build a store with', 'make a store with',
        'with a', 'with an', 'add', 'add some', 'add to the store', 'to the store',
        'stock', 'stock the store with', 'put in the store', 'include'
    ]
    
    product_text = ""
    best_match_len = 0
    for indicator in product_indicators:
        if indicator in prompt_lower:
            parts = prompt_lower.split(indicator, 1)
            if len(parts) > 1 and len(indicator) > best_match_len:
                product_text = parts[1].strip()
                best_match_len = len(indicator)
                print(f"Found indicator: '{indicator}' (len={len(indicator)})")
                print(f"Product text after split: '{product_text}'")
    
    print(f"Final product_text: '{product_text}'")
    
    if 'for men and women' in product_text:
        base_product = product_text.replace('for men and women', '').strip()
        print(f"Base product after removing 'for men and women': '{base_product}'")
        
        import re
        base_product = re.sub(r'\s*(to\s+the\s+store|in\s+the\s+store|with\s+.*|that\s+.*)$', '', base_product).strip()
        print(f"Base product after regex cleanup: '{base_product}'")

if __name__ == "__main__":
    debug_parsing()
