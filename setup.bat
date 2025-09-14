@echo off
echo ⚡ Setting up Electrician Chatbot Booking System
echo ================================================

echo.
echo Step 1: Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Step 2: Checking if Ollama is installed...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Ollama not found! Please install it from https://ollama.com
    echo After installation, run this script again.
    pause
    exit /b 1
)

echo.
echo Step 3: Downloading Mistral model (this may take a few minutes)...
ollama pull mistral

echo.
echo Step 4: Starting Ollama service...
start "Ollama Service" cmd /k "ollama serve"

echo.
echo Step 5: Waiting for Ollama to start...
timeout /t 5 /nobreak >nul

echo.
echo Step 6: Starting the chatbot application...
echo.
echo ✅ Setup complete! Your chatbot is starting...
echo.
echo 🌐 Customer Interface: http://localhost:5000
echo 📊 Admin Dashboard: http://localhost:5000/bookings
echo.
echo Press Ctrl+C to stop the application
echo.

python app.py

pause
