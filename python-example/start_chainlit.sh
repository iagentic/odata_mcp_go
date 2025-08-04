#!/bin/bash

# Chainlit Startup Script for OData MCP
# This script helps you start the Chainlit web applications

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "chainlit_app.py" ]; then
    print_error "chainlit_app.py not found!"
    print_status "Please run this script from the python-example directory"
    exit 1
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    print_warning "OPENAI_API_KEY environment variable not set"
    print_status "You can set it with: export OPENAI_API_KEY='your-key-here'"
    print_status "Or provide it in the Chainlit settings panel"
fi

# Check if MCP server is running
print_status "Checking MCP server connection..."
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    print_success "MCP server is running"
else
    print_warning "MCP server not found at http://localhost:8080"
    print_status "Please start the MCP server first:"
    echo "  ./odata-mcp --transport http https://services.odata.org/V2/Northwind/Northwind.svc/"
    echo ""
    read -p "Press Enter to continue anyway, or Ctrl+C to exit..."
fi

# Check Python dependencies
print_status "Checking Python dependencies..."
if ! python3 -c "import chainlit" 2>/dev/null; then
    print_error "Chainlit not found!"
    print_status "Installing dependencies..."
    pip install -r requirements.txt
fi

# Function to show usage
show_usage() {
    echo "Chainlit OData MCP Startup Script"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  basic     - Start basic Chainlit app"
    echo "  advanced  - Start advanced Chainlit app with data visualization"
    echo "  enhanced  - Start enhanced app (may have HTML rendering issues)"
    echo "  simple    - Start simple app (text-based, reliable) - RECOMMENDED"
    echo "  elements  - Start elements app (uses Chainlit elements)"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Start simple app (recommended)"
    echo "  $0 simple       # Start simple app"
    echo "  $0 basic        # Start basic app"
    echo "  $0 advanced     # Start advanced app"
    echo "  $0 elements     # Start elements app"
    echo ""
    echo "The app will be available at http://localhost:8000"
}

# Main script
case "${1:-simple}" in
    basic)
        print_status "Starting basic Chainlit app..."
        print_status "App will be available at http://localhost:8000"
        print_status "Press Ctrl+C to stop"
        echo ""
        chainlit run chainlit_app.py
        ;;
    advanced)
        print_status "Starting advanced Chainlit app with data visualization..."
        print_status "App will be available at http://localhost:8000"
        print_status "Press Ctrl+C to stop"
        echo ""
        chainlit run chainlit_advanced_app.py
        ;;
    enhanced)
        print_status "Starting enhanced Chainlit app (may have HTML rendering issues)..."
        print_status "App will be available at http://localhost:8000"
        print_status "Press Ctrl+C to stop"
        echo ""
        chainlit run chainlit_enhanced_app.py
        ;;
    simple)
        print_status "Starting simple Chainlit app (text-based, reliable)..."
        print_status "App will be available at http://localhost:8000"
        print_status "Press Ctrl+C to stop"
        echo ""
        chainlit run chainlit_simple_app.py
        ;;
    elements)
        print_status "Starting elements Chainlit app (uses Chainlit elements)..."
        print_status "App will be available at http://localhost:8000"
        print_status "Press Ctrl+C to stop"
        echo ""
        chainlit run chainlit_elements_app.py
        ;;
    help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown option: $1"
        show_usage
        exit 1
        ;;
esac 