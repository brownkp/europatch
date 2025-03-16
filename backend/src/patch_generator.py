"""
Module for generating patch ideas based on available modules and user prompts.
"""
import logging
import random
from datetime import datetime
from src.models import db, Module, ModuleConnection, ModuleControl, PatchIdea, PatchModule, PatchConnection, PatchControlSetting
from src.cache_manager import CacheManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PatchGenerator:
    """
    Generator for eurorack patch ideas based on available modules and user prompts.
    """
    
    def __init__(self):
        """Initialize the patch generator."""
        self.cache_manager = CacheManager()
        
        # Define patch types and their characteristics
        self.patch_types = {
            "ambient": {
                "description": "Evolving, atmospheric sounds with slow modulation",
                "common_modules": ["oscillator", "filter", "reverb", "delay", "lfo"],
                "connection_patterns": [
                    "oscillator -> filter -> reverb",
                    "lfo -> oscillator parameters",
                    "noise -> reverb"
                ]
            },
            "generative": {
                "description": "Self-evolving patches with random elements",
                "common_modules": ["random", "quantizer", "oscillator", "sequencer", "clock"],
                "connection_patterns": [
                    "random -> quantizer -> oscillator pitch",
                    "clock -> sequencer -> trigger inputs",
                    "sequencer -> filter cutoff"
                ]
            },
            "percussion": {
                "description": "Rhythmic sounds and drum-like patches",
                "common_modules": ["noise", "envelope", "vca", "filter", "clock"],
                "connection_patterns": [
                    "noise -> filter -> vca",
                    "envelope -> vca",
                    "clock -> envelope trigger"
                ]
            },
            "bass": {
                "description": "Low frequency sounds with punch and presence",
                "common_modules": ["oscillator", "filter", "envelope", "vca", "distortion"],
                "connection_patterns": [
                    "oscillator -> filter -> vca",
                    "envelope -> filter cutoff",
                    "envelope -> vca"
                ]
            },
            "lead": {
                "description": "Expressive melodic sounds",
                "common_modules": ["oscillator", "filter", "envelope", "vca", "delay"],
                "connection_patterns": [
                    "oscillator -> filter -> vca -> delay",
                    "envelope -> filter cutoff",
                    "lfo -> oscillator pitch (vibrato)"
                ]
            },
            "drone": {
                "description": "Sustained, evolving textures",
                "common_modules": ["oscillator", "filter", "reverb", "delay", "lfo"],
                "connection_patterns": [
                    "oscillator -> filter -> reverb -> delay",
                    "lfo -> filter cutoff",
                    "lfo -> oscillator parameters"
                ]
            }
        }
    
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
            elif isinstance(module, dict) and 'id' in module:
                module_obj = Module.query.get(module['id'])
                if module_obj:
                    module_objects.append(module_obj)
            elif hasattr(module, 'id'):
                module_objects.append(module)
        
        if not module_objects:
            raise ValueError("No valid modules provided")
        
        # Gather information about modules from manuals and forums
        module_info = {}
        for module in module_objects:
            # Get manual content
            if module.manual_url:
                manual_content = self.cache_manager.get_manual_content(module.id, module.manual_url)
            else:
                manual_content = None
            
            # Get forum data
            forum_data = self.cache_manager.get_forum_data(module.id, module.name)
            
            module_info[module.id] = {
                "manual_content": manual_content,
                "forum_data": forum_data
            }
        
        # Generate patch title and description
        title, description = self._generate_title_description(module_objects, patch_type, prompt)
        
        # Determine module roles in the patch
        module_roles = self._determine_module_roles(module_objects, patch_type)
        
        # Generate connections between modules
        connections = self._generate_connections(module_objects, module_roles, patch_type)
        
        # Generate control settings
        control_settings = self._generate_control_settings(module_objects, module_roles, patch_type)
        
        # Create patch idea in database
        patch_idea = PatchIdea(
            title=title,
            description=description,
            patch_type=patch_type,
            complexity=random.randint(2, 5),  # Random complexity between 2-5
            source_type="generated",
            source_text=f"Generated based on user prompt: {prompt}"
        )
        db.session.add(patch_idea)
        db.session.commit()
        
        # Add modules to patch
        for module in module_objects:
            importance = 5 if module.id in module_roles and module_roles[module.id]["importance"] > 3 else 3
            patch_module = PatchModule(
                patch_id=patch_idea.id,
                module_id=module.id,
                importance=importance
            )
            db.session.add(patch_module)
        
        db.session.commit()
        
        # Add connections to patch
        for conn in connections:
            patch_connection = PatchConnection(
                patch_id=patch_idea.id,
                source_module_id=conn["source_module_id"],
                source_connection_id=conn["source_connection_id"],
                target_module_id=conn["target_module_id"],
                target_connection_id=conn["target_connection_id"],
                cable_color=conn["cable_color"],
                description=conn["description"],
                importance=conn["importance"]
            )
            db.session.add(patch_connection)
        
        db.session.commit()
        
        # Add control settings to patch
        for setting in control_settings:
            patch_control = PatchControlSetting(
                patch_id=patch_idea.id,
                module_id=setting["module_id"],
                control_id=setting["control_id"],
                value_numeric=setting["value_numeric"],
                value_text=setting["value_text"],
                description=setting["description"],
                importance=setting["importance"]
            )
            db.session.add(patch_control)
        
        db.session.commit()
        
        # Return the generated patch idea
        return {
            "id": patch_idea.id,
            "title": patch_idea.title,
            "description": patch_idea.description,
            "patch_type": patch_idea.patch_type,
            "complexity": patch_idea.complexity,
            "modules": [
                {
                    "id": module.id,
                    "name": module.name,
                    "manufacturer": module.manufacturer,
                    "type": module.module_type,
                    "description": module.description,
                    "role": module_roles.get(module.id, {}).get("role", "Unknown")
                }
                for module in module_objects
            ],
            "connections": [
                {
                    "source_module": Module.query.get(conn["source_module_id"]).name,
                    "source_connection": ModuleConnection.query.get(conn["source_connection_id"]).name,
                    "target_module": Module.query.get(conn["target_module_id"]).name,
                    "target_connection": ModuleConnection.query.get(conn["target_connection_id"]).name,
                    "description": conn["description"]
                }
                for conn in connections
            ],
            "control_settings": [
                {
                    "module": Module.query.get(setting["module_id"]).name,
                    "control": ModuleControl.query.get(setting["control_id"]).control_name,
                    "value": setting["value_text"],
                    "description": setting["description"]
                }
                for setting in control_settings
            ],
            "sources": self._get_sources(module_objects, patch_type)
        }
    
    def _determine_patch_type(self, prompt):
        """
        Determine the patch type based on the user prompt.
        
        Args:
            prompt (str): User prompt
            
        Returns:
            str: Patch type
        """
        prompt_lower = prompt.lower()
        
        # Check for explicit mentions of patch types
        for patch_type in self.patch_types:
            if patch_type in prompt_lower:
                return patch_type
        
        # Check for related keywords
        keywords = {
            "ambient": ["ambient", "atmospheric", "pad", "texture", "drone", "evolving", "spacey", "ethereal"],
            "generative": ["generative", "random", "evolving", "self-playing", "algorithmic", "chance", "probability"],
            "percussion": ["percussion", "drum", "kick", "snare", "hat", "rhythmic", "beat"],
            "bass": ["bass", "low", "sub", "808", "acid", "deep"],
            "lead": ["lead", "melody", "solo", "arpeggio", "sequence", "pluck"],
            "drone": ["drone", "sustained", "continuous", "dark", "rumble", "noise"]
        }
        
        # Count keyword matches for each type
        counts = {patch_type: 0 for patch_type in self.patch_types}
        for patch_type, type_keywords in keywords.items():
            for keyword in type_keywords:
                if keyword in prompt_lower:
                    counts[patch_type] += 1
        
        # Return the type with the most keyword matches
        max_count = max(counts.values())
        if max_count > 0:
            max_types = [pt for pt, count in counts.items() if count == max_count]
            return random.choice(max_types)
        
        # Default to ambient if no matches
        return "ambient"
    
    def _generate_title_description(self, modules, patch_type, prompt):
        """
        Generate a title and description for the patch.
        
        Args:
            modules (list): List of module objects
            patch_type (str): Type of patch
            prompt (str): User prompt
            
        Returns:
            tuple: (title, description)
        """
        # Get module names for use in title
        module_names = [module.name for module in modules]
        
        # Title templates
        title_templates = [
            f"{patch_type.title()} {random.choice(['Adventure', 'Journey', 'Exploration'])} with {random.choice(module_names)}",
            f"{random.choice(module_names)} {patch_type.title()} {random.choice(['Textures', 'Soundscape', 'Experience'])}",
            f"{patch_type.title()} {random.choice(['Patch', 'System', 'Network'])} using {random.choice(module_names)}",
            f"{random.choice(['Evolving', 'Dynamic', 'Expressive'])} {patch_type.title()} with {random.choice(module_names)}"
        ]
        
        title = random.choice(title_templates)
        
        # Description templates
        description_templates = [
            f"A {patch_type} patch that utilizes {', '.join(module_names[:3])} to create {random.choice(['evolving', 'dynamic', 'expressive'])} sounds. {self.patch_types[patch_type]['description']}.",
            f"This {patch_type} patch focuses on {random.choice(['texture', 'rhythm', 'melody', 'timbre'])} using {', '.join(module_names[:2])} as the core modules. {prompt}",
            f"An exploration of {patch_type} sounds using {', '.join(module_names[:3])}. This patch is designed to create {random.choice(['evolving', 'dynamic', 'expressive'])} {patch_type} textures."
        ]
        
        description = random.choice(description_templates)
        
        return title, description
    
    def _determine_module_roles(self, modules, patch_type):
        """
        Determine the roles of modules in the patch.
        
        Args:
            modules (list): List of module objects
            patch_type (str): Type of patch
            
        Returns:
            dict: Module roles
        """
        module_roles = {}
        
        # Define common module types and their potential roles
        module_type_roles = {
            "oscillator": ["sound source", "modulation source", "carrier", "modulator"],
            "filter": ["sound processor", "tone shaper", "resonator"],
            "envelope": ["modulation source", "amplitude shaper", "transient generator"],
            "lfo": ["modulation source", "rhythm generator"],
            "vca": ["amplitude controller", "modulation controller"],
            "reverb": ["space processor", "ambience generator"],
            "delay": ["time processor", "echo generator"],
            "sequencer": ["pattern generator", "rhythm controller", "melody generator"],
            "clock": ["timing source", "trigger generator"],
            "random": ["chance generator", "unpredictability source"],
            "quantizer": ["pitch controller", "scale enforcer"],
            "mixer": ["signal combiner", "balance controller"],
            "function": ["modulation source", "signal processor", "envelope generator"],
            "granular": ["texture generator", "sound mangler"],
            "resonator": ["tone generator", "harmonic enhancer"]
        }
        
        # Assign roles based on module type and patch type
        for module in modules:
            module_type_lower = module.module_type.lower() if module.module_type else "unknown"
            
            # Find matching module type
            matching_type = None
            for type_key in module_type_roles:
                if type_key in module_type_lower:
                    matching_type = type_key
                    break
            
            if matching_type:
                # Assign a role based on module type
                possible_roles = module_type_roles[matching_type]
                
                # Prioritize certain roles based on patch type
                if patch_type == "ambient" and matching_type in ["reverb", "delay", "granular"]:
                    role = "ambience generator"
                    importance = 5
                elif patch_type == "generative" and matching_type in ["random", "sequencer", "clock"]:
                    role = "pattern generator"
                    importance = 5
                elif patch_type == "percussion" and matching_type in ["envelope", "noise", "filter"]:
                    role = "percussio<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>