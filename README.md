# ⚡ Electrician Chatbot Booking System

A complete **FREE** human-like chatbot system for electrician receptionist booking, built with Flask, Ollama (free LLM), and SQLite.

## 🌟 Features

- **Human-like conversations** using free local LLM (Mistral/LLaMA/Phi-3)
- **Smart booking extraction** from natural conversation
- **Beautiful chat interface** with quick action buttons
- **Admin dashboard** to view and manage bookings
- **SQLite database** for persistent storage
- **100% FREE** - no API costs, no subscriptions
- **Runs locally** - complete privacy and control

## 🚀 Quick Start

### Step 1: Install Ollama (Free LLM)

**Windows:**
```bash
# Download and install from https://ollama.com
# Or use PowerShell:
winget install Ollama.Ollama
```

**macOS:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 2: Download a Free Model

```bash
# Choose one of these free models:
ollama pull mistral        # Recommended: Good balance of speed & quality
# OR
ollama pull llama3        # Alternative: Very capable
# OR  
ollama pull phi3          # Lightweight: Fast but smaller
```

### Step 3: Start Ollama Service

```bash
ollama serve
```
Keep this running in a separate terminal.

### Step 4: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run the Application

```bash
python app.py
```

### Step 6: Open Your Chatbot

Visit: `http://localhost:5000`

## 📱 How It Works

### For Customers:
1. **Visit the chat interface** - Clean, modern design
2. **Start chatting naturally** - "I need to fix my broken outlet"
3. **Provide details** - Name, phone, address, preferred time
4. **Get confirmation** - AI confirms booking details

### For Electricians:
1. **View bookings dashboard** - `http://localhost:5000/bookings`
2. **See all appointments** - Customer details, job types, status
3. **Update status** - Mark as confirmed, completed, etc.
4. **Export data** - All bookings stored in SQLite database

## 🎯 Smart Features

### Natural Language Processing
- Extracts customer name, phone, job type, date/time from conversation
- Handles various ways of expressing the same information
- Works with incomplete information

### Job Type Recognition
- **Repairs**: "fix", "broken", "not working", "issue"
- **Installations**: "install", "new", "add", "put in"
- **Emergencies**: "emergency", "urgent", "asap"
- **Inspections**: "inspect", "check", "safety"
- **Outlets/Switches**: "outlet", "socket", "plug"
- **Lighting**: "light", "lamp", "fixture", "bulb"
- **Panel Work**: "panel", "breaker", "electrical panel"

### Conversation Examples

**Customer:** "Hi, I need someone to fix my broken light switch"

**Sarah (AI):** "Hello! I'd be happy to help you with that light switch repair. My name is Sarah, and I'm here to schedule your electrical service. Could I get your name and phone number so I can set up the appointment?"

**Customer:** "I'm John Smith, my number is 555-123-4567"

**Sarah (AI):** "Thank you, John! I have you down for a light switch repair. When would be a good time for our electrician to come by? Do you have a preferred date and time?"

## 🛠️ Customization

### Modify the AI Personality
Edit the `system_prompt` in `app.py`:

```python
system_prompt = """You are a professional and friendly receptionist for an electrician service company. Your name is Sarah.

Your role:
- Greet customers warmly and professionally
- Ask for their name, phone number, and job details
- Inquire about preferred date and time for the appointment
- Ask for their address if not provided
- Confirm booking details clearly
- Be helpful, patient, and understanding
- Use a warm, professional tone
"""
```

### Add New Job Types
Edit the `job_keywords` dictionary in `app.py`:

```python
job_keywords = {
    'repair': ['repair', 'fix', 'broken', 'not working', 'issue', 'problem'],
    'installation': ['install', 'new', 'add', 'put in'],
    'emergency': ['emergency', 'urgent', 'asap', 'immediately'],
    'inspection': ['inspect', 'check', 'safety', 'inspection'],
    'outlet': ['outlet', 'socket', 'plug'],
    'lighting': ['light', 'lamp', 'fixture', 'bulb'],
    'panel': ['panel', 'breaker', 'electrical panel'],
    'your_new_type': ['keyword1', 'keyword2', 'keyword3']  # Add here
}
```

### Change Company Information
Update the header in `templates/index.html`:

```html
<h1>⚡ Your Company Name</h1>
<p>Hi! I'm Sarah, your electrician booking assistant...</p>
```

## 📊 Database Schema

The SQLite database (`bookings.db`) contains:

```sql
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    job_type TEXT NOT NULL,
    preferred_date TEXT NOT NULL,
    preferred_time TEXT NOT NULL,
    address TEXT,
    description TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 Troubleshooting

### Ollama Not Working
```bash
# Check if Ollama is running
ollama list

# Restart Ollama service
ollama serve

# Test with a simple prompt
ollama run mistral "Hello, how are you?"
```

### Port Already in Use
```bash
# Change port in app.py
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

### Model Not Found
```bash
# List available models
ollama list

# Pull the model again
ollama pull mistral
```

## 🌐 Deployment Options

### Local Network Access
```bash
# Run with host 0.0.0.0 to access from other devices
python app.py
# Then access via: http://YOUR_IP:5000
```

### Free Cloud Deployment
- **Heroku** (free tier)
- **Railway** (free tier)
- **Render** (free tier)
- **PythonAnywhere** (free tier)

### VPS Deployment
- **DigitalOcean** ($5/month)
- **Linode** ($5/month)
- **Vultr** ($2.50/month)

## 📈 Performance Tips

1. **Use Phi-3 for faster responses** (smaller model)
2. **Use Mistral for better quality** (balanced)
3. **Use LLaMA 3 for best quality** (larger model)
4. **Run on SSD** for better database performance
5. **Close unused applications** to free up RAM

## 🔒 Security Notes

- All data stays on your local machine
- No external API calls (except Ollama)
- SQLite database is local
- No personal data sent to third parties

## 📞 Support

If you need help:
1. Check the troubleshooting section above
2. Ensure Ollama is running properly
3. Verify all dependencies are installed
4. Check the console for error messages

## 🎉 Success!

You now have a complete, free, human-like chatbot for your electrician business! 

- **Customer Interface**: `http://localhost:5000`
- **Admin Dashboard**: `http://localhost:5000/bookings`
- **Database**: `bookings.db` (SQLite file)

The system will automatically extract booking information from natural conversations and store them in the database for you to manage.