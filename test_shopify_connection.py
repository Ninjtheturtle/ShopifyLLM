import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_shopify_connection():
    shop_domain = os.getenv('SHOPIFY_SHOP_DOMAIN')
    access_token = os.getenv('SHOPIFY_ACCESS_TOKEN')
    
    print(f"Testing Shopify connection...")
    print(f"Shop domain: {shop_domain}")
    print(f"Access token: {'*' * 20 if access_token else 'MISSING'}")
    
    if not shop_domain or not access_token:
        print("❌ Missing Shopify credentials!")
        return False
    
    # Test API connection
    api_base = f"https://{shop_domain}/admin/api/2023-10"
    headers = {
        'X-Shopify-Access-Token': access_token,
        'Content-Type': 'application/json'
    }
    
    try:
        # Test 1: Get shop info
        print("\n1. Testing shop access...")
        response = requests.get(f"{api_base}/shop.json", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            shop_data = response.json()
            print(f"   ✅ Shop: {shop_data['shop']['name']}")
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
        # Test 2: List existing products
        print("\n2. Testing products access...")
        response = requests.get(f"{api_base}/products.json?limit=5", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            products_data = response.json()
            product_count = len(products_data.get('products', []))
            print(f"   ✅ Found {product_count} existing products")
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
        # Test 3: Try creating a test product
        print("\n3. Testing product creation...")
        test_product = {
            "product": {
                "title": "Test Product - DELETE ME",
                "body_html": "This is a test product created by the API test. Please delete.",
                "vendor": "API Test",
                "product_type": "Test",
                "tags": "test, api, delete",
                "variants": [{
                    "price": "1.00",
                    "sku": "TEST-001",
                    "inventory_management": "shopify",
                    "inventory_quantity": 1,
                    "weight": 100,
                    "requires_shipping": True
                }]
            }
        }
        
        response = requests.post(f"{api_base}/products.json", headers=headers, json=test_product, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            product_data = response.json()
            product_id = product_data['product']['id']
            print(f"   ✅ Created test product with ID: {product_id}")
            
            # Clean up - delete the test product
            delete_response = requests.delete(f"{api_base}/products/{product_id}.json", headers=headers, timeout=10)
            if delete_response.status_code == 200:
                print(f"   ✅ Cleaned up test product")
            else:
                print(f"   ⚠️ Failed to delete test product: {delete_response.status_code}")
                
        else:
            print(f"   ❌ Failed to create test product: {response.text}")
            return False
            
        print("\n🎉 All Shopify API tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    test_shopify_connection()
