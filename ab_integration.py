# A/B Testing Integration for Store Builder
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ABTestingIntegration:
    """Integration layer between store builder and A/B testing system"""
    
    def __init__(self):
        self.enabled = True
        
    def create_product_experiments(self, product_data: Dict, store_config: Dict) -> List[str]:
        """Create A/B experiments for a new product"""
        try:
            if not self.enabled:
                return []
            
            from models import db, Experiment, Variant
            from services.llm_variants import LLMVariantGenerator
            
            experiment_ids = []
            variant_generator = LLMVariantGenerator()
            
            # Create description experiment
            if store_config.get('test_descriptions', True):
                desc_experiment = Experiment(
                    name=f"Product Description Test - {product_data.get('title', 'Product')}",
                    description=f"A/B test for product description optimization",
                    experiment_type='product_description',
                    status='draft',
                    config={
                        'product_id': product_data.get('id'),
                        'auto_created': True,
                        'store_integration': True
                    },
                    created_at=datetime.utcnow()
                )
                
                db.session.add(desc_experiment)
                db.session.flush()
                
                # Generate description variants
                description_variants = variant_generator.generate_description_variants(product_data, 3)
                
                for i, variant_data in enumerate(description_variants):
                    variant = Variant(
                        experiment_id=desc_experiment.id,
                        name=variant_data['name'],
                        variant_type=variant_data['variant_type'],
                        config={
                            'content': variant_data['content'],
                            'approach': variant_data['approach'],
                            **variant_data.get('config', {})
                        },
                        traffic_allocation=33.33 if i < 2 else 33.34,  # Even split
                        is_active=True,
                        created_at=datetime.utcnow()
                    )
                    db.session.add(variant)
                
                experiment_ids.append(desc_experiment.id)
                logger.info(f"Created description experiment {desc_experiment.id} for product")
            
            # Create title experiment
            if store_config.get('test_titles', True):
                title_experiment = Experiment(
                    name=f"Product Title Test - {product_data.get('title', 'Product')}",
                    description=f"A/B test for product title optimization",
                    experiment_type='product_title',
                    status='draft',
                    config={
                        'product_id': product_data.get('id'),
                        'auto_created': True,
                        'store_integration': True
                    },
                    created_at=datetime.utcnow()
                )
                
                db.session.add(title_experiment)
                db.session.flush()
                
                # Generate title variants
                title_variants = variant_generator.generate_title_variants(product_data, 3)
                
                for i, variant_data in enumerate(title_variants):
                    variant = Variant(
                        experiment_id=title_experiment.id,
                        name=variant_data['name'],
                        variant_type=variant_data['variant_type'],
                        config={
                            'content': variant_data['content'],
                            'approach': variant_data['approach'],
                            **variant_data.get('config', {})
                        },
                        traffic_allocation=33.33 if i < 2 else 33.34,
                        is_active=True,
                        created_at=datetime.utcnow()
                    )
                    db.session.add(variant)
                
                experiment_ids.append(title_experiment.id)
                logger.info(f"Created title experiment {title_experiment.id} for product")
            
            db.session.commit()
            return experiment_ids
            
        except Exception as e:
            logger.error(f"Error creating product experiments: {str(e)}")
            db.session.rollback()
            return []
    
    def auto_start_experiments(self, experiment_ids: List[str]) -> int:
        """Auto-start experiments if configured"""
        try:
            from models import db, Experiment
            
            started_count = 0
            
            for exp_id in experiment_ids:
                experiment = Experiment.query.get(exp_id)
                if experiment and experiment.status == 'draft':
                    experiment.status = 'running'
                    experiment.start_date = datetime.utcnow()
                    started_count += 1
            
            db.session.commit()
            logger.info(f"Auto-started {started_count} experiments")
            return started_count
            
        except Exception as e:
            logger.error(f"Error auto-starting experiments: {str(e)}")
            db.session.rollback()
            return 0
    
    def generate_ab_tracking_code(self, product_id: str, experiment_ids: List[str]) -> str:
        """Generate JavaScript tracking code for theme integration"""
        if not experiment_ids:
            return ""
        
        tracking_code = f"""
<!-- ShopifyLLM A/B Testing -->
<script>
  document.addEventListener('DOMContentLoaded', function() {{
    if (typeof window.shopifyAB !== 'undefined') {{
      const productId = '{product_id}';
      const experiments = {experiment_ids};
      
      // Apply A/B tests for this product
      experiments.forEach(async function(experimentId) {{
        try {{
          // Determine test type and apply accordingly
          if (experimentId.includes('description')) {{
            await window.shopifyAB.testProductDescription(experimentId);
          }} else if (experimentId.includes('title')) {{
            await window.shopifyAB.testProductTitle(experimentId);
          }}
        }} catch (error) {{
          console.warn('A/B test error:', error);
        }}
      }});
      
      // Track add to cart events
      const addToCartBtn = document.querySelector('form[action="/cart/add"] button[type="submit"]');
      if (addToCartBtn) {{
        addToCartBtn.addEventListener('click', function() {{
          experiments.forEach(function(experimentId) {{
            window.shopifyAB.onAddToCart(experimentId, {{
              product_id: productId,
              product_title: document.querySelector('.product-title')?.textContent?.trim()
            }});
          }});
        }});
      }}
    }}
  }});
</script>
<!-- End ShopifyLLM A/B Testing -->
"""
        return tracking_code.strip()
    
    def integrate_with_shopify_product(self, shopify_product: Dict, experiment_ids: List[str]) -> Dict:
        """Integrate A/B testing data with Shopify product"""
        try:
            # Add A/B testing metadata to product
            if 'metafields' not in shopify_product:
                shopify_product['metafields'] = []
            
            # Store experiment IDs in metafields
            shopify_product['metafields'].append({
                'namespace': 'shopify_llm',
                'key': 'ab_experiments',
                'value': ','.join(experiment_ids),
                'value_type': 'string'
            })
            
            # Add tracking code to product description
            tracking_code = self.generate_ab_tracking_code(
                shopify_product.get('id', 'unknown'), 
                experiment_ids
            )
            
            if tracking_code:
                original_description = shopify_product.get('body_html', '')
                shopify_product['body_html'] = original_description + '\n\n' + tracking_code
            
            logger.info(f"Integrated A/B testing with product {shopify_product.get('id')}")
            return shopify_product
            
        except Exception as e:
            logger.error(f"Error integrating A/B testing with Shopify product: {str(e)}")
            return shopify_product
    
    def get_winning_content(self, experiment_id: str) -> Optional[Dict]:
        """Get winning variant content for publishing"""
        try:
            from models import Experiment
            from services.stats import StatisticalAnalyzer
            
            experiment = Experiment.query.get(experiment_id)
            if not experiment:
                return None
            
            # Check if experiment has a declared winner
            if experiment.config and experiment.config.get('winner_variant_id'):
                from models import Variant
                winner = Variant.query.get(experiment.config['winner_variant_id'])
                if winner:
                    return {
                        'variant_id': winner.id,
                        'content': winner.config.get('content'),
                        'approach': winner.config.get('approach'),
                        'config': winner.config
                    }
            
            # If no declared winner, check statistical significance
            stats_analyzer = StatisticalAnalyzer()
            results = stats_analyzer.test_statistical_significance(experiment_id)
            
            if results.get('significant') and results.get('overall_winner'):
                from models import Variant
                winner = Variant.query.get(results['overall_winner'])
                if winner:
                    return {
                        'variant_id': winner.id,
                        'content': winner.config.get('content'),
                        'approach': winner.config.get('approach'),
                        'config': winner.config
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting winning content: {str(e)}")
            return None
    
    def publish_winners_to_store(self, store_id: str) -> Dict[str, Any]:
        """Publish winning variants back to the live store"""
        try:
            from models import Experiment
            
            # Find completed experiments for this store
            completed_experiments = Experiment.query.filter_by(
                status='completed'
            ).filter(
                Experiment.config['store_id'].astext == store_id
            ).all()
            
            published_count = 0
            errors = []
            
            for experiment in completed_experiments:
                try:
                    winning_content = self.get_winning_content(experiment.id)
                    if winning_content:
                        # Update the live product with winning content
                        product_id = experiment.config.get('product_id')
                        if product_id:
                            # This would integrate with your Shopify API to update the product
                            # For now, just log the action
                            logger.info(
                                f"Would publish winning content for experiment {experiment.id} "
                                f"to product {product_id}: {winning_content['content'][:100]}..."
                            )
                            published_count += 1
                
                except Exception as exp_error:
                    errors.append(f"Experiment {experiment.id}: {str(exp_error)}")
            
            return {
                'published_count': published_count,
                'total_experiments': len(completed_experiments),
                'errors': errors
            }
            
        except Exception as e:
            logger.error(f"Error publishing winners to store: {str(e)}")
            return {'published_count': 0, 'errors': [str(e)]}
    
    def cleanup_old_experiments(self, days_old: int = 30) -> int:
        """Clean up old completed experiments"""
        try:
            from models import db, Experiment
            from datetime import timedelta
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            old_experiments = Experiment.query.filter(
                Experiment.status == 'completed',
                Experiment.end_date < cutoff_date
            ).all()
            
            deleted_count = 0
            for experiment in old_experiments:
                # Archive the results before deletion if needed
                logger.info(f"Cleaning up old experiment: {experiment.name}")
                db.session.delete(experiment)
                deleted_count += 1
            
            db.session.commit()
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old experiments: {str(e)}")
            db.session.rollback()
            return 0
