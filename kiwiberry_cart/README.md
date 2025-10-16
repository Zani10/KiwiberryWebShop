# Kiwiberry Cart 🥝

A minimal, clean eCommerce web application built with Python Flask and Bootstrap 5, themed around kiwiberries (mini-kiwis). Features session-based authentication, admin functionality, product management, and a session-based shopping cart.

## Features

- **User Authentication**: Session-based login/register with password hashing
- **Admin Panel**: Predefined admin can add new products via web interface
- **Product Management**: JSON-based storage with search functionality
- **Shopping Cart**: Session-based cart with quantity management
- **Search**: Both server-side and client-side filtering
- **Responsive Design**: Bootstrap 5 with custom kiwiberry-themed styling
- **Thread-Safe**: File locking for concurrent JSON operations

## Tech Stack

- **Backend**: Python 3.10+, Flask 3.0.3
- **Frontend**: Bootstrap 5, Bootstrap Icons, Custom CSS/JS
- **Storage**: JSON files (no database required)
- **Security**: Werkzeug password hashing, session management

## Project Structure

```
kiwiberry_cart/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── data/                # JSON data storage
│   ├── products.json    # Product catalog
│   └── users.json       # User accounts
├── templates/           # HTML templates
│   ├── base.html       # Base template with navigation
│   ├── index.html      # Home page with products
│   ├── login.html      # User login
│   ├── register.html   # User registration
│   ├── cart.html       # Shopping cart
│   └── admin_add_product.html  # Admin product form
├── static/             # Static assets
│   ├── css/
│   │   └── custom.css  # Custom styling
│   └── js/
│       └── search.js   # Client-side search
└── README.md          # This file
```

## Quick Start

### 1. Clone and Setup

```bash
# Navigate to project directory
cd kiwiberry_cart

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file (optional - defaults are provided)
nano .env
```

**Environment Variables:**
- `SECRET_KEY`: Flask secret key (change in production)
- `ADMIN_EMAIL`: Admin email (default: admin@kiwiberry.co)
- `ADMIN_PASSWORD`: Admin password (default: admin123)

### 3. Run the Application

```bash
# Start development server
python app.py

# Or use Flask CLI
flask --app app run --debug
```

The application will be available at `http://127.0.0.1:5000/`

## Default Admin Credentials

- **Email**: admin@kiwiberry.co
- **Password**: admin123

## Usage Guide

### For Users

1. **Browse Products**: Visit the home page to see all kiwiberry products
2. **Search**: Use the search bar to filter products by name
3. **Add to Cart**: Click "Add to Cart" on any product
4. **Manage Cart**: View, modify quantities, or remove items in your cart
5. **Register/Login**: Create an account or login to access features

### For Admins

1. **Login**: Use admin credentials above
2. **Add Products**: Click "Add Product" in the navigation bar
3. **Fill Form**: Provide product details (name, price, image URL required)
4. **Save**: New products are immediately available on the site

## Data Storage

- **Products**: Stored in `data/products.json` with incremental IDs
- **Users**: Stored in `data/users.json` with hashed passwords
- **Cart**: Session-based (lost on browser close)

### Sample Product Format

```json
{
  "id": 1,
  "name": "Scarlet September",
  "price": 4.99,
  "image_url": "https://example.com/image.jpg",
  "cultivar": "Scarlet September",
  "description": "Red-blushed skin, sweet-tart flesh. Early season."
}
```

### Sample User Format

```json
{
  "email": "user@example.com",
  "password_hash": "pbkdf2:sha256:600000$..."
}
```

## Features Explained

### Session-Based Cart
- Cart data stored in Flask session (server-side)
- No database required for cart persistence
- Cart lost when session expires (browser restart)

### JSON Storage with Thread Safety
- Simple file-based storage using JSON
- Threading locks prevent concurrent write issues
- Automatic recovery from corrupted files

### Search Functionality
- **Server-side**: URL parameter filtering (`?q=searchterm`)
- **Client-side**: Real-time JavaScript filtering while typing
- Case-insensitive search on product names and cultivars

### Admin Authentication
- Predefined admin credentials from environment variables
- Admin doesn't need to register as a regular user
- Special "admin" role in session for access control

## Customization

### Styling
- Custom CSS in `static/css/custom.css`
- Bootstrap 5 components with kiwiberry color scheme
- Responsive design for mobile/tablet

### Adding Features
- Routes in `app.py` follow RESTful patterns
- Templates extend `base.html` for consistent navigation
- Helper functions in `app.py` for data operations

## Security Notes

- Passwords hashed using Werkzeug security
- Session-based authentication (no cookies stored)
- Admin route protection with decorators
- Input validation for forms
- File locking for concurrent operations

## Development

### Code Organization
- **Routes**: All HTTP endpoints in `app.py`
- **Data Layer**: JSON file operations with error handling
- **Templates**: Jinja2 templates with Bootstrap components
- **Static Files**: Organized CSS and JavaScript

### Best Practices
- Clear function naming and comments
- Error handling for file operations
- Input validation and sanitization
- Responsive design principles

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install -r requirements.txt
   ```

2. **Port Already in Use**
   ```bash
   # Kill process on port 5000
   lsof -ti:5000 | xargs kill -9
   ```

3. **Environment Variables**
   ```bash
   # Ensure .env file exists and is readable
   ls -la .env
   ```

4. **Permission Errors**
   ```bash
   # Check data directory permissions
   chmod 755 data/
   ```

## Production Deployment

For production use:

1. Change `SECRET_KEY` in `.env`
2. Use a production WSGI server (Gunicorn)
3. Set `FLASK_ENV=production`
4. Use HTTPS in production
5. Consider using a proper database for larger scale

## Screenshots

*[Screenshots would be added here showing the main features]*

## Contributing

This is a demo application for learning Flask and eCommerce concepts. Feel free to:

- Fork and modify for your own projects
- Submit issues for bugs or improvements
- Use as a starting point for similar applications

## License

This project is for educational purposes. Feel free to use and modify as needed.

---

**Built with ❤️ using Flask + Bootstrap 5**
