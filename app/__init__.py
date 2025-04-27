from flask import Flask, current_app
from flask_cors import CORS
import os
import sys

def create_app(config=None):
    app = Flask(__name__)
    
    # Configure CORS to allow access from any origin
    CORS(app,
         resources={r"/change-flag": {"origins": "*"}},
         methods=["POST", "OPTIONS"],
         allow_headers=["Content-Type"],
         supports_credentials=False)
    
    # Store whether mock mode is active
    app.config['MOCK_MODE'] = '--mock' in sys.argv
    
    # Set up application context
    @app.context_processor
    def inject_mock_status():
        # Use the stored mock mode value
        return {'is_mock_display': app.config['MOCK_MODE']}
    
    # Import routes and register blueprint
    from app.routes import main
    app.register_blueprint(main)
    
    return app