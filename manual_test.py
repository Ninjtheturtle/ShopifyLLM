#!/usr/bin/env python3

# Manual test of the product extraction logic
import re
import random

def test_extraction():
    prompt = 'create a store with a vanilla candle, lavender candle, and cherry candle'
    prompt_lower = prompt.lower()
    products = []
    
    print(f"Testing prompt: {prompt_lower}")
    
    # Enhanced product indicators including list patterns
    product_indicators = [
        'sells', 'selling', 'store that', 'store selling', 'shop that', 'shop selling',
        'business that', 'business selling', 'want to sell', 'i want to sell', 'store for', 'shop for',
        'create a store with', 'store with', 'build a store with', 'make a store with',
        'with a', 'with an'
    ]
    
    # Find what the user wants to sell
    product_text = ""
    for indicator in product_indicators:
        if indicator in prompt_lower:
            print(f"Found indicator: {indicator}")
            # Get text after the indicator
            parts = prompt_lower.split(indicator, 1)
            if len(parts) > 1:
                product_text = parts[1].strip()
                print(f"Product text: '{product_text}'")
                break
    
    if not product_text:
        print("No product text found!")
        return []
    
    # Parse lists - look for comma-separated items or "and" lists
    product_items = []
    
    # Handle comma-separated lists: "vanilla candle, lavender candle, and cherry candle"
    if ',' in product_text:
        print("Found commas, parsing list...")
        # Split by comma and clean up
        items = [item.strip() for item in product_text.split(',')]
        print(f"Items after comma split: {items}")
        
        # Handle "and" in the last item
        last_item = items[-1]
        if ' and ' in last_item:
            print(f"Processing 'and' in last item: '{last_item}'")
            and_parts = last_item.split(' and ')
            items[-1] = and_parts[0].strip()
            for part in and_parts[1:]:
                if part.strip():
                    items.append(part.strip())
        
        product_items = [item for item in items if item.strip()]
        print(f"Product items after comma processing: {product_items}")
    
    # Handle simple "and" lists: "vanilla and lavender candles"
    elif ' and ' in product_text:
        print("Found 'and' list...")
        and_parts = product_text.split(' and ')
        product_items = [part.strip() for part in and_parts if part.strip()]
    
    # Single product
    else:
        print("Single product...")
        product_items = [product_text.strip()]
    
    # Clean up items - remove leading "and" or articles
    cleaned_items = []
    for item in product_items:
        item = item.strip()
        print(f"Processing item: '{item}'")
        if item.lower().startswith('and '):
            item = item[4:].strip()  # Remove 'and '
            print(f"  Removed 'and': '{item}'")
        # Remove articles
        item = re.sub(r'^(a|an|the)\s+', '', item)
        print(f"  After article removal: '{item}'")
        if item:
            cleaned_items.append(item)
    
    product_items = cleaned_items
    print(f"Final cleaned items: {product_items}")
    
    # Process each product item
    for item in product_items:
        print(f"\\nProcessing product: '{item}'")
        if not item or len(item) < 3:
            print(f"  Skipping - too short: {len(item)}")
            continue
            
        # Clean up the item text
        item = item.strip()
        
        # Stop at common ending words that aren't part of the product name
        stop_words = ['make', 'with', 'that', 'stock', 'inventory', 'for', 'in']
        for stop in stop_words:
            if ' ' + stop in item:
                item = item.split(' ' + stop)[0].strip()
        
        print(f"  After stop word processing: '{item}'")
        
        # Extract product name (first 1-3 meaningful words)
        words = [w for w in item.split() if len(w) > 1 and w.lower() not in ['the', 'and', 'for', 'with']]
        print(f"  Words: {words}")
        if not words:
            print(f"  No valid words found!")
            continue
        
        # Determine product name
        if len(words) >= 2:
            # Check for common compound products
            two_word = ' '.join(words[:2]).lower()
            print(f"  Two word combo: '{two_word}'")
            if any(combo in two_word for combo in ['vanilla candle', 'lavender candle', 'cherry candle', 
                                                   'soy candle', 'scented candle', 'aromatherapy candle',
                                                   'water bottle', 'coffee bean', 'yoga mat', 'speed cube']):
                product_name = ' '.join(words[:2])
                print(f"  Using two-word name: '{product_name}'")
            else:
                product_name = words[0]
                print(f"  Using single word name: '{product_name}'")
        else:
            product_name = words[0]
            print(f"  Using only word: '{product_name}'")
        
        print(f"  Final product name: '{product_name}'")
        
        # Create the product
        products.append({
            'name': product_name.title(),
            'price': round(random.uniform(15.99, 49.99), 2),
            'sku': f"TEST{len(products)+1}"
        })
    
    print(f"\\nFinal products: {len(products)}")
    for i, p in enumerate(products, 1):
        print(f"  {i}. {p['name']} - ${p['price']}")
    
    return products

if __name__ == "__main__":
    test_extraction()
