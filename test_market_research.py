from market_research import MarketResearcher

researcher = MarketResearcher()

# Test the improved product features
product = {
    'name': 'Workout Clothes',
    'price': 30.00,
    'description': 'Basic workout clothes'
}

print("Testing improved market research...")
enhanced = researcher.enhance_product_with_research(product)

print(f"Product: {enhanced['name']}")
print(f"Price: ${enhanced['price']:.2f}")
print(f"Description: {enhanced['description']}")
print(f"Key Features:")
for feature in enhanced['key_features']:
    print(f"  - {feature}")
