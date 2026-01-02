#!/bin/bash

# Women Safety AI - Setup Script
# This script sets up both backend and frontend

echo "================================================"
echo "Women Safety AI - Project Setup"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Step 1: Backend Setup
echo "================================================"
echo "Step 1: Setting up Backend"
echo "================================================"
cd backend || exit

print_info "Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    print_success "Backend dependencies installed"
else
    print_error "Failed to install backend dependencies"
    exit 1
fi

echo ""
print_info "Testing backend..."
python -c "import fastapi, uvicorn, pandas, joblib; print('All imports successful')"

if [ $? -eq 0 ]; then
    print_success "Backend setup complete"
else
    print_error "Backend import test failed"
    exit 1
fi

cd ..

# Step 2: Frontend Setup
echo ""
echo "================================================"
echo "Step 2: Setting up Frontend"
echo "================================================"
cd frontend || exit

print_info "Installing Node.js dependencies..."
npm install

if [ $? -eq 0 ]; then
    print_success "Frontend dependencies installed"
else
    print_error "Failed to install frontend dependencies"
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    print_info "Creating .env file..."
    echo "VITE_API_URL=http://localhost:8000" > .env
    print_success ".env file created"
else
    print_success ".env file already exists"
fi

cd ..

# Summary
echo ""
echo "================================================"
echo "Setup Complete! 🎉"
echo "================================================"
echo ""
echo "To start the application:"
echo ""
echo "Terminal 1 - Backend:"
echo "  cd backend"
echo "  uvicorn app:app --reload"
echo ""
echo "Terminal 2 - Frontend:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then visit:"
echo "  Frontend: http://localhost:5173"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "================================================"
