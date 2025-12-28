# QuickDeliver 🚀
> A modern, API-driven delivery application.

QuickDeliver is a Flask-based full-stack web application that facilitates seamless order processing between Customers, Service Offerors (Restaurants/Shops), Couriers, and Admins.

## 🛠️ Tech Stack
- **Backend**: Python, Flask, Flask-SQLAlchemy, SQLite
- **Frontend**: Vanilla JavaScript (ES6+), HTML5, CSS3
- **Architecture**: REST API with role-based access control (RBAC)

## ✨ Key Features
- **Frontend-Backend Integration**: Full separation of concerns; the frontend communicates exclusively via REST API endpoints.
- **Multi-Role System**:
  - **Customers**: Browse products, manage cart, place orders, and track status.
  - **Service Offerors**: Manage products (Create, Update, Delete).
  - **Couriers**: Set delivery areas and manage assigned orders.
  - **Admins**: Approve products, manage users, and oversee platform activity.
- **Robust Verification**: Automated end-to-end testing script (`verify_full_workflow.py`) validates critical user flows.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation
1.  Clone the repository and navigate to the project directory.
2.  Install dependencies:
    ```bash
    pip install flask flask-sqlalchemy flask-cors requests
    ```

### Database Setup
Initialize and seed the database with test data:
```bash
python seed_database.py
```
*Note: This script clears any existing data and repopulates tables with default users and products.*

### Running the Application
Start the Flask development server:
```bash
python app.py
```
Access the application at: `http://127.0.0.1:5000`

## 🧪 Testing
Run the full verification suite to test all API workflows:
```bash
python verify_full_workflow.py
```

## 🔐 Default Credentials
Use these accounts to test different roles:

| Role | Email | Password |
|------|-------|----------|
| **Admin** | `admin@email.com` | `admin123` |
| **Customer** | `ahmed@email.com` | `123456` |
| **Service Provider** | `pizza@email.com` | `pizza123` |
| **Courier** | `nour@email.com` | `nour123` |

---
*Built with ❤️ by the QuickDeliver Team*
