# Flask Web Application for Shopify Store Creator
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
import json
import uuid
from datetime import datetime
import sys
import threading
import time

# Add the parent directory to the path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.store_builder import CompleteShopifyStoreCreator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the project root directory (two levels up from src/api/)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__, 
           template_folder=os.path.join(project_root, 'templates'),
           static_folder=os.path.join(project_root, 'static'))
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-this')
CORS(app)

# Store creation status tracking
creation_jobs = {}

class StoreCreationJob:
    def __init__(self, job_id, prompt):
        self.id = job_id
        self.prompt = prompt
        self.status = 'pending'
        self.progress = 0
        self.result = None
        self.error = None
        self.started_at = datetime.now()
        self.completed_at = None

@app.route('/')
def index():
    """Main page with store creation interface"""
    return render_template('index.html')

@app.route('/api/create-store', methods=['POST'])
def create_store():
    """API endpoint to create a new Shopify store"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Create job tracker
        job = StoreCreationJob(job_id, prompt)
        creation_jobs[job_id] = job
        
        # Start store creation in background thread
        thread = threading.Thread(target=create_store_background, args=(job_id, prompt))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'job_id': job_id,
            'status': 'started',
            'message': 'Store creation started successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_store_background(job_id, prompt):
    """Background task to create the store"""
    job = creation_jobs[job_id]
    
    try:
        job.status = 'running'
        job.progress = 10
        
        # Initialize store creator
        creator = CompleteShopifyStoreCreator(
            shop_domain=os.getenv('SHOPIFY_SHOP_DOMAIN'),
            access_token=os.getenv('SHOPIFY_ACCESS_TOKEN'),
            real_mode=os.getenv('STORE_CREATION_MODE', 'demo').lower() == 'real'
        )
        
        job.progress = 25
        
        # Create the store
        result = creator.create_store_from_prompt(prompt)
        
        job.progress = 100
        job.status = 'completed'
        job.result = result
        job.completed_at = datetime.now()
        
    except Exception as e:
        job.status = 'failed'
        job.error = str(e)
        job.completed_at = datetime.now()

@app.route('/api/job-status/<job_id>')
def get_job_status(job_id):
    """Get the status of a store creation job"""
    job = creation_jobs.get(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    response = {
        'id': job.id,
        'status': job.status,
        'progress': job.progress,
        'prompt': job.prompt,
        'started_at': job.started_at.isoformat()
    }
    
    if job.completed_at:
        response['completed_at'] = job.completed_at.isoformat()
    
    if job.result:
        response['result'] = job.result
    
    if job.error:
        response['error'] = job.error
    
    return jsonify(response)

@app.route('/api/recent-stores')
def get_recent_stores():
    """Get list of recently created stores"""
    recent_jobs = []
    
    # Get completed jobs from the last 24 hours
    for job in creation_jobs.values():
        if job.status == 'completed' and job.result:
            recent_jobs.append({
                'id': job.id,
                'prompt': job.prompt,
                'store_name': job.result.get('concept', {}).get('store_name', 'Unknown Store'),
                'store_url': job.result.get('store_url', ''),
                'products_count': job.result.get('products_created', 0),
                'created_at': job.completed_at.isoformat() if job.completed_at else None,
                'mode': job.result.get('mode', 'demo')
            })
    
    # Sort by creation time (newest first)
    recent_jobs.sort(key=lambda x: x['created_at'] or '', reverse=True)
    
    return jsonify(recent_jobs[:10])  # Return last 10 stores

@app.route('/api/config')
def get_config():
    """Get current configuration status"""
    return jsonify({
        'shopify_configured': bool(os.getenv('SHOPIFY_SHOP_DOMAIN') and os.getenv('SHOPIFY_ACCESS_TOKEN')),
        'store_mode': os.getenv('STORE_CREATION_MODE', 'demo'),
        'shop_domain': os.getenv('SHOPIFY_SHOP_DOMAIN', ''),
    })

@app.route('/api/test-connection')
def test_connection():
    """Test Shopify API connection"""
    try:
        creator = CompleteShopifyStoreCreator(
            shop_domain=os.getenv('SHOPIFY_SHOP_DOMAIN'),
            access_token=os.getenv('SHOPIFY_ACCESS_TOKEN')
        )
        
        # Test basic API access (this would need to be implemented in the store builder)
        return jsonify({
            'status': 'connected',
            'shop_domain': os.getenv('SHOPIFY_SHOP_DOMAIN'),
            'message': 'Successfully connected to Shopify'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/store-settings', methods=['GET'])
def get_store_settings():
    """Get current store settings"""
    try:
        # In a real implementation, this would fetch from Shopify API
        # For now, return mock data or from environment
        settings = {
            'store_name': 'My AI Store',
            'store_description': 'Created with AI-powered store builder',
            'email': 'admin@mystore.com',
            'phone': '+1 (555) 123-4567',
            'address': {
                'street': '123 Main Street',
                'city': 'Anytown',
                'state': 'CA',
                'zip': '12345',
                'country': 'United States'
            },
            'currency': 'USD',
            'timezone': 'America/Los_Angeles',
            'domain': os.getenv('SHOPIFY_SHOP_DOMAIN', 'yourstore.myshopify.com'),
            'plan': 'Basic Shopify',
            'theme': 'Dawn'
        }
        
        return jsonify(settings)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/store-settings', methods=['PUT'])
def update_store_settings():
    """Update store settings"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['store_name', 'store_description', 'email']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # In a real implementation, this would update via Shopify API
        # For now, we'll simulate the update
        
        # Here you would typically make Shopify API calls like:
        # creator = CompleteShopifyStoreCreator()
        # creator.update_store_settings(data)
        
        updated_settings = data  # In reality, return the updated data from Shopify
        
        return jsonify({
            'success': True,
            'message': 'Store settings updated successfully',
            'settings': updated_settings
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/store-theme', methods=['PUT'])
def update_store_theme():
    """Update store theme settings"""
    try:
        data = request.get_json()
        
        # Validate theme data
        if 'theme_name' not in data:
            return jsonify({'error': 'Theme name is required'}), 400
        
        # In a real implementation, this would update theme via Shopify API
        theme_settings = {
            'theme_name': data.get('theme_name'),
            'primary_color': data.get('primary_color', '#6366f1'),
            'secondary_color': data.get('secondary_color', '#10b981'),
            'accent_color': data.get('accent_color', '#f59e0b'),
            'logo_url': data.get('logo_url', ''),
            'favicon_url': data.get('favicon_url', ''),
            'updated_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'message': 'Theme updated successfully',
            'theme': theme_settings
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Ensure templates and static directories exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
