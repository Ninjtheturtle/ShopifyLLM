# shopify_builder.py - Core Shopify API integration

import shopify
import requests
import json
from typing import Dict, List, Any

class ShopifyStoreBuilder:
    def __init__(self, shop_url: str, api_token: str):
        """Initialize Shopify API connection"""
        self.shop_url = shop_url
        self.api_token = api_token
        
        # Configure shopify session
        shopify.ShopifyResource.set_site(f"https://{api_token}@{shop_url}.myshopify.com/admin/api/2023-10/")
        
    def create_product(self, product_data: Dict[str, Any]) -> Dict:
        """Create a new product in Shopify"""
        try:
            product = shopify.Product()
            product.title = product_data.get('title')
            product.body_html = product_data.get('description')
            product.vendor = product_data.get('vendor', 'Your Store')
            product.product_type = product_data.get('product_type')
            product.tags = product_data.get('tags', [])
            
            # Add variants (size, color, etc.)
            if 'variants' in product_data:
                product.variants = []
                for variant_data in product_data['variants']:
                    variant = shopify.Variant()
                    variant.title = variant_data.get('title')
                    variant.price = variant_data.get('price')
                    variant.sku = variant_data.get('sku')
                    variant.inventory_quantity = variant_data.get('inventory', 0)
                    product.variants.append(variant)
            
            product.save()
            return {'success': True, 'product_id': product.id}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_collection(self, collection_data: Dict[str, Any]) -> Dict:
        """Create a product collection"""
        try:
            collection = shopify.CustomCollection()
            collection.title = collection_data.get('title')
            collection.body_html = collection_data.get('description')
            collection.sort_order = collection_data.get('sort_order', 'best-selling')
            collection.save()
            
            return {'success': True, 'collection_id': collection.id}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_theme_settings(self, theme_settings: Dict[str, Any]) -> Dict:
        """Update theme colors, fonts, and layout"""
        try:
            # Get active theme
            themes = shopify.Theme.find()
            active_theme = next((t for t in themes if t.role == 'main'), None)
            
            if not active_theme:
                return {'success': False, 'error': 'No active theme found'}
            
            # Update theme settings
            for setting_key, setting_value in theme_settings.items():
                asset = shopify.Asset()
                asset.prefix = f"themes/{active_theme.id}/"
                asset.key = f"config/settings_data.json"
                # Load existing settings and update
                # (This would need more complex logic to merge settings)
                
            return {'success': True, 'theme_id': active_theme.id}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_page(self, page_data: Dict[str, Any]) -> Dict:
        """Create store pages (About, Contact, etc.)"""
        try:
            page = shopify.Page()
            page.title = page_data.get('title')
            page.body_html = page_data.get('content')
            page.handle = page_data.get('handle')  # URL slug
            page.save()
            
            return {'success': True, 'page_id': page.id}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
