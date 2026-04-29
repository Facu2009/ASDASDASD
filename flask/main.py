from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

MENSAJE_AUTO_REPLY = "¡Hola! Tu mensaje fue recibido correctamente."

@app.route('/api/mensajes/recibir', methods=['POST'])
def recibir_mensaje():
    """Ruta RECEPTORA: Escucha y muestra los mensajes que llegan."""
    data = request.get_json()
    mensaje_texto = data.get('mensaje', 'Mensaje vacío')
    ip_origen = data.get('ip_origen')

    # Muestra el mensaje en la pantalla del que lo recibe
    print("\n" + "⭐"*20)
    print(f"📩 NUEVO MENSAJE RECIBIDO:")
    print(f"   {mensaje_texto}")
    print("⭐"*20 + "\n")

    # Si viene ip_origen, mandamos un auto-reply
    if ip_origen:
        try:
            url = f"http://{ip_origen}:5000/api/mensajes/recibir"
            requests.post(
                url,
                json={"mensaje": MENSAJE_AUTO_REPLY},
                timeout=3
            )
            print(f"📤 Auto-reply enviado a {ip_origen}")
        except Exception as e:
            print(f"⚠️  No se pudo enviar auto-reply a {ip_origen}: {str(e)}")

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
        # Obtenemos la IP local para que el destino pueda hacer auto-reply
        import socket
        ip_local = socket.gethostbyname(socket.gethostname())

        # Disparamos el mensaje a la otra PC, incluyendo nuestra IP como ip_origen
        respuesta = requests.post(
            url,
            json={"mensaje": mensaje_texto, "ip_origen": ip_local},
            timeout=3
        )

        confirmacion = respuesta.json()

        return jsonify({
            "status": "enviado exitosamente",
            "destino": ip_destino,
            "respuesta_de_la_otra_pc": confirmacion
        }), 200

    except Exception as e:
        return jsonify({"error": f"No se pudo conectar con {ip_destino}: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)