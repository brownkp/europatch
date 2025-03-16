# Eurorack Patch Generator - Docker Setup Instructions

This document provides instructions for setting up and running the Eurorack Patch Generator application using Docker.

## Prerequisites

- Docker and Docker Compose installed on your system
- Git (optional, for cloning the repository)

## Directory Structure

```
eurorack-patch-generator/
├── backend/
│   ├── services/
│   │   ├── __init__.py
│   │   ├── modulargrid_parser.py
│   │   └── patch_generator.py
│   ├── __init__.py
│   ├── app.py
│   ├── Dockerfile
│   ├── models.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── styles/
│   │   ├── App.js
│   │   └── index.js
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── start.sh
```

## Quick Start

1. Clone or download the repository
2. Navigate to the project directory
3. Run the start script:

```bash
./start.sh
```

This will start all the necessary services:
- PostgreSQL database
- Flask backend API
- React frontend application

## Accessing the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:5001/api

## Development

The Docker setup includes volume mounts for both frontend and backend code, allowing you to make changes to the code and see them reflected immediately without rebuilding the containers.

## Troubleshooting

If you encounter any issues:

1. Check that all required ports (3000, 5001, 5432) are available
2. Ensure Docker and Docker Compose are properly installed
3. Try rebuilding the containers with:

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

## Manual Setup (without Docker)

If you prefer to run the application without Docker:

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
flask run
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

Note: You'll need to set up a PostgreSQL database separately and configure the connection string in the backend.
