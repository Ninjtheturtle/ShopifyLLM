from store_builder import CompleteShopifyStoreCreator

print("🧪 Testing Full Store Creation with Fixed Logic")
print("=" * 50)

creator = CompleteShopifyStoreCreator()
prompt = "create a store that sells workout clothes"

print(f"✅ Prompt: '{prompt}'")

# Test the product extraction
products = creator._extract_products_from_prompt(prompt)
print(f"\n📦 Extracted Products: {len(products)}")
for i, p in enumerate(products, 1):
    print(f"{i}. Name: '{p['name']}'")
    print(f"   Price: ${p['price']}")
    print(f"   Description: {p['description'][:100]}...")
    print()

# Test generating a fresh description with the fixed method
if products:
    product_name = products[0]['name']
    print(f"🔄 Generating fresh description for: '{product_name}'")
    new_description = creator._generate_product_specific_description(product_name)
    print(f"   Fresh Description: {new_description[:150]}...")
