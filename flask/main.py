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
    """Ruta RECEPTORA: Escucha, muestra y reenvía el mismo mensaje al origen."""
    data = request.get_json()
    mensaje_texto = data.get('mensaje', 'Mensaje vacío')
    ip_origen = data.get('ip_origen')

    print("\n" + "⭐"*20)
    print(f"📩 NUEVO MENSAJE RECIBIDO:")
    print(f"   {mensaje_texto}")
    print("⭐"*20 + "\n")

    # Si viene ip_origen, reenviamos el MISMO mensaje de vuelta (sin ip_origen para no hacer loop)
    if ip_origen:
        def enviar_eco():
            try:
                url = f"http://{ip_origen}:5000/api/mensajes/recibir"
                requests.post(
                    url,
                    json={"mensaje": mensaje_texto},
                    timeout=3
                )
                print(f"📤 Eco enviado a {ip_origen}: '{mensaje_texto}'")
            except Exception as e:
                print(f"⚠️  No se pudo enviar eco a {ip_origen}: {str(e)}")

        # Lo mandamos en un hilo para no bloquear la respuesta HTTP
        threading.Thread(target=enviar_eco).start()

    return jsonify({
        "status": "ok",
        "msj": "¡Mensaje recibido fuerte y claro por la otra computadora!"
    }), 200

@app.route('/api/mensajes/enviar', methods=['POST'])
def enviar_mensaje():
    """Ruta EMISORA: Manda un mensaje a otra PC incluyendo nuestra IP."""
    data = request.get_json()

    ip_destino = data.get('ip_destino')
    mensaje_texto = data.get('mensaje')

    if not ip_destino or not mensaje_texto:
        return jsonify({"error": "Falta la ip_destino o el mensaje"}), 400

    url = f"http://{ip_destino}:5000/api/mensajes/recibir"

    try:
        ip_local = get_ip_local()

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

def iniciar_como_primero():
    """Pide IP destino y mensaje por consola, luego envía."""
    print("\n" + "="*40)
    print("  MODO INICIADOR - Vos sos el primero")
    print("="*40)
    ip_destino = input("📡 IP de la otra PC: ").strip()
    mensaje = input("✉️  Mensaje a enviar: ").strip()

    if not ip_destino or not mensaje:
        print("❌ IP o mensaje vacío. Abortando.")
        return

    # Esperamos a que el servidor Flask arranque
    import time
    time.sleep(1.5)

    ip_local = get_ip_local()
    url = f"http://{ip_destino}:5000/api/mensajes/recibir"

    try:
        respuesta = requests.post(
            url,
            json={"mensaje": mensaje, "ip_origen": ip_local},
            timeout=5
        )
        print(f"\n✅ Mensaje enviado. Respuesta: {respuesta.json()}")
    except Exception as e:
        print(f"\n❌ No se pudo conectar con {ip_destino}: {str(e)}")

if __name__ == '__main__':
    print("\n" + "="*40)
    print("  ¿Cómo querés arrancar?")
    print("  1) Esperar mensajes (receptor)")
    print("  2) Ser el primero en mandar (iniciador)")
    print("="*40)
    opcion = input("Elegí 1 o 2: ").strip()

    if opcion == "2":
        # Arrancamos Flask en segundo plano para poder recibir el eco de vuelta
        hilo_servidor = threading.Thread(
            target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
        )
        hilo_servidor.daemon = True
        hilo_servidor.start()

        iniciar_como_primero()

        print("\n🟢 Servidor activo, esperando respuestas...\n")
        hilo_servidor.join()
    else:
        print("\n🟢 Esperando mensajes entrantes...\n")
        app.run(host='0.0.0.0', port=5000, debug=True)