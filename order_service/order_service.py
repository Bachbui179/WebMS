from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

connection_string = 'mongodb+srv://bach1809:Bach1809.@mycluster.21haxwj.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(connection_string)

# Accessing the database
user_database_name = 'Users'
user_collection_name = 'users'
user_db = client[user_database_name]
user_collection = user_db[user_collection_name]

product_database_name = 'Products'
product_collection_name = 'products'
product_db = client[product_database_name]
product_collection = product_db[product_collection_name]

def verify_token(token):
    url = "http://localhost:3000/auth/verify"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response.status_code == 200

def get_product_details(product_id, token):
    url = f"http://localhost:3002/products/{product_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
@app.route('/order/get_cart', methods=['POST'])
def get_cart():
    data = request.json
    email = data.get('email')
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authorization header missing or invalid'}), 401

    token = auth_header.split(" ")[1]

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    user = user_collection.find_one({'users.email': email}, {'users.$': 1})

    if user is None:
        return jsonify({'error': 'User not found'}), 404

    user = user['users'][0]  # Extract the user object from the result

    return jsonify({'cart': user.get('cart', [])}), 200

@app.route('/order/add', methods=['POST'])
def add_to_cart():
    auth_header = request.headers.get('Authorization')
    if auth_header is None or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authorization header missing or invalid'}), 401

    token = auth_header.split(" ")[1]
    if not verify_token(token):
        return jsonify({'error': 'Invalid or expired token'}), 401

    data = request.get_json()
    email = data.get('email')
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    if not email or not product_id or not quantity:
        return jsonify({'error': 'Missing data'}), 400

    user = user_collection.find_one({"users.email": email}, {"_id": 0, "users.$": 1})
    
    if user:
        user = user['users'][0]
        product_details = get_product_details(product_id, token)
        if not product_details:
            return jsonify({'error': 'Product not found'}), 404

        cart_item = {
            "product_id": product_id,
            "title": product_details['title'],
            "price": product_details['price'],
            "discount_percentage": product_details['discount_percentage'],
            "stock": product_details['stock'],
            "quantity": quantity
        }

        user_collection.update_one(
            {"users.email": email},
            {"$push": {"users.$.cart": cart_item}}
        )

        return jsonify({'message': 'Product added to cart'}), 200
    else:
        return jsonify({'error': 'User not found'}), 404

if __name__ == '__main__':
    app.run(port=3001)
