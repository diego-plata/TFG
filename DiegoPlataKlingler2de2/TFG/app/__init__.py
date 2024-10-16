import os
from flask import Flask, json
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from config import Config

db = SQLAlchemy()
ficherin_swagger = os.path.join(os.path.dirname(__file__), 'static')
swagger_file = os.path.join(ficherin_swagger, 'fichero_swag.json')
with open(swagger_file, 'r') as f:
    importar_swagger = json.load(f)
def create_app():
    app = Flask(__name__)
    
    app.config.from_object(Config)
    
    db.init_app(app)
    app.config['SESSION_TYPE'] = 'filesystem'  # Almacena las sesiones en el sistema de archivos en lugar de en ram
    Session(app)  # Configurar Flask-Session

    from .usuarios.usuarios import usuarios_bp
    from .dispositivos.dispositivos import dispositivos_bp
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(dispositivos_bp)
    # app.register_blueprint(dispositivos_bp)  
    return app
