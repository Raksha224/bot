# 🚀 Electrician Chatbot - Complete Installation Guide

## 📋 **What You'll Get**
- **Intelligent AI Chatbot** with human-like conversations
- **Emergency Call System** for urgent electrical issues
- **Admin Dashboard** to manage bookings
- **100% FREE** - no API costs, no subscriptions
- **Works on Windows, Mac, and Linux**

## 🎯 **Quick Start (5 Minutes)**

### **Step 1: Download Required Software**

#### **For Windows:**
1. **Download Python**: Go to https://python.org/downloads
   - Check "Add Python to PATH" during installation
   - Verify: Open Command Prompt, type `python --version`

2. **Download Ollama**: Go to https://ollama.com/download
   - Download and install Ollama
   - Verify: Open Command Prompt, type `ollama --version`


#### **For Mac:**
1. **Install Python**: `brew install python` or download from python.org
2. **Install Ollama**: `curl -fsSL https://ollama.com/install.sh | sh`

#### **For Linux:**
1. **Install Python**: `sudo apt install python3 python3-pip` (Ubuntu/Debian)
2. **Install Ollama**: `curl -fsSL https://ollama.com/install.sh | sh`

### **Step 2: Download the Chatbot Files**
1. **Download all files** to a folder (e.g., `electrician-chatbot`)
2. **Files needed:**
   - `app.py` (main chatbot)
   - `requirements.txt` (dependencies)
   - `templates/` folder (web interface)
   - `setup.bat` (Windows) or `setup.sh` (Mac/Linux)

### **Step 3: Install Dependencies**
Open Command Prompt/Terminal in the chatbot folder and run:

```bash
pip install -r requirements.txt
```

### **Step 4: Download AI Model**
```bash
ollama pull mistral
```
*This downloads the free AI model (takes 2-3 minutes)*

### **Step 5: Start the Chatbot**

#### **Option A: Automatic Setup (Windows)**
Double-click `setup.bat` - it will do everything automatically!

#### **Option B: Manual Setup**
1. **Start Ollama** (in one terminal):
   ```bash
   ollama serve
   ```

2. **Start Chatbot** (in another terminal):
   ```bash
   python app.py
   ```

### **Step 6: Access Your Chatbot**
Open your web browser and go to:
- **Customer Chat**: http://localhost:5000
- **Admin Dashboard**: http://localhost:5000/bookings

## 🎉 **You're Done!**

Your intelligent electrician chatbot is now running! Customers can chat naturally, and you can manage bookings through the admin dashboard.

---

## 📚 **Detailed Installation Steps**

### **System Requirements**
- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB free space
- **Internet**: Required for initial setup

### **Step-by-Step Installation**

#### **1. Install Python**
**Windows:**
1. Go to https://python.org/downloads
2. Download Python 3.8 or newer
3. Run installer
4. ✅ **IMPORTANT**: Check "Add Python to PATH"
5. Click "Install Now"

**Verify Installation:**
```bash
python --version
```
Should show: `Python 3.x.x`

**Mac:**
```bash
# Using Homebrew (recommended)
brew install python

# Or download from python.org
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# CentOS/RHEL
sudo yum install python3 python3-pip
```

#### **2. Install Ollama (AI Model Runner)**
**Windows:**
1. Go to https://ollama.com/download
2. Download Windows installer
3. Run installer
4. Restart Command Prompt

**Mac/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Verify Installation:**
```bash
ollama --version
```

#### **3. Download Chatbot Files**
Create a folder called `electrician-chatbot` and download these files:

**Required Files:**
- `app.py` (main chatbot application)
- `requirements.txt` (Python dependencies)
- `templates/index.html` (chat interface)
- `templates/bookings.html` (admin dashboard)
- `setup.bat` (Windows setup script)
- `setup.sh` (Mac/Linux setup script)

#### **4. Install Python Dependencies**
Open Command Prompt/Terminal in the chatbot folder:

```bash
pip install -r requirements.txt
```

**If you get permission errors:**
```bash
pip install --user -r requirements.txt
```

#### **5. Download AI Model**
```bash
ollama pull mistral
```

**Alternative models:**
```bash
ollama pull llama3    # Alternative model
ollama pull phi3      # Smaller, faster model
```

