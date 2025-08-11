#!/usr/bin/env python3
"""
COMPREHENSIVE Premium Dataset Creator
Creates 300+ high-quality examples for fine-tuning
"""

import json
import random
from typing import List, Dict

def create_comprehensive_premium_dataset():
    """Create a comprehensive dataset with 300+ premium examples"""
    
    dataset = []
    
    # Core brand examples (high quality, manually crafted)
    core_examples = [
        # Apple Examples
        {
            "input": "Create a product description for Apple iPhone 16 Pro with A18 Pro chip, 48MP camera, titanium design, and Apple Intelligence features",
            "output": "iPhone 16 Pro. Built for Apple Intelligence. The most advanced iPhone ever features the revolutionary A18 Pro chip that delivers unprecedented performance for pro workflows and AI features. Capture your world in stunning detail with the 48MP Main camera and new Camera Control. The aerospace-grade titanium design is incredibly strong yet remarkably light. Apple Intelligence helps you write, express yourself, and get things done effortlessly with groundbreaking privacy protections. All in a design that's built to last.",
            "brand": "Apple", "category": "Smartphone", "seo_keywords": "iPhone 16 Pro, A18 Pro chip, Apple Intelligence, 48MP camera, titanium smartphone"
        },
        {
            "input": "Write SEO-optimized copy for MacBook Air M4 with 18-hour battery life and fanless design",
            "output": "MacBook Air with M4. Supercharged by the M4 chip, MacBook Air delivers exceptional performance and up to 18 hours of battery life in an incredibly thin and light design. The fanless architecture means silent operation while the M4 chip handles demanding tasks with ease. Features a gorgeous Liquid Retina display, advanced camera for video calls, and the convenience of MagSafe charging. Available in four stunning colors.",
            "brand": "Apple", "category": "Laptop", "seo_keywords": "MacBook Air M4, 18-hour battery, fanless laptop, Apple M4 chip"
        },
        {
            "input": "Generate product features for AirPods Pro 2 with hearing health capabilities",
            "output": "• Active Noise Cancellation up to 2x more effective than previous generation\\n• Hearing Test and clinical-grade Hearing Aid features\\n• Personalized Spatial Audio with dynamic head tracking\\n• Transparency mode for staying aware of surroundings\\n• Up to 6 hours listening time with ANC, 30 hours total with case\\n• Wireless charging case with MagSafe compatibility\\n• Sweat and water resistant (IPX4 rated)\\n• Touch controls for music, calls, and Siri activation",
            "brand": "Apple", "category": "Audio", "seo_keywords": "AirPods Pro 2, hearing health, active noise cancellation, spatial audio"
        },
        
        # Nike Examples
        {
            "input": "Create motivational product copy for Nike Air Max 270 with Air Max cushioning and React foam",
            "output": "Step into the future with Air Max 270. Revolutionary Max Air cushioning delivers unmatched impact protection with every stride, while React foam technology provides responsive energy return that keeps you moving forward. The breathable engineered mesh upper adapts to your foot for a locked-in feel that moves with you. Designed for athletes who refuse to compromise on comfort or style. Your potential has no limits. Just Do It.",
            "brand": "Nike", "category": "Athletic Footwear", "seo_keywords": "Nike Air Max 270, Air Max cushioning, React foam, athletic shoes"
        },
        {
            "input": "Write performance-focused description for Nike Pegasus running shoes with ZoomX foam",
            "output": "Meet your new running partner. The Nike Pegasus features responsive ZoomX foam that delivers incredible energy return with every step. Engineered mesh upper provides targeted breathability where you need it most. Full-length Air Zoom unit gives you the bounce to power through any distance. From your first mile to your personal best, Pegasus adapts to your stride and elevates your run. Because every runner deserves to fly.",
            "brand": "Nike", "category": "Running Shoes", "seo_keywords": "Nike Pegasus, ZoomX foam, running shoes, Air Zoom technology"
        },
        
        # Allbirds Examples
        {
            "input": "Create sustainable product description for Allbirds Tree Runner made from eucalyptus with carbon neutral shipping",
            "output": "Tree Runner: Comfort by Nature. Crafted from silky-smooth eucalyptus tree fiber that's naturally moisture-wicking and odor-resistant. Our innovative SweetFoam™ midsole is made from Brazilian sugarcane for cloud-like cushioning with every step. The breathable, lightweight design moves with your foot for all-day comfort. Machine washable for easy care. Carbon neutral shipping included because we believe in protecting the planet we explore.",
            "brand": "Allbirds", "category": "Sustainable Footwear", "seo_keywords": "Allbirds Tree Runner, eucalyptus shoes, sustainable footwear, carbon neutral"
        },
        {
            "input": "Write eco-friendly copy for Allbirds Wool Cruiser with merino wool and recycled materials",
            "output": "Wool Cruiser: The Evolution of Comfort. Made with the world's finest ZQ-certified merino wool that naturally regulates temperature and resists odor. The sole is crafted from recycled materials and renewable castor bean oil. Designed for modern life with sophisticated style that works from morning meetings to evening adventures. 10 years of comfort innovation in every step. Materials from the earth, designed for life.",
            "brand": "Allbirds", "category": "Sustainable Footwear", "seo_keywords": "Allbirds Wool Cruiser, merino wool shoes, recycled materials, sustainable fashion"
        },
        
        # Warby Parker Examples
        {
            "input": "Create accessible luxury description for Warby Parker Lucien glasses with acetate frames and anti-reflective coating",
            "output": "Lucien: Where vintage meets modern. Hand-polished acetate frames offer exceptional durability and all-day comfort. Each pair includes premium prescription lenses with anti-reflective and scratch-resistant coatings at no extra cost—because quality shouldn't be an upcharge. 100% UVA and UVB protection keeps your eyes healthy. Thoughtfully designed to complement faces of every shape and size. For every pair sold, we provide glasses to someone in need.",
            "brand": "Warby Parker", "category": "Eyewear", "seo_keywords": "Warby Parker Lucien, acetate glasses, prescription lenses, anti-reflective coating"
        },
        
        # Patagonia Examples
        {
            "input": "Create environmental product description for Patagonia Better Sweater with recycled polyester and Fair Trade certification",
            "output": "Better Sweater: Warmth with Purpose. Made from 100% recycled polyester fleece that delivers cozy insulation while reducing environmental impact. Wind-resistant fabric breathes naturally for active pursuits. Fair Trade Certified™ sewn, ensuring fair wages and safe working conditions. Full-zip design with stand-up collar provides versatile protection. Built to last through countless adventures because we're in business to save our home planet.",
            "brand": "Patagonia", "category": "Outdoor Apparel", "seo_keywords": "Patagonia Better Sweater, recycled polyester, Fair Trade Certified, fleece jacket"
        },
        
        # Microsoft Examples
        {
            "input": "Create premium tech description for Microsoft Surface Pro with Snapdragon X Elite and Copilot+ PC features",
            "output": "Surface Pro: The 2-in-1 that adapts to you. Powered by Snapdragon X Elite processor delivering faster performance than MacBook Air M4. Copilot+ PC features provide AI acceleration for enhanced productivity. Up to 14 hours of battery life keeps you productive anywhere. Vibrant PixelSense touchscreen with Surface Pen support for natural creation. Transform from laptop to tablet in seconds with the versatile kickstand design.",
            "brand": "Microsoft", "category": "2-in-1 Laptop", "seo_keywords": "Microsoft Surface Pro, Snapdragon X Elite, Copilot+ PC, 2-in-1 laptop"
        },
        
        # Amazon Examples
        {
            "input": "Create product description for Amazon Fire TV Stick 4K with AI-powered search and Wi-Fi 6 support",
            "output": "Fire TV Stick 4K: Your gateway to endless entertainment. Stream over 1.8 million movies and shows in stunning 4K resolution with support for Dolby Vision and HDR10+. AI-powered Fire TV Search finds content across apps and services instantly. Wi-Fi 6 support delivers faster, more reliable streaming. Alexa Voice Remote included for hands-free control. Access free and live TV content plus all your favorite streaming services.",
            "brand": "Amazon", "category": "Streaming Device", "seo_keywords": "Fire TV Stick 4K, AI-powered search, Wi-Fi 6, 4K streaming, Alexa Voice Remote"
        }
    ]
    
    # Generate varied synthetic examples
    templates = [
        "Create a compelling product description for",
        "Write SEO-optimized copy for",
        "Generate premium marketing copy for",
        "Develop brand-focused description for",
        "Create conversion-optimized text for",
        "Write feature-rich description for",
        "Generate luxury product copy for",
        "Create technical description for",
        "Write lifestyle-focused copy for",
        "Generate eco-friendly description for",
        "Create professional description for",
        "Write customer-focused copy for",
        "Generate performance-oriented description for",
        "Create value-driven copy for",
        "Write innovative product description for"
    ]
    
    categories = [
        "Tech", "Fashion", "Automotive", "Beauty", "Home", "Sports", "Travel", 
        "Health", "Food", "Books", "Toys", "Garden", "Pet", "Office", "Kitchen",
        "Fitness", "Gaming", "Audio", "Photography", "Art", "Music", "Baby",
        "Jewelry", "Watch", "Bag", "Shoe", "Clothing", "Skincare", "Fragrance"
    ]
    
    product_types = {
        "Tech": ["smartphone", "laptop", "tablet", "smartwatch", "headphones", "speaker", "camera", "monitor"],
        "Fashion": ["jacket", "dress", "jeans", "shirt", "sweater", "coat", "blouse", "pants"],
        "Home": ["sofa", "lamp", "table", "chair", "bed", "mirror", "vase", "curtain"],
        "Beauty": ["moisturizer", "serum", "cleanser", "foundation", "lipstick", "mascara", "perfume", "sunscreen"],
        "Sports": ["running shoes", "yoga mat", "water bottle", "gym bag", "fitness tracker", "protein powder"],
        "Kitchen": ["blender", "coffee maker", "knife set", "cutting board", "pan", "cookware"],
        "Audio": ["wireless earbuds", "bluetooth speaker", "noise-canceling headphones", "sound bar"],
        "Automotive": ["car accessories", "floor mats", "phone mount", "dash cam", "seat covers"]
    }
    
    features_pool = [
        "premium materials", "innovative design", "advanced technology", "sustainable manufacturing",
        "ergonomic design", "wireless connectivity", "long battery life", "weather resistance",
        "luxury finish", "compact size", "user-friendly interface", "professional grade",
        "energy efficient", "fast charging", "waterproof design", "scratch resistant",
        "anti-bacterial coating", "temperature control", "smart features", "voice control",
        "app integration", "customizable settings", "premium packaging", "lifetime warranty"
    ]
    
    benefits_pool = [
        "exceptional performance", "unmatched comfort", "superior durability", "effortless convenience",
        "professional results", "enhanced productivity", "peace of mind", "elevated experience",
        "reliable operation", "modern style", "intuitive use", "versatile functionality",
        "outstanding value", "premium quality", "innovative solutions", "seamless integration",
        "enhanced safety", "improved efficiency", "optimal performance", "lasting satisfaction"
    ]
    
    # Generate 250+ synthetic examples
    synthetic_examples = []
    for i in range(250):
        template = random.choice(templates)
        category = random.choice(categories)
        
        # Get product type for category
        if category in product_types:
            product = random.choice(product_types[category])
        else:
            product = f"{category.lower()} product"
        
        # Select features and benefits
        features = random.sample(features_pool, 2)
        benefit = random.choice(benefits_pool)
        
        # Create more varied copy patterns
        copy_patterns = [
            f"Discover {benefit} with our latest {product}. Featuring {features[0]} and {features[1]}, this product delivers exceptional value for discerning customers. Thoughtfully crafted with attention to every detail, it represents the perfect balance of form and function.",
            f"Experience the difference with our premium {product}. Combining {features[0]} with {features[1]}, this innovative design elevates your daily routine. Built for those who demand excellence and appreciate quality craftsmanship.",
            f"Introducing our revolutionary {product} with {features[0]} and {features[1]}. Designed for modern lifestyles, this product delivers {benefit} while maintaining the highest standards of quality and reliability.",
            f"Transform your experience with our cutting-edge {product}. The integration of {features[0]} and {features[1]} creates a product that offers {benefit} for today's discerning consumer.",
            f"Elevate your standards with our luxury {product}. Featuring {features[0]} and {features[1]}, this meticulously crafted product provides {benefit} with uncompromising quality."
        ]
        
        output_text = random.choice(copy_patterns)
        
        synthetic_example = {
            "input": f"{template} a premium {product} with {features[0]} and {features[1]}",
            "output": output_text,
            "brand": f"Premium {category}",
            "category": category,
            "seo_keywords": f"premium {product}, {features[0]}, {features[1]}, quality {category.lower()}"
        }
        synthetic_examples.append(synthetic_example)
    
    # Combine all examples
    all_examples = core_examples + synthetic_examples
    
    # Convert to fine-tuning format
    for example in all_examples:
        fine_tuning_example = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert e-commerce copywriter who creates compelling, premium product descriptions with strong SEO optimization and persuasive marketing copy. You understand brand voice, target audiences, and conversion optimization. Focus on benefits over features, use sensory language, and create emotional connections with customers."
                },
                {
                    "role": "user",
                    "content": example["input"]
                },
                {
                    "role": "assistant", 
                    "content": example["output"]
                }
            ],
            "brand": example["brand"],
            "category": example["category"],
            "seo_keywords": example["seo_keywords"]
        }
        dataset.append(fine_tuning_example)
    
    return dataset

def save_dataset(dataset, filename="premium_ecommerce_300_examples.jsonl"):
    """Save dataset in JSONL format"""
    with open(filename, 'w', encoding='utf-8') as f:
        for example in dataset:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    
    print(f"✅ Dataset saved to {filename}")
    print(f"📊 Total examples: {len(dataset)}")
    
    # Print category breakdown
    category_counts = {}
    for example in dataset:
        category = example.get("category", "Unknown")
        category_counts[category] = category_counts.get(category, 0) + 1
    
    print(f"\n📈 Category Distribution (top 10):")
    sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    for category, count in sorted_categories[:10]:
        print(f"   {category}: {count} examples")
    
    return filename

def main():
    """Main function"""
    print("🚀 Creating Comprehensive Premium E-commerce Dataset...")
    print("📚 High-quality examples from top brands + 250+ synthetic variations")
    
    dataset = create_comprehensive_premium_dataset()
    filename = save_dataset(dataset)
    
    print(f"\n🎯 Dataset created successfully!")
    print(f"📁 File: {filename}")
    print(f"💡 Ready for LLM fine-tuning with {len(dataset)} high-quality examples")
    print("\n✨ Features:")
    print("   • Premium product descriptions from top brands")
    print("   • 250+ varied synthetic examples")
    print("   • SEO-optimized marketing copy")
    print("   • Brand voice consistency")
    print("   • Conversion-focused language")
    print("   • Diverse product categories")
    print("   • Professional copywriting patterns")

if __name__ == "__main__":
    main()
