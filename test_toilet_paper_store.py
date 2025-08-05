#!/usr/bin/env python3
"""
Test toilet paper store creation
"""

from store_builder import CompleteShopifyStoreCreator

def main():
    print("🧪 Testing Toilet Paper Store Creation")
    print("=" * 40)
    
    creator = CompleteShopifyStoreCreator()
    prompt = "create a store that sells toilet paper"
    
    print(f"📝 Testing prompt: {prompt}")
    print()
    
    try:
        result = creator.create_store_from_prompt(prompt)
        
        if result.get('success', True):
            print(f"🎉 SUCCESS! Store creation result:")
            print(f"📦 Products Created: {result.get('products_created', 0)}")
            
            # Show product details if available
            if 'products' in result:
                print("\n📋 Products created:")
                for i, product in enumerate(result['products'], 1):
                    print(f"  {i}. {product.get('name', 'N/A')}")
                    print(f"     Price: ${product.get('price', 'N/A')}")
                    print(f"     Inventory: {product.get('inventory', 'N/A')}")
                    print(f"     SKU: {product.get('sku', 'N/A')}")
                    print()
        else:
            print(f"❌ Store creation failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
