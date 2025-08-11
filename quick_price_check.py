import requests
import json

# Test the dashboard API
response = requests.get('http://127.0.0.1:5000/api/products')
data = response.json()

print("Dashboard API Prices:")
print("=" * 40)
for product in data.get('products', []):
    title = product.get('title', '')
    price = product.get('variants', [{}])[0].get('price', '0')
    print(f"{title}: ${price}")
