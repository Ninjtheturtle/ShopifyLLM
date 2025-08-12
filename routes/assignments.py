# Assignments API Routes
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

from models import db, Assignment, Experiment, Variant
from services.assign import AssignmentEngine

logger = logging.getLogger(__name__)

assignments_bp = Blueprint('assignments', __name__, url_prefix='/api/assignments')

@assignments_bp.route('/assign', methods=['POST'])
def assign_user():
    """Assign a user to a variant in an experiment"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'experiment_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        assignment_engine = AssignmentEngine()
        
        # Assign user to variant
        assignment_result = assignment_engine.assign_user_to_variant(
            user_id=data['user_id'],
            experiment_id=data['experiment_id']
        )
        
        if assignment_result is None:
            return jsonify({
                'error': 'Could not assign user to variant. Experiment may not be running.'
            }), 400
        
        return jsonify({
            'user_id': data['user_id'],
            'experiment_id': data['experiment_id'],
            'assignment': assignment_result
        }), 200
        
    except Exception as e:
        logger.error(f"Error assigning user: {str(e)}")
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/bulk-assign', methods=['POST'])
def bulk_assign_users():
    """Assign multiple users to variants in an experiment"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_ids', 'experiment_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        if not isinstance(data['user_ids'], list):
            return jsonify({'error': 'user_ids must be a list'}), 400
        
        if len(data['user_ids']) > 1000:
            return jsonify({'error': 'Cannot assign more than 1000 users at once'}), 400
        
        assignment_engine = AssignmentEngine()
        
        # Bulk assign users
        assignments = assignment_engine.bulk_assign_users(
            user_ids=data['user_ids'],
            experiment_id=data['experiment_id']
        )
        
        return jsonify({
            'experiment_id': data['experiment_id'],
            'total_users': len(data['user_ids']),
            'assignments': assignments,
            'successful_assignments': len(assignments)
        }), 200
        
    except Exception as e:
        logger.error(f"Error in bulk assignment: {str(e)}")
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/user/<user_id>', methods=['GET'])
def get_user_assignments(user_id):
    """Get all active assignments for a user"""
    try:
        assignment_engine = AssignmentEngine()
        assignments = assignment_engine.get_user_assignments(user_id)
        
        return jsonify({
            'user_id': user_id,
            'assignments': assignments,
            'total_assignments': len(assignments)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting user assignments: {str(e)}")
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/experiment/<experiment_id>/distribution', methods=['GET'])
def get_assignment_distribution(experiment_id):
    """Get assignment distribution for an experiment"""
    try:
        experiment = Experiment.query.get_or_404(experiment_id)
        
        assignment_engine = AssignmentEngine()
        distribution = assignment_engine.get_assignment_distribution(experiment_id)
        
        return jsonify(distribution), 200
        
    except Exception as e:
        logger.error(f"Error getting assignment distribution: {str(e)}")
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/experiment/<experiment_id>', methods=['GET'])
def list_experiment_assignments(experiment_id):
    """Get paginated list of assignments for an experiment"""
    try:
        experiment = Experiment.query.get_or_404(experiment_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        variant_id = request.args.get('variant_id')
        
        query = Assignment.query.filter_by(experiment_id=experiment_id)
        
        if variant_id:
            query = query.filter_by(variant_id=variant_id)
        
        assignments = query.order_by(Assignment.assigned_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        result = []
        for assignment in assignments.items:
            variant = Variant.query.get(assignment.variant_id)
            result.append({
                'id': assignment.id,
                'user_id': assignment.user_id,
                'variant_id': assignment.variant_id,
                'variant_name': variant.name if variant else 'Unknown',
                'assigned_at': assignment.assigned_at.isoformat()
            })
        
        return jsonify({
            'experiment_id': experiment_id,
            'assignments': result,
            'pagination': {
                'page': assignments.page,
                'pages': assignments.pages,
                'per_page': assignments.per_page,
                'total': assignments.total
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing experiment assignments: {str(e)}")
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/<assignment_id>', methods=['DELETE'])
def remove_assignment(assignment_id):
    """Remove a specific assignment"""
    try:
        assignment = Assignment.query.get_or_404(assignment_id)
        
        # Check if experiment is running
        experiment = Experiment.query.get(assignment.experiment_id)
        if experiment.status == 'running':
            return jsonify({
                'error': 'Cannot remove assignments while experiment is running'
            }), 400
        
        user_id = assignment.user_id
        experiment_id = assignment.experiment_id
        
        db.session.delete(assignment)
        db.session.commit()
        
        return jsonify({
            'user_id': user_id,
            'experiment_id': experiment_id,
            'message': 'Assignment removed successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error removing assignment: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/user/<user_id>/experiment/<experiment_id>', methods=['DELETE'])
def remove_user_from_experiment(user_id, experiment_id):
    """Remove a user from an experiment"""
    try:
        assignment_engine = AssignmentEngine()
        
        removed = assignment_engine.remove_user_from_experiment(user_id, experiment_id)
        
        if removed:
            return jsonify({
                'user_id': user_id,
                'experiment_id': experiment_id,
                'message': 'User removed from experiment successfully'
            }), 200
        else:
            return jsonify({
                'user_id': user_id,
                'experiment_id': experiment_id,
                'message': 'User was not assigned to this experiment'
            }), 404
        
    except Exception as e:
        logger.error(f"Error removing user from experiment: {str(e)}")
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/validate/<experiment_id>', methods=['GET'])
def validate_experiment_assignments(experiment_id):
    """Validate assignment configuration for an experiment"""
    try:
        experiment = Experiment.query.get_or_404(experiment_id)
        
        assignment_engine = AssignmentEngine()
        validation = assignment_engine.validate_experiment_assignment_rules(experiment_id)
        
        return jsonify(validation), 200
        
    except Exception as e:
        logger.error(f"Error validating experiment assignments: {str(e)}")
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/stats/<experiment_id>', methods=['GET'])
def get_assignment_stats(experiment_id):
    """Get assignment statistics for an experiment"""
    try:
        experiment = Experiment.query.get_or_404(experiment_id)
        
        # Get basic assignment counts
        total_assignments = Assignment.query.filter_by(experiment_id=experiment_id).count()
        
        # Get assignments by variant
        variant_stats = db.session.query(
            Variant.id,
            Variant.name,
            Variant.traffic_allocation,
            db.func.count(Assignment.id).label('assignment_count')
        ).outerjoin(
            Assignment, Assignment.variant_id == Variant.id
        ).filter(
            Variant.experiment_id == experiment_id
        ).group_by(
            Variant.id, Variant.name, Variant.traffic_allocation
        ).all()
        
        # Get assignment timeline (last 7 days)
        from datetime import timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        daily_assignments = db.session.query(
            db.func.date(Assignment.assigned_at).label('date'),
            db.func.count(Assignment.id).label('count')
        ).filter(
            Assignment.experiment_id == experiment_id,
            Assignment.assigned_at >= seven_days_ago
        ).group_by(
            db.func.date(Assignment.assigned_at)
        ).order_by('date').all()
        
        # Calculate distribution
        variants = []
        for stat in variant_stats:
            actual_percentage = (stat.assignment_count / total_assignments * 100) if total_assignments > 0 else 0
            variants.append({
                'variant_id': stat.id,
                'variant_name': stat.name,
                'target_allocation': stat.traffic_allocation,
                'actual_assignments': stat.assignment_count,
                'actual_percentage': round(actual_percentage, 2),
                'deviation': round(actual_percentage - stat.traffic_allocation, 2)
            })
        
        # Format timeline
        timeline = []
        for day in daily_assignments:
            timeline.append({
                'date': day.date.isoformat(),
                'assignments': day.count
            })
        
        return jsonify({
            'experiment_id': experiment_id,
            'experiment_name': experiment.name,
            'total_assignments': total_assignments,
            'variants': variants,
            'timeline': timeline,
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting assignment stats: {str(e)}")
        return jsonify({'error': str(e)}), 500
