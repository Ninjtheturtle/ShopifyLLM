from store_builder import CompleteShopifyStoreCreator

def test_product_parsing():
    """Test the product parsing logic directly"""
    creator = CompleteShopifyStoreCreator()
    
    # Test the parsing methods directly without AI
    prompt = "add some workout clothes for men and women to the store"
    
    print("Testing prompt parsing...")
    products = creator._extract_products_from_prompt(prompt)
    print(f"Direct parsing found: {len(products)} products")
    for p in products:
        print(f"  - {p}")
    
    print("\nTesting fallback parsing...")
    fallback_products = creator._generate_fallback_products_for_prompt(prompt)
    print(f"Fallback parsing found: {len(fallback_products)} products")
    for p in fallback_products:
        print(f"  - {p}")

if __name__ == "__main__":
    test_product_parsing()
