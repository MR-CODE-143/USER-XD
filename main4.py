import os
import json
import hashlib
import uuid
from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify, flash
import requests
from functools import wraps

app = Flask(__name__)
app.secret_key = '14304072025920|ANH4FT4N1SH4L0V32Y34R'

# --- Configuration ---
# !!! ATTENTION !!!
# REPLACE THE VALUES BELOW WITH YOUR ACTUAL TELEGRAM BOT TOKEN AND CHAT ID.
ADMIN_USERNAME = "hadianhaf.official.bd@gmail.com"
ADMIN_PASSWORD = "akash.com1$admin" # Change this!
TELEGRAM_BOT_TOKEN = "7967931288:AAG-ofv2_LKcB6w891SpzDBo991pMC03CW8"  # <-- IMPORTANT: Add your Bot Token here
TELEGRAM_CHAT_ID = "7233221453"    # <-- IMPORTANT: Add your Chat ID here


# --- File-based Database Setup ---
if not os.path.exists('data'):
    os.makedirs('data')

USERS_FILE = 'data/users.json'
ORDERS_FILE = 'data/orders.json'

def init_json_file(filepath, default_content):
    if not os.path.exists(filepath):
        with open(filepath, 'w') as f:
            json.dump(default_content, f, indent=4)

init_json_file(USERS_FILE, {})
init_json_file(ORDERS_FILE, [])

