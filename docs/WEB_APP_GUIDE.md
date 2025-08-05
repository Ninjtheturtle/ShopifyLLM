# AI Shopify Store Creator - Web Application Setup Guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
Create a `.env` file in the project root:

```env
# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here
FLASK_DEBUG=true

# Shopify Configuration (Optional - Demo mode works without these)
SHOPIFY_SHOP_DOMAIN=yourstore.myshopify.com
SHOPIFY_ACCESS_TOKEN=your-admin-api-token
STORE_CREATION_MODE=demo  # Change to 'real' for actual store creation

# AI Model Configuration (Optional)
OPENAI_API_KEY=your-openai-key  # If using OpenAI for enhanced descriptions
```

### 3. Run the Web Application
```bash
python app.py
```

The web app will be available at: http://localhost:5000

## 🎨 Features

### Beautiful Modern Interface
- **Dark theme** with gradient backgrounds and smooth animations
- **Responsive design** that works on desktop, tablet, and mobile
- **Real-time progress tracking** with animated progress bars
- **Toast notifications** for user feedback
- **Connection status indicator** showing Shopify configuration

### Smart Store Creation
- **Natural language prompts** - describe your store in plain English
- **AI-powered parsing** that understands products, quantities, specifications
- **Background processing** with real-time progress updates
- **Comprehensive results** showing store details, products, and links

### Recent Stores Dashboard
- **History tracking** of all created stores
- **Quick access** to previously created stores
- **Store metadata** including creation time, product count, and mode

## 🛠️ API Endpoints

### Store Creation
- `POST /api/create-store` - Create a new store from a prompt
- `GET /api/job-status/<job_id>` - Check store creation progress

### Management
- `GET /api/recent-stores` - Get list of recently created stores
- `GET /api/config` - Get current configuration status
- `GET /api/test-connection` - Test Shopify API connection

## 🔧 Configuration Modes

### Demo Mode (Default)
- **No Shopify credentials required**
- **Simulates store creation** with realistic data
- **Perfect for testing** and development
- **Shows all features** without actual API calls

### Real Mode
- **Requires Shopify credentials** (shop domain + access token)
- **Creates actual Shopify stores** with real products
- **Full API integration** with your Shopify account
- **Production-ready** store creation

## 📱 Mobile Responsive

The interface is fully responsive and provides an excellent experience on:
- **Desktop computers** - Full feature set with multi-column layouts
- **Tablets** - Optimized touch interface with adapted layouts
- **Mobile phones** - Streamlined interface with stacked components

## 🎯 Example Prompts

Try these example prompts to see the AI in action:

1. **Specific Product with Inventory:**
   ```
   Create a store that sells premium water bottles with 30oz capacity, make sure there's 70 in stock
   ```

2. **Product Category:**
   ```
   I want a store selling speed cubes for speedcubing competitions
   ```

3. **Multi-Product Store:**
   ```
   Build a store for eco-friendly yoga mats and meditation accessories
   ```

4. **Detailed Specifications:**
   ```
   Create a store that sells stainless steel water bottles in blue and silver colors, 20oz and 30oz sizes
   ```

## 🔐 Security Features

- **Secret key protection** for session management
- **CORS configuration** for secure API access
- **Input validation** to prevent malicious requests
- **Error handling** with secure error messages

## 🚦 Getting Started Steps

1. **Clone/Download** the project files
2. **Install dependencies** with `pip install -r requirements.txt`
3. **Create .env file** with your configuration (demo mode works without Shopify)
4. **Run the app** with `python app.py`
5. **Open browser** to http://localhost:5000
6. **Start creating stores** with natural language prompts!

## 🎨 Customization

The interface uses CSS custom properties (variables) for easy theming:
- Colors, fonts, spacing can be modified in `static/css/style.css`
- Component behavior can be customized in `static/js/main.js`
- Backend logic can be extended in `app.py`

## 📊 Monitoring & Debugging

- **Real-time job tracking** shows progress of store creation
- **Detailed error messages** help with troubleshooting
- **Connection status** indicates Shopify API health
- **Console logging** for development debugging

Start creating amazing Shopify stores with just natural language descriptions!
