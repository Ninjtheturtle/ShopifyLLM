# Experiments API Routes
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from typing import Dict, Any

from models import db, Experiment, Variant
from services.stats import StatisticalAnalyzer
from services.assign import AssignmentEngine
from services.llm_variants import LLMVariantGenerator

logger = logging.getLogger(__name__)

experiments_bp = Blueprint('experiments', __name__, url_prefix='/api/experiments')

@experiments_bp.route('/', methods=['GET'])
def list_experiments():
    """Get list of all experiments with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status_filter = request.args.get('status')
        
        query = Experiment.query
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        experiments = query.order_by(Experiment.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        result = []
        for exp in experiments.items:
            # Get variant count
            variant_count = Variant.query.filter_by(experiment_id=exp.id).count()
            
            result.append({
                'id': exp.id,
                'name': exp.name,
                'description': exp.description,
                'status': exp.status,
                'experiment_type': exp.experiment_type,
                'start_date': exp.start_date.isoformat() if exp.start_date else None,
                'end_date': exp.end_date.isoformat() if exp.end_date else None,
                'created_at': exp.created_at.isoformat(),
                'variant_count': variant_count
            })
        
        return jsonify({
            'experiments': result,
            'pagination': {
                'page': experiments.page,
                'pages': experiments.pages,
                'per_page': experiments.per_page,
                'total': experiments.total
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing experiments: {str(e)}")
        return jsonify({'error': str(e)}), 500

@experiments_bp.route('/', methods=['POST'])
def create_experiment():
    """Create a new A/B test experiment"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'experiment_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create experiment
        experiment = Experiment(
            name=data['name'],
            description=data.get('description', ''),
            experiment_type=data['experiment_type'],
            status='draft',
            config=data.get('config', {}),
            created_at=datetime.utcnow()
        )
        
        db.session.add(experiment)
        db.session.flush()  # Get ID without committing
        
        # Auto-generate variants if product data provided
        if data.get('auto_generate_variants') and data.get('product_data'):
            try:
                variant_generator = LLMVariantGenerator()
                
                if data['experiment_type'] == 'product_description':
                    variants_data = variant_generator.generate_description_variants(
                        data['product_data'], 
                        data.get('num_variants', 3)
                    )
                elif data['experiment_type'] == 'product_title':
                    variants_data = variant_generator.generate_title_variants(
                        data['product_data'],
                        data.get('num_variants', 3)
                    )
                elif data['experiment_type'] == 'cta_button':
                    variants_data = variant_generator.generate_cta_variants(
                        data['product_data'],
                        data.get('num_variants', 3)
                    )
                else:
                    variants_data = []
                
                # Create variant records
                for i, variant_data in enumerate(variants_data):
                    variant = Variant(
                        experiment_id=experiment.id,
                        name=variant_data['name'],
                        variant_type=variant_data['variant_type'],
                        config={
                            'content': variant_data['content'],
                            'approach': variant_data['approach'],
                            **variant_data.get('config', {})
                        },
                        traffic_allocation=100.0 / len(variants_data),
                        is_active=True,
                        created_at=datetime.utcnow()
                    )
                    db.session.add(variant)
                
            except Exception as variant_error:
                logger.error(f"Error generating variants: {str(variant_error)}")
                # Continue without auto-generated variants
        
        db.session.commit()
        
        return jsonify({
            'id': experiment.id,
            'name': experiment.name,
            'status': experiment.status,
            'experiment_type': experiment.experiment_type,
            'created_at': experiment.created_at.isoformat(),
            'message': 'Experiment created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating experiment: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@experiments_bp.route('/<experiment_id>', methods=['GET'])
def get_experiment(experiment_id):
    """Get detailed experiment information"""
    try:
        experiment = Experiment.query.get_or_404(experiment_id)
        
        # Get variants
        variants = Variant.query.filter_by(experiment_id=experiment_id).all()
        variants_data = []
        
        for variant in variants:
            variants_data.append({
                'id': variant.id,
                'name': variant.name,
                'variant_type': variant.variant_type,
                'config': variant.config,
                'traffic_allocation': variant.traffic_allocation,
                'is_active': variant.is_active,
                'created_at': variant.created_at.isoformat()
            })
        
        # Get assignment distribution if experiment is running
        assignment_distribution = None
        if experiment.status == 'running':
            try:
                assignment_engine = AssignmentEngine()
                assignment_distribution = assignment_engine.get_assignment_distribution(experiment_id)
            except Exception as dist_error:
                logger.warning(f"Could not get assignment distribution: {str(dist_error)}")
        
        return jsonify({
            'id': experiment.id,
            'name': experiment.name,
            'description': experiment.description,
            'status': experiment.status,
            'experiment_type': experiment.experiment_type,
            'config': experiment.config,
            'start_date': experiment.start_date.isoformat() if experiment.start_date else None,
            'end_date': experiment.end_date.isoformat() if experiment.end_date else None,
            'created_at': experiment.created_at.isoformat(),
            'variants': variants_data,
            'assignment_distribution': assignment_distribution
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting experiment: {str(e)}")
        return jsonify({'error': str(e)}), 500

@experiments_bp.route('/<experiment_id>', methods=['PUT'])
def update_experiment(experiment_id):
    """Update experiment configuration"""
    try:
        experiment = Experiment.query.get_or_404(experiment_id)
        data = request.get_json()
        
        # Prevent certain updates if experiment is running
        if experiment.status == 'running':
            protected_fields = ['experiment_type']
            for field in protected_fields:
                if field in data:
                    return jsonify({
                        'error': f'Cannot update {field} while experiment is running'
                    }), 400
        
        # Update allowed fields
        updateable_fields = ['name', 'description', 'config']
        for field in updateable_fields:
            if field in data:
                setattr(experiment, field, data[field])
        
        experiment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'id': experiment.id,
            'message': 'Experiment updated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating experiment: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@experiments_bp.route('/<experiment_id>/start', methods=['POST'])
def start_experiment(experiment_id):
    """Start an experiment"""
    try:
        experiment = Experiment.query.get_or_404(experiment_id)
        
        if experiment.status != 'draft':
            return jsonify({
                'error': f'Can only start experiments in draft status. Current status: {experiment.status}'
            }), 400
        
        # Validate experiment configuration
        assignment_engine = AssignmentEngine()
        validation = assignment_engine.validate_experiment_assignment_rules(experiment_id)
        
        if not validation['valid']:
            return jsonify({
                'error': 'Experiment validation failed',
                'validation_errors': validation['errors']
            }), 400
        
        # Start experiment
        experiment.status = 'running'
        experiment.start_date = datetime.utcnow()
        experiment.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'id': experiment.id,
            'status': experiment.status,
            'start_date': experiment.start_date.isoformat(),
            'message': 'Experiment started successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error starting experiment: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@experiments_bp.route('/<experiment_id>/stop', methods=['POST'])
def stop_experiment(experiment_id):
    """Stop a running experiment"""
    try:
        experiment = Experiment.query.get_or_404(experiment_id)
        
        if experiment.status != 'running':
            return jsonify({
                'error': f'Can only stop running experiments. Current status: {experiment.status}'
            }), 400
        
        experiment.status = 'stopped'
        experiment.end_date = datetime.utcnow()
        experiment.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'id': experiment.id,
            'status': experiment.status,
            'end_date': experiment.end_date.isoformat(),
            'message': 'Experiment stopped successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error stopping experiment: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@experiments_bp.route('/<experiment_id>/results', methods=['GET'])
def get_experiment_results(experiment_id):
    """Get comprehensive experiment results and statistical analysis"""
    try:
        experiment = Experiment.query.get_or_404(experiment_id)
        
        if experiment.status == 'draft':
            return jsonify({
                'error': 'Cannot get results for draft experiments'
            }), 400
        
        # Generate comprehensive analysis
        stats_analyzer = StatisticalAnalyzer()
        results = stats_analyzer.get_experiment_summary(experiment_id)
        
        return jsonify(results), 200
        
    except Exception as e:
        logger.error(f"Error getting experiment results: {str(e)}")
        return jsonify({'error': str(e)}), 500

@experiments_bp.route('/<experiment_id>/publish-winner', methods=['POST'])
def publish_winner(experiment_id):
    """Publish the winning variant as the default"""
    try:
        data = request.get_json()
        winner_variant_id = data.get('variant_id')
        
        if not winner_variant_id:
            return jsonify({'error': 'variant_id is required'}), 400
        
        experiment = Experiment.query.get_or_404(experiment_id)
        winner_variant = Variant.query.get_or_404(winner_variant_id)
        
        # Verify variant belongs to experiment
        if winner_variant.experiment_id != experiment_id:
            return jsonify({'error': 'Variant does not belong to this experiment'}), 400
        
        # Update experiment status
        experiment.status = 'completed'
        experiment.end_date = datetime.utcnow()
        experiment.config = experiment.config or {}
        experiment.config['winner_variant_id'] = winner_variant_id
        experiment.config['published_at'] = datetime.utcnow().isoformat()
        
        db.session.commit()
        
        # TODO: Implement actual publishing logic to update product/store content
        # This would integrate with store_builder.py to update the live content
        
        return jsonify({
            'experiment_id': experiment_id,
            'winner_variant_id': winner_variant_id,
            'status': 'completed',
            'message': 'Winner published successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error publishing winner: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@experiments_bp.route('/<experiment_id>', methods=['DELETE'])
def delete_experiment(experiment_id):
    """Delete an experiment and all associated data"""
    try:
        experiment = Experiment.query.get_or_404(experiment_id)
        
        if experiment.status == 'running':
            return jsonify({
                'error': 'Cannot delete running experiments. Stop the experiment first.'
            }), 400
        
        # Delete will cascade to variants, assignments, and events due to foreign key constraints
        db.session.delete(experiment)
        db.session.commit()
        
        return jsonify({
            'message': 'Experiment deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting experiment: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
