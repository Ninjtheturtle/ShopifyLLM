from store_builder import CompleteShopifyStoreCreator

creator = CompleteShopifyStoreCreator()

prompt = "create a store that sells workout clothes"
print(f"Testing prompt: '{prompt}'")

products = creator._extract_products_from_prompt(prompt)
print(f"\nExtracted {len(products)} products:")
for p in products:
    print(f"- Name: '{p['name']}'")
    print(f"- Price: ${p['price']}")
    print(f"- Description: {p['description'][:80]}...")
    print()
