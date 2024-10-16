import paho.mqtt.client as mqtt
import tkinter as tk
import json
import mariadb

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("sensor/arranque")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    if msg.topic == "sensor/arranque":
        print("arranque")
        mensaje = json.loads(msg.payload.decode("utf-8"))

        # Extraer datos del mensaje MQTT
        device_id = mensaje.get("device_id")
        ip = mensaje.get("ip")
        
        ventana = tk.Tk()
        ventana.title("Datos del dispositivo")
        ventana.geometry("300x300")
        
        tk.Label(ventana, text="Nombre del dispositivo").pack()
        nombre_entry = tk.Entry(ventana)
        nombre_entry.pack()
        
        tk.Label(ventana, text="Ubicación del dispositivo").pack()
        ubicacion_entry = tk.Entry(ventana)
        ubicacion_entry.pack()
        
        tk.Label(ventana, text="Tipo de dispositivo (0 si está en el exterior, 1 si está en el interior)").pack()
        tipo_entry = tk.Entry(ventana)
        tipo_entry.pack()

        def validar_campos():
            if nombre_entry.get() == '' or ubicacion_entry.get() == '' or tipo_entry.get() == '':
                return False
            return True

        def validar_es_interior():
            valor = tipo_entry.get()
            if valor not in ['0', '1']:
                return False
            return True

        def guardar():
            if not validar_campos():
                return
            
            if not validar_es_interior():
                return
            
            # Conectar a la base de datos
            try:
                with mariadb.connect(
                    user="root",
                    password="2002",
                    host="localhost",
                    port=3306,
                    database="usuarios_tfg"
                ) as conn:
                    cur = conn.cursor()
                    cur.execute("INSERT INTO dispositivo (identificador, nombre, ip, es_interior, ciudad) VALUES (?, ?, ?, ?, ?)", 
                                (device_id, nombre_entry.get(), ip, tipo_entry.get(), ubicacion_entry.get()))
                    conn.commit()
                print("Datos guardados")
            except mariadb.Error as e:
                print(f"Error al conectar a la base de datos: {e}")
            ventana.destroy()

        def cerrar_ventana():
            ventana.destroy()

        tk.Button(ventana, text="Guardar", command=guardar).pack()
        ventana.protocol("WM_DELETE_WINDOW", cerrar_ventana)
        ventana.mainloop()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.1.58", 1883, 60)

client.loop_forever()
