import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient
import datetime
import random
import paho.mqtt.client as mqtt
import time
import mariadb
from mariadb import Error as MariaDBError

MQTT_BROKER_HOST = "192.168.1.58"
MQTT_BROKER_PORT = 1883
MQTT_TOPIC = "/sensor/#"
MQTT_RIEGO_TOPIC = "riego"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:2002@localhost/usuarios_tfg'
db = SQLAlchemy(app)

class Dispositivo(db.Model):
    __tablename__ = 'dispositivo'
    identificador = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    ip = db.Column(db.String(15))
    es_interior = db.Column(db.Boolean)
    ciudad = db.Column(db.String(15))

def obtener_prediccion_lluvia(ciudad):
    apiKey = 'e27a2065ccfe1b3bbdf9ddcb44fbe220'
    units = 'metric'
    apiUrl = f"https://api.openweathermap.org/data/2.5/forecast?q={ciudad}&appid={apiKey}&units={units}"

    response = requests.get(apiUrl)

    if response.status_code == 200:
        data = response.json()
        rain = 0
        for forecast in data["list"][:2]:
            rain_probability = forecast.get("pop", 0) * 100
            if rain_probability > 65:
                if rain_probability > rain:
                    rain = rain_probability
        return rain
    else:
        print("Error al obtener el pronóstico del tiempo:", response.status_code)
        return None  

def conectar_mariadb():
    global mariadb_connection
    try:
        mariadb_connection = mariadb.connect(
            user="root",
            password="2002",
            host="localhost",
            port=3306,
            database="usuarios_tfg"
        )
        print("Conectado a MariaDB")
    except mariadb.Error as e:
        print(f"Error al conectar a MariaDB: {e}")

def desconectar_mariadb():
    global mariadb_connection
    if mariadb_connection:
        mariadb_connection.close()
        print("Desconectado de MariaDB")

def obtener_dispositivos():
    global dispositivos
    dispositivos = {}
    try:
        with mariadb_connection.cursor() as cursor:
            cursor.execute("SELECT identificador, nombre FROM dispositivo")
            for identificador, nombre in cursor:
                dispositivos[identificador] = nombre
        print("Dispositivos obtenidos de MariaDB")
        print(dispositivos)
    except mariadb.Error as e:
        print(f"Error al obtener dispositivos de MariaDB: {e}")
    finally:
        return dispositivos

while True:
    # Conectar a MariaDB y obtener los dispositivos
    conectar_mariadb()
    dispositivos_dict = obtener_dispositivos()
    desconectar_mariadb()

    # Diccionario para almacenar las probabilidades de lluvia de los dispositivos
    dispositivos_lluvia = {}

    with app.app_context():
        for dispositivo_id, dispositivo_nombre in dispositivos_dict.items():
            dispositivo = Dispositivo.query.get(dispositivo_id)
            if dispositivo:
                lluvia = obtener_prediccion_lluvia(dispositivo.ciudad) if not dispositivo.es_interior else 0
                dispositivos_lluvia[dispositivo.identificador] = {
                    "identificador": dispositivo.identificador,
                    "dispositivo": dispositivo_nombre,
                    "probabilidad_lluvia": lluvia,
                    "media_temperaturas": 0,  # Inicializamos las medias en 0
                    "media_humedad_ambiente": 0,
                    "media_humedad_suelo": 0
                }

                # Obtener los últimos datos de MongoDB y calcular las medias
                MONGO_HOST = "localhost"
                MONGO_PORT = 27017
                usuario = "riego"
                contrasena = "riego00"

                cliente_mongo = MongoClient(MONGO_HOST, MONGO_PORT, username=usuario, password=contrasena)
                db_mongo = cliente_mongo['riego']

                if dispositivo_nombre:  # Verificar que el nombre del dispositivo no esté vacío
                    collection = db_mongo[dispositivo_nombre]
                    datos = collection.find().sort("_id", -1).limit(2)

                    media_temperaturas = 0
                    media_humedad_ambiente = 0
                    media_humedad_suelo = 0
                    num_datos = 0  # Contador para asegurarnos de que dividimos por el número correcto de datos

                    for dato in datos:
                        media_temperaturas += dato.get("temperatura_ambiente", 0)
                        media_humedad_ambiente += dato.get("humedad_ambiente", 0)
                        media_humedad_suelo += dato.get("humedad_suelo", 0)
                        num_datos += 1

                    if num_datos > 0:
                        media_temperaturas /= num_datos
                        media_humedad_ambiente /= num_datos
                        media_humedad_suelo /= num_datos

                    dispositivos_lluvia[dispositivo.identificador].update({
                        "media_temperaturas": media_temperaturas,
                        "media_humedad_ambiente": media_humedad_ambiente,
                        "media_humedad_suelo": media_humedad_suelo
                    })

                    print(f"Identificador: {dispositivo.identificador}")
                    print(f"Dispositivo: {dispositivo_nombre}")
                    print(f"Probabilidad de lluvia: {lluvia}")
                    print(f"Media de temperaturas: {media_temperaturas}")
                    print(f"Media de humedad ambiente: {media_humedad_ambiente}")
                    print(f"Media de humedad suelo: {media_humedad_suelo}")
                    print("-" * 50)

    # Conexión al broker MQTT y procesamiento de la información de los dispositivos
    client = mqtt.Client()
    client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)

    for identificador, info_dispositivo in dispositivos_lluvia.items():
        if info_dispositivo["probabilidad_lluvia"] < 65:
            if info_dispositivo["media_humedad_suelo"] > 850:  # esto según planta
                print("Activar riego en el dispositivo:", info_dispositivo["dispositivo"])
                if info_dispositivo["media_temperaturas"] > 30 and info_dispositivo["media_humedad_ambiente"] < 70:
                    print("Enviar mensaje MQTT al topic riego con el mensaje Activar riego y el número 70")
                    client.publish(f"/sensor/{identificador}", "70")
                else:
                    print("Enviar mensaje MQTT al topic riego con el mensaje Activar riego y el número 50")
                    client.publish(f"/sensor/{identificador}", "50")
            else:
                print("No activar riego en el dispositivo:", info_dispositivo["dispositivo"])
                print("Enviar mensaje MQTT al topic riego con el mensaje No activar riego")
        else:
            print("Probabilidad de lluvia alta, no activar riego en el dispositivo:", info_dispositivo["dispositivo"])

    # Desconectar el cliente MQTT
    client.disconnect()
    print("repite")
    # Esperar 20 segundos antes de ejecutar de nuevo
    time.sleep(20)
