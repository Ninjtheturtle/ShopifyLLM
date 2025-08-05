#!/usr/bin/env python3
"""
Quick script to check what products are in the Shopify store
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_store_products():
    """Check what products exist in the store"""
    shop_domain = os.getenv('SHOPIFY_SHOP_DOMAIN')
    access_token = os.getenv('SHOPIFY_ACCESS_TOKEN')
    
    if not shop_domain or not access_token:
        print("❌ Missing credentials in .env file")
        return
    
    api_base = f"https://{shop_domain}/admin/api/2023-10"
    headers = {
        'X-Shopify-Access-Token': access_token,
        'Content-Type': 'application/json'
    }
    
    try:
        # Get all products
        response = requests.get(f"{api_base}/products.json", headers=headers)
        
        if response.status_code == 200:
            products = response.json().get('products', [])
            print(f"🛍️ Found {len(products)} products in your store:")
            print("=" * 60)
            
            for i, product in enumerate(products, 1):
                title = product.get('title', 'No Title')
                price = 'No Price'
                if product.get('variants') and len(product['variants']) > 0:
                    price = f"${product['variants'][0].get('price', 'N/A')}"
                
                created = product.get('created_at', '')[:10]  # Just date
                
                print(f"{i}. {title}")
                print(f"   💰 Price: {price}")
                print(f"   📅 Created: {created}")
                print(f"   🔗 Product ID: {product.get('id')}")
                print()
                
        else:
            print(f"❌ Error getting products: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_store_products()
