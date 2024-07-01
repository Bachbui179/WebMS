from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


connection_string = 'mongodb+srv://bach1809:Bach1809.@mycluster.21haxwj.mongodb.net/?retryWrites=true&w=majority'

# Establishing a connection to MongoDB Atlas
client = MongoClient(connection_string)

# Accessing the database
database_name = 'Products'
collection_name = 'products'
db = client[database_name]
collection = db[collection_name]


def verify_token(token):
    url = "http://localhost:3000/auth/verify"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response.status_code == 200

@app.route('/products', methods=['GET'])
def get_products():
    auth_header = request.headers.get('Authorization')
    if auth_header is None or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authorization header missing or invalid'}), 401

    token = auth_header.split(" ")[1]
    if not verify_token(token):
        return jsonify({'error': 'Invalid or expired token'}), 401

    try:
        products_list = list(collection.find({}, {'_id': 0}))
        return jsonify({'products': products_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    auth_header = request.headers.get('Authorization')
    if auth_header is None or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authorization header missing or invalid'}), 401

    token = auth_header.split(" ")[1]
    if not verify_token(token):
        return jsonify({'error': 'Invalid or expired token'}), 401

    try:
        # Load the entire document
        document = collection.find_one({}, {'_id': 0})
        if document and 'products' in document:
            # Iterate through products to find the product with the given product_id
            for product in document['products']:
                if product['id'] == product_id:
                    return jsonify(product), 200
            return jsonify({'error': 'Product not found :()'}), 404
        else:
            return jsonify({'error': 'No products found in database'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=3002, debug=True)
