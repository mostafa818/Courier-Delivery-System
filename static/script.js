/* ==================== CONFIGURATION ==================== */
const API_BASE_URL = '/api';

/* ==================== GLOBAL STATE ==================== */
// We now rely on the backend for data, but we keep some UI state here
let currentUser = null; // Will store the logged-in user object from API
let selectedProductId = null; // Checks which product is being edited
let currentCategoryFilter = 'all'; // Current filter for products

/* ==================== SECTION 1: INITIALIZATION ====================
   Code that runs when the page loads.
   ================================================================== */

document.addEventListener('DOMContentLoaded', function () {
    console.log("🚀 QuickDeliver Frontend Loaded");

    // Check if we verify session on load? (Optional future enhancement)
    // For now we start at login screen
});


/* ==================== SECTION 2: AUTHENTICATION ====================
   Login and Signup functions.
   ================================================================== */

function showAuthTab(tab) {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const tabs = document.querySelectorAll('.auth-tab');

    tabs.forEach(t => t.classList.remove('active'));

    if (tab === 'login') {
        loginForm.classList.remove('hidden');
        signupForm.classList.add('hidden');
        tabs[0].classList.add('active');
    } else {
        loginForm.classList.add('hidden');
        signupForm.classList.remove('hidden');
        tabs[1].classList.add('active');
    }
}

/**
 * handleLogin(event)
 * Calls POST /api/login
 */
async function handleLogin(event) {
    event.preventDefault();

    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Login failed');
        }

        currentUser = await response.json();
        showToast(`Login successful! Welcome ${currentUser.name} 🎉`, 'success');
        redirectToRolePage();

    } catch (error) {
        showToast(error.message, 'error');
        console.error('Login error:', error);
    }
}

/**
 * handleSignup(event)
 * Calls POST /api/customers
 */
async function handleSignup(event) {
    event.preventDefault();

    const name = document.getElementById('signupName').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;

    try {
        const response = await fetch(`${API_BASE_URL}/customers`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Signup failed');
        }

        const newUser = await response.json();
        // Auto-login (store user as current)
        currentUser = newUser;

        showToast('Account created successfully! Welcome! 🎉', 'success');
        redirectToRolePage();

    } catch (error) {
        showToast(error.message, 'error');
        console.error('Signup error:', error);
    }
}

/**
 * logout()
 * Clears current user and returns to login.
 */
function logout() {
    currentUser = null;
    document.getElementById('mainApp').classList.add('hidden');
    document.getElementById('loginPage').classList.remove('hidden');

    // Clear forms
    document.getElementById('loginForm').reset();
    document.getElementById('signupForm').reset();

    showToast('Logged out successfully', 'success');
}

/**
 * redirectToRolePage()
 * Shows the correct section based on currentUser.role
 */
function redirectToRolePage() {
    // Hide login page
    document.getElementById('loginPage').classList.add('hidden');
    // Show main app
    document.getElementById('mainApp').classList.remove('hidden');

    // Update Header Info
    document.getElementById('welcomeUser').textContent = `Welcome, ${currentUser.name}`;
    document.getElementById('userRoleBadge').textContent = formatRoleName(currentUser.role);

    // Hide all role sections first
    document.querySelectorAll('.role-section').forEach(el => el.classList.add('hidden'));
    document.getElementById('userAccountsLink').classList.add('hidden');

    // Show specific section
    if (currentUser.role === 'customer') {
        document.getElementById('customerSection').classList.remove('hidden');
        displayProducts();
        displayCart();
        displayCustomerOrders();
    }
    else if (currentUser.role === 'admin') {
        document.getElementById('adminSection').classList.remove('hidden');
        document.getElementById('userAccountsLink').classList.remove('hidden');
        displayPendingProducts();
        displayAdminProducts();
        displayUsersTable();
    }
    else if (currentUser.role === 'serviceOfferor') {
        document.getElementById('serviceOfferorSection').classList.remove('hidden');
        displayServiceProducts();
    }
    else if (currentUser.role === 'courier') {
        document.getElementById('courierSection').classList.remove('hidden');
        // Pre-fill area
        document.getElementById('deliveryArea').value = currentUser.area || '';
        document.getElementById('currentArea').textContent = currentUser.area || 'Not set';
        displayCourierOrders();
    }
}


/* ==================== SECTION 3: CUSTOMER FUNCTIONS ==================== */

