# ⚡ Quick Start Guide - Electrician Chatbot

## 🚀 **Get Running in 5 Minutes**

### **Step 1: Install Software**
1. **Python**: Download from https://python.org (check "Add to PATH")
2. **Ollama**: Download from https://ollama.com

### **Step 2: Download Chatbot**
1. Download all files to a folder
2. Open Command Prompt in that folder

### **Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 4: Download AI Model**
```bash
ollama pull mistral
```

### **Step 5: Start Chatbot**
**Windows**: Double-click `setup.bat`
**Mac/Linux**: Run `./setup.sh`

### **Step 6: Open in Browser**
Go to: **http://localhost:5000**

---

## 🎯 **That's It!**

Your intelligent electrician chatbot is now running!

- **Customer Chat**: http://localhost:5000
- **Admin Dashboard**: http://localhost:5000/bookings

## 🔧 **If Something Goes Wrong**

### **"Python not found"**
- Reinstall Python with "Add to PATH" checked

### **"Ollama not found"**
- Reinstall Ollama and restart Command Prompt

### **"Port 5000 in use"**
- Close other applications or change port in app.py

### **Chatbot shows errors**
- Make sure Ollama is running: `ollama serve`
- Make sure model is downloaded: `ollama list`

## 📱 **Access from Phone**
Use your computer's IP address instead of localhost:
- Find IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
- Use: `http://YOUR_IP:5000`

## 🆘 **Emergency Setup**
If you need it working immediately:
1. Install Python and Ollama
2. Run: `ollama serve` (in one terminal)
3. Run: `python app.py` (in another terminal)
4. Go to: http://localhost:5000

**Need more help? Check the full INSTALLATION_GUIDE.md**
