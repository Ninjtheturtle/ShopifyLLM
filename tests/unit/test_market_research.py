#!/usr/bin/env python3
"""
Test the market research system with different product types
"""

from market_research import MarketResearcher

def test_market_research():
    """Test market research for different product categories"""
    researcher = MarketResearcher()
    
    print("🔬 Testing Market Research System")
    print("=" * 50)
    
    # Test different product types
    test_products = [
        {"name": "Speed Cube 3x3", "price": 35.00, "description": "Basic cube"},
        {"name": "Vanilla Soy Candle", "price": 25.00, "description": "Basic candle"},
        {"name": "Premium Yoga Mat", "price": 70.00, "description": "Basic mat"},
        {"name": "Cube Timer Pro", "price": 30.00, "description": "Basic timer"},
        {"name": "Lavender Dream Candle", "price": 28.00, "description": "Basic lavender candle"}
    ]
    
    for product in test_products:
        print(f"\n🔍 Researching: {product['name']}")
        print(f"   Original: ${product['price']:.2f} - {product['description']}")
        
        enhanced = researcher.enhance_product_with_research(product)
        
        print(f"   Enhanced: ${enhanced['price']:.2f}")
        print(f"   Description: {enhanced['description'][:100]}...")
        
        if enhanced.get('key_features'):
            print(f"   Features: {', '.join(enhanced['key_features'][:3])}")
        
        if enhanced.get('market_research', {}).get('research_notes'):
            print(f"   Market Notes: {enhanced['market_research']['research_notes']}")
        
        print("-" * 40)

if __name__ == "__main__":
    test_market_research()
