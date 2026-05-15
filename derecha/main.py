import sys
import os
import threading
import requests
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# --- CARGA DEL ARCHIVO .env ---
load_dotenv()

app = Flask(__name__)

# --- CONFIGURACIÓN DESDE .env ---
DESTINATION_URL  = os.getenv("DESTINATION_URL")
MY_PORT          = int(os.getenv("MY_PORT"))
MY_NAME          = os.getenv("MY_NAME")
LIMITE_CONTADOR  = int(os.getenv("LIMITE_CONTADOR"))

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/', methods=['POST'])
def receive():
    """Endpoint que recibe el paquete, modifica el mensaje y retransmite."""
    data = request.get_json()

    original_msg = data.get('name', '')
    counter      = data.get('counter', 0)
    repetidores  = data.get('repetidores', [])

    if MY_NAME not in repetidores:
        repetidores.append(MY_NAME)

    print(f"\n[RECIBIDO] Mensaje original: '{original_msg}'")
    print(f"-> Counter: {counter}")
    print(f"-> Repetidores: {', '.join(repetidores)}")

    if counter >= LIMITE_CONTADOR:
        print(f"\n{'='*40}\n¡LÍMITE ALCANZADO! Finalizando...\n{'='*40}")
        return jsonify({"status": "mensaje detenido", "counter": counter})

    new_counter = counter + 1
    payload = {
        'name':    MY_NAME,
        'counter':    new_counter,
        'repetidores': repetidores
    }

    try:
        requests.post(DESTINATION_URL, json=payload, timeout=3)
        print(f"[RETRANSMITIDO] Mensaje cambiado a '{MY_NAME}' enviado a {DESTINATION_URL}")
    except Exception as e:
        print(f"[ERROR] No se pudo retransmitir: {e}")

    return jsonify({"status": "ok"}), 200


def manual_sender():
    """Hilo para originar un mensaje nuevo desde la terminal."""
    print(f"--- MODO TERMINAL ACTIVO (Puerto: {MY_PORT}) ---")
    print(f"Escribe cualquier cosa y pulsa ENTER para iniciar la cadena con tu nombre:\n")
    while True:
        try:
            user_input = input("> ")
            if user_input.strip():
                payload = {
                    'name':    MY_NAME,
                    'counter':    0,
                    'repetidores': [MY_NAME]
                }
                requests.post(DESTINATION_URL, json=payload, timeout=3)
                print(f"[ORIGINADO] Cadena iniciada con mensaje: '{MY_NAME}'")
        except EOFError:
            break
        except Exception as e:
            print(f"[ERROR MANUAL] {e}")


if __name__ == '__main__':
    sender_thread = threading.Thread(target=manual_sender, daemon=True)
    sender_thread.start()
    try:
        app.run(host='0.0.0.0', port=MY_PORT, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\nPrograma detenido.")
        sys.exit()