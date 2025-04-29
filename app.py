import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env (opcional)
load_dotenv()


def create_app():


    app = Flask(__name__)

    # Obtener configuración desde variables de entorno
    MONGO_URI = os.environ.get('MONGO_URI')
    DB_NAME = os.environ.get('DB_NAME')
    COLLECTION_NAME = os.environ.get('COLLECTION_NAME')

    # Conectar a MongoDB
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    @app.route('/send-data', methods=['POST'])
    def receive_data():
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400

        # Validación de parámetros esperados
        if not all(k in data for k in ('presion', 'temperatura', 'humedad')):
            return jsonify({'status': 'error', 'message': 'Missing parameters'}), 400

        try:
            data['timestamp'] = datetime.utcnow()
            collection.insert_one(data)
            return jsonify({'status': 'success', 'message': 'Data saved'}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/get-data', methods=['GET'])
    def get_data():
        try:
            data = list(collection.find().sort('timestamp', -1).limit(10))
            for entry in data:
                entry['_id'] = str(entry['_id'])  # Convertir ObjectId a string
            return jsonify(data), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app_instance = create_app()
    # host='0.0.0.0' permite acceso desde otros gidispositivos en la red local
    app_instance.run(debug=True)
