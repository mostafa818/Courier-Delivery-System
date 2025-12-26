# Flask Courier Delivery System Backend

This project is a robust Flask-based backend for a **Courier Delivery System**. It manages the logistics of orders, courier assignments, and delivery tracking using specific user roles and complex model relationships.

## 🚀 Key Features

*   **Delivery Logistics**: Core focus on Order lifecycle from placement to delivery.
*   **Courier Management**: Dedicated `Courier` role with area management and order assignment capabilities.
*   **Customer & Merchant Portals**: Distinct roles for Customers (Receivers) and Merchants (Service Offerors) to manage orders and items.
*   **Dispatch System**: Orders are tracked via status updates and assigned to couriers based on logistics logic.
*   **Cart & Orders**: Flexible system for grouping items into delivery orders.

## 🛠️ Architecture & Tech Stack

*   **Flask & Blueprints**: Modular application structure.
*   **SQLAlchemy ORM**: Complex data modeling inheritance:
    *   **User Hierarchy**: Base `User` class extended by `Courier`, `Customer`, `Admin`, and `ServiceOfferor` (Merchant).
    *   **Relationships**: Many-to-Many associations for `Cart` items and `Order` contents.
*   **Database**: SQLite (default) for easy deployment and testing.

## 📂 Project Structure

*   `app.py`: **Application Factory** entry point.
*   `models.py`: Defines the logistics schema.
    *   `Courier`: Handles status, salary, and service area.
    *   `Order`: Tracks pickup/delivery addresses, weights, and courier assignment.
    *   `ServiceOfferor`: Represents merchants or senders providing the items.
*   `routes.py`: RESTful API endpoints for managing the delivery flow.
*   `extensions.py`: Shared extensions.
*   `verify_backend.py`: Integration testing script.

## 🔧 Setup & Running

1.  **Clone the repository**
2.  **Install dependencies**
    ```bash
    pip install flask flask-sqlalchemy
    ```
3.  **Run Integration Tests**
    Initializes the system and verifies the delivery flow:
    ```bash
    python verify_backend.py
    ```
4.  **Start the Server**
    ```bash
    python app.py
    ```
    API accessible at `http://localhost:5000/api`.

## 🛡️ Security Note

The application defaults to `debug=True` for development ease. **Disable this in production** to prevent Remote Code Execution (RCE) vulnerabilities.
