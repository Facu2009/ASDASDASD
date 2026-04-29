from flask import Flask, request, jsonify
import requests
import socket
import threading
import time

app = Flask(__name__)

# =============================================
#   CONFIGURÁ ESTA IP ANTES DE ARRANCAR
# =============================================
IP_SIGUIENTE = "192.168.1.10"

LIMITE_CONTADOR = 100


def get_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


@app.route('/api/mensajes/recibir', methods=['POST'])
def recibir_mensaje():
    data = request.get_json()
    mensaje_texto = data.get('mensaje', '')
    contador = data.get('contador', 0) + 1

    ip_local = get_ip_local()
    print(f"[{ip_local}] [{contador}] {mensaje_texto}")

    if contador >= LIMITE_CONTADOR:
        print(f"[{ip_local}] Mensaje eliminado (limite {LIMITE_CONTADOR} alcanzado)")
        return jsonify({"status": "eliminado", "contador": contador}), 200

    def pasar_siguiente():
        try:
            url = f"http://{IP_SIGUIENTE}:5000/api/mensajes/recibir"
            requests.post(
                url,
                json={"mensaje": mensaje_texto, "contador": contador},
                timeout=5
            )
        except Exception as e:
            print(f"Error al pasar a {IP_SIGUIENTE}: {str(e)}")

    threading.Thread(target=pasar_siguiente).start()

    return jsonify({"status": "ok", "contador": contador}), 200


def enviar_mensaje(mensaje):
    try:
        url = f"http://{IP_SIGUIENTE}:5000/api/mensajes/recibir"
        requests.post(
            url,
            json={"mensaje": mensaje, "contador": 0},
            timeout=5
        )
    except Exception as e:
        print(f"Error al enviar a {IP_SIGUIENTE}: {str(e)}")


def loop_input():
    time.sleep(1)
    while True:
        try:
            mensaje = input()
            if mensaje.strip():
                threading.Thread(target=enviar_mensaje, args=(mensaje.strip(),)).start()
        except EOFError:
            break


if __name__ == '__main__':
    ip_local = get_ip_local()
    print(f"Servidor en {ip_local}:5000 -> siguiente: {IP_SIGUIENTE}")

    threading.Thread(target=loop_input, daemon=True).start()

    app.run(host='0.0.0.0', port=5000, debug=False)