from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
 
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
    base_path = os.getcwd()
    carpeta_destino = os.path.join(base_path, "uploads")
    carpeta_destino = os.path.join("uploads", fecha)
    os.makedirs(carpeta_destino, exist_ok=True)
 
    archivo_path = os.path.join(carpeta_destino, archivo.filename)
    archivo.save(archivo_path)
 
    return jsonify({"mensaje": f"Archivo {archivo.filename} guardado en {carpeta_destino}"}), 200
 
 
if __name__ == '__main__':
    app.run()
 