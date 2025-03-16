"""
Database models for the Eurorack Patch Generator application.
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

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
    forum_sources = db.relationship('ForumSource', backref='module', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'manufacturer': self.manufacturer,
            'hp_width': self.hp_width,
            'module_type': self.module_type,
            'description': self.description,
            'manual_url': self.manual_url,
            'image_url': self.image_url,
            'modulargrid_url': self.modulargrid_url,
            'connections': [conn.to_dict() for conn in self.connections],
            'controls': [ctrl.to_dict() for ctrl in self.controls]
        }

class ModuleConnection(db.Model):
    __tablename__ = 'module_connections'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    connection_type = db.Column(db.String(50), nullable=False)  # 'input', 'output', 'cv', 'gate', etc.
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'module_id': self.module_id,
            'name': self.name,
            'connection_type': self.connection_type,
            'description': self.description
        }

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

    def to_dict(self):
        return {
            'id': self.id,
            'module_id': self.module_id,
            'control_type': self.control_type,
            'control_name': self.control_name,
            'description': self.description,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'default_value': self.default_value,
            'is_attenuator': self.is_attenuator,
            'is_attenuverter': self.is_attenuverter
        }

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
    
    modules = db.relationship('PatchModule', backref='patch', lazy=True, cascade='all, delete-orphan')
    connections = db.relationship('PatchConnection', backref='patch', lazy=True, cascade='all, delete-orphan')
    control_settings = db.relationship('PatchControlSetting', backref='patch', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'patch_type': self.patch_type,
            'complexity': self.complexity,
            'source_type': self.source_type,
            'source_url': self.source_url,
            'modules': [m.to_dict() for m in self.modules],
            'connections': [c.to_dict() for c in self.connections],
            'control_settings': [s.to_dict() for s in self.control_settings]
        }

class PatchModule(db.Model):
    __tablename__ = 'patch_modules'
    
    id = db.Column(db.Integer, primary_key=True)
    patch_id = db.Column(db.Integer, db.ForeignKey('patch_ideas.id', ondelete='CASCADE'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'), nullable=False)
    importance = db.Column(db.Integer)  # 1-5 scale, how central the module is to the patch
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    module = db.relationship('Module')

    def to_dict(self):
        return {
            'id': self.id,
            'patch_id': self.patch_id,
            'module_id': self.module_id,
            'module': self.module.to_dict() if self.module else None,
            'importance': self.importance
        }

class PatchConnection(db.Model):
    __tablename__ = 'patch_connections'
    
    id = db.Column(db.Integer, primary_key=True)
    patch_id = db.Column(db.Integer, db.ForeignKey('patch_ideas.id', ondelete='CASCADE'), nullable=False)
    source_module_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'), nullable=False)
    source_connection_id = db.Column(db.Integer, db.ForeignKey('module_connections.id', ondelete='CASCADE'), nullable=False)
    target_module_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'), nullable=False)
    target_connection_id = db.Column(db.Integer, db.ForeignKey('module_connections.id', ondelete='CASCADE'), nullable=False)
    cable_color = db.Column(db.String(50))  # for visualization
    description = db.Column(db.Text)
    importance = db.Column(db.Integer)  # 1-5 scale
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    source_module = db.relationship('Module', foreign_keys=[source_module_id])
    source_connection = db.relationship('ModuleConnection', foreign_keys=[source_connection_id])
    target_module = db.relationship('Module', foreign_keys=[target_module_id])
    target_connection = db.relationship('ModuleConnection', foreign_keys=[target_connection_id])

    def to_dict(self):
        return {
            'id': self.id,
            'patch_id': self.patch_id,
            'source_module': self.source_module.name if self.source_module else None,
            'source_connection': self.source_connection.name if self.source_connection else None,
            'target_module': self.target_module.name if self.target_module else None,
            'target_connection': self.target_connection.name if self.target_connection else None,
            'cable_color': self.cable_color,
            'description': self.description,
            'importance': self.importance
        }

class PatchControlSetting(db.Model):
    __tablename__ = 'patch_control_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    patch_id = db.Column(db.Integer, db.ForeignKey('patch_ideas.id', ondelete='CASCADE'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'), nullable=False)
    control_id = db.Column(db.Integer, db.ForeignKey('module_controls.id', ondelete='CASCADE'), nullable=False)
    value_numeric = db.Column(db.Float)
    value_text = db.Column(db.String(100))  # e.g., "3 o'clock", "fully clockwise"
    description = db.Column(db.Text)
    importance = db.Column(db.Integer)  # 1-5 scale
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    module = db.relationship('Module')
    control = db.relationship('ModuleControl')

    def to_dict(self):
        return {
            'id': self.id,
            'patch_id': self.patch_id,
            'module': self.module.name if self.module else None,
            'control': self.control.control_name if self.control else None,
            'value_numeric': self.value_numeric,
            'value_text': self.value_text,
            'description': self.description,
            'importance': self.importance
        }

class UserRack(db.Model):
    __tablename__ = 'user_racks'
    
    id = db.Column(db.Integer, primary_key=True)
    modulargrid_url = db.Column(db.String(255), nullable=False)
    modulargrid_id = db.Column(db.String(100))
    rack_name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    
    modules = db.relationship('RackModule', backref='rack', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'modulargrid_url': self.modulargrid_url,
            'modulargrid_id': self.modulargrid_id,
            'rack_name': self.rack_name,
            'created_at': self.created_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat(),
            'modules': [m.to_dict() for m in self.modules]
        }

class RackModule(db.Model):
    __tablename__ = 'rack_modules'
    
    id = db.Column(db.Integer, primary_key=True)
    rack_id = db.Column(db.Integer, db.ForeignKey('user_racks.id', ondelete='CASCADE'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'), nullable=False)
    position_x = db.Column(db.Integer)
    position_y = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    module = db.relationship('Module')

    def to_dict(self):
        return {
            'id': self.id,
            'rack_id': self.rack_id,
            'module_id': self.module_id,
            'module': self.module.to_dict() if self.module else None,
            'position_x': self.position_x,
            'position_y': self.position_y
        }

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

    def to_dict(self):
        return {
            'id': self.id,
            'source_type': self.source_type,
            'url': self.url,
            'title': self.title,
            'content': self.content,
            'module_id': self.module_id,
            'scraped_at': self.scraped_at.isoformat(),
            'relevance_score': self.relevance_score
        }
