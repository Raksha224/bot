# 🤖 Intelligent Electrician Chatbot

## ⚡ **What This Is**
A smart AI chatbot that acts as your electrician receptionist. It can:
- Have natural conversations with customers
- Handle emergency situations with direct call options
- Schedule appointments automatically
- Manage bookings through an admin dashboard
- Work 24/7 for your business

## 🎯 **Key Features**
- **Human-like conversations** - Customers think they're talking to a real person
- **Emergency handling** - Direct call button for urgent electrical issues
- **Smart booking** - Automatically captures customer details
- **Admin dashboard** - View and manage all appointments
- **100% FREE** - No monthly fees or API costs
- **Mobile friendly** - Works on phones, tablets, and computers

## 🚀 **Quick Start (5 Minutes)**

### **1. Install Required Software**
- **Python**: https://python.org/downloads (check "Add to PATH")
- **Ollama**: https://ollama.com/download

### **2. Download and Setup**
1. Download all files to a folder
2. Open Command Prompt in that folder
3. Run: `pip install -r requirements.txt`
4. Run: `ollama pull mistral`

### **3. Start the Chatbot**
**Windows**: Double-click `setup.bat`
**Mac/Linux**: Run `./setup.sh`

### **4. Access Your Chatbot**
- **Customer Interface**: http://localhost:5000
- **Admin Dashboard**: http://localhost:5000/bookings

## 📱 **How Customers Use It**

### **Normal Conversation**
Customer: "Hi, I need to fix my broken outlet"
Sarah: "Hi there! I'm sorry to hear you're having electrical issues! That can be really frustrating. I'd be happy to help you get that sorted out. Can you tell me more about what's happening?"

### **Emergency Situation**
Customer: "I have sparks coming from my outlet!"
Sarah: "I understand this is an electrical emergency! For your safety, please call our emergency line immediately at (555) 911-ELECTRIC. Our certified electricians are available 24/7 for urgent situations."

### **Booking Process**
1. Customer describes their electrical issue
2. Sarah asks for their name, phone, and preferred time
3. Sarah confirms the appointment details
4. Booking is automatically saved to your database

## 🎨 **Admin Dashboard Features**

### **View All Bookings**
- Customer name and contact information
- Job type and description
- Preferred date and time
- Booking status (pending, confirmed, completed)
- Created date and time

### **Manage Appointments**
- Update booking status
- Mark as confirmed or completed
- Cancel appointments
- View booking history

## 🔧 **Customization**

### **Change Company Information**
Edit `templates/index.html`:
```html
<h1>⚡ Your Company Name</h1>
<p>Hi! I'm Sarah, your friendly electrical assistant...</p>
```

### **Update Emergency Phone Number**
Edit `app.py`:
```python
"Please call our emergency line immediately at (555) 911-ELECTRIC"
```

### **Add New Services**
Edit the service keywords in `app.py` to recognize new electrical services.

## 🌐 **Sharing with Others**

### **For Team Members**
1. Share this README and installation files
2. Provide the admin dashboard URL
3. Update emergency phone numbers

### **For Customers**
1. Share the customer interface URL
2. For remote access, use your computer's IP address
3. Example: `http://192.168.1.100:5000`

## 📊 **What You Get**

### **Customer Experience**
- Natural, human-like conversations
- Quick action buttons for common requests
- Emergency call option for urgent situations
- Mobile-friendly interface
- 24/7 availability

### **Business Benefits**
- Never miss a customer inquiry
- Automatic appointment scheduling
- Professional customer service
- Reduced phone calls
- Better customer satisfaction

## 🔒 **Security & Privacy**

- **Local Only**: Runs on your computer, not in the cloud
- **Your Data**: All bookings stored locally in SQLite database
- **No External APIs**: Everything runs on your machine
- **Free Forever**: No monthly fees or subscriptions

## 🆘 **Emergency Features**

### **Emergency Button**
- Red pulsing button for urgent situations
- Direct call to emergency line
- Safety warnings and instructions
- Immediate electrician contact

### **Emergency Detection**
- Automatically detects emergency keywords
- Prioritizes urgent situations
- Provides safety instructions
- Routes to emergency electricians

## 📞 **Support**

### **If You Need Help**
1. Check the troubleshooting section in INSTALLATION_GUIDE.md
2. Verify all software is installed correctly
3. Make sure Ollama is running
4. Check error messages in Command Prompt

### **Common Issues**
- **"Python not found"**: Reinstall Python with "Add to PATH"
- **"Ollama not found"**: Reinstall Ollama
- **"Port in use"**: Close other applications or change port
- **Chatbot errors**: Make sure Ollama is running

## 🎉 **Success!**

Once running, you'll have:
- ✅ Professional AI receptionist
- ✅ 24/7 customer service
- ✅ Automatic appointment booking
- ✅ Emergency handling system
- ✅ Admin dashboard for management
- ✅ Mobile-friendly interface
- ✅ 100% free to run

**Your electrician business now has a smart AI assistant that works around the clock!**

---

## 📁 **File Structure**
```
electrician-chatbot/
├── app.py                 # Main chatbot application
├── requirements.txt       # Python dependencies
├── setup.bat             # Windows setup script
├── setup.sh              # Mac/Linux setup script
├── templates/
│   ├── index.html        # Customer chat interface
│   └── bookings.html     # Admin dashboard
├── README_FOR_SHARING.md # This file
├── INSTALLATION_GUIDE.md # Detailed setup instructions
└── QUICK_START.md       # Quick setup guide
```

**Ready to get started? Follow the Quick Start guide above!**
