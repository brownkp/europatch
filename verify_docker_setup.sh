#!/bin/bash

# This script verifies the Docker setup for the Eurorack Patch Generator

echo "Verifying Docker setup..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker before proceeding."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose before proceeding."
    exit 1
fi

# Verify directory structure
echo "Checking directory structure..."
MISSING_FILES=0

# Check backend files
if [ ! -f "./backend/app.py" ]; then
    echo "Missing: backend/app.py"
    MISSING_FILES=$((MISSING_FILES+1))
fi

if [ ! -f "./backend/models.py" ]; then
    echo "Missing: backend/models.py"
    MISSING_FILES=$((MISSING_FILES+1))
fi

if [ ! -f "./backend/Dockerfile" ]; then
    echo "Missing: backend/Dockerfile"
    MISSING_FILES=$((MISSING_FILES+1))
fi

if [ ! -f "./backend/requirements.txt" ]; then
    echo "Missing: backend/requirements.txt"
    MISSING_FILES=$((MISSING_FILES+1))
fi

if [ ! -f "./backend/services/modulargrid_parser.py" ]; then
    echo "Missing: backend/services/modulargrid_parser.py"
    MISSING_FILES=$((MISSING_FILES+1))
fi

if [ ! -f "./backend/services/patch_generator.py" ]; then
    echo "Missing: backend/services/patch_generator.py"
    MISSING_FILES=$((MISSING_FILES+1))
fi

# Check frontend files
if [ ! -f "./frontend/Dockerfile" ]; then
    echo "Missing: frontend/Dockerfile"
    MISSING_FILES=$((MISSING_FILES+1))
fi

if [ ! -f "./frontend/package.json" ]; then
    echo "Missing: frontend/package.json"
    MISSING_FILES=$((MISSING_FILES+1))
fi

# Check docker-compose.yml
if [ ! -f "./docker-compose.yml" ]; then
    echo "Missing: docker-compose.yml"
    MISSING_FILES=$((MISSING_FILES+1))
fi

if [ $MISSING_FILES -gt 0 ]; then
    echo "Found $MISSING_FILES missing files. Please fix these issues before proceeding."
    exit 1
fi

echo "All required files are present."
echo "Docker setup verification complete. The application is ready to be started with './start.sh'."
