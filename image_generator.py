#!/usr/bin/env python3
"""
Product Image Generator - Creates realistic product images for Shopify products
"""

import requests
import base64
import io
import os
import time
import re
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Optional
import random

class ProductImageGenerator:
    """Generate realistic product images for Shopify products"""
    
    def __init__(self):
        self.image_cache = {}
        
    def generate_product_image(self, product_name: str, category: str = "general") -> Optional[bytes]:
        """Generate a realistic product image based on product name and category"""
        print(f"🎨 Generating image for: {product_name}")
        
        try:
            # Priority 1: Try multiple real image sources
            image_bytes = self._fetch_real_product_image(product_name)
            
            if image_bytes:
                print(f"   ✅ Found real product image for {product_name}")
                return image_bytes
            
            # Priority 2: Try AI image generation services
            image_bytes = self._generate_ai_image(product_name)
            
            if image_bytes:
                print(f"   🤖 Generated AI image for {product_name}")
                return image_bytes
            
            # Priority 3: Create a minimalist product representation (not cartoon)
            print(f"   📐 Creating minimalist product representation for {product_name}")
            image_bytes = self._create_minimalist_product_image(product_name)
            
            if image_bytes:
                print(f"   ✅ Generated minimalist image for {product_name}")
                return image_bytes
            else:
                print(f"   ❌ Failed to generate image for {product_name}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error generating image for {product_name}: {e}")
            return None
    
    def _fetch_real_product_image(self, product_name: str) -> Optional[bytes]:
        """Try to fetch a real product image from multiple free sources"""
        try:
            search_terms = self._get_search_terms(product_name)
            
            # Try multiple image sources for better success rate
            image_sources = [
                self._fetch_from_unsplash,
                self._fetch_from_pexels,
                self._fetch_from_pixabay
            ]
            
            for term in search_terms:
                for source_func in image_sources:
                    try:
                        image_bytes = source_func(term)
                        if image_bytes and len(image_bytes) > 5000:
                            # Enhance the fetched image
                            return self._enhance_fetched_image(image_bytes, product_name)
                    except Exception as e:
                        print(f"   ⚠️ Failed to fetch from source for {term}: {str(e)[:50]}")
                        continue
            
            return None
            
        except Exception as e:
            print(f"   ⚠️ Could not fetch real image: {e}")
            return None
    
    def _fetch_from_unsplash(self, search_term: str) -> Optional[bytes]:
        """Fetch from Unsplash Source API"""
        unsplash_url = f"https://source.unsplash.com/800x800/?{search_term},product,white+background"
        
        response = requests.get(unsplash_url, timeout=15, 
                              headers={'User-Agent': 'Shopify-Product-Generator/1.0'})
        
        if response.status_code == 200:
            return response.content
        return None
    
    def _fetch_from_pexels(self, search_term: str) -> Optional[bytes]:
        """Fetch from Pexels (using their free API)"""
        try:
            # Using Pexels API v1 (free tier)
            pexels_url = f"https://www.pexels.com/photo/download/{search_term.replace('+', '-')}"
            
            response = requests.get(pexels_url, timeout=15,
                                  headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
            
            if response.status_code == 200 and 'image' in response.headers.get('content-type', ''):
                return response.content
        except:
            pass
        return None
    
    def _fetch_from_pixabay(self, search_term: str) -> Optional[bytes]:
        """Fetch from Pixabay free images"""
        try:
            # Use Pixabay's direct image URLs (no API key needed for some)
            pixabay_url = f"https://pixabay.com/get/g{random.randint(1000000, 9999999)}-{search_term.replace('+', '_')}.jpg"
            
            response = requests.get(pixabay_url, timeout=10,
                                  headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
            
            if response.status_code == 200 and len(response.content) > 5000:
                return response.content
        except:
            pass
        return None
    
    def _generate_ai_image(self, product_name: str) -> Optional[bytes]:
        """Generate realistic product image using AI services"""
        try:
            # Try free AI image generation services
            ai_services = [
                self._generate_with_pollinations,
                self._generate_with_craiyon
            ]
            
            for service_func in ai_services:
                try:
                    image_bytes = service_func(product_name)
                    if image_bytes and len(image_bytes) > 5000:
                        return self._enhance_fetched_image(image_bytes, product_name)
                except Exception as e:
                    print(f"   ⚠️ AI service failed: {str(e)[:50]}")
                    continue
            
            return None
            
        except Exception as e:
            print(f"   ⚠️ AI image generation failed: {e}")
            return None
    
    def _generate_with_pollinations(self, product_name: str) -> Optional[bytes]:
        """Generate image using Pollinations AI (free service)"""
        try:
            # Create a detailed prompt for realistic product photography
            prompt = f"professional product photography of {product_name}, white background, studio lighting, high quality, commercial photography, detailed, realistic"
            prompt_encoded = requests.utils.quote(prompt)
            
            pollinations_url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=800&height=800&nologo=true"
            
            response = requests.get(pollinations_url, timeout=20,
                                  headers={'User-Agent': 'Shopify-Product-Generator/1.0'})
            
            if response.status_code == 200 and 'image' in response.headers.get('content-type', ''):
                return response.content
                
        except Exception as e:
            print(f"   ⚠️ Pollinations failed: {e}")
        
        return None
    
    def _generate_with_craiyon(self, product_name: str) -> Optional[bytes]:
        """Generate image using Craiyon (formerly DALL-E mini)"""
        try:
            # Note: This would require their API integration
            # For now, return None to fall back to other methods
            return None
            
        except Exception:
            return None
    
    def _create_minimalist_product_image(self, product_name: str) -> bytes:
        """Create a clean, minimalist product representation (not cartoon)"""
        
        width, height = 800, 800
        
        # Create clean white background
        img = Image.new('RGB', (width, height), '#ffffff')
        draw = ImageDraw.Draw(img)
        
        # Detect product category
        category = self._detect_category(product_name)
        
        # Create minimalist product representation
        self._draw_minimalist_product(draw, width, height, category, product_name)
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG', quality=95)
        img_byte_arr.seek(0)
        
        return img_byte_arr.getvalue()
    
    def _draw_minimalist_product(self, draw, width, height, category, product_name):
        """Draw clean, minimalist product representations"""
        center_x, center_y = width // 2, height // 2
        
        if 'bottle' in product_name.lower():
            self._draw_minimalist_bottle(draw, center_x, center_y, product_name)
        elif 'headphone' in product_name.lower():
            self._draw_minimalist_headphones(draw, center_x, center_y)
        elif 'shirt' in product_name.lower() or 'cotton' in product_name.lower():
            self._draw_minimalist_shirt(draw, center_x, center_y)
        elif 'lamp' in product_name.lower():
            self._draw_minimalist_lamp(draw, center_x, center_y)
        else:
            self._draw_minimalist_generic(draw, center_x, center_y, product_name)
    
    def _draw_minimalist_bottle(self, draw, cx, cy, product_name):
        """Draw clean, realistic water bottle"""
        # Determine size from product name
        size_match = re.search(r'(\d+)\s*oz', product_name.lower())
        if size_match:
            oz = int(size_match.group(1))
            # Scale bottle height based on size
            bottle_height = min(300, 150 + (oz * 4))
            bottle_width = min(80, 40 + (oz * 1))
        else:
            bottle_height = 200
            bottle_width = 60
        
        # Bottle body - clean stainless steel look
        draw.rectangle([cx-bottle_width//2, cy-bottle_height//2, cx+bottle_width//2, cy+bottle_height//2], 
                      fill='#e8eaed', outline='#bdc1c6', width=2)
        
        # Cap
        cap_height = bottle_height // 6
        draw.rectangle([cx-bottle_width//3, cy-bottle_height//2-cap_height, cx+bottle_width//3, cy-bottle_height//2], 
                      fill='#4285f4', outline='#1a73e8', width=2)
        
        # Subtle branding area
        label_height = bottle_height // 4
        draw.rectangle([cx-bottle_width//3, cy-label_height//2, cx+bottle_width//3, cy+label_height//2], 
                      outline='#9aa0a6', width=1)
        
        # Size text
        if size_match:
            font = self._get_font(24)
            text = f"{oz}oz"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            draw.text((cx - text_width//2, cy + bottle_height//2 + 20), text, fill='#5f6368', font=font)
    
    def _draw_minimalist_headphones(self, draw, cx, cy):
        """Draw clean, minimal headphones"""
        # Headband
        draw.arc([cx-80, cy-100, cx+80, cy+20], start=0, end=180, fill='#34495e', width=8)
        
        # Ear cups - clean circles
        draw.ellipse([cx-90, cy-30, cx-40, cy+30], fill='#2c3e50', outline='#1a252f', width=2)
        draw.ellipse([cx+40, cy-30, cx+90, cy+30], fill='#2c3e50', outline='#1a252f', width=2)
        
        # Inner speakers - minimal
        draw.ellipse([cx-75, cy-15, cx-55, cy+15], fill='#1a1a1a')
        draw.ellipse([cx+55, cy-15, cx+75, cy+15], fill='#1a1a1a')
    
    def _draw_minimalist_shirt(self, draw, cx, cy):
        """Draw clean t-shirt silhouette"""
        # T-shirt body - simple outline
        draw.rectangle([cx-50, cy-30, cx+50, cy+70], outline='#4285f4', width=3, fill='#f8f9fa')
        
        # Sleeves
        draw.rectangle([cx-70, cy-30, cx-50, cy+10], outline='#4285f4', width=2, fill='#f8f9fa')
        draw.rectangle([cx+50, cy-30, cx+70, cy+10], outline='#4285f4', width=2, fill='#f8f9fa')
        
        # Neckline
        draw.arc([cx-15, cy-40, cx+15, cy-10], start=0, end=180, outline='#4285f4', width=2)
    
    def _draw_minimalist_lamp(self, draw, cx, cy):
        """Draw clean desk lamp"""
        # Base
        draw.ellipse([cx-30, cy+50, cx+30, cy+80], fill='#5f6368', outline='#3c4043')
        
        # Stem
        draw.rectangle([cx-3, cy-10, cx+3, cy+50], fill='#5f6368')
        
        # Lampshade - clean cone
        draw.polygon([(cx-40, cy-40), (cx+40, cy-40), (cx+25, cy-10), (cx-25, cy-10)], 
                    fill='#ffffff', outline='#9aa0a6', width=2)
    
    def _draw_minimalist_generic(self, draw, cx, cy, product_name):
        """Draw clean generic product box"""
        # Clean product box
        draw.rectangle([cx-60, cy-60, cx+60, cy+60], fill='#f8f9fa', outline='#9aa0a6', width=2)
        
        # Product indicator
        draw.ellipse([cx-15, cy-15, cx+15, cy+15], fill='#4285f4')
    
    def _get_search_terms(self, product_name: str) -> list:
        """Extract optimized search terms for better image matching"""
        name_lower = product_name.lower()
        
        # Extract size information for water bottles
        if 'bottle' in name_lower:
            size_match = re.search(r'(\d+)\s*oz', name_lower)
            if size_match:
                size = size_match.group(1)
                return [f'{size}oz+water+bottle', 'stainless+steel+water+bottle', 'insulated+bottle', 'water+bottle+product']
        
        # Comprehensive search term mapping
        term_mapping = {
            'headphones': ['headphones+product', 'wireless+headphones+white+background', 'bluetooth+headphones+studio', 'audio+equipment+product'],
            'bluetooth': ['bluetooth+headphones+product', 'wireless+speaker+white', 'bluetooth+device+studio'],
            'wireless': ['wireless+headphones+product', 'wireless+speaker+studio', 'wireless+device+white+background'],
            'bottle': ['water+bottle+product', 'steel+bottle+white+background', 'insulated+bottle+studio', 'drinking+bottle+product'],
            'water': ['water+bottle+product', 'hydration+bottle+white', 'sports+bottle+studio'],
            'shirt': ['t-shirt+product', 'cotton+shirt+white+background', 'mens+shirt+studio', 'clothing+product'],
            'cotton': ['cotton+shirt+product', 'organic+cotton+white', 'cotton+clothing+studio'],
            'lamp': ['desk+lamp+product', 'led+lamp+white+background', 'table+lamp+studio', 'office+lighting+product'],
            'led': ['led+lamp+product', 'led+light+white+background', 'desk+lamp+studio', 'modern+lighting+product']
        }
        
        search_terms = []
        
        # Find matching terms
        for key, terms in term_mapping.items():
            if key in name_lower:
                search_terms.extend(terms)
                break  # Use first match to avoid too many terms
        
        # If no specific terms found, create from product name
        if not search_terms:
            clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', product_name)
            words = [w for w in clean_name.split() if len(w) > 2][:3]
            if words:
                main_term = '+'.join(words)
                search_terms = [f'{main_term}+product+white+background', f'{words[0]}+product+studio', f'{main_term}+commercial+photography']
        
        return search_terms[:3]  # Limit to 3 best attempts
    
    def _enhance_fetched_image(self, image_data: bytes, product_name: str) -> bytes:
        """Enhance fetched image to look professional"""
        try:
            img = Image.open(io.BytesIO(image_data))
            
            # Resize to standard dimensions
            img = img.resize((800, 800), Image.Resampling.LANCZOS)
            
            # Ensure RGB mode
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Create professional white background
            background = Image.new('RGB', (800, 800), '#ffffff')
            
            # Paste the product image onto white background
            background.paste(img, (0, 0))
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            background.save(img_byte_arr, format='PNG', quality=95)
            img_byte_arr.seek(0)
            
            return img_byte_arr.getvalue()
            
        except Exception as e:
            print(f"   ⚠️ Could not enhance image: {e}")
            return image_data

    def _get_font(self, size):
        """Get font or default"""
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            return ImageFont.load_default()
    
    def _detect_category(self, product_name: str) -> str:
        """Detect product category from name"""
        name_lower = product_name.lower()
        
        categories = {
            'electronics': ['headphone', 'bluetooth', 'wireless', 'speaker', 'led', 'lamp'],
            'fitness': ['dumbbell', 'weight', 'resistance', 'foam', 'roller', 'exercise', 'gym'],
            'home': ['lamp', 'desk', 'bottle', 'water', 'home'],
            'clothing': ['shirt', 'cotton', 'fabric', 'clothing', 'organic'],
            'cards': ['card', 'playing', 'deck', 'poker', 'bicycle'],
            'candle': ['candle', 'scented', 'vanilla', 'lavender'],
            'yoga': ['yoga', 'meditation', 'mat', 'cushion'],
            'jewelry': ['necklace', 'bracelet', 'ring', 'earring', 'jewelry', 'silver', 'gold']
        }
        
        for category, keywords in categories.items():
            if any(keyword in name_lower for keyword in keywords):
                return category
        
        return 'general'
    
    def upload_image_to_shopify(self, image_bytes: bytes, filename: str, product_id: str, 
                               shop_domain: str, access_token: str) -> bool:
        """Upload generated image to Shopify product"""
        try:
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            api_url = f"https://{shop_domain}/admin/api/2023-10/products/{product_id}/images.json"
            headers = {
                'X-Shopify-Access-Token': access_token,
                'Content-Type': 'application/json'
            }
            
            payload = {
                "image": {
                    "attachment": image_b64,
                    "filename": filename,
                    "alt": f"Product image for {filename.replace('.png', '').replace('_', ' ')}"
                }
            }
            
            response = requests.post(api_url, json=payload, headers=headers)
            
            if response.status_code in [200, 201]:
                print(f"   🖼️ Image uploaded successfully for product {product_id}")
                return True
            else:
                print(f"   ❌ Failed to upload image: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error uploading image: {e}")
            return False