#### **6. Start the System**

**Method 1: Automatic (Recommended)**
- **Windows**: Double-click `setup.bat`
- **Mac/Linux**: Run `./setup.sh`

**Method 2: Manual**
1. **Terminal 1** (Start Ollama):
   ```bash
   ollama serve
   ```

2. **Terminal 2** (Start Chatbot):
   ```bash
   python app.py
   ```

#### **7. Access Your Chatbot**
Open web browser and go to:
- **Customer Interface**: http://localhost:5000
- **Admin Dashboard**: http://localhost:5000/bookings

---

## 🔧 **Troubleshooting**

### **Common Issues and Solutions**

#### **"Python not found" Error**
**Solution:**
1. Reinstall Python with "Add to PATH" checked
2. Or add Python to PATH manually:
   - Windows: Add `C:\Python39\` to System PATH
   - Mac/Linux: Add to `.bashrc` or `.zshrc`

#### **"Ollama not found" Error**
**Solution:**
1. Reinstall Ollama
2. Restart Command Prompt/Terminal
3. Try: `ollama --version`

#### **"Module not found" Error**
**Solution:**
```bash
pip install flask requests
```

#### **"Port 5000 already in use" Error**
**Solution:**
1. Close other applications using port 5000
2. Or change port in `app.py`:
   ```python
   app.run(debug=True, host='0.0.0.0', port=5001)
   ```

#### **"Ollama connection failed" Error**
**Solution:**
1. Make sure Ollama is running: `ollama serve`
2. Wait 30 seconds after starting Ollama
3. Check if model is downloaded: `ollama list`

#### **Chatbot shows error messages**
**Solution:**
1. Make sure Ollama is running
2. Make sure Mistral model is downloaded
3. Restart both Ollama and the chatbot

### **Performance Issues**

#### **Slow Responses**
**Solutions:**
1. Use smaller model: `ollama pull phi3`
2. Close other applications
3. Increase RAM if possible

#### **High Memory Usage**
**Solutions:**
1. Use `phi3` model instead of `mistral`
2. Close other applications
3. Restart the system

---

## 🌐 **Sharing with Others**

### **For Team Members**
1. **Share the installation guide** (this document)
2. **Share the chatbot files** (zip the entire folder)
3. **Provide your phone number** for emergency calls
4. **Update the phone number** in `app.py`:
   ```python
   # Change this line in app.py
   "Please call our emergency line immediately at (555) 911-ELECTRIC"
   ```

### **For Customers**
1. **Share the customer URL**: `http://YOUR_IP:5000`
2. **Find your IP address**:
   - Windows: `ipconfig`
   - Mac/Linux: `ifconfig`
3. **Make sure firewall allows port 5000**

### **For Remote Access**
1. **Use your public IP** instead of localhost
2. **Configure router** to forward port 5000
3. **Use cloud hosting** (Heroku, Railway, etc.)

---

## 📱 **Mobile Access**

### **Access from Phone/Tablet**
1. **Find your computer's IP address**
2. **Use**: `http://YOUR_IP:5000`
3. **Example**: `http://192.168.1.100:5000`

### **Make it Mobile-Friendly**
The chatbot is already mobile-responsive and works great on phones!

---

## 🔒 **Security Notes**

- **Local Only**: Chatbot runs on your local network
- **No External Data**: All data stays on your computer
- **Free Forever**: No API costs or subscriptions
- **Your Data**: All bookings stored in local SQLite database

---

## 📞 **Support**

### **If You Need Help**
1. **Check troubleshooting section** above
2. **Verify all steps** were followed correctly
3. **Check error messages** in Command Prompt/Terminal
4. **Restart everything** and try again

### **Common Commands**
```bash
# Check if Python works
python --version

# Check if Ollama works
ollama --version

# List downloaded models
ollama list

# Start Ollama
ollama serve

# Start chatbot
python app.py
```

---

## 🎉 **Success!**

Once everything is running, you'll have:
- ✅ **Intelligent AI chatbot** that talks like a human
- ✅ **Emergency call system** for urgent situations
- ✅ **Admin dashboard** to manage all bookings
- ✅ **Mobile-friendly interface** for customers
- ✅ **100% free** to run forever

**Your electrician business now has a professional AI assistant!**
