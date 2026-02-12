from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import requests
import logging
app = Flask(__name__)
auth = HTTPBasicAuth()
 
# Usuarios válidos
users = {
    "admin": generate_password_hash("clave123")
}
 
@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

def get_daily_logger():
    """Configura y devuelve un logger que escribe en un archivo con la fecha actual."""
    log_dir = "/home/LogFiles"
    os.makedirs(log_dir, exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    log_filename = os.path.join(log_dir, f"{today}.log")
    
    logger = logging.getLogger("seriot_daily_logger")
    logger.setLevel(logging.INFO)
    
    # Evitar duplicar handlers
    if not logger.handlers:
        handler = logging.FileHandler(log_filename)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    else:
        # Verificar si el handler existente apunta al archivo de hoy, si no, cambiarlo
        current_handler_filename = logger.handlers[0].baseFilename
        if current_handler_filename != log_filename:
            logger.handlers = []
            handler = logging.FileHandler(log_filename)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
    return logger
 
@app.route('/upload', methods=['POST'])
@auth.login_required
def recibir_archivo():
    if not request.files:
        return jsonify({"error": "No se encontró ningún archivo"}), 400
 
    archivo = next(iter(request.files.values()))  # Toma el primer archivo recibido
 
    # Crear carpeta por fecha (YYYY-MM-DD)
    fecha = datetime.now().strftime("%Y-%m-%d")
    # base_path = os.getcwd()
    carpeta_destino = os.path.join("/home/excel", "uploads")
    carpeta_destino = os.path.join(carpeta_destino, fecha)
    os.makedirs(carpeta_destino, exist_ok=True)
 
    archivo_path = os.path.join(carpeta_destino, archivo.filename)
    archivo.save(archivo_path)
 
    return jsonify({"mensaje": f"Archivo {archivo.filename} guardado en {carpeta_destino}"}), 200
 

@app.route('/telemetry_seriot', methods=['POST'])
def recibir_peticion_seriot():
    try:
        logger = get_daily_logger()
        datos = request.get_json()
        # print(datos)
        logger.info(f"Datos recibidos: {datos}")

        payload = {
            "device": datos['device'],
            "date": datos['date'],
            "Activa": datos['Activa'],
            "Reactiva": datos['Reactiva'],
        }
        # print(payload)
        header = {
            "X-Auth-Token": request.headers.get('X-Auth-Token')
        }
        response = requests.post(
            url="https://canovabackendprodenergym.happysmoke-127484da.eastus2.azurecontainerapps.io/telemetry/seriot/load",
            headers=header,
            data=payload,
        )
        print("Me respondio: ", response.status_code)
        if response.status_code in [200,201,202]:
            logger.info(f"Respuesta backend: {response.status_code} - {response.content}")
            return jsonify({"mensaje": f"Dato almacenado correctamente, {response.content}"}), 200
        else:
            logger.warning(f"Fallo al almacenar en backend. Status: {response.status_code}")
            return jsonify({"mensaje": "Dato no almacenado"}), 400
    except Exception as e:
        logger = get_daily_logger() # Asegurar logger en caso de error temprano
        # print(str(e))
        logger.error(f"Excepcion ocurrida: {str(e)}")
        if 'datos' in locals():
            print("Datos recibidos: ", datos)
            logger.error(f"Datos que causaron error: {datos}")
        return jsonify({"mensaje": "Problemas al procesar datos"}), 204


if __name__ == '__main__':
    app.run()
  
 
 