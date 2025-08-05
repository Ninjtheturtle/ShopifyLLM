#!/usr/bin/env python3
"""
Test toilet paper pricing
"""

from market_research import MarketResearcher

def main():
    print("🧪 Testing Toilet Paper Pricing")
    print("=" * 40)
    
    researcher = MarketResearcher()
    
    # Test different toilet paper product names
    test_products = [
        "Commercial Grade Toilet Paper",
        "Eco-Friendly Toilet Paper", 
        "Premium Quilted Toilet Paper",
        "Ultra-Soft Toilet Paper"
    ]
    
    for product_name in test_products:
        print(f"\n📝 Testing: {product_name}")
        research = researcher.research_product(product_name)
        
        print(f"   💰 Suggested Price: ${research['suggested_price']:.2f}")
        print(f"   🏷️ Category: {research.get('category', 'N/A')}")
        print(f"   📊 Price Range: ${research['price_range'][0]}-${research['price_range'][1]}")
        
        # Test enhance function
        test_product = {
            'name': product_name,
            'price': 15.99,
            'description': 'Basic toilet paper'
        }
        
        enhanced = researcher.enhance_product_with_research(test_product)
        print(f"   🔄 Enhanced Price: ${enhanced['price']:.2f}")

if __name__ == "__main__":
    main()
