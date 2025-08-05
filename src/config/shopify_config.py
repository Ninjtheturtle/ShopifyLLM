#!/usr/bin/env python3
"""
Shopify API Configuration Helper
Run this script to set up your Shopify credentials safely
"""

import os
from pathlib import Path

def setup_shopify_credentials():
    """Interactive setup for Shopify API credentials"""
    print("🔧 Shopify API Configuration Setup")
    print("=" * 50)
    print()
    
    # Check if .env already exists
    env_file = Path('.env')
    if env_file.exists():
        print("⚠️  .env file already exists!")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    print("Please enter your Shopify credentials:")
    print("(You can find these in your Shopify development store)")
    print()
    
    # Get store domain
    print("📍 Store Domain:")
    print("Example: my-test-store.myshopify.com")
    shop_domain = input("Enter your store domain: ").strip()
    
    # Validate domain format
    if not shop_domain.endswith('.myshopify.com'):
        if '.' not in shop_domain:
            shop_domain = f"{shop_domain}.myshopify.com"
        else:
            print("⚠️  Domain should end with .myshopify.com")
            return
    
    print()
    
    # Get access token
    print("🔑 Access Token:")
    print("Example: shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    access_token = input("Enter your Admin API access token: ").strip()
    
    # Validate token format
    if not access_token.startswith('shpat_'):
        print("⚠️  Access token should start with 'shpat_'")
        return
    
    print()
    
    # Write to .env file
    env_content = f"""# Shopify API Configuration
SHOPIFY_SHOP_DOMAIN={shop_domain}
SHOPIFY_ACCESS_TOKEN={access_token}

# Optional: Set to 'real' when ready for live stores
STORE_CREATION_MODE=demo
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ Configuration saved to .env file!")
        print()
        print("🔒 Security Notes:")
        print("- Your .env file contains sensitive credentials")
        print("- Never commit this file to version control")
        print("- The .gitignore file should exclude .env")
        print()
        print("🧪 Test your setup:")
        print("python test_shopify_connection.py")
        
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")

def show_setup_instructions():
    """Display step-by-step setup instructions"""
    print("📋 How to Get Your Shopify Credentials:")
    print("=" * 50)
    print()
    print("1. Create Development Store:")
    print("   • Go to https://partners.shopify.com/")
    print("   • Create partner account (free)")
    print("   • Click 'Stores' → 'Add store' → 'Development store'")
    print()
    print("2. Create Private App:")
    print("   • Go to your dev store admin panel")
    print("   • Navigate to 'Apps' → 'Develop apps'")
    print("   • Click 'Create an app'")
    print("   • Name: 'AI Store Generator'")
    print()
    print("3. Set API Permissions:")
    print("   • Click 'Configure Admin API scopes'")
    print("   • Enable these scopes:")
    print("     - write_products")
    print("     - write_inventory") 
    print("     - write_content")
    print("     - write_themes")
    print("     - write_orders")
    print("     - write_customers")
    print()
    print("4. Install & Get Token:")
    print("   • Click 'Install app'")
    print("   • Copy 'Admin API access token'")
    print("   • Note your store domain")
    print()
    print("5. Run This Setup:")
    print("   python shopify_config.py")
    print()

if __name__ == "__main__":
    print("🛍️ Shopify API Setup Helper")
    print()
    choice = input("Choose an option:\n1. Show setup instructions\n2. Configure credentials\n\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        show_setup_instructions()
    elif choice == "2":
        setup_shopify_credentials()
    else:
        print("Invalid choice. Please run again and select 1 or 2.")
