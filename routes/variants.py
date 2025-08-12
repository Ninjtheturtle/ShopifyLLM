# Variants API Routes
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

from models import db, Experiment, Variant
from services.llm_variants import LLMVariantGenerator

logger = logging.getLogger(__name__)

variants_bp = Blueprint('variants', __name__, url_prefix='/api/variants')

@variants_bp.route('/', methods=['POST'])
def create_variant():
    """Create a new variant for an experiment"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['experiment_id', 'name', 'variant_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Verify experiment exists and is in draft status
        experiment = Experiment.query.get(data['experiment_id'])
        if not experiment:
            return jsonify({'error': 'Experiment not found'}), 404
        
        if experiment.status != 'draft':
            return jsonify({
                'error': 'Can only add variants to draft experiments'
            }), 400
        
        # Create variant
        variant = Variant(
            experiment_id=data['experiment_id'],
            name=data['name'],
            variant_type=data['variant_type'],
            config=data.get('config', {}),
            traffic_allocation=data.get('traffic_allocation', 50.0),
            is_active=data.get('is_active', True),
            created_at=datetime.utcnow()
        )
        
        db.session.add(variant)
        db.session.commit()
        
        return jsonify({
            'id': variant.id,
            'name': variant.name,
            'variant_type': variant.variant_type,
            'experiment_id': variant.experiment_id,
            'created_at': variant.created_at.isoformat(),
            'message': 'Variant created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating variant: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@variants_bp.route('/<variant_id>', methods=['GET'])
def get_variant(variant_id):
    """Get variant details"""
    try:
        variant = Variant.query.get_or_404(variant_id)
        
        return jsonify({
            'id': variant.id,
            'experiment_id': variant.experiment_id,
            'name': variant.name,
            'variant_type': variant.variant_type,
            'config': variant.config,
            'traffic_allocation': variant.traffic_allocation,
            'is_active': variant.is_active,
            'created_at': variant.created_at.isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting variant: {str(e)}")
        return jsonify({'error': str(e)}), 500

@variants_bp.route('/<variant_id>', methods=['PUT'])
def update_variant(variant_id):
    """Update variant configuration"""
    try:
        variant = Variant.query.get_or_404(variant_id)
        data = request.get_json()
        
        # Check if experiment is running
        experiment = Experiment.query.get(variant.experiment_id)
        if experiment.status == 'running':
            # Only allow certain updates during running experiments
            allowed_fields = ['traffic_allocation', 'is_active']
            for field in data:
                if field not in allowed_fields:
                    return jsonify({
                        'error': f'Cannot update {field} while experiment is running'
                    }), 400
        
        # Update allowed fields
        updateable_fields = ['name', 'config', 'traffic_allocation', 'is_active']
        for field in updateable_fields:
            if field in data:
                setattr(variant, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'id': variant.id,
            'message': 'Variant updated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating variant: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@variants_bp.route('/<variant_id>', methods=['DELETE'])
def delete_variant(variant_id):
    """Delete a variant"""
    try:
        variant = Variant.query.get_or_404(variant_id)
        
        # Check if experiment is running
        experiment = Experiment.query.get(variant.experiment_id)
        if experiment.status == 'running':
            return jsonify({
                'error': 'Cannot delete variants while experiment is running'
            }), 400
        
        # Prevent deletion if it's the only variant
        variant_count = Variant.query.filter_by(experiment_id=variant.experiment_id).count()
        if variant_count <= 1:
            return jsonify({
                'error': 'Cannot delete the last variant in an experiment'
            }), 400
        
        db.session.delete(variant)
        db.session.commit()
        
        return jsonify({
            'message': 'Variant deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting variant: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@variants_bp.route('/experiment/<experiment_id>', methods=['GET'])
def list_experiment_variants(experiment_id):
    """Get all variants for an experiment"""
    try:
        experiment = Experiment.query.get_or_404(experiment_id)
        variants = Variant.query.filter_by(experiment_id=experiment_id).order_by(Variant.created_at).all()
        
        result = []
        for variant in variants:
            result.append({
                'id': variant.id,
                'name': variant.name,
                'variant_type': variant.variant_type,
                'config': variant.config,
                'traffic_allocation': variant.traffic_allocation,
                'is_active': variant.is_active,
                'created_at': variant.created_at.isoformat()
            })
        
        return jsonify({
            'experiment_id': experiment_id,
            'experiment_name': experiment.name,
            'variants': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing experiment variants: {str(e)}")
        return jsonify({'error': str(e)}), 500

@variants_bp.route('/generate', methods=['POST'])
def generate_variants():
    """Auto-generate variants using LLM for an experiment"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['experiment_id', 'product_data', 'variant_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        experiment = Experiment.query.get(data['experiment_id'])
        if not experiment:
            return jsonify({'error': 'Experiment not found'}), 404
        
        if experiment.status != 'draft':
            return jsonify({
                'error': 'Can only generate variants for draft experiments'
            }), 400
        
        # Generate variants using LLM
        variant_generator = LLMVariantGenerator()
        num_variants = data.get('num_variants', 3)
        
        if data['variant_type'] == 'product_description':
            variants_data = variant_generator.generate_description_variants(
                data['product_data'], num_variants
            )
        elif data['variant_type'] == 'product_title':
            variants_data = variant_generator.generate_title_variants(
                data['product_data'], num_variants
            )
        elif data['variant_type'] == 'cta_button':
            variants_data = variant_generator.generate_cta_variants(
                data['product_data'], num_variants
            )
        else:
            return jsonify({
                'error': f'Unsupported variant type: {data["variant_type"]}'
            }), 400
        
        # Create variant records
        created_variants = []
        traffic_per_variant = 100.0 / len(variants_data)
        
        for variant_data in variants_data:
            variant = Variant(
                experiment_id=data['experiment_id'],
                name=variant_data['name'],
                variant_type=variant_data['variant_type'],
                config={
                    'content': variant_data['content'],
                    'approach': variant_data['approach'],
                    **variant_data.get('config', {})
                },
                traffic_allocation=traffic_per_variant,
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.session.add(variant)
            db.session.flush()  # Get ID without committing
            
            created_variants.append({
                'id': variant.id,
                'name': variant.name,
                'variant_type': variant.variant_type,
                'config': variant.config,
                'traffic_allocation': variant.traffic_allocation
            })
        
        db.session.commit()
        
        return jsonify({
            'experiment_id': data['experiment_id'],
            'generated_variants': created_variants,
            'message': f'Successfully generated {len(created_variants)} variants'
        }), 201
        
    except Exception as e:
        logger.error(f"Error generating variants: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@variants_bp.route('/<variant_id>/validate', methods=['POST'])
def validate_variant(variant_id):
    """Validate variant content"""
    try:
        variant = Variant.query.get_or_404(variant_id)
        
        # Get content from variant config
        content = variant.config.get('content', '')
        
        if not content:
            return jsonify({
                'valid': False,
                'errors': ['No content found in variant configuration']
            }), 400
        
        # Validate using LLM service
        variant_generator = LLMVariantGenerator()
        
        # Map experiment type to variant type for validation
        experiment = Experiment.query.get(variant.experiment_id)
        validation_type = experiment.experiment_type
        
        validation_result = variant_generator.validate_variant_content(content, validation_type)
        
        return jsonify(validation_result), 200
        
    except Exception as e:
        logger.error(f"Error validating variant: {str(e)}")
        return jsonify({'error': str(e)}), 500

@variants_bp.route('/<variant_id>/duplicate', methods=['POST'])
def duplicate_variant(variant_id):
    """Create a duplicate of an existing variant"""
    try:
        original_variant = Variant.query.get_or_404(variant_id)
        data = request.get_json()
        
        # Check if experiment allows new variants
        experiment = Experiment.query.get(original_variant.experiment_id)
        if experiment.status != 'draft':
            return jsonify({
                'error': 'Can only duplicate variants in draft experiments'
            }), 400
        
        # Create duplicate
        new_name = data.get('name', f"{original_variant.name} (Copy)")
        
        duplicate_variant = Variant(
            experiment_id=original_variant.experiment_id,
            name=new_name,
            variant_type=original_variant.variant_type,
            config=original_variant.config.copy() if original_variant.config else {},
            traffic_allocation=data.get('traffic_allocation', original_variant.traffic_allocation),
            is_active=data.get('is_active', True),
            created_at=datetime.utcnow()
        )
        
        db.session.add(duplicate_variant)
        db.session.commit()
        
        return jsonify({
            'id': duplicate_variant.id,
            'name': duplicate_variant.name,
            'original_variant_id': variant_id,
            'message': 'Variant duplicated successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error duplicating variant: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
