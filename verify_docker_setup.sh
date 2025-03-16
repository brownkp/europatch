#!/bin/bash

# Verify Docker and Docker Compose are installed
echo "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi
echo "Docker is installed."

echo "Checking Docker Compose installation..."
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi
echo "Docker Compose is installed."

# Check if the containers are already running
echo "Checking if containers are already running..."
if docker ps | grep -q "europatch"; then
    echo "EuroPatch containers are already running. Stopping them..."
    docker-compose down
fi

# Start the containers
echo "Starting EuroPatch containers..."
docker-compose up -d

# Wait for containers to be ready
echo "Waiting for containers to be ready..."
sleep 10

# Check if all containers are running
echo "Verifying containers are running..."
if ! docker ps | grep -q "europatch_backend"; then
    echo "Backend container is not running."
    docker-compose logs backend
    exit 1
fi

if ! docker ps | grep -q "europatch_frontend"; then
    echo "Frontend container is not running."
    docker-compose logs frontend
    exit 1
fi

if ! docker ps | grep -q "europatch_db"; then
    echo "Database container is not running."
    docker-compose logs db
    exit 1
fi

echo "All containers are running."

# Check if the services are accessible
echo "Checking if backend API is accessible..."
curl -s http://localhost:5001/api/modules > /dev/null
if [ $? -ne 0 ]; then
    echo "Backend API is not accessible."
    docker-compose logs backend
    exit 1
fi
echo "Backend API is accessible."

echo "Checking if frontend is accessible..."
curl -s http://localhost:3000 > /dev/null
if [ $? -ne 0 ]; then
    echo "Frontend is not accessible."
    docker-compose logs frontend
    exit 1
fi
echo "Frontend is accessible."

echo "All components are operational!"
echo "You can access the application at: http://localhost:3000"

# Keep the containers running in the background
echo "The application is now running in the background."
echo "To stop it, run: docker-compose down"
