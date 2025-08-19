# Complete Shopify Store Creator
# Uses our trained AI model + Shopify API to create full stores automatically

import requests
import json
import time
import os
from typing import Dict, List, Optional
import random
import re

import requests
import json
import time
import random
import re
from typing import Dict, List
import os
from dotenv import load_dotenv
from market_research import MarketResearcher
from image_generator import ProductImageGenerator

# Load environment variables
load_dotenv()

class CompleteShopifyStoreCreator:
    def __init__(self, shop_domain: str = None, access_token: str = None, real_mode: bool = False):
        """
        Initialize with Shopify credentials (optional for demo mode)
        
        Args:
            shop_domain: Your shop domain (e.g., 'yourstore.myshopify.com')
            access_token: Your Shopify Admin API access token
            real_mode: Set to True to create actual stores (default: demo mode)
        """
        # Try to load from environment variables if not provided
        self.shop_domain = shop_domain or os.getenv('SHOPIFY_SHOP_DOMAIN')
        self.access_token = access_token or os.getenv('SHOPIFY_ACCESS_TOKEN')
        
        # Check if we should use real mode from environment
        env_mode = os.getenv('STORE_CREATION_MODE', 'demo').lower()
        self.real_mode = real_mode or (env_mode == 'real')
        
        # Initialize market researcher for enhanced product data
        self.researcher = MarketResearcher()
        
        # Initialize image generator for product images
        self.image_generator = ProductImageGenerator()
        
        # Cache for AI assistant to avoid multiple model loads
        self._ai_assistant = None
        
        # Set up API configuration
        if self.shop_domain and self.access_token:
            self.api_base = f"https://{self.shop_domain}/admin/api/2023-10"
            self.headers = {
                'X-Shopify-Access-Token': self.access_token,
                'Content-Type': 'application/json'
            }
            print(f"🔧 Configured for: {self.shop_domain}")
            print(f"🎭 Mode: {'Real Store Creation' if self.real_mode else 'Demo Mode'}")
        else:
            print("🎭 Demo mode - will simulate store creation")
            print("💡 Run 'python shopify_config.py' to set up real Shopify connection")
            self.real_mode = False

    def create_store_from_prompt(self, prompt: str) -> Dict:
        """Create a complete Shopify store from a single prompt"""
        print(f"\n🚀 Creating store from: '{prompt}'")
        print("=" * 60)
        
        # Step 1: Generate store concept using AI
        print("🤖 Step 1: Generating store concept with AI...")
        concept = self._generate_ai_concept(prompt)
        
        # Step 2: Create store structure
        print("🏗️ Step 2: Building store structure...")
        if not self.real_mode:
            result = self._simulate_store_creation(concept)
        else:
            result = self._create_real_shopify_store(concept)
        
        print("\n🎉 Store creation complete!")
        print("=" * 60)
        
        return result
    
    def _generate_ai_concept(self, prompt: str) -> Dict:
        """Use our trained AI model to generate store concept"""
        print("⚠️ AI model is currently producing invalid output - using enhanced fallback")
        return self._create_fallback_concept(prompt)
    
    def _parse_ai_response(self, response: str, prompt: str) -> Dict:
        """Parse AI response into structured store data"""
        lines = response.split('\n')
        
        concept = {
            'store_name': 'Generated Store',
            'tagline': 'AI-Generated Excellence',
            'products': [],
            'brand_values': [],
            'blog_posts': [],
            'categories': [],
            'color_scheme': self._get_random_color_scheme()
        }
        
        # FIRST: Check if the prompt has specific product requests that the AI didn't parse
        prompt_products = self._extract_products_from_prompt(prompt)
        if prompt_products:
            concept['products'] = prompt_products
            print(f"   ✅ Extracted {len(prompt_products)} products directly from your request")
            for p in prompt_products:
                print(f"   - {p['name']}: ${p['price']}")
            return concept
        
        # SECOND: Try to parse from AI response
        current_product = {}
        product_names_seen = set()  # Track product names to avoid duplicates
        
        for line in lines:
            line = line.strip()
            
            # Extract store name - look for patterns like "Store Name:" or "**Store Name:**"
            if 'store name' in line.lower() and ':' in line:
                name_part = line.split(':')[-1].strip()
                name = name_part.replace('**', '').replace('*', '').strip()
                if name and len(name) > 2:
                    concept['store_name'] = name
            
            # Extract tagline - look for patterns like "Tagline:" or quoted text
            elif 'tagline' in line.lower() and ':' in line:
                tagline_part = line.split(':')[-1].strip()
                tagline = tagline_part.replace('**', '').replace('*', '').replace('"', '').strip()
                if tagline and len(tagline) > 2:
                    concept['tagline'] = tagline
            
            # Extract products (numbered list) - but filter out non-products
            elif re.match(r'^\d+\.', line):
                if current_product and current_product.get('name'):
                    concept['products'].append(current_product)
                
                # Parse: "1. Product Name ($XX.XX) - description"
                content = re.sub(r'^\d+\.\s*', '', line)
                
                # Skip if this looks like blog content, pages, or services
                skip_keywords = ['blog post', 'blog', 'page', 'landing page', 'template', 
                                'pricing', 'gallery', 'about', 'contact', 'guide', 
                                'tutorial', 'how to', 'testing', 'speed testing']
                
                if any(keyword in content.lower() for keyword in skip_keywords):
                    # This is blog content, not a product
                    blog_title = content.replace('Blog Post About', '').replace('Blog Post', '').strip()
                    blog_title = re.sub(r'\([^)]*\)', '', blog_title)  # Remove parentheses
                    blog_title = re.sub(r'\$[\d.]+', '', blog_title)   # Remove price
                    blog_title = blog_title.replace(' - ', ': ').strip()
                    
                    if blog_title and len(blog_title) > 5:
                        # Clean up the title
                        if blog_title.lower().startswith('about '):
                            blog_title = blog_title[6:].strip()
                        concept['blog_posts'].append(blog_title.title())
                    current_product = {}
                    continue
                
                # Split on dash to separate name/price from description
                if ' - ' in content:
                    name_price_part, description = content.split(' - ', 1)
                else:
                    name_price_part = content
                    description = 'High-quality product for your needs'
                
                # Extract price using regex
                price_match = re.search(r'\$(\d+\.?\d*)', name_price_part)
                price = float(price_match.group(1)) if price_match else random.randint(25, 95) + 0.99
                
                # Clean product name by removing price info
                product_name = re.sub(r'\([^)]*\)', '', name_price_part)  # Remove parentheses
                product_name = re.sub(r'\$[\d.]+', '', product_name)      # Remove price
                product_name = product_name.strip()
                
                # Check for duplicates (case-insensitive)
                product_key = product_name.lower()
                if product_key in product_names_seen:
                    print(f"   ⚠️ Skipping duplicate product: {product_name}")
                    current_product = {}
                    continue
                
                if product_name and len(product_name) > 2:
                    product_names_seen.add(product_key)
                    current_product = {
                        'name': product_name,
                        'price': price,
                        'description': description.strip(),
                        'inventory': random.randint(20, 100),
                        'sku': f"PROD{random.randint(1000, 9999)}"
                    }
                else:
                    current_product = {}
            
            # Extract brand values - lines starting with dash and containing key terms
            elif line.startswith('- ') and any(word in line.lower() for word in ['quality', 'innovation', 'sustainability', 'craftsmanship', 'authentic', 'premium']):
                value = line.replace('- ', '').replace('**', '').replace('*', '').strip()
                if value and len(value) > 5:
                    concept['brand_values'].append(value)
            
            # Extract blog post ideas - lines with quotes or explicit blog mentions
            elif ('blog' in line.lower() and ':' in line) or (line.startswith('- ') and '"' in line):
                blog_title = line.replace('- ', '').replace('"', '').replace('**', '').replace('*', '').strip()
                if ':' in blog_title:
                    blog_title = blog_title.split(':')[-1].strip()
                if blog_title and len(blog_title) > 5:
                    concept['blog_posts'].append(blog_title.title())
        
        # Add the last product if it exists
        if current_product and current_product.get('name'):
            concept['products'].append(current_product)
        
        # Remove any remaining duplicates by name
        unique_products = []
        seen_names = set()
        for product in concept['products']:
            if product['name'].lower() not in seen_names:
                unique_products.append(product)
                seen_names.add(product['name'].lower())
        concept['products'] = unique_products
        
        # Debug output
        print(f"   Parsed {len(concept['products'])} unique products from AI response")
        if concept['products']:
            for p in concept['products'][:3]:  # Show first 3
                print(f"   - {p['name']}: ${p['price']}")
        
        if concept['blog_posts']:
            print(f"   Parsed {len(concept['blog_posts'])} blog posts:")
            for blog in concept['blog_posts'][:3]:
                print(f"   - {blog}")
        
        # Ensure we have products - if parsing failed, use fallback
        if not concept['products']:
            print("   ⚠️ No products parsed, using fallback products")
            concept['products'] = self._generate_fallback_products_for_prompt(prompt)
        
        # Clean up data to fit Shopify limits
        concept['store_name'] = concept['store_name'][:50]  # Shopify limit
        concept['tagline'] = concept['tagline'][:100]
        
        return concept
    
    def _extract_products_from_prompt(self, prompt: str) -> List[Dict]:
        """Extract specific product requests directly from user prompt - IMPROVED LIST PARSING"""
        prompt_lower = prompt.lower()
        
        # Enhanced workout detection with typos and variations
        workout_keywords = [
            'workout', 'workouts', 'wokrout', 'wokrouts',  # typos
            'athletic', 'fitness', 'gym', 'exercise', 'sport', 'sports',
            'activewear', 'sportswear', 'athleisure',
            'running', 'training', 'yoga', 'crossfit'
        ]
        
        if any(word in prompt_lower for word in workout_keywords):
            print("🏋️ Detected workout/athletic clothing request - using specialized products")
            return self._generate_workout_clothing_products()
        
        products = []
        
        # Enhanced product indicators including list patterns - ordered by priority
        product_indicators = [
            # Specific store creation phrases (highest priority)
            'create a store with', 'store with', 'build a store with', 'make a store with',
            'add some', 'stock the store with', 'put in the store',
            
            # General selling phrases  
            'store that sells', 'store selling', 'shop that sells', 'shop selling',
            'business that sells', 'business selling', 'want to sell', 'i want to sell', 'store for', 'shop for',
            'store that', 'shop that', 'business that',  # These can be followed by 'sells'
            'sells', 'selling',
            
            # Simple additions
            'add to the store', 'include', 'stock', 'add',
            
            # Prepositions (lowest priority)
            'with a', 'with an'
        ]
        
        # Find what the user wants to sell - prioritize longer matches
        product_text = ""
        best_match_len = 0
        for indicator in product_indicators:
            if indicator in prompt_lower:
                # Get text after the indicator
                parts = prompt_lower.split(indicator, 1)
                if len(parts) > 1 and len(indicator) > best_match_len:
                    product_text = parts[1].strip()
                    best_match_len = len(indicator)
        
        # CRITICAL FIX: Remove action verbs that might remain in product_text
        action_verbs = ['sells', 'selling', 'sell']
        for verb in action_verbs:
            if product_text.startswith(verb + ' '):
                product_text = product_text[len(verb):].strip()
        
        if not product_text:
            return []
        
        # FIRST: Check for specific patterns like "workout clothes for men and women"
        if 'for men and women' in product_text or 'for both men and women' in product_text:
            base_product = product_text.replace('for men and women', '').replace('for both men and women', '').strip()
            # Clean up any trailing words like "to the store"
            base_product = re.sub(r'\s*(to\s+the\s+store|in\s+the\s+store|with\s+.*|that\s+.*)$', '', base_product).strip()
            if base_product:
                return [
                    {
                        'name': f"Men's {base_product.title()}",
                        'price': 29.99,
                        'description': f"Premium {base_product} designed specifically for men with superior quality and style.",
                        'inventory': 50,
                        'sku': f"MENS_{base_product.replace(' ', '_').upper()}001"
                    },
                    {
                        'name': f"Women's {base_product.title()}",
                        'price': 29.99,
                        'description': f"Premium {base_product} designed specifically for women with superior quality and style.",
                        'inventory': 50,
                        'sku': f"WOMENS_{base_product.replace(' ', '_').upper()}001"
                    }
                ]
        
        # SECOND: Try the original complex parsing logic for other cases
        try:
            # Parse lists - look for comma-separated items or "and" lists
            product_items = []
            
            # Handle comma-separated lists: "vanilla candle, lavender candle, and cherry candle"
            if ',' in product_text:
                # Split by comma and clean up
                items = [item.strip() for item in product_text.split(',')]
                
                # Handle "and" in the last item
                last_item = items[-1]
                if ' and ' in last_item:
                    and_parts = last_item.split(' and ')
                    items[-1] = and_parts[0].strip()
                    for part in and_parts[1:]:
                        if part.strip():
                            items.append(part.strip())
                
                product_items = [item for item in items if item.strip()]
            
            # Handle simple "and" lists: "vanilla and lavender candles"
            elif ' and ' in product_text:
                and_parts = product_text.split(' and ')
                product_items = [part.strip() for part in and_parts if part.strip()]
            
            # Single product
            else:
                product_items = [product_text.strip()]
            
            # Clean up items - remove leading "and" or articles
            cleaned_items = []
            for item in product_items:
                item = item.strip()
                if item.lower().startswith('and '):
                    item = item[4:].strip()  # Remove 'and '
                # Remove articles
                item = re.sub(r'^(a|an|the)\s+', '', item)
                if item:
                    cleaned_items.append(item)
            
            product_items = cleaned_items
            
            # Process each product item
            for item in product_items:
                if not item or len(item) < 3:
                    continue
                    
                # Clean up the item text
                item = item.strip()
                
                # Stop at common ending words that aren't part of the product name
                stop_words = ['make', 'with', 'that', 'stock', 'inventory', 'for', 'in']
                for stop in stop_words:
                    if ' ' + stop in item:
                        item = item.split(' ' + stop)[0].strip()
                
                # Extract product name (first 1-3 meaningful words)
                words = [w for w in item.split() if len(w) > 1 and w.lower() not in ['the', 'and', 'for', 'with']]
                if not words:
                    continue
                
                # Determine product name - improved for compound products
                if len(words) >= 2:
                    # Check for common compound products (expanded list)
                    two_word = ' '.join(words[:2]).lower()
                    compound_products = [
                        'vanilla candle', 'lavender candle', 'cherry candle', 'soy candle', 'scented candle', 'aromatherapy candle',
                        'water bottle', 'coffee bean', 'yoga mat', 'speed cube',
                        'workout clothes', 'workout gear', 'fitness equipment', 'sports wear', 'athletic wear',
                        'running shoes', 'hiking boots', 'winter jacket', 'summer dress',
                        'phone case', 'laptop bag', 'gaming chair', 'office desk'
                    ]
                    
                    if any(combo in two_word for combo in compound_products):
                        product_name = ' '.join(words[:2])
                    else:
                        # For non-compound products, still use the full name if it makes sense
                        if len(words) == 2 and all(len(w) > 2 for w in words):
                            product_name = ' '.join(words[:2])  # Use both words
                        else:
                            product_name = words[0]
                else:
                    product_name = words[0]
                
                # Extract specifications from the original item
                inventory = 50  # default
                color = None
                size = None
                material = None
                
                # Look for inventory specifications in the full prompt
                inventory_patterns = [
                    r'(\d+)\s*in\s*stock',
                    r'stock\s*of\s*(\d+)',
                    r'(\d+)\s*inventory',
                    r'theres?\s*(\d+)',
                    r'make\s*sure\s*theres?\s*(\d+)',
                    r'(\d+)\s*pieces',
                    r'(\d+)\s*units',
                    r'stock\s*(\d+)',
                    r'stock\s*(\d+)\s*for\s*each'
                ]
                for pattern in inventory_patterns:
                    inventory_match = re.search(pattern, prompt_lower)
                    if inventory_match:
                        inventory = int(inventory_match.group(1))
                        break
                
                # Extract color from the item name itself
                color_words = ['vanilla', 'lavender', 'cherry', 'red', 'blue', 'green', 'black', 'white', 
                              'silver', 'gold', 'yellow', 'purple', 'orange', 'pink', 'grey', 'gray', 'brown']
                for c in color_words:
                    if c in item.lower():
                        color = c
                        break
                
                # Build the final product name
                final_name = product_name.title()
                
                # Generate product-specific description
                description = self._generate_product_specific_description(product_name, material, color, size)
                
                # Generate SKU
                sku_base = ''.join([c.upper() for c in product_name.replace(' ', '') if c.isalpha()])[:6]
                if color:
                    sku_base += color.upper()[:3]
                sku = sku_base[:12] or f"PROD{random.randint(1000, 9999)}"
                
                # Base price (will be enhanced by market research)
                # For candles, use lower pricing if requested
                if 'lower end' in prompt_lower or 'low price' in prompt_lower:
                    base_price = random.uniform(6.99, 12.99)
                else:
                    base_price = random.uniform(15.99, 49.99)
                
                product = {
                    'name': final_name,
                    'price': self._normalize_price(base_price),
                    'description': description,
                    'inventory': inventory,
                    'sku': sku
                }
                
                products.append(product)
            
            return products
            
        except Exception as e:
            return []
    
    def _parse_product_list(self, product_text: str) -> List[str]:
        """Parse multiple products from text like 'lavender, cherry, and vanilla candle'"""
        # Handle lists with "and" and commas
        product_text = product_text.strip()
        
        # Split on "and" first
        if ' and ' in product_text:
            # Handle "lavender, cherry, and vanilla candle"
            parts = product_text.split(' and ')
            if len(parts) == 2:
                first_part = parts[0]
                last_item = parts[1]
                
                # Check if first part has commas
                if ',' in first_part:
                    items = [item.strip() for item in first_part.split(',')]
                    items.append(last_item.strip())
                    
                    # Detect the base product type from the last item
                    base_product = self._extract_base_product_type(last_item)
                    if base_product:
                        # Apply base product to all items that don't have it
                        final_items = []
                        for item in items:
                            if base_product not in item.lower():
                                final_items.append(f"{item.strip()} {base_product}")
                            else:
                                final_items.append(item.strip())
                        return final_items
                else:
                    return [first_part.strip(), last_item.strip()]
        
        # Split on commas
        if ',' in product_text:
            return [item.strip() for item in product_text.split(',')]
        
        # Single product
        return [product_text.strip()]
    
    def _extract_base_product_type(self, text: str) -> str:
        """Extract the product type from text like 'vanilla candle' -> 'candle'"""
        words = text.strip().split()
        if len(words) >= 2:
            # Return the last word as the product type
            return words[-1]
        return ""
    
    def _clean_product_name(self, product_name: str) -> str:
        """Clean up product name and make it proper"""
        # Remove specification words but keep the core product
        spec_removals = [
            'make sure', 'ensure', 'with stock', 'with inventory', 'stock of', 
            'inventory of', 'pieces each', 'units each', 'make the stock',
            'do market research', 'market research', 'price it on', 'lower end',
            'higher end', 'competitive price'
        ]
        
        clean_name = product_name
        for removal in spec_removals:
            if removal in clean_name.lower():
                clean_name = clean_name.lower().split(removal)[0].strip()
        
        # Clean up the product name - remove common store creation phrases
        cleanup_phrases = [
            'a store that sells', 'store that sells', 'create a store selling', 
            'store selling', 'i want a store selling', 'build a store for',
            'create a store for', 'make a store that sells'
        ]
        
        for phrase in cleanup_phrases:
            clean_name = clean_name.replace(phrase, '').strip()
        
        # Split by "and" to get individual products, return the first one
        if ' and ' in clean_name:
            clean_name = clean_name.split(' and ')[0].strip()
        
        # Split by commas to get individual products, return the first one  
        if ',' in clean_name:
            clean_name = clean_name.split(',')[0].strip()
        
        # Capitalize properly
        clean_name = clean_name.title().strip()
        
        return clean_name if clean_name else "Custom Product"
    
    def _extract_product_specs(self, full_prompt: str, product_name: str) -> Dict:
        """Extract specifications like stock, price, etc. from the full prompt"""
        prompt_lower = full_prompt.lower()
        specs = {}
        
        # Extract stock/inventory numbers
        import re
        stock_patterns = [
            r'stock (\d+)',
            r'inventory (\d+)', 
            r'(\d+) in stock',
            r'(\d+) inventory',
            r'(\d+) for each',
            r'(\d+) each'
        ]
        
        for pattern in stock_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                specs['inventory'] = int(match.group(1))
                break
        
        # Extract price preferences
        if 'lower end' in prompt_lower or 'low price' in prompt_lower or 'cheap' in prompt_lower:
            specs['price_range'] = 'low'
        elif 'higher end' in prompt_lower or 'premium' in prompt_lower or 'expensive' in prompt_lower:
            specs['price_range'] = 'high'
        else:
            specs['price_range'] = 'medium'
        
        # Extract size/capacity
        size_patterns = [
            r'(\d+)\s*oz',
            r'(\d+)\s*ml', 
            r'(\d+)\s*liter',
            r'(\d+)\s*inch'
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                specs['size'] = match.group(0)
                break
        
        return specs

    def _generate_base_price(self, product_name: str, price_range: str = 'medium') -> float:
        """Generate appropriate base price for product based on type and range"""
        product_lower = product_name.lower()
        
        # Base prices by category (adjusted for candles since user wants lower end)
        base_prices = {
            'candle': {'low': 6.99, 'medium': 12.99, 'high': 22.99},
            'candles': {'low': 6.99, 'medium': 12.99, 'high': 22.99},
            'bottle': {'low': 12.99, 'medium': 19.99, 'high': 35.99},
            'headphones': {'low': 29.99, 'medium': 79.99, 'high': 199.99},
            'coffee': {'low': 9.99, 'medium': 16.99, 'high': 28.99},
            'shirt': {'low': 14.99, 'medium': 24.99, 'high': 39.99},
            'lavender': {'low': 6.99, 'medium': 12.99, 'high': 22.99},  # Likely a candle
            'vanilla': {'low': 6.99, 'medium': 12.99, 'high': 22.99},   # Likely a candle
            'cherry': {'low': 6.99, 'medium': 12.99, 'high': 22.99}     # Likely a candle
        }
        
        # Find matching category
        for category, prices in base_prices.items():
            if category in product_lower:
                return prices.get(price_range, prices['medium'])
        
        # Default pricing
        defaults = {'low': 9.99, 'medium': 19.99, 'high': 34.99}
        return defaults.get(price_range, defaults['medium'])

    def _generate_fallback_products_for_prompt(self, prompt: str) -> List[Dict]:
        """Generate ONLY what the user specifically asked for - NO hardcoded fallbacks"""
        prompt_lower = prompt.lower()
        
        # Try one more time to extract products using different patterns
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
        
        import re
        for pattern in patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                product_text = match.group(1).strip()
                # Clean up the match
                product_text = re.sub(r'\s*(make\s+sure|with\s+\d+|stock|inventory).*', '', product_text)
                
                if product_text:
                    # Handle lists in the product text (e.g., "workout clothes for men and women")
                    products = []
                    
                    # Parse gender-specific products
                    if 'for men and women' in product_text or 'for both men and women' in product_text:
                        base_product = product_text.replace('for men and women', '').replace('for both men and women', '').strip()
                        products.extend([
                            {
                                'name': f"Men's {base_product.title()}",
                                'price': 29.99,
                                'description': f"Premium {base_product} designed specifically for men with superior quality and style.",
                                'inventory': 50,
                                'sku': f"MENS_{base_product.replace(' ', '_').upper()}001"
                            },
                            {
                                'name': f"Women's {base_product.title()}",
                                'price': 29.99,
                                'description': f"Premium {base_product} designed specifically for women with superior quality and style.",
                                'inventory': 50,
                                'sku': f"WOMENS_{base_product.replace(' ', '_').upper()}001"
                            }
                        ])
                    else:
                        products.append({
                            'name': product_text.title(),
                            'price': 19.99,
                            'description': f"Premium {product_text} with high-quality materials and excellent craftsmanship.",
                            'inventory': 50,
                            'sku': f"PROD_{product_text.replace(' ', '_').upper()}001"
                        })
                    
                    return products
        
        # If we absolutely cannot parse anything, return empty list
        # DO NOT create random products like water bottles, t-shirts, etc.
        print(f"⚠️ Could not parse any products from prompt: '{prompt}'")
        return []

    def _extract_main_product_from_prompt(self, prompt_lower: str) -> str:
        """Extract the main product name from the prompt"""
        # Common phrases that indicate what they want to sell
        selling_phrases = [
            'sells', 'selling', 'store that sells', 'shop that sells', 
            'store selling', 'shop selling', 'want to sell', 'business that sells'
        ]
        
        product_text = ""
        for phrase in selling_phrases:
            if phrase in prompt_lower:
                parts = prompt_lower.split(phrase, 1)
                if len(parts) > 1:
                    product_text = parts[1].strip()
                    break
        
        if not product_text:
            return ""
        
        # Clean up the product text to get the main product
        # Remove common stopwords and specifications
        stopwords = ['and', 'the', 'a', 'an', 'that', 'with', 'make', 'sure', 'theres', 'there', 'are', 'is', 'in', 'stock', 'inventory', 'premium', 'high-quality']
        
        # Split by common delimiters and take the first meaningful part
        for delimiter in [' make sure', ' with', ' that has', ' that have', ' featuring', ' capacity', ' oz', ' ml']:
            if delimiter in product_text:
                product_text = product_text.split(delimiter)[0]
                break
        
        # Get first few words as the product name, but prioritize common product combinations
        words = [w for w in product_text.split() if w not in stopwords and len(w) > 1]
        
        if words:
            # Check for common two-word products first
            two_word_products = ['water bottle', 'speed cube', 'yoga mat', 'coffee bean', 'toilet paper', 'phone case']
            if len(words) >= 2:
                potential_two_word = ' '.join(words[:2]).lower()
                if any(product in potential_two_word for product in two_word_products):
                    return ' '.join(words[:2])
            
            # Otherwise take just the first meaningful word
            return words[0]
        
        return ""
    
    def _get_ai_assistant(self):
        """Get cached AI assistant instance"""
        if self._ai_assistant is None:
            from chat_assistant import ShopifyAssistant
            self._ai_assistant = ShopifyAssistant()
        return self._ai_assistant

    def _generate_product_specific_description(self, product_name: str, material: str = None, color: str = None, size: str = None) -> str:
        """Generate product-specific descriptions using our fine-tuned AI model with targeted prompts"""
        try:
            # Create product-specific, detailed prompt like Nike does
            product_lower = product_name.lower()
            
            # Build specific prompt based on product type
            if any(word in product_lower for word in ['workout clothes', 'athletic wear', 'sportswear', 'fitness', 'activewear']):
                prompt = f"Write a product description for {product_name} that mentions fabric technology, fit, and performance benefits like moisture-wicking or breathability. Use concrete details like Nike does for athletic wear."
            elif any(word in product_lower for word in ['shoes', 'sneakers', 'boots', 'footwear']):
                prompt = f"Write a product description for {product_name} focusing on comfort, support, sole technology, and materials. Mention specific features like cushioning or traction."
            elif any(word in product_lower for word in ['shirt', 'top', 'tee', 'tank']):
                prompt = f"Write a product description for {product_name} focusing on fabric, fit, comfort, and style. Mention specific features like breathability or stretch."
            elif any(word in product_lower for word in ['pants', 'shorts', 'leggings', 'joggers']):
                prompt = f"Write a product description for {product_name} focusing on fit, fabric technology, and movement. Mention features like stretch, waistband comfort, or pockets."
            elif any(word in product_lower for word in ['jacket', 'hoodie', 'sweatshirt', 'outerwear']):
                prompt = f"Write a product description for {product_name} focusing on warmth, protection, and comfort. Mention features like weather resistance or insulation."
            else:
                # General product prompt - still specific
                prompt = f"Write a detailed product description for {product_name}. Focus on what makes this product useful and unique. Avoid generic words like premium or professional grade."
            
            # Add material/color context if provided
            if material:
                prompt += f" The product is made from {material}."
            if color:
                prompt += f" It comes in {color}."
                
            # Use the cached fine-tuned model to generate the description
            assistant = self._get_ai_assistant()
            ai_description = assistant.respond(prompt)
            
            # Clean up the AI response and remove filler words
            if ai_description:
                # Remove any system prompts or extra text
                lines = ai_description.split('\n')
                description_lines = [line.strip() for line in lines 
                                   if line.strip() 
                                   and not line.startswith('Store Name:') 
                                   and not line.startswith('Tagline:')
                                   and not line.startswith('Product Name:')
                                   and len(line.strip()) > 20]  # Ensure substantial content
                
                if description_lines:
                    # Look for the best description line - prefer longer, more detailed lines
                    best_description = max(description_lines, key=len)
                    
                    # Remove generic filler words and phrases
                    filler_removals = [
                        'premium', 'professional grade', 'professional-grade', 'luxury',
                        'high-quality', 'top-quality', 'exceptional quality', 'superior quality',
                        'cutting-edge', 'state-of-the-art', 'world-class', 'industry-leading',
                        'revolutionary', 'innovative design', 'sophisticated', 'artistry',
                        'meticulously crafted', 'expertly designed'
                    ]
                    
                    for filler in filler_removals:
                        best_description = best_description.replace(filler, '').strip()
                    
                    # Clean up extra spaces
                    best_description = ' '.join(best_description.split())
                    
                    return best_description[:500] if best_description else self._fallback_description(product_name, material, color, size)
            
            # Fallback to template if AI fails
            return self._fallback_description(product_name, material, color, size)
            
        except Exception as e:
            print(f"⚠️ AI description generation failed: {e}")
            return self._fallback_description(product_name, material, color, size)
    
    def _fallback_description(self, product_name: str, material: str = None, color: str = None, size: str = None) -> str:
        """Fallback method with product-specific, realistic descriptions"""
        product_lower = product_name.lower()
        
        # Workout clothes and athletic wear
        if any(word in product_lower for word in ['workout clothes', 'athletic wear', 'sportswear', 'activewear', 'fitness']):
            features = ['moisture-wicking fabric', 'four-way stretch', 'flatlock seams', 'quick-dry technology', 'breathable mesh panels']
            selected_features = random.sample(features, 2)
            
            descriptions = [
                f"Designed with {selected_features[0]} and {selected_features[1]} for unrestricted movement during training",
                f"Features {selected_features[0]} to keep you dry and {selected_features[1]} for maximum comfort",
                f"Built with {selected_features[0]} and {selected_features[1]} to enhance your workout performance"
            ]
            base_desc = random.choice(descriptions)
            
            if color:
                base_desc += f". Available in {color} for versatile styling with your existing athletic gear"
            if material:
                base_desc += f". Constructed from {material} for long-lasting durability"
                
        # Athletic shoes and footwear  
        elif any(word in product_lower for word in ['shoes', 'sneakers', 'runners', 'trainers', 'footwear']):
            features = ['responsive cushioning', 'rubber outsole', 'breathable upper', 'arch support', 'heel counter']
            selected_features = random.sample(features, 2)
            
            descriptions = [
                f"Engineered with {selected_features[0]} and {selected_features[1]} for all-day comfort",
                f"Features {selected_features[0]} to reduce impact and {selected_features[1]} for stability",
                f"Built with {selected_features[0]} and {selected_features[1]} for enhanced performance"
            ]
            base_desc = random.choice(descriptions)
            
            if color:
                base_desc += f". The {color} colorway pairs easily with your workout gear"
            if material:
                base_desc += f". Made with {material} for breathability and durability"
                
        # Water bottles and drinkware
        elif any(word in product_lower for word in ['water', 'bottle', 'flask', 'tumbler', 'mug']):
            descriptions = [
                f"Double-wall insulation keeps drinks cold for 24 hours or hot for 12 hours",
                f"Leak-proof design with wide mouth opening for easy filling and cleaning", 
                f"BPA-free construction with comfortable grip and fits most cup holders"
            ]
            base_desc = random.choice(descriptions)
            
            if size:
                base_desc += f". {size} capacity provides the right amount for daily hydration"
            if color:
                base_desc += f" in a sleek {color} finish"
                
        # Shirts and tops
        elif any(word in product_lower for word in ['shirt', 'top', 'tee', 'tank']):
            features = ['soft cotton blend', 'relaxed fit', 'crew neck', 'tagless design', 'pre-shrunk fabric']
            selected_features = random.sample(features, 2)
            
            descriptions = [
                f"Made with {selected_features[0]} and features {selected_features[1]} for everyday comfort",
                f"Constructed from {selected_features[0]} with {selected_features[1]} for a classic look",
                f"Features {selected_features[0]} and {selected_features[1]} for versatile styling"
            ]
            base_desc = random.choice(descriptions)
            
        # Pants and bottoms
        elif any(word in product_lower for word in ['pants', 'shorts', 'leggings', 'joggers']):
            features = ['elastic waistband', 'side pockets', 'stretch fabric', 'drawstring closure', 'reinforced seams']
            selected_features = random.sample(features, 2)
            
            descriptions = [
                f"Designed with {selected_features[0]} and {selected_features[1]} for comfort and convenience",
                f"Features {selected_features[0]} for easy wear and {selected_features[1]} for functionality",
                f"Built with {selected_features[0]} and {selected_features[1]} for active lifestyles"
            ]
            base_desc = random.choice(descriptions)
            
        # Electronics and tech
        elif any(word in product_lower for word in ['headphones', 'earbuds', 'speaker', 'charger', 'phone', 'laptop']):
            features = ['wireless connectivity', 'long battery life', 'noise cancellation', 'fast charging', 'compact design']
            selected_features = random.sample(features, 2)
            
            descriptions = [
                f"Features {selected_features[0]} and {selected_features[1]} for seamless use",
                f"Built with {selected_features[0]} and {selected_features[1]} for convenience",
                f"Designed with {selected_features[0]} and {selected_features[1]} for reliability"
            ]
            base_desc = random.choice(descriptions)
            
        # Default for unknown products
        else:
            descriptions = [
                f"Designed for everyday use with attention to quality and functionality",
                f"Built to last with thoughtful construction and reliable performance",
                f"Crafted with care to meet your daily needs"
            ]
            base_desc = random.choice(descriptions)
            
            if material:
                base_desc += f". Made from {material} for durability"
            if color:
                base_desc += f" in {color}"
                
        return base_desc

    def _generate_product_variations(self, base_product: str, prompt_lower: str) -> List[Dict]:
        """Generate variations of a product based on the prompt"""
        products = []
        base_product = base_product.strip()
        
        if not base_product:
            return self._generate_default_products()
        
        # Enhanced workout detection with typos and variations
        workout_keywords = [
            'workout', 'workouts', 'wokrout', 'wokrouts',  # typos
            'athletic', 'fitness', 'gym', 'exercise', 'sport', 'sports',
            'activewear', 'sportswear', 'athleisure',
            'running', 'training', 'yoga', 'crossfit'
        ]
        
        if any(word in prompt_lower for word in workout_keywords):
            return self._generate_workout_clothing_products()
        
        # Parse specifications from the prompt
        specs = self._parse_product_specifications(prompt_lower)
        
        # Generate base product
        main_product = self._create_product_variant(base_product, specs)
        products.append(main_product)
        
        # Generate logical variations (2-3 additional products)
        variations = self._generate_logical_variations(base_product, specs)
        products.extend(variations)
        
        return products[:4]  # Limit to 4 products max
    
    def _generate_workout_clothing_products(self) -> List[Dict]:
        """Generate specific workout clothing products with realistic prices"""
        workout_products = [
            {
                'name': 'Premium Workout T-Shirt',
                'price': 26.49,  # Updated to match market research
                'description': 'Moisture-wicking athletic shirt designed for high-intensity workouts. Features four-way stretch fabric and breathable mesh panels for maximum comfort.',
                'features': [
                    'Moisture-wicking fabric',
                    'Four-way stretch',
                    'Breathable mesh panels',
                    'Quick-dry technology',
                    'Flatlock seams',
                    'UPF 30+ sun protection'
                ],
                'inventory': 100
            },
            {
                'name': 'Athletic Leggings',
                'price': 22.00,  # Updated to match market research
                'description': 'High-performance leggings with compression fit and side pockets. Perfect for yoga, running, or weightlifting.',
                'features': [
                    'Compression fit',
                    'Side pockets',
                    'High waistband',
                    'Squat-proof fabric',
                    'Moisture-wicking',
                    'Four-way stretch'
                ],
                'inventory': 85
            },
            {
                'name': 'Training Shorts',
                'price': 24.49,  # Updated to match market research
                'description': 'Lightweight training shorts with built-in compression liner. Ideal for running and cross-training.',
                'features': [
                    'Built-in compression liner',
                    'Lightweight fabric',
                    'Quick-dry material',
                    'Elastic waistband',
                    'Reflective details',
                    'Multiple pockets'
                ],
                'inventory': 120
            },
            {
                'name': 'Performance Tank Top',
                'price': 27.49,  # Updated to match market research
                'description': 'Sleeveless performance top with racerback design. Features antimicrobial treatment and ultra-soft fabric.',
                'features': [
                    'Racerback design',
                    'Antimicrobial treatment',
                    'Ultra-soft fabric',
                    'Moisture-wicking',
                    'Tag-free label',
                    'Loose fit'
                ],
                'inventory': 95
            }
        ]
        
        print("🏋️ Generated workout clothing products with Nike-style descriptions")
        return workout_products
    
    def _normalize_price(self, price: float) -> float:
        """Normalize price to end with .99, .49, or .00"""
        # Convert to integer part and decimal part
        whole_part = int(price)
        decimal_part = price - whole_part
        
        # Choose ending based on the decimal part
        if decimal_part < 0.25:
            return float(f"{whole_part}.00")
        elif decimal_part < 0.75:
            return float(f"{whole_part}.49")
        else:
            return float(f"{whole_part}.99")
    
    def _parse_product_specifications(self, prompt_lower: str) -> Dict:
        """Parse specifications from the prompt"""
        specs = {
            'colors': [],
            'sizes': [],
            'materials': [],
            'features': [],
            'inventory': 50
        }
        
        # Parse colors
        color_words = ['red', 'blue', 'green', 'black', 'white', 'silver', 'gold', 'yellow', 'purple', 'orange', 'pink', 'grey', 'gray', 'brown']
        specs['colors'] = [color for color in color_words if color in prompt_lower]
        
        # Parse sizes
        size_patterns = [
            r'(\d+)\s*oz', r'(\d+)\s*ml', r'(\d+)\s*inch', r'(\d+)\s*cm',
            r'small', r'medium', r'large', r'extra large', r'xl'
        ]
        for pattern in size_patterns:
            matches = re.findall(pattern, prompt_lower)
            if matches:
                specs['sizes'].extend(matches)
        
        # Parse materials
        materials = ['steel', 'stainless steel', 'plastic', 'wood', 'metal', 'glass', 'ceramic', 'cotton', 'polyester', 'leather', 'rubber', 'silicon', 'bamboo', 'organic']
        specs['materials'] = [mat for mat in materials if mat in prompt_lower]
        
        # Parse inventory
        inventory_patterns = [
            r'(\d+)\s*in\s*stock', r'stock\s*of\s*(\d+)', r'(\d+)\s*inventory',
            r'theres?\s*(\d+)', r'(\d+)\s*pieces', r'(\d+)\s*units'
        ]
        for pattern in inventory_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                specs['inventory'] = int(match.group(1))
                break
        
        return specs
    
    def _create_product_variant(self, base_product: str, specs: Dict, variant_type: str = 'standard') -> Dict:
        """Create a single product variant"""
        # Build product name
        name_parts = []
        
        if variant_type == 'premium':
            name_parts.append('Premium')
        elif variant_type == 'eco':
            name_parts.append('Eco-Friendly')
        elif variant_type == 'deluxe':
            name_parts.append('Deluxe')
        
        if specs['sizes'] and variant_type == 'standard':
            name_parts.append(specs['sizes'][0])
        elif variant_type == 'large' and 'large' not in specs['sizes']:
            name_parts.append('Large')
        elif variant_type == 'small' and 'small' not in specs['sizes']:
            name_parts.append('Compact')
        
        if specs['colors'] and variant_type == 'standard':
            name_parts.append(specs['colors'][0].title())
        elif variant_type != 'standard' and specs['colors']:
            # Use different color for variants
            available_colors = [c for c in specs['colors'] if c != specs['colors'][0]]
            if available_colors:
                name_parts.append(available_colors[0].title())
        
        if specs['materials'] and variant_type == 'standard':
            name_parts.append(specs['materials'][0].title())
        
        name_parts.append(base_product.title())
        
        product_name = ' '.join(name_parts)
        
        # Generate product-specific description with variant modifier
        material = specs['materials'][0] if specs['materials'] else None
        color = specs['colors'][0] if specs['colors'] and variant_type == 'standard' else None
        if variant_type != 'standard' and specs['colors']:
            available_colors = [c for c in specs['colors'] if c != specs['colors'][0]]
            if available_colors:
                color = available_colors[0]
        
        # Get base description from product-specific generator
        base_description = self._generate_product_specific_description(base_product, material, color)
        
        # Add variant-specific modifiers
        if variant_type == 'premium':
            description = base_description.replace("Premium", "Ultra-Premium").replace("High-quality", "Luxury")
            description += " Enhanced with premium features and superior materials for the ultimate experience."
        elif variant_type == 'eco':
            description = base_description.replace("Premium", "Eco-Friendly").replace("High-quality", "Sustainable")
            description += " Made with environmentally responsible materials and processes."
        elif variant_type == 'deluxe':
            description = base_description.replace("Premium", "Deluxe").replace("High-quality", "Professional-grade")
            description += " Features enhanced design and advanced functionality for demanding users."
        elif variant_type == 'large':
            description = base_description
            description += " Available in generous sizing for extended use and maximum convenience."
        else:
            description = base_description
        
        # Generate price based on variant type
        base_price = random.uniform(15.99, 39.99)
        if variant_type == 'premium':
            base_price *= 1.5
        elif variant_type == 'deluxe':
            base_price *= 1.3
        elif variant_type == 'eco':
            base_price *= 1.2
        
        # Generate SKU
        sku_parts = [''.join([c.upper() for c in base_product if c.isalpha()])[:4]]
        if variant_type != 'standard':
            sku_parts.append(variant_type.upper()[:3])
        sku = ''.join(sku_parts) + f"{random.randint(10, 99)}"
        
        return {
            'name': product_name,
            'price': self._normalize_price(base_price),
            'description': description,
            'inventory': specs['inventory'] if variant_type == 'standard' else random.randint(30, 60),
            'sku': sku[:12]
        }
    
    def _generate_logical_variations(self, base_product: str, specs: Dict) -> List[Dict]:
        """Generate logical variations of the base product"""
        variations = []
        
        # Generate a premium variant
        premium = self._create_product_variant(base_product, specs, 'premium')
        variations.append(premium)
        
        # Generate an eco-friendly variant
        eco = self._create_product_variant(base_product, specs, 'eco')
        variations.append(eco)
        
        # Generate a size variant if sizes were mentioned
        if specs['sizes']:
            size_variant = self._create_product_variant(base_product, specs, 'large')
            variations.append(size_variant)
        else:
            # Generate a deluxe variant instead
            deluxe = self._create_product_variant(base_product, specs, 'deluxe')
            variations.append(deluxe)
        
        return variations[:3]  # Return max 3 variations
    
    def _generate_fallback_products_for_prompt(self, prompt: str) -> List[Dict]:
        """Generate appropriate fallback products based on the prompt"""
        words = prompt.lower().split()
        prompt_lower = prompt.lower()
        
        # Check for water bottle requests with specific sizes
        if 'water' in prompt_lower and 'bottle' in prompt_lower:
            products = []
            
            # Look for specific sizes mentioned (10oz, 20oz, 30oz, etc.)
            import re
            size_matches = re.findall(r'(\d+)\s*oz', prompt_lower)
            
            if size_matches:
                # Create products for each size mentioned
                for size in size_matches:
                    size_int = int(size)
                    # Price based on size (bigger = more expensive)
                    base_price = 15.99 + (size_int * 0.75)
                    
                    products.append({
                        'name': f'{size}oz Stainless Steel Water Bottle',
                        'price': round(base_price, 2),
                        'description': f'Premium {size}oz insulated stainless steel water bottle that keeps drinks cold for 24 hours and hot for 12 hours. Double-wall vacuum insulation with leak-proof cap.',
                        'inventory': 40 + (10 - len(size_matches)) * 5,  # More inventory for fewer sizes
                        'sku': f'BOTTLE{size}OZ'
                    })
                
                return products
            else:
                # Default water bottle selection if no specific sizes
                return [
                    {'name': '10oz Stainless Steel Water Bottle', 'price': 22.99, 'description': 'Compact 10oz insulated bottle perfect for kids or short trips', 'inventory': 45, 'sku': 'BOTTLE10OZ'},
                    {'name': '20oz Stainless Steel Water Bottle', 'price': 29.99, 'description': 'Standard 20oz insulated bottle ideal for daily hydration', 'inventory': 50, 'sku': 'BOTTLE20OZ'},
                    {'name': '30oz Stainless Steel Water Bottle', 'price': 36.99, 'description': 'Large 30oz insulated bottle for all-day hydration', 'inventory': 35, 'sku': 'BOTTLE30OZ'}
                ]
        
        elif any(word in words for word in ['rubik', 'cube', 'speedcube', 'speedcubing']):
            return [
                {'name': 'Speed Cube 3x3', 'price': 34.99, 'description': 'Professional magnetic 3x3 speed cube with smooth turning', 'inventory': 50, 'sku': 'CUBE3X3'},
                {'name': 'Speed Cube 2x2', 'price': 19.99, 'description': 'Compact 2x2 pocket cube for beginners', 'inventory': 45, 'sku': 'CUBE2X2'},
                {'name': 'Speed Cube 4x4', 'price': 49.99, 'description': 'Advanced 4x4 magnetic speed cube', 'inventory': 30, 'sku': 'CUBE4X4'},
                {'name': 'Cube Timer Pro', 'price': 24.99, 'description': 'Professional speedcubing timer with precision timing', 'inventory': 35, 'sku': 'TIMER001'},
                {'name': 'Cube Lubricant Set', 'price': 15.99, 'description': 'Premium cube lubricants for optimal performance', 'inventory': 60, 'sku': 'LUBE001'}
            ]
        elif any(word in words for word in ['candle', 'scented', 'wax', 'fragrance']):
            return [
                {'name': 'Vanilla Soy Candle', 'price': 24.99, 'description': 'Natural vanilla scented candle', 'inventory': 45, 'sku': 'VAN001'},
                {'name': 'Lavender Dream Candle', 'price': 27.99, 'description': 'Relaxing lavender scented candle', 'inventory': 32, 'sku': 'LAV001'},
                {'name': 'Eucalyptus Mint Candle', 'price': 26.99, 'description': 'Refreshing eucalyptus mint aromatherapy candle', 'inventory': 40, 'sku': 'EUC001'},
                {'name': 'Candle Care Kit', 'price': 12.99, 'description': 'Wick trimmer and snuffer set', 'inventory': 60, 'sku': 'CARE001'}
            ]
        elif any(word in words for word in ['yoga', 'meditation', 'mat', 'pilates']):
            return [
                {'name': 'Premium Yoga Mat', 'price': 78.99, 'description': 'Non-slip premium yoga mat', 'inventory': 25, 'sku': 'MAT001'},
                {'name': 'Meditation Cushion', 'price': 45.99, 'description': 'Comfortable meditation cushion', 'inventory': 40, 'sku': 'CUSH001'},
                {'name': 'Cork Yoga Blocks', 'price': 29.99, 'description': 'Set of 2 cork yoga blocks for support', 'inventory': 55, 'sku': 'BLOCK001'},
                {'name': 'Yoga Strap', 'price': 18.99, 'description': 'Adjustable yoga strap for deeper stretches', 'inventory': 35, 'sku': 'STRAP001'}
            ]
        elif any(word in words for word in ['card', 'cards', 'deck', 'playing', 'poker']):
            return [
                {'name': 'Premium Playing Cards', 'price': 8.99, 'description': 'Professional-grade playing cards with premium linen finish and superior durability for smooth shuffling and dealing', 'inventory': 100, 'sku': 'CARDS001'},
                {'name': 'Waterproof Playing Cards', 'price': 14.99, 'description': '100% plastic waterproof cards perfect for outdoor games, pool parties, and heavy use', 'inventory': 60, 'sku': 'CARDS002'},
                {'name': 'Luxury Gold Edition Cards', 'price': 24.99, 'description': 'Elegant playing cards with gold foil accents and custom artwork in premium gift box', 'inventory': 45, 'sku': 'CARDS003'},
                {'name': 'Jumbo Index Playing Cards', 'price': 6.99, 'description': 'Easy-to-read large index cards perfect for seniors and low-vision players', 'inventory': 70, 'sku': 'CARDS004'}
            ]
        elif any(word in words for word in ['coffee', 'espresso', 'beans', 'roast']):
            return [
                {'name': 'Premium Ethiopian Coffee', 'price': 18.99, 'description': 'Single-origin Ethiopian coffee with bright floral notes and citrus undertones', 'inventory': 50, 'sku': 'COFFEE001'},
                {'name': 'Rich Colombian Blend', 'price': 16.99, 'description': 'Smooth Colombian coffee with chocolate and caramel notes, medium roast', 'inventory': 40, 'sku': 'COFFEE002'},
                {'name': 'Dark Roast Signature Blend', 'price': 15.99, 'description': 'Bold dark roast with smoky flavor and rich body, perfect for espresso', 'inventory': 35, 'sku': 'COFFEE003'},
                {'name': 'House Blend Coffee', 'price': 14.99, 'description': 'Balanced medium roast blend perfect for everyday brewing and drip coffee', 'inventory': 45, 'sku': 'COFFEE004'}
            ]
        elif any(word in words for word in ['jewelry', 'necklace', 'bracelet', 'ring', 'earring']):
            return [
                {'name': 'Moonstone Silver Necklace', 'price': 89.99, 'description': 'Handcrafted sterling silver necklace with genuine moonstone pendant', 'inventory': 25, 'sku': 'MOON001'},
                {'name': 'Rose Quartz Stud Earrings', 'price': 124.99, 'description': 'Natural rose quartz gemstone earrings in 14k gold setting', 'inventory': 20, 'sku': 'ROSE001'},
                {'name': 'Amethyst Statement Ring', 'price': 149.99, 'description': 'Bold amethyst cocktail ring with vintage-inspired design', 'inventory': 15, 'sku': 'AMETHYST001'},
                {'name': 'Turquoise Link Bracelet', 'price': 199.99, 'description': 'Southwestern-style bracelet featuring genuine turquoise stones', 'inventory': 12, 'sku': 'TURQ001'}
            ]
        elif any(word in words for word in ['book', 'books', 'novel', 'reading']):
            return [
                {'name': 'Mystery Novel Collection', 'price': 24.99, 'description': 'Thrilling mystery novel paperback', 'inventory': 60, 'sku': 'MYSTERY001'},
                {'name': 'Science Fiction Epic', 'price': 19.99, 'description': 'Award-winning science fiction novel', 'inventory': 45, 'sku': 'SCIFI001'},
                {'name': 'Self-Help Guide', 'price': 16.99, 'description': 'Practical life improvement handbook', 'inventory': 55, 'sku': 'HELP001'},
                {'name': 'Cookbook Masterclass', 'price': 29.99, 'description': 'Professional chef cookbook with 200+ recipes', 'inventory': 30, 'sku': 'COOK001'}
            ]
        elif any(word in words for word in ['fitness', 'weights', 'dumbbells', 'exercise', 'gym']):
            return [
                {'name': 'Adjustable Dumbbells Set', 'price': 199.99, 'description': 'Space-saving adjustable dumbbells with quick weight changes from 5-50 lbs per dumbbell', 'inventory': 20, 'sku': 'FITNESS001'},
                {'name': 'Resistance Band Set', 'price': 34.99, 'description': 'Professional resistance bands with varying resistance levels and door anchor system', 'inventory': 40, 'sku': 'FITNESS002'},
                {'name': 'Premium Foam Roller', 'price': 29.99, 'description': 'High-density foam roller for deep tissue massage and muscle recovery therapy', 'inventory': 35, 'sku': 'FITNESS003'},
                {'name': 'Exercise Mat Pro', 'price': 39.99, 'description': 'Non-slip exercise mat with alignment guides for yoga, pilates, and stretching', 'inventory': 45, 'sku': 'FITNESS004'}
            ]
        elif any(word in words for word in ['plant', 'plants', 'succulent', 'garden', 'flower']):
            return [
                {'name': 'Succulent Garden Set', 'price': 34.99, 'description': 'Collection of 6 assorted succulent plants perfect for indoor gardens', 'inventory': 25, 'sku': 'PLANT001'},
                {'name': 'Modern Ceramic Planter', 'price': 18.99, 'description': 'Sleek ceramic planter with drainage system for optimal plant health', 'inventory': 40, 'sku': 'PLANT002'},
                {'name': 'Plant Care Essentials Kit', 'price': 24.99, 'description': 'Complete plant care tools and organic fertilizer set for healthy growth', 'inventory': 35, 'sku': 'PLANT003'},
                {'name': 'Hanging Garden Planter', 'price': 29.99, 'description': 'Macrame hanging planter perfect for air plants and trailing varieties', 'inventory': 30, 'sku': 'PLANT004'}
            ]
        elif any(word in words for word in ['toilet', 'paper', 'bathroom', 'tissue']):
            return [
                {'name': 'Ultra-Soft Toilet Paper', 'price': 12.99, 'description': '3-ply ultra-soft toilet paper made from sustainable bamboo fibers, 12-pack', 'inventory': 100, 'sku': 'TOILET001'},
                {'name': 'Eco-Friendly Toilet Paper', 'price': 15.99, 'description': '100% recycled toilet paper that is septic-safe and environmentally friendly, 24-pack', 'inventory': 80, 'sku': 'TOILET002'},
                {'name': 'Premium Quilted Toilet Paper', 'price': 18.99, 'description': 'Luxurious quilted toilet paper with aloe and vitamin E for ultimate comfort, 18-pack', 'inventory': 60, 'sku': 'TOILET003'},
                {'name': 'Commercial Grade Toilet Paper', 'price': 22.99, 'description': 'Bulk commercial toilet paper perfect for offices and high-traffic areas, 36-pack', 'inventory': 40, 'sku': 'TOILET004'}
            ]
        elif any(word in words for word in ['soap', 'shampoo', 'body', 'wash', 'personal', 'care']):
            return [
                {'name': 'Natural Body Soap', 'price': 8.99, 'description': 'Handcrafted natural soap with organic oils and essential fragrances', 'inventory': 60, 'sku': 'SOAP001'},
                {'name': 'Moisturizing Shampoo', 'price': 14.99, 'description': 'Sulfate-free shampoo with argan oil for healthy, shiny hair', 'inventory': 45, 'sku': 'SOAP002'},
                {'name': 'Exfoliating Body Scrub', 'price': 12.99, 'description': 'Gentle exfoliating scrub with sea salt and natural botanicals', 'inventory': 35, 'sku': 'SOAP003'},
                {'name': 'Luxury Body Wash Set', 'price': 24.99, 'description': 'Premium body wash collection with 3 signature scents', 'inventory': 30, 'sku': 'SOAP004'}
            ]
        elif any(word in words for word in ['phone', 'case', 'screen', 'protector', 'mobile', 'accessories']):
            return [
                {'name': 'Universal Phone Case', 'price': 19.99, 'description': 'Protective phone case with shock absorption and wireless charging compatibility', 'inventory': 75, 'sku': 'PHONE001'},
                {'name': 'Tempered Glass Screen Protector', 'price': 9.99, 'description': 'Ultra-clear tempered glass screen protector with bubble-free installation', 'inventory': 100, 'sku': 'PHONE002'},
                {'name': 'Wireless Charging Pad', 'price': 29.99, 'description': 'Fast wireless charging pad compatible with all Qi-enabled devices', 'inventory': 50, 'sku': 'PHONE003'},
                {'name': 'Portable Phone Stand', 'price': 14.99, 'description': 'Adjustable phone stand perfect for video calls and media viewing', 'inventory': 60, 'sku': 'PHONE004'}
            ]
        elif any(word in words for word in ['snack', 'food', 'nuts', 'chips', 'healthy']):
            return [
                {'name': 'Gourmet Trail Mix', 'price': 8.99, 'description': 'Premium trail mix with almonds, cranberries, and dark chocolate chips', 'inventory': 80, 'sku': 'SNACK001'},
                {'name': 'Organic Protein Bars', 'price': 24.99, 'description': 'Plant-based protein bars with natural ingredients, 12-pack variety', 'inventory': 50, 'sku': 'SNACK002'},
                {'name': 'Artisan Nut Collection', 'price': 16.99, 'description': 'Roasted and seasoned premium nuts including cashews, almonds, and pecans', 'inventory': 40, 'sku': 'SNACK003'},
                {'name': 'Healthy Veggie Chips', 'price': 6.99, 'description': 'Baked vegetable chips made from sweet potatoes, beets, and carrots', 'inventory': 70, 'sku': 'SNACK004'}
            ]
        else:
            return self._generate_default_products()
    
    def _generate_default_products(self) -> List[Dict]:
        """DO NOT generate default products - return empty list to force proper parsing"""
        print("⚠️ No products could be parsed from prompt - refusing to create random products")
        return []
    
    def _create_fallback_concept(self, prompt: str) -> Dict:
        """Create a concept based on the user's specific request if AI fails - GENERIC approach"""
        # Extract key information from prompt
        prompt_lower = prompt.lower()
        
        # Try to extract products first
        extracted_products = self._extract_products_from_prompt(prompt)
        if extracted_products:
            # Build store concept around the extracted products
            product_name = extracted_products[0]['name']
            
            # Generate store name based on the product
            base_product = self._extract_main_product_from_prompt(prompt_lower)
            if base_product:
                store_name = f"{base_product.title()} Store"
            else:
                store_name = "Custom Store"
            
            tagline = "Exactly What You Asked For"
            products = extracted_products
        else:
            # Fallback to generic products if we can't parse anything specific
            main_product = self._extract_main_product_from_prompt(prompt_lower)
            if main_product:
                store_name = f"{main_product.title()} Store"
                tagline = f"Premium {main_product.title()} Products"
                products = self._generate_product_variations(main_product, prompt_lower)
            else:
                store_name = 'Quality Goods Store'
                tagline = 'Premium Products, Exceptional Value'
                products = self._generate_default_products()
        
        return {
            'store_name': store_name,
            'tagline': tagline,
            'products': products,
            'brand_values': ['Quality', 'Customer Service', 'Innovation'],
            'blog_posts': ['Getting Started Guide', 'Product Care Tips', 'Customer Stories'],
            'color_scheme': self._get_random_color_scheme()
        }
    
    def _get_random_color_scheme(self) -> Dict:
        """Get a random color scheme"""
        schemes = [
            {'primary': '#2E7D32', 'secondary': '#66BB6A', 'accent': '#FFC107'},
            {'primary': '#1565C0', 'secondary': '#42A5F5', 'accent': '#FF7043'},
            {'primary': '#6A1B9A', 'secondary': '#BA68C8', 'accent': '#26C6DA'},
            {'primary': '#D32F2F', 'secondary': '#EF5350', 'accent': '#FFC107'},
            {'primary': '#F57C00', 'secondary': '#FFB74D', 'accent': '#26A69A'}
        ]
        return random.choice(schemes)
    
    def _simulate_store_creation(self, concept: Dict) -> Dict:
        """Simulate store creation for demo purposes"""
        store_url = f"https://{concept['store_name'].lower().replace(' ', '-')}.myshopify.com"
        
        print(f"🏪 Creating store: {concept['store_name']}")
        time.sleep(1)
        
        print(f"📦 Adding {len(concept['products'])} products...")
        for product in concept['products']:
            print(f"   ✅ {product['name']} - ${product['price']}")
            time.sleep(0.3)
        
        print(f"📚 Creating collection: {concept['store_name']} Collection")
        time.sleep(0.5)
        
        print(f"✍️ Adding {len(concept['blog_posts'])} blog posts...")
        time.sleep(0.5)
        
        print("🎨 Customizing theme...")
        time.sleep(0.5)
        
        print("🧭 Setting up navigation...")
        time.sleep(0.5)
        
        return {
            'success': True,
            'store_url': store_url,
            'admin_url': f"{store_url}/admin",
            'concept': concept,
            'products_created': len(concept['products']),
            'mode': 'demo'
        }
    
    def _create_real_shopify_store(self, concept: Dict) -> Dict:
        """Create actual Shopify store (requires credentials)"""
        try:
            # Update store info
            self._update_store_info(concept)
            
            # Create products
            if not concept.get('products'):
                print("⚠️ Concept contains 0 products; nothing will be pushed to Shopify.")
                print("   Tip: Provide explicit product names/quantities or use more specific prompts.")
                product_ids = []
            else:
                product_ids = self._create_products(concept['products'])
            
            # Create collection
            collection_id = self._create_collection(concept)
            
            # Add products to collection
            self._add_products_to_collection(collection_id, product_ids)
            
            # Create blog posts
            self._create_blog_posts(concept['blog_posts'])
            
            # Customize theme
            self._customize_theme(concept)
            
            return {
                'success': True,
                'store_url': f"https://{self.shop_domain}",
                'admin_url': f"https://{self.shop_domain}/admin",
                'concept': concept,
                'products_created': len(product_ids),
                'collection_id': collection_id,
                'mode': 'real'
            }
            
        except Exception as e:
            print(f"❌ Error creating real store: {e}")
            return {'success': False, 'error': str(e)}
    
    def _update_store_info(self, concept: Dict):
        """Update store name and description"""
        print(f"🏪 Setting store name: {concept['store_name']}")
        # Shopify API call would go here
    
    def _create_products(self, products: List[Dict]) -> List[int]:
        """Create products in Shopify with enhanced descriptions and competitive pricing"""
        product_ids = []
        print(f"📦 Creating {len(products)} products with market research...")
        
        for product in products:
            # Enhance product with market research
            print(f"🔍 Researching: {product['name']}")
            enhanced_product = self.researcher.enhance_product_with_research(product)
            
            print(f"   ✅ {enhanced_product['name']} - ${enhanced_product['price']:.2f}")
            if enhanced_product.get('market_research', {}).get('research_notes'):
                print(f"      💡 {enhanced_product['market_research']['research_notes']}")
            
            # Create detailed HTML description
            html_description = self._create_product_html_description(enhanced_product)
            
            # Create the product via Shopify API
            product_data = {
                "product": {
                    "title": enhanced_product['name'],
                    "body_html": html_description,
                    "vendor": "Premium Store",
                    "product_type": self._determine_product_type(enhanced_product['name']),
                    "tags": self._generate_product_tags(enhanced_product),
                    "variants": [{
                        "price": str(enhanced_product['price']),
                        "sku": enhanced_product.get('sku', f"SKU-{random.randint(1000, 9999)}"),
                        "inventory_management": "shopify",
                        "inventory_quantity": enhanced_product.get('inventory', 50),
                        "weight": random.randint(100, 2000),  # grams
                        "requires_shipping": True
                    }],
                    "images": []  # Could add image URLs here
                }
            }
            
            try:
                response = requests.post(
                    f"{self.api_base}/products.json",
                    headers=self.headers,
                    json=product_data
                )
                
                if response.status_code == 201:
                    product_id = response.json()['product']['id']
                    product_ids.append(product_id)
                    
                    # Generate and upload product image
                    self._add_product_image(product_id, enhanced_product['name'])
                    
                else:
                    print(f"   ⚠️ Failed to create {product['name']}: {response.status_code}")
                    print(f"   Error: {response.text}")
                    
            except Exception as e:
                print(f"   ❌ API error for {product['name']}: {e}")
            
            time.sleep(0.5)  # Rate limiting
        
        return product_ids
    
    def _create_product_html_description(self, product: Dict) -> str:
        """Create detailed HTML description for a product"""
        description = product.get('description', '')
        features = product.get('key_features', [])
        
        html = f"<div class='product-description'>"
        html += f"<p class='main-description'>{description}</p>"
        
        if features:
            html += "<h3>Key Features:</h3><ul class='feature-list'>"
            for feature in features[:6]:  # Limit to 6 features
                html += f"<li>{feature}</li>"
            html += "</ul>"
        
        # Market research is kept internal only - not displayed on website
        
        html += "</div>"
        return html
    
    def _determine_product_type(self, product_name: str) -> str:
        """Determine Shopify product type based on product name"""
        name_lower = product_name.lower()
        
        if any(word in name_lower for word in ['cube', 'rubik', 'timer']):
            return "Puzzles & Games"
        elif 'candle' in name_lower:
            return "Home & Garden"
        elif any(word in name_lower for word in ['yoga', 'meditation', 'mat']):
            return "Sports & Recreation"
        elif any(word in name_lower for word in ['shirt', 'tee', 'clothing']):
            return "Apparel & Accessories"
        else:
            return "General"
    
    def _generate_product_tags(self, product: Dict) -> str:
        """Generate relevant tags for the product"""
        name = product['name'].lower()
        tags = []
        
        # Add category-based tags
        if 'cube' in name or 'rubik' in name:
            tags.extend(['speedcube', 'puzzle', 'brain-teaser', 'competition', 'fidget'])
        elif 'candle' in name:
            tags.extend(['home-decor', 'aromatherapy', 'relaxation', 'ambiance', 'gift'])
        elif 'yoga' in name or 'meditation' in name:
            tags.extend(['wellness', 'fitness', 'mindfulness', 'exercise', 'health'])
        
        # Add quality indicators
        tags.extend(['premium', 'professional', 'high-quality'])
        
        return ', '.join(tags)
    
    def _create_collection(self, concept: Dict) -> int:
        """Create product collection"""
        collection_name = f"{concept['store_name']} Collection"
        print(f"📚 Creating collection: {collection_name}")
        
        collection_data = {
            "custom_collection": {
                "title": collection_name,
                "body_html": f"Curated collection of {concept['store_name']} products",
                "published": True
            }
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/custom_collections.json",
                headers=self.headers,
                json=collection_data
            )
            
            if response.status_code == 201:
                collection_id = response.json()['custom_collection']['id']
                return collection_id
            else:
                print(f"   ⚠️ Failed to create collection: {response.status_code}")
                print(f"   Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ API error creating collection: {e}")
            return None
    
    def _add_products_to_collection(self, collection_id: int, product_ids: List[int]):
        """Add products to collection"""
        if not collection_id or not product_ids:
            return
            
        print(f"🔗 Adding {len(product_ids)} products to collection")
        
        for product_id in product_ids:
            collect_data = {
                "collect": {
                    "product_id": product_id,
                    "collection_id": collection_id
                }
            }
            
            try:
                response = requests.post(
                    f"{self.api_base}/collects.json",
                    headers=self.headers,
                    json=collect_data
                )
                
                if response.status_code != 201:
                    print(f"   ⚠️ Failed to add product {product_id} to collection")
                    
            except Exception as e:
                print(f"   ❌ API error adding product to collection: {e}")
            
            time.sleep(0.2)  # Rate limiting
    
    def _create_blog_posts(self, blog_titles: List[str]):
        """Create blog posts"""
        if not blog_titles:
            return
            
        print(f"✍️ Creating {len(blog_titles)} blog posts...")
        
        # First, create a blog if it doesn't exist
        blog_data = {
            "blog": {
                "title": "Store News & Updates",
                "handle": "news"
            }
        }
        
        try:
            # Check if blog exists or create it
            blog_response = requests.get(f"{self.api_base}/blogs.json", headers=self.headers)
            if blog_response.status_code == 200:
                blogs = blog_response.json().get('blogs', [])
                blog_id = blogs[0]['id'] if blogs else None
                
                if not blog_id:
                    # Create blog
                    create_blog_response = requests.post(
                        f"{self.api_base}/blogs.json",
                        headers=self.headers,
                        json=blog_data
                    )
                    if create_blog_response.status_code == 201:
                        blog_id = create_blog_response.json()['blog']['id']
                    else:
                        print("   ⚠️ Failed to create blog")
                        return
                
                # Create blog posts
                for title in blog_titles[:3]:  # Limit to 3
                    print(f"   📝 {title}")
                    
                    post_data = {
                        "article": {
                            "title": title,
                            "body_html": f"<p>Welcome to our latest update about {title.lower()}. We're excited to share this information with our customers.</p>",
                            "published": True
                        }
                    }
                    
                    try:
                        post_response = requests.post(
                            f"{self.api_base}/blogs/{blog_id}/articles.json",
                            headers=self.headers,
                            json=post_data
                        )
                        
                        if post_response.status_code != 201:
                            print(f"   ⚠️ Failed to create blog post: {title}")
                            
                    except Exception as e:
                        print(f"   ❌ Error creating blog post '{title}': {e}")
                    
                    time.sleep(0.3)  # Rate limiting
                    
        except Exception as e:
            print(f"   ❌ API error with blog posts: {e}")
    
    def _customize_theme(self, concept: Dict):
        """Customize store theme"""
        print("🎨 Customizing theme colors and fonts...")
        # Theme customization API calls would go here
    
    def _add_product_image(self, product_id: int, product_name: str):
        """Generate and upload an image for a product"""
        try:
            # Determine category for better image generation
            category = self.image_generator._detect_category(product_name)
            
            # Generate image
            image_bytes = self.image_generator.generate_product_image(product_name, category)
            
            if image_bytes:
                # Create filename
                safe_name = re.sub(r'[^a-zA-Z0-9\s]', '', product_name)
                safe_name = re.sub(r'\s+', '_', safe_name).lower()
                filename = f"{safe_name}_product_image.png"
                
                # Upload to Shopify
                success = self.image_generator.upload_image_to_shopify(
                    image_bytes, filename, str(product_id), 
                    self.shop_domain, self.access_token
                )
                
                if success:
                    print(f"   🖼️ Added product image for {product_name}")
                else:
                    print(f"   ⚠️ Failed to upload image for {product_name}")
            else:
                print(f"   ⚠️ Failed to generate image for {product_name}")
                
        except Exception as e:
            print(f"   ❌ Error adding image for {product_name}: {e}")

    def _get_all_products(self) -> List[Dict]:
        """Get all products from Shopify store"""
        if not self.real_mode:
            return []
        
        try:
            url = f"https://{self.shop_domain}/admin/api/2023-10/products.json"
            headers = {
                'X-Shopify-Access-Token': self.access_token,
                'Content-Type': 'application/json'
            }
            
            all_products = []
            page_info = None
            
            while True:
                params = {'limit': 250}
                if page_info:
                    params['page_info'] = page_info
                
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                products = data.get('products', [])
                all_products.extend(products)
                
                # Check for pagination
                link_header = response.headers.get('Link', '')
                if 'rel="next"' not in link_header:
                    break
                
                # Extract next page info from Link header
                for link in link_header.split(','):
                    if 'rel="next"' in link:
                        page_info = link.split('page_info=')[1].split('>')[0]
                        break
                else:
                    break
            
            return all_products
            
        except Exception as e:
            print(f"❌ Error fetching products: {e}")
            return []

    def _get_product(self, product_id: str) -> Optional[Dict]:
        """Get a specific product by ID"""
        if not self.real_mode:
            return None
        
        try:
            url = f"https://{self.shop_domain}/admin/api/2023-10/products/{product_id}.json"
            headers = {
                'X-Shopify-Access-Token': self.access_token,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data.get('product')
            
        except Exception as e:
            print(f"❌ Error fetching product {product_id}: {e}")
            return None

    def _find_product_by_name(self, product_name: str) -> Optional[Dict]:
        """Find a product by name/title (fuzzy matching)"""
        products = self._get_all_products()
        if not products:
            return None
        
        product_name_lower = product_name.lower().strip()
        
        # First try exact match
        for product in products:
            title = product.get('title', '').lower()
            if title == product_name_lower:
                return product
        
        # Then try partial matches
        for product in products:
            title = product.get('title', '').lower()
            # Check if product name is contained in title or vice versa
            if product_name_lower in title or title in product_name_lower:
                return product
        
        # Try keyword matching
        product_keywords = product_name_lower.split()
        for product in products:
            title = product.get('title', '').lower()
            # Check if all keywords from product_name are in the title
            if all(keyword in title for keyword in product_keywords):
                return product
        
        return None

    def _identify_product_from_prompt(self, prompt: str) -> Optional[Dict]:
        """Identify which product to edit from a natural language prompt"""
        prompt_lower = prompt.lower()
        
        # Common patterns for identifying products
        product_patterns = [
            r'(?:change|edit|update|modify)\s+(?:the\s+)?([^,\s]+(?:\s+[^,\s]+)*?)(?:\s+(?:to|into|and))',
            r'(?:make|turn)\s+(?:the\s+)?([^,\s]+(?:\s+[^,\s]+)*?)(?:\s+(?:into|to))',
            r'(?:the\s+)?([^,\s]+(?:\s+[^,\s]+)*?)(?:\s+(?:should|needs|must))',
            r'(?:for\s+(?:the\s+)?)?([^,\s]+(?:\s+[^,\s]+)*?)(?:\s+(?:product|item))',
        ]
        
        # Try to extract product identifier from prompt
        for pattern in product_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                potential_product_name = match.group(1).strip()
                
                # Skip common words that aren't product names
                skip_words = ['it', 'this', 'that', 'product', 'item', 'thing']
                if potential_product_name not in skip_words:
                    product = self._find_product_by_name(potential_product_name)
                    if product:
                        return product
        
        # If no specific product identified, try common product types mentioned
        products = self._get_all_products()
        if not products:
            return None
        
        # Look for product type mentions
        for product in products:
            title = product.get('title', '').lower()
            title_words = title.split()
            
            # Check if any significant word from the title appears in the prompt
            for word in title_words:
                if len(word) > 3 and word in prompt_lower:  # Skip short words
                    return product
        
        return None

    def _update_product(self, product_id: str, updates: Dict) -> Optional[Dict]:
        """Update a product with new data"""
        if not self.real_mode:
            print(f"🎭 Demo Mode: Would update product {product_id} with {updates}")
            return updates
        
        try:
            url = f"https://{self.shop_domain}/admin/api/2023-10/products/{product_id}.json"
            headers = {
                'X-Shopify-Access-Token': self.access_token,
                'Content-Type': 'application/json'
            }
            
            # Prepare product data for Shopify API
            product_data = {
                'product': updates
            }
            
            response = requests.put(url, headers=headers, json=product_data)
            response.raise_for_status()
            
            data = response.json()
            updated_product = data.get('product')
            
            print(f"✅ Product {product_id} updated successfully")
            return updated_product
            
        except Exception as e:
            print(f"❌ Error updating product {product_id}: {e}")
            raise

    def _parse_product_edit_prompt(self, prompt: str, current_product: Dict) -> Dict:
        """Parse editing instructions from natural language prompt"""
        prompt_lower = prompt.lower()
        updates = {}
        
        # Current product details
        current_title = current_product.get('title', '')
        current_description = current_product.get('body_html', '')
        current_price = None
        
        # Get current price from variants
        variants = current_product.get('variants', [])
        if variants:
            current_price = float(variants[0].get('price', 0))
        
        # Parse different types of changes
        
        # 1. Title/Name changes
        if any(word in prompt_lower for word in ['title', 'name', 'call it', 'rename']):
            title_patterns = [
                r'(?:title|name|call it|rename).*?["\']([^"\']+)["\']',
                r'(?:title|name|call it|rename).*?(?:to|as)\s+([^,\.\!]+)',
            ]
            
            for pattern in title_patterns:
                match = re.search(pattern, prompt, re.IGNORECASE)
                if match:
                    new_title = match.group(1).strip()
                    updates['title'] = new_title
                    updates['generate_new_image'] = True
                    break
        
        # 2. Scent/Flavor changes
        scent_patterns = [
            r'(?:change|make|turn).*?(?:to|into)\s+([^,\.\!]+?)(?:\s+(?:scented|flavored|flavor|scent))',
            r'(?:scented|flavored|flavor|scent).*?(?:to|as|with)\s+([^,\.\!]+)',
            r'(?:vanilla|lavender|cherry|lemon|mint|chocolate|strawberry|coconut|pine|eucalyptus)'
        ]
        
        for pattern in scent_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                if len(match.groups()) > 0:
                    scent = match.group(1).strip()
                else:
                    scent = match.group(0).strip()
                
                # Update title to include new scent
                base_title = current_title
                # Remove existing scent words
                scent_words = ['vanilla', 'lavender', 'cherry', 'lemon', 'mint', 'chocolate', 'strawberry', 'coconut', 'pine', 'eucalyptus']
                for word in scent_words:
                    base_title = re.sub(rf'\b{word}\b', '', base_title, flags=re.IGNORECASE).strip()
                
                # Clean up extra spaces
                base_title = re.sub(r'\s+', ' ', base_title).strip()
                
                # Add new scent
                updates['title'] = f"{scent.title()} {base_title}"
                updates['generate_new_image'] = True
                break
        
        # 3. Color changes
        colors = ['black', 'white', 'silver', 'blue', 'red', 'green', 'gold', 'rose gold', 'pink', 'purple', 'orange', 'yellow', 'brown', 'gray', 'grey']
        color_patterns = [
            r'(?:change|make|turn).*?(?:to|into)\s+((?:' + '|'.join(colors) + r'))',
            r'(?:color|colored).*?(?:to|as)\s+((?:' + '|'.join(colors) + r'))',
        ]
        
        for pattern in color_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                new_color = match.group(1).strip()
                
                # Update title to include new color
                base_title = current_title
                # Remove existing color words
                for color in colors:
                    base_title = re.sub(rf'\b{color}\b', '', base_title, flags=re.IGNORECASE).strip()
                
                # Clean up extra spaces
                base_title = re.sub(r'\s+', ' ', base_title).strip()
                
                # Add new color
                updates['title'] = f"{new_color.title()} {base_title}"
                updates['generate_new_image'] = True
                break
        
        # 4. Size/Capacity changes
        size_patterns = [
            r'(?:change|make|turn).*?(?:to|into)\s+(\d+)\s*(oz|ounce|ml|liter|inch|inches|ft|feet)',
            r'(?:size|capacity).*?(?:to|as)\s+(\d+)\s*(oz|ounce|ml|liter|inch|inches|ft|feet)',
            r'(\d+)\s*(oz|ounce|ml|liter|inch|inches|ft|feet)'
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                size = match.group(1)
                unit = match.group(2)
                
                # Normalize unit
                if unit in ['ounce']:
                    unit = 'oz'
                elif unit in ['liter']:
                    unit = 'L'
                elif unit in ['inches']:
                    unit = 'inch'
                elif unit in ['feet']:
                    unit = 'ft'
                
                # Update title
                base_title = current_title
                # Remove existing size info
                base_title = re.sub(r'\d+\s*(oz|ounce|ml|liter|inch|inches|ft|feet|L)', '', base_title, flags=re.IGNORECASE).strip()
                base_title = re.sub(r'\s+', ' ', base_title).strip()
                
                updates['title'] = f"{base_title} - {size}{unit}"
                
                # Update description
                description = current_description or ""
                if f"{size}{unit}" not in description:
                    description += f"\n<p><strong>Size:</strong> {size}{unit}</p>"
                    updates['body_html'] = description
                
                updates['generate_new_image'] = True
                break
        
        # 5. Price changes
        price_patterns = [
            r'(?:change|make|set).*?(?:price|cost).*?(?:to|as)\s*\$?(\d+\.?\d*)',
            r'(?:price|cost).*?(?:to|as)\s*\$?(\d+\.?\d*)',
            r'\$(\d+\.?\d*)'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                new_price = float(match.group(1))
                updates['variants'] = [{'price': str(new_price)}]
                break
        
        # 6. Description/Feature changes
        if any(word in prompt_lower for word in ['description', 'details', 'feature', 'add']):
            if current_description:
                updates['body_html'] = self._enhance_product_description(current_description, prompt)
        
        # 7. Material changes
        materials = ['stainless steel', 'plastic', 'glass', 'ceramic', 'wood', 'metal', 'fabric', 'leather', 'cotton']
        for material in materials:
            if material in prompt_lower:
                base_title = current_title
                # Remove existing material words
                for mat in materials:
                    base_title = re.sub(rf'\b{mat}\b', '', base_title, flags=re.IGNORECASE).strip()
                
                base_title = re.sub(r'\s+', ' ', base_title).strip()
                updates['title'] = f"{material.title()} {base_title}"
                updates['generate_new_image'] = True
                break
        
        return updates

    def _enhance_product_description(self, current_description: str, prompt: str) -> str:
        """Enhance product description based on editing prompt"""
        # Add features mentioned in prompt
        enhancements = []
        
        if 'durable' in prompt.lower():
            enhancements.append("<li>Durable construction</li>")
        if 'insulated' in prompt.lower():
            enhancements.append("<li>Double-wall insulated</li>")
        if 'leak proof' in prompt.lower() or 'leak-proof' in prompt.lower():
            enhancements.append("<li>Leak-proof design</li>")
        if 'eco friendly' in prompt.lower() or 'sustainable' in prompt.lower():
            enhancements.append("<li>Eco-friendly materials</li>")
        
        if enhancements:
            features_html = f"""
            <h3>Key Features:</h3>
            <ul>
                {''.join(enhancements)}
            </ul>
            """
            return current_description + features_html
        
        return current_description

    def _generate_and_upload_product_image(self, product_title: str, product_id: str) -> Optional[str]:
        """Generate and upload a new product image"""
        try:
            # Generate image using AI
            image_bytes = self.image_generator.generate_product_image(product_title)
            
            if image_bytes and len(image_bytes) > 1000:
                # Create filename
                safe_name = re.sub(r'[^a-zA-Z0-9\s]', '', product_title)
                safe_name = re.sub(r'\s+', '_', safe_name).lower()
                filename = f"{safe_name}_updated.png"
                
                # Upload to Shopify using the image generator's method
                success = self.image_generator.upload_image_to_shopify(
                    image_bytes, filename, product_id, 
                    self.shop_domain, self.access_token
                )
                
                if success:
                    print(f"   🖼️ Generated and uploaded new image for {product_title}")
                    return f"Updated image for {product_title}"
                else:
                    print(f"   ⚠️ Failed to upload generated image for {product_title}")
            else:
                print(f"   ⚠️ Failed to generate image for {product_title}")
        
        except Exception as e:
            print(f"❌ Error generating/uploading image: {e}")
        
        return None

    def _update_product_image(self, product_id: str, image_url: str):
        """Update product's main image"""
        if not self.real_mode:
            print(f"🎭 Demo Mode: Would update product {product_id} image to {image_url}")
            return
        
        try:
            url = f"https://{self.shop_domain}/admin/api/2023-10/products/{product_id}/images.json"
            headers = {
                'X-Shopify-Access-Token': self.access_token,
                'Content-Type': 'application/json'
            }
            
            image_data = {
                'image': {
                    'src': image_url,
                    'position': 1
                }
            }
            
            response = requests.post(url, headers=headers, json=image_data)
            response.raise_for_status()
            
            print(f"✅ Product {product_id} image updated")
            
        except Exception as e:
            print(f"❌ Error updating product image: {e}")


def interactive_store_creator():
    """Interactive interface for creating stores"""
    print("🛍️ AI-Powered Shopify Store Creator")
    print("=" * 50)
    print("💡 Just describe what you want to sell, and I'll create a complete store!")
    print()
    
    # Initialize creator
    creator = CompleteShopifyStoreCreator()
    
    while True:
        print("\n" + "─" * 50)
        prompt = input("📝 What kind of store do you want to create? (or 'quit' to exit)\n> ").strip()
        
        if prompt.lower() in ['quit', 'exit', 'q']:
            print("👋 Thanks for using the AI Store Creator!")
            break
        
        if not prompt:
            continue
        
        try:
            result = creator.create_store_from_prompt(prompt)
            
            if result.get('success', True):
                print(f"\n🎉 SUCCESS! Your store is ready:")
                print(f"🌐 Store URL: {result['store_url']}")
                print(f"⚙️ Admin Panel: {result['admin_url']}")
                print(f"📦 Products: {result['products_created']} items created")
                print(f"🏪 Store Name: {result['concept']['store_name']}")
                print(f"💭 Tagline: {result['concept']['tagline']}")
                
                if result.get('mode') == 'demo':
                    print("\n📝 Note: This was a demo. To create real stores:")
                    print("   1. Set up Shopify API credentials")
                    print("   2. Run with real_mode=True")
            else:
                print(f"❌ Failed to create store: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")


def quick_test():
    """Quick test with sample prompts"""
    creator = CompleteShopifyStoreCreator()
    
    test_prompts = [
        "Create a store for selling handmade candles and home fragrances",
        "I want to sell yoga equipment and meditation accessories",
        "Generate a store for vintage band t-shirts and music merchandise"
    ]
    
    for prompt in test_prompts:
        print(f"\n🧪 Testing: {prompt}")
        result = creator.create_store_from_prompt(prompt)
        print(f"✅ Created: {result['concept']['store_name']}")
        time.sleep(2)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        quick_test()
    else:
        interactive_store_creator()
