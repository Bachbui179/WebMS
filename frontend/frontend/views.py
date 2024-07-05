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
        product = get_product_by_id(products, id)
    return render(request, 'product_detail.html', {'product': product})

def view_order(request):
    token = request.COOKIES.get('access_token')
    if not token:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # Get user email from user_data cookie
    user_data_cookie = request.COOKIES.get('user_data')
    if not user_data_cookie:
        return JsonResponse({'error': 'User data not found'}, status=401)

    try:
        user_data = json.loads(user_data_cookie.replace("'", '"'))
        email = user_data.get('email')
    except (json.JSONDecodeError, IndexError, KeyError) as e:
        print(f"Error parsing user_data cookie: {e}")
        return JsonResponse({'error': '1Invalid user data'}, status=400)

    # Prepare the data payload
    data = {
        'email': email
    }

    try:
        response = requests.post('http://localhost:5000/order_service/order/get_order', headers=headers, json=data)
        if response.status_code == 200:
            order_data = response.json()
            print(order_data)
            
            for item in order_data['order']:
                item['price_after_discount'] = round(item['price'] * (1 - item['discount_percentage'] / 100), 2)
                item['total'] = round(item['quantity'] * item['price_after_discount'], 2)
            
            return render(request, 'order.html', {'order': order_data['order']})
        else:
            return JsonResponse({'error': 'Unable to fetch cart data'}, status=response.status_code)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def remove_order_item(request, item_id):
    token = request.COOKIES.get('access_token')
    if not token:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    user_data_cookie = request.COOKIES.get('user_data')
    if not user_data_cookie:
        return JsonResponse({'error': 'User data not found'}, status=401)

    try:
        user_data = json.loads(user_data_cookie.replace("'", '"'))
        email = user_data.get('email')
    except (json.JSONDecodeError, IndexError, KeyError) as e:
        return JsonResponse({'error': 'Invalid user data'}, status=400)

    data = {'email': email, 'product_id': item_id}

    try:
        response = requests.post('http://localhost:5000/order_service/order/remove', headers=headers, json=data)
        if response.status_code == 200:
            return redirect('view_order')
        else:
            return JsonResponse({'error': 'Unable to remove item'}, status=response.status_code)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def add_order_item(request, item_id):
    token = request.COOKIES.get('access_token')
    if not token:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    user_data_cookie = request.COOKIES.get('user_data')
    if not user_data_cookie:
        return JsonResponse({'error': 'User data not found'}, status=401)

    try:
        user_data = json.loads(user_data_cookie.replace("'", '"'))
        email = user_data.get('email')
    except (json.JSONDecodeError, IndexError, KeyError) as e:
        return JsonResponse({'error': 'Invalid user data'}, status=400)

    quantity = request.POST.get('quantity')
    if not quantity or int(quantity) < 1:
        return JsonResponse({'error': 'Invalid quantity'}, status=400)

    data = {'email': email, 'product_id': item_id, 'quantity': int(quantity)}

    try:
        response = requests.post('http://localhost:5000/order_service/order/add', headers=headers, json=data)
        if response.status_code == 200:
            return redirect('view_order')
        else:
            return JsonResponse({'error': 'Unable to add item'}, status=response.status_code)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


    
def error_404(request, exception):
    return render(request, '404_Not_Found.html')