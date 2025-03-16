# Eurorack Patch Generator

A web application that generates Eurorack synthesizer patch ideas based on ModularGrid racks. The application allows users to submit a ModularGrid rack, looks up manuals for all modules in the rack, and scrapes forums to generate interesting patch ideas.

## Features

- **ModularGrid Integration**: Submit your ModularGrid rack URL to analyze available modules
- **Intelligent Patch Generation**: Create contextually relevant patch ideas based on your modules
- **Detailed Connection Explanations**: Understand why connections are needed and how they work
- **Knob Setting Recommendations**: Get optimal settings for each module
- **Moog-Inspired UI**: Beautiful vintage-inspired user interface
- **Local Database Caching**: Minimizes network calls by caching module information

## Quick Start

1. Make sure you have Docker and Docker Compose installed
2. Clone this repository
3. Run the start script:

```bash
./start.sh
```

This will start all necessary services:
- PostgreSQL database
- Flask backend API
- React frontend application

## Accessing the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:5001/api

## Project Structure

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
├── start.sh
├── verify_docker_setup.sh
└── DOCKER_SETUP.md
```

## Development

The Docker setup includes volume mounts for both frontend and backend code, allowing you to make changes to the code and see them reflected immediately without rebuilding the containers.

## API Endpoints

- `POST /api/rack/parse`: Parse a ModularGrid rack URL
- `GET /api/rack/{rack_id}`: Get details about a parsed rack
- `GET /api/module/{module_id}`: Get details about a specific module
- `POST /api/patch/generate`: Generate patch ideas based on a rack and prompt
- `GET /api/module/{module_id}/discussions`: Get forum discussions about a module

## Technologies Used

- **Frontend**: React.js with styled-components
- **Backend**: Python/Flask
- **Database**: PostgreSQL
- **Containerization**: Docker & Docker Compose

## Detailed Documentation

For more detailed information about the Docker setup, please refer to the [Docker Setup Documentation](DOCKER_SETUP.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
