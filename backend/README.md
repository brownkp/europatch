# EuroPatch Backend

Backend service for the EuroPatch eurorack patch generation application.

## Features

- ModularGrid rack parsing and module extraction
- Patch idea generation based on available modules
- Database storage for modules, racks, and patch ideas
- API endpoints for frontend integration

## Setup with Poetry

This project uses Poetry for dependency management.

### Installation

1. Install Poetry (if not already installed):
   ```
   pip install poetry
   ```

2. Install dependencies:
   ```
   poetry install
   ```

3. Activate the virtual environment:
   ```
   poetry shell
   ```

### Running the Application

Start the backend server:
```
poetry run start
```

Initialize the database:
```
poetry run init-db
```

## API Endpoints

- `/api/health` - Health check endpoint
- `/api/parse-rack` - Parse a ModularGrid rack URL
- `/api/generate-patch` - Generate a patch idea based on modules
- `/api/modules` - Get all modules
- `/api/racks` - Get all user racks

## Development

Run tests:
```
poetry run pytest
```
