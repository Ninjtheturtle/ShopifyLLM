# A/B Testing Assignment Service
import hashlib
import random
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging

from models import db, Experiment, Variant, Assignment

logger = logging.getLogger(__name__)

class AssignmentEngine:
    """Production-grade user assignment engine for A/B testing"""
    
    def __init__(self):
        self.hash_seed = "shopify_ab_test"  # Consistent seed for deterministic assignment
        
    def assign_user_to_variant(self, user_id: str, experiment_id: str) -> Optional[Dict]:
        """Assign user to a variant with consistent assignment logic"""
        try:
            # Check if user already assigned
            existing_assignment = Assignment.query.filter_by(
                user_id=user_id,
                experiment_id=experiment_id
            ).first()
            
            if existing_assignment:
                variant = Variant.query.get(existing_assignment.variant_id)
                return {
                    'assignment_id': existing_assignment.id,
                    'variant_id': variant.id,
                    'variant_name': variant.name,
                    'variant_type': variant.variant_type,
                    'variant_config': variant.config,
                    'existing_assignment': True,
                    'assigned_at': existing_assignment.assigned_at.isoformat()
                }
            
            # Check if experiment is active
            experiment = Experiment.query.get(experiment_id)
            if not experiment or experiment.status != 'running':
                logger.warning(f"Experiment {experiment_id} is not running")
                return None
            
            # Get active variants
            variants = Variant.query.filter_by(
                experiment_id=experiment_id,
                is_active=True
            ).all()
            
            if not variants:
                logger.warning(f"No active variants found for experiment {experiment_id}")
                return None
            
            # Deterministic assignment based on user_id hash
            selected_variant = self._deterministic_assignment(user_id, experiment_id, variants)
            
            # Create assignment record
            assignment = Assignment(
                user_id=user_id,
                experiment_id=experiment_id,
                variant_id=selected_variant.id,
                assigned_at=datetime.utcnow()
            )
            
            db.session.add(assignment)
            db.session.commit()
            
            logger.info(f"Assigned user {user_id} to variant {selected_variant.name} in experiment {experiment_id}")
            
            return {
                'assignment_id': assignment.id,
                'variant_id': selected_variant.id,
                'variant_name': selected_variant.name,
                'variant_type': selected_variant.variant_type,
                'variant_config': selected_variant.config,
                'existing_assignment': False,
                'assigned_at': assignment.assigned_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error assigning user to variant: {str(e)}")
            db.session.rollback()
            raise
    
    def _deterministic_assignment(self, user_id: str, experiment_id: str, variants: List[Variant]) -> Variant:
        """Assign user to variant using consistent hash-based distribution"""
        # Create deterministic hash
        hash_input = f"{self.hash_seed}:{experiment_id}:{user_id}"
        hash_value = hashlib.md5(hash_input.encode()).hexdigest()
        
        # Convert to integer for modulo operation
        hash_int = int(hash_value, 16)
        
        # Calculate total traffic allocation
        total_allocation = sum(v.traffic_allocation for v in variants)
        
        # Handle case where total allocation is not 100%
        if total_allocation <= 0:
            # Equal distribution if no allocations set
            selected_index = hash_int % len(variants)
            return variants[selected_index]
        
        # Weighted assignment based on traffic allocation
        allocation_point = (hash_int % 10000) / 100.0  # 0-100 range
        cumulative_allocation = 0
        
        for variant in variants:
            cumulative_allocation += variant.traffic_allocation
            if allocation_point <= cumulative_allocation:
                return variant
        
        # Fallback to last variant if rounding issues
        return variants[-1]
    
    def bulk_assign_users(self, user_ids: List[str], experiment_id: str) -> Dict[str, Dict]:
        """Efficiently assign multiple users to variants"""
        try:
            assignments = {}
            
            # Check experiment status
            experiment = Experiment.query.get(experiment_id)
            if not experiment or experiment.status != 'running':
                logger.warning(f"Experiment {experiment_id} is not running")
                return assignments
            
            # Get existing assignments
            existing_assignments = Assignment.query.filter(
                Assignment.experiment_id == experiment_id,
                Assignment.user_id.in_(user_ids)
            ).all()
            
            existing_map = {a.user_id: a for a in existing_assignments}
            
            # Get active variants
            variants = Variant.query.filter_by(
                experiment_id=experiment_id,
                is_active=True
            ).all()
            
            if not variants:
                logger.warning(f"No active variants found for experiment {experiment_id}")
                return assignments
            
            new_assignments = []
            
            for user_id in user_ids:
                if user_id in existing_map:
                    # Return existing assignment
                    existing = existing_map[user_id]
                    variant = Variant.query.get(existing.variant_id)
                    assignments[user_id] = {
                        'assignment_id': existing.id,
                        'variant_id': variant.id,
                        'variant_name': variant.name,
                        'variant_type': variant.variant_type,
                        'variant_config': variant.config,
                        'existing_assignment': True,
                        'assigned_at': existing.assigned_at.isoformat()
                    }
                else:
                    # Create new assignment
                    selected_variant = self._deterministic_assignment(user_id, experiment_id, variants)
                    
                    assignment = Assignment(
                        user_id=user_id,
                        experiment_id=experiment_id,
                        variant_id=selected_variant.id,
                        assigned_at=datetime.utcnow()
                    )
                    
                    new_assignments.append(assignment)
                    assignments[user_id] = {
                        'assignment_id': None,  # Will be set after commit
                        'variant_id': selected_variant.id,
                        'variant_name': selected_variant.name,
                        'variant_type': selected_variant.variant_type,
                        'variant_config': selected_variant.config,
                        'existing_assignment': False,
                        'assigned_at': assignment.assigned_at.isoformat()
                    }
            
            # Bulk insert new assignments
            if new_assignments:
                db.session.add_all(new_assignments)
                db.session.commit()
                
                # Update assignment IDs
                for i, assignment in enumerate(new_assignments):
                    user_id = assignment.user_id
                    assignments[user_id]['assignment_id'] = assignment.id
            
            logger.info(f"Bulk assigned {len(user_ids)} users to experiment {experiment_id}")
            return assignments
            
        except Exception as e:
            logger.error(f"Error in bulk assignment: {str(e)}")
            db.session.rollback()
            raise
    
    def get_user_assignments(self, user_id: str) -> List[Dict]:
        """Get all active assignments for a user"""
        try:
            assignments = db.session.query(Assignment, Variant, Experiment).join(
                Variant, Assignment.variant_id == Variant.id
            ).join(
                Experiment, Assignment.experiment_id == Experiment.id
            ).filter(
                Assignment.user_id == user_id,
                Experiment.status == 'running'
            ).all()
            
            result = []
            for assignment, variant, experiment in assignments:
                result.append({
                    'assignment_id': assignment.id,
                    'experiment_id': experiment.id,
                    'experiment_name': experiment.name,
                    'variant_id': variant.id,
                    'variant_name': variant.name,
                    'variant_type': variant.variant_type,
                    'variant_config': variant.config,
                    'assigned_at': assignment.assigned_at.isoformat()
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting user assignments: {str(e)}")
            raise
    
    def remove_user_from_experiment(self, user_id: str, experiment_id: str) -> bool:
        """Remove user from experiment (for opt-out scenarios)"""
        try:
            assignment = Assignment.query.filter_by(
                user_id=user_id,
                experiment_id=experiment_id
            ).first()
            
            if assignment:
                db.session.delete(assignment)
                db.session.commit()
                logger.info(f"Removed user {user_id} from experiment {experiment_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error removing user from experiment: {str(e)}")
            db.session.rollback()
            raise
    
    def get_assignment_distribution(self, experiment_id: str) -> Dict[str, Dict]:
        """Get current assignment distribution across variants"""
        try:
            # Get assignment counts per variant
            assignment_counts = db.session.query(
                Variant.id,
                Variant.name,
                Variant.traffic_allocation,
                db.func.count(Assignment.id).label('actual_assignments')
            ).outerjoin(
                Assignment, 
                Assignment.variant_id == Variant.id,
                Assignment.experiment_id == experiment_id
            ).filter(
                Variant.experiment_id == experiment_id
            ).group_by(
                Variant.id, Variant.name, Variant.traffic_allocation
            ).all()
            
            total_assignments = sum(count.actual_assignments for count in assignment_counts)
            
            distribution = {}
            for count in assignment_counts:
                actual_percentage = (count.actual_assignments / total_assignments * 100) if total_assignments > 0 else 0
                
                distribution[count.id] = {
                    'variant_name': count.name,
                    'target_allocation': count.traffic_allocation,
                    'actual_assignments': count.actual_assignments,
                    'actual_percentage': actual_percentage,
                    'deviation': actual_percentage - count.traffic_allocation
                }
            
            return {
                'total_assignments': total_assignments,
                'variants': distribution,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting assignment distribution: {str(e)}")
            raise
    
    def validate_experiment_assignment_rules(self, experiment_id: str) -> Dict[str, Any]:
        """Validate experiment assignment configuration"""
        try:
            experiment = Experiment.query.get(experiment_id)
            if not experiment:
                return {'valid': False, 'errors': ['Experiment not found']}
            
            variants = Variant.query.filter_by(experiment_id=experiment_id).all()
            errors = []
            warnings = []
            
            # Check if experiment has variants
            if not variants:
                errors.append("No variants defined for experiment")
                return {'valid': False, 'errors': errors}
            
            # Check traffic allocation
            total_allocation = sum(v.traffic_allocation for v in variants if v.is_active)
            
            if total_allocation > 100:
                errors.append(f"Total traffic allocation exceeds 100% ({total_allocation}%)")
            elif total_allocation < 100:
                warnings.append(f"Traffic allocation is less than 100% ({total_allocation}%)")
            
            # Check for control variant
            control_variants = [v for v in variants if v.variant_type == 'control']
            if len(control_variants) == 0:
                warnings.append("No control variant defined")
            elif len(control_variants) > 1:
                warnings.append("Multiple control variants defined")
            
            # Check variant configurations
            for variant in variants:
                if not variant.config:
                    warnings.append(f"Variant '{variant.name}' has no configuration")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings,
                'total_allocation': total_allocation,
                'active_variants': len([v for v in variants if v.is_active])
            }
            
        except Exception as e:
            logger.error(f"Error validating assignment rules: {str(e)}")
            return {'valid': False, 'errors': [f"Validation error: {str(e)}"]}
