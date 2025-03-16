-- Eurorack Patch Generator Database Schema

-- Modules Table
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

CREATE INDEX idx_modules_name ON modules(name);
CREATE INDEX idx_modules_manufacturer ON modules(manufacturer);
CREATE INDEX idx_modules_type ON modules(module_type);
CREATE INDEX idx_modules_name_manufacturer ON modules(name, manufacturer);

-- Module Connections Table
CREATE TABLE module_connections (
    id SERIAL PRIMARY KEY,
    module_id INTEGER REFERENCES modules(id) ON DELETE CASCADE,
    connection_type VARCHAR(50) NOT NULL, -- 'input', 'output'
    connection_name VARCHAR(100) NOT NULL,
    description TEXT,
    voltage_range VARCHAR(50), -- e.g., '0-5V', '±10V'
    is_cv BOOLEAN DEFAULT FALSE,
    is_gate BOOLEAN DEFAULT FALSE,
    is_audio BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_connections_module_id ON module_connections(module_id);
CREATE INDEX idx_connections_type ON module_connections(connection_type);

-- Module Controls Table
CREATE TABLE module_controls (
    id SERIAL PRIMARY KEY,
    module_id INTEGER REFERENCES modules(id) ON DELETE CASCADE,
    control_type VARCHAR(50) NOT NULL, -- 'knob', 'switch', 'button', 'slider'
    control_name VARCHAR(100) NOT NULL,
    description TEXT,
    min_value FLOAT,
    max_value FLOAT,
    default_value FLOAT,
    is_attenuator BOOLEAN DEFAULT FALSE,
    is_attenuverter BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_controls_module_id ON module_controls(module_id);

-- Patch Ideas Table
CREATE TABLE patch_ideas (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    patch_type VARCHAR(100), -- e.g., 'ambient', 'generative', 'percussion'
    complexity INTEGER, -- 1-5 scale
    source_type VARCHAR(50), -- 'manual', 'reddit', 'modwiggler', 'generated'
    source_url VARCHAR(255),
    source_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_patch_ideas_type ON patch_ideas(patch_type);
CREATE INDEX idx_patch_ideas_complexity ON patch_ideas(complexity);
CREATE INDEX idx_patch_ideas_type_complexity ON patch_ideas(patch_type, complexity);

-- Patch Modules Table (Junction Table)
CREATE TABLE patch_modules (
    id SERIAL PRIMARY KEY,
    patch_id INTEGER REFERENCES patch_ideas(id) ON DELETE CASCADE,
    module_id INTEGER REFERENCES modules(id) ON DELETE CASCADE,
    importance INTEGER, -- 1-5 scale, how central the module is to the patch
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(patch_id, module_id)
);

CREATE INDEX idx_patch_modules_patch_id ON patch_modules(patch_id);
CREATE INDEX idx_patch_modules_module_id ON patch_modules(module_id);

-- Patch Connections Table
CREATE TABLE patch_connections (
    id SERIAL PRIMARY KEY,
    patch_id INTEGER REFERENCES patch_ideas(id) ON DELETE CASCADE,
    source_module_id INTEGER REFERENCES modules(id) ON DELETE CASCADE,
    source_connection_id INTEGER REFERENCES module_connections(id) ON DELETE CASCADE,
    target_module_id INTEGER REFERENCES modules(id) ON DELETE CASCADE,
    target_connection_id INTEGER REFERENCES module_connections(id) ON DELETE CASCADE,
    cable_color VARCHAR(50), -- for visualization
    description TEXT,
    importance INTEGER, -- 1-5 scale
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_patch_connections_patch_id ON patch_connections(patch_id);
CREATE INDEX idx_patch_connections_source ON patch_connections(source_module_id, source_connection_id);
CREATE INDEX idx_patch_connections_target ON patch_connections(target_module_id, target_connection_id);
CREATE INDEX idx_patch_connections_patch_importance ON patch_connections(patch_id, importance);

-- Patch Control Settings Table
CREATE TABLE patch_control_settings (
    id SERIAL PRIMARY KEY,
    patch_id INTEGER REFERENCES patch_ideas(id) ON DELETE CASCADE,
    module_id INTEGER REFERENCES modules(id) ON DELETE CASCADE,
    control_id INTEGER REFERENCES module_controls(id) ON DELETE CASCADE,
    value_numeric FLOAT,
    value_text VARCHAR(100), -- e.g., "3 o'clock", "fully clockwise"
    description TEXT,
    importance INTEGER, -- 1-5 scale
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_patch_settings_patch_id ON patch_control_settings(patch_id);
CREATE INDEX idx_patch_settings_module_control ON patch_control_settings(module_id, control_id);

-- User Racks Table
CREATE TABLE user_racks (
    id SERIAL PRIMARY KEY,
    modulargrid_url VARCHAR(255) NOT NULL,
    modulargrid_id VARCHAR(100),
    rack_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_racks_modulargrid_id ON user_racks(modulargrid_id);

-- Rack Modules Junction Table
CREATE TABLE rack_modules (
    id SERIAL PRIMARY KEY,
    rack_id INTEGER REFERENCES user_racks(id) ON DELETE CASCADE,
    module_id INTEGER REFERENCES modules(id) ON DELETE CASCADE,
    position_x INTEGER,
    position_y INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(rack_id, module_id, position_x, position_y)
);

CREATE INDEX idx_rack_modules_rack_id ON rack_modules(rack_id);

-- Forum Sources Table
CREATE TABLE forum_sources (
    id SERIAL PRIMARY KEY,
    source_type VARCHAR(50) NOT NULL, -- 'reddit', 'modwiggler', etc.
    url VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    content TEXT,
    module_id INTEGER REFERENCES modules(id),
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    relevance_score FLOAT, -- 0-1 scale
    
    UNIQUE(source_type, url)
);

CREATE INDEX idx_forum_sources_module_id ON forum_sources(module_id);
CREATE INDEX idx_forum_sources_relevance ON forum_sources(relevance_score);
CREATE INDEX idx_forum_sources_module_relevance ON forum_sources(module_id, relevance_score);
