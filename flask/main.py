from flask import Flask, request, jsonify
import requests
import socket
import threading

app = Flask(__name__)

# =============================================
#   CONFIGURÁ ESTA IP ANTES DE ARRANCAR
#   Poné la IP de la PC siguiente en la cadena
#   Ejemplo:
#     PC1 pone la IP de PC2
#     PC2 pone la IP de PC3
#     PC3 pone la IP de PC1  (cierra el círculo)
# =============================================
IP_SIGUIENTE = "192.168.220.100"

# =============================================
#   ¿ES ESTA PC EL PRIMER EMISOR?
#   Poné True solo en la PC que arranca la cadena.
#   En todas las demás dejá False.
# =============================================
ES_EMISOR_INICIAL = True


def get_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


@app.route('/api/mensajes/recibir', methods=['POST'])
def recibir_mensaje():
    """Recibe el mensaje, lo muestra y lo pasa a la siguiente PC de la cadena."""
    data = request.get_json()
    mensaje_texto = data.get('mensaje', 'Mensaje vacío')
    contador = data.get('contador', 0) + 1  # Incrementa el contador al recibir

    print("\n" + "⭐" * 20)
    print(f"📩 MENSAJE RECIBIDO:")
    print(f"   {mensaje_texto}")
    print(f"   🔢 Saltos recorridos: {contador}")
    print(f"   Pasando a → {IP_SIGUIENTE}")
    print("⭐" * 20 + "\n")

    def pasar_siguiente():
        try:
            url = f"http://{IP_SIGUIENTE}:5000/api/mensajes/recibir"
            requests.post(
                url,
                json={"mensaje": mensaje_texto, "contador": contador},
                timeout=3
            )
            print(f"📤 Mensaje pasado a {IP_SIGUIENTE} (saltos: {contador})")
        except Exception as e:
            print(f"⚠️  No se pudo pasar a {IP_SIGUIENTE}: {str(e)}")

    threading.Thread(target=pasar_siguiente).start()

    return jsonify({
        "status": "ok",
        "msj": f"Mensaje recibido y pasado a {IP_SIGUIENTE}",
        "contador": contador
    }), 200


@app.route('/api/mensajes/enviar', methods=['POST'])
def enviar_mensaje():
    """Solo la usa el emisor inicial desde requests.http para arrancar la cadena."""
    data = request.get_json()
    mensaje_texto = data.get('mensaje')

    if not mensaje_texto:
        return jsonify({"error": "Falta el mensaje"}), 400

    try:
        url = f"http://{IP_SIGUIENTE}:5000/api/mensajes/recibir"
        respuesta = requests.post(
            url,
            json={"mensaje": mensaje_texto, "contador": 0},
            timeout=3
        )

        return jsonify({
            "status": "cadena iniciada",
            "primer_destino": IP_SIGUIENTE,
            "respuesta": respuesta.json()
        }), 200

    except Exception as e:
        return jsonify({"error": f"No se pudo conectar con {IP_SIGUIENTE}: {str(e)}"}), 500


def arrancar_cadena(mensaje):
    """Envía el mensaje inicial a la siguiente PC de la cadena."""
    import time
    time.sleep(1)  # Espera a que Flask levante antes de mandar
    try:
        url = f"http://{IP_SIGUIENTE}:5000/api/mensajes/recibir"
        respuesta = requests.post(
            url,
            json={"mensaje": mensaje, "contador": 0},
            timeout=3
        )
        print(f"🚀 Cadena iniciada → {IP_SIGUIENTE}")
        print(f"   Respuesta: {respuesta.json()}")
    except Exception as e:
        print(f"⚠️  No se pudo iniciar la cadena: {str(e)}")


if __name__ == '__main__':
    ip_local = get_ip_local()
    print(f"\n🟢 Servidor corriendo en {ip_local}:5000")
    print(f"➡️  Siguiente en la cadena: {IP_SIGUIENTE}\n")

    if ES_EMISOR_INICIAL:
        print("📝 Sos el emisor inicial. Escribí el mensaje para arrancar la cadena:")
        mensaje_inicial = input("   Mensaje: ").strip()
        if mensaje_inicial:
            threading.Thread(target=arrancar_cadena, args=(mensaje_inicial,)).start()
        else:
            print("⚠️  No ingresaste ningún mensaje. El servidor arranca sin enviar nada.")

    app.run(host='0.0.0.0', port=5000, debug=False)