/**
 * displayProducts()
 * Fetches approved products from /api/products
 */
async function displayProducts() {
    const container = document.getElementById('productsList');
    container.innerHTML = '<p>Loading products...</p>';

    try {
        const response = await fetch(`${API_BASE_URL}/products`);
        if (!response.ok) throw new Error('Failed to fetch products');

        const products = await response.json();
        const approvedProducts = products.filter(p => p.status === 'approved');

        // Apply Category Filter
        const filtered = currentCategoryFilter === 'all'
            ? approvedProducts
            : approvedProducts.filter(p => p.category === currentCategoryFilter);

        container.innerHTML = '';

        if (filtered.length === 0) {
            container.innerHTML = '<p>No products found in this category.</p>';
            return;
        }

        filtered.forEach(product => {
            const card = document.createElement('div');
            card.className = 'product-card';
            card.innerHTML = `
                <div class="product-icon">${getCategoryIcon(product.category)}</div>
                <div class="product-info">
                    <h4>${product.name}</h4>
                    <p class="product-price">${product.price} EGP</p>
                    <button onclick="addToCart('${product.id}')" class="btn btn-sm btn-primary">Add to Cart</button>
                </div>
            `;
            container.appendChild(card);
        });

    } catch (error) {
        container.innerHTML = '<p class="error-text">Error loading products.</p>';
        console.error(error);
    }
}

