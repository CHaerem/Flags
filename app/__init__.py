from flask import Flask
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    
    # Configure CORS to allow access from any origin
    CORS(app,
         resources={r"/change-flag": {"origins": "*"}},
         methods=["POST", "OPTIONS"],
         allow_headers=["Content-Type"],
         supports_credentials=False)
    
    # Import routes and register blueprint
    from app.routes import main
    app.register_blueprint(main)
    
    return app