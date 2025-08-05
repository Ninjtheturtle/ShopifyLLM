#!/usr/bin/env python3
"""Check actual Shopify product inventory levels"""

import os
import requests
from dotenv import load_dotenv

def check_product_inventory():
    """Check the actual inventory of products in Shopify"""
    
    # Load environment variables
    load_dotenv()
    
    shop_domain = os.getenv('SHOPIFY_SHOP_DOMAIN')
    access_token = os.getenv('SHOPIFY_ACCESS_TOKEN')
    
    if not shop_domain or not access_token:
        print("❌ Shopify credentials not configured. Run 'python shopify_config.py' first.")
        return
    
    headers = {
        'X-Shopify-Access-Token': access_token,
        'Content-Type': 'application/json'
    }
    
    # Get all products
    products_url = f"https://{shop_domain}/admin/api/2023-01/products.json"
    
    try:
        response = requests.get(products_url, headers=headers)
        response.raise_for_status()
        
        products = response.json().get('products', [])
        
        print(f"🛍️ Checking inventory for {len(products)} products:")
        print("=" * 60)
        
        for product in products:
            product_name = product.get('title', 'Unknown')
            created_at = product.get('created_at', '').split('T')[0] if product.get('created_at') else 'Unknown'
            
            # Get variants for this product to see inventory
            for variant in product.get('variants', []):
                inventory_quantity = variant.get('inventory_quantity', 'N/A')
                price = variant.get('price', 'N/A')
                
                print(f"📦 {product_name}")
                print(f"   💰 Price: ${price}")
                print(f"   📊 Inventory: {inventory_quantity}")
                print(f"   📅 Created: {created_at}")
                print(f"   🔗 Product ID: {product.get('id')}")
                print()
                
    except Exception as e:
        print(f"❌ Error checking inventory: {e}")

if __name__ == "__main__":
    check_product_inventory()
