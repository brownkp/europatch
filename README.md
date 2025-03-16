# EuroPatch - Eurorack Synthesizer Patch Idea Generator

EuroPatch is a web application that generates patch ideas for Eurorack synthesizers based on your ModularGrid rack and creative prompts. It analyzes your modules, looks up manuals, and scrapes forum discussions to provide intelligent patching suggestions.

## Features

- Submit your ModularGrid rack URL to analyze your available modules
- Generate patch ideas based on text prompts (ambient, generative, percussion, etc.)
- Get detailed connection suggestions with explanations
- Receive knob and macro controller setting recommendations
- View source citations from forums like Reddit and ModWiggler
- Cached module data and forum information for fast responses

## Technology Stack

- **Frontend**: React.js with styled-components
- **Backend**: Flask (Python) with Poetry for dependency management
- **Database**: PostgreSQL for module and patch data storage
- **Deployment**: Docker and Docker Compose

## Getting Started

### Prerequisites

- Docker and Docker Compose installed on your system
- Git for cloning the repository

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/brownkp/europatch.git
   cd europatch
   ```

2. Start the application using Docker Compose:
   ```
   docker-compose up
   ```

3. Access the application in your browser:
   ```
   http://localhost:3000
   ```

## Usage

1. Enter your ModularGrid rack URL (e.g., https://www.modulargrid.net/e/racks/view/123456)
2. Provide a description of the type of patch you want to create
3. Adjust the complexity level if desired
4. Click "Generate Patch Ideas"
5. Review the suggested patch connections, knob settings, and explanations
6. Implement the patch on your physical Eurorack system

## Development

### Project Structure

```
europatch/
├── backend/             # Python Flask backend
│   ├── src/             # Source code
│   │   ├── api/         # API routes and app configuration
│   │   ├── models/      # Database models
│   │   ├── services/    # Business logic services
│   │   └── utils/       # Utility functions
│   ├── pyproject.toml   # Poetry dependency management
│   └── Dockerfile       # Backend container configuration
├── frontend/            # React.js frontend
│   ├── src/             # Source code
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   └── styles/      # CSS styles
│   ├── package.json     # npm dependencies
│   └── Dockerfile       # Frontend container configuration
├── docker-compose.yml   # Multi-container configuration
└── schema.sql           # Database schema
```

### Running for Development

The same `docker-compose up` command can be used for development. The application uses volume mounting to enable hot reloading of both frontend and backend code.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to ModularGrid for their excellent Eurorack planning tool
- Thanks to the Eurorack community for sharing their patching knowledge
