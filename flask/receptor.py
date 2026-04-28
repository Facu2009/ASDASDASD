from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/recibir', methods=['POST'])
def recibir_mensaje():
    # Extraemos la información que nos mandó tu otra PC
    datos = request.get_json()
    
    # Lo imprimimos en la consola para que se vea claro
    print("\n" + "="*40)
    print("🔔 ¡ALERTA! MENSAJE RECIBIDO DE LA OTRA PC")
    print(f"Datos: {datos}")
    print("="*40 + "\n")
    
    # Le devolvemos un "OK" a la PC original para que sepa que llegó
    return jsonify({"status": "ok", "msj": "Recibido sin problemas"}), 200

if __name__ == '__main__':
    # host='0.0.0.0' es crucial para que acepte mensajes desde la red local
    app.run(host='0.0.0.0', port=5000, debug=True)