# Eurorack Synthesizer Patch Idea Generator

A web application that generates eurorack synthesizer patch ideas based on your ModularGrid rack. The application allows you to submit a ModularGrid rack URL, looks up manuals for all modules in the rack, and scrapes forums such as Reddit and ModWiggler to generate interesting patch ideas using those modules.

## Features

- Submit a ModularGrid rack URL to import your modules
- Generate patch ideas based on your modules and a text prompt
- View detailed patch connections with explanations
- Get suggestions for knob settings with visual representations
- Access information from module manuals and forum discussions
- Cache module information to minimize network calls

## User Flow

1. **Submit ModularGrid Rack**: The user enters a ModularGrid URL (e.g., https://www.modulargrid.net/e/racks/view/123456) in the submission form.

2. **Parse Rack**: The backend parses the URL, extracts the rack ID, and fetches information about all modules in the rack. This information is stored in the database for future use.

3. **Enter Patch Prompt**: The user enters a text prompt describing the type of patch they want to create (e.g., "ambient drone with slowly evolving textures").

4. **Generate Patch**: The backend analyzes the modules in the rack and the user's prompt to determine the patch type and generate appropriate connections and knob settings.

5. **View Results**: The user sees a detailed patch idea with:
   - Module roles (which module serves what purpose in the patch)
   - Patch connections (which outputs connect to which inputs)
   - Knob settings (recommended positions for various controls)
   - Sources (references to manuals and forum discussions)

6. **Implement Patch**: The user can follow the suggested connections and settings to implement the patch on their physical eurorack system.

## Architecture

The application consists of three main components:

1. **Frontend**: React application with vintage synthesizer-inspired design
2. **Backend**: Python Flask API with various services
3. **Database**: PostgreSQL database for storing module information and patch ideas

### Backend Components

- **ModularGrid Parser**: Extracts module information from ModularGrid rack URLs
- **Cache Manager**: Caches module manuals and forum data to minimize network calls
- **Patch Generator**: Generates patch ideas based on available modules and user prompts
- **API Endpoints**: Provides data to the frontend

### Forum Scraping Functionality

The application includes functionality to search Reddit and ModWiggler for useful patch ideas:

1. **Data Collection**: When a module is first encountered, the system searches Reddit and ModWiggler for discussions about that module.

2. **Content Analysis**: The system analyzes forum posts to identify:
   - Patch connection suggestions
   - Recommended settings for knobs and controls
   - Common use cases for the module
   - Creative applications and techniques

3. **Relevance Scoring**: Each forum post is assigned a relevance score based on how useful it is for patch creation.

4. **Caching Mechanism**: Forum data is cached in the database to minimize network calls:
   - Data is stored in the `forum_sources` table
   - Each entry includes source type, URL, title, content, and relevance score
   - Data is refreshed after 7 days to ensure up-to-date information

5. **Integration with Patch Generation**: When generating patch ideas, the system incorporates insights from forum discussions:
   - Connections are suggested based on popular forum recommendations
   - Knob settings are informed by user experiences shared in forums
   - Sources are cited in the patch idea output

### Frontend Components

- **Rack Submission Form**: Allows users to submit ModularGrid rack URLs
- **Patch Display**: Shows generated patch ideas with connections and knob settings
- **Interactive Knobs**: Visual representation of suggested knob settings

## Code Structure

```
europatch/
├── backend/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   ├── modulargrid_parser.py
│   │   ├── patch_generator.py
│   │   ├── cache_manager.py
│   │   └── init_db.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── entrypoint.sh
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   └── Header.js
│   │   │   └── Knob.js
│   │   ├── pages/
│   │   │   └── Home.js
│   │   ├── App.js
│   │   ├── index.js
│   │   └── index.css
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── schema.sql
```

## Installation and Setup

The application is designed to be run with Docker Compose:

```bash
docker-compose up
```

This will start the frontend, backend, and database services. The frontend will be available at http://localhost:3000 and the backend API at http://localhost:5001.

## API Endpoints

- `GET /api/health`: Health check endpoint
- `GET /api/modules`: Get all modules
- `GET /api/modules/<id>`: Get a specific module
- `GET /api/modules/<id>/manual`: Get manual content for a module
- `GET /api/modules/<id>/forum-data`: Get forum data for a module
- `POST /api/parse-rack`: Parse a ModularGrid rack URL
- `GET /api/racks`: Get all user racks
- `GET /api/racks/<id>`: Get a specific rack
- `POST /api/generate-patch`: Generate a patch idea
- `GET /api/patch-ideas`: Get all patch ideas
- `GET /api/patch-ideas/<id>`: Get a specific patch idea

## Implementation Details

### ModularGrid Parser

The ModularGrid parser extracts module information from ModularGrid rack URLs. It uses web scraping techniques to extract module names, manufacturers, and other details from the ModularGrid website.

```python
def parse_url(self, url):
    """
    Parse a ModularGrid rack URL and extract module information.
    
    Args:
        url (str): ModularGrid rack URL
        
    Returns:
        dict: Rack information including modules
    """
    logger.info(f"Parsing ModularGrid URL: {url}")
    
    # Extract rack ID from URL
    rack_id_match = re.search(r'/racks/view/(\d+)', url)
    if not rack_id_match:
        raise ValueError("Invalid ModularGrid URL format. Expected format: https://www.modulargrid.net/e/racks/view/123456")
    
    rack_id = rack_id_match.group(1)
    logger.info(f"Extracted rack ID: {rack_id}")
    
    # Check if rack already exists in database
    existing_rack = UserRack.query.filter_by(modulargrid_id=rack_id).first()
    if existing_rack:
        logger.info(f"Rack {rack_id} already exists in database, returning cached data")
        return {
            "rack_id": existing_rack.id,
            "modulargrid_id": existing_rack.modulargrid_id,
            "rack_name": existing_rack.rack_name,
            "modules": [rm.module.to_dict() for rm in existing_rack.modules]
        }
```

### Patch Generator

The patch generator creates patch ideas based on available modules and user prompts. It analyzes the modules in the rack, determines their roles in the patch, and generates connections and control settings.

```python
def generate_patch(self, modules, prompt):
    """
    Generate a patch idea based on available modules and user prompt.
    
    Args:
        modules (list): List of module IDs or module objects
        prompt (str): User prompt describing desired patch
        
    Returns:
        dict: Generated patch idea
    """
    logger.info(f"Generating patch idea for prompt: {prompt}")
    
    # Determine patch type from prompt
    patch_type = self._determine_patch_type(prompt)
    logger.info(f"Determined patch type: {patch_type}")
    
    # Get module objects if IDs were provided
    module_objects = []
    for module in modules:
        if isinstance(module, int):
            module_obj = Module.query.get(module)
            if module_obj:
                module_objects.append(module_obj)
```

### Cache Manager

The cache manager handles caching of module manuals and forum data to minimize network calls. It stores the data in the database and provides methods to retrieve it.

```python
def get_manual_content(self, module_id, manual_url, force_refresh=False):
    """
    Get manual content for a module, either from cache or by fetching from URL.
    
    Args:
        module_id (int): ID of the module
        manual_url (str): URL of the manual
        force_refresh (bool): Whether to force refresh the cache
        
    Returns:
        str: Manual content
    """
    # Check if manual content exists in database
    module = Module.query.get(module_id)
    
    # If content exists in database and is not expired, return it
    if module.manual_content and module.manual_last_updated and not force_refresh:
        # Check if manual was updated within the last 30 days
        if module.manual_last_updated > datetime.utcnow() - timedelta(days=30):
            logger.info(f"Using cached manual content from database for module {module_id}")
            return module.manual_content
```

## Frontend Components

The frontend is built with React and styled-components, featuring a vintage synthesizer design language with warm, vintage colors, wood-like textures, and skeuomorphic controls.

### Home Page

The Home page contains the ModularGrid URL submission form and displays the generated patch ideas.

```jsx
const Home = () => {
  const [modulargridUrl, setModulargridUrl] = useState('');
  const [patchPrompt, setPatchPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [patchResult, setPatchResult] = useState(null);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!modulargridUrl) return;
    
    setLoading(true);
    setPatchResult(null);
    
    try {
      // API call to generate patch
      // ...
    } catch (error) {
      console.error("Error generating patch:", error);
      setLoading(false);
    }
  };
```

### Knob Component

The Knob component provides an interactive, skeuomorphic representation of module knobs.

```jsx
export const Knob = ({
  value = 0,
  min = 0,
  max = 100,
  size = 60,
  thickness = 0.2,
  color = '#f5f5f5',
  backgroundColor = '#333',
  onChange,
  name
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [startY, setStartY] = useState(0);
  const [startValue, setStartValue] = useState(value);
  
  // Calculate rotation based on value
  const minAngle = -150;
  const maxAngle = 150;
  const angleRange = maxAngle - minAngle;
  const valueRange = max - min;
  const rotation = minAngle + (value - min) / valueRange * angleRange;
```

## Database Schema

The database schema includes tables for modules, connections, controls, patch ideas, and user racks. The schema is designed to efficiently store and retrieve module information and patch ideas.

```sql
-- Module Table
CREATE TABLE modules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    manufacturer VARCHAR(255) NOT NULL,
    hp_width INTEGER,
    module_type VARCHAR(100),
    description TEXT,
    manual_url VARCHAR(255),
    manual_content TEXT,
    manual_last_updated TIMESTAMP,
    image_url VARCHAR(255),
    modulargrid_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Conclusion

The Eurorack Synthesizer Patch Idea Generator is a comprehensive web application that helps eurorack enthusiasts discover new patch ideas for their modular synthesizers. By leveraging module manuals and forum discussions, it provides detailed patch connections and knob settings tailored to the user's specific modules and preferences.
