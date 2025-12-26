from extensions import db
from datetime import datetime
from abc import ABC, ABCMeta, abstractmethod

# Get the actual metaclass from db.Model
ModelMetaclass = type(db.Model)

class CombinedMeta(ModelMetaclass, ABCMeta):
    pass

# Association Tables
cart_products = db.Table('cart_products',
    db.Column('cart_id', db.String(50), db.ForeignKey('cart.id'), primary_key=True),
    db.Column('product_id', db.String(50), db.ForeignKey('product.id'), primary_key=True)
)

order_products = db.Table('order_products',
    db.Column('order_id', db.String(50), db.ForeignKey('order.id'), primary_key=True),
    db.Column('product_id', db.String(50), db.ForeignKey('product.id'), primary_key=True)
)

# Abstract User Class
class User(db.Model, ABC, metaclass=CombinedMeta):
    __abstract__ = True
    
    id = db.Column(db.String(50), primary_key=True) 
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def login(self, password_attempt):
        return self.password == password_attempt

    def sign_up(self):
        db.session.add(self)
        db.session.commit()

    @abstractmethod
    def update_data(self, **kwargs):
        pass
    
    def set_data(self, id, name, email, password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
    
    def get_data(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email
        }

    def to_dict(self):
        return self.get_data()

class Customer(User):
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    
    # Relationships
    orders = db.relationship('Order', backref='customer', lazy=True)
    cart = db.relationship('Cart', backref='customer', uselist=False, lazy=True)

    def update_data(self, **kwargs):
        if 'address' in kwargs: self.address = kwargs['address']
        if 'phone' in kwargs: self.phone = kwargs['phone']
        if 'name' in kwargs: self.name = kwargs['name']
        if 'email' in kwargs: self.email = kwargs['email']
        db.session.commit()

    def get_data(self):
        data = super().get_data()
        data.update({
            "address": self.address,
            "phone": self.phone
        })
        return data

    def create_orders(self, products_list):
        new_order = Order(id=str(datetime.now().timestamp()), customer_id=self.id)
        new_order.products.extend(products_list)
        new_order.calculate_price()
        db.session.add(new_order)
        db.session.commit()
        return new_order

    def view_order(self, order_id):
        return Order.query.filter_by(id=order_id, customer_id=self.id).first()

    def check_profile_data(self):
        return self.get_data()

    def view_cart(self):
        return self.cart

class Admin(User):
    status = db.Column(db.String(50))

    def update_data(self, **kwargs):
        if 'status' in kwargs: self.status = kwargs['status']
        if 'name' in kwargs: self.name = kwargs['name']
        db.session.commit()

    def get_data(self):
        data = super().get_data()
        data.update({
            "status": self.status
        })
        return data

    def manage_products(self):
        pass

    def view_users_profile(self):
        pass

class Courier(User):
    status = db.Column(db.String(50))
    salary = db.Column(db.Float)
    area = db.Column(db.String(100))
    
    orders = db.relationship('Order', backref='courier', lazy=True)

    def update_data(self, **kwargs):
        if 'status' in kwargs: self.status = kwargs['status']
        if 'area' in kwargs: self.area = kwargs['area']
        db.session.commit()

    def get_data(self):
        data = super().get_data()
        data.update({
            "status": self.status,
            "salary": self.salary,
            "area": self.area
        })
        return data

    def view_orders(self):
        return Order.query.filter_by(courier_id=self.id).all()

    def edit_area(self, new_area):
        self.area = new_area
        db.session.commit()

    def choose_order(self, order):
        order.courier_id = self.id
        db.session.commit()

class ServiceOfferor(User):
    service_type = db.Column(db.String(50))
    area = db.Column(db.String(100))
    
    products = db.relationship('Product', backref='provider', lazy=True)

    def update_data(self, **kwargs):
        if 'service_type' in kwargs: self.service_type = kwargs['service_type']
        if 'area' in kwargs: self.area = kwargs['area']
        db.session.commit()

    def get_data(self):
        data = super().get_data()
        data.update({
            "service_type": self.service_type,
            "area": self.area
        })
        return data

    def add_products(self, product):
        product.provider_id = self.id
        db.session.add(product)
        db.session.commit()

    def update_products(self, product, **kwargs):
        if product.provider_id == self.id:
            if 'name' in kwargs: product.name = kwargs['name']
            if 'price' in kwargs: product.price = kwargs['price']
            db.session.commit()

    def remove_products(self, product_id):
        prod = Product.query.get(product_id)
        if prod and prod.provider_id == self.id:
            db.session.delete(prod)
            db.session.commit()

class Product(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    weight = db.Column(db.Float)
    price = db.Column(db.Float)
    category = db.Column(db.String(50))
    status = db.Column(db.String(50))
    
    provider_id = db.Column(db.String(50), db.ForeignKey('service_offeror.id'), nullable=False)

    def get_product_details(self):
        return {
            "id": self.id,
            "name": self.name,
            "details": self.details,
            "price": self.price
        }

    def update_product(self, name, price, details):
        self.name = name
        self.price = price
        self.details = details
        db.session.commit()

    def check_availability(self):
        return self.status == 'Available'

    def calculate_weight(self):
        return self.weight

    def set_availability(self, status):
        self.status = status
        db.session.commit()
    
    def to_dict(self):
        return self.get_product_details()

class Cart(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    price = db.Column(db.Float, default=0.0)
    customer_id = db.Column(db.String(50), db.ForeignKey('customer.id'), nullable=False)
    
    products = db.relationship('Product', secondary=cart_products, lazy='subquery',
        backref=db.backref('carts', lazy=True))

    def add_product(self, product):
        if product not in self.products:
            self.products.append(product)
            self.calculate_price()
            db.session.commit()

    def remove_product(self, product_id):
        product = next((p for p in self.products if p.id == product_id), None)
        if product:
            self.products.remove(product)
            self.calculate_price()
            db.session.commit()

    def calculate_price(self):
        self.price = sum(p.price for p in self.products)
        return self.price

    def clear_cart(self):
        self.products = []
        self.price = 0.0
        db.session.commit()

    def checkout(self):
        pass

class Order(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50))
    pickup_address = db.Column(db.String(200))
    delivery_address = db.Column(db.String(200))
    total_weight = db.Column(db.Float)
    price = db.Column(db.Float)
    
    customer_id = db.Column(db.String(50), db.ForeignKey('customer.id'), nullable=False)
    courier_id = db.Column(db.String(50), db.ForeignKey('courier.id'), nullable=True)

    products = db.relationship('Product', secondary=order_products, lazy='subquery',
        backref=db.backref('orders', lazy=True))

    def create_order(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        db.session.add(self)
        db.session.commit()

    def add_products(self, product):
        self.products.append(product)
        self.calculate_price()
        db.session.commit()

    def remove_products(self, product_id):
        product = next((p for p in self.products if p.id == product_id), None)
        if product:
            self.products.remove(product)
            self.calculate_price()
            db.session.commit()

    def calculate_price(self):
        self.price = sum(p.price for p in self.products if p.price)
        self.total_weight = sum(p.weight for p in self.products if p.weight)
        return self.price

    def update_status(self, new_stats):
        self.status = new_stats
        db.session.commit()

    def cancel_order(self):
        self.status = "Cancelled"
        db.session.commit()

    def change_pickup_addr(self, new_addr):
        self.pickup_address = new_addr
        db.session.commit()

    def change_delivery_addr(self, new_addr):
        self.delivery_address = new_addr
        db.session.commit()
