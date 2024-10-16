import subprocess
from app import create_app, db
from app.usuarios.models import Usuario
from flask_login import LoginManager
from flasgger import Swagger
# Función para ejecutar los otros scripts
def ejecutar_scripts():
    # Ejecutar script1.py
    subprocess.Popen(["python", "registro_disp.py"])
    # Ejecutar script2.py
    subprocess.Popen(["python", "GESTOR_MSG.py"])

# Crear la aplicación Flask
app = create_app()
swagger = Swagger(app)
# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # Cargar el usuario desde la base de datos
    user = Usuario.query.get(int(user_id))
    print("Usuario cargado:", user)  # Agregar esta línea para depurar
    return user

if __name__ == '__main__':
    # Ejecutar los otros scripts al inicio
    #ejecutar_scripts()
    # Ejecutar la aplicación Flask
    app.run(debug=True)
