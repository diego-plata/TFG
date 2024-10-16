import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')  #clave_secreta. o bien una variable de entorno que no está definida en este pc o la contrasñea. se ha borrado la contraseña por seguridad
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://usuario:password@localhost/usuarios_tfg'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
