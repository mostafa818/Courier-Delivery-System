from flask import Blueprint, jsonify, request
from extensions import db
from models import Customer, Admin, Courier, ServiceOfferor, Product, Order, Cart
import uuid

main = Blueprint('main', __name__)

def generate_id():
    return str(uuid.uuid4())

@main.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    # Check each user type
    # Note: Using _User__email because the model uses private attributes with properties, 
    # so filter_by(email=...) fails to find the column.
    user = Customer.query.filter(Customer._User__email == email).first()
    role = 'customer'
    
    if not user:
        user = Admin.query.filter(Admin._User__email == email).first()
        role = 'admin'
    
    if not user:
        user = ServiceOfferor.query.filter(ServiceOfferor._User__email == email).first()
        role = 'serviceOfferor'
        
    if not user:
        user = Courier.query.filter(Courier._User__email == email).first()
        role = 'courier'
        
    if user:
        print(f"DEBUG LOGIN: User found: {user.name}")
        print(f"DEBUG LOGIN: Stored Pwd: {user.password}")
        print(f"DEBUG LOGIN: Attempt Pwd: {password}")
        print(f"DEBUG LOGIN: Match?: {user.login(password)}")

    if user and user.login(password):
        user_data = user.to_dict()
        user_data['role'] = role
        return jsonify(user_data)
        
    return jsonify({"error": "Invalid email or password"}), 401

@main.route('/api/users', methods=['GET'])
def get_users():
    users = []
    
    # Collect all users from all tables
    for c in Customer.query.all():
        u = c.to_dict()
        u['role'] = 'customer'
        users.append(u)
        
    for a in Admin.query.all():
        u = a.to_dict()
        u['role'] = 'admin'
        users.append(u)
        
    for s in ServiceOfferor.query.all():
        u = s.to_dict()
        u['role'] = 'serviceOfferor'
        users.append(u)
        
    for cr in Courier.query.all():
        u = cr.to_dict()
        u['role'] = 'courier'
        users.append(u)
        
    return jsonify(users)

@main.route('/api/users/<id>', methods=['PUT'])
def update_user_generic(id):
    data = request.get_json()
    
    # Try to find user in each table
    user = Customer.query.get(id)
    if user:
        user.update_data(**data)
        return jsonify(user.to_dict())
        
    user = Admin.query.get(id)
    if user:
        user.update_data(**data)
        return jsonify(user.to_dict())
        
    user = ServiceOfferor.query.get(id)
    if user:
        user.update_data(**data)
        return jsonify(user.to_dict())
        
    user = Courier.query.get(id)
    if user:
        # Special handling for Courier salary which is private
        if 'salary' in data:
            user.salary = float(data['salary'])
        user.update_data(**data)
        return jsonify(user.to_dict())
        
    return jsonify({"error": "User not found"}), 404

# --- Customer Routes ---
@main.route('/api/customers', methods=['POST'])
def create_customer():
    data = request.get_json()
    new_customer = Customer(
        id=generate_id(),
        name=data['name'],
        email=data['email'],
        password=data['password'],
        address=data.get('address'),
        phone=str(data.get('phone'))
    )
    new_customer.sign_up() 
    return jsonify({**new_customer.to_dict(), "role": "customer"}), 201

