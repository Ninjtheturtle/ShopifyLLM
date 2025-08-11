from store_builder import CompleteShopifyStoreCreator

# Test the description generation specifically
creator = CompleteShopifyStoreCreator()

product_name = "Workout Clothes"
print(f"Testing description generation for: '{product_name}'")

# Test the full method with improved caching and parsing
full_description = creator._generate_product_specific_description(product_name)
print(f"Full Method Result: '{full_description}'")

# Test another product to see consistency
product_name2 = "Running Shoes"
print(f"\nTesting description generation for: '{product_name2}'")
full_description2 = creator._generate_product_specific_description(product_name2)
print(f"Full Method Result: '{full_description2}'")
