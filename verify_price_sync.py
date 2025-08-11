#!/usr/bin/env python3
"""
Verify that dashboard prices match Shopify store prices
"""

import requests
import json
from store_builder import CompleteShopifyStoreCreator

def test_price_consistency():
    """Test that dashboard API returns the same prices as direct Shopify API"""
    
    print("🔍 Testing price consistency between dashboard and Shopify store...")
    print("=" * 60)
    
    # Test 1: Get prices from dashboard API
    try:
        dashboard_response = requests.get('http://127.0.0.1:5000/api/products')
        dashboard_data = dashboard_response.json()
        
        if not dashboard_data.get('success'):
            print("❌ Dashboard API failed")
            return
        
        dashboard_products = dashboard_data.get('products', [])
        print(f"📊 Dashboard returned {len(dashboard_products)} products")
        
    except Exception as e:
        print(f"❌ Error accessing dashboard: {e}")
        return
    
    # Test 2: Get prices directly from Shopify
    try:
        creator = CompleteShopifyStoreCreator()
        shopify_products = creator._get_all_products()
        print(f"🏪 Shopify returned {len(shopify_products)} products")
        
    except Exception as e:
        print(f"❌ Error accessing Shopify: {e}")
        return
    
    # Test 3: Compare prices
    print("\n🔍 Price Comparison:")
    print("-" * 60)
    
    # Create lookup for dashboard products by title
    dashboard_lookup = {p.get('title', ''): p for p in dashboard_products}
    
    all_match = True
    for shopify_product in shopify_products:
        title = shopify_product.get('title', '')
        shopify_price = shopify_product.get('variants', [{}])[0].get('price', '0')
        
        dashboard_product = dashboard_lookup.get(title)
        if dashboard_product:
            dashboard_price = dashboard_product.get('variants', [{}])[0].get('price', '0')
            
            match = shopify_price == dashboard_price
            status = "✅" if match else "❌"
            
            print(f"{status} {title}")
            print(f"   Shopify: ${shopify_price}")
            print(f"   Dashboard: ${dashboard_price}")
            
            if not match:
                all_match = False
            print()
        else:
            print(f"⚠️ {title} not found in dashboard")
            all_match = False
    
    print("=" * 60)
    if all_match:
        print("🎉 SUCCESS: All prices match between dashboard and Shopify store!")
    else:
        print("❌ FAILURE: Price discrepancies found")
    
    return all_match

if __name__ == "__main__":
    test_price_consistency()
