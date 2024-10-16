from datetime import datetime
from app import db

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    mail = db.Column(db.String(100), unique=True, nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    dispositivos_registrados_id = db.Column(db.Text)

    def __repr__(self):
        return f'<Usuario {self.username}>'

    def is_active(self):
        return True
    
    def get_id(self):
        return str(self.id)
    
    def is_authenticated(self):
        return True