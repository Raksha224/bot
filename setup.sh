#!/bin/bash

echo "⚡ Setting up Electrician Chatbot Booking System"
echo "================================================"

echo ""
echo "Step 1: Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "Step 2: Checking if Ollama is installed..."
if ! command -v ollama &> /dev/null; then
    echo "Ollama not found! Please install it from https://ollama.com"
    echo "After installation, run this script again."
    exit 1
fi

echo ""
echo "Step 3: Downloading Mistral model (this may take a few minutes)..."
ollama pull mistral

echo ""
echo "Step 4: Starting Ollama service in background..."
ollama serve &
OLLAMA_PID=$!

echo ""
echo "Step 5: Waiting for Ollama to start..."
sleep 5

echo ""
echo "Step 6: Starting the chatbot application..."
echo ""
echo "✅ Setup complete! Your chatbot is starting..."
echo ""
echo "🌐 Customer Interface: http://localhost:5000"
echo "📊 Admin Dashboard: http://localhost:5000/bookings"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping Ollama service..."
    kill $OLLAMA_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

python app.py
