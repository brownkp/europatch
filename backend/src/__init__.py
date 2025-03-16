"""
Entry point for the Flask application.
"""
import os
from flask import Flask
from flask_cors import CORS
from src.models import db
from src.routes import register_routes
from src.modulargrid_parser import ModularGridParser
from src.patch_generator import PatchGenerator

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/eurorack_patch_generator')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database with app
    db.init_app(app)
    
    # Initialize services
    modulargrid_parser = ModularGridParser()
    patch_generator = PatchGenerator()
    
    # Register routes
    register_routes(app, modulargrid_parser, patch_generator)
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)
