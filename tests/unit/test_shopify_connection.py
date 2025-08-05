#!/usr/bin/env python3
"""
Test Shopify API Connection
Verifies that your credentials work and you can connect to Shopify
"""

import os
import requests
from dotenv import load_dotenv
import json

def test_shopify_connection():
    """Test the Shopify API connection"""
    print("🧪 Testing Shopify API Connection")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    shop_domain = os.getenv('SHOPIFY_SHOP_DOMAIN')
    access_token = os.getenv('SHOPIFY_ACCESS_TOKEN')
    
    if not shop_domain or not access_token:
        print("❌ Missing credentials!")
        print("Please run: python shopify_config.py")
        return False
    
    print(f"🏪 Store: {shop_domain}")
    print(f"🔑 Token: {access_token[:10]}...")
    print()
    
    # Test API connection
    headers = {
        'X-Shopify-Access-Token': access_token,
        'Content-Type': 'application/json'
    }
    
    try:
        # Test 1: Get shop info
        print("📋 Test 1: Getting shop information...")
        url = f"https://{shop_domain}/admin/api/2023-10/shop.json"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            shop_data = response.json()['shop']
            print(f"   ✅ Connected to: {shop_data['name']}")
            print(f"   📧 Email: {shop_data['email']}")
            print(f"   🌍 Domain: {shop_data['domain']}")
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
            return False
        
        print()
        
        # Test 2: List products (should be empty for new store)
        print("📦 Test 2: Checking products access...")
        url = f"https://{shop_domain}/admin/api/2023-10/products.json?limit=5"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            products = response.json()['products']
            print(f"   ✅ Products API working - Found {len(products)} products")
        else:
            print(f"   ❌ Products access failed: {response.status_code}")
            return False
        
        print()
        
        # Test 3: Check theme access
        print("🎨 Test 3: Checking themes access...")
        url = f"https://{shop_domain}/admin/api/2023-10/themes.json"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            themes = response.json()['themes']
            active_theme = next((t for t in themes if t['role'] == 'main'), None)
            print(f"   ✅ Themes API working - Active theme: {active_theme['name'] if active_theme else 'None'}")
        else:
            print(f"   ❌ Themes access failed: {response.status_code}")
            return False
        
        print()
        print("🎉 All tests passed! Your Shopify API is ready.")
        print()
        print("🚀 Next steps:")
        print("1. Run the store creator: python store_builder.py")
        print("2. Try creating a test store with AI")
        print("3. Set STORE_CREATION_MODE=real in .env when ready for live stores")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def show_troubleshooting():
    """Show common troubleshooting tips"""
    print("🔧 Troubleshooting Tips:")
    print("=" * 30)
    print()
    print("Common Issues:")
    print("1. 401 Unauthorized:")
    print("   - Check your access token is correct")
    print("   - Ensure token starts with 'shpat_'")
    print()
    print("2. 403 Forbidden:")
    print("   - Check API scopes are enabled")
    print("   - Ensure app is installed on store")
    print()
    print("3. 404 Not Found:")
    print("   - Check store domain is correct")
    print("   - Ensure domain ends with '.myshopify.com'")
    print()
    print("4. Rate Limiting:")
    print("   - Wait a moment and try again")
    print("   - API has 2 requests per second limit")

if __name__ == "__main__":
    if not test_shopify_connection():
        print()
        show_troubleshooting()
