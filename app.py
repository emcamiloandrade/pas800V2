from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import requests
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
        datos = request.get_json()
        payload = {
            "device": datos['device'],
            "date": datos['date'],
            "Activa": datos['Activa'],
            "Reactiva": datos['Reactiva'],
        }
        header = {
            "X-Auth-Token": request.headers.get('X-Auth-Token')
        }
        print("Entre a enviar info a NOVA")
        response = requests.post(
            url="https://canovabackendprodenergym.happysmoke-127484da.eastus2.azurecontainerapps.io/telemetry/seriot/load",
            headers=header,
            data=payload,
        )
        print("Despues de enviar datos a NOVA")
        print("Me respondio: ", response.status_code)
        if response.status_code in [200,201,202]:
            return jsonify({"mensaje": f"Dato almacenado correctamente, {response.content}"}), 200
        else:
            return jsonify({"mensaje": "Dato no almacenado"}), 400
    except Exception as e:
        print(str(e))
        return jsonify({"mensaje": "Problemas al procesar datos"}), 500


if __name__ == '__main__':
    app.run()
  
 
