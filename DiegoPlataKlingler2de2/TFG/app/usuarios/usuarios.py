from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from random import randint
import random
import smtplib
import string
from subprocess import Popen
import bcrypt
from flask import Blueprint, jsonify, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from .models import Usuario
from werkzeug.security import generate_password_hash, check_password_hash
from app.dispositivos.dispositivos import dispositivos_bp
from flasgger import swag_from
from app import importar_swagger

usuarios_bp = Blueprint('usuarios', __name__)
dispositivos_bp = Blueprint('dispositivos', __name__)
@usuarios_bp.route('/registro', methods=['GET', 'POST'])
@swag_from(importar_swagger)
def registro():
    error = False  
    
    if request.method == 'POST':
        username = request.form.get('username')
        mail = request.form.get('mail')
        password = request.form.get('password')
        
        if Usuario.query.filter_by(username=username).first():
            flash('El nombre de usuario ya está en uso', 'danger')
            error = True  
        else:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            nuevo_usuario = Usuario(username=username, mail=mail, password=hashed_password.decode('utf-8'))
            
            try:
                db.session.add(nuevo_usuario)
                db.session.commit()
                flash('Usuario registrado con éxito', 'success')
                login_user(nuevo_usuario)
                return redirect(url_for('usuarios.seleccionar_dispositivos'))
            except Exception as e:
                flash('Error al registrar el usuario', 'danger')
                error = True  

    return render_template('registro.html', error=error)  

@usuarios_bp.route('/login', methods=['GET', 'POST'])
@swag_from(importar_swagger)
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        usuario = Usuario.query.filter_by(username=username).first()

        if usuario and bcrypt.checkpw(password.encode('utf-8'), usuario.password.encode('utf-8')):
            login_user(usuario)
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('usuarios.home'))  
        else:
            flash('Nombre de usuario o contraseña incorrectos', 'danger')
            return render_template('login.html', error=True)

    return render_template('login.html', error=False)


@usuarios_bp.route('/logout')
@swag_from(importar_swagger)
@login_required
def logout():
    logout_user()
    return redirect(url_for('usuarios.login'))

@usuarios_bp.route('/home')
@swag_from(importar_swagger)
@login_required  
def home():
    usuario = current_user
    return render_template('home.html', usuario=usuario)

@usuarios_bp.route('/perfil')
@swag_from(importar_swagger)
@login_required
def perfil():
    usuario = current_user
    with open('app/static/colecciones.txt', 'r') as file:
        dispositivos_disponibles = file.read().splitlines()
    
    # Obtener los dispositivos registrados del usuario actual, manejar el caso None
    dispositivos_registrados_id = current_user.dispositivos_registrados_id
    if dispositivos_registrados_id is None:
        dispositivos_registrados_id = []
    else:
        dispositivos_registrados_id = dispositivos_registrados_id.split(',')

    return render_template('perfil.html', usuario=usuario, dispositivos_registrados_id=dispositivos_registrados_id, todos_dispositivos=dispositivos_disponibles)

@usuarios_bp.route('/')
def index():
    return render_template('index.html')


@usuarios_bp.route('/actualizar_perfil', methods=['POST'])
@swag_from(importar_swagger)
def actualizar_perfil():
    """
    Actualiza el perfil del usuario
    ---
    Consumes:
    - application/x-www-form-urlencoded
    Produces:
    - text/html
    """
    if request.method == 'POST':
        nuevo_nombre = request.form.get('nombre')
        nuevo_email = request.form.get('email')
        nuevo_password = request.form.get('password')
        
        if nuevo_nombre:
            current_user.username = nuevo_nombre
        if nuevo_email:
            current_user.mail = nuevo_email
        if nuevo_password:
            current_user.password = bcrypt.hashpw(nuevo_password.encode('utf-8'), bcrypt.gensalt())
        
        db.session.commit()
        
        return redirect(url_for('usuarios.home'))  
    else:
        return redirect(url_for('usuarios.perfil'))


@usuarios_bp.route('/seleccionar_dispositivos', methods=['GET', 'POST'])
@login_required
@swag_from(importar_swagger)
def seleccionar_dispositivos():
    if request.method == 'POST':
        # Obtener los dispositivos seleccionados por el usuario desde el formulario
        dispositivos_seleccionados_str = request.form.get('dispositivos_seleccionados')
        
        # Convertir la cadena de dispositivos separada por comas en una lista
        dispositivos_seleccionados = dispositivos_seleccionados_str.split(',')

        # Imprimir los dispositivos seleccionados para verificar
        print("Dispositivos seleccionados:", dispositivos_seleccionados)

        # Actualizar la base de datos
        current_user.dispositivos_registrados_id = dispositivos_seleccionados_str
        db.session.commit()

        return redirect(url_for('usuarios.home'))

    with open('app/static/colecciones.txt', 'r') as file:
        dispositivos = file.read().splitlines()
    return render_template('seleccionar_dispositivos.html', dispositivos=dispositivos)


@usuarios_bp.route('/obtener_dispositivos_registrados_id')
@swag_from(importar_swagger)
@login_required
def obtener_dispositivos_registrados_id():
    # Obtener el ID de dispositivos registrados del usuario actual
    dispositivos_registrados_id = current_user.dispositivos_registrados_id
    
    # Crear un diccionario con el ID de dispositivos registrados
    data = {"dispositivos_registrados_id": dispositivos_registrados_id}
    
    # Devolver el diccionario como una respuesta JSON
    return jsonify(data)

@usuarios_bp.route('/eliminar_cuenta', methods=['POST'])
@login_required
@swag_from(importar_swagger)
def eliminar_cuenta():
    """
    Elimina la cuenta del usuario actual
    """
    try:
        # Eliminar el usuario de la base de datos
        db.session.delete(current_user)
        db.session.commit()

        # Desconectar al usuario
        logout_user()

        flash('Tu cuenta ha sido eliminada', 'success')
        return redirect(url_for('usuarios.login'))
    except Exception as e:
        flash('Error al eliminar tu cuenta', 'danger')
        return redirect(url_for('usuarios.perfil'))
    
@usuarios_bp.route('/recuperar_contrasena', methods=['POST'])
def recuperar_ctr():
    email = request.form.get('email')
    usuario = Usuario.query.filter_by(mail=email).first()
    if usuario:
        # Generar una cadena 4 letras
        numero = random.randint(100000, 999999)
    # Generar cadena de 4 caracteres aleatorios
        letras = ''.join(random.choices(string.ascii_letters, k=4))
    # Combinar ambos
        password_nueva = str(numero) + letras

        #print(password_nueva)
        # Hashear la contraseña
        hashed_password = bcrypt.hashpw(password_nueva.encode('utf-8'), bcrypt.gensalt())        # Actualizar la contraseña del usuario
        usuario.password = hashed_password.decode('utf-8')
        db.session.commit()
        
        # Configurar el correo electrónico
        sender_email = "plata.tfg@gmail.com"
        receiver_email = email
        email_password = "rvfd kpma ejfx hcdu"
        subject = "Recuperar contraseña"
        # Convertir la contraseña a una cadena hexadecimal para enviarla por correo
        body = "Tu nueva contraseña es: " + password_nueva + "\n\nPor favor, actualizala cuando puedas desde tu perfil."

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        # Enviar el correo electrónico
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, email_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        
        return redirect(url_for('usuarios.login'))
    return 'Correo electrónico no encontrado', 404