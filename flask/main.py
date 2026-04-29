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
    """Ruta RECEPTORA: Recibe, muestra y reenvía el mensaje de vuelta al origen (loop infinito)."""
    data = request.get_json()
    mensaje_texto = data.get('mensaje', 'Mensaje vacío')
    ip_origen = data.get('ip_origen')

    print("\n" + "⭐"*20)
    print(f"📩 MENSAJE RECIBIDO:")
    print(f"   {mensaje_texto}")
    if ip_origen:
        print(f"   (de {ip_origen})")
    print("⭐"*20 + "\n")

    # Siempre reenviamos el mismo mensaje al origen, con nuestra IP para que el rebote continúe
    if ip_origen:
        def reenviar():
            try:
                ip_local = get_ip_local()
                url = f"http://{ip_origen}:5000/api/mensajes/recibir"
                requests.post(
                    url,
                    json={
                        "mensaje": mensaje_texto,   # mismo mensaje
                        "ip_origen": ip_local        # nuestra IP para que el otro rebote de vuelta
                    },
                    timeout=3
                )
                print(f"📤 Reenviado a {ip_origen}: '{mensaje_texto}'")
            except Exception as e:
                print(f"⚠️  No se pudo reenviar a {ip_origen}: {str(e)}")

        threading.Thread(target=reenviar).start()

    return jsonify({
        "status": "ok",
        "msj": "Mensaje recibido y rebotado."
    }), 200

@app.route('/api/mensajes/enviar', methods=['POST'])
def enviar_mensaje():
    """Ruta EMISORA: Manda un mensaje a otra PC incluyendo nuestra IP para iniciar el loop."""
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
            "status": "loop iniciado",
            "destino": ip_destino,
            "respuesta_de_la_otra_pc": confirmacion
        }), 200

    except Exception as e:
        return jsonify({"error": f"No se pudo conectar con {ip_destino}: {str(e)}"}), 500

def iniciar_como_primero():
    """Pide IP destino y mensaje por consola, luego dispara el loop."""
    print("\n" + "="*40)
    print("  MODO INICIADOR - Vos sos el primero")
    print("="*40)
    ip_destino = input("📡 IP de la otra PC: ").strip()
    mensaje = input("✉️  Mensaje a enviar: ").strip()

    if not ip_destino or not mensaje:
        print("❌ IP o mensaje vacío. Abortando.")
        return

    import time
    time.sleep(1.5)  # esperamos que Flask arranque

    ip_local = get_ip_local()
    url = f"http://{ip_destino}:5000/api/mensajes/recibir"

    try:
        respuesta = requests.post(
            url,
            json={"mensaje": mensaje, "ip_origen": ip_local},
            timeout=5
        )
        print(f"\n✅ Loop iniciado. Respuesta: {respuesta.json()}")
        print("🔁 El mensaje va a rebotar infinitamente entre las dos PCs.")
        print("   Apagá el servidor (Ctrl+C) para detenerlo.\n")
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
        hilo_servidor = threading.Thread(
            target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
        )
        hilo_servidor.daemon = True
        hilo_servidor.start()

        iniciar_como_primero()

        print("\n🟢 Servidor activo, rebotando mensajes...\n")
        hilo_servidor.join()
    else:
        print("\n🟢 Esperando el primer mensaje...\n")
        app.run(host='0.0.0.0', port=5000, debug=True)