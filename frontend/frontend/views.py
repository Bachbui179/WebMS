from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import requests
import json

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        response = requests.post('http://localhost:3000/auth/login', json={'email': email, 'password': password})
        
        if response.status_code == 200:
            token = response.json().get('access_token')
            
            headers = {'Authorization': f'Bearer {token}'}
            user_response = requests.get('http://localhost:3000/auth/user', headers=headers)
            
            if user_response.status_code == 200:
                user_data = user_response.json()

                # Set the token and user data in cookies
                response = redirect('/home/')
                response.set_cookie('access_token', token)
                response.set_cookie('user_data', json.dumps(user_data))
                return response
            else:
                return render(request, 'login.html', {'error': 'Failed to fetch user data'})
            
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
        
    return render(request, 'login.html')

def logout_view(request):
    response = redirect('login')
    response.delete_cookie('access_token')
    response.delete_cookie('user_data')
    return response

def home_view(request):
    token = request.COOKIES.get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.get('http://localhost:5000/product_service/products', headers=headers)
    
    if response.status_code == 200:
        products = response.json().get('products', [])
        categories = set(product.get('category') for product in products)
        return render(request, 'home.html', {'products': products, 'categories': categories})
    else:
        return redirect('login')

def product_view(request):
    token = request.COOKIES.get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.get('http://localhost:5000/product_service/products', headers=headers)
    
    if response.status_code == 200:
        products_data = response.json().get('products', [])
        products = [item for sublist in products_data for item in sublist['products']]
        categories = set(product.get('category') for product in products)
        print(products)
        return render(request, 'products.html', {'products': products, 'categories': categories})
    else:
        return redirect('login.html')


def get_product_by_id(products, id):
    for product in products:
        if product['id'] == id:
            return product
    return None
    
def product_detail(request, id):
    token = request.COOKIES.get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.get('http://localhost:5000/product_service/products', headers=headers)
    
    if response.status_code == 200:
        products_data = response.json().get('products', [])
        products = [item for sublist in products_data for item in sublist['products']]
        print(products)
        product = get_product_by_id(products, id)
    return render(request, 'product_detail.html', {'product': product})

def cart(request): 
    token = request.COOKIES.get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.get('http://localhost:5000/order_service/orders', headers=headers)

def error_404(request, exception):
    return render(request, '404_Not_Found.html')