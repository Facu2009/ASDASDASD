from flask import Flask, request, jsonify
import requests
import socket
import threading

app = Flask(__name__)

def get_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

@app.route('/api/mensajes/recibir', methods=['POST'])
def recibir_mensaje():
    """Recibe el mensaje, lo muestra y lo reenvía de vuelta al origen (loop infinito)."""
    data = request.get_json()
    mensaje_texto = data.get('mensaje', 'Mensaje vacío')
    ip_origen = data.get('ip_origen')

    print("\n" + "⭐"*20)
    print(f"📩 MENSAJE RECIBIDO:")
    print(f"   {mensaje_texto}")
    if ip_origen:
        print(f"   (de {ip_origen})")
    print("⭐"*20 + "\n")

    # Reenviamos el mismo mensaje al origen con nuestra IP para que el loop continúe
    if ip_origen:
        def reenviar():
            try:
                ip_local = get_ip_local()
                url = f"http://{ip_origen}:5000/api/mensajes/recibir"
                requests.post(
                    url,
                    json={
                        "mensaje": mensaje_texto,
                        "ip_origen": ip_local
                    },
                    timeout=3
                )
                print(f"📤 Reenviado a {ip_origen}")
            except Exception as e:
                print(f"⚠️  No se pudo reenviar a {ip_origen}: {str(e)}")

        threading.Thread(target=reenviar).start()

    return jsonify({
        "status": "ok",
        "msj": "Mensaje recibido y rebotado."
    }), 200

@app.route('/api/mensajes/enviar', methods=['POST'])
def enviar_mensaje():
    """El emisor llama a esta ruta (desde requests.http) para iniciar el loop."""
    data = request.get_json()

    ip_destino = data.get('ip_destino')
    mensaje_texto = data.get('mensaje')

    if not ip_destino or not mensaje_texto:
        return jsonify({"error": "Falta la ip_destino o el mensaje"}), 400

    try:
        ip_local = get_ip_local()
        url = f"http://{ip_destino}:5000/api/mensajes/recibir"

        respuesta = requests.post(
            url,
            json={"mensaje": mensaje_texto, "ip_origen": ip_local},
            timeout=3
        )

        return jsonify({
            "status": "loop iniciado",
            "destino": ip_destino,
            "respuesta_de_la_otra_pc": respuesta.json()
        }), 200

    except Exception as e:
        return jsonify({"error": f"No se pudo conectar con {ip_destino}: {str(e)}"}), 500

if __name__ == '__main__':
    print(f"\n🟢 Servidor corriendo en {get_ip_local()}:5000\n")
    app.run(host='0.0.0.0', port=5000, debug=True)