function filterByCategory(category) {
    currentCategoryFilter = category;

    // Update button styles
    document.querySelectorAll('.category-btn').forEach(btn => {
        if (btn.textContent.includes(category) || (category === 'all' && btn.textContent === 'All')) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    displayProducts();
}

/**
 * addToCart(productId)
 * Calls POST /api/customers/{id}/cart/add
 */
async function addToCart(productId) {
    try {
        const response = await fetch(`${API_BASE_URL}/customers/${currentUser.id}/cart/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId })
        });

        if (!response.ok) throw new Error('Failed to add to cart');

        showToast('Added to cart!', 'success');
        displayCart();

    } catch (error) {
        showToast(error.message, 'error');
    }
}

/**
 * displayCart()
 * Fetches cart from /api/customers/{id}/cart
 */
async function displayCart() {
    const cartItemsDiv = document.getElementById('cartItems');
    const cartTotalSpan = document.getElementById('cartTotal');

    try {
        const response = await fetch(`${API_BASE_URL}/customers/${currentUser.id}/cart`);
        // If 404, cart might be empty/not created yet
        if (response.status === 404) {
            cartItemsDiv.innerHTML = '<p class="empty-cart">Your cart is empty</p>';
            cartTotalSpan.textContent = '0 EGP';
            return;
        }

        const cart = await response.json();

        if (!cart.products || cart.products.length === 0) {
            cartItemsDiv.innerHTML = '<p class="empty-cart">Your cart is empty</p>';
            cartTotalSpan.textContent = '0 EGP';
            return;
        }

        // Calculate counts for display (backend returns list of product objects)
        const productCounts = {};
        cart.products.forEach(p => {
            productCounts[p.id] = (productCounts[p.id] || 0) + 1;
        });

        // Dedup for list
        const uniqueProducts = [];
        const seen = new Set();
        cart.products.forEach(p => {
            if (!seen.has(p.id)) {
                uniqueProducts.push(p);
                seen.add(p.id);
            }
        });

        cartItemsDiv.innerHTML = '';
        uniqueProducts.forEach(p => {
            const count = productCounts[p.id];
            const div = document.createElement('div');
            div.className = 'cart-item';
            div.innerHTML = `
                <span>${p.name} (x${count})</span>
                <span>${p.price * count} EGP</span>
                <button onclick="removeFromCart('${p.id}')" class="btn-remove">&times;</button>
            `;
            cartItemsDiv.appendChild(div);
        });

        cartTotalSpan.textContent = `${cart.total_price} EGP`;

    } catch (error) {
        console.error('Cart error:', error);
    }
}

/**
 * removeFromCart(productId)
 * Calls POST /api/customers/{id}/cart/remove
 */
async function removeFromCart(productId) {
    try {
        const response = await fetch(`${API_BASE_URL}/customers/${currentUser.id}/cart/remove`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId })
        });

        if (!response.ok) throw new Error('Failed to remove item');

        showToast('Removed from cart', 'success');
        displayCart();

    } catch (error) {
        showToast(error.message, 'error');
    }
}

/* --- Checkout Functions --- */
function showCheckout() {
    document.getElementById('checkoutModal').classList.remove('hidden');
    // Copy cart to checkout summary
    const cartContent = document.getElementById('cartItems').innerHTML;
    const total = document.getElementById('cartTotal').textContent;

    document.getElementById('checkoutItems').innerHTML = cartContent;
    document.getElementById('checkoutTotal').textContent = total;

    // Remove delete buttons from summary
    document.querySelectorAll('#checkoutItems .btn-remove').forEach(el => el.remove());
}

function closeCheckout() {
    document.getElementById('checkoutModal').classList.add('hidden');
}

function togglePaymentForm() {
    const method = document.querySelector('input[name="paymentMethod"]:checked').value;
    const cardForm = document.getElementById('creditCardForm');
    if (method === 'card') cardForm.classList.remove('hidden');
    else cardForm.classList.add('hidden');
}

/**
 * processPayment()
 * Creates order via POST /api/orders
 */
async function processPayment() {
    const paymentMethod = document.querySelector('input[name="paymentMethod"]:checked').value;

    // We need product IDs to create order. Fetch cart first.
    try {
        const cartRes = await fetch(`${API_BASE_URL}/customers/${currentUser.id}/cart`);
        const cartData = await cartRes.json();

        if (!cartData.products || cartData.products.length === 0) return;

        const productIds = cartData.products.map(p => p.id);

        const response = await fetch(`${API_BASE_URL}/orders`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                customer_id: currentUser.id,
                product_ids: productIds,
                payment_method: paymentMethod
            })
        });

        if (!response.ok) throw new Error('Order creation failed');

        // Success
        closeCheckout();
        showPaymentSuccess();
        displayCart(); // Should be empty now if backend clears it, otherwise we might see issue
        displayCustomerOrders();

    } catch (error) {
        showToast(error.message, 'error');
    }
}

function showPaymentSuccess() {
    document.getElementById('paymentSuccessModal').classList.remove('hidden');
}

function closePaymentSuccess() {
    document.getElementById('paymentSuccessModal').classList.add('hidden');
}

/**
 * displayCustomerOrders()
 * Fetches GET /api/customers/{id}/orders
 */
async function displayCustomerOrders() {
    const container = document.getElementById('customerOrders');
    container.innerHTML = '<p>Loading orders...</p>';

    try {
        const response = await fetch(`${API_BASE_URL}/customers/${currentUser.id}/orders`);
        if (!response.ok) throw new Error('Failed to fetch orders');

        const orders = await response.json();

        if (orders.length === 0) {
            container.innerHTML = '<p class="no-orders">No orders yet</p>';
            return;
        }

        container.innerHTML = '';
        orders.forEach(order => {
            const div = document.createElement('div');
            div.className = 'order-card';
            div.innerHTML = `
                <div class="order-header">
                    <strong>Order #${order.id.substring(0, 8)}</strong>
                    <span class="status-badge status-${order.status}">${formatStatusName(order.status)}</span>
                </div>
                <div class="order-details">
                    <p>Total: ${order.total_price} EGP</p>
                    <p>Method: ${order.payment_method}</p>
                </div>
            `;
            container.appendChild(div);
        });

    } catch (error) {
        container.innerHTML = '<p class="error-text">Error loading orders</p>';
    }
}


/* ==================== SECTION 4: ADMIN FUNCTIONS ==================== */

/**
 * createAccount(event)
 * Admin creating generic accounts.
 */
async function createAccount(event) {
    event.preventDefault();

    const name = document.getElementById('newUserName').value;
    const email = document.getElementById('newUserEmail').value;
    const password = document.getElementById('newUserPassword').value;
    const role = document.getElementById('newUserRole').value;

    if (!role) { showToast('Please select a role', 'error'); return; }

    let endpoint = '';
    let body = { name, email, password };

    if (role === 'admin') {
        endpoint = '/admins';
        body.status = 'active';
    } else if (role === 'serviceOfferor') {
        endpoint = '/providers';
        body.service_type = 'General'; // Default
        body.area = 'Cairo'; // Default
    } else if (role === 'courier') {
        endpoint = '/couriers';
        body.vehicle = 'Scooter';
        body.area = 'Cairo';
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        if (!response.ok) throw new Error('Failed to create account');

        showToast(`Created new ${role} successfully!`, 'success');
        document.getElementById('createAccountForm').reset();
        displayUsersTable();

    } catch (error) {
        showToast(error.message, 'error');
    }
}

/**
 * displayUsersTable()
 * GET /api/users
 */
async function displayUsersTable() {
    const container = document.getElementById('usersTable');
    container.innerHTML = '<p>Loading users...</p>';

    try {
        const response = await fetch(`${API_BASE_URL}/users`);
        const users = await response.json();

        let html = `
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Role</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
        `;

        users.forEach(u => {
            html += `
                <tr>
                    <td>${u.name}</td>
                    <td>${u.email}</td>
                    <td><span class="role-tag role-${u.role}">${formatRoleName(u.role)}</span></td>
                    <td>
                        <button onclick="editUser('${u.id}')" class="btn-xs">Edit</button>
                    </td>
                </tr>
            `;
        });

        html += '</tbody></table>';
        container.innerHTML = html;

    } catch (error) {
        container.innerHTML = '<p class="error-text">Error loading users</p>';
    }
}

function editUser(userId) {
    showToast(`Edit feature for user ${userId.substring(0, 5)}... coming soon!`, 'info');
}

/* Product Management (Admin) */

/**
 * displayPendingProducts()
 * Fetch all products, filter by p.status === 'pending'
 */
async function displayPendingProducts() {
    const container = document.getElementById('pendingProductsList');

    try {
        const response = await fetch(`${API_BASE_URL}/products`);
        const products = await response.json();
        const pending = products.filter(p => p.status === 'pending');

        container.innerHTML = '';
        if (pending.length === 0) {
            container.innerHTML = '<p class="empty-list">No pending products.</p>';
            return;
        }

        pending.forEach(p => {
            const div = document.createElement('div');
            div.className = 'admin-list-item warning-bg';
            div.innerHTML = `
                <div>
                    <strong>${p.name}</strong> (${p.price} EGP) - ${p.category}
                    <br><small>Provider: ${p.provider_id}</small>
                </div>
                <div class="actions">
                    <button onclick="approveProduct('${p.id}')" class="btn-success btn-sm">Approve</button>
                    <button onclick="removeProduct('${p.id}')" class="btn-danger btn-sm">Reject</button>
                </div>
            `;
            container.appendChild(div);
        });

    } catch (error) {
        console.error(error);
    }
}

async function approveProduct(productId) {
    try {
        const response = await fetch(`${API_BASE_URL}/products/${productId}/approve`, {
            method: 'PUT'
        });
        if (!response.ok) throw new Error('Approval failed');

        showToast('Product approved', 'success');
        displayPendingProducts();
        displayAdminProducts();

    } catch (error) {
        showToast(error.message, 'error');
    }
}

/**
 * displayAdminProducts()
 * Show all approved products for management
 */
async function displayAdminProducts() {
    const container = document.getElementById('adminProductsList');

    try {
        const response = await fetch(`${API_BASE_URL}/products`);
        const products = await response.json();

        container.innerHTML = '';
        products.forEach(p => {
            const div = document.createElement('div');
            div.className = 'admin-list-item';
            div.innerHTML = `
                <div>
                    <strong>${p.name}</strong> (${p.price} EGP)
                    <span class="status-badge status-${p.status}">${p.status}</span>
                </div>
                <div class="actions">
                    <button onclick="selectProduct('${p.id}', '${p.name}', ${p.price}, '${p.category}')" class="btn-secondary btn-sm">Edit</button>
                    <button onclick="removeProduct('${p.id}')" class="btn-danger btn-sm">Delete</button>
                </div>
            `;
            container.appendChild(div);
        });

    } catch (error) {
        console.error(error);
    }
}

async function addProduct(event) {
    event.preventDefault();
    const name = document.getElementById('productName').value;
    const price = parseFloat(document.getElementById('productPrice').value);
    const category = document.getElementById('productCategory').value;

    try {
        /* Note: Basic products need a provider ID. 
           In a real app, Admin might be a provider, or we assign a system provider.
           For now we'll fail if backend strictly requires provider_id unless we pass one.
           Let's assume backend handles it or we pass a placeholder if needed.
        */
        // We'll just try passing generic info. The backend model requires provider_id.
        // If we are admin, we don't have a provider_id? 
        // Workaround: We might need to find a provider first. 
        // For simplicity: We'll create a new product via POST /products 
        // BUT we need a provider_id. 
        // Let's assume there is a 'System' provider or similar.
        // We'll fetch providers and pick the first one as a fallback?

        // Fetch a provider first
        const provRes = await fetch(`${API_BASE_URL}/users`);
        const users = await provRes.json();
        const provider = users.find(u => u.role === 'serviceOfferor');

        if (!provider) throw new Error('No Service Provider available to assign product to.');

        const response = await fetch(`${API_BASE_URL}/products`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name, price, category,
                provider_id: provider.id,
                status: 'approved', // Admin adds as approved
                details: 'Admin added',
                weight: 1.0
            })
        });

        if (!response.ok) throw new Error('Failed to add product');

        showToast('Product added successfully', 'success');
        document.getElementById('productForm').reset();
        displayAdminProducts();

    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function removeProduct(productId) {
    if (!confirm('Delete this product?')) return;
    try {
        await fetch(`${API_BASE_URL}/products/${productId}`, { method: 'DELETE' });
        showToast('Product deleted', 'success');
        displayAdminProducts();
        displayPendingProducts();
        displayServiceProducts(); // if applicable
    } catch (error) {
        showToast('Failed to delete', 'error');
    }
}

// Select product for editing
function selectProduct(id, name, price, category) {
    selectedProductId = id;
    document.getElementById('productName').value = name;
    document.getElementById('productPrice').value = price;
    document.getElementById('productCategory').value = category;
    showToast('Product selected for editing. Click Update.', 'info');
}

async function updateProduct() {
    if (!selectedProductId) return;

    const name = document.getElementById('productName').value;
    const price = document.getElementById('productPrice').value;
    const category = document.getElementById('productCategory').value;

    try {
        const response = await fetch(`${API_BASE_URL}/products/${selectedProductId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, price: parseFloat(price), category })
        });

        if (!response.ok) throw new Error('Update failed');

        showToast('Product updated', 'success');
        document.getElementById('productForm').reset();
        selectedProductId = null;
        displayAdminProducts();

    } catch (error) {
        showToast(error.message, 'error');
    }
}


