import json
import signal
import time
import paho.mqtt.client as mqtt
from pymongo import MongoClient
from datetime import datetime
import mariadb
import threading

# Configuración de MQTT
MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
MQTT_TOPIC = "sensor/#"

# Configuración de MongoDB
MONGO_HOST = "localhost"
MONGO_PORT = 27017
usuario = "riego"
contrasena = "riego00"

# Conexión a MongoDB
cliente_mongo = None
db = None

# Conexión a MariaDB
mariadb_connection = None

# Diccionario global de dispositivos
dispositivos = {}
solicitud_desconexion = False

# Lock para manejar el acceso a dispositivos
dispositivos_lock = threading.Lock()

def conexion_mongo():
    global cliente_mongo, db
    try:
        cliente_mongo = MongoClient(MONGO_HOST, MONGO_PORT, username=usuario, password=contrasena)
        db = cliente_mongo.riego
        print("Conectado a MongoDB")
    except Exception as e:
        print(f"Error al conectar a MongoDB: {e}")

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
    try:
        with mariadb_connection.cursor() as cursor:
            cursor.execute("SELECT identificador, nombre FROM dispositivo")
            with dispositivos_lock:
                for identificador, nombre in cursor:
                    dispositivos[identificador] = nombre
        print("Dispositivos obtenidos de MariaDB")
        print(dispositivos)
    except mariadb.Error as e:
        print(f"Error al obtener dispositivos de MariaDB: {e}")

def buscar_nombre_dispositivo(device_id):
    global dispositivos
    while not solicitud_desconexion:
        print(f"Buscando nombre para el dispositivo {device_id}")
        try:
            conectar_mariadb()
            with mariadb_connection.cursor() as cursor:
                cursor.execute("SELECT nombre FROM dispositivo WHERE identificador = ?", (device_id,))
                result = cursor.fetchone()
                if result:
                    with dispositivos_lock:
                        dispositivos[device_id] = result[0]
                    print(f"Nombre encontrado para el dispositivo {device_id}: {result[0]}")
                    desconectar_mariadb()
                    return
                else:
                    print(f"Nombre no encontrado para el dispositivo {device_id}, reintentando en 5 segundos")
            desconectar_mariadb()
        except mariadb.Error as e:
            print(f"Error al buscar nombre de dispositivo en MariaDB: {e}")
            desconectar_mariadb()
        time.sleep(5)

def on_connect(client, userdata, flags, rc):
    print("Conectado al broker MQTT")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, message):
    #print(f"Mensaje recibido en {message.topic}")
    payload = message.payload.decode("utf-8")
   # print(f"Payload: {payload}")
    topic = message.topic

    if topic == "sensor/datos":
        try:
            datos = json.loads(payload)
            now = datetime.now()
            fecha = now.strftime("%Y-%m-%d")
            hora = now.strftime("%H:%M:%S")

            timestamp = f"{fecha} {hora}"
            device_id = datos.get("device_id")
            humedad_ambiente = datos.get("humidity")
            temperatura_ambiente = datos.get("temperature")
            humedad_suelo = datos.get("soil_moisture")

            if device_id:
                with dispositivos_lock:
                    nombre_dispositivo = dispositivos.get(device_id)
                
                if nombre_dispositivo:
                    coleccion = db[nombre_dispositivo]
                    nuevo_documento = {
                        "fecha": fecha,
                        "hora": hora,
                        "device_id": device_id,
                        "humedad_ambiente": humedad_ambiente,
                        "temperatura_ambiente": temperatura_ambiente,
                        "humedad_suelo": humedad_suelo
                    }
                    try:
                        coleccion.insert_one(nuevo_documento)
                        print(f"Documento insertado en la colección '{nombre_dispositivo}'")
                    except Exception as e:
                        print(f"Error al insertar en MongoDB: {e}")
                else:
                    print(f"No se encontró un nombre para el identificador {device_id}, iniciando búsqueda")
                    threading.Thread(target=buscar_nombre_dispositivo, args=(device_id,)).start()
            else:
                print("JSON incompleto: no se proporcionó device_id")
        except json.JSONDecodeError:
            print("Error al decodificar el JSON:", payload)

def handler_interrupt(signum, frame): #tipica manejadora de ssoo1 :)
    global solicitud_desconexion
    print("Ctrl+C")
    solicitud_desconexion = True
    client.disconnect()

# Configurar señales
signal.signal(signal.SIGINT, handler_interrupt) #lo del estuche que metes bolis y sacas uno...

# Conectar a MongoDB y MariaDB, y obtener dispositivos
conexion_mongo()
conectar_mariadb()
obtener_dispositivos()

# Configurar cliente MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)

# Bucle principal
while not solicitud_desconexion:
    client.loop()

# Cerrar conexiones a las bases de datos
if cliente_mongo:
    cliente_mongo.close()
    print("Conexión a la base de datos MongoDB cerrada")
if mariadb_connection:
    mariadb_connection.close()
    print("Conexión a la base de datos MariaDB cerrada")
