import os
from pymongo import MongoClient

# Configuración mongo
MONGO_HOST = "localhost"
MONGO_PORT = 27017
DB_NAME = "riego"
usuario = "riego"
contrasena = "riego00"

# Ruta a archivo de salida
ruta_salida = os.path.join("app", "static", "colecciones.txt")

# actualizar txt con nombres de colecciones
def actualizar_archivo():
    try:
        # Conexión a MongoDB
        client = MongoClient(MONGO_HOST, MONGO_PORT, username=usuario, password=contrasena)
        db = client[DB_NAME]

        # obtener y ordenar nombres de colecciones
        collection_names = sorted(db.list_collection_names())

        # escribir en ficher
        with open(ruta_salida, "w") as file:
            for collection_name in collection_names:
                file.write(collection_name + "\n")
        
        print("colecciones actualizadas en el txt", collection_names)

        # Cerrar mongo
        client.close()

    except Exception as e:
        print("Error al actualizar colecciones:", e)



actualizar_archivo()

