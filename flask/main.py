from flask import Flask, request, jsonify
import requests
import socket
import threading
import time

app = Flask(__name__)

# =============================================
#   CONFIGURÁ ESTAS IPs ANTES DE ARRANCAR
#   IP_SIGUIENTE: a quién le mandás los mensajes
#   Ejemplo:
#     PC1 → IP de PC2
#     PC2 → IP de PC3
#     PC3 → IP de PC1  (cierra el círculo)
# =============================================
IP_SIGUIENTE = "192.168.220.100"


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
    mensaje_texto = data.get('mensaje', 'Mensaje vacío')
    contador = data.get('contador', 0) + 1

    print("\n" + "⭐" * 20)
    print(f"📩 MENSAJE RECIBIDO:")
    print(f"   {mensaje_texto}")
    print(f"   🔢 Saltos recorridos: {contador}")
    print(f"   Pasando a → {IP_SIGUIENTE}")
    print("⭐" * 20 + "\n")

    def pasar_siguiente():
        time.sleep(1)
        try:
            url = f"http://{IP_SIGUIENTE}:5000/api/mensajes/recibir"
            requests.post(
                url,
                json={"mensaje": mensaje_texto, "contador": contador},
                timeout=5
            )
        except Exception as e:
            print(f"⚠️  No se pudo pasar a {IP_SIGUIENTE}: {str(e)}")

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
        print(f"📤 Enviado a {IP_SIGUIENTE}")
    except Exception as e:
        print(f"⚠️  No se pudo enviar a {IP_SIGUIENTE}: {str(e)}")


def loop_input():
    """Hilo que lee mensajes de la terminal y los manda a la cadena."""
    time.sleep(1)  # Espera a que Flask levante
    print("\n💬 Escribí un mensaje y presioná Enter para enviarlo a la cadena:\n")
    while True:
        try:
            mensaje = input()
            if mensaje.strip():
                threading.Thread(target=enviar_mensaje, args=(mensaje.strip(),)).start()
        except EOFError:
            break


if __name__ == '__main__':
    ip_local = get_ip_local()
    print(f"\n🟢 Servidor corriendo en {ip_local}:5000")
    print(f"➡️  Siguiente en la cadena: {IP_SIGUIENTE}")

    threading.Thread(target=loop_input, daemon=True).start()

    app.run(host='0.0.0.0', port=5000, debug=False)