from store_builder import CompleteShopifyStoreCreator
import re

prompt = "create a store that sells workout clothes"
prompt_lower = prompt.lower()

# Enhanced product indicators including list patterns - ordered by priority
product_indicators = [
    # Specific store creation phrases (highest priority)
    'create a store with', 'store with', 'build a store with', 'make a store with',
    'add some', 'stock the store with', 'put in the store',
    
    # General selling phrases  
    'store that', 'store selling', 'shop that', 'shop selling',
    'business that', 'business selling', 'want to sell', 'i want to sell', 'store for', 'shop for',
    'sells', 'selling',
    
    # Simple additions
    'add to the store', 'include', 'stock', 'add',
    
    # Prepositions (lowest priority)
    'with a', 'with an'
]

# Find what the user wants to sell - prioritize longer matches
product_text = ""
best_match_len = 0
matched_indicator = ""

for indicator in product_indicators:
    if indicator in prompt_lower:
        # Get text after the indicator
        parts = prompt_lower.split(indicator, 1)
        if len(parts) > 1 and len(indicator) > best_match_len:
            product_text = parts[1].strip()
            best_match_len = len(indicator)
            matched_indicator = indicator

print(f"Original prompt: '{prompt}'")
print(f"Matched indicator: '{matched_indicator}'")
print(f"Product text after indicator: '{product_text}'")

# Now trace through the single product parsing
product_items = [product_text.strip()]

print(f"Product items: {product_items}")

# Clean up items - remove leading "and" or articles
item = product_items[0]
item = item.strip()
if item.lower().startswith('and '):
    item = item[4:].strip()  # Remove 'and '
# Remove articles
item = re.sub(r'^(a|an|the)\s+', '', item)

print(f"After cleanup: '{item}'")

# Stop at common ending words that aren't part of the product name
stop_words = ['make', 'with', 'that', 'stock', 'inventory', 'for', 'in']
for stop in stop_words:
    if ' ' + stop in item:
        item = item.split(' ' + stop)[0].strip()

print(f"After stop words: '{item}'")

# Extract product name (first 1-3 meaningful words)
words = [w for w in item.split() if len(w) > 1 and w.lower() not in ['the', 'and', 'for', 'with']]
print(f"Words extracted: {words}")

if words:
    # Determine product name
    if len(words) >= 2:
        # Check for common compound products
        two_word = ' '.join(words[:2]).lower()
        print(f"Two word combo: '{two_word}'")
        if any(combo in two_word for combo in ['vanilla candle', 'lavender candle', 'cherry candle', 
                                               'soy candle', 'scented candle', 'aromatherapy candle',
                                               'water bottle', 'coffee bean', 'yoga mat', 'speed cube']):
            product_name = ' '.join(words[:2])
            print(f"Compound product detected: '{product_name}'")
        else:
            product_name = words[0]
            print(f"Single word from compound: '{product_name}'")
    else:
        product_name = words[0]
        print(f"Single word product: '{product_name}'")
    
    # Build the final product name
    final_name = product_name.title()
    print(f"Final product name: '{final_name}'")
