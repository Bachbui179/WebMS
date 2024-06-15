import json
import boto3

def fetch_products():
    # Read the products from the JSON file
    with open('store_info.json') as f:
        products_list = json.load(f)
    return products_list['products']  # Assuming 'products' is the key in your JSON file

# Initialize a session using Amazon DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('BachProducts')

# Load JSON data
products = fetch_products()

# Insert data into the DynamoDB table
try:
    for product in products:
        response = table.put_item(Item=product)
        print(f"Inserted product with ID: {product['id']}")
except Exception as e:
    print(f"Error inserting data: {e}")

print("Data insertion completed.")
