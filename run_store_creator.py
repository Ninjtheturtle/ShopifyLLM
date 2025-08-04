#!/usr/bin/env python3
"""
Example: Using the AI Store Creator with Your Shopify Account
Run this after setting up your credentials with shopify_config.py
"""

from store_builder import CompleteShopifyStoreCreator
import os

def main():
    print("🛍️ AI-Powered Shopify Store Creator - Real Mode Example")
    print("=" * 60)
    print()
    
    # Method 1: Auto-load from environment variables
    print("🔧 Loading credentials from .env file...")
    creator = CompleteShopifyStoreCreator()
    
    # Method 2: Manually specify credentials (alternative)
    # creator = CompleteShopifyStoreCreator(
    #     shop_domain="your-store.myshopify.com",
    #     access_token="shpat_your_token_here",
    #     real_mode=True  # Set to True for real store creation
    # )
    
    print()
    print("🎯 Example store creation prompts:")
    print("1. 'Create a store selling handmade candles'")
    print("2. 'I want to sell vintage band t-shirts'") 
    print("3. 'Create a yoga and meditation accessories store'")
    print("4. 'Make a store for selling Rubik's cubes speedcubes'")
    print()
    
    # Interactive mode
    while True:
        prompt = input("📝 Enter your store idea (or 'quit' to exit): ").strip()
        
        if prompt.lower() in ['quit', 'exit', 'q']:
            print("👋 Thanks for using the AI Store Creator!")
            break
        
        if not prompt:
            continue
        
        try:
            print()
            result = creator.create_store_from_prompt(prompt)
            
            if result.get('success', True):
                print(f"\n🎉 SUCCESS! Store creation result:")
                if result.get('mode') == 'demo':
                    print("📝 This was a demo. To create real stores:")
                    print("   1. Set up your Shopify credentials: python shopify_config.py")
                    print("   2. Set STORE_CREATION_MODE=real in your .env file")
                    print("   3. Run this script again")
                else:
                    print(f"🌐 Store URL: {result.get('store_url', 'N/A')}")
                    print(f"⚙️ Admin Panel: {result.get('admin_url', 'N/A')}")
                    print(f"📦 Products Created: {result.get('products_created', 0)}")
            else:
                print(f"❌ Store creation failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "─" * 50)

if __name__ == "__main__":
    main()
