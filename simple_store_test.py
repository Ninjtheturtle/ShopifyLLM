#!/usr/bin/env python3
"""
Simple store creation test without AI model to verify basic functionality
"""

import json
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

def test_simple_store_creation():
    """Test store creation with manual products instead of AI"""
    
    print("🧪 Testing Simple Store Creation (No AI)")
    print("="*50)
    
    # Get Shopify configuration from environment
    shop_domain = os.getenv('SHOPIFY_SHOP_DOMAIN', 'finetunedtest.myshopify.com')
    access_token = os.getenv('SHOPIFY_ACCESS_TOKEN')
    
    if not access_token:
        print("❌ No Shopify access token found in environment")
        return False
    
    # Set up API configuration
    api_base = f"https://{shop_domain}/admin/api/2023-10"
    headers = {
        'X-Shopify-Access-Token': access_token,
        'Content-Type': 'application/json'
    }
    
    print(f"🔧 Configured for: {shop_domain}")
    print("🎭 Mode: Real Store Creation")
    
    # Create manual product data instead of using AI
    manual_products = [
        {
            'title': 'Premium Workout T-Shirt',
            'price': 29.99,
            'description': 'Moisture-wicking athletic shirt designed for high-intensity workouts. Features four-way stretch fabric and breathable mesh panels for maximum comfort.',
            'features': [
                'Moisture-wicking fabric',
                'Four-way stretch',
                'Breathable mesh panels',
                'Quick-dry technology',
                'Flatlock seams',
                'UPF 30+ sun protection'
            ]
        },
        {
            'title': 'Athletic Leggings',
            'price': 45.99,
            'description': 'High-performance leggings with compression fit and side pockets. Perfect for yoga, running, or weightlifting.',
            'features': [
                'Compression fit',
                'Side pockets',
                'High waistband',
                'Squat-proof fabric',
                'Moisture-wicking',
                'Four-way stretch'
            ]
        },
        {
            'title': 'Training Shorts',
            'price': 24.99,
            'description': 'Lightweight training shorts with built-in compression liner. Ideal for running and cross-training.',
            'features': [
                'Built-in compression liner',
                'Lightweight fabric',
                'Quick-dry material',
                'Elastic waistband',
                'Reflective details',
                'Multiple pockets'
            ]
        }
    ]
    
    print(f"📦 Manual Products Created: {len(manual_products)}")
    for i, product in enumerate(manual_products, 1):
        print(f"{i}. {product['title']} - ${product['price']}")
    
    # Test Shopify connection
    try:
        print("\n🔗 Testing Shopify connection...")
        response = requests.get(f"{api_base}/shop.json", headers=headers)
        if response.status_code == 200:
            shop_data = response.json()['shop']
            print(f"✅ Connected to: {shop_data['name']}")
        else:
            print(f"❌ Connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    # Create products in Shopify
    print("\n🏪 Creating products in Shopify...")
    created_products = []
    
    for product_data in manual_products:
        try:
            print(f"📝 Creating: {product_data['title']}")
            
            # Prepare Shopify product data
            shopify_product = {
                "product": {
                    "title": product_data['title'],
                    "body_html": f"<p>{product_data['description']}</p><ul>{''.join([f'<li>{feature}</li>' for feature in product_data['features']])}</ul>",
                    "vendor": "FitGear Pro",
                    "product_type": "Athletic Wear",
                    "variants": [
                        {
                            "price": str(product_data['price']),
                            "inventory_quantity": 100,
                            "inventory_management": "shopify"
                        }
                    ],
                    "tags": "workout, athletic, fitness, activewear"
                }
            }
            
            # Create product via API
            response = requests.post(f"{api_base}/products.json", json=shopify_product, headers=headers)
            
            if response.status_code == 201:
                product_result = response.json()['product']
                created_products.append(product_result)
                print(f"✅ Created: {product_result['title']} (ID: {product_result['id']})")
            else:
                print(f"❌ Failed to create {product_data['title']}: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error creating {product_data['title']}: {e}")
    
    print(f"\n🎉 Store Creation Complete!")
    print(f"📊 Products Created: {len(created_products)}")
    print(f"🔗 Store URL: https://{shop_domain}")
    
    return len(created_products) > 0

if __name__ == "__main__":
    success = test_simple_store_creation()
    print(f"\n🏁 Test {'PASSED' if success else 'FAILED'}")
