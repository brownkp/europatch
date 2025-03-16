from app import db
from datetime import datetime

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
    
    # Relationships
    connections = db.relationship('ModuleConnection', backref='module', cascade='all, delete-orphan')
    controls = db.relationship('ModuleControl', backref='module', cascade='all, delete-orphan')
    forum_sources = db.relationship('ForumSource', backref='module')
    
    def __repr__(self):
        return f"<Module(name='{self.name}', manufacturer='{self.manufacturer}')>"


class ModuleConnection(db.Model):
    __tablename__ = 'module_connections'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'))
    connection_type = db.Column(db.String(50), nullable=False)  # 'input', 'output'
    connection_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    voltage_range = db.Column(db.String(50))  # e.g., '0-5V', '±10V'
    is_cv = db.Column(db.Boolean, default=False)
    is_gate = db.Column(db.Boolean, default=False)
    is_audio = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ModuleConnection(module_id={self.module_id}, name='{self.connection_name}', type='{self.connection_type}')>"


class ModuleControl(db.Model):
    __tablename__ = 'module_controls'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'))
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
    
    def __repr__(self):
        return f"<ModuleControl(module_id={self.module_id}, name='{self.control_name}', type='{self.control_type}')>"


class PatchIdea(db.Model):
    __tablename__ = 'patch_ideas'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    patch_type = db.Column(db.String(100))  # e.g., 'ambient', 'generative', 'percussion'
    complexity = db.Column(db.Integer)  # 1-5 scale
    source_type = db.Column(db.String(50))  # 'manual', 'reddit', 'modwiggler', 'generated'
    source_url = db.Column(db.String(255))
    source_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    connections = db.relationship('PatchConnection', backref='patch', cascade='all, delete-orphan')
    control_settings = db.relationship('PatchControlSetting', backref='patch', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<PatchIdea(title='{self.title}', type='{self.patch_type}')>"


class PatchConnection(db.Model):
    __tablename__ = 'patch_connections'
    
    id = db.Column(db.Integer, primary_key=True)
    patch_id = db.Column(db.Integer, db.ForeignKey('patch_ideas.id', ondelete='CASCADE'))
    source_module_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'))
    source_connection_id = db.Column(db.Integer, db.ForeignKey('module_connections.id', ondelete='CASCADE'))
    target_module_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'))
    target_connection_id = db.Column(db.Integer, db.ForeignKey('module_connections.id', ondelete='CASCADE'))
    description = db.Column(db.Text)
    cable_color = db.Column(db.String(50))  # for visualization
    importance = db.Column(db.Integer)  # 1-5 scale
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    source_module = db.relationship('Module', foreign_keys=[source_module_id])
    target_module = db.relationship('Module', foreign_keys=[target_module_id])
    source_connection = db.relationship('ModuleConnection', foreign_keys=[source_connection_id])
    target_connection = db.relationship('ModuleConnection', foreign_keys=[target_connection_id])
    
    def __repr__(self):
        return f"<PatchConnection(patch_id={self.patch_id}, source={self.source_module_id}, target={self.target_module_id})>"


class PatchControlSetting(db.Model):
    __tablename__ = 'patch_control_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    patch_id = db.Column(db.Integer, db.ForeignKey('patch_ideas.id', ondelete='CASCADE'))
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'))
    control_id = db.Column(db.Integer, db.ForeignKey('module_controls.id', ondelete='CASCADE'))
    value_numeric = db.Column(db.Float)
    value_text = db.Column(db.String(100))  # e.g., "3 o'clock", "fully clockwise"
    description = db.Column(db.Text)
    importance = db.Column(db.Integer)  # 1-5 scale
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    module = db.relationship('Module')
    control = db.relationship('ModuleControl')
    
    def __repr__(self):
        return f"<PatchControlSetting(patch_id={self.patch_id}, module_id={self.module_id}, control_id={self.control_id})>"


class ForumSource(db.Model):
    __tablename__ = 'forum_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    source_type = db.Column(db.String(50), nullable=False)  # 'reddit', 'modwiggler', etc.
    url = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'))
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)
    relevance_score = db.Column(db.Float)  # 0-1 scale
    
    __table_args__ = (db.UniqueConstraint('source_type', 'url'),)
    
    def __repr__(self):
        return f"<ForumSource(source_type='{self.source_type}', module_id={self.module_id})>"


class UserRack(db.Model):
    __tablename__ = 'user_racks'
    
    id = db.Column(db.Integer, primary_key=True)
    modulargrid_url = db.Column(db.String(255), nullable=False)
    modulargrid_id = db.Column(db.String(100))
    rack_name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    modules = db.relationship('RackModule', backref='rack', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<UserRack(id={self.id}, name='{self.rack_name}')>"


class RackModule(db.Model):
    __tablename__ = 'rack_modules'
    
    id = db.Column(db.Integer, primary_key=True)
    rack_id = db.Column(db.Integer, db.ForeignKey('user_racks.id', ondelete='CASCADE'))
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'))
    position_x = db.Column(db.Integer)
    position_y = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    module = db.relationship('Module')
    
    __table_args__ = (db.UniqueConstraint('rack_id', 'module_id', 'position_x', 'position_y'),)
    
    def __repr__(self):
        return f"<RackModule(rack_id={self.rack_id}, module_id={self.module_id})>"
