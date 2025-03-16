"""
Script to initialize the database with mock data for testing.
"""
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from src.models import db, Module, ModuleConnection, ModuleControl, PatchIdea, PatchModule, PatchConnection, PatchControlSetting, UserRack, RackModule, ForumSource

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/eurorack_patch_generator')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def create_mock_data():
    """Create mock data for testing the application."""
    # Create modules
    modules = [
        Module(
            name="Plaits",
            manufacturer="Mutable Instruments",
            hp_width=12,
            module_type="Oscillator",
            description="Macro-oscillator with multiple synthesis models",
            manual_url="https://mutable-instruments.net/modules/plaits/manual/",
            image_url="https://mutable-instruments.net/modules/plaits/images/plaits_front.jpg",
            modulargrid_url="https://www.modulargrid.net/e/mutable-instruments-plaits"
        ),
        Module(
            name="Rings",
            manufacturer="Mutable Instruments",
            hp_width=14,
            module_type="Resonator",
            description="Modal resonator",
            manual_url="https://mutable-instruments.net/modules/rings/manual/",
            image_url="https://mutable-instruments.net/modules/rings/images/rings_front.jpg",
            modulargrid_url="https://www.modulargrid.net/e/mutable-instruments-rings"
        ),
        Module(
            name="Clouds",
            manufacturer="Mutable Instruments",
            hp_width=18,
            module_type="Granular Processor",
            description="Texture synthesizer",
            manual_url="https://mutable-instruments.net/modules/clouds/manual/",
            image_url="https://mutable-instruments.net/modules/clouds/images/clouds_front.jpg",
            modulargrid_url="https://www.modulargrid.net/e/mutable-instruments-clouds"
        ),
        Module(
            name="Maths",
            manufacturer="Make Noise",
            hp_width=20,
            module_type="Function Generator",
            description="Dual function generator with mixing and logic",
            manual_url="http://www.makenoisemusic.com/manuals/MATHSmanual.pdf",
            image_url="http://www.makenoisemusic.com/thumbs/modules/maths-panel-thumb.jpg",
            modulargrid_url="https://www.modulargrid.net/e/make-noise-maths"
        ),
        Module(
            name="Pamela's NEW Workout",
            manufacturer="ALM Busy Circuits",
            hp_width=8,
            module_type="Clock",
            description="Advanced clocking module with multiple outputs",
            manual_url="https://busycircuits.com/alm017/",
            image_url="https://busycircuits.com/images/alm017.jpg",
            modulargrid_url="https://www.modulargrid.net/e/alm-busy-circuits-pamela-s-new-workout"
        )
    ]
    
    for module in modules:
        db.session.add(module)
    
    db.session.commit()
    
    # Create module connections
    connections = [
        # Plaits connections
        ModuleConnection(module_id=1, name="OUT", connection_type="output", description="Main audio output"),
        ModuleConnection(module_id=1, name="AUX", connection_type="output", description="Auxiliary audio output"),
        ModuleConnection(module_id=1, name="TRIG", connection_type="input", description="Trigger input"),
        ModuleConnection(module_id=1, name="PITCH", connection_type="input", description="V/Oct pitch input"),
        ModuleConnection(module_id=1, name="TIMBRE", connection_type="input", description="Timbre CV input"),
        ModuleConnection(module_id=1, name="MODEL", connection_type="input", description="Model selection CV input"),
        
        # Rings connections
        ModuleConnection(module_id=2, name="IN", connection_type="input", description="Audio input"),
        ModuleConnection(module_id=2, name="OUT", connection_type="output", description="Main audio output"),
        ModuleConnection(module_id=2, name="ODD", connection_type="output", description="Odd harmonics output"),
        ModuleConnection(module_id=2, name="EVEN", connection_type="output", description="Even harmonics output"),
        ModuleConnection(module_id=2, name="STRUM", connection_type="input", description="Excitation input"),
        ModuleConnection(module_id=2, name="V/OCT", connection_type="input", description="V/Oct pitch input"),
        ModuleConnection(module_id=2, name="DAMPING", connection_type="input", description="Damping CV input"),
        ModuleConnection(module_id=2, name="POSITION", connection_type="input", description="Position CV input"),
        
        # Clouds connections
        ModuleConnection(module_id=3, name="IN L", connection_type="input", description="Left audio input"),
        ModuleConnection(module_id=3, name="IN R", connection_type="input", description="Right audio input"),
        ModuleConnection(module_id=3, name="OUT L", connection_type="output", description="Left audio output"),
        ModuleConnection(module_id=3, name="OUT R", connection_type="output", description="Right audio output"),
        ModuleConnection(module_id=3, name="TRIG", connection_type="input", description="Trigger input"),
        ModuleConnection(module_id=3, name="FREEZE", connection_type="input", description="Freeze input"),
        ModuleConnection(module_id=3, name="POSITION", connection_type="input", description="Position CV input"),
        ModuleConnection(module_id=3, name="SIZE", connection_type="input", description="Size CV input"),
        ModuleConnection(module_id=3, name="DENSITY", connection_type="input", description="Density CV input"),
        ModuleConnection(module_id=3, name="TEXTURE", connection_type="input", description="Texture CV input"),
        
        # Maths connections
        ModuleConnection(module_id=4, name="CH 1 OUT", connection_type="output", description="Channel 1 output"),
        ModuleConnection(module_id=4, name="CH 4 OUT", connection_type="output", description="Channel 4 output"),
        ModuleConnection(module_id=4, name="CH 1 TRIG", connection_type="input", description="Channel 1 trigger input"),
        ModuleConnection(module_id=4, name="CH 4 TRIG", connection_type="input", description="Channel 4 trigger input"),
        ModuleConnection(module_id=4, name="OR", connection_type="output", description="OR logic output"),
        ModuleConnection(module_id=4, name="SUM", connection_type="output", description="SUM output"),
        ModuleConnection(module_id=4, name="UNITY", connection_type="output", description="UNITY output"),
        ModuleConnection(module_id=4, name="INV", connection_type="output", description="Inverted output"),
        
        # Pamela's NEW Workout connections
        ModuleConnection(module_id=5, name="OUT 1", connection_type="output", description="Clock output 1"),
        ModuleConnection(module_id=5, name="OUT 2", connection_type="output", description="Clock output 2"),
        ModuleConnection(module_id=5, name="OUT 3", connection_type="output", description="Clock output 3"),
        ModuleConnection(module_id=5, name="OUT 4", connection_type="output", description="Clock output 4"),
        ModuleConnection(module_id=5, name="OUT 5", connection_type="output", description="Clock output 5"),
        ModuleConnection(module_id=5, name="OUT 6", connection_type="output", description="Clock output 6"),
        ModuleConnection(module_id=5, name="OUT 7", connection_type="output", description="Clock output 7"),
        ModuleConnection(module_id=5, name="OUT 8", connection_type="output", description="Clock output 8"),
        ModuleConnection(module_id=5, name="RESET", connection_type="input", description="Reset input")
    ]
    
    for connection in connections:
        db.session.add(connection)
    
    db.session.commit()
    
    # Create module controls
    controls = [
        # Plaits controls
        ModuleControl(module_id=1, control_type="knob", control_name="MODEL", description="Selects synthesis model", min_value=0, max_value=15, default_value=0),
        ModuleControl(module_id=1, control_type="knob", control_name="TIMBRE", description="Controls timbre/harmonic content", min_value=0, max_value=100, default_value=50),
        ModuleControl(module_id=1, control_type="knob", control_name="FREQ", description="Controls frequency/pitch", min_value=0, max_value=100, default_value=50),
        ModuleControl(module_id=1, control_type="knob", control_name="HARMONICS", description="Controls harmonic structure", min_value=0, max_value=100, default_value=50),
        ModuleControl(module_id=1, control_type="knob", control_name="MORPH", description="Morphs between variations of the model", min_value=0, max_value=100, default_value=50),
        ModuleControl(module_id=1, control_type="switch", control_name="TRIGGER MODE", description="Selects trigger mode", min_value=0, max_value=1, default_value=0),
        
        # Rings controls
        ModuleControl(module_id=2, control_type="knob", control_name="FREQUENCY", description="Controls frequency/pitch", min_value=0, max_value=100, default_value=50),
        ModuleControl(module_id=2, control_type="knob", control_name="STRUCTURE", description="Controls resonator structure", min_value=0, max_value=100, default_value=50),
        ModuleControl(module_id=2, control_type="knob", control_name="BRIGHTNESS", description="Controls brightness/damping", min_value=0, max_value=100, default_value=50),
        ModuleControl(module_id=2, control_type="knob", control_name="POSITION", description="Controls excitation position", min_value=0, max_value=100, default_value=50),
        ModuleControl(module_id=2, control_type="switch", control_name="RESONATOR", description="Selects resonator type", min_value=0, max_value=2, default_value=0),
        ModuleControl(module_id=2, control_type="switch", control_name="POLYPHONY", description="Selects polyphony mode", min_value=0, max_value=2, default_value=0),
        
        # Clouds controls
        ModuleControl(module_id=3, control_type="knob", control_name="POSITION", description="Controls playback position", min_value=0, max_value=100, default_value=50),
        ModuleControl(module_id=3, control_type="knob", control_name="SIZE", description="Controls grain size", min_value=0, max_value=100, default_value=50),
        ModuleControl(module_id=3, control_type="knob", control_name="DENSITY", description="Controls grain density", min_value=0, max_value=100, default_value=50),
        ModuleControl(module_id=3, control_type="knob", control_name="TEXTURE", description="Controls grain texture", min_value=0, max_value=100, default_value=50),
        ModuleControl(module_id=3, control_type="knob", control_name="BLEND", description="Controls wet/dry mix", min_value=0, max_value=100, default_value=50),
        ModuleControl(module_id=3, control_type="knob", control_name="SPREAD", description="Controls stereo spread", min_value=0, max_value=100, default_value=50),
        ModuleControl(module_id=3, control_type="knob", control_name="FEEDBACK", description="Controls feedback amount", min_value=0, max_value=100, default_value=0),
        ModuleControl(module_id=3, control_type="knob", control_name="REVERB", description="Controls reverb amount", min_value=0, max_value=100, default_value=0),
        ModuleControl(module_id=3, control_type="switch", control_name="QUALITY", description="Selects audio quality", min_value=0, max_value=1, default_value=0),
        ModuleControl(module_id=3, control_type="switch", control_name="MODE", description="Selects processing mode", min_value=0, max_value=3, default_value=0),
        
        # Maths controls
        ModuleControl(module_id=4, control_type="knob", control_name="RISE 1", description="Channel 1 rise time", min_value=0, max_value=100, default_value=50),
        ModuleControl(module_id=4, control_type="knob", control_name="FALL 1", description="Channel 1 fall time", min_value=0, max_value=100, default_value=50),
        ModuleControl(module_id=4, control_type="knob", control_name="RISE 4", description="Channel 4 rise time", min_value=0, max_value=100, default_value=50),
        ModuleControl(module_id=4, control_type="knob", control_name="FALL 4", description="Channel 4 fall time", min_value=0, max_value=100, default_value=50),
        ModuleControl(module_id=4, control_type="knob", control_name="CHANNEL 1", description="Channel 1 level", min_value=0, max_value=100, default_value=50, is_attenuverter=True),
        ModuleControl(module_id=4, control_type="knob", control_name="CHANNEL 2", description="Channel 2 level", min_value=0, max_value=100, default_value=50, is_attenuverter=True),
        ModuleControl(module_id=4, control_type="knob", control_name="CHANNEL 3", description="Channel 3 level", min_value=0, max_value=100, default_value=50, is_attenuverter=True),
        ModuleControl(module_id=4, control_type="knob", control_name="CHANNEL 4", description="Channel 4 level", min_value=0, max_value=100, default_value=50, is_attenuverter=True),
        ModuleControl(module_id=4, control_type="switch", control_name="CYCLE 1", description="Channel 1 cycle mode", min_value=0, max_value=1, default_value=0),
        ModuleControl(module_id=4, control_type="switch", control_name="CYCLE 4", description="Channel 4 cycle mode", min_value=0, max_value=1, default_value=0),
        
        # Pamela's NEW Workout controls
        ModuleControl(module_id=5, control_type="knob", control_name="BPM", description="Master tempo", min_value=1, max_value=300, default_value=120),
        ModuleControl(module_id=5, control_type="knob", control_name="DIVISION 1", description="Clock division for output 1", min_value=1, max_value=64, default_value=1),
        ModuleControl(module_id=5, control_type="knob", control_name="DIVISION 2", description="Clock division for output 2", min_value=1, max_value=64, default_value=2),
        ModuleControl(module_id=5, control_type="knob", control_name="DIVISION 3", description="Clock division for output 3", min_value=1, max_value=64, default_value=4),
        ModuleControl(module_id=5, control_type="knob", control_name="DIVISION 4", description="Clock division for output 4", min_value=1, max_value=64, default_value=8),
        ModuleControl(module_id=5, control_type="knob", control_name="DIVISION 5", description="Clock division for output 5", min_value=1, max_value=64, default_value=16),
        ModuleControl(module_id=5, control_type="knob", control_name="DIVISION 6", description="Clock division for output 6", min_value=1, max_value=64, default_value=32),
        ModuleControl(module_id=5, control_type="knob", control_name="DIVISION 7", description="Clock division for output 7", min_value=1, max_value=64, default_value=3),
        ModuleControl(module_id=5, control_type="knob", control_name="DIVISION 8", description="Clock division for output 8", min_value=1, max_value=64, default_value=6)
    ]
    
    for control in controls:
        db.session.add(control)
    
    db.session.commit()
    
    # Create patch ideas
    patch_ideas = [
        PatchIdea(
            title="Ambient Clouds Texture",
            description="A generative ambient patch that creates evolving textures using Clouds to process sounds from Plaits.",
            patch_type="ambient",
            complexity=3,
            source_type="generated",
            source_text="This patch uses Plaits as a sound source, feeding into Clouds for granular processing. Maths provides modulation for both modules, creating slowly evolving textures."
        ),
        PatchIdea(
            title="Plucked Resonato<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>