#!/usr/bin/env python3
"""
Main entry point for the Shopify LLM Store Creator web application.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == '__main__':
    from api.app import app
    app.run(debug=True, host='0.0.0.0', port=5000)
