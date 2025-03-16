from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
import json

# Import custom modules
from modulargrid_parser import ModularGridParser
from patch_generator import PatchGenerator

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/eurorack_patch_generator')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize services
modulargrid_parser = ModularGridParser()
patch_generator = PatchGenerator()

# Database models
class Module(db.Model):
    __tablename__ = 'modules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    manufacturer = db.Column(db.String(255), nullable=False)
    hp_width = db.Column(db.Integer)
    module_type = db.Column(db.String(100))
    description = db.Column(db.Text)
    manual_url = db.Column(db.String(255))
    manual_content = db.Column(db.Text)
    manual_last_updated = db.Column(db.DateTime)
    image_url = db.Column(db.String(255))
    modulargrid_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    connections = db.relationship('ModuleConnection', backref='module', lazy=True, cascade='all, delete-orphan')
    controls = db.relationship('ModuleControl', backref='module', lazy=True, cascade='all, delete-orphan')

class ModuleConnection(db.Model):
    __tablename__ = 'module_connections'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'), nullable=False)
    connection_type = db.Column(db.String(50), nullable=False)  # 'input', 'output'
    connection_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    voltage_range = db.Column(db.String(50))
    is_cv = db.Column(db.Boolean, default=False)
    is_gate = db.Column(db.Boolean, default=False)
    is_audio = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ModuleControl(db.Model):
    __tablename__ = 'module_controls'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'), nullable=False)
    control_type = db.Column(db.String(50), nullable=False)  # 'knob', 'switch', 'button', 'slider'
    control_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    min_value = db.Column(db.Float)
    max_value = db.Column(db.Float)
    default_value = db.Column(db.Float)
    is_attenuator = db.Column(db.Boolean, default=False)
    is_attenuverter = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserRack(db.Model):
    __tablename__ = 'user_racks'
    
    id = db.Column(db.Integer, primary_key=True)
    modulargrid_url = db.Column(db.String(255), nullable=False)
    modulargrid_id = db.Column(db.String(100))
    rack_name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    
    rack_modules = db.relationship('RackModule', backref='rack', lazy=True, cascade='all, delete-orphan')

