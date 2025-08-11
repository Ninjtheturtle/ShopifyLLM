from store_builder import CompleteShopifyStoreCreator

def test_full_store_creation():
    """Test the complete store creation process"""
    creator = CompleteShopifyStoreCreator(real_mode=True)
    
    prompt = "add some workout clothes for men and women to the store"
    print(f"Testing full store creation with prompt: '{prompt}'")
    
    try:
        result = creator.create_store_from_prompt(prompt)
        print("\nStore creation result:")
        print(f"Success: {result.get('success')}")
        print(f"Products created: {result.get('products_created', 0)}")
        print(f"Mode: {result.get('mode')}")
        
        if result.get('error'):
            print(f"Error: {result.get('error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Store creation failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_full_store_creation()
