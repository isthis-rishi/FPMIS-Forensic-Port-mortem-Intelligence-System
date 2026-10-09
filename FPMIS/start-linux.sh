#!/bin/bash

echo "============================================"
echo "   FPMIS - Quick Start Script (Linux/Mac)"
echo "============================================"
echo ""

# Check if running from project root
if [ ! -d "backend" ]; then
    echo "ERROR: Please run this script from the FPMIS_Complete_Project directory"
    exit 1
fi

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}[1/4] Setting up Backend...${NC}"
cd backend

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt -q

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Edit backend/.env with your database credentials!${NC}"
    echo ""
fi

echo ""
echo -e "${GREEN}[2/4] Starting Backend Server...${NC}"
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

cd ..

echo ""
echo -e "${GREEN}[3/4] Setting up Frontend...${NC}"
cd frontend

# Install node modules if not exists
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

# Create .env.local if not exists
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local file..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
fi

echo ""
echo -e "${GREEN}[4/4] Starting Frontend Server...${NC}"
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "============================================"
echo "   FPMIS Started Successfully!"
echo "============================================"
echo ""
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "   Press Ctrl+C to stop all servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
