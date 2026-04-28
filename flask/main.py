from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/api/mensajes/recibir', methods=['POST'])
def recibir_mensaje():
    """Ruta RECEPTORA: Escucha y muestra los mensajes que llegan."""
    data = request.get_json()
    mensaje_texto = data.get('mensaje', 'Mensaje vacío')
    
    # Muestra el mensaje en la pantalla del que lo recibe
    print("\n" + "⭐"*20)
    print(f"📩 NUEVO MENSAJE RECIBIDO:")
    print(f"   {mensaje_texto}")
    print("⭐"*20 + "\n")
    
    # Esta es la CONFIRMACIÓN que se le devuelve automáticamente al que envió el mensaje
    return jsonify({
        "status": "ok", 
        "msj": "¡Mensaje recibido fuerte y claro por la otra computadora!"
    }), 200

@app.route('/api/mensajes/enviar', methods=['POST'])
def enviar_mensaje():
    """Ruta EMISORA: Tú la usas para mandar un mensaje a otra PC."""
    data = request.get_json()
    
    ip_destino = data.get('ip_destino')
    mensaje_texto = data.get('mensaje')
    
    if not ip_destino or not mensaje_texto:
        return jsonify({"error": "Falta la ip_destino o el mensaje"}), 400
        
    url = f"http://{ip_destino}:5000/api/mensajes/recibir"
    
    try:
        # Disparamos el mensaje a la otra PC
        respuesta = requests.post(url, json={"mensaje": mensaje_texto}, timeout=3)
        
        # Leemos la respuesta de confirmación que nos dio la otra PC
        confirmacion = respuesta.json()
        
        return jsonify({
            "status": "enviado exitosamente", 
            "destino": ip_destino,
            "respuesta_de_la_otra_pc": confirmacion  # Te mostramos la confirmación
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"No se pudo conectar con {ip_destino}: {str(e)}"}), 500

if __name__ == '__main__':
    # host='0.0.0.0' permite que la red local vea este servidor
    app.run(host='0.0.0.0', port=5000, debug=True)