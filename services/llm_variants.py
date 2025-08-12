# LLM Variants Generation Service
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from models import db, Experiment, Variant

logger = logging.getLogger(__name__)

class LLMVariantGenerator:
    """Generate and manage LLM-based content variants for A/B testing"""
    
    def __init__(self, model_path: str = "premium_shopify_v3"):
        self.model_path = model_path
        self.variant_types = [
            'product_description',
            'product_title', 
            'collection_description',
            'marketing_copy',
            'email_subject',
            'cta_button',
            'pricing_display'
        ]
        
    def generate_description_variants(self, product_data: Dict, num_variants: int = 3) -> List[Dict]:
        """Generate multiple product description variants using different approaches"""
        try:
            variants = []
            
            # Base product information
            product_name = product_data.get('title', 'Product')
            category = product_data.get('category', 'general')
            price = product_data.get('price', 0)
            features = product_data.get('features', [])
            
            # Variant 1: Feature-focused (Control)
            control_variant = self._generate_feature_focused_description(
                product_name, category, price, features
            )
            variants.append({
                'variant_type': 'control',
                'name': 'Feature-Focused Description',
                'content': control_variant,
                'approach': 'feature_focused',
                'config': {
                    'focus': 'features',
                    'tone': 'informative',
                    'length': 'medium'
                }
            })
            
            # Variant 2: Benefit-focused
            if num_variants >= 2:
                benefit_variant = self._generate_benefit_focused_description(
                    product_name, category, price, features
                )
                variants.append({
                    'variant_type': 'treatment',
                    'name': 'Benefit-Focused Description', 
                    'content': benefit_variant,
                    'approach': 'benefit_focused',
                    'config': {
                        'focus': 'benefits',
                        'tone': 'persuasive',
                        'length': 'medium'
                    }
                })
            
            # Variant 3: Emotional/Story-driven
            if num_variants >= 3:
                emotional_variant = self._generate_emotional_description(
                    product_name, category, price, features
                )
                variants.append({
                    'variant_type': 'treatment',
                    'name': 'Emotional Story Description',
                    'content': emotional_variant,
                    'approach': 'emotional_story',
                    'config': {
                        'focus': 'emotion',
                        'tone': 'engaging',
                        'length': 'long'
                    }
                })
            
            # Variant 4: Concise/Minimal
            if num_variants >= 4:
                minimal_variant = self._generate_minimal_description(
                    product_name, category, price, features
                )
                variants.append({
                    'variant_type': 'treatment',
                    'name': 'Minimal Description',
                    'content': minimal_variant,
                    'approach': 'minimal',
                    'config': {
                        'focus': 'essential',
                        'tone': 'direct',
                        'length': 'short'
                    }
                })
            
            return variants[:num_variants]
            
        except Exception as e:
            logger.error(f"Error generating description variants: {str(e)}")
            raise
    
    def _generate_feature_focused_description(self, name: str, category: str, price: float, features: List[str]) -> str:
        """Generate feature-focused product description"""
        feature_list = ""
        if features:
            feature_list = "\n\nKey Features:\n" + "\n".join(f"• {feature}" for feature in features[:5])
        
        descriptions = {
            'electronics': f"The {name} delivers exceptional performance with cutting-edge technology. "
                          f"Engineered for reliability and designed for the modern user.{feature_list}",
            
            'clothing': f"Elevate your style with the {name}. Crafted from premium materials with "
                       f"attention to detail in every stitch.{feature_list}",
            
            'home_garden': f"Transform your space with the {name}. Combining functionality with "
                          f"elegant design for the discerning homeowner.{feature_list}",
            
            'sports_outdoors': f"Gear up for adventure with the {name}. Built for performance and "
                              f"engineered to withstand the elements.{feature_list}",
            
            'health_beauty': f"Discover the difference with {name}. Formulated with care using "
                            f"quality ingredients for optimal results.{feature_list}"
        }
        
        return descriptions.get(category, 
            f"Experience excellence with the {name}. Designed with precision and built to last.{feature_list}")
    
    def _generate_benefit_focused_description(self, name: str, category: str, price: float, features: List[str]) -> str:
        """Generate benefit-focused product description"""
        benefit_mappings = {
            'electronics': f"Stay connected and productive with the {name}. Save time with faster performance "
                          f"and enjoy peace of mind with reliable technology that works when you need it most.",
            
            'clothing': f"Look confident and feel comfortable in the {name}. Stand out from the crowd while "
                       f"enjoying all-day comfort that keeps up with your busy lifestyle.",
            
            'home_garden': f"Create the perfect sanctuary with the {name}. Enjoy more relaxation time in a "
                          f"beautiful space that reflects your personal style and brings daily joy.",
            
            'sports_outdoors': f"Achieve your fitness goals with the {name}. Push your limits safely while "
                              f"staying comfortable and confident in any condition.",
            
            'health_beauty': f"Reveal your natural radiance with {name}. Feel confident in your skin while "
                            f"enjoying the convenience of effective, gentle care."
        }
        
        return benefit_mappings.get(category,
            f"Enhance your daily experience with the {name}. Designed to make your life easier, "
            f"more comfortable, and more enjoyable.")
    
    def _generate_emotional_description(self, name: str, category: str, price: float, features: List[str]) -> str:
        """Generate emotional/story-driven product description"""
        emotional_stories = {
            'electronics': f"Imagine never missing that important video call again. The {name} transforms "
                          f"ordinary moments into extraordinary experiences. Whether you're connecting with "
                          f"loved ones or presenting to colleagues, this isn't just technology – it's your "
                          f"gateway to meaningful connections.",
            
            'clothing': f"Picture yourself walking into any room with complete confidence. The {name} isn't "
                       f"just clothing – it's your armor for conquering the day. From morning meetings to "
                       f"evening adventures, feel the difference that comes from wearing something truly special.",
            
            'home_garden': f"Close your eyes and imagine your perfect retreat. The {name} turns that vision "
                          f"into reality, creating a space where memories are made and stress melts away. "
                          f"This is more than decor – it's the foundation of your sanctuary.",
            
            'sports_outdoors': f"Feel the rush of achievement as you cross that finish line. The {name} has "
                              f"been with you every step of the journey, through early morning training and "
                              f"challenging weather. This isn't just gear – it's your partner in greatness.",
            
            'health_beauty': f"Discover the confidence that comes from feeling truly beautiful. The {name} "
                            f"awakens your natural glow, revealing the radiant person you've always been. "
                            f"This isn't just skincare – it's self-care that transforms how you see yourself."
        }
        
        return emotional_stories.get(category,
            f"Discover how the {name} transforms everyday moments into something special. This isn't just "
            f"a product – it's your partner in creating the life you've always imagined.")
    
    def _generate_minimal_description(self, name: str, category: str, price: float, features: List[str]) -> str:
        """Generate concise, minimal product description"""
        key_feature = features[0] if features else "premium quality"
        
        minimal_descriptions = {
            'electronics': f"{name}. {key_feature.title()}. Reliable performance.",
            'clothing': f"{name}. Premium materials. Exceptional fit.",
            'home_garden': f"{name}. Elegant design. Functional beauty.", 
            'sports_outdoors': f"{name}. Built tough. Peak performance.",
            'health_beauty': f"{name}. Natural ingredients. Visible results."
        }
        
        return minimal_descriptions.get(category, f"{name}. {key_feature.title()}. Quality guaranteed.")
    
    def generate_title_variants(self, product_data: Dict, num_variants: int = 3) -> List[Dict]:
        """Generate product title variants with different approaches"""
        try:
            base_title = product_data.get('title', 'Product')
            category = product_data.get('category', 'general')
            key_features = product_data.get('features', [])[:2]
            
            variants = []
            
            # Variant 1: Original (Control)
            variants.append({
                'variant_type': 'control',
                'name': 'Original Title',
                'content': base_title,
                'approach': 'original',
                'config': {'style': 'standard'}
            })
            
            # Variant 2: Feature-enhanced
            if num_variants >= 2 and key_features:
                feature_title = f"{base_title} - {key_features[0]}"
                variants.append({
                    'variant_type': 'treatment',
                    'name': 'Feature-Enhanced Title',
                    'content': feature_title,
                    'approach': 'feature_enhanced',
                    'config': {'style': 'descriptive'}
                })
            
            # Variant 3: Benefit-focused
            if num_variants >= 3:
                benefit_modifiers = {
                    'electronics': 'Pro',
                    'clothing': 'Premium',
                    'home_garden': 'Deluxe',
                    'sports_outdoors': 'Performance',
                    'health_beauty': 'Advanced'
                }
                
                modifier = benefit_modifiers.get(category, 'Premium')
                benefit_title = f"{modifier} {base_title}"
                variants.append({
                    'variant_type': 'treatment',
                    'name': 'Benefit-Focused Title',
                    'content': benefit_title,
                    'approach': 'benefit_focused',
                    'config': {'style': 'premium'}
                })
            
            return variants[:num_variants]
            
        except Exception as e:
            logger.error(f"Error generating title variants: {str(e)}")
            raise
    
    def generate_cta_variants(self, product_data: Dict, num_variants: int = 3) -> List[Dict]:
        """Generate call-to-action button text variants"""
        try:
            price = product_data.get('price', 0)
            category = product_data.get('category', 'general')
            
            variants = []
            
            # Variant 1: Standard (Control)
            variants.append({
                'variant_type': 'control',
                'name': 'Standard CTA',
                'content': 'Add to Cart',
                'approach': 'standard',
                'config': {'urgency': 'none', 'personalization': 'none'}
            })
            
            # Variant 2: Value-focused
            if num_variants >= 2:
                value_cta = f"Get Yours for ${price:.2f}" if price > 0 else "Get Yours Now"
                variants.append({
                    'variant_type': 'treatment',
                    'name': 'Value-Focused CTA',
                    'content': value_cta,
                    'approach': 'value_focused',
                    'config': {'urgency': 'low', 'personalization': 'medium'}
                })
            
            # Variant 3: Urgency-driven
            if num_variants >= 3:
                urgency_ctas = [
                    "Buy Now - Limited Stock",
                    "Secure Yours Today",
                    "Order Now - Don't Miss Out"
                ]
                
                import random
                urgency_cta = random.choice(urgency_ctas)
                variants.append({
                    'variant_type': 'treatment',
                    'name': 'Urgency-Driven CTA',
                    'content': urgency_cta,
                    'approach': 'urgency_driven',
                    'config': {'urgency': 'high', 'personalization': 'low'}
                })
            
            return variants[:num_variants]
            
        except Exception as e:
            logger.error(f"Error generating CTA variants: {str(e)}")
            raise
    
    def create_experiment_variants(self, experiment_id: str, variant_configs: List[Dict]) -> List[str]:
        """Create variant records in database for an experiment"""
        try:
            variant_ids = []
            
            for config in variant_configs:
                variant = Variant(
                    experiment_id=experiment_id,
                    name=config['name'],
                    variant_type=config['variant_type'],
                    config=config.get('config', {}),
                    traffic_allocation=config.get('traffic_allocation', 50.0),
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                
                db.session.add(variant)
                db.session.flush()  # Get ID without committing
                variant_ids.append(variant.id)
            
            db.session.commit()
            logger.info(f"Created {len(variant_ids)} variants for experiment {experiment_id}")
            
            return variant_ids
            
        except Exception as e:
            logger.error(f"Error creating experiment variants: {str(e)}")
            db.session.rollback()
            raise
    
    def generate_complete_product_variants(self, product_data: Dict) -> Dict[str, List[Dict]]:
        """Generate all types of variants for a complete product A/B test"""
        try:
            return {
                'descriptions': self.generate_description_variants(product_data, 3),
                'titles': self.generate_title_variants(product_data, 3),
                'ctas': self.generate_cta_variants(product_data, 3)
            }
            
        except Exception as e:
            logger.error(f"Error generating complete product variants: {str(e)}")
            raise
    
    def validate_variant_content(self, content: str, variant_type: str) -> Dict[str, Any]:
        """Validate generated variant content"""
        try:
            validation_rules = {
                'product_description': {
                    'min_length': 50,
                    'max_length': 1000,
                    'required_elements': []
                },
                'product_title': {
                    'min_length': 10,
                    'max_length': 100,
                    'required_elements': []
                },
                'cta_button': {
                    'min_length': 5,
                    'max_length': 30,
                    'required_elements': []
                }
            }
            
            rules = validation_rules.get(variant_type, validation_rules['product_description'])
            
            errors = []
            warnings = []
            
            # Length validation
            if len(content) < rules['min_length']:
                errors.append(f"Content too short (minimum {rules['min_length']} characters)")
            
            if len(content) > rules['max_length']:
                errors.append(f"Content too long (maximum {rules['max_length']} characters)")
            
            # Content quality checks
            if content.count('!') > 3:
                warnings.append("Excessive exclamation marks may appear unprofessional")
            
            if content.upper() == content:
                warnings.append("All caps text may appear aggressive")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings,
                'length': len(content)
            }
            
        except Exception as e:
            logger.error(f"Error validating variant content: {str(e)}")
            return {'valid': False, 'errors': [f"Validation error: {str(e)}"]}
