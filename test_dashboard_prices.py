#!/usr/bin/env python3

import requests
import json

def test_dashboard_prices():
    """Test the prices returned by the dashboard API"""
    try:
        # Test the dashboard API
        response = requests.get('http://127.0.0.1:5000/api/products')
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            return
            
        data = response.json()
        products = data.get('products', [])
        
        print(f"📊 Dashboard API Response: {len(products)} products found")
        print("=" * 60)
        
        for product in products:
            title = product.get('title', 'No title')
            variants = product.get('variants', [])
            
            if variants and len(variants) > 0:
                price = variants[0].get('price', 'No price')
                print(f"💰 {title}: ${price}")
            else:
                print(f"⚠️  {title}: No variants found")
                
        # Also check if enhanced_price is available
        print("\n🔍 Enhanced prices (if available):")
        for product in products:
            title = product.get('title', 'No title')
            enhanced_price = product.get('enhanced_price')
            if enhanced_price:
                print(f"🎯 {title}: Enhanced ${enhanced_price}")
                
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")

if __name__ == "__main__":
    test_dashboard_prices()
