"""
Script to initialize the database with tables.
"""
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from src.models import db

def create_app():
    app = Flask(__name__)
    # Configure database - use SQLite instead of PostgreSQL
    # Store the database file in a persistent volume
    sqlite_path = os.path.join('/app', 'database', 'europatch.db')
    os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{sqlite_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def init_db():
    """Initialize the database with tables."""
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
