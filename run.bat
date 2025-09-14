@echo off
echo ⚡ Starting Electrician Chatbot
echo ===============================

echo.
echo Starting Ollama service...
start "Ollama Service" cmd /k "ollama serve"

echo.
echo Waiting for Ollama to start...
timeout /t 5 /nobreak >nul

echo.
echo Starting chatbot application...
echo.
echo 🌐 Customer Interface: http://localhost:5000
echo 📊 Admin Dashboard: http://localhost:5000/bookings
echo.
echo Press Ctrl+C to stop the application
echo.

python app.py

pause