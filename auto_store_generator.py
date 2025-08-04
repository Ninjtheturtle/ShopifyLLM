# auto_store_generator.py - Main orchestrator for automatic store creation

import torch
from store_planner import StoreDesignPlanner
from shopify_builder import ShopifyStoreBuilder
import json
import time
from typing import Dict, Any

class AutomaticStoreGenerator:
    def __init__(self, shopify_shop_url: str, shopify_api_token: str):
        """Initialize the automatic store generator"""
        self.store_planner = StoreDesignPlanner()
        self.shopify_builder = ShopifyStoreBuilder(shopify_shop_url, shopify_api_token)
        
    def generate_store_from_description(self, description: str, 
                                      deploy_to_shopify: bool = False) -> Dict[str, Any]:
        """
        Main function: Generate complete store from natural language description
        
        Args:
            description: Natural language description of desired store
            deploy_to_shopify: Whether to actually create the store on Shopify
            
        Returns:
            Dictionary with store plan and deployment results
        """
        
        print(f"🤖 Analyzing store description: '{description}'")
        
        # Step 1: Generate store plan using AI
        store_plan = self.store_planner.generate_store_plan(description)
        
        print("✅ Store plan generated!")
        print(f"📊 Store Type: {store_plan['store_info']['store_type']}")
        print(f"🎨 Style Theme: {store_plan['store_info']['style_theme']}")
        print(f"🎯 Target Audience: {store_plan['store_info']['target_audience']}")
        
        results = {
            "store_plan": store_plan,
            "deployment_results": {}
        }
        
        if deploy_to_shopify:
            print("\n🚀 Deploying to Shopify...")
            results["deployment_results"] = self._deploy_to_shopify(store_plan)
        else:
            print("\n💾 Store plan generated (deployment skipped)")
            self._save_store_plan(store_plan)
        
        return results
    
    def _deploy_to_shopify(self, store_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy the generated store plan to Shopify"""
        deployment_results = {
            "collections": [],
            "products": [],
            "pages": [],
            "theme_updates": {},
            "errors": []
        }
        
        try:
            # Step 1: Create Collections
            print("📁 Creating collections...")
            for collection_data in store_plan["collections"]:
                result = self.shopify_builder.create_collection(collection_data)
                deployment_results["collections"].append(result)
                if result["success"]:
                    print(f"  ✅ Created collection: {collection_data['title']}")
                else:
                    print(f"  ❌ Failed to create collection: {result['error']}")
                time.sleep(1)  # Rate limiting
            
            # Step 2: Create Products
            print("🛍️ Creating products...")
            for product_data in store_plan["products"]:
                result = self.shopify_builder.create_product(product_data)
                deployment_results["products"].append(result)
                if result["success"]:
                    print(f"  ✅ Created product: {product_data['title']}")
                else:
                    print(f"  ❌ Failed to create product: {result['error']}")
                time.sleep(1)  # Rate limiting
            
            # Step 3: Create Pages
            print("📄 Creating pages...")
            for page_data in store_plan["pages"]:
                result = self.shopify_builder.create_page(page_data)
                deployment_results["pages"].append(result)
                if result["success"]:
                    print(f"  ✅ Created page: {page_data['title']}")
                else:
                    print(f"  ❌ Failed to create page: {result['error']}")
                time.sleep(1)  # Rate limiting
            
            # Step 4: Update Theme Settings
            print("🎨 Updating theme settings...")
            theme_result = self.shopify_builder.update_theme_settings(store_plan["theme_settings"])
            deployment_results["theme_updates"] = theme_result
            if theme_result["success"]:
                print("  ✅ Theme settings updated")
            else:
                print(f"  ❌ Failed to update theme: {theme_result['error']}")
            
            print("\n🎉 Store deployment completed!")
            
        except Exception as e:
            error_msg = f"Deployment failed: {str(e)}"
            deployment_results["errors"].append(error_msg)
            print(f"❌ {error_msg}")
        
        return deployment_results
    
    def _save_store_plan(self, store_plan: Dict[str, Any]):
        """Save the generated store plan to a file"""
        filename = f"store_plan_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(store_plan, f, indent=2)
        print(f"💾 Store plan saved to: {filename}")
    
    def preview_store_plan(self, description: str) -> Dict[str, Any]:
        """Generate and preview store plan without deploying"""
        return self.generate_store_from_description(description, deploy_to_shopify=False)
    
    def deploy_existing_plan(self, plan_file: str) -> Dict[str, Any]:
        """Deploy a previously generated store plan"""
        with open(plan_file, 'r') as f:
            store_plan = json.load(f)
        
        print(f"📁 Loading store plan from: {plan_file}")
        
        results = {
            "store_plan": store_plan,
            "deployment_results": self._deploy_to_shopify(store_plan)
        }
        
        return results

# Example usage and testing
def main():
    """Example usage of the automatic store generator"""
    
    # Example store descriptions
    example_descriptions = [
        "I want a minimalist jewelry store with rose gold accents, targeting young professionals",
        "Create a vintage bookstore with dark academia vibes, selling rare books and literary accessories",
        "Build a sustainable clothing brand with earthy tones, focusing on eco-friendly materials",
        "Design a luxury skincare store with clean white aesthetics and premium beauty products"
    ]
    
    # Initialize generator (you'd need real Shopify credentials)
    generator = AutomaticStoreGenerator(
        shopify_shop_url="your-shop-name",  # Replace with real shop
        shopify_api_token="your-api-token"   # Replace with real token
    )
    
    # Test with preview mode (no actual deployment)
    for description in example_descriptions:
        print("=" * 80)
        results = generator.preview_store_plan(description)
        print("\n")

if __name__ == "__main__":
    main()
