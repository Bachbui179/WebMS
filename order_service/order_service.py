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
    
@app.route('/order/get_order', methods=['POST'])
def get_order():
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

    return jsonify({'order': user.get('order', [])}), 200


@app.route('/order/add', methods=['POST'])
def add_to_order():
    data = request.get_json()
    email = data.get('email')
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authorization header missing or invalid'}), 401

    token = auth_header.split(" ")[1]
    if not verify_token(token):
        return jsonify({'error': 'Invalid or expired token'}), 401

    user = user_collection.find_one({"users.email": email}, {"users.$": 1})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    product = get_product_details(product_id, token)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    user_data = user['users'][0]
    order_item = {
        "product_id": product['id'],
        "title": product['title'],
        "price": product['price'],
        "discount_percentage": product['discount_percentage'],
        "stock": product['stock'],
        "quantity": quantity
    }

    # Update order in the user document
    user_collection.update_one(
        {"users.email": email},
        {"$push": {"users.$.order": order_item}}
    )

    return jsonify({'message': 'Product added to order successfully'}), 200

@app.route('/order/remove', methods=['POST'])
def remove_item():
    data = request.json
    email = data.get('email')
    product_id = data.get('product_id')
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authorization header missing or invalid'}), 401

    token = auth_header.split(" ")[1]

    if not email or not product_id:
        return jsonify({'error': 'Email and product ID are required'}), 400

    user = user_collection.find_one({'users.email': email}, {'users.$': 1})

    if user is None:
        return jsonify({'error': 'User not found'}), 404

    user = user['users'][0]  # Extract the user object from the result

    # Remove item from order
    user_collection.update_one(
        {'users.email': email},
        {'$pull': {'users.$.order': {'product_id': product_id}}}
    )

    return jsonify({'message': 'Item removed successfully'}), 200



if __name__ == '__main__':
    app.run(port=3001)
