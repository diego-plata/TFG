from flask import Blueprint

# Crear un blueprint para dispositivos
dispositivos_bp = Blueprint('dispositivos', __name__, template_folder='templates')
usuarios_bp = Blueprint('usuarios', __name__)



