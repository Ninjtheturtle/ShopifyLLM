# store_planner.py - AI-powered store planning and generation

import json
from typing import Dict, List, Any
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

class StoreDesignPlanner:
    def __init__(self, model_path: str = "./fine_tuned_model"):
        """Initialize the fine-tuned Shopify assistant"""
        self.load_model(model_path)
        
    def load_model(self, model_path: str):
        """Load the fine-tuned model"""
        model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        base_model = AutoModelForCausalLM.from_pretrained(
            model_id, 
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        self.model = PeftModel.from_pretrained(base_model, model_path)
    
    def parse_store_description(self, description: str) -> Dict[str, Any]:
        """Extract structured data from natural language store description"""
        
        # Create a detailed prompt for the LLM to analyze the description
        analysis_prompt = f"""
        Analyze this store description and extract key information:
        
        Description: "{description}"
        
        Extract the following information in JSON format:
        {{
            "store_type": "type of business (clothing, books, etc.)",
            "style_theme": "aesthetic style (minimalist, vintage, modern, etc.)",
            "color_scheme": ["primary color", "secondary color", "accent color"],
            "target_audience": "who the customers are",
            "product_categories": ["category1", "category2", "category3"],
            "brand_personality": "brand voice and personality",
            "key_features": ["special features or requirements"]
        }}
        
        JSON:
        """
        
        # Generate structured analysis
        inputs = self.tokenizer(analysis_prompt, return_tensors="pt", truncation=True, max_length=512)
        device = next(self.model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=512,
                temperature=0.3,  # Lower temperature for more structured output
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract JSON from response (would need better parsing in production)
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            return json.loads(json_str)
        except:
            # Fallback to manual parsing if JSON extraction fails
            return self._manual_parse_description(description)
    
    def _manual_parse_description(self, description: str) -> Dict[str, Any]:
        """Fallback manual parsing for when LLM JSON extraction fails"""
        # Simple keyword-based extraction as fallback
        description_lower = description.lower()
        
        # Determine store type
        store_types = {
            "clothing": ["clothing", "fashion", "apparel", "clothes"],
            "books": ["book", "library", "literature", "reading"],
            "jewelry": ["jewelry", "accessories", "rings", "necklace"],
            "home": ["home", "decor", "furniture", "interior"],
            "beauty": ["beauty", "cosmetics", "skincare", "makeup"]
        }
        
        store_type = "general"
        for stype, keywords in store_types.items():
            if any(keyword in description_lower for keyword in keywords):
                store_type = stype
                break
        
        # Determine style theme
        style_themes = {
            "minimalist": ["minimal", "clean", "simple", "modern"],
            "vintage": ["vintage", "retro", "classic", "traditional"],
            "bohemian": ["boho", "bohemian", "artistic", "eclectic"],
            "luxury": ["luxury", "premium", "high-end", "elegant"]
        }
        
        style_theme = "modern"
        for style, keywords in style_themes.items():
            if any(keyword in description_lower for keyword in keywords):
                style_theme = style
                break
        
        return {
            "store_type": store_type,
            "style_theme": style_theme,
            "color_scheme": self._get_default_colors(style_theme),
            "target_audience": "general consumers",
            "product_categories": self._get_default_categories(store_type),
            "brand_personality": "friendly and professional",
            "key_features": ["responsive design", "easy navigation"]
        }
    
    def _get_default_colors(self, style_theme: str) -> List[str]:
        """Get default color schemes for different styles"""
        color_schemes = {
            "minimalist": ["#FFFFFF", "#000000", "#F5F5F5"],
            "vintage": ["#8B4513", "#F4A460", "#DEB887"],
            "bohemian": ["#8B0000", "#DAA520", "#CD853F"],
            "luxury": ["#000000", "#FFD700", "#FFFFFF"],
            "modern": ["#2C3E50", "#3498DB", "#ECF0F1"]
        }
        return color_schemes.get(style_theme, color_schemes["modern"])
    
    def _get_default_categories(self, store_type: str) -> List[str]:
        """Get default product categories for different store types"""
        categories = {
            "clothing": ["Tops", "Bottoms", "Dresses", "Accessories"],
            "books": ["Fiction", "Non-Fiction", "Classics", "New Releases"],
            "jewelry": ["Rings", "Necklaces", "Bracelets", "Earrings"],
            "home": ["Living Room", "Bedroom", "Kitchen", "Bathroom"],
            "beauty": ["Skincare", "Makeup", "Fragrance", "Hair Care"]
        }
        return categories.get(store_type, ["Featured", "New", "Sale", "Popular"])
    
    def generate_store_plan(self, description: str) -> Dict[str, Any]:
        """Generate complete store implementation plan"""
        
        # Parse the description
        store_info = self.parse_store_description(description)
        
        # Generate comprehensive store plan
        store_plan = {
            "store_info": store_info,
            "theme_settings": self._generate_theme_settings(store_info),
            "products": self._generate_product_list(store_info),
            "collections": self._generate_collections(store_info),
            "pages": self._generate_pages(store_info),
            "navigation": self._generate_navigation(store_info)
        }
        
        return store_plan
    
    def _generate_theme_settings(self, store_info: Dict) -> Dict:
        """Generate theme configuration"""
        return {
            "colors": {
                "primary": store_info["color_scheme"][0],
                "secondary": store_info["color_scheme"][1],
                "accent": store_info["color_scheme"][2]
            },
            "typography": {
                "heading_font": "Playfair Display" if store_info["style_theme"] == "vintage" else "Roboto",
                "body_font": "Georgia" if store_info["style_theme"] == "vintage" else "Open Sans"
            },
            "layout": {
                "header_style": "centered" if store_info["style_theme"] == "minimalist" else "standard",
                "product_grid": "3-column",
                "show_vendor": True
            }
        }
    
    def _generate_product_list(self, store_info: Dict) -> List[Dict]:
        """Generate sample products based on store type"""
        # This would be expanded to generate many products
        products = []
        
        for category in store_info["product_categories"][:2]:  # Generate 2 categories for demo
            products.append({
                "title": f"Premium {category} Item",
                "description": f"High-quality {category.lower()} perfect for {store_info['target_audience']}",
                "product_type": category,
                "vendor": "Your Store",
                "tags": [store_info["style_theme"], category.lower()],
                "variants": [
                    {"title": "Default", "price": "29.99", "sku": f"{category.upper()}-001"}
                ]
            })
        
        return products
    
    def _generate_collections(self, store_info: Dict) -> List[Dict]:
        """Generate product collections"""
        collections = []
        
        for category in store_info["product_categories"]:
            collections.append({
                "title": category,
                "description": f"Our curated selection of {category.lower()} items",
                "sort_order": "best-selling"
            })
        
        # Add special collections
        collections.append({
            "title": "Featured Products",
            "description": "Our most popular items",
            "sort_order": "manual"
        })
        
        return collections
    
    def _generate_pages(self, store_info: Dict) -> List[Dict]:
        """Generate store pages"""
        return [
            {
                "title": "About Us",
                "handle": "about",
                "content": f"<h2>Welcome to our {store_info['store_type']} store!</h2><p>We specialize in {store_info['style_theme']} style products for {store_info['target_audience']}.</p>"
            },
            {
                "title": "Contact",
                "handle": "contact",
                "content": "<h2>Get in Touch</h2><p>We'd love to hear from you. Contact us with any questions!</p>"
            },
            {
                "title": "Shipping Info",
                "handle": "shipping",
                "content": "<h2>Shipping Information</h2><p>Fast, reliable shipping worldwide.</p>"
            }
        ]
    
    def _generate_navigation(self, store_info: Dict) -> Dict:
        """Generate site navigation structure"""
        return {
            "main_menu": [
                {"title": "Home", "url": "/"},
                {"title": "Shop", "url": "/collections/all"},
                *[{"title": cat, "url": f"/collections/{cat.lower().replace(' ', '-')}"} 
                  for cat in store_info["product_categories"]],
                {"title": "About", "url": "/pages/about"},
                {"title": "Contact", "url": "/pages/contact"}
            ]
        }
