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
        try:
            # Import our trained model
            from chat_assistant import ShopifyAssistant
            
            assistant = ShopifyAssistant()
            response = assistant.respond(prompt)
            
            print(f"🤖 AI Response: {response[:200]}...")
            
            # Parse the AI response
            concept = self._parse_ai_response(response, prompt)
            
            print(f"✅ AI generated: {concept['store_name']}")
            print(f"   Tagline: {concept['tagline']}")
            print(f"   Products: {len(concept['products'])} items")
            
            return concept
            
        except Exception as e:
            print(f"⚠️ AI generation failed, using fallback: {e}")
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
        products = []
        
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
                # Get text after the indicator
                parts = prompt_lower.split(indicator, 1)
                if len(parts) > 1:
                    product_text = parts[1].strip()
                    break
        
        if not product_text:
            return []
        
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
                
                # Determine product name
                if len(words) >= 2:
                    # Check for common compound products
                    two_word = ' '.join(words[:2]).lower()
                    if any(combo in two_word for combo in ['vanilla candle', 'lavender candle', 'cherry candle', 
                                                           'soy candle', 'scented candle', 'aromatherapy candle',
                                                           'water bottle', 'coffee bean', 'yoga mat', 'speed cube']):
                        product_name = ' '.join(words[:2])
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
                    'price': round(base_price, 2),
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
            r'shop\s+for\s+([^,\n]+)'
        ]
        
        import re
        for pattern in patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                product_text = match.group(1).strip()
                # Clean up the match
                product_text = re.sub(r'\s*(make\s+sure|with\s+\d+|stock|inventory).*', '', product_text)
                
                if product_text:
                    return [{
                        'name': product_text.title(),
                        'price': 19.99,
                        'description': f"Premium {product_text} with high-quality materials and excellent craftsmanship.",
                        'inventory': 50
                    }]
        
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
    
    def _generate_product_specific_description(self, product_name: str, material: str = None, color: str = None, size: str = None) -> str:
        """Generate product-specific descriptions based on the product type"""
        product_lower = product_name.lower()
        
        # Water bottles and drinkware
        if any(word in product_lower for word in ['water', 'bottle', 'flask', 'tumbler', 'mug']):
            descriptions = [
                f"Constructed from premium {material or 'stainless steel'}, this {product_name.lower()} features double-wall vacuum insulation that keeps beverages ice-cold for 24+ hours or piping hot for 12+ hours",
                f"This {product_name.lower()} combines advanced insulation technology with leak-proof engineering, featuring a comfortable grip design and wide mouth for easy filling and cleaning",
                f"Engineered for maximum hydration with fewer refills, this {product_name.lower()} offers superior temperature retention with durable construction built to last"
            ]
            base_desc = random.choice(descriptions)
            
            if size:
                base_desc += f". The {size} capacity provides optimal hydration for daily activities, commuting, or outdoor adventures"
            else:
                base_desc += f". Perfect for daily hydration, workouts, or travel"
                
            if color:
                base_desc += f" with a sleek {color} finish that's both stylish and functional"
                
            if material and 'steel' in material:
                base_desc += f". The ergonomic design includes comfort-grip features and fits most standard cup holders"
            else:
                base_desc += f". Features an ergonomic design for comfortable carrying and convenient storage"
        
        # Toilet paper and bathroom products
        elif any(word in product_lower for word in ['toilet', 'paper', 'tissue']):
            descriptions = [
                f"Ultra-soft {product_name.lower()} crafted from sustainable bamboo fibers, offering superior comfort and absorbency with 3-ply construction for strength you can trust",
                f"Premium {product_name.lower()} engineered with advanced quilting technology for maximum softness and durability, featuring septic-safe biodegradable materials",
                f"Eco-conscious {product_name.lower()} made from 100% recycled materials with enhanced absorption and gentle texture for sensitive skin"
            ]
            base_desc = random.choice(descriptions)
            base_desc += ". Each sheet provides reliable performance for everyday use while being gentle on skin and safe for all plumbing systems. Manufactured using environmentally responsible processes for sustainable household care."
        
        # Electronics and tech
        elif any(word in product_lower for word in ['headphones', 'earbuds', 'speaker', 'charger', 'phone', 'laptop']):
            descriptions = [
                f"Professional-grade {product_name.lower()} featuring advanced technology for superior performance",
                f"High-quality {product_name.lower()} designed for seamless connectivity and exceptional user experience",
                f"Premium {product_name.lower()} with cutting-edge features and reliable durability"
            ]
            base_desc = random.choice(descriptions)
            if color:
                base_desc += f" in an elegant {color} finish"
        
        # Clothing and apparel
        elif any(word in product_lower for word in ['shirt', 't-shirt', 'tee', 'hoodie', 'jacket', 'pants', 'jeans']):
            descriptions = [
                f"Comfortable {product_name.lower()} made from premium materials for all-day wearability",
                f"Stylish {product_name.lower()} featuring modern design and superior fabric quality",
                f"Classic {product_name.lower()} with perfect fit and timeless appeal"
            ]
            base_desc = random.choice(descriptions)
            if material:
                base_desc += f". Crafted from soft {material} for maximum comfort"
            if color:
                base_desc += f" available in vibrant {color}"
        
        # Home and garden
        elif any(word in product_lower for word in ['candle', 'lamp', 'plant', 'planter', 'decor']):
            descriptions = [
                f"Elegant {product_name.lower()} designed to enhance your living space with style and functionality",
                f"Beautiful {product_name.lower()} featuring premium craftsmanship and attention to detail",
                f"Sophisticated {product_name.lower()} that brings warmth and ambiance to any room"
            ]
            base_desc = random.choice(descriptions)
            if material:
                base_desc += f". Made from quality {material} for lasting beauty"
            if color:
                base_desc += f" in a stunning {color} finish"
        
        # Sports and fitness
        elif any(word in product_lower for word in ['yoga', 'mat', 'weights', 'dumbbells', 'fitness', 'exercise']):
            descriptions = [
                f"Professional {product_name.lower()} engineered for optimal performance and durability",
                f"High-performance {product_name.lower()} designed to support your fitness goals",
                f"Premium {product_name.lower()} featuring superior construction for serious athletes"
            ]
            base_desc = random.choice(descriptions)
            if material:
                base_desc += f". Made from durable {material} for long-lasting use"
        
        # Food and consumables
        elif any(word in product_lower for word in ['coffee', 'tea', 'snack', 'protein', 'organic']):
            descriptions = [
                f"Premium {product_name.lower()} sourced from the finest ingredients for exceptional taste",
                f"Artisanal {product_name.lower()} carefully crafted to deliver superior flavor and quality",
                f"Gourmet {product_name.lower()} featuring rich, complex flavors that satisfy discerning palates"
            ]
            base_desc = random.choice(descriptions)
            if 'organic' in (material or '') or 'organic' in product_lower:
                base_desc += ". Certified organic and sustainably sourced"
        
        # Beauty and personal care
        elif any(word in product_lower for word in ['soap', 'shampoo', 'lotion', 'cream', 'skincare']):
            descriptions = [
                f"Luxurious {product_name.lower()} formulated with natural ingredients for healthy, radiant results",
                f"Premium {product_name.lower()} designed to nourish and protect with gentle, effective care",
                f"Professional-grade {product_name.lower()} featuring advanced formulation for superior performance"
            ]
            base_desc = random.choice(descriptions)
            base_desc += ". Dermatologist-tested and suitable for daily use"
        
        # Toys and games
        elif any(word in product_lower for word in ['cube', 'rubik', 'puzzle', 'game', 'toy']):
            descriptions = [
                f"Professional {product_name.lower()} engineered for smooth operation and competitive performance",
                f"High-quality {product_name.lower()} featuring precision construction and superior mechanics",
                f"Premium {product_name.lower()} designed for both beginners and advanced enthusiasts"
            ]
            base_desc = random.choice(descriptions)
            if color:
                base_desc += f" with vibrant {color} color scheme"
        
        # Books and media
        elif any(word in product_lower for word in ['book', 'novel', 'guide', 'manual']):
            descriptions = [
                f"Comprehensive {product_name.lower()} packed with valuable insights and practical knowledge",
                f"Engaging {product_name.lower()} written by experts to inform, inspire, and educate",
                f"Essential {product_name.lower()} featuring in-depth coverage and expert analysis"
            ]
            base_desc = random.choice(descriptions)
            base_desc += ". Perfect for both beginners and advanced readers"
        
        # Jewelry and accessories
        elif any(word in product_lower for word in ['necklace', 'bracelet', 'ring', 'earrings', 'jewelry']):
            descriptions = [
                f"Exquisite {product_name.lower()} handcrafted with attention to detail and timeless elegance",
                f"Stunning {product_name.lower()} featuring premium materials and sophisticated design",
                f"Beautiful {product_name.lower()} created by skilled artisans for lasting beauty"
            ]
            base_desc = random.choice(descriptions)
            if material:
                base_desc += f". Made from genuine {material} for authentic luxury"
        
        # Generic fallback for unknown products
        else:
            descriptions = [
                f"Premium {product_name.lower()} crafted with attention to detail and superior quality",
                f"High-quality {product_name.lower()} designed for performance and durability",
                f"Professional-grade {product_name.lower()} featuring excellent construction and reliability"
            ]
            base_desc = random.choice(descriptions)
            if material:
                base_desc += f". Made from quality {material}"
            if color:
                base_desc += f" in {color}"
            if size:
                base_desc += f" with {size} specifications"
        
        return base_desc
    
    def _generate_product_variations(self, base_product: str, prompt_lower: str) -> List[Dict]:
        """Generate variations of a product based on the prompt"""
        products = []
        base_product = base_product.strip()
        
        if not base_product:
            return self._generate_default_products()
        
        # Parse specifications from the prompt
        specs = self._parse_product_specifications(prompt_lower)
        
        # Generate base product
        main_product = self._create_product_variant(base_product, specs)
        products.append(main_product)
        
        # Generate logical variations (2-3 additional products)
        variations = self._generate_logical_variations(base_product, specs)
        products.extend(variations)
        
        return products[:4]  # Limit to 4 products max
    
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
            'price': round(base_price, 2),
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
        
        # Parse title changes
        if any(word in prompt_lower for word in ['title', 'name', 'call it', 'rename']):
            # Extract new title from prompt
            title_patterns = [
                r'title.*?["\']([^"\']+)["\']',
                r'name.*?["\']([^"\']+)["\']',
                r'call it\s+["\']([^"\']+)["\']',
                r'rename.*?to\s+["\']([^"\']+)["\']'
            ]
            
            for pattern in title_patterns:
                match = re.search(pattern, prompt, re.IGNORECASE)
                if match:
                    updates['title'] = match.group(1)
                    break
            
            # If no quotes found, try to extract from context
            if 'title' not in updates:
                if 'black' in prompt_lower and 'water bottle' in prompt_lower:
                    updates['title'] = 'Black Stainless Steel Water Bottle'
                elif 'stainless steel' in prompt_lower and 'bottle' in prompt_lower:
                    updates['title'] = 'Stainless Steel Water Bottle'
        
        # Parse color changes
        colors = ['black', 'white', 'silver', 'blue', 'red', 'green', 'gold', 'rose gold']
        for color in colors:
            if color in prompt_lower:
                if 'title' not in updates:
                    # Update title to include color
                    updates['title'] = f"{color.title()} {current_title}"
                updates['generate_new_image'] = True
                break
        
        # Parse size/capacity changes
        size_patterns = [
            r'(\d+)\s*oz',
            r'(\d+)\s*ounce',
            r'(\d+)\s*ml',
            r'(\d+)\s*liter'
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                size = match.group(1)
                unit = 'oz' if 'oz' in match.group(0) else ('ml' if 'ml' in match.group(0) else 'L')
                
                # Update title and description
                if 'title' not in updates:
                    updates['title'] = f"{current_title} - {size}{unit}"
                
                # Update description
                description = current_description or ""
                if size not in description:
                    description += f"\n<p><strong>Capacity:</strong> {size}{unit}</p>"
                    updates['body_html'] = description
                
                updates['generate_new_image'] = True
                break
        
        # Parse price changes
        price_patterns = [
            r'\$(\d+\.?\d*)',
            r'price.*?(\d+\.?\d*)',
            r'cost.*?(\d+\.?\d*)'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                new_price = float(match.group(1))
                updates['variants'] = [{'price': str(new_price)}]
                break
        
        # Parse description changes
        if any(word in prompt_lower for word in ['description', 'details', 'about']):
            # For now, enhance existing description
            if current_description:
                updates['body_html'] = self._enhance_product_description(current_description, prompt)
        
        # Always generate new image if significant changes
        if any(key in updates for key in ['title']) or any(color in prompt_lower for color in colors):
            updates['generate_new_image'] = True
        
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
            image_path = self.image_generator.generate_product_image(product_title)
            
            if image_path and os.path.exists(image_path):
                # Upload to Shopify
                image_url = self._upload_product_image(image_path, product_id)
                return image_url
        
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


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        quick_test()
    else:
        interactive_store_creator()
