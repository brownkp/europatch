""" Module for generating patch ideas based on available modules and user prompts.
"""
import logging
import random
from datetime import datetime
from src.models import db, Module, ModuleConnection, ModuleControl, PatchIdea, PatchModule, PatchConnection, PatchControlSetting, ForumSource
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
                    role = "percussion generator"
                    importance = 5
                elif patch_type == "bass" and matching_type in ["oscillator", "filter"]:
                    role = "bass generator"
                    importance = 5
                elif patch_type == "lead" and matching_type in ["oscillator", "filter", "envelope"]:
                    role = "lead voice"
                    importance = 5
                elif patch_type == "drone" and matching_type in ["oscillator", "filter", "reverb"]:
                    role = "drone generator"
                    importance = 5
                else:
                    # Default role assignment
                    role = random.choice(possible_roles)
                    importance = 3

                module_roles[module.id] = {
                    "role": role,
                    "importance": importance
                }
            else:
                # Default role for unknown module types
                module_roles[module.id] = {
                    "role": "utility",
                    "importance": 2
                }

        return module_roles

    def _generate_connections(self, modules, module_roles, patch_type):
        """
        Generate connections between modules based on their roles and the patch type.

        Args:
            modules (list): List of module objects
            module_roles (dict): Module roles
            patch_type (str): Type of patch

        Returns:
            list: Connections
        """
        connections = []

        # Group modules by type
        module_types = {}
        for module in modules:
            module_type = module.module_type.lower() if module.module_type else "unknown"
            if module_type not in module_types:
                module_types[module_type] = []
            module_types[module_type].append(module)

        # Get connection patterns for this patch type
        connection_patterns = self.patch_types[patch_type]["connection_patterns"]

        # Create connections based on patterns
        for pattern in connection_patterns:
            parts = pattern.split("->")
            if len(parts) < 2:
                continue

            source_type = parts[0].strip()
            target_type = parts[-1].strip()

            # Find matching source and target modules
            source_modules = []
            target_modules = []

            for module_type, type_modules in module_types.items():
                if any(st in module_type for st in source_type.split()):
                    source_modules.extend(type_modules)
                if any(tt in module_type for tt in target_type.split()):
                    target_modules.extend(type_modules)

            if not source_modules or not target_modules:
                continue

            # Create connections between matching modules
            for source_module in source_modules[:2]:  # Limit to 2 source modules per pattern
                for target_module in target_modules[:2]:  # Limit to 2 target modules per pattern
                    if source_module.id == target_module.id:
                        continue

                    # Get output connections from source module
                    source_connections = ModuleConnection.query.filter_by(
                        module_id=source_module.id,
                        connection_type="output"
                    ).all()

                    # Get input connections from target module
                    target_connections = ModuleConnection.query.filter_by(
                        module_id=target_module.id,
                        connection_type="input"
                    ).all()

                    if not source_connections or not target_connections:
                        continue

                    # Create a connection
                    source_connection = random.choice(source_connections)
                    target_connection = random.choice(target_connections)

                    # Generate description based on the pattern
                    if "pitch" in target_type:
                        description = f"Modulate the pitch of {target_module.name} with {source_module.name}"
                    elif "filter" in target_type:
                        description = f"Process {source_module.name} through the filter of {target_module.name}"
                    elif "reverb" in target_type or "delay" in target_type:
                        description = f"Add space to {source_module.name} using {target_module.name}"
                    elif "envelope" in source_type and "vca" in target_type:
                        description = f"Shape the amplitude of {target_module.name} with {source_module.name}"
                    elif "clock" in source_type or "trigger" in target_type:
                        description = f"Trigger {target_module.name} with {source_module.name}"
                    else:
                        description = f"Connect {source_module.name} to {target_module.name} for {patch_type} sounds"

                    # Determine importance based on module roles
                    source_importance = module_roles.get(source_module.id, {}).get("importance", 3)
                    target_importance = module_roles.get(target_module.id, {}).get("importance", 3)
                    importance = max(source_importance, target_importance)

                    # Choose a cable color based on connection type
                    cable_colors = ["red", "blue", "yellow", "green", "orange", "purple", "black", "white"]
                    if "pitch" in target_type:
                        cable_color = "blue"  # Convention: blue for pitch
                    elif "gate" in target_type or "trigger" in target_type:
                        cable_color = "orange"  # Convention: orange for gates/triggers
                    elif "clock" in source_type:
                        cable_color = "purple"  # Convention: purple for clock
                    elif "audio" in source_connection.name.lower() or "out" in source_connection.name.lower():
                        cable_color = "black"  # Convention: black for audio
                    else:
                        cable_color = random.choice(cable_colors)

                    connections.append({
                        "source_module_id": source_module.id,
                        "source_connection_id": source_connection.id,
                        "target_module_id": target_module.id,
                        "target_connection_id": target_connection.id,
                        "cable_color": cable_color,
                        "description": description,
                        "importance": importance
                    })

        # If we don't have enough connections, add some random ones
        if len(connections) < 3:
            # Find modules with outputs
            output_modules = []
            for module in modules:
                outputs = ModuleConnection.query.filter_by(
                    module_id=module.id,
                    connection_type="output"
                ).all()
                if outputs:
                    output_modules.append((module, outputs))

            # Find modules with inputs
            input_modules = []
            for module in modules:
                inputs = ModuleConnection.query.filter_by(
                    module_id=module.id,
                    connection_type="input"
                ).all()
                if inputs:
                    input_modules.append((module, inputs))

            # Create random connections
            for _ in range(min(5, len(output_modules) * len(input_modules))):
                if not output_modules or not input_modules:
                    break

                source_module, source_connections = random.choice(output_modules)
                target_module, target_connections = random.choice(input_modules)

                if source_module.id == target_module.id:
                    continue

                source_connection = random.choice(source_connections)
                target_connection = random.choice(target_connections)

                # Check if this connection already exists
                if any(
                    conn["source_module_id"] == source_module.id and
                    conn["source_connection_id"] == source_connection.id and
                    conn["target_module_id"] == target_module.id and
                    conn["target_connection_id"] == target_connection.id
                    for conn in connections
                ):
                    continue

                description = f"Connect {source_module.name} to {target_module.name} for interesting {patch_type} sounds"
                cable_color = random.choice(["red", "blue", "yellow", "green", "orange", "purple", "black", "white"])

                connections.append({
                    "source_module_id": source_module.id,
                    "source_connection_id": source_connection.id,
                    "target_module_id": target_module.id,
                    "target_connection_id": target_connection.id,
                    "cable_color": cable_color,
                    "description": description,
                    "importance": 3
                })

        return connections

    def _generate_control_settings(self, modules, module_roles, patch_type):
        """
        Generate control settings for modules based on their roles and the patch type.

        Args:
            modules (list): List of module objects
            module_roles (dict): Module roles
            patch_type (str): Type of patch

        Returns:
            list: Control settings
        """
        control_settings = []

        # Define control setting patterns based on patch type
        control_patterns = {
            "ambient": {
                "filter": {"cutoff": "low", "resonance": "medium"},
                "reverb": {"decay": "high", "mix": "high"},
                "delay": {"time": "high", "feedback": "medium"},
                "lfo": {"rate": "low", "depth": "high"}
            },
            "generative": {
                "random": {"density": "medium", "range": "high"},
                "quantizer": {"scale": "pentatonic", "root": "C"},
                "sequencer": {"length": "medium", "variation": "high"},
                "clock": {"tempo": "medium", "swing": "low"}
            },
            "percussion": {
                "envelope": {"attack": "low", "decay": "low", "sustain": "low", "release": "medium"},
                "filter": {"cutoff": "medium", "resonance": "high"},
                "vca": {"gain": "medium", "response": "fast"}
            },
            "bass": {
                "oscillator": {"waveform": "saw", "detune": "low"},
                "filter": {"cutoff": "low", "resonance": "medium"},
                "envelope": {"attack": "low", "decay": "medium", "sustain": "medium", "release": "medium"}
            },
            "lead": {
                "oscillator": {"waveform": "square", "detune": "medium"},
                "filter": {"cutoff": "high", "resonance": "medium"},
                "envelope": {"attack": "low", "decay": "medium", "sustain": "medium", "release": "low"}
            },
            "drone": {
                "oscillator": {"waveform": "sine", "detune": "low"},
                "filter": {"cutoff": "medium", "resonance": "low"},
                "reverb": {"decay": "high", "mix": "high"},
                "lfo": {"rate": "very low", "depth": "medium"}
            }
        }

        # Generate settings for each module
        for module in modules:
            module_type_lower = module.module_type.lower() if module.module_type else "unknown"

            # Find matching module type in control patterns
            matching_type = None
            for type_key in control_patterns[patch_type]:
                if type_key in module_type_lower:
                    matching_type = type_key
                    break

            if not matching_type:
                continue

            # Get controls for this module
            controls = ModuleControl.query.filter_by(module_id=module.id).all()
            if not controls:
                continue

            # Get pattern for this module type
            pattern = control_patterns[patch_type][matching_type]

            # Generate settings based on pattern
            for control in controls:
                control_name_lower = control.control_name.lower()

                # Find matching control in pattern
                matching_control = None
                for control_key in pattern:
                    if control_key in control_name_lower:
                        matching_control = control_key
                        break

                if not matching_control:
                    continue

                # Get setting value from pattern
                value = pattern[matching_control]

                # Convert value to numeric and text representation
                value_numeric = None
                value_text = None

                if value == "low":
                    value_numeric = control.min_value + (control.max_value - control.min_value) * 0.25
                    value_text = "Low (25%)"
                elif value == "medium":
                    value_numeric = control.min_value + (control.max_value - control.min_value) * 0.5
                    value_text = "Medium (50%)"
                elif value == "high":
                    value_numeric = control.min_value + (control.max_value - control.min_value) * 0.75
                    value_text = "High (75%)"
                elif value == "very low":
                    value_numeric = control.min_value + (control.max_value - control.min_value) * 0.1
                    value_text = "Very low (10%)"
                elif value == "very high":
                    value_numeric = control.min_value + (control.max_value - control.min_value) * 0.9
                    value_text = "Very high (90%)"
                elif value in ["saw", "square", "sine", "triangle"]:
                    value_numeric = None
                    value_text = value.capitalize()
                elif value in ["pentatonic", "major", "minor", "chromatic"]:
                    value_numeric = None
                    value_text = value.capitalize()
                elif value in ["C", "D", "E", "F", "G", "A", "B"]:
                    value_numeric = None
                    value_text = value
                elif value == "fast":
                    value_numeric = control.min_value + (control.max_value - control.min_value) * 0.8
                    value_text = "Fast response"
                else:
                    value_numeric = control.min_value + (control.max_value - control.min_value) * 0.5
                    value_text = value

                # Generate description
                if "cutoff" in control_name_lower:
                    if value == "low":
                        description = f"Set {control.control_name} low for a dark, filtered sound"
                    elif value == "high":
                        description = f"Set {control.control_name} high for a bright, open sound"
                    else:
                        description = f"Set {control.control_name} to {value} for balanced filtering"
                elif "resonance" in control_name_lower:
                    if value == "high":
                        description = f"Increase {control.control_name} for an emphasized filter character"
                    else:
                        description = f"Set {control.control_name} to {value} for subtle filtering"
                elif "decay" in control_name_lower or "release" in control_name_lower:
                    if value == "high":
                        description = f"Long {control.control_name} creates spacious, evolving sounds"
                    else:
                        description = f"Set {control.control_name} to {value} for appropriate decay time"
                elif "attack" in control_name_lower:
                    if value == "low":
                        description = f"Quick {control.control_name} for immediate response"
                    else:
                        description = f"Set {control.control_name} to {value} for gradual onset"
                elif "rate" in control_name_lower:
                    if value == "low" or value == "very low":
                        description = f"Slow {control.control_name} for subtle, evolving modulation"
                    else:
                        description = f"Set {control.control_name} to {value} for appropriate modulation speed"
                else:
                    description = f"Set {control.control_name} to {value} for optimal {patch_type} sound"

                # Determine importance based on module role
                importance = module_roles.get(module.id, {}).get("importance", 3)

                control_settings.append({
                    "module_id": module.id,
                    "control_id": control.id,
                    "value_numeric": value_numeric,
                    "value_text": value_text,
                    "description": description,
                    "importance": importance
                })

        return control_settings

    def _get_sources(self, modules, patch_type):
        """
        Get sources of information used to generate the patch.

        Args:
            modules (list): List of module objects
            patch_type (str): Type of patch

        Returns:
            list: Sources
        """
        sources = []

        # Add patch type description as a source
        sources.append({
            "type": "patch_type",
            "title": f"{patch_type.title()} Patch Type",
            "content": self.patch_types[patch_type]["description"],
            "url": None
        })

        # Add module manuals as sources
        for module in modules:
            if module.manual_url:
                sources.append({
                    "type": "manual",
                    "title": f"{module.name} Manual",
                    "content": "Reference to module manual",
                    "url": module.manual_url
                })

        # Add forum sources
        for module in modules:
            # Get forum data for this module
            forum_sources = ForumSource.query.filter_by(module_id=module.id).order_by(ForumSource.relevance_score.desc()).limit(3).all()

            for source in forum_sources:
                sources.append({
                    "type": source.source_type,
                    "title": source.title,
                    "content": source.content[:200] + "..." if source.content and len(source.content) > 200 else source.content,
                    "url": source.url
                })

        return sources
