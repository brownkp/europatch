#!/bin/bash

# Create cache directories
mkdir -p /app/cache/manuals
mkdir -p /app/cache/forums

# Initialize the database
python -m src.init_db

# Start the Flask application
gunicorn --bind 0.0.0.0:5001 "src:create_app()"
