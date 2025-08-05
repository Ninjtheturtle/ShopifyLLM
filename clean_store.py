#!/usr/bin/env python3
"""
Clean up duplicate and invalid products from the Shopify store
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def clean_store_products():
    """Remove duplicate and invalid products from the store"""
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
            print(f"🛍️ Found {len(products)} products in store")
            print("🧹 Cleaning up duplicate and invalid products...")
            print("=" * 60)
            
            # Identify products to remove
            to_remove = []
            invalid_keywords = ['blog post', 'blog', 'landing page', 'template', 'pricing', 
                              'gallery', 'testing', 'speed testing', 'guide', 'tutorial']
            
            seen_names = set()
            
            for product in products:
                title = product.get('title', '').lower()
                product_id = product.get('id')
                
                # Check if it's an invalid product type
                is_invalid = any(keyword in title for keyword in invalid_keywords)
                
                # Check if it's a duplicate
                is_duplicate = title in seen_names
                
                if is_invalid:
                    print(f"❌ Invalid product: {product.get('title')} (ID: {product_id})")
                    to_remove.append(product_id)
                elif is_duplicate:
                    print(f"🔄 Duplicate product: {product.get('title')} (ID: {product_id})")
                    to_remove.append(product_id)
                else:
                    seen_names.add(title)
                    print(f"✅ Keeping: {product.get('title')}")
            
            print(f"\n🗑️ Removing {len(to_remove)} invalid/duplicate products...")
            
            # Remove identified products
            for product_id in to_remove:
                try:
                    delete_response = requests.delete(
                        f"{api_base}/products/{product_id}.json",
                        headers=headers
                    )
                    
                    if delete_response.status_code == 200:
                        print(f"   ✅ Deleted product ID: {product_id}")
                    else:
                        print(f"   ❌ Failed to delete product ID: {product_id}")
                        
                except Exception as e:
                    print(f"   ❌ Error deleting product {product_id}: {e}")
            
            print(f"\n🎉 Cleanup complete! Removed {len(to_remove)} products")
            
        else:
            print(f"❌ Error getting products: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    clean_store_products()
