from flask import Blueprint, jsonify, request
from extensions import db
from models import Customer, Admin, Courier, ServiceOfferor, Product, Order, Cart
import uuid

main = Blueprint('main', __name__)

def generate_id():
    return str(uuid.uuid4())

@main.route('/api/test')
def list_routes():
    return jsonify({"message": "Server is running"})

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
    return jsonify(new_customer.to_dict()), 201

@main.route('/api/customers/<id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get(id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    
    data = request.get_json()
    customer.update_data(**data)
    return jsonify(customer.to_dict())

@main.route('/api/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return jsonify([c.to_dict() for c in customers])

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

@main.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])

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
    return jsonify(new_provider.to_dict()), 201

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

# --- Order Routes ---
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
    return jsonify(new_admin.to_dict()), 201

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
