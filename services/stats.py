# A/B Testing Statistical Analysis Service
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy import and_, func
import logging

from models import db, Experiment, Variant, Assignment, Event

logger = logging.getLogger(__name__)

class StatisticalAnalyzer:
    """Production-grade statistical analysis for A/B testing with proper significance testing"""
    
    def __init__(self):
        self.min_sample_size = 100  # Minimum conversions per variant
        self.confidence_level = 0.95  # 95% confidence
        self.min_runtime_hours = 24  # Minimum experiment duration
        
    def calculate_conversion_rates(self, experiment_id: str) -> Dict[str, Dict[str, Any]]:
        """Calculate conversion rates and confidence intervals for all variants"""
        try:
            variants = Variant.query.filter_by(experiment_id=experiment_id).all()
            results = {}
            
            for variant in variants:
                # Get total assignments (views)
                total_assignments = Assignment.query.filter_by(
                    experiment_id=experiment_id,
                    variant_id=variant.id
                ).count()
                
                # Get conversions (purchase events)
                conversions = db.session.query(Event).join(Assignment).filter(
                    and_(
                        Assignment.experiment_id == experiment_id,
                        Assignment.variant_id == variant.id,
                        Event.event_type == 'purchase'
                    )
                ).count()
                
                # Calculate conversion rate
                conversion_rate = conversions / total_assignments if total_assignments > 0 else 0
                
                # Calculate 95% confidence interval using Wilson score interval
                ci_lower, ci_upper = self._wilson_confidence_interval(
                    conversions, total_assignments, self.confidence_level
                )
                
                # Calculate revenue metrics
                revenue_data = self._calculate_revenue_metrics(experiment_id, variant.id)
                
                results[variant.id] = {
                    'variant_name': variant.name,
                    'variant_type': variant.variant_type,
                    'total_assignments': total_assignments,
                    'conversions': conversions,
                    'conversion_rate': conversion_rate,
                    'confidence_interval': {
                        'lower': ci_lower,
                        'upper': ci_upper
                    },
                    'revenue': revenue_data,
                    'sample_sufficient': conversions >= self.min_sample_size
                }
                
            return results
            
        except Exception as e:
            logger.error(f"Error calculating conversion rates: {str(e)}")
            raise
    
    def _wilson_confidence_interval(self, successes: int, trials: int, confidence: float) -> Tuple[float, float]:
        """Calculate Wilson score confidence interval for conversion rate"""
        if trials == 0:
            return 0.0, 0.0
            
        z = stats.norm.ppf((1 + confidence) / 2)
        p = successes / trials
        
        denominator = 1 + z**2 / trials
        centre_adjusted_probability = (p + z**2 / (2 * trials)) / denominator
        adjusted_standard_deviation = np.sqrt((p * (1 - p) + z**2 / (4 * trials)) / trials) / denominator
        
        lower_bound = centre_adjusted_probability - z * adjusted_standard_deviation
        upper_bound = centre_adjusted_probability + z * adjusted_standard_deviation
        
        return max(0, lower_bound), min(1, upper_bound)
    
    def _calculate_revenue_metrics(self, experiment_id: str, variant_id: str) -> Dict[str, float]:
        """Calculate revenue metrics for a variant"""
        try:
            # Get all purchase events with revenue
            revenue_query = db.session.query(
                func.sum(Event.revenue).label('total_revenue'),
                func.avg(Event.revenue).label('avg_revenue'),
                func.count(Event.id).label('purchase_count')
            ).join(Assignment).filter(
                and_(
                    Assignment.experiment_id == experiment_id,
                    Assignment.variant_id == variant_id,
                    Event.event_type == 'purchase',
                    Event.revenue.isnot(None)
                )
            ).first()
            
            total_assignments = Assignment.query.filter_by(
                experiment_id=experiment_id,
                variant_id=variant_id
            ).count()
            
            total_revenue = float(revenue_query.total_revenue or 0)
            avg_order_value = float(revenue_query.avg_revenue or 0)
            revenue_per_visitor = total_revenue / total_assignments if total_assignments > 0 else 0
            
            return {
                'total_revenue': total_revenue,
                'avg_order_value': avg_order_value,
                'revenue_per_visitor': revenue_per_visitor,
                'purchase_count': revenue_query.purchase_count or 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating revenue metrics: {str(e)}")
            return {
                'total_revenue': 0.0,
                'avg_order_value': 0.0,
                'revenue_per_visitor': 0.0,
                'purchase_count': 0
            }
    
    def test_statistical_significance(self, experiment_id: str) -> Dict[str, Any]:
        """Perform statistical significance tests between variants"""
        try:
            variants_data = self.calculate_conversion_rates(experiment_id)
            
            if len(variants_data) < 2:
                return {
                    'significant': False,
                    'reason': 'Need at least 2 variants for comparison',
                    'p_value': None,
                    'winner': None
                }
            
            # Find control and treatment variants
            control_variant = None
            treatment_variants = []
            
            for variant_id, data in variants_data.items():
                if data['variant_type'] == 'control':
                    control_variant = (variant_id, data)
                else:
                    treatment_variants.append((variant_id, data))
            
            if not control_variant:
                return {
                    'significant': False,
                    'reason': 'No control variant found',
                    'p_value': None,
                    'winner': None
                }
            
            # Perform chi-square test for each treatment vs control
            results = {
                'significant': False,
                'tests': {},
                'overall_winner': None,
                'recommendations': []
            }
            
            control_id, control_data = control_variant
            
            for treatment_id, treatment_data in treatment_variants:
                # Check if we have sufficient sample size
                if (control_data['conversions'] < self.min_sample_size or 
                    treatment_data['conversions'] < self.min_sample_size):
                    results['tests'][treatment_id] = {
                        'significant': False,
                        'reason': f'Insufficient sample size (need {self.min_sample_size} conversions)',
                        'p_value': None
                    }
                    continue
                
                # Create contingency table
                control_conversions = control_data['conversions']
                control_non_conversions = control_data['total_assignments'] - control_conversions
                treatment_conversions = treatment_data['conversions']
                treatment_non_conversions = treatment_data['total_assignments'] - treatment_conversions
                
                contingency_table = np.array([
                    [control_conversions, control_non_conversions],
                    [treatment_conversions, treatment_non_conversions]
                ])
                
                # Perform chi-square test
                chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
                
                # Calculate effect size (Cramer's V)
                n = np.sum(contingency_table)
                cramers_v = np.sqrt(chi2 / (n * (min(contingency_table.shape) - 1)))
                
                # Calculate relative uplift
                control_rate = control_data['conversion_rate']
                treatment_rate = treatment_data['conversion_rate']
                relative_uplift = ((treatment_rate - control_rate) / control_rate * 100) if control_rate > 0 else 0
                
                is_significant = p_value < (1 - self.confidence_level)
                
                results['tests'][treatment_id] = {
                    'significant': is_significant,
                    'p_value': p_value,
                    'chi_square': chi2,
                    'cramers_v': cramers_v,
                    'relative_uplift': relative_uplift,
                    'treatment_rate': treatment_rate,
                    'control_rate': control_rate,
                    'winner': 'treatment' if (is_significant and treatment_rate > control_rate) else 
                             ('control' if (is_significant and control_rate > treatment_rate) else 'inconclusive')
                }
                
                if is_significant:
                    results['significant'] = True
                    if treatment_rate > control_rate:
                        results['overall_winner'] = treatment_id
            
            # Add recommendations
            results['recommendations'] = self._generate_recommendations(results, variants_data)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in statistical significance testing: {str(e)}")
            raise
    
    def _generate_recommendations(self, test_results: Dict, variants_data: Dict) -> List[str]:
        """Generate actionable recommendations based on test results"""
        recommendations = []
        
        if test_results['significant']:
            if test_results['overall_winner']:
                winner_data = variants_data[test_results['overall_winner']]
                recommendations.append(
                    f"🎉 Significant winner found: {winner_data['variant_name']} "
                    f"with {winner_data['conversion_rate']:.2%} conversion rate"
                )
                recommendations.append("✅ Recommend implementing the winning variant")
            else:
                recommendations.append("⚠️ Significant results found but no clear winner")
                recommendations.append("📊 Review individual variant performance")
        else:
            insufficient_samples = any(
                not data['sample_sufficient'] for data in variants_data.values()
            )
            
            if insufficient_samples:
                recommendations.append(f"📈 Continue test - need {self.min_sample_size} conversions per variant")
                recommendations.append("⏱️ Estimated additional runtime needed")
            else:
                recommendations.append("📊 No significant difference detected")
                recommendations.append("🔄 Consider testing more dramatic changes")
        
        return recommendations
    
    def check_experiment_readiness(self, experiment_id: str) -> Dict[str, Any]:
        """Check if experiment is ready for significance testing"""
        try:
            experiment = Experiment.query.get(experiment_id)
            if not experiment:
                return {'ready': False, 'reason': 'Experiment not found'}
            
            # Check minimum runtime
            if experiment.status == 'running':
                runtime_hours = (datetime.utcnow() - experiment.start_date).total_seconds() / 3600
                if runtime_hours < self.min_runtime_hours:
                    return {
                        'ready': False,
                        'reason': f'Minimum runtime not met ({runtime_hours:.1f}/{self.min_runtime_hours}h)',
                        'runtime_hours': runtime_hours
                    }
            
            # Check sample sizes
            variants_data = self.calculate_conversion_rates(experiment_id)
            insufficient_variants = [
                v for v in variants_data.values() 
                if not v['sample_sufficient']
            ]
            
            if insufficient_variants:
                return {
                    'ready': False,
                    'reason': 'Insufficient sample size for some variants',
                    'insufficient_variants': [v['variant_name'] for v in insufficient_variants]
                }
            
            return {
                'ready': True,
                'runtime_hours': runtime_hours if experiment.status == 'running' else None,
                'total_conversions': sum(v['conversions'] for v in variants_data.values())
            }
            
        except Exception as e:
            logger.error(f"Error checking experiment readiness: {str(e)}")
            return {'ready': False, 'reason': f'Error: {str(e)}'}
    
    def get_experiment_summary(self, experiment_id: str) -> Dict[str, Any]:
        """Get comprehensive experiment summary with all metrics"""
        try:
            experiment = Experiment.query.get(experiment_id)
            if not experiment:
                raise ValueError("Experiment not found")
            
            variants_data = self.calculate_conversion_rates(experiment_id)
            significance_results = self.test_statistical_significance(experiment_id)
            readiness = self.check_experiment_readiness(experiment_id)
            
            # Calculate total metrics
            total_assignments = sum(v['total_assignments'] for v in variants_data.values())
            total_conversions = sum(v['conversions'] for v in variants_data.values())
            total_revenue = sum(v['revenue']['total_revenue'] for v in variants_data.values())
            
            return {
                'experiment': {
                    'id': experiment_id,
                    'name': experiment.name,
                    'status': experiment.status,
                    'start_date': experiment.start_date.isoformat() if experiment.start_date else None,
                    'end_date': experiment.end_date.isoformat() if experiment.end_date else None
                },
                'overall_metrics': {
                    'total_assignments': total_assignments,
                    'total_conversions': total_conversions,
                    'overall_conversion_rate': total_conversions / total_assignments if total_assignments > 0 else 0,
                    'total_revenue': total_revenue
                },
                'variants': variants_data,
                'statistical_analysis': significance_results,
                'readiness': readiness,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating experiment summary: {str(e)}")
            raise
