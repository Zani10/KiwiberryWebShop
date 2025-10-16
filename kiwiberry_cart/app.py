"""
Kiwiberry Cart - A minimal eCommerce web application in Flask
Features: user authentication, admin functionality, product management, and session-based cart
"""

import json
import os
import threading
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort

# Import configuration
from config import config


# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY

# Configure session to not be permanent (expires when browser closes)
app.config['SESSION_PERMANENT'] = False

# File lock for thread-safe JSON operations
file_lock = threading.Lock()


def safe_read_json(file_path):
    """
    Safely read JSON file with error handling.
    Returns empty list/dict if file doesn't exist or is corrupted.
    """
    try:
        if not os.path.exists(file_path):
            return [] if file_path.endswith('products.json') or file_path.endswith('users.json') else {}

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # If file is corrupted, recreate with empty data
        if file_path.endswith('products.json'):
            return []
        elif file_path.endswith('users.json'):
            return []
        else:
            return {}


def safe_write_json(file_path, data):
    """
    Safely write data to JSON file with file locking for thread safety.
    """
    with file_lock:
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error writing to {file_path}: {e}")
            raise


def get_products():
    """Get all products from JSON file."""
    return safe_read_json(config.PRODUCTS_FILE)


def save_products(products):
    """Save products list to JSON file."""
    safe_write_json(config.PRODUCTS_FILE, products)


def get_users():
    """Get all users from JSON file."""
    return safe_read_json(config.USERS_FILE)


def save_users(users):
    """Save users list to JSON file."""
    safe_write_json(config.USERS_FILE, users)


def get_next_product_id():
    """Get the next available product ID."""
    products = get_products()
    if not products:
        return 1
    return max(product['id'] for product in products) + 1


def find_user_by_email(email):
    """Find a user by email address."""
    users = get_users()
    return next((user for user in users if user['email'].lower() == email.lower()), None)


def is_admin():
    """Check if current session user is an admin."""
    return session.get('role') == 'admin'


def login_required(f):
    """Decorator to require user login for protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin access for protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id') or not is_admin():
            flash('Admin access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    """Home page showing products with optional server-side search."""
    # Get search query from URL parameters
    query = request.args.get('q', '').strip()

    products = get_products()

    # Server-side filtering if query provided
    if query:
        query_lower = query.lower()
        products = [
            product for product in products
            if query_lower in product['name'].lower()
        ]

    return render_template('index.html', products=products)


@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    """Product detail page showing full product information."""
    products = get_products()
    product = next((p for p in products if p['id'] == product_id), None)

    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Handle add to cart from product detail page
        try:
            quantity = int(request.form.get('quantity', 1))
            if quantity < 1 or quantity > 99:
                raise ValueError('Invalid quantity')
        except (ValueError, TypeError):
            quantity = 1

        # Initialize cart if it doesn't exist
        if 'cart' not in session:
            session['cart'] = {}

        # Update cart quantity
        cart = session['cart']
        cart[str(product_id)] = cart.get(str(product_id), 0) + quantity

        flash(f'Added {quantity} x {product["name"]} to cart!', 'success')
        return redirect(url_for('product_detail', product_id=product_id))

    return render_template('product_detail.html', product=product)


@app.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    """Add a product to the session cart."""
    products = get_products()
    product = next((p for p in products if p['id'] == product_id), None)

    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('index'))

    try:
        quantity = int(request.form.get('quantity', 1))
        if quantity < 1 or quantity > 99:
            raise ValueError('Invalid quantity')
    except (ValueError, TypeError):
        quantity = 1

    # Initialize cart if it doesn't exist
    if 'cart' not in session:
        session['cart'] = {}

    # Update cart quantity
    cart = session['cart']
    cart[str(product_id)] = cart.get(str(product_id), 0) + quantity

    flash(f'Added {quantity} x {product["name"]} to cart!', 'success')
    return redirect(request.referrer or url_for('index'))


@app.route('/cart/decrement/<int:product_id>', methods=['POST'])
def decrement_cart(product_id):
    """Decrement quantity of a product in cart."""
    if 'cart' not in session:
        return redirect(url_for('cart'))

    cart = session['cart']
    product_key = str(product_id)

    if product_key in cart:
        cart[product_key] -= 1
        if cart[product_key] <= 0:
            del cart[product_key]
        # Mark session as modified to ensure changes are saved
        session.modified = True

    return redirect(url_for('cart'))


@app.route('/cart/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    """Remove a product completely from cart."""
    if 'cart' in session:
        cart = session['cart']
        product_key = str(product_id)
        if product_key in cart:
            del cart[product_key]
            # Mark session as modified to ensure changes are saved
            session.modified = True

    flash('Item removed from cart.', 'success')
    return redirect(url_for('cart'))


@app.route('/cart')
def cart():
    """Display shopping cart contents."""
    cart_items = []
    total = 0.0

    if 'cart' in session and session['cart']:
        products = get_products()
        # Create a lookup dict for faster product access
        products_by_id = {str(p['id']): p for p in products}

        for product_id, quantity in session['cart'].items():
            if product_id in products_by_id:
                product = products_by_id[product_id]
                cart_items.append({
                    'product': product,
                    'quantity': quantity
                })
                total += product['price'] * quantity

    return render_template('cart.html', cart_items=cart_items, total=total)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please provide both email and password.', 'error')
            return render_template('login.html')

        # Check if this is the predefined admin
        if email.lower() == config.ADMIN_EMAIL.lower() and password == config.ADMIN_PASSWORD:
            # Clear any existing session data
            session.clear()
            session['user_id'] = 'admin'
            session['email'] = email
            session['role'] = 'admin'
            flash('Welcome, Admin!', 'success')
            return redirect(url_for('index'))

        # Check regular users
        user = find_user_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            # Clear any existing session data
            session.clear()
            session['user_id'] = user['email']
            session['email'] = user['email']
            session['role'] = 'user'
            flash(f'Welcome back, {user["email"]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page."""
    errors = {}

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        if not email:
            errors['email'] = 'Email is required.'
        elif '@' not in email:
            errors['email'] = 'Please enter a valid email address.'
        elif find_user_by_email(email):
            errors['email'] = 'Email already registered.'

        if not password:
            errors['password'] = 'Password is required.'
        elif len(password) < 6:
            errors['password'] = 'Password must be at least 6 characters.'

        if not confirm_password:
            errors['confirm_password'] = 'Please confirm your password.'
        elif password != confirm_password:
            errors['confirm_password'] = 'Passwords do not match.'

        if not errors:
            # Create new user
            users = get_users()
            new_user = {
                'email': email,
                'password_hash': generate_password_hash(password, method='pbkdf2:sha256')
            }
            users.append(new_user)
            save_users(users)

            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html', errors=errors)