# Endpoint to get specific customer details
@main.route('/api/customers/<id>', methods=['GET'])
def get_customer(id):
    customer = Customer.query.get(id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify(customer.to_dict())

# --- Product Routes ---
@main.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()
    provider_id = data.get('provider_id')
    
    provider = ServiceOfferor.query.get(provider_id)
    if not provider:
        return jsonify({"error": "Provider not found"}), 404

    new_product = Product(
        id=generate_id(),
        name=data['name'],
        details=data.get('details'),
        weight=data.get('weight'),
        price=data.get('price'),
        category=data.get('category'),
        status=data.get('status')
    )
    
    provider.add_products(new_product)
    
    return jsonify(new_product.to_dict()), 201

@main.route('/api/products/<id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    data = request.get_json()
    # In real app, check permission (e.g. current user is provider)
    # provider = ServiceOfferor.query.get(data['provider_id'])
    # provider.update_products(product, **data)
    
    # Direct update for simplicity or via wrapper
    product.update_product(
        name=data.get('name', product.name),
        price=data.get('price', product.price),
        details=data.get('details', product.details)
    )
    return jsonify(product.to_dict())

@main.route('/api/products/<id>/approve', methods=['PUT'])
def approve_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    product.set_availability('approved') # Reusing set_availability for status update
    return jsonify(product.to_dict())

@main.route('/api/products/<id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
        
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"})

@main.route('/api/products', methods=['GET'])
def get_products():
    # Only return approved products? Or all? Frontend filers them, but typically API should support filtering.
    # For now returning all, frontend filters.
    products = Product.query.all()
    # Enhance product dict with provider name
    result = []
    for p in products:
        d = p.to_dict()
        d['status'] = p.status
        d['category'] = p.category
        d['provider_id'] = p.provider_id
        if p.provider:
            d['ownerName'] = p.provider.name
        result.append(d)
    return jsonify(result)

# --- Service Offeror Routes ---
@main.route('/api/providers', methods=['POST'])
def create_provider():
    data = request.get_json()
    new_provider = ServiceOfferor(
        id=generate_id(),
        name=data['name'],
        email=data['email'],
        password=data['password'],
        service_type=data.get('service_type'),
        area=data.get('area')
    )
    new_provider.sign_up()
    return jsonify({**new_provider.to_dict(), "role": "serviceOfferor"}), 201

@main.route('/api/providers/<id>', methods=['PUT'])
def update_provider(id):
    provider = ServiceOfferor.query.get(id)
    if not provider:
        return jsonify({"error": "Provider not found"}), 404
    
    data = request.get_json()
    provider.update_data(**data)
    return jsonify(provider.to_dict())

@main.route('/api/providers', methods=['GET'])
def get_providers():
    providers = ServiceOfferor.query.all()
    return jsonify([p.to_dict() for p in providers])

# --- Courier Routes ---
@main.route('/api/couriers', methods=['POST'])
def create_courier():
    data = request.get_json()
    new_courier = Courier(
        id=generate_id(),
        name=data['name'],
        email=data['email'],
        password=data['password'],
        area=data.get('area'),
        status="Active"
    )
    new_courier.sign_up()
    return jsonify({**new_courier.to_dict(), "role": "courier"}), 201

@main.route('/api/couriers/<id>/area', methods=['PUT'])
def update_courier_area(id):
    courier = Courier.query.get(id)
    if not courier:
        return jsonify({"error": "Courier not found"}), 404
        
    data = request.get_json()
    new_area = data.get('area')
    courier.edit_area(new_area)
    return jsonify(courier.to_dict())

# --- Order Routes ---
@main.route('/api/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    result = []
    for o in orders:
        # Construct detailed order object
        order_dict = {
            "id": o.id,
            "status": o.status,
            "totalPrice": o.price,
            "date": o.order_date.strftime("%Y-%m-%d"),
            "customerId": o.customer_id,
            "customerName": o.customer.name if o.customer else "Unknown",
            "assignedCourier": o.courier_id,
            "items": [{"name": p.name, "price": p.price} for p in o.products]
        }
        result.append(order_dict)
    return jsonify(result)

@main.route('/api/customers/<cid>/orders', methods=['GET'])
def get_customer_orders(cid):
    customer = Customer.query.get(cid)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
        
    result = []
    for o in customer.orders:
        order_dict = {
            "id": o.id,
            "status": o.status or 'Pending', # Handle None status
            "total_price": o.price,
            "payment_method": "Cash", # Placeholder until DB column added
            "date": o.order_date.strftime("%Y-%m-%d") if o.order_date else "N/A",
            "items": [{"name": p.name, "price": p.price} for p in o.products]
        }
        result.append(order_dict)
    return jsonify(result)

@main.route('/api/orders/<id>', methods=['PUT'])
def update_order(id):
    order = Order.query.get(id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
        
    data = request.get_json()
    
    if 'status' in data:
        order.update_status(data['status'])
        
    if 'courier_id' in data:
        # Assign courier
        order.courier_id = data['courier_id']
        db.session.commit()
        
    return jsonify({"id": order.id, "status": order.status})

@main.route('/api/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    customer_id = data.get('customer_id')
    product_ids = data.get('product_ids', [])
    
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    
    products = Product.query.filter(Product.id.in_(product_ids)).all()
    
    # customer.create_orders returns the order object
    order = customer.create_orders(products)
    
    return jsonify({
        "id": order.id,
        "price": order.price,
        "status": order.status,
        "products": [p.id for p in order.products]
    }), 201

# --- Admin Routes ---
@main.route('/api/admins', methods=['POST'])
def create_admin():
    data = request.get_json()
    new_admin = Admin(
        id=generate_id(),
        name=data['name'],
        email=data['email'],
        password=data['password'],
        status=data.get('status', 'Active')
    )
    new_admin.sign_up()
    return jsonify({**new_admin.to_dict(), "role": "admin"}), 201

# --- Cart Routes ---
@main.route('/api/customers/<customer_id>/cart', methods=['GET'])
def get_cart(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
        
    cart = customer.cart
    if not cart:
        # Create cart if it doesn't exist
        cart = Cart(id=generate_id(), customer_id=customer_id)
        db.session.add(cart)
        db.session.commit()
    
    return jsonify({
        "id": cart.id,
        "price": cart.price,
        "products": [p.to_dict() for p in cart.products]
    })

@main.route('/api/customers/<customer_id>/cart/add', methods=['POST'])
def add_to_cart(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
        
    cart = customer.cart
    if not cart:
        cart = Cart(id=generate_id(), customer_id=customer_id)
        db.session.add(cart)
        db.session.commit()
        
    data = request.get_json()
    product_id = data.get('product_id')
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({"error": "Product not found"}), 404
        
    cart.add_product(product)
    
    return jsonify({
        "message": "Product added to cart",
        "cart_price": cart.price,
        "products": [p.id for p in cart.products]
    })

@main.route('/api/customers/<customer_id>/cart/remove', methods=['POST'])
def remove_from_cart(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
        
    cart = customer.cart
    if not cart:
        return jsonify({"error": "Cart not found"}), 404
        
    data = request.get_json()
    product_id = data.get('product_id')
    
    cart.remove_product(product_id)
    
    return jsonify({
        "message": "Product removed from cart",
        "cart_price": cart.price,
        "products": [p.id for p in cart.products]
    })
