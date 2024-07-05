from flask import Flask, request, jsonify
from flask_cors import CORS
from requests import request as proxy_request
import jwt
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes

# Configuration for different services
services = {
    'auth_service': 'http://localhost:3000',
    'product_service': 'http://localhost:3002',
    'order_service': 'http://localhost:3001',
}

product_service_url = 'http://localhost:3002'
order_service_url= 'http://localhost:3001'

def proxy(service_url):
    try:
        response = proxy_request(
            method=request.method,
            url=service_url + request.full_path.replace('/auth_service', ''),
            headers={key: value for (key, value) in request.headers if key != 'Host'},
            json=request.get_json(),
            cookies=request.cookies,
            allow_redirects=False
        )
        return response.content, response.status_code, response.headers.items()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def verify_jwt(token):
    try:
        url = 'http://localhost:3000/auth/verify'
        headers = {'Authorization': token}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error verifying token: {e}")
        return False

@app.route('/product_service/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def product_service_proxy(path):
    token = request.headers.get('Authorization')
    if token and verify_jwt(token):
        # Forward the request to the product service
        url = f'{product_service_url}/{path}'
        headers = {key: value for key, value in request.headers if key != 'Host'}

        if request.method == 'GET':
            response = requests.get(url, headers=headers, params=request.args)
        elif request.method == 'POST':
            response = requests.post(url, headers=headers, json=request.json)
        elif request.method == 'PUT':
            response = requests.put(url, headers=headers, json=request.json)
        elif request.method == 'DELETE':
            response = requests.delete(url, headers=headers)

        return (response.content, response.status_code, response.headers.items())
    else:
        return jsonify({'error': 'Unauthorized'}), 401

@app.route('/order_service/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def order_service_proxy(path):
    token = request.headers.get('Authorization')
    if token and verify_jwt(token):
        # Forward the request to the order service
        url = f'{order_service_url}/{path}'  # Corrected URL construction
        headers = {key: value for key, value in request.headers if key != 'Host'}

        if request.method == 'GET':
            response = requests.get(url, headers=headers, params=request.args)
        elif request.method == 'POST':
            response = requests.post(url, headers=headers, json=request.json)
        elif request.method == 'PUT':
            response = requests.put(url, headers=headers, json=request.json)
        elif request.method == 'DELETE':
            response = requests.delete(url, headers=headers)

        return (response.content, response.status_code, response.headers.items())
    else:
        return jsonify({'error': 'Unauthorized'}), 401

if __name__ == '__main__':
    app.run(port=5000, debug=True)