@app.route('/logout')
def logout():
    """User logout."""
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


@app.route('/admin/products/new', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    """Admin page for adding new products."""
    errors = {}

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price_str = request.form.get('price', '').strip()
        image_url = request.form.get('image_url', '').strip()
        cultivar = request.form.get('cultivar', '').strip()
        description = request.form.get('description', '').strip()

        # Validation
        if not name:
            errors['name'] = 'Product name is required.'
        elif len(name) < 2:
            errors['name'] = 'Product name must be at least 2 characters.'

        if not price_str:
            errors['price'] = 'Price is required.'
        else:
            try:
                price = float(price_str)
                if price <= 0:
                    errors['price'] = 'Price must be greater than 0.'
            except ValueError:
                errors['price'] = 'Please enter a valid price.'

        if not image_url:
            errors['image_url'] = 'Image URL is required.'
        elif not (image_url.startswith('http://') or image_url.startswith('https://')):
            errors['image_url'] = 'Please enter a valid URL starting with http:// or https://'

        if not errors:
            # Create new product
            products = get_products()
            new_product = {
                'id': get_next_product_id(),
                'name': name,
                'price': round(float(price), 2),
                'image_url': image_url,
                'cultivar': cultivar if cultivar else name,  # Default to name if no cultivar
                'description': description
            }
            products.append(new_product)
            save_products(products)

            flash(f'Product "{name}" added successfully!', 'success')
            return redirect(url_for('index'))

    return render_template('admin_add_product.html', errors=errors)


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500


if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs(config.DATA_DIR, exist_ok=True)

    # Seed initial data if files don't exist or are empty
    if not os.path.exists(config.PRODUCTS_FILE) or not get_products():
        print("Seeding initial product data...")
        save_products([
            {
                "id": 1,
                "name": "Scarlet September",
                "price": 4.99,
                "image_url": "https://images.unsplash.com/photo-1511690656952-34342bb7c2f2?q=80&w=1200",
                "cultivar": "Scarlet September",
                "description": "Red-blushed skin, sweet-tart flesh. Early season."
            },
            {
                "id": 2,
                "name": "Ananasnaya",
                "price": 3.99,
                "image_url": "https://images.unsplash.com/photo-1506806732259-39c2d0268443?q=80&w=1200",
                "cultivar": "Ananasnaya",
                "description": "Classic green mini-kiwi with aromatic, tropical notes."
            },
            {
                "id": 3,
                "name": "Ken's Red",
                "price": 5.49,
                "image_url": "https://images.unsplash.com/photo-1547514701-42782101795e?q=80&w=1200",
                "cultivar": "Ken's Red",
                "description": "Red skin, red-tinged flesh; rich, berry-like flavor."
            },
            {
                "id": 4,
                "name": "Geneva",
                "price": 4.49,
                "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?q=80&w=1200",
                "cultivar": "Geneva",
                "description": "Early ripening, balanced sweetness and acidity."
            },
            {
                "id": 5,
                "name": "Issai",
                "price": 3.79,
                "image_url": "https://images.unsplash.com/photo-1515541965486-c9137d79c6b5?q=80&w=1200",
                "cultivar": "Issai",
                "description": "Self-fertile, smooth green skin, mild sweetness."
            },
            {
                "id": 6,
                "name": "Fresh Jumbo",
                "price": 5.99,
                "image_url": "https://images.unsplash.com/photo-1526318472351-c75fcf070305?q=80&w=1200",
                "cultivar": "Fresh Jumbo",
                "description": "Larger sized berries, juicy texture, dessert-friendly."
            }
        ])

    if not os.path.exists(config.USERS_FILE) or not get_users():
        print("Users file initialized (empty)")
        save_users([])

    print("Starting Kiwiberry Cart application...")
    print(f"Admin login: {config.ADMIN_EMAIL} / {config.ADMIN_PASSWORD}")
    app.run(debug=True)