/* ==================== SECTION 5: SERVICE OFFEROR FUNCTIONS ==================== */

async function displayServiceProducts() {
    const container = document.getElementById('serviceProductsList');

    try {
        const response = await fetch(`${API_BASE_URL}/products`);
        const products = await response.json();
        // Filter by current user (provider)
        const myProducts = products.filter(p => p.provider_id === currentUser.id);

        container.innerHTML = '';
        if (myProducts.length === 0) {
            container.innerHTML = '<p class="empty-list">You have no products.</p>';
            return;
        }

        myProducts.forEach(p => {
            const div = document.createElement('div');
            div.className = 'admin-list-item';
            div.innerHTML = `
                <div>
                    <strong>${p.name}</strong>
                    <span class="status-badge status-${p.status}">${p.status}</span>
                </div>
                <div class="actions">
                     <button onclick="selectServiceProduct('${p.id}', '${p.name}', ${p.price}, '${p.category}')" class="btn-secondary btn-sm">Edit</button>
                    <button onclick="removeServiceProduct('${p.id}')" class="btn-danger btn-sm">Delete</button>
                </div>
            `;
            container.appendChild(div);
        });

    } catch (error) {
        console.error(error);
    }
}

async function addServiceProduct(event) {
    event.preventDefault();
    const name = document.getElementById('serviceProductName').value;
    const price = parseFloat(document.getElementById('serviceProductPrice').value);
    const category = document.getElementById('serviceProductCategory').value;

    try {
        const response = await fetch(`${API_BASE_URL}/products`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name, price, category,
                provider_id: currentUser.id,
                status: 'pending',
                details: 'Freshly made',
                weight: 0.5
            })
        });

        if (!response.ok) throw new Error('Failed to add product');

        showToast('Product added! Waiting for admin approval.', 'success');
        document.getElementById('serviceProductForm').reset();
        displayServiceProducts();

    } catch (error) {
        showToast(error.message, 'error');
    }
}

