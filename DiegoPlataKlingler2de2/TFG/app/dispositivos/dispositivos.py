import datetime
from flask import Blueprint, jsonify, render_template, request
from app.utils import login_required  
import os
from subprocess import Popen
from pymongo import MongoClient
from app import importar_swagger
from flasgger import swag_from

MONGO_HOST = "localhost"
MONGO_PORT = 27017
DB_NAME = "riego"
usuario = "riego"
contrasena = "riego00"
dispositivos_bp = Blueprint('dispositivos', __name__, template_folder='templates')


@dispositivos_bp.route('/ejecutar_script')
@swag_from(importar_swagger)
def ejecutar_script():
    run_leer_disp_script()
    return 'Script ejecutado correctamente'

def run_leer_disp_script():
    script_path = os.path.join(os.path.dirname(__file__), 'leer_disp.py')
    print("Ejecutando leer_disp.py:", script_path)
    process = Popen(['python', script_path])
    return process

@dispositivos_bp.route('/colecciones/<filename>')
@swag_from(importar_swagger)
def serve_static_files(filename):
    try:
        file_path = os.path.join("app", "colecciones", filename)
        with open(file_path, "rb") as file:
            file_content = file.read()
        return file_content
    except FileNotFoundError:
        return "Archivo no encontrado", 404

@dispositivos_bp.route('/cargar_html')
@swag_from(importar_swagger)
def cargar_html():
    try:
        nombre_dispositivo = request.args.get('nombre') #nombre que le llega por para en la url ?nombre=piscina
        datos = obtener_datos_mongo(nombre_dispositivo)
        if datos:
            return jsonify(datos)
        else:
            print("No hay nombre en la solicitud")
            return jsonify({'error': 'No hay nombre en la solicitud'}), 400
    except Exception as e:
        print(f"Error HTML: {e}")
        return jsonify({'error': 'Error HTML'}), 500

def obtener_datos_mongo(nombre_coleccion):
    try:
        # Conexión a MongoDB
        client = MongoClient(MONGO_HOST, MONGO_PORT, username=usuario, password=contrasena)
        db = client[DB_NAME]

        # Obtener los datos de la colección especificada por nombre
        collection_data = list(db[nombre_coleccion].find())

        # Preparar los datos para las gráficas
        datos = {
            'success': True,
            'humedad_ambiente': {'x': [], 'y': []},
            'temperatura_ambiente': {'x': [], 'y': []},
            'humedad_suelo': {'x': [], 'y': []}
        }

        # Llenar los datos
        for data in collection_data:#asignamos cada fecha a su dato en las tres graficas
            fecha_hora = data['fecha'] + ' ' + data['hora']
            datos['humedad_ambiente']['x'].append(fecha_hora)
            datos['humedad_ambiente']['y'].append(data['humedad_ambiente'])
            datos['temperatura_ambiente']['x'].append(fecha_hora)
            datos['temperatura_ambiente']['y'].append(data['temperatura_ambiente'])
            datos['humedad_suelo']['x'].append(fecha_hora)
            datos['humedad_suelo']['y'].append(data['humedad_suelo'])

        # Cerrar la conexión a MongoDB
        client.close()

        return datos

    except Exception as e:
        print("Error al obtener datos de MongoDB:", e)
        return None

