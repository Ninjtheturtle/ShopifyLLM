# Events API Routes
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import logging

from models import db, Event, Assignment, Experiment, Variant

logger = logging.getLogger(__name__)

events_bp = Blueprint('events', __name__, url_prefix='/api/events')

@events_bp.route('/', methods=['POST'])
def track_event():
    """Track a conversion or interaction event"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'experiment_id', 'event_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Find user's assignment for this experiment
        assignment = Assignment.query.filter_by(
            user_id=data['user_id'],
            experiment_id=data['experiment_id']
        ).first()
        
        if not assignment:
            return jsonify({
                'error': 'User is not assigned to this experiment'
            }), 400
        
        # Validate event type
        valid_event_types = ['view', 'click', 'add_to_cart', 'purchase', 'signup', 'custom']
        if data['event_type'] not in valid_event_types:
            return jsonify({
                'error': f'Invalid event_type. Must be one of: {valid_event_types}'
            }), 400
        
        # Create event record
        event = Event(
            assignment_id=assignment.id,
            event_type=data['event_type'],
            event_data=data.get('event_data', {}),
            revenue=data.get('revenue'),
            timestamp=datetime.utcnow()
        )
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify({
            'event_id': event.id,
            'user_id': data['user_id'],
            'experiment_id': data['experiment_id'],
            'event_type': event.event_type,
            'timestamp': event.timestamp.isoformat(),
            'message': 'Event tracked successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error tracking event: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@events_bp.route('/bulk', methods=['POST'])
def track_bulk_events():
    """Track multiple events in batch"""
    try:
        data = request.get_json()
        
        if 'events' not in data or not isinstance(data['events'], list):
            return jsonify({'error': 'events field must be a list'}), 400
        
        if len(data['events']) > 1000:
            return jsonify({'error': 'Cannot track more than 1000 events at once'}), 400
        
        successful_events = []
        failed_events = []
        
        for i, event_data in enumerate(data['events']):
            try:
                # Validate required fields for each event
                required_fields = ['user_id', 'experiment_id', 'event_type']
                for field in required_fields:
                    if field not in event_data:
                        failed_events.append({
                            'index': i,
                            'error': f'Missing required field: {field}',
                            'event_data': event_data
                        })
                        continue
                
                # Find assignment
                assignment = Assignment.query.filter_by(
                    user_id=event_data['user_id'],
                    experiment_id=event_data['experiment_id']
                ).first()
                
                if not assignment:
                    failed_events.append({
                        'index': i,
                        'error': 'User not assigned to experiment',
                        'event_data': event_data
                    })
                    continue
                
                # Create event
                event = Event(
                    assignment_id=assignment.id,
                    event_type=event_data['event_type'],
                    event_data=event_data.get('event_data', {}),
                    revenue=event_data.get('revenue'),
                    timestamp=datetime.utcnow()
                )
                
                db.session.add(event)
                successful_events.append({
                    'index': i,
                    'user_id': event_data['user_id'],
                    'experiment_id': event_data['experiment_id'],
                    'event_type': event_data['event_type']
                })
                
            except Exception as event_error:
                failed_events.append({
                    'index': i,
                    'error': str(event_error),
                    'event_data': event_data
                })
        
        db.session.commit()
        
        return jsonify({
            'total_events': len(data['events']),
            'successful_events': len(successful_events),
            'failed_events': len(failed_events),
            'successful': successful_events,
            'failed': failed_events
        }), 200
        
    except Exception as e:
        logger.error(f"Error in bulk event tracking: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@events_bp.route('/experiment/<experiment_id>', methods=['GET'])
def list_experiment_events(experiment_id):
    """Get events for an experiment with pagination and filtering"""
    try:
        experiment = Experiment.query.get_or_404(experiment_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        event_type = request.args.get('event_type')
        variant_id = request.args.get('variant_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = db.session.query(Event, Assignment, Variant).join(
            Assignment, Event.assignment_id == Assignment.id
        ).join(
            Variant, Assignment.variant_id == Variant.id
        ).filter(
            Assignment.experiment_id == experiment_id
        )
        
        # Apply filters
        if event_type:
            query = query.filter(Event.event_type == event_type)
        
        if variant_id:
            query = query.filter(Assignment.variant_id == variant_id)
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(Event.timestamp >= start_dt)
            except ValueError:
                return jsonify({'error': 'Invalid start_date format. Use ISO format.'}), 400
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(Event.timestamp <= end_dt)
            except ValueError:
                return jsonify({'error': 'Invalid end_date format. Use ISO format.'}), 400
        
        events = query.order_by(Event.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        result = []
        for event, assignment, variant in events.items:
            result.append({
                'id': event.id,
                'user_id': assignment.user_id,
                'variant_id': variant.id,
                'variant_name': variant.name,
                'event_type': event.event_type,
                'event_data': event.event_data,
                'revenue': event.revenue,
                'timestamp': event.timestamp.isoformat()
            })
        
        return jsonify({
            'experiment_id': experiment_id,
            'events': result,
            'pagination': {
                'page': events.page,
                'pages': events.pages,
                'per_page': events.per_page,
                'total': events.total
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing experiment events: {str(e)}")
        return jsonify({'error': str(e)}), 500

@events_bp.route('/user/<user_id>', methods=['GET'])
def get_user_events(user_id):
    """Get all events for a specific user"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        events_query = db.session.query(Event, Assignment, Experiment, Variant).join(
            Assignment, Event.assignment_id == Assignment.id
        ).join(
            Experiment, Assignment.experiment_id == Experiment.id
        ).join(
            Variant, Assignment.variant_id == Variant.id
        ).filter(
            Assignment.user_id == user_id
        )
        
        events = events_query.order_by(Event.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        result = []
        for event, assignment, experiment, variant in events.items:
            result.append({
                'event_id': event.id,
                'experiment_id': experiment.id,
                'experiment_name': experiment.name,
                'variant_id': variant.id,
                'variant_name': variant.name,
                'event_type': event.event_type,
                'event_data': event.event_data,
                'revenue': event.revenue,
                'timestamp': event.timestamp.isoformat()
            })
        
        return jsonify({
            'user_id': user_id,
            'events': result,
            'pagination': {
                'page': events.page,
                'pages': events.pages,
                'per_page': events.per_page,
                'total': events.total
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting user events: {str(e)}")
        return jsonify({'error': str(e)}), 500

@events_bp.route('/stats/<experiment_id>', methods=['GET'])
def get_event_stats(experiment_id):
    """Get event statistics for an experiment"""
    try:
        experiment = Experiment.query.get_or_404(experiment_id)
        
        # Get basic event counts
        event_counts = db.session.query(
            Event.event_type,
            db.func.count(Event.id).label('count'),
            db.func.sum(Event.revenue).label('total_revenue')
        ).join(
            Assignment, Event.assignment_id == Assignment.id
        ).filter(
            Assignment.experiment_id == experiment_id
        ).group_by(Event.event_type).all()
        
        # Get events by variant
        variant_stats = db.session.query(
            Variant.id,
            Variant.name,
            Event.event_type,
            db.func.count(Event.id).label('count'),
            db.func.sum(Event.revenue).label('revenue')
        ).join(
            Assignment, Assignment.variant_id == Variant.id
        ).join(
            Event, Event.assignment_id == Assignment.id
        ).filter(
            Assignment.experiment_id == experiment_id
        ).group_by(
            Variant.id, Variant.name, Event.event_type
        ).all()
        
        # Get timeline (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        daily_events = db.session.query(
            db.func.date(Event.timestamp).label('date'),
            Event.event_type,
            db.func.count(Event.id).label('count')
        ).join(
            Assignment, Event.assignment_id == Assignment.id
        ).filter(
            Assignment.experiment_id == experiment_id,
            Event.timestamp >= seven_days_ago
        ).group_by(
            db.func.date(Event.timestamp),
            Event.event_type
        ).order_by('date').all()
        
        # Format results
        event_summary = {}
        total_revenue = 0
        
        for event_count in event_counts:
            event_summary[event_count.event_type] = {
                'count': event_count.count,
                'total_revenue': float(event_count.total_revenue or 0)
            }
            total_revenue += float(event_count.total_revenue or 0)
        
        # Format variant stats
        variants = {}
        for stat in variant_stats:
            if stat.id not in variants:
                variants[stat.id] = {
                    'variant_name': stat.name,
                    'events': {}
                }
            
            variants[stat.id]['events'][stat.event_type] = {
                'count': stat.count,
                'revenue': float(stat.revenue or 0)
            }
        
        # Format timeline
        timeline = {}
        for day in daily_events:
            date_str = day.date.isoformat()
            if date_str not in timeline:
                timeline[date_str] = {}
            timeline[date_str][day.event_type] = day.count
        
        return jsonify({
            'experiment_id': experiment_id,
            'experiment_name': experiment.name,
            'event_summary': event_summary,
            'total_revenue': total_revenue,
            'variants': variants,
            'timeline': timeline,
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting event stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@events_bp.route('/<event_id>', methods=['GET'])
def get_event(event_id):
    """Get detailed information about a specific event"""
    try:
        event_details = db.session.query(Event, Assignment, Experiment, Variant).join(
            Assignment, Event.assignment_id == Assignment.id
        ).join(
            Experiment, Assignment.experiment_id == Experiment.id
        ).join(
            Variant, Assignment.variant_id == Variant.id
        ).filter(Event.id == event_id).first()
        
        if not event_details:
            return jsonify({'error': 'Event not found'}), 404
        
        event, assignment, experiment, variant = event_details
        
        return jsonify({
            'id': event.id,
            'user_id': assignment.user_id,
            'experiment': {
                'id': experiment.id,
                'name': experiment.name,
                'experiment_type': experiment.experiment_type
            },
            'variant': {
                'id': variant.id,
                'name': variant.name,
                'variant_type': variant.variant_type
            },
            'event_type': event.event_type,
            'event_data': event.event_data,
            'revenue': event.revenue,
            'timestamp': event.timestamp.isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting event: {str(e)}")
        return jsonify({'error': str(e)}), 500

@events_bp.route('/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    """Delete a specific event (for data correction purposes)"""
    try:
        event = Event.query.get_or_404(event_id)
        
        # Get assignment to check experiment status
        assignment = Assignment.query.get(event.assignment_id)
        experiment = Experiment.query.get(assignment.experiment_id)
        
        if experiment.status == 'running':
            return jsonify({
                'error': 'Cannot delete events while experiment is running'
            }), 400
        
        db.session.delete(event)
        db.session.commit()
        
        return jsonify({
            'message': 'Event deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting event: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
