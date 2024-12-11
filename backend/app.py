from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration
app.config['DEBUG'] = True  # Enable debug mode for development

# Routes
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Flask backend!"})

@app.route('/api/data', methods=['GET'])
def get_data():
    sample_data = {"id": 1, "name": "Sample Data"}
    return jsonify(sample_data)

@app.route('/api/data', methods=['POST'])
def create_data():
    data = request.get_json()
    return jsonify({"message": "Data received", "data": data}), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
