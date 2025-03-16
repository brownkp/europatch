from datetime import datetime
import random

class PatchGenerator:
    """
    Generator for Eurorack synthesizer patch ideas based on available modules and user prompts
    """
    
    def __init__(self, db_connector=None):
        """
        Initialize the patch generator
        
        Args:
            db_connector: Optional database connector for retrieving module data
        """
        self.db_connector = db_connector
        self.patch_types = {
            'ambient': self._generate_ambient_patch,
            'generative': self._generate_generative_patch,
            'percussion': self._generate_percussion_patch,
            'bass': self._generate_bass_patch,
            'lead': self._generate_lead_patch,
            'drone': self._generate_drone_patch,
            'techno': self._generate_techno_patch
        }
        
        # Cable colors for visualization
        self.cable_colors = ['red', 'blue', 'yellow', 'green', 'purple', 'orange', 'white', 'black']
    
    def generate_patch_ideas(self, rack_id, prompt, complexity=3, max_results=3):
        """
        Generate patch ideas based on available modules and user prompt
        
        Args:
            rack_id (str): Rack ID
            prompt (str): User prompt
            complexity (int): Desired complexity (1-5)
            max_results (int): Maximum number of results
            
        Returns:
            list: Generated patch ideas
            
        Raises:
            ValueError: If no modules are found or prompt is invalid
        """
        # Get rack modules
        modules = self._get_rack_modules(rack_id)
        if not modules:
            raise ValueError(f"No modules found for rack: {rack_id}")
        
        # Analyze prompt to determine patch type
        patch_type = self._analyze_prompt(prompt)
        
        # Find relevant modules for the patch type
        relevant_modules = self._find_relevant_modules(modules, patch_type)
        
        # Find relevant patch ideas from database
        db_patch_ideas = []
        if self.db_connector:
            db_patch_ideas = self._find_relevant_patch_ideas(relevant_modules, patch_type, complexity)
        
        # Generate new patch ideas based on modules
        generated_ideas = []
        
        # Use appropriate generator function based on patch type
        if patch_type in self.patch_types:
            generator_func = self.patch_types[patch_type]
            generated_ideas = generator_func(relevant_modules, complexity)
        else:
            # Default to generative patch if type not recognized
            generated_ideas = self._generate_generative_patch(relevant_modules, complexity)
        
        # Combine database ideas and generated ideas
        all_ideas = db_patch_ideas + generated_ideas
        
        # Sort by relevance and limit results
        all_ideas.sort(key=lambda x: x.get('relevance_score', 0.5), reverse=True)
        return all_ideas[:max_results]
    
    def _get_rack_modules(self, rack_id):
        """
        Get modules for a specific rack
        
        Args:
            rack_id (str): Rack ID
            
        Returns:
            list: Modules in the rack
        """
        if self.db_connector:
            return self.db_connector.get_rack_modules(rack_id)
        else:
            # Mock implementation for testing without database
            return self._mock_get_rack_modules(rack_id)
    
    def _mock_get_rack_modules(self, rack_id):
        """
        Mock implementation for testing without database
        
        Args:
            rack_id (str): Rack ID
            
        Returns:
            list: Mock modules
        """
        # This is just for testing without a database
        # In a real implementation, this would query the database
        return [
            {
                'id': 1,
                'name': 'Plaits',
                'manufacturer': 'Mutable Instruments',
                'hp_width': 12,
                'module_type': 'VCO',
                'description': 'Macro-oscillator with multiple synthesis models',
                'connections': [
                    {'id': 1, 'type': 'input', 'name': 'V/OCT', 'description': '1V/octave pitch control'},
                    {'id': 2, 'type': 'input', 'name': 'TRIG', 'description': 'Trigger input'},
                    {'id': 3, 'type': 'output', 'name': 'OUT', 'description': 'Main audio output'},
                    {'id': 4, 'type': 'output', 'name': 'AUX', 'description': 'Auxiliary audio output'}
                ],
                'controls': [
                    {'id': 1, 'type': 'knob', 'name': 'MODEL', 'description': 'Synthesis model selection'},
                    {'id': 2, 'type': 'knob', 'name': 'TIMBRE', 'description': 'Timbre control'},
                    {'id': 3, 'type': 'knob', 'name': 'MORPH', 'description': 'Morph control'}
                ]
            },
            {
                'id': 2,
                'name': 'Clouds',
                'manufacturer': 'Mutable Instruments',
                'hp_width': 18,
                'module_type': 'Effect',
                'description': 'Texture synthesizer',
                'connections': [
                    {'id': 5, 'type': 'input', 'name': 'IN', 'description': 'Audio input'},
                    {'id': 6, 'type': 'output', 'name': 'OUT', 'description': 'Audio output'},
                    {'id': 7, 'type': 'input', 'name': 'TRIG', 'description': 'Trigger input'},
                    {'id': 8, 'type': 'input', 'name': 'FREEZE', 'description': 'Freeze input'}
                ],
                'controls': [
                    {'id': 4, 'type': 'knob', 'name': 'POSITION', 'description': 'Buffer position'},
                    {'id': 5, 'type': 'knob', 'name': 'SIZE', 'description': 'Grain size'},
                    {'id': 6, 'type': 'knob', 'name': 'TEXTURE', 'description': 'Texture control'},
                    {'id': 7, 'type': 'knob', 'name': 'BLEND', 'description': 'Dry/wet mix'}
                ]
            },
            {
                'id': 3,
                'name': 'Maths',
                'manufacturer': 'Make Noise',
                'hp_width': 20,
                'module_type': 'Utility',
                'description': 'Function generator',
                'connections': [
                    {'id': 9, 'type': 'input', 'name': 'TRIG 1', 'description': 'Trigger input for channel 1'},
                    {'id': 10, 'type': 'output', 'name': 'EOC 1', 'description': 'End of cycle output for channel 1'},
                    {'id': 11, 'type': 'output', 'name': 'OUT 1', 'description': 'Output for channel 1'},
                    {'id': 12, 'type': 'output', 'name': 'OUT 4', 'description': 'Output for channel 4'}
                ],
                'controls': [
                    {'id': 8, 'type': 'knob', 'name': 'RISE', 'description': 'Rise time'},
                    {'id': 9, 'type': 'knob', 'name': 'FALL', 'description': 'Fall time'},
                    {'id': 10, 'type': 'switch', 'name': 'CYCLE', 'description': 'Cycle mode'}
                ]
            }
        ]
    
    def _analyze_prompt(self, prompt):
        """
        Analyze prompt to determine patch type
        
        Args:
            prompt (str): User prompt
            
        Returns:
            str: Patch type
        """
        prompt_lower = prompt.lower()
        
        # Check for specific patch types in prompt
        if 'ambient' in prompt_lower or 'atmospheric' in prompt_lower or 'pad' in prompt_lower:
            return 'ambient'
        elif 'generative' in prompt_lower or 'random' in prompt_lower or 'evolving' in prompt_lower:
            return 'generative'
        elif 'percussion' in prompt_lower or 'drum' in prompt_lower or 'beat' in prompt_lower:
            return 'percussion'
        elif 'bass' in prompt_lower or 'low' in prompt_lower:
            return 'bass'
        elif 'lead' in prompt_lower or 'melody' in prompt_lower:
            return 'lead'
        elif 'drone' in prompt_lower or 'sustained' in prompt_lower:
            return 'drone'
        elif 'techno' in prompt_lower or 'dance' in prompt_lower:
            return 'techno'
        else:
            # Default to generative if no specific type is detected
            return 'generative'
    
    def _find_relevant_modules(self, modules, patch_type):
        """
        Find modules relevant to the patch type
        
        Args:
            modules (list): Available modules
            patch_type (str): Patch type
            
        Returns:
            list: Sorted modules by relevance
        """
        # Group modules by type
        module_types = {}
        for module in modules:
            module_type = module.get('module_type', 'Other')
            if module_type not in module_types:
                module_types[module_type] = []
            module_types[module_type].append(module)
        
        # Return all modules, but sorted by relevance to patch type
        sorted_modules = []
        
        # Define priority module types for each patch type
        priority_types = {
            'ambient': ['VCO', 'Effect', 'LFO', 'VCA', 'VCF'],
            'generative': ['Sequencer', 'LFO', 'VCO', 'Effect', 'VCF'],
            'percussion': ['VCO', 'Envelope', 'VCA', 'Effect'],
            'bass': ['VCO', 'VCF', 'VCA', 'Envelope'],
            'lead': ['VCO', 'VCF', 'Envelope', 'Effect'],
            'drone': ['VCO', 'Effect', 'VCF', 'LFO'],
            'techno': ['Sequencer', 'VCO', 'VCF', 'Envelope', 'Effect']
        }
        
        # Get priority types for the current patch type
        current_priorities = priority_types.get(patch_type, ['VCO', 'VCF', 'VCA', 'Effect'])
        
        # Add modules in priority order
        for priority_type in current_priorities:
            if priority_type in module_types:
                sorted_modules.extend(module_types[priority_type])
        
        # Add remaining modules
        for module_type, module_list in module_types.items():
            if module_type not in current_priorities:
                sorted_modules.extend(module_list)
        
        return sorted_modules
    
    def _find_relevant_patch_ideas(self, modules, patch_type, complexity):
        """
        Find relevant patch ideas from database
        
        Args:
            modules (list): Available modules
            patch_type (str): Patch type
            complexity (int): Desired complexity
            
        Returns:
            list: Relevant patch ideas
        """
        if self.db_connector:
            return self.db_connector.find_patch_ideas(modules, patch_type, complexity)
        else:
            return []
    
    def _generate_ambient_patch(self, modules, complexity):
        """
        Generate ambient patch ideas
        
        Args:
            modules (list): Available modules
            complexity (int): Desired complexity
            
        Returns:
            list: Generated patch ideas
        """
        ideas = []
        
        # Find sound sources (VCOs, noise, etc.)
        sound_sources = [m for m in modules if m['module_type'] == 'VCO']
        
        # Find modulation sources (LFOs, envelopes, etc.)
        modulation_sources = [m for m in modules if m['module_type'] in ['LFO', 'Envelope', 'Utility']]
        
        # Find effects (reverb, delay, etc.)
        effects = [m for m in modules if m['module_type'] == 'Effect']
        
        # Find mixers and VCAs
        mixers = [m for m in modules if m['module_type'] in ['Mixer', 'VCA']]
        
        # Generate patch idea if we have the necessary modules
        if sound_sources and effects:
            # Basic ambient patch
            idea = {
                'title': f"Ambient Texture with {sound_sources[0]['name']} and {effects[0]['name']}",
                'description': f"A spacious ambient patch using {sound_sources[0]['name']} as the sound source and {effects[0]['name']} for spatial effects.",
                'patch_type': 'ambient',
                'complexity': complexity,
                'connections': [],
                'control_settings': [],
                'sources': []
            }
            
            # Add connections
            if sound_sources and effects:
                # Find appropriate output from sound source
                source_output = next((conn for conn in sound_sources[0].get('connections', []) 
                                    if conn['type'] == 'output' and ('OUT' in conn['name'] or 'OUTPUT' in conn['name'].upper())), 
                                   {'id': 0, 'name': 'Output', 'type': 'output'})
                
                # Find appropriate input to effect
                effect_input = next((conn for conn in effects[0].get('connections', []) 
                                   if conn['type'] == 'input' and ('IN' in conn['name'] or 'INPUT' in conn['name'].upper())),
                                  {'id': 0, 'name': 'Input', 'type': 'input'})
                
                idea['connections'].append({
                    'source_module': {
                        'id': sound_sources[0]['id'],
                        'name': sound_sources[0]['name'],
                        'manufacturer': sound_sources[0]['manufacturer']
                    },
                    'source_connection': {
                        'id': source_output['id'],
                        'name': source_output['name'],
                        'type': 'output'
                    },
                    'target_module': {
                        'id': effects[0]['id'],
                        'name': effects[0]['name'],
                        'manufacturer': effects[0]['manufacturer']
                    },
                    'target_connection': {
                        'id': effect_input['id'],
                        'name': effect_input['name'],
                        'type': 'input'
                    },
                    'description': f"Route audio from {sound_sources[0]['name']} to {effects[0]['name']} for processing",
                    'cable_color': random.choice(self.cable_colors),
                    'importance': 5
                })
            
            # Add modulation if available
            if modulation_sources and sound_sources:
                # Find appropriate output from modulation source
                mod_output = next((conn for conn in modulation_sources[0].get('connections', []) 
                                 if conn['type'] == 'output' and ('OUT' in conn['name'] or 'OUTPUT' in conn['name'].upper())),
                                {'id': 0, 'name': 'Output', 'type': 'output'})
                
                # Find appropriate modulation input on sound source
                mod_input = next((conn for conn in sound_sources[0].get('connections', []) 
                                if conn['type'] == 'input' and any(x in conn['name'].upper() for x in ['FM', 'MOD', 'CV'])),
                               {'id': 0, 'name': 'FM Input', 'type': 'input'})
                
                idea['connections'].append({
                    'source_module': {
                        'id': modulation_sources[0]['id'],
                        'name': modulation_sources[0]['name'],
                        'manufacturer': modulation_sources[0]['manufacturer']
                    },
                    'source_connection': {
                        'id': mod_output['id'],
                        'name': mod_output['name'],
                        'type': 'output'
                    },
                    'target_module': {
                        'id': sound_sources[0]['id'],
                        'name': sound_sources[0]['name'],
                        'manufacturer': sound_sources[0]['manufacturer']
                    },
                    'target_connection': {
                        'id': mod_input['id'],
                        'name': mod_input['name'],
                        'type': 'input'
                    },
                    'description': f"Modulate {sound_sources[0]['name']} with {modulation_sources[0]['name']} for evolving textures",
                    'cable_color': random.choice(self.cable_colors),
                    'importance': 4
                })
            
            # Add mixer connection if available
            if effects and mixers:
                # Find appropriate output from effect
                effect_output = next((conn for conn in effects[0].get('connections', []) 
                                    if conn['type'] == 'output' and ('OUT' in conn['name'] or 'OUTPUT' in conn['name'].upper())),
                                   {'id': 0, 'name': 'Output', 'type': 'output'})
                
                # Find appropriate input on mixer
                mixer_input = next((conn for conn in mixers[0].get('connections', []) 
                                  if conn['type'] == 'input' and ('IN' in conn['name'] or 'INPUT' in conn['name'].upper())),
                                 {'id': 0, 'name': 'Input 1', 'type': 'input'})
                
                idea['connections'].append({
                    'source_module': {
                        'id': effects[0]['id'],
                        'name': effects[0]['name'],
                        'manufacturer': effects[0]['manufacturer']
                    },
                    'source_connection': {
                        'id': effect_output['id'],
                        'name': effect_output['name'],
                        'type': 'output'
                    },
                    'target_module': {
                        'id': mixers[0]['id'],
                        'name': mixers[0]['name'],
                        'manufacturer': mixers[0]['manufacturer']
                    },
                    'target_connection': {
                        'id': mixer_input['id'],
                        'name': mixer_input['name'],
                        'type': 'input'
                    },
                    'description': f"Route processed audio to {mixers[0]['name']} for final output",
                    'cable_color': random.choice(self.cable_colors),
                    'importance': 3
                })
            
            # Add control settings
            if effects:
                # Find mix/blend control if available
                mix_control = next((ctrl for ctrl in effects[0].get('controls', []) 
                                  if any(x in ctrl['name'].upper() for x in ['MIX', 'BLEND', 'WET'])),
                                 None)
                
                if mix_control:
                    idea['control_settings'].append({
                        'module': {
                            'id': effects[0]['id'],
                            'name': effects[0]['name'],
                            'manufacturer': effects[0]['manufacturer']
                        },
                        'control': {
                            'id': mix_control['id'],
                            'name': mix_control['name'],
                            'type': mix_control['type']
                        },
                        'value_numeric': 0.75,
                        'value_text': '3 o\'clock',
                        'description': f"Set {effects[0]['name']} {mix_control['name']} to 75% wet for spacious sound",
                        'importance': 4
                    })
            
            if sound_sources:
                # Find frequency/pitch control if available
                freq_control = next((ctrl for ctrl in sound_sources[0].get('controls', []) 
                                   if any(x in ctrl['name'].upper() for x in ['FREQ', 'PITCH', 'TUNE'])),
                                  None)
                
                if freq_control:
                    idea['control_settings'].append({
                        'module': {
                            'id': sound_sources[0]['id'],
                            'name': sound_sources[0]['name'],
                            'manufacturer': sound_sources[0]['manufacturer']
                        },
                        'control': {
                            'id': freq_control['id'],
                            'name': freq_control['name'],
                            'type': freq_control['type']
                        },
                        'value_numeric': 0.3,
                        'value_text': '9 o\'clock',
                        'description': f"Set {sound_sources[0]['name']} {freq_control['name']} to a low frequency for deep ambient tones",
                        'importance': 5
                    })
            
            # Add sources
            idea['sources'].append({
                'type': 'generated',
                'title': 'Generated based on available modules',
                'url': None,
                'relevance_score': 1.0
            })
            
            ideas.append(idea)
        
        return ideas
    
    def _generate_generative_patch(self, modules, complexity):
        """
        Generate generative patch ideas
        
        Args:
            modules (list): Available modules
            complexity (int): Desired complexity
            
        Returns:
            list: Generated patch ideas
        """
        ideas = []
        
        # Find sequencers and random sources
        sequencers = [m for m in modules if m['module_type'] == 'Sequencer']
        
        # Find sound sources (VCOs, noise, etc.)
        sound_sources = [m for m in modules if m['module_type'] == 'VCO']
        
        # Find modulation sources (LFOs, envelopes, etc.)
        modulation_sources = [m for m in modules if m['module_type'] in ['LFO', 'Envelope', 'Utility']]
        
        # Find effects (reverb, delay, etc.)
        effects = [m for m in modules if m['module_type'] == 'Effect']
        
        # Generate patch idea if we have the necessary modules
        if sound_sources and (sequencers or modulation_sources):
            # Basic generative patch
            title = "Generative Sequence"
            if sequencers:
                title += f" with {sequencers[0]['name']}"
            elif modulation_sources:
                title += f" with {modulation_sources[0]['name']}"
            
            idea = {
                'title': title,
                'description': "A self-generating patch that creates evolving melodies and textures without user intervention.",
                'patch_type': 'generative',
                'complexity': complexity,
                'connections': [],
                'control_settings': [],
                'sources': []
            }
            
            # Add connections based on available modules
            # This is a simplified implementation - a real one would be more sophisticated
            
            # Add sources
            idea['sources'].append({
                'type': 'generated',
                'title': 'Generated based on available modules',
                'url': None,
                'relevance_score': 1.0
            })
            
            ideas.append(idea)
        
        return ideas
    
    # Additional patch type generators would be implemented here
    def _generate_percussion_patch(self, modules, complexity):
        """Generate percussion patch ideas"""
        # Implementation for percussion patches
        return []
    
    def _generate_bass_patch(self, modules, complexity):
        """Generate bass patch ideas"""
        # Implementation for bass patches
        return []
    
    def _generate_lead_patch(self, modules, complexity):
        """Generate lead patch ideas"""
        # Implementation for lead patches
        return []
    
    def _generate_drone_patch(self, modules, complexity):
        """Generate drone patch ideas"""
        # Implementation for drone patches
        return []
    
    def _generate_techno_patch(self, modules, complexity):
        """Generate techno patch ideas"""
        # Implementation for techno patches
        return []


# Example usage
if __name__ == "__main__":
    generator = PatchGenerator()
    try:
        patch_ideas = generator.generate_patch_ideas("12345", "I want to create an ambient texture with evolving sounds")
        
        for idea in patch_ideas:
            print(f"\nPatch Idea: {idea['title']}")
            print(f"Description: {idea['description']}")
            print(f"Type: {idea['patch_type']}, Complexity: {idea['complexity']}")
            
            print("\nConnections:")
            for conn in idea['connections']:
                print(f"- {conn['source_module']['name']} ({conn['source_connection']['name']}) → "
                      f"{conn['target_module']['name']} ({conn['target_connection']['name']})")
                print(f"  {conn['description']}")
            
            print("\nControl Settings:")
            for ctrl in idea['control_settings']:
                print(f"- {ctrl['module']['name']} {ctrl['control']['name']} = {ctrl['value_text']}")
                print(f"  {ctrl['description']}")
    
    except Exception as e:
        print(f"Error: {e}")
