#!/bin/bash

echo "⚡ Starting Electrician Receptionist Chatbot"
echo "=========================================="

echo ""
echo "Checking if Ollama is running..."
if ! ollama list >/dev/null 2>&1; then
    echo "❌ Ollama is not running!"
    echo "Please start Ollama first:"
    echo "  1. Run: ollama serve"
    echo "  2. Come back and run this script again"
    exit 1
fi

echo "✅ Ollama is running!"

echo ""
echo "Starting the chatbot application..."
python3 app.py
