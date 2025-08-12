# ShopifyLLM Unified Dashboard Setup and Requirements

## Required Python Packages
Flask==2.3.3
Flask-CORS==4.0.0
Flask-SQLAlchemy==3.0.5
SQLAlchemy==2.0.21
python-dotenv==1.0.0
requests==2.31.0
numpy==1.24.3
scipy==1.11.3
pandas==2.1.1
transformers==4.34.0
torch==2.0.1
Pillow==10.0.1
shopify-python-api==12.0.0

## Installation Instructions

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in .env file:
```
SHOPIFY_SHOP_DOMAIN=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=your-admin-api-access-token
STORE_CREATION_MODE=demo  # or 'real' for live stores
FLASK_SECRET_KEY=your-secret-key-change-this
```

3. Run the unified dashboard:
```bash
python app.py
```

4. Access the dashboard:
- Main Dashboard: http://localhost:5000/dashboard
- Store Creation: http://localhost:5000/
- A/B Testing API: http://localhost:5000/api/experiments

## Features

### 🏪 Store Creation
- AI-powered store generation from text prompts
- Automatic product creation with descriptions and images
- Real-time progress tracking
- Demo and live store modes

### 🧪 A/B Testing Engine
- Statistical significance testing with Wilson confidence intervals
- Automatic variant generation for product descriptions, titles, and CTAs
- Real-time assignment and event tracking
- Automated winner publishing

### 📊 Analytics
- Comprehensive dashboard with key metrics
- Conversion funnel analysis
- Performance charts and trends
- Statistical analysis results

### 🛍️ Product Management
- Live product editing with AI assistance
- Bulk product operations
- Price synchronization
- Image generation and management

## API Endpoints

### Store Creation
- POST /api/create-store-with-ab - Create store with A/B testing
- GET /api/job-status/<job_id> - Track creation progress
- GET /api/recent-stores - List recent stores

### A/B Testing
- POST /api/experiments - Create new experiment
- GET /api/experiments - List experiments
- POST /api/experiments/<id>/start - Start experiment
- POST /api/variants/generate - Generate AI variants
- POST /api/assignments/assign - Assign user to variant
- POST /api/events - Track conversion events

### Analytics
- GET /api/dashboard-stats - Dashboard statistics
- GET /api/experiments/<id>/results - Experiment results
- GET /api/assignments/stats/<id> - Assignment statistics

## Architecture

```
ShopifyLLM/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── services/              # Core business logic
│   ├── stats.py          # Statistical analysis
│   ├── assign.py         # User assignment
│   └── llm_variants.py   # AI variant generation
├── routes/               # API endpoints
│   ├── experiments.py   # Experiment management
│   ├── variants.py      # Variant operations
│   ├── assignments.py   # Assignment tracking
│   └── events.py        # Event tracking
├── templates/           # HTML templates
│   └── dashboard.html   # Unified dashboard
├── static/             # Static assets
│   └── js/dashboard.js # Dashboard JavaScript
└── theme_extension/    # Shopify theme integration
    └── ab_client.js    # Client-side A/B testing
```

## Production Deployment

1. Set environment variables for production
2. Use PostgreSQL instead of SQLite for database
3. Configure Redis for session management
4. Set up proper logging and monitoring
5. Use gunicorn or uwsgi for production server
6. Configure SSL certificates
7. Set up automated backups

## Integration with Shopify Themes

Add the A/B testing client to your theme:

```html
<!-- Add to theme.liquid before closing </body> tag -->
<script src="/theme_extension/ab_client.js"></script>
<script>
// Test product descriptions
shopifyAB.testProductDescription('experiment-id-here');

// Test CTA buttons
shopifyAB.testCTAButton('experiment-id-here');

// Track purchases on thank you page
if (Shopify.checkout) {
  shopifyAB.onPurchase('experiment-id-here', Shopify.checkout.total_price);
}
</script>
```

## Support

For issues and questions:
1. Check the dashboard logs at /api/health
2. Verify Shopify API credentials
3. Ensure database is properly initialized
4. Check browser console for JavaScript errors
