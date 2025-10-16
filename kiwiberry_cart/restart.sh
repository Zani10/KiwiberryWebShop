#!/bin/bash
# Restart script for Kiwiberry Cart application

echo "🔄 Restarting Kiwiberry Cart..."

# Kill any existing Flask processes
lsof -ti:5000 | xargs kill -9 2>/dev/null
echo "✓ Killed any existing processes on port 5000"

# Navigate to project directory
cd "$(dirname "$0")"

# Activate virtual environment
source .venv/bin/activate
echo "✓ Virtual environment activated"

# Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
echo "✓ Cleared Python cache"

# Start the application
echo ""
echo "🚀 Starting Kiwiberry Cart application..."
echo "📍 Access the application at:"
echo "   - http://127.0.0.1:5000/"
echo "   - http://localhost:5000/"
echo ""
echo "🔐 Admin credentials:"
echo "   Email: admin@kiwiberry.co"
echo "   Password: admin123"
echo ""
echo "Press Ctrl+C to stop the server"
echo "-----------------------------------"

python app.py