class RackModule(db.Model):
    __tablename__ = 'rack_modules'
    
    id = db.Column(db.Integer, primary_key=True)
    rack_id = db.Column(db.Integer, db.ForeignKey('user_racks.id', ondelete='CASCADE'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'), nullable=False)
    position_x = db.Column(db.Integer)
    position_y = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    module = db.relationship('Module')
    
    __table_args__ = (
        db.UniqueConstraint('rack_id', 'module_id', 'position_x', 'position_y', name='uq_rack_module_position'),
    )

# Helper functions
def get_or_create_module(module_data):
    """Get existing module or create a new one"""
    module = Module.query.filter_by(
        name=module_data['name'],
        manufacturer=module_data['manufacturer']
    ).first()
    
    if module:
        # Update existing module
        for key, value in module_data.items():
            if hasattr(module, key) and key not in ['id', 'created_at']:
                setattr(module, key, value)
        module.updated_at = datetime.utcnow()
    else:
        # Create new module
        module = Module(**module_data)
        db.session.add(module)
    
    db.session.commit()
    return module

def get_or_create_rack(rack_data):
    """Get existing rack or create a new one"""
    rack = UserRack.query.filter_by(modulargrid_id=rack_data['rack_id']).first()
    
    if rack:
        # Update existing rack
        rack.last_accessed = datetime.utcnow()
    else:
        # Create new rack
        rack = UserRack(
            modulargrid_url=rack_data['modulargrid_url'],
            modulargrid_id=rack_data['rack_id'],
            rack_name=rack_data['rack_name']
        )
        db.session.add(rack)
    
    db.session.commit()
    return rack

# API Routes
@app.route('/api/rack/parse', methods=['POST'])
def parse_rack():
    """Parse a ModularGrid rack URL and extract module information"""
    data = request.json
    
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        # Parse rack URL
        rack_data = modulargrid_parser.parse_rack_url(data['url'])
        
        # Store rack in database
        rack = get_or_create_rack(rack_data)
        
        # Store modules in database
        modules = []
        for module_data in rack_data['modules']:
            module = get_or_create_module(module_data)
            
            # Create rack-module association
            rack_module = RackModule(
                rack_id=rack.id,
                module_id=module.id,
                position_x=module_data.get('position_x', 0),
                position_y=module_data.get('position_y', 0)
            )
            db.session.add(rack_module)
            
            # Add module to response
            modules.append({
                'id': module.id,
                'name': module.name,
                'manufacturer': module.manufacturer,
                'hp_width': module.hp_width,
                'module_type': module.module_type,
                'image_url': module.image_url,
                'position_x': module_data.get('position_x', 0),
                'position_y': module_data.get('position_y', 0)
            })
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'rack_id': rack.modulargrid_id,
            'rack_name': rack.rack_name,
            'modules': modules
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rack/<rack_id>', methods=['GET'])
def get_rack_details(rack_id):
    """Get detailed information about a previously parsed rack"""
    try:
        rack = UserRack.query.filter_by(modulargrid_id=rack_id).first()
        
        if not rack:
            return jsonify({'error': 'Rack not found'}), 404
        
        # Update last accessed timestamp
        rack.last_accessed = datetime.utcnow()
        db.session.commit()
        
        # Get modules in this rack
        modules = []
        for rack_module in rack.rack_modules:
            module = rack_module.module
            
            # Get module connections
            connections = []
            for conn in module.connections:
                connections.append({
                    'id': conn.id,
                    'type': conn.connection_type,
                    'name': conn.connection_name,
                    'description': conn.description,
                    'voltage_range': conn.voltage_range,
                    'is_cv': conn.is_cv,
                    'is_gate': conn.is_gate,
                    'is_audio': conn.is_audio
                })
            
            # Get module controls
            controls = []
            for ctrl in module.controls:
                controls.append({
                    'id': ctrl.id,
                    'type': ctrl.control_type,
                    'name': ctrl.control_name,
                    'description': ctrl.description,
                    'min_value': ctrl.min_value,
                    'max_value': ctrl.max_value,
                    'default_value': ctrl.default_value,
                    'is_attenuator': ctrl.is_attenuator,
                    'is_attenuverter': ctrl.is_attenuverter
                })
            
            modules.append({
                'id': module.id,
                'name': module.name,
                'manufacturer': module.manufacturer,
                'hp_width': module.hp_width,
                'module_type': module.module_type,
                'description': module.description,
                'image_url': module.image_url,
                'position_x': rack_module.position_x,
                'position_y': rack_module.position_y,
                'connections': connections,
                'controls': controls
            })
        
        return jsonify({
            'rack_id': rack.modulargrid_id,
            'rack_name': rack.rack_name,
            'modulargrid_url': rack.modulargrid_url,
            'modules': modules
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/patch/generate', methods=['POST'])
def generate_patch_ideas():
    """Generate patch ideas based on available modules and user prompt"""
    data = request.json
    
    if not data or 'rack_id' not in data or 'prompt' not in data:
        return jsonify({'error': 'Rack ID and prompt are required'}), 400
    
    try:
        # Get complexity and max results from request or use defaults
        complexity = data.get('complexity', 3)
        max_results = data.get('max_results', 3)
        
        # Generate patch ideas
        patch_ideas = patch_generator.generate_patch_ideas(
            data['rack_id'],
            data['prompt'],
            complexity,
            max_results
        )
        
        return jsonify({
            'success': True,
            'prompt': data['prompt'],
            'patch_ideas': patch_ideas
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/module/<int:module_id>', methods=['GET'])
def get_module_details(module_id):
    """Get detailed information about a specific module"""
    try:
        module = Module.query.get(module_id)
        
        if not module:
            return jsonify({'error': 'Module not found'}), 404
        
        # Get module connections
        connections = []
        for conn in module.connections:
            connections.append({
                'id': conn.id,
                'type': conn.connection_type,
                'name': conn.connection_name,
                'description': conn.description,
                'voltage_range': conn.voltage_range,
                'is_cv': conn.is_cv,
                'is_gate': conn.is_gate,
                'is_audio': conn.is_audio
            })
        
        # Get module controls
        controls = []
        for ctrl in module.controls:
            controls.append({
                'id': ctrl.id,
                'type': ctrl.control_type,
                'name': ctrl.control_name,
                'description': ctrl.description,
                'min_value': ctrl.min_value,
                'max_value': ctrl.max_value,
                'default_value': ctrl.default_value,
                'is_attenuator': ctrl.is_attenuator,
                'is_attenuverter': ctrl.is_attenuverter
            })
        
        return jsonify({
            'id': module.id,
            'name': module.name,
            'manufacturer': module.manufacturer,
            'hp_width': module.hp_width,
            'module_type': module.module_type,
            'description': module.description,
            'manual_url': module.manual_url,
            'image_url': module.image_url,
            'connections': connections,
            'controls': controls
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Run the application
if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5001, debug=True)
