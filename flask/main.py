from flask import Flask, request, jsonify  
import requests                            

from config import Config
from models import db, Persona

app = Flask(__name__)
# ... y luego el resto de tu código ...

@app.route('/api/mensajes/recibir', methods=['POST'])
def recibir_mensaje():
    """Esta ruta actúa como RECEPTOR. Escucha si alguien le manda un mensaje."""
    data = request.get_json()
    mensaje_texto = data.get('mensaje', 'Mensaje vacío')
    
    # Imprime el mensaje bonito en la terminal
    print("\n" + "⭐"*20)
    print(f"📩 NUEVO MENSAJE RECIBIDO:")
    print(f"   {mensaje_texto}")
    print("⭐"*20 + "\n")
    
    return jsonify({"status": "ok", "msj": "Mensaje recibido correctamente"}), 200


@app.route('/api/mensajes/enviar', methods=['POST'])
def enviar_mensaje():
    """Esta ruta actúa como EMISOR. Tú la llamas para disparar un mensaje a otra IP."""
    data = request.get_json()
    
    # Necesitamos saber a qué IP mandar y qué decir
    ip_destino = data.get('ip_destino')
    mensaje_texto = data.get('mensaje')
    
    if not ip_destino or not mensaje_texto:
        return jsonify({"error": "Falta la ip_destino o el mensaje"}), 400
        
    # Armamos la URL de la otra PC (apuntando a su ruta de recibir)
    url = f"http://{ip_destino}:5000/api/mensajes/recibir"
    
    try:
        # Enviamos solo el texto
        requests.post(url, json={"mensaje": mensaje_texto}, timeout=3)
        return jsonify({"status": "enviado", "destino": ip_destino}), 200
    except Exception as e:
        return jsonify({"error": f"No se pudo conectar con {ip_destino}: {str(e)}"}), 500