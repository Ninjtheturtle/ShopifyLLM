# Shopify API Setup Guide

## Prerequisites
pip install requests pillow

## Shopify App Setup Instructions

### Step 1: Create a Shopify Development Store
1. Go to https://partners.shopify.com/
2. Create a partner account if you don't have one
3. Click "Stores" → "Add store" → "Development store"
4. Fill in store details and create the store

### Step 2: Create a Private App
1. Go to your development store admin
2. Navigate to "Apps" → "Develop apps"
3. Click "Create an app"
4. Name your app (e.g., "AI Store Generator")
5. Click "Configure Admin API scopes"

### Step 3: Set Required Permissions
Enable the following scopes:
- `write_products` - Create and modify products
- `write_product_listings` - Manage product listings
- `write_inventory` - Manage inventory
- `write_content` - Create blog posts and pages
- `write_themes` - Customize theme settings
- `write_script_tags` - Add custom scripts
- `write_shipping` - Configure shipping
- `write_orders` - Access order data
- `write_customers` - Manage customers
- `write_draft_orders` - Create draft orders

### Step 4: Install and Get Access Token
1. Click "Install app"
2. Copy the "Admin API access token"
3. Save your store domain (e.g., "your-store.myshopify.com")

### Step 5: Configure the Store Builder
```python
from store_builder import CompleteShopifyStoreCreator

# Replace with your actual credentials
SHOP_DOMAIN = "your-store.myshopify.com"
ACCESS_TOKEN = "shpat_xxxxxxxxxxxxxxxxxxxxx"

creator = CompleteShopifyStoreCreator(SHOP_DOMAIN, ACCESS_TOKEN)
result = creator.create_store_from_prompt("Create a store for selling handmade candles")
```

## Environment Variables (Recommended)
Create a `.env` file:
```
SHOPIFY_SHOP_DOMAIN=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_xxxxxxxxxxxxxxxxxxxxx
```

Then use:
```python
import os
from dotenv import load_dotenv

load_dotenv()
creator = CompleteShopifyStoreCreator(
    os.getenv('SHOPIFY_SHOP_DOMAIN'),
    os.getenv('SHOPIFY_ACCESS_TOKEN')
)
```

## Rate Limits
- Shopify REST Admin API: 2 requests per second
- The script includes automatic rate limiting delays
- For high-volume operations, consider Shopify Plus

## Security Notes
- Never commit access tokens to version control
- Use environment variables or secure vaults
- Rotate tokens regularly
- Use the principle of least privilege for scopes