# --- Data Helper Functions ---
def read_data(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def write_data(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

# --- Password Hashing ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- Telegram Bot Integration (UPDATED TO SEND DOCUMENT) ---

def send_telegram_message(message):
    """Sends a TEXT message to the admin via Telegram."""
    if TELEGRAM_BOT_TOKEN.startswith("YOUR_") or TELEGRAM_CHAT_ID.startswith("YOUR_"):
        print("!!! FATAL: TELEGRAM BOT NOT CONFIGURED. Skipping notification.")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}
    try:
        print("Attempting to send TEXT notification to Telegram...")
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("Successfully sent TEXT notification.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"---! ERROR: Failed to send Telegram TEXT message: {e}")
        return False

def send_telegram_document_with_caption(caption, document_file):
    """Sends a DOCUMENT with a caption. Falls back to a text message if it fails."""
    if TELEGRAM_BOT_TOKEN.startswith("YOUR_") or TELEGRAM_CHAT_ID.startswith("YOUR_"):
        print("!!! FATAL: TELEGRAM BOT NOT CONFIGURED. Skipping notification.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    files = {'document': (document_file.filename, document_file.stream, document_file.mimetype)}
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption, 'parse_mode': 'Markdown'}

    try:
        print("Attempting to send DOCUMENT notification to Telegram...")
        response = requests.post(url, data=payload, files=files, timeout=30) # Increased timeout for uploads
        response.raise_for_status()
        print("Successfully sent DOCUMENT notification.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"---! ERROR: Failed to send Telegram DOCUMENT: {e}")
        print("---! FALLING BACK to text-only notification.")
        error_message = caption + "\n\n*⚠️ ADMIN ALERT: User's file could not be sent. Please check server logs.*"
        send_telegram_message(error_message)
        return False

# --- Product Data ---
PRODUCTS = {
    "fb-auto-create": {
        "id": "fb-auto-create",
        "name": "Facebook Auto Create Tool",
        "price": "15.00",
        "description": "Automate the creation of Facebook accounts with our powerful tool. Ideal for marketers and developers needing accounts in bulk."},
    "random-clone": {
        "id": "random-clone",
        "name": "Random Clone Tool",
        "price": "10.00",
        "description": "Clone random Facebook accounts for research and analysis. This tool gathers public data efficiently. *Use responsibly.*" },
    "file-clone": {
        "id": "file-clone",
        "name": "File Clone Tool",
        "price": "12.00",
        "description": "Provide a list of user IDs in a file and our tool will attempt to clone the public information from each profile." },
    "file-random-cloner": {
        "id": "file-random-cloner",
        "name": "File + Random Cloner Tool",
        "price": "20.00",
        "description": "The ultimate package. Combines the functionality of both File Clone and Random Clone tools for maximum flexibility." },
    "script-update": {
        "id": "script-update",
        "name": "Script Update",
        "price": "5.00",
        "description": "Get the latest updates for your purchased scripts. Includes new features, bug fixes, and performance improvements." }
}

# --- Decorators for Authentication ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please login to continue.", "login_error")
            return redirect(url_for('index', show_login=True))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin'): # More robust check
            flash("You must be an admin to access this page.", "login_error")
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Frontend Templates (NEW DARK THEME) ---
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>codeX Store</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
        .glass-card {
            background: rgba(41, 51, 78, 0.5); /* Semi-transparent background */
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: background 0.3s ease, border 0.3s ease, transform 0.3s ease;
        }
        .glass-card:hover {
            background: rgba(41, 51, 78, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transform: translateY(-5px);
        }
        .animated-button {
            background-image: linear-gradient(to right, #3b82f6, #14b8a6);
            transition: all 0.3s ease;
            background-size: 200% auto;
        }
        .animated-button:hover {
            background-position: right center; /* change the direction of the change here */
            transform: scale(1.05);
        }
        .modal-backdrop {
            background-color: rgba(10, 10, 20, 0.7);
            backdrop-filter: blur(5px);
        }
        .dark-input {
            background-color: #1f2937; /* gray-800 */
            border: 1px solid #4b5563; /* gray-600 */
            color: #d1d5db; /* gray-300 */
        }
        .dark-input:focus {
            outline: none;
            border-color: #3b82f6; /* blue-500 */
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.4);
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        .fade-in-card { animation: fadeIn 0.5s ease-out forwards; }
    </style>
</head>
<body class="antialiased bg-slate-900 text-gray-300">
    <div id="app-container" class="min-h-screen">
        <header class="bg-slate-900/70 backdrop-blur-md sticky top-0 z-30 shadow-lg shadow-slate-900/50">
            <nav class="container mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex items-center justify-between h-16">
                    <div class="flex-shrink-0">
                        <a href="/" class="text-2xl font-bold">
                            <span class="text-white">code</span><span class="text-cyan-400">X</span>
                        </a>
                    </div>
                    <div class="flex items-center">
                        {% if 'user_id' in session %}
                            <a href="{{ url_for('profile') }}" class="text-gray-300 hover:text-cyan-400">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-6-3a2 2 0 11-4 0 2 2 0 014 0zm-2 4a5 5 0 00-4.546 2.916A5.986 5.986 0 0010 16a5.986 5.986 0 004.546-2.084A5 5 0 0012 11z" clip-rule="evenodd" /></svg>
                            </a>
                        {% else %}
                            <button id="login-icon" class="text-gray-300 hover:text-cyan-400">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" /></svg>
                            </button>
                        {% endif %}
                    </div>
                </div>
            </nav>
        </header>
        <main class="container mx-auto px-4 sm:px-6 lg:px-8 py-8">{{ content | safe }}</main>
        <footer class="text-center py-4 text-gray-500 text-sm">&copy; 2024 codeX. All rights reserved.</footer>
    </div>
    {% if 'user_id' not in session %}
    <div id="auth-modal" class="modal-backdrop fixed inset-0 z-40 flex items-center justify-center {% if not show_login %}hidden{% endif %}">
        <div class="modal-content glass-card w-full max-w-md m-4 p-8 rounded-2xl">
            <div class="flex justify-end"><button id="close-modal" class="text-gray-400 hover:text-white">&times;</button></div>
            <div id="login-form">
                <h2 class="text-2xl font-bold text-center mb-6 text-white">Welcome Back</h2>
                {% with messages = get_flashed_messages(category_filter=["login_error"]) %}{% if messages %}<div class="bg-red-500/20 border border-red-500 text-red-300 px-4 py-3 rounded-lg relative mb-4" role="alert"><span class="block sm:inline">{{ messages[0] }}</span></div>{% endif %}{% endwith %}
                <form action="{{ url_for('login') }}" method="POST"><div class="space-y-4"><input type="email" name="email" placeholder="Gmail Address" class="dark-input w-full p-3 rounded-lg" required><input type="password" name="password" placeholder="Password" class="dark-input w-full p-3 rounded-lg" required><button type="submit" class="animated-button text-white font-bold w-full p-3 rounded-lg">Login</button></div></form>
                <p class="text-center mt-4 text-sm text-gray-400">Don't have an account? <a href="#" id="show-register" class="text-cyan-400 hover:underline">Register here</a></p>
            </div>
            <div id="register-form" class="hidden">
                <h2 class="text-2xl font-bold text-center mb-6 text-white">Create Account</h2>
                {% with messages = get_flashed_messages(category_filter=["register_error"]) %}{% if messages %}<div class="bg-red-500/20 border border-red-500 text-red-300 px-4 py-3 rounded-lg relative mb-4" role="alert"><span class="block sm:inline">{{ messages[0] }}</span></div>{% endif %}{% endwith %}
                <form action="{{ url_for('register') }}" method="POST"><div class="space-y-4"><input type="text" name="username" placeholder="Username" class="dark-input w-full p-3 rounded-lg" required><input type="email" name="email" placeholder="Gmail Address" class="dark-input w-full p-3 rounded-lg" required><input type="password" name="password" placeholder="Password" class="dark-input w-full p-3 rounded-lg" required><input type="tel" name="phone" placeholder="Phone Number" class="dark-input w-full p-3 rounded-lg" required><input type="text" name="telegram" placeholder="Telegram Username (e.g., @username)" class="dark-input w-full p-3 rounded-lg" required><button type="submit" class="animated-button text-white font-bold w-full p-3 rounded-lg">Register</button></div></form>
                <p class="text-center mt-4 text-sm text-gray-400">Already have an account? <a href="#" id="show-login" class="text-cyan-400 hover:underline">Login here</a></p>
            </div>
        </div>
    </div>
    {% endif %}
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const authModal = document.getElementById('auth-modal');
            const loginIcon = document.getElementById('login-icon');
            const closeModalBtn = document.getElementById('close-modal');
            const showRegisterLink = document.getElementById('show-register');
            const showLoginLink = document.getElementById('show-login');
            const loginForm = document.getElementById('login-form');
            const registerForm = document.getElementById('register-form');
            function openModal() { if (authModal) authModal.classList.remove('hidden'); }
            function closeModal() { if (authModal) authModal.classList.add('hidden'); }
            if (loginIcon) loginIcon.addEventListener('click', openModal);
            if (closeModalBtn) closeModalBtn.addEventListener('click', closeModal);
            if (authModal) authModal.addEventListener('click', function(event) { if (event.target === authModal) closeModal(); });
            if (showRegisterLink && showLoginLink) {
                showRegisterLink.addEventListener('click', (e) => { e.preventDefault(); loginForm.classList.add('hidden'); registerForm.classList.remove('hidden'); });
                showLoginLink.addEventListener('click', (e) => { e.preventDefault(); registerForm.classList.add('hidden'); loginForm.classList.remove('hidden'); });
            }
            if (new URLSearchParams(window.location.search).get('show_login')) { openModal(); }
        });
    </script>
</body>
</html>
"""
HOME_PAGE_CONTENT = """
<h1 class="text-3xl font-bold text-white mb-8">Our Products</h1>
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
    {% for product in products.values() %}
    <div class="glass-card p-6 flex flex-col rounded-2xl fade-in-card">
        <h2 class="text-xl font-bold text-white mb-2">{{ product.name }}</h2>
        <p class="text-gray-400 flex-grow mb-4">{{ product.description }}</p>
        <div class="flex items-center justify-between mt-auto">
            <span class="text-2xl font-bold text-white">${{ product.price }}</span>
            <a href="{{ url_for('buy_product', product_id=product.id) }}" class="animated-button text-white font-semibold px-6 py-2 rounded-lg">
                Add to Cart
            </a>
        </div>
    </div>
    {% endfor %}
</div>
"""
PROFILE_PAGE_CONTENT = """
<h1 class="text-3xl font-bold text-white mb-8">My Profile</h1>
<div class="glass-card p-8 mb-8 rounded-2xl">
    <h2 class="text-2xl font-semibold text-white mb-4">Account Details</h2>
    <div class="space-y-3 text-gray-300">
        <p><strong>Username:</strong> {{ user.username }}</p><p><strong>Email:</strong> {{ user.email }}</p><p><strong>Phone:</strong> {{ user.phone }}</p><p><strong>Telegram:</strong> {{ user.telegram }}</p>
    </div>
    <a href="{{ url_for('logout') }}" class="animated-button bg-red-600 hover:bg-red-700 text-white font-bold mt-6 px-6 py-3 rounded-lg inline-block">Logout</a>
</div>
<div class="glass-card p-8 rounded-2xl">
    <h2 class="text-2xl font-semibold text-white mb-6">My Orders</h2>
    <div class="space-y-6">
        {% if orders %}
            {% for order in orders %}
            <div class="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                <div class="flex flex-wrap justify-between items-start">
                    <div>
                        <p class="font-bold text-lg text-white">{{ order.product_name }}</p>
                        <p class="text-sm text-gray-400">Order ID: {{ order.order_id }}</p>
                        <p class="text-sm text-gray-400">Date: {{ order.date }}</p>
                    </div>
                    <div class="mt-2 sm:mt-0 text-right">
                        <span class="font-semibold text-lg text-white">${{ order.amount }}</span>
                        <span class="ml-2 px-3 py-1 text-sm font-semibold rounded-full 
                        {% if order.status == 'Payment Accepted' %} bg-green-500/20 text-green-300 
                        {% elif order.status == 'Pending' %} bg-yellow-500/20 text-yellow-300 
                        {% else %} bg-red-500/20 text-red-300 {% endif %}">{{ order.status }}</span>
                    </div>
                </div>
            </div>
            {% endfor %}
        {% else %}
            <p class="text-gray-500">You have no orders yet.</p>
        {% endif %}
    </div>
</div>
"""
BUY_PAGE_CONTENT = """
<h1 class="text-3xl font-bold text-white mb-2">Complete Your Purchase</h1>
<p class="text-lg text-gray-400 mb-8">You are buying: <span class="font-bold text-cyan-400">{{ product.name }}</span></p>
<div class="glass-card p-8 max-w-2xl mx-auto rounded-2xl">
    <form action="{{ url_for('submit_payment', product_id=product.id) }}" method="POST" enctype="multipart/form-data">
        <div class="space-y-6">
            <div>
                <label class="font-semibold text-gray-200">1. Select Payment Method</label>
                <div class="mt-2 flex space-x-4" id="payment-methods">
                    <button type="button" data-method="Bkash" data-info="Bkash Number: 01728195051" class="payment-btn flex-1 p-3 border border-slate-600 rounded-lg text-gray-300 hover:bg-slate-700 hover:border-cyan-400">Bkash</button>
                    <button type="button" data-method="Nagad" data-info="Nagad Number: 01721474011" class="payment-btn flex-1 p-3 border border-slate-600 rounded-lg text-gray-300 hover:bg-slate-700 hover:border-cyan-400">Nagad</button>
                    <button type="button" data-method="Binance" data-info="Binance Pay ID: 740407118" class="payment-btn flex-1 p-3 border border-slate-600 rounded-lg text-gray-300 hover:bg-slate-700 hover:border-cyan-400">Binance</button>
                </div>
                <input type="hidden" name="payment_method" id="payment_method_input" required>
            </div>
            <div id="payment-info" class="hidden p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg text-center"><p id="payment-details" class="font-semibold text-cyan-300"></p></div>
            <div>
                <label for="amount" class="font-semibold text-gray-200">2. Amount Paid</label>
                <p class="text-sm text-gray-500">Please pay exactly: <strong class="text-gray-300">${{ product.price }}</strong></p>
                <input type="text" id="amount" name="amount" value="${{ product.price }}" class="dark-input w-full p-3 rounded-lg mt-2" readonly>
            </div>
            <div>
                <label for="transaction_id" class="font-semibold text-gray-200">3. Transaction ID / Reference</label>
                <input type="text" id="transaction_id" name="transaction_id" placeholder="Enter the TrxID from your payment app" class="dark-input w-full p-3 rounded-lg mt-2" required>
            </div>
            <div>
                <label for="screenshot" class="font-semibold text-gray-200">4. Upload Payment Screenshot</label>
                <p class="text-sm text-gray-500">This helps us verify your payment faster.</p>
                <input type="file" id="screenshot" name="screenshot" class="dark-input w-full p-3 rounded-lg mt-2 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-violet-50 file:text-violet-700 hover:file:bg-violet-100" accept="image/*,application/pdf" required>
            </div>
            <button type="submit" class="animated-button text-white font-bold w-full p-3 rounded-lg !mt-8">Submit for Verification</button>
        </div>
    </form>
</div>
<script>
document.addEventListener('DOMContentLoaded', function() {
    const paymentMethodsContainer = document.getElementById('payment-methods');
    const paymentInfoBox = document.getElementById('payment-info');
    const paymentDetailsText = document.getElementById('payment-details');
    const paymentMethodInput = document.getElementById('payment_method_input');
    const paymentButtons = document.querySelectorAll('.payment-btn');
    const form = document.querySelector('form');
    paymentMethodsContainer.addEventListener('click', function(e) {
        if (e.target.closest('.payment-btn')) {
            const button = e.target.closest('.payment-btn');
            paymentDetailsText.textContent = button.dataset.info;
            paymentInfoBox.classList.remove('hidden');
            paymentMethodInput.value = button.dataset.method;
            paymentButtons.forEach(btn => { btn.classList.remove('bg-cyan-500', 'text-white', 'border-cyan-500'); btn.classList.add('border-slate-600'); });
            button.classList.add('bg-cyan-500', 'text-white', 'border-cyan-500');
            button.classList.remove('border-slate-600');
        }
    });
    form.addEventListener('submit', function(e) { if (!paymentMethodInput.value) { e.preventDefault(); alert('Please select a payment method.'); } });
});
</script>
"""
ADMIN_LOGIN_PAGE = """
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Admin Login</title><script src="https://cdn.tailwindcss.com"></script><style>body { font-family: 'Inter', sans-serif; }</style></head><body class="bg-slate-900 flex items-center justify-center h-screen"><div class="bg-slate-800 p-8 rounded-2xl shadow-lg w-full max-w-sm border border-slate-700"><h1 class="text-2xl font-bold text-center mb-6 text-white">Admin Login</h1>{% with messages = get_flashed_messages(category_filter=['login_error']) %}{% if messages %}<p class="bg-red-500/20 text-red-300 p-3 rounded-lg mb-4">{{ messages[0] }}</p>{% endif %}{% endwith %}<form method="post"><div class="space-y-4"><input type="text" name="username" placeholder="Username" class="w-full p-3 border rounded-lg bg-slate-700 border-slate-600 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500" required><input type="password" name="password" placeholder="Password" class="w-full p-3 border rounded-lg bg-slate-700 border-slate-600 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500" required><button type="submit" class="w-full bg-gradient-to-r from-blue-500 to-cyan-500 text-white p-3 rounded-lg font-semibold hover:from-blue-600 hover:to-cyan-600">Login</button></div></form></div></body></html>
"""
ADMIN_DASHBOARD_PAGE = """
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Admin Dashboard</title><script src="https://cdn.tailwindcss.com"></script><style>body { font-family: 'Inter', sans-serif; }</style></head><body class="bg-slate-900 text-gray-300"><div class="container mx-auto p-4 sm:p-6 lg:p-8"><div class="flex justify-between items-center mb-6"><h1 class="text-3xl font-bold text-white">Admin Dashboard</h1><a href="{{ url_for('admin_logout') }}" class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700">Logout</a></div><div class="bg-slate-800/50 rounded-xl shadow-lg border border-slate-700 overflow-hidden"><div class="p-6"><h2 class="text-xl font-bold text-white mb-4">Pending Orders</h2></div><div class="overflow-x-auto"><table class="w-full text-sm text-left text-gray-400"><thead class="text-xs text-gray-300 uppercase bg-slate-700/50"><tr><th scope="col" class="px-6 py-3">Order ID</th><th scope="col" class="px-6 py-3">User</th><th scope="col" class="px-6 py-3">Product</th><th scope="col" class="px-6 py-3">Payment Details</th><th scope="col" class="px-6 py-3">Status</th><th scope="col" class="px-6 py-3">Action</th></tr></thead><tbody>{% for order in orders %}{% if order.status == 'Pending' %}<tr class="border-b border-slate-700 hover:bg-slate-800"><td class="px-6 py-4 font-mono text-xs">{{ order.order_id }}</td><td class="px-6 py-4 text-white">{{ users.get(order.user_id, {}).get('username', 'N/A') }}<br><span class="text-gray-500">{{ users.get(order.user_id, {}).get('telegram', 'N/A') }}</span></td><td class="px-6 py-4 font-semibold text-white">{{ order.product_name }}</td><td class="px-6 py-4">{{ order.payment_method }} - ${{ order.amount }}<br><span class="font-mono text-xs">{{ order.transaction_id }}</span></td><td class="px-6 py-4"><span class="px-2 py-1 font-semibold leading-tight text-yellow-300 bg-yellow-500/20 rounded-full">{{ order.status }}</span></td><td class="px-6 py-4"><form action="{{ url_for('approve_order', order_id=order.order_id) }}" method="post"><button type="submit" class="bg-green-500 text-white px-3 py-1 rounded-md hover:bg-green-600">Approve</button></form></td></tr>{% endif %}{% endfor %}</tbody></table></div></div><div class="bg-slate-800/50 rounded-xl shadow-lg border border-slate-700 overflow-hidden mt-8"><div class="p-6"><h2 class="text-xl font-bold text-white mb-4">Completed Orders</h2></div><div class="overflow-x-auto"><table class="w-full text-sm text-left text-gray-400"><thead class="text-xs text-gray-300 uppercase bg-slate-700/50"><tr><th scope="col" class="px-6 py-3">Order ID</th><th scope="col" class="px-6 py-3">User</th><th scope="col" class="px-6 py-3">Product</th><th scope="col" class="px-6 py-3">Date</th><th scope="col" class="px-6 py-3">Status</th></tr></thead><tbody>{% for order in orders %}{% if order.status != 'Pending' %}<tr class="border-b border-slate-700 hover:bg-slate-800"><td class="px-6 py-4 font-mono text-xs">{{ order.order_id }}</td><td class="px-6 py-4 text-white">{{ users.get(order.user_id, {}).get('username', 'N/A') }}</td><td class="px-6 py-4 font-semibold text-white">{{ order.product_name }}</td><td class="px-6 py-4">{{ order.date }}</td><td class="px-6 py-4"><span class="px-2 py-1 font-semibold leading-tight text-green-300 bg-green-500/20 rounded-full">{{ order.status }}</span></td></tr>{% endif %}{% endfor %}</tbody></table></div></div></div></body></html>
"""

# --- Flask Routes ---

@app.route('/')
def index():
    show_login_flag = request.args.get('show_login', 'false').lower() == 'true'
    content = render_template_string(HOME_PAGE_CONTENT, products=PRODUCTS)
    return render_template_string(BASE_TEMPLATE, content=content, show_login=show_login_flag)

@app.route('/register', methods=['POST'])
def register():
    users = read_data(USERS_FILE)
    email = request.form['email']
    for user_data in users.values():
        if user_data['email'] == email:
            flash("This email is already registered.", 'register_error')
            return redirect(url_for('index', show_login=True))
    user_id = str(uuid.uuid4())
    new_user = { 'username': request.form['username'], 'email': email, 'password': hash_password(request.form['password']), 'phone': request.form['phone'], 'telegram': request.form['telegram'], }
    users[user_id] = new_user
    write_data(USERS_FILE, users)
    message = (f"👤 *New User Registration*\n\nUsername: `{new_user['username']}`\nEmail: `{new_user['email']}`\nTelegram: `{new_user['telegram']}`")
    send_telegram_message(message)
    session['user_id'] = user_id
    return redirect(url_for('profile'))

@app.route('/login', methods=['POST'])
def login():
    users = read_data(USERS_FILE)
    email = request.form['email']
    password = request.form['password']
    user_id = next((uid for uid, u in users.items() if u['email'] == email), None)
    if user_id and users[user_id]['password'] == hash_password(password):
        session['user_id'] = user_id
        session.pop('admin', None) # Ensure admin session is cleared
        return redirect(url_for('profile'))
    flash('Invalid email or password.', 'login_error')
    return redirect(url_for('index', show_login=True))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    users = read_data(USERS_FILE)
    all_orders = read_data(ORDERS_FILE)
    user_id = session['user_id']
    user_data = users.get(user_id)
    if not user_data: return redirect(url_for('logout'))
    user_orders = [order for order in all_orders if order.get('user_id') == user_id]
    user_orders.sort(key=lambda x: x.get('date', ''), reverse=True)
    content = render_template_string(PROFILE_PAGE_CONTENT, user=user_data, orders=user_orders)
    return render_template_string(BASE_TEMPLATE, content=content)

@app.route('/buy/<product_id>')
@login_required
def buy_product(product_id):
    product = PRODUCTS.get(product_id)
    if not product: return "Product not found", 404
    content = render_template_string(BUY_PAGE_CONTENT, product=product)
    return render_template_string(BASE_TEMPLATE, content=content)

@app.route('/pay/<product_id>', methods=['POST'])
@login_required
def submit_payment(product_id):
    product = PRODUCTS.get(product_id)
    if not product: return "Product not found", 404

    screenshot = request.files.get('screenshot')
    screenshot_info = f"File '{screenshot.filename}' provided." if screenshot and screenshot.filename else "No file provided."

    orders = read_data(ORDERS_FILE)
    users = read_data(USERS_FILE)
    user_id = session['user_id']
    user = users.get(user_id)

    new_order = {
        "order_id": f"codex-{uuid.uuid4().hex[:8]}", "user_id": user_id, "product_id": product_id, "product_name": product['name'], "amount": product['price'],
        "payment_method": request.form['payment_method'], "transaction_id": request.form['transaction_id'], "screenshot_info": screenshot_info, "status": "Pending",
        "date": __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    orders.append(new_order)
    write_data(ORDERS_FILE, orders)

    caption = (
        f"📦 *New Order Placed (Pending)*\n\n"
        f"**Order ID:** `{new_order['order_id']}`\n"
        f"**User:** `{user['username']}` ({user['telegram']})\n"
        f"**Product:** `{new_order['product_name']}`\n"
        f"**Amount:** `${new_order['amount']}`\n"
        f"**Method:** `{new_order['payment_method']}`\n"
        f"**TrxID:** `{new_order['transaction_id']}`\n\n"
        f"Please log in to the admin panel to approve."
    )

    if screenshot and screenshot.filename:
        send_telegram_document_with_caption(caption=caption, document_file=screenshot)
    else:
        message_with_no_screenshot = caption + "\n\n*Note: User did not upload a file.*"
        send_telegram_message(message_with_no_screenshot)

    return redirect(url_for('profile'))

# --- Admin Routes (FIXED) ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin'):
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple plain text comparison for admin credentials
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            session.pop('user_id', None) # Clear any user session
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid admin credentials.", "login_error")
            return redirect(url_for('admin_login'))
            
    return render_template_string(ADMIN_LOGIN_PAGE)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    orders = read_data(ORDERS_FILE)
    users = read_data(USERS_FILE)
    orders.sort(key=lambda x: x.get('date', ''), reverse=True)
    return render_template_string(ADMIN_DASHBOARD_PAGE, orders=orders, users=users)

@app.route('/admin/approve/<order_id>', methods=['POST'])
@admin_required
def approve_order(order_id):
    orders = read_data(ORDERS_FILE)
    users = read_data(USERS_FILE)
    for order in orders:
        if order['order_id'] == order_id:
            order['status'] = 'Payment Accepted'
            user = users.get(order['user_id'])
            message = (f"✅ *Payment Approved!*\n\nOrder ID: `{order['order_id']}`\nProduct: `{order['product_name']}`\nUser: `{user['username'] if user else 'N/A'}`")
            send_telegram_message(message)
            write_data(ORDERS_FILE, orders)
            break
    return redirect(url_for('admin_dashboard'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=False)
