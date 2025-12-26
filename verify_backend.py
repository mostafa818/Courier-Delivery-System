import requests
import sys
import subprocess
import time
import os

def run_tests():
    print("Starting server...")
    process = subprocess.Popen([sys.executable, "app.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    try:
        time.sleep(5)
        base_url = "http://127.0.0.1:5000/api"

        # 1. Create Provider
        print("Creating Service Offeror...")
        r = requests.post(f"{base_url}/providers", json={
            "name": "Tech Supplier", "email": "s@p1.com", "password": "pass",
            "service_type": "Electronics", "area": "NY"
        })
        if r.status_code != 201: raise Exception(f"Provider failed: {r.text}")
        provider_id = r.json()['id']

        # 1.5 Update Provider
        print("Updating Service Offeror...")
        r = requests.put(f"{base_url}/providers/{provider_id}", json={
            "area": "San Francisco"
        })
        if r.status_code != 200: raise Exception(f"Update Provider failed: {r.text}")
        print(f"Provider Updated: {r.json()['area']}")

        # 2. Create Product
        print("Creating Product...")
        r = requests.post(f"{base_url}/products", json={
            "name": "ipad2", "price": 1000.0, "provider_id": provider_id
        })
        if r.status_code != 201: raise Exception(f"Product failed: {r.text}")
        product_id = r.json()['id']

        # 3. Create Customer
        print("Creating Customer...")
        r = requests.post(f"{base_url}/customers", json={
            "name": "John1", "email": "j@d2.com", "password": "pass"
        })
        if r.status_code != 201: raise Exception(f"Customer failed: {r.text}")
        customer_id = r.json()['id']

        # 4. Update Customer
        print("Updating Customer...")
        r = requests.put(f"{base_url}/customers/{customer_id}", json={
            "address": "Updated Address"
        })
        if r.status_code != 200: raise Exception(f"Update Customer failed: {r.text}")
        print(f"Customer Updated: {r.json()}")

        # 5. Create Order
        print("Creating Order...")
        r = requests.post(f"{base_url}/orders", json={
            "customer_id": customer_id,
            "product_ids": [product_id]
        })
        if r.status_code != 201: raise Exception(f"Order failed: {r.text}")
        print(f"Order Created: {r.json()}")

        # 6. Test Cart
        print("Testing Cart...")
        # Get Empty/New Cart
        r = requests.get(f"{base_url}/customers/{customer_id}/cart")
        if r.status_code != 200: raise Exception(f"Get Cart failed: {r.text}")
        
        # Add to Cart
        r = requests.post(f"{base_url}/customers/{customer_id}/cart/add", json={
            "product_id": product_id
        })
        if r.status_code != 200: raise Exception(f"Add to Cart failed: {r.text}")
        if product_id not in r.json()['products']: raise Exception("Product not added to cart")
        print("Cart: Product added.")

        # Remove from Cart
        r = requests.post(f"{base_url}/customers/{customer_id}/cart/remove", json={
            "product_id": product_id
        })
        if r.status_code != 200: raise Exception(f"Remove from Cart failed: {r.text}")
        if len(r.json()['products']) != 0: raise Exception("Product not removed from cart")
        print("Cart: Product removed.")

        # 7. Create Admin
        print("Creating Admin...")
        r = requests.post(f"{base_url}/admins", json={
            "name": "Admin User", "email": "admin@sys.com", "password": "secure",
            "status": "Active"
        })
        if r.status_code != 201: raise Exception(f"Create Admin failed: {r.text}")
        print(f"Admin Created: {r.json()['name']}")
        
        print("\nSUCCESS: All tests passed.")

    except Exception as e:
        print(f"\nFAILURE: {e}")
        process.kill()
        outs, errs = process.communicate()
        print(outs.decode())
        print(errs.decode())
    finally:
        if process.poll() is None:
            process.terminate()

if __name__ == "__main__":
    run_tests()
