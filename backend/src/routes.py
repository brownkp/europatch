"""
API routes for the Eurorack Patch Generator application.
"""
from flask import Blueprint, request, jsonify
import os
from datetime import datetime
import logging
from src.models import db, Module, ModuleConnection, ModuleControl, PatchIdea, UserRack, RackModule
from src.cache_manager import CacheManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_routes(app, modulargrid_parser, patch_generator):
    """Register API routes with the Flask app."""
    api = Blueprint('api', __name__)
    cache_manager = CacheManager()
    
    @api.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            "status": "ok", 
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        })
    
    @api.route('/modules', methods=['GET'])
    def get_modules():
        """Get all modules."""
        try:
            modules = Module.query.all()
            return jsonify([module.to_dict() for module in modules])
        except Exception as e:
            logger.error(f"Error getting modules: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @api.route('/modules/<int:module_id>', methods=['GET'])
    def get_module(module_id):
        """Get a specific module by ID."""
        try:
            module = Module.query.get(module_id)
            if not module:
                return jsonify({"error": f"Module with ID {module_id} not found"}), 404
            
            return jsonify(module.to_dict())
        except Exception as e:
            logger.error(f"Error getting module {module_id}: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @api.route('/modules/<int:module_id>/manual', methods=['GET'])
    def get_module_manual(module_id):
        """Get manual content for a specific module."""
        try:
            module = Module.query.get(module_id)
            if not module:
                return jsonify({"error": f"Module with ID {module_id} not found"}), 404
            
            if not module.manual_url:
                return jsonify({"error": f"No manual URL available for module {module_id}"}), 404
            
            # Force refresh if requested
            force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
            
            manual_content = cache_manager.get_manual_content(module_id, module.manual_url, force_refresh)
            
            return jsonify({
                "module_id": module_id,
                "module_name": module.name,
                "manual_url": module.manual_url,
                "manual_content": manual_content,
                "last_updated": module.manual_last_updated.isoformat() if module.manual_last_updated else None
            })
        except Exception as e:
            logger.error(f"Error getting manual for module {module_id}: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @api.route('/modules/<int:module_id>/forum-data', methods=['GET'])
    def get_module_forum_data(module_id):
        """Get forum data for a specific module."""
        try:
            module = Module.query.get(module_id)
            if not module:
                return jsonify({"error": f"Module with ID {module_id} not found"}), 404
            
            # Get source type from query params
            source_type = request.args.get('source_type', 'all')
            
            # Force refresh if requested
            force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
            
            forum_data = cache_manager.get_forum_data(module_id, module.name, source_type, force_refresh)
            
            return jsonify({
                "module_id": module_id,
                "module_name": module.name,
                "source_type": source_type,
                "forum_data": forum_data
            })
        except Exception as e:
            logger.error(f"Error getting forum data for module {module_id}: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @api.route('/parse-rack', methods=['POST'])
    def parse_rack():
        """Parse a ModularGrid rack URL and extract module information."""
        try:
            data = request.json
            if not data or 'modulargrid_url' not in data:
                return jsonify({"error": "Missing modulargrid_url parameter"}), 400
            
            rack_data = modulargrid_parser.parse_url(data['modulargrid_url'])
            return jsonify(rack_data)
        except Exception as e:
            logger.error(f"Error parsing rack: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @api.route('/racks', methods=['GET'])
    def get_racks():
        """Get all user racks."""
        try:
            racks = UserRack.query.all()
            return jsonify([rack.to_dict() for rack in racks])
        except Exception as e:
            logger.error(f"Error getting racks: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @api.route('/racks/<int:rack_id>', methods=['GET'])
    def get_rack(rack_id):
        """Get a specific rack by ID."""
        try:
            rack = UserRack.query.get(rack_id)
            if not rack:
                return jsonify({"error": f"Rack with ID {rack_id} not found"}), 404
            
            return jsonify(rack.to_dict())
        except Exception as e:
            logger.error(f"Error getting rack {rack_id}: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @api.route('/generate-patch', methods=['POST'])
    def generate_patch():
        """Generate a patch idea based on modules and user prompt."""
        try:
            data = request.json
            if not data:
                return jsonify({"error": "Missing request data"}), 400
            
            # Check if we're generating from a rack or module list
            if 'rack_id' in data:
                rack = UserRack.query.get(data['rack_id'])
                if not rack:
                    return jsonify({"error": f"Rack with ID {data['rack_id']} not found"}), 404
                
                modules = [rm.module_id for rm in rack.modules]
            elif 'modules' in data:
                modules = data['modules']
            else:
                return jsonify({"error": "Missing rack_id or modules parameter"}), 400
            
            if 'prompt' not in data:
                return jsonify({"error": "Missing prompt parameter"}), 400
            
            patch_idea = patch_generator.generate_patch(
                modules=modules,
                prompt=data['prompt']
            )
            
            return jsonify(patch_idea)
        except Exception as e:
            logger.error(f"Error generating patch: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @api.route('/patch-ideas', methods=['GET'])
    def get_patch_ideas():
        """Get all patch ideas, with optional filtering."""
        try:
            # Get filter parameters
            patch_type = request.args.get('patch_type')
            complexity = request.args.get('complexity')
            
            # Build query
            query = PatchIdea.query
            
            if patch_type:
                query = query.filter_by(patch_type=patch_type)
            
            if complexity:
                query = query.filter_by(complexity=int(complexity))
            
            # Execute query
            patch_ideas = query.all()
            
            return jsonify([
                {
                    "id": idea.id,
                    "title": idea.title,
                    "description": idea.description,
                    "patch_type": idea.patch_type,
                    "complexity": idea.complexity,
                    "source_type": idea.source_type,
                    "source_url": idea.source_url,
                    "created_at": idea.created_at.isoformat()
                }
                for idea in patch_ideas
            ])
        except Exception as e:
            logger.error(f"Error getting patch ideas: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @api.route('/patch-ideas/<int:patch_id>', methods=['GET'])
    def get_patch_idea(patch_id):
        """Get a specific patch idea by ID."""
        try:
            patch_idea = PatchIdea.query.get(patch_id)
            if not patch_idea:
                return jsonify({"error": f"Patch idea with ID {patch_id} not found"}), 404
            
            # Get modules
            modules = []
            for pm in patch_idea.modules:
                module = Module.query.get(pm.module_id)
                if module:
                    modules.append({
                        "id": module.id,
                        "name": module.name,
                        "manufacturer": module.manufacturer,
                        "type": module.module_type,
                        "description": module.description,
                        "importance": pm.importance
                    })
            
            # Get connections
            connections = []
            for pc in patch_idea.connections:
                source_module = Module.query.get(pc.source_module_id)
                source_connection = ModuleConnection.query.get(pc.source_connection_id)
                target_module = Module.query.get(pc.target_module_id)
                target_connection = ModuleConnection.query.get(pc.target_connection_id)
                
                if source_module and source_connection and target_module and target_connection:
                    connections.append({
                        "source_module": source_module.name,
                        "source_connection": source_connection.name,
                        "target_module": target_module.name,
                        "target_connection": target_connection.name,
                        "cable_color": pc.cable_color,
                        "description": pc.description,
                        "importance": pc.importance
                    })
            
            # Get control settings
            control_settings = []
            for pcs in patch_idea.control_settings:
                module = Module.query.get(pcs.module_id)
                control = ModuleControl.query.get(pcs.control_id)
                
                if module and control:
                    control_settings.append({
                        "module": module.name,
                        "control": control.control_name,
                        "value_numeric": pcs.value_numeric,
                        "value_text": pcs.value_text,
                        "description": pcs.description,
                        "importance": pcs.importance
                    })
            
            return jsonify({
                "id": patch_idea.id,
                "title": patch_idea.title,
                "description": patch_idea.description,
                "patch_type": patch_idea.patch_type,
                "complexity": patch_idea.complexity,
                "source_type": patch_idea.source_type,
                "source_url": patch_idea.source_url,
                "source_text": patch_idea.source_text,
                "created_at": patch_idea.created_at.isoformat(),
                "modules": modules,
                "connections": connections,
                "control_settings": control_settings
            })
        except Exception as e:
            logger.error(f"Error getting patch idea {patch_id}: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    # Register the blueprint with the app
    app.register_blueprint(api, url_prefix='/api')
