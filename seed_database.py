"""
Database Seeding Script
Seeds the database with sample data from the frontend JavaScript
This includes users, products, and orders.
"""

from app import create_app
from extensions import db
from models import Customer, Admin, Courier, ServiceOfferor, Product, Order, Cart

def seed_database():
    """Seed the database with sample data from frontend"""
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        print("Seeding users...")
        
        # ===== ADMIN USER =====
        admin = Admin(
            id="admin-1",
            name="Mohamed Salah",
            email="admin@email.com",
            password="admin123",
            status="Active"
        )
        db.session.add(admin)
        
        # ===== CUSTOMERS =====
        customers = [
            Customer(
                id="customer-2",
                name="Ahmed Hassan",
                email="ahmed@email.com",
                password="123456",
                address="Cairo, Egypt",
                phone="01234567890"
            ),
            Customer(
                id="customer-3",
                name="Fatma Ali",
                email="fatma@email.com",
                password="123456",
                address="Giza, Egypt",
                phone="01234567891"
            ),
            Customer(
                id="customer-4",
                name="Salma Mostafa",
                email="salma@email.com",
                password="123456",
                address="Alexandria, Egypt",
                phone="01234567892"
            )
        ]
        
        for customer in customers:
            db.session.add(customer)
            # Create empty cart for each customer
            cart = Cart(
                id=f"cart-{customer.id}",
                customer_id=customer.id
            )
            db.session.add(cart)
        
        # ===== SERVICE OFFERORS =====
        service_offerors = [
            ServiceOfferor(
                id="provider-5",
                name="Pizza King Restaurant",
                email="pizza@email.com",
                password="pizza123",
                service_type="Restaurant",
                area="Cairo"
            ),
            ServiceOfferor(
                id="provider-6",
                name="Burger House Egypt",
                email="burger@email.com",
                password="burger123",
                service_type="Restaurant",
                area="Giza"
            ),
            ServiceOfferor(
                id="provider-system",
                name="QuickDeliver",
                email="system@quickdeliver.com",
                password="system123",
                service_type="System",
                area="All"
            )
        ]
        
        for offeror in service_offerors:
            db.session.add(offeror)
        
        # ===== COURIERS =====
        couriers = [
            Courier(
                id="courier-7",
                name="Nour El-Din",
                email="nour@email.com",
                password="nour123",
                area="Downtown Cairo"
            ),
            Courier(
                id="courier-8",
                name="Karim Mahmoud",
                email="karim@email.com",
                password="karim123",
                area="Maadi"
            )
        ]
        
        for courier in couriers:
            db.session.add(courier)
        
        # Commit users first so we can reference them
        db.session.commit()
        print(f"Created {len(customers)} customers")
        print(f"Created {len(service_offerors)} service offerors")
        print(f"Created {len(couriers)} couriers")
        print(f"Created 1 admin")
        
        print("\nSeeding products...")
        
        # ===== PRODUCTS =====
        products_data = [
            # Pizza (approved, owned by Pizza King)
            {
                "id": "product-1",
                "name": "Margherita Pizza",
                "price": 90.0,
                "category": "Pizza",
                "status": "approved",
                "provider_id": "provider-5",
                "details": "Fresh tomato sauce, mozzarella, basil",
                "weight": 500
            },
            {
                "id": "product-2",
                "name": "Pepperoni Pizza",
                "price": 120.0,
                "category": "Pizza",
                "status": "approved",
                "provider_id": "provider-5",
                "details": "Pepperoni slices, mozzarella, tomato sauce",
                "weight": 550
            },
            {
                "id": "product-3",
                "name": "Vegetable Pizza",
                "price": 85.0,
                "category": "Pizza",
                "status": "approved",
                "provider_id": "provider-5",
                "details": "Mixed vegetables, mozzarella, tomato sauce",
                "weight": 500
            },
            
            # Burgers (approved, owned by Burger House)
            {
                "id": "product-4",
                "name": "Classic Beef Burger",
                "price": 75.0,
                "category": "Burgers",
                "status": "approved",
                "provider_id": "provider-6",
                "details": "Beef patty, lettuce, tomato, cheese",
                "weight": 300
            },
            {
                "id": "product-5",
                "name": "Crispy Chicken Burger",
                "price": 65.0,
                "category": "Burgers",
                "status": "approved",
                "provider_id": "provider-6",
                "details": "Crispy chicken, lettuce, mayo",
                "weight": 280
            },
            
            # Drinks (approved, no specific owner - admin added)
            {
                "id": "product-6",
                "name": "Fresh Orange Juice",
                "price": 25.0,
                "category": "Drinks",
                "status": "approved",
                "provider_id": "provider-system",
                "details": "Freshly squeezed orange juice",
                "weight": 250
            },
            {
                "id": "product-7",
                "name": "Coca Cola",
                "price": 15.0,
                "category": "Drinks",
                "status": "approved",
                "provider_id": "provider-system",
                "details": "330ml can",
                "weight": 330
            },
            
            # Desserts (approved)
            {
                "id": "product-8",
                "name": "Kunafa Nabulsia",
                "price": 45.0,
                "category": "Desserts",
                "status": "approved",
                "provider_id": "provider-system",
                "details": "Traditional Middle Eastern dessert",
                "weight": 200
            },
            {
                "id": "product-9",
                "name": "Om Ali",
                "price": 35.0,
                "category": "Desserts",
                "status": "approved",
                "provider_id": "provider-system",
                "details": "Traditional Egyptian dessert",
                "weight": 180
            },
            
            # Pending product (needs approval)
            {
                "id": "product-10",
                "name": "Seafood Pizza Special",
                "price": 150.0,
                "category": "Pizza",
                "status": "pending",
                "provider_id": "provider-5",
                "details": "Shrimp, squid, mussels, mozzarella",
                "weight": 600
            }
        ]
        
        products = []
        for product_data in products_data:
            product = Product(
                id=product_data["id"],
                name=product_data["name"],
                price=product_data["price"],
                category=product_data["category"],
                status=product_data["status"],
                provider_id=product_data["provider_id"],
                details=product_data.get("details"),
                weight=product_data.get("weight")
            )
            db.session.add(product)
            products.append(product)
        
        db.session.commit()
        print(f"Created {len(products)} products")
        print(f"  - {len([p for p in products if p.status == 'approved'])} approved")
        print(f"  - {len([p for p in products if p.status == 'pending'])} pending approval")
        
        print("\nSeeding sample order...")
        
        # ===== SAMPLE ORDER =====
        # Create a sample order for Ahmed Hassan
        order = Order(
            id="order-1001",
            price=120.0,
            status="preparing",
            customer_id="customer-2"
        )
        db.session.add(order)
        
        # Add products to the order
        # Margherita Pizza + 2x Coca Cola = 90 + 15 + 15 = 120 EGP
        margherita = Product.query.get("product-1")
        cola = Product.query.get("product-7")
        
        if margherita and cola:
            order.products.append(margherita)
            order.products.append(cola)
        
        db.session.commit()
        print(f"Created 1 sample order")
        
        print("\n" + "="*50)
        print("Database seeding completed successfully!")
        print("="*50)
        print(f"\nSummary:")
        print(f"  Users: {len(customers) + len(service_offerors) + len(couriers) + 1}")
        print(f"    - Customers: {len(customers)}")
        print(f"    - Service Offerors: {len(service_offerors)}")
        print(f"    - Couriers: {len(couriers)}")
        print(f"    - Admins: 1")
        print(f"  Products: {len(products)}")
        print(f"  Orders: 1")
        print(f"\nTest Login Credentials:")
        print(f"  Admin: admin@email.com / admin123")
        print(f"  Customer: ahmed@email.com / 123456")
        print(f"  Service Offeror: pizza@email.com / pizza123")
        print(f"  Courier: nour@email.com / nour123")

if __name__ == '__main__':
    seed_database()