function selectServiceProduct(id, name, price, category) {
    selectedProductId = id;
    document.getElementById('serviceProductName').value = name;
    document.getElementById('serviceProductPrice').value = price;
    document.getElementById('serviceProductCategory').value = category;
}

async function updateServiceProduct() {
    if (!selectedProductId) return;
    const name = document.getElementById('serviceProductName').value;
    const price = document.getElementById('serviceProductPrice').value;
    const category = document.getElementById('serviceProductCategory').value;

    try {
        const response = await fetch(`${API_BASE_URL}/products/${selectedProductId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, price: parseFloat(price), category })
        });
        if (!response.ok) throw new Error('Update failed');

        showToast('Product updated', 'success');
        document.getElementById('serviceProductForm').reset();
        selectedProductId = null;
        displayServiceProducts();

    } catch (e) { showToast(e.message, 'error'); }
}

async function removeServiceProduct(id) {
    if (!confirm('Delete this product?')) return;
    try {
        await fetch(`${API_BASE_URL}/products/${id}`, { method: 'DELETE' });
        displayServiceProducts();
    } catch (e) { showToast('Error deleting', 'error'); }
}


/* ==================== SECTION 6: COURIER FUNCTIONS ==================== */

async function updateDeliveryArea() {
    const area = document.getElementById('deliveryArea').value;
    if (!area) return;

    try {
        const response = await fetch(`${API_BASE_URL}/couriers/${currentUser.id}/area`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ area })
        });
        if (!response.ok) throw new Error('Update failed');

        document.getElementById('currentArea').textContent = area;
        showToast('Delivery area updated', 'success');

    } catch (e) { showToast(e.message, 'error'); }
}

async function displayCourierOrders() {
    const container = document.getElementById('courierOrders');

    try {
        // Fetch all orders for now (Simplified)
        // In real app, we filter by area or assignment
        const response = await fetch(`${API_BASE_URL}/orders`);
        const orders = await response.json();
        /* Filter: show orders that are 'placed' or 'on-the-way'? 
           Let's show all pending orders 
        */
        const activeOrders = orders.filter(o => o.status !== 'delivered' && o.status !== 'cancelled');

        container.innerHTML = '';
        if (activeOrders.length === 0) {
            container.innerHTML = '<p class="no-orders">No active orders available.</p>';
            return;
        }

        activeOrders.forEach(o => {
            const div = document.createElement('div');
            div.className = 'order-card';
            div.innerHTML = `
                <div class="order-header">
                    <strong>Order #${o.id.substring(0, 8)}</strong>
                    <span class="status-badge status-${o.status}">${o.status}</span>
                </div>
                <div class="order-details">
                    <p>Total: ${o.total_price} EGP</p>
                    <p>Customer ID: ${o.customer_id.substring(0, 5)}...</p>
                </div>
                <div class="actions">
                    <button onclick="updateOrderStatus('${o.id}', 'on-the-way')" class="btn-xs btn-primary">Pickup</button>
                    <button onclick="updateOrderStatus('${o.id}', 'delivered')" class="btn-xs btn-success">Deliver</button>
                </div>
            `;
            container.appendChild(div);
        });

    } catch (e) { console.error(e); }
}

async function updateOrderStatus(orderId, status) {
    try {
        const response = await fetch(`${API_BASE_URL}/orders/${orderId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status })
        });
        if (!response.ok) throw new Error('Status update failed');

        showToast(`Order marked as ${status}`, 'success');
        displayCourierOrders();

    } catch (e) { showToast(e.message, 'error'); }
}


/* ==================== UTILITIES ==================== */

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const msgEl = document.getElementById('toastMessage');

    msgEl.textContent = message;
    toast.className = `toast visible ${type}`;

    setTimeout(() => {
        toast.className = 'toast hidden';
    }, 3000);
}

function getCategoryIcon(category) {
    const icons = {
        'Pizza': '🍕', 'Burgers': '🍔', 'Drinks': '🥤',
        'Desserts': '🍰', 'Other': '📦'
    };
    return icons[category] || '📦';
}

function formatRoleName(role) {
    const roles = {
        'customer': 'Customer',
        'admin': 'Admin',
        'serviceOfferor': 'Service Partner',
        'courier': 'Courier'
    };
    return roles[role] || role;
}

function formatStatusName(status) {
    return status.charAt(0).toUpperCase() + status.slice(1);
}

function scrollToUsers() {
    document.getElementById('usersListContainer').scrollIntoView({ behavior: 'smooth' });
}
