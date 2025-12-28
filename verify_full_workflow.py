import requests
import sys
import subprocess
import time
import os
import json

# Configuration
BASE_URL = "http://127.0.0.1:5000/api"
DB_FILE = "test.db"

def print_pass(msg):
    print(f"[PASS] {msg}")

def print_fail(msg):
    print(f"[FAIL] {msg}")
    sys.exit(1)

def run_workflow():
    # 1. Start Flask Server in background
    print("Starting Flask Server...")
    # Using the python executable that we know exists
    python_exe = sys.executable
    process = subprocess.Popen([python_exe, "app.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    try:
        # Wait for server to start
        time.sleep(3)
        
        # Session to store cookies if needed (though we use token/id mostly)
        session = requests.Session()

        print("\n--- 1. AUTHENTICATION FLOW ---")
        
        # Test Signup
        print("Testing Customer Signup...")
        unique_email = f"test_{int(time.time())}@user.com"
        signup_data = {"name": "Test Customer", "email": unique_email, "password": "password123", "role": "customer"}
        res = session.post(f"{BASE_URL}/customers", json=signup_data)
        if res.status_code != 201: print_fail(f"Signup failed: {res.text}")
        customer_id = res.json()['id']
        print_pass(f"Customer Signup ({unique_email})")
        
        # DEBUG: Check if user exists
        print("DEBUG: Fetching all users...")
        res = session.get(f"{BASE_URL}/users")
        if res.status_code == 200:
            users_list = res.json()
            found = any(u['email'] == unique_email for u in users_list)
            if found: print(f"DEBUG: User '{unique_email}' FOUND in list")
            else: print(f"DEBUG: User '{unique_email}' NOT FOUND in list")
        else:
            print(f"DEBUG: Failed to fetch users: {res.status_code}")

        # Test Login
        print("Testing Login...")
        login_data = {"email": unique_email, "password": "password123"}
        res = session.post(f"{BASE_URL}/login", json=login_data)
        if res.status_code != 200: print_fail(f"Login failed: {res.text}")
        user_data = res.json()
        if user_data['role'] != 'customer': print_fail("Wrong role returned on login")
        print_pass(f"Login successful as {user_data['name']}")


        print("\n--- 2. SERVICE OFFEROR FLOW ---")
        
        # Create Service Offeror (Admin function usually, but via API direct for test)
        # Note: In our app, Admin creates these. Let's start by logging in as Admin (seeded)
        admin_login = {"email": "admin@email.com", "password": "admin123"} # From seed_database.py
        res = session.post(f"{BASE_URL}/login", json=admin_login)
        if res.status_code == 200:
            print_pass("Admin Login (Seeded)")
        else:
            print("Seeded admin not found, creating new admin for test...")
            res = session.post(f"{BASE_URL}/admins", json={"name": "Test Admin", "email": "newadmin@test.com", "password": "admin", "status": "active"})
            if res.status_code != 201: print_fail("Could not create admin")
            print_pass("Admin Created")

        # Create Service Offeror via API
        print("Creating Service Offeror...")
        provider_data = {"name": "Pizza King", "email": f"pizza_{int(time.time())}@king.com", "password": "pizza", "service_type": "Food", "area": "Cairo"}
        res = session.post(f"{BASE_URL}/providers", json=provider_data)
        if res.status_code != 201: print_fail("Provider creation failed")
        provider_id = res.json()['id']
        print_pass("Service Offeror Created")

        # Service Offeror adds product
        print("Adding Product (Pending)...")
        product_data = {
            "name": "Super Pizza", 
            "price": 150.0, 
            "category": "Pizza", 
            "provider_id": provider_id,
            "status": "pending",
            "details": "Yummy",
            "weight": 0.5
        }
        res = session.post(f"{BASE_URL}/products", json=product_data)
        if res.status_code != 201: print_fail("Product creation failed")
        product_id = res.json()['id']
        print_pass("Product Added")


        print("\n--- 3. ADMIN PRODUCT APPROVAL ---")
        
        # Approve Product
        print("Approving Product...")
        res = session.put(f"{BASE_URL}/products/{product_id}/approve")
        if res.status_code != 200: print_fail("Product approval failed")
        if res.json()['status'] != 'approved': print_fail("Product status not updated")
        print_pass("Product Approved")


        print("\n--- 4. CUSTOMER ORDER FLOW ---")
        
        # Add to Cart
        print("Adding to Cart...")
        res = session.post(f"{BASE_URL}/customers/{customer_id}/cart/add", json={"product_id": product_id})
        if res.status_code != 200: print_fail("Add to cart failed")
        print_pass("Added to Cart")

        # Verify Cart
        res = session.get(f"{BASE_URL}/customers/{customer_id}/cart")
        cart_data = res.json()
        if len(cart_data['products']) == 0: print_fail("Cart is empty")
        print_pass("Cart Verified")

        # Checkout (Create Order)
        print("Checking Out...")
        order_data = {
            "customer_id": customer_id,
            "product_ids": [product_id],
            "payment_method": "cash"
        }
        res = session.post(f"{BASE_URL}/orders", json=order_data)
        if res.status_code != 201: print_fail(f"Checkout failed: {res.text}")
        order_id = res.json()['id']
        print_pass(f"Order Created: #{order_id}")

        # Verify Order History (GET /orders)
        print("Verifying Order History...")
        res = session.get(f"{BASE_URL}/customers/{customer_id}/orders")
        if res.status_code != 200: print_fail("Failed to fetch order history")
        orders = res.json()
        if len(orders) == 0: print_fail("Order history is empty")
        if 'total_price' not in orders[0]: print_fail("Missing total_price in order history")
        print_pass("Order History Verified")


        print("\n--- 5. COURIER FLOW ---")
        
        # Create Courier (Admin function)
        print("Creating Courier...")
        courier_data = {"name": "Fast Courier", "email": f"run_{int(time.time())}@fast.com", "password": "run", "vehicle": "Bike", "area": "Cairo"}
        res = session.post(f"{BASE_URL}/couriers", json=courier_data)
        if res.status_code != 201: print_fail("Courier creation failed")
        courier_id = res.json()['id']
        print_pass("Courier Created")

        # Update Delivery Area
        print("Updating Courier Area...")
        res = session.put(f"{BASE_URL}/couriers/{courier_id}/area", json={"area": "Cairo"})
        if res.status_code != 200: print_fail("Area update failed")
        print_pass("Courier Area Updated")

        # Update Order Status (simulate courier action)
        print("Updating Order Status...")
        res = session.put(f"{BASE_URL}/orders/{order_id}", json={"status": "on-the-way"})
        if res.status_code != 200: print_fail("Order status update failed")
        print_pass("Order Status Updated to 'on-the-way'")


        print("\nALL WORKFLOW TESTS PASSED SUCCESSFULLY!")
        print("The Frontend and Backend are correctly integrated via these API contracts.")

    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
    finally:
        print("\nStopping Server...")
        try:
            process.kill()
        except:
            pass
            
        try:
            # Wait briefly for output then give up to avoid hanging
            outs, errs = process.communicate(timeout=5)
            print("\n--- SERVER OUTPUT ---")
            print(outs.decode(errors='ignore'))
            print("\n--- SERVER ERRORS ---")
            print(errs.decode(errors='ignore'))
        except subprocess.TimeoutExpired:
            print("Server output capture timed out.")

if __name__ == "__main__":
    run_workflow()
