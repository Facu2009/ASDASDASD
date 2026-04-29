from flask import Flask, request, jsonify
import requests
import socket
import threading
import time

app = Flask(__name__)

# Estas variables se configuran al arrancar via input()
IP_SIGUIENTE = None
ES_EMISOR = False

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
    contador = data.get('contador', 0) + 1

    print("\n" + "⭐" * 20)
    print(f"📩 MENSAJE RECIBIDO:")
    print(f"   {mensaje_texto}")
    print(f"   🔢 Saltos recorridos: {contador}")
    print(f"   Pasando a → {IP_SIGUIENTE}")
    print("⭐" * 20 + "\n")

    def pasar_siguiente():
        time.sleep(1)  # 1 segundo de pausa antes de pasar el mensaje
        try:
            url = f"http://{IP_SIGUIENTE}:5000/api/mensajes/recibir"
            requests.post(
                url,
                json={"mensaje": mensaje_texto, "contador": contador},
                timeout=5
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


def arrancar_cadena(mensaje):
    """Envía el mensaje inicial a la siguiente PC de la cadena."""
    time.sleep(1)  # Espera a que Flask levante
    try:
        url = f"http://{IP_SIGUIENTE}:5000/api/mensajes/recibir"
        respuesta = requests.post(
            url,
            json={"mensaje": mensaje, "contador": 0},
            timeout=5
        )
        print(f"🚀 Cadena iniciada → {IP_SIGUIENTE}")
        print(f"   Respuesta: {respuesta.json()}")
    except Exception as e:
        print(f"⚠️  No se pudo iniciar la cadena: {str(e)}")


def configurar():
    """Pregunta al usuario si es emisor o receptor y configura las variables."""
    global IP_SIGUIENTE, ES_EMISOR

    ip_local = get_ip_local()

    print("\n" + "="*45)
    print("   🖧  CONFIGURACIÓN DE LA CADENA DE MENSAJES")
    print("="*45)
    print(f"   Tu IP local: {ip_local}")
    print("="*45 + "\n")

    while True:
        rol = input("¿Sos emisor o receptor? [e/r]: ").strip().lower()
        if rol in ("e", "r"):
            break
        print("   ⚠️  Ingresá 'e' para emisor o 'r' para receptor.\n")

    ES_EMISOR = (rol == "e")

    if ES_EMISOR:
        print("\n📡 Modo: EMISOR")
        IP_SIGUIENTE = input("   IP de destino (primera PC que va a recibir): ").strip()
        print(f"\n📝 Escribí el mensaje para arrancar la cadena:")
        mensaje = input("   Mensaje: ").strip()
        if not mensaje:
            mensaje = "Mensaje de prueba"
            print(f"   (sin mensaje, se usa: '{mensaje}')")
        return mensaje
    else:
        print("\n📡 Modo: RECEPTOR")
        IP_SIGUIENTE = input("   IP del siguiente receptor en la cadena: ").strip()
        print(f"\n✅ Listo. Esperando mensajes en {ip_local}:5000 ...")
        print(f"   Siguiente en la cadena → {IP_SIGUIENTE}\n")
        return None


if __name__ == '__main__':
    mensaje_inicial = configurar()

    if ES_EMISOR and mensaje_inicial:
        threading.Thread(target=arrancar_cadena, args=(mensaje_inicial,)).start()

    ip_local = get_ip_local()
    print(f"\n🟢 Servidor Flask corriendo en {ip_local}:5000\n")
    app.run(host='0.0.0.0', port=5000, debug=False)