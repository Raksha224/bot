from flask import Flask, render_template, request, jsonify
import sqlite3
import json
import re
import requests
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
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
        )
    ''')
    conn.commit()
    conn.close()

# Helper function to clean AI responses
def clean_response(response):
    """Clean up AI responses to make them more natural"""
    # Remove common AI prefixes
    prefixes_to_remove = [
        "I'm Sarah, and ", "As Sarah, ", "Sarah here, ", "This is Sarah, ",
        "I'm the receptionist, ", "As the receptionist, ", "I'm here to help, ",
        "I'd be happy to help, ", "I can help you with that, "
    ]
    
    for prefix in prefixes_to_remove:
        if response.startswith(prefix):
            response = response[len(prefix):]
            break
    
    # Remove any system-like responses
    if response.startswith(("I am an AI", "I'm an AI", "As an AI")):
        return "Hi there! Thanks for reaching out to PowerPro Electrical! How can I help you with your electrical needs today?"
    
    # Ensure response doesn't end abruptly
    if not response.endswith(('.', '!', '?')):
        response += "."
    
    return response.strip()

# Fallback responses for when AI doesn't respond properly
def get_fallback_response(message, conversation_history):
    """Provide natural fallback responses based on conversation context"""
    message_lower = message.lower()
    
    # Greeting responses
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
        return "Hi there! Thanks for reaching out to PowerPro Electrical! I'm Sarah, and I'm here to help you with all your electrical needs. What can I do for you today?"
    
    # Electrical problem responses
    if any(word in message_lower for word in ['broken', 'not working', 'problem', 'issue', 'fix', 'repair']):
        return "I'm sorry to hear you're having electrical issues! That can be really frustrating. I'd be happy to help you get that sorted out. Can you tell me a bit more about what's going on?"
    
    # Emergency responses
    if any(word in message_lower for word in ['emergency', 'urgent', 'asap', 'immediately', 'dangerous']):
        return "I understand this is urgent! We do offer emergency electrical services. Can you tell me what's happening and where you're located? I'll do my best to get someone out to you as quickly as possible."
    
    # Installation responses
    if any(word in message_lower for word in ['install', 'new', 'add', 'put in', 'wiring']):
        return "Great! I'd love to help you with that installation. New electrical work is exciting! Can you tell me what you're looking to have installed?"
    
    # General fallback
    return "I'd be happy to help you with that! Can you tell me a bit more about what electrical service you need? Whether it's a repair, installation, or something else, I'm here to make sure we get you taken care of."

# Advanced conversational AI system with intelligent state management
def get_ai_response(message, conversation_history):
    """Get AI response using intelligent conversation management"""
    
    # Try Ollama first
    try:
        ollama_response = get_ollama_response(message, conversation_history)
        if ollama_response and not ollama_response.startswith("I'm really sorry"):
            return ollama_response
    except:
        pass
    
    # Use advanced fallback system with intelligent conversation flow
    return get_intelligent_response(message, conversation_history)

def get_ollama_response(message, conversation_history):
    """Try to get response from Ollama"""
    try:
        # Format conversation history
        history_text = ""
        for msg in conversation_history[-6:]:
            role = "Customer" if msg['role'] == 'user' else "Sarah"
            history_text += f"{role}: {msg['content']}\n"
        
        # Enhanced system prompt with solid electrical knowledge
        system_prompt = """You are Sarah, an expert electrical service receptionist with 10+ years experience. You have deep knowledge of electrical systems, safety codes, and customer service.

ELECTRICAL EXPERTISE:
- Residential electrical systems (120V/240V)
- Commercial electrical installations
- Electrical safety and code compliance
- Common electrical problems and solutions
- Emergency electrical situations
- Smart home electrical integration
- Energy efficiency and electrical upgrades

CONVERSATION STYLE:
- Warm, professional, and knowledgeable
- Use electrical terminology appropriately
- Ask specific technical questions when needed
- Provide reassurance about safety
- Explain processes clearly
- Show genuine concern for customer safety

SERVICES WE PROVIDE:
- Emergency electrical repairs (24/7)
- Electrical troubleshooting and diagnostics
- Outlet and switch installation/repair
- Lighting installation and upgrades
- Electrical panel upgrades
- GFCI and AFCI installation
- Electrical inspections and safety audits
- Smart home electrical work
- Outdoor and landscape lighting
- Electrical code compliance work

EMERGENCY RESPONSES:
For electrical emergencies (sparks, burning smell, power outages, exposed wires):
"I understand this is an electrical emergency! For your safety, please call our emergency line immediately at (555) 911-ELECTRIC. Our certified electricians are available 24/7 for urgent situations. Do NOT attempt to fix electrical emergencies yourself."

CONVERSATION FLOW:
1. Warm greeting and assess the situation
2. Ask specific questions about the electrical issue
3. Determine if it's an emergency or regular service
4. Gather contact information and scheduling details
5. Provide safety advice if needed
6. Confirm appointment details
7. Offer additional services or advice

Remember: Safety first! Always prioritize customer safety and provide accurate electrical information."""

        full_prompt = f"""{system_prompt}

CONVERSATION HISTORY:
{history_text}

CURRENT CUSTOMER MESSAGE: {message}

RESPOND AS SARAH:"""
        
        response = requests.post('http://localhost:11434/api/generate', 
                               json={
                                   'model': 'mistral',
                                   'prompt': full_prompt,
                                   'stream': False,
                                   'options': {
                                       'temperature': 0.7,
                                       'top_p': 0.9,
                                       'max_tokens': 400
                                   }
                               },
                               timeout=15)
        
        if response.status_code == 200:
            return response.json()['response'].strip()
        else:
            return None
    
    except Exception as e:
        print(f"Ollama error: {e}")
        return None

def get_intelligent_response(message, conversation_history):
    """Advanced intelligent response system with conversation state management"""
    
    # Analyze conversation context
    context = analyze_conversation_context(message, conversation_history)
    
    # Generate intelligent response based on context
    return generate_contextual_response(message, context, conversation_history)

def analyze_conversation_context(message, conversation_history):
    """Analyze the conversation to understand context and intent"""
    message_lower = message.lower()
    
    context = {
        'customer_name': extract_customer_name(conversation_history),
        'conversation_stage': determine_conversation_stage(conversation_history),
        'intent': classify_intent(message_lower),
        'urgency_level': assess_urgency(message_lower),
        'service_type': identify_service_type(message_lower),
        'emotion': detect_emotion(message_lower),
        'previous_topics': extract_previous_topics(conversation_history),
        'missing_info': identify_missing_information(conversation_history)
    }
    
    return context

def determine_conversation_stage(conversation_history):
    """Determine what stage of the conversation we're in"""
    if len(conversation_history) <= 2:
        return 'greeting'
    elif any('name' in msg['content'].lower() for msg in conversation_history[-3:]):
        return 'information_gathering'
    elif any(word in ' '.join([msg['content'].lower() for msg in conversation_history[-3:]]) 
             for word in ['tomorrow', 'today', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']):
        return 'scheduling'
    elif any(word in ' '.join([msg['content'].lower() for msg in conversation_history[-3:]]) 
             for word in ['address', 'location', 'where']):
        return 'finalizing'
    else:
        return 'discussion'

def classify_intent(message_lower):
    """Classify the user's intent"""
    intents = {
        'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'],
        'emergency': ['emergency', 'urgent', 'spark', 'burning', 'smoke', 'fire', 'exposed wire', 'electrocution', 'shock', 'dangerous', 'asap', 'immediately'],
        'repair': ['broken', 'not working', 'fix', 'repair', 'outlet', 'switch', 'light', 'circuit', 'breaker', 'fuse', 'trip', 'flicker', 'problem', 'issue'],
        'installation': ['install', 'new', 'add', 'wiring', 'outlet', 'lighting', 'ceiling fan', 'chandelier', 'recessed', 'under cabinet', 'put in'],
        'inspection': ['inspect', 'inspection', 'check', 'safety', 'code', 'permit', 'upgrade', 'panel', 'electrical system'],
        'pricing': ['price', 'cost', 'how much', 'estimate', 'quote', 'charge', 'expensive', 'cheap'],
        'scheduling': ['tomorrow', 'today', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'morning', 'afternoon', 'evening', 'am', 'pm', 'when', 'schedule'],
        'contact_info': ['name is', 'my name', 'phone', 'number', 'call me', 'i am', 'address', 'location'],
        'thanks': ['thank', 'thanks', 'appreciate', 'helpful', 'great', 'wonderful'],
        'question': ['what', 'how', 'why', 'when', 'where', 'can you', 'do you', 'is it', 'are you'],
        'clarification': ['explain', 'tell me more', 'what do you mean', 'i don\'t understand']
    }
    
    for intent, keywords in intents.items():
        if any(keyword in message_lower for keyword in keywords):
            return intent
    return 'general'

def assess_urgency(message_lower):
    """Assess the urgency level of the request"""
    high_urgency = ['emergency', 'urgent', 'spark', 'burning', 'smoke', 'fire', 'exposed wire', 'electrocution', 'shock', 'dangerous', 'asap', 'immediately', 'right now']
    medium_urgency = ['soon', 'quickly', 'fast', 'today', 'tomorrow']
    
    if any(word in message_lower for word in high_urgency):
        return 'high'
    elif any(word in message_lower for word in medium_urgency):
        return 'medium'
    else:
        return 'low'

def identify_service_type(message_lower):
    """Identify the specific electrical service needed"""
    services = {
        'outlet_repair': ['outlet', 'socket', 'plug', 'receptacle'],
        'switch_repair': ['switch', 'dimmer', 'toggle'],
        'lighting': ['light', 'lamp', 'fixture', 'bulb', 'chandelier', 'ceiling fan'],
        'panel_work': ['panel', 'breaker', 'electrical panel', 'main panel', 'sub panel'],
        'wiring': ['wire', 'wiring', 'cable', 'conduit'],
        'gfci': ['gfci', 'ground fault', 'bathroom', 'kitchen', 'outdoor'],
        'afci': ['afci', 'arc fault', 'bedroom'],
        'smart_home': ['smart', 'automation', 'home automation', 'smart switch', 'smart outlet'],
        'outdoor': ['outdoor', 'exterior', 'landscape', 'patio', 'deck']
    }
    
    for service, keywords in services.items():
        if any(keyword in message_lower for keyword in keywords):
            return service
    return 'general'

def detect_emotion(message_lower):
    """Detect the emotional tone of the message"""
    emotions = {
        'frustrated': ['frustrated', 'annoying', 'driving me crazy', 'hate', 'terrible', 'awful'],
        'worried': ['worried', 'concerned', 'scared', 'nervous', 'afraid', 'unsafe'],
        'excited': ['excited', 'great', 'wonderful', 'amazing', 'love', 'perfect'],
        'confused': ['confused', 'don\'t understand', 'not sure', 'unclear', 'help'],
        'urgent': ['urgent', 'emergency', 'asap', 'immediately', 'right now']
    }
    
    for emotion, keywords in emotions.items():
        if any(keyword in message_lower for keyword in keywords):
            return emotion
    return 'neutral'

def extract_previous_topics(conversation_history):
    """Extract topics discussed in previous messages"""
    topics = []
    for msg in conversation_history[-5:]:  # Last 5 messages
        content = msg['content'].lower()
        if any(word in content for word in ['outlet', 'switch', 'light', 'panel', 'wiring']):
            topics.append('electrical_components')
        if any(word in content for word in ['repair', 'fix', 'broken']):
            topics.append('repairs')
        if any(word in content for word in ['install', 'new', 'add']):
            topics.append('installation')
    return topics

def identify_missing_information(conversation_history):
    """Identify what information is still needed"""
    full_conversation = ' '.join([msg['content'].lower() for msg in conversation_history])
    missing = []
    
    if not any(word in full_conversation for word in ['name is', 'my name', 'i am']):
        missing.append('name')
    if not any(word in full_conversation for word in ['phone', 'number', 'call']):
        missing.append('phone')
    if not any(word in full_conversation for word in ['address', 'location', 'where']):
        missing.append('address')
    if not any(word in full_conversation for word in ['tomorrow', 'today', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']):
        missing.append('scheduling')
    
    return missing

def generate_contextual_response(message, context, conversation_history):
    """Generate intelligent response based on context"""
    
    # Get personalized greeting
    greeting = get_personalized_greeting(context)
    
    # Handle emergency situations first
    if context['urgency_level'] == 'high' or context['intent'] == 'emergency':
        return generate_emergency_response(greeting, context)
    
    # Generate response based on conversation stage and intent
    if context['conversation_stage'] == 'greeting':
        return generate_greeting_response(greeting, context)
    elif context['conversation_stage'] == 'information_gathering':
        return generate_information_gathering_response(greeting, context, message)
    elif context['conversation_stage'] == 'scheduling':
        return generate_scheduling_response(greeting, context, message)
    elif context['conversation_stage'] == 'finalizing':
        return generate_finalizing_response(greeting, context, message)
    else:
        return generate_discussion_response(greeting, context, message)

def get_personalized_greeting(context):
    """Generate personalized greeting based on context"""
    if context['customer_name']:
        return f"Hi {context['customer_name']}!"
    elif context['emotion'] == 'frustrated':
        return "I can hear the frustration in your message, and I'm here to help!"
    elif context['emotion'] == 'worried':
        return "I understand your concern, and I want to help you feel safe and secure."
    elif context['emotion'] == 'excited':
        return "I love your enthusiasm! Let's make this electrical project amazing!"
    else:
        return "Hi there!"

def generate_emergency_response(greeting, context):
    """Generate response for emergency situations"""
    return f"""{greeting} I understand this is an electrical emergency! For your safety, please call our emergency line immediately at (555) 911-ELECTRIC.

Our certified electricians are available 24/7 for urgent situations. Do NOT attempt to fix electrical emergencies yourself - this could be very dangerous.

Can you tell me what's happening so I can make sure we get the right emergency electrician to you quickly?"""

def generate_greeting_response(greeting, context):
    """Generate response for greeting stage"""
    return f"""{greeting} Thanks for reaching out to PowerPro Electrical! I'm Sarah, and I'm genuinely excited to help you with all your electrical needs.

Whether you're dealing with:
• Electrical repairs that are driving you crazy
• New installations you're excited about  
• Emergency situations that need immediate attention
• Safety inspections for peace of mind
• Smart home electrical upgrades
• Outdoor and landscape lighting

I'm here to make sure you get the right electrical service for your needs. What's going on with your electrical system today?"""

def generate_information_gathering_response(greeting, context, message):
    """Generate response for information gathering stage"""
    if context['intent'] == 'contact_info':
        return f"""{greeting} Perfect! I'm getting your information down. 

To complete your booking, I'll need to know:
- What electrical service do you need?
- When would be a good time for our electrician to visit?
- What's your address so we know where to go?

Once I have these details, I'll confirm your appointment and our electrician will contact you directly to discuss the work needed."""
    
    elif context['intent'] == 'repair':
        return f"""{greeting} I'm sorry to hear you're having electrical issues! That can be really frustrating and sometimes dangerous.

I'd be happy to help you get that sorted out. Can you tell me more about what's happening? For example:
- What exactly isn't working?
- When did the problem start?
- Are there any unusual sounds, smells, or sparks?
- Is it affecting multiple outlets or just one?

This information helps me understand the situation better and schedule the right electrician for your needs."""
    
    elif context['intent'] == 'installation':
        return f"""{greeting} Great! I'd love to help you with that installation. New electrical work is exciting and can really improve your home!

Can you tell me more about what you're looking to have installed? For example:
- What type of installation (outlets, lighting, ceiling fan, etc.)?
- Where in your home?
- Do you have any specific requirements or preferences?
- Is this part of a larger renovation project?

I'll make sure we schedule the right electrician who specializes in that type of work."""
    
    else:
        return f"""{greeting} I'd be happy to help you with that! 

To make sure I understand exactly what you need, could you tell me more about your electrical situation? Whether it's a repair, installation, inspection, or something else, I'm here to help you get the right electrical service.

What's going on with your electrical system today?"""

def generate_scheduling_response(greeting, context, message):
    """Generate response for scheduling stage"""
    return f"""{greeting} Great! I'd be happy to schedule that for you.

To make sure I get you the right appointment time, can you tell me:
- What electrical service do you need?
- Your preferred date and time?
- Your name and phone number?
- Your address?

Once I have all the details, I'll confirm your appointment and our electrician will call you to discuss the specific work needed."""

def generate_finalizing_response(greeting, context, message):
    """Generate response for finalizing stage"""
    return f"""{greeting} Perfect! I have all the information I need to schedule your appointment.

Let me confirm the details:
- Service: [Service type]
- Date/Time: [Scheduled time]
- Contact: [Customer info]
- Address: [Location]

Our electrician will call you directly to discuss the specific work needed and provide a detailed estimate. Is there anything else I can help you with today?"""

def generate_discussion_response(greeting, context, message):
    """Generate response for general discussion"""
    if context['intent'] == 'pricing':
        return f"""{greeting} Great question! We provide free, detailed estimates for all our electrical work. 

Our pricing is transparent and competitive, with no hidden fees. The electrician will give you a detailed quote when they visit, including:
- Labor costs
- Materials needed
- Timeline for completion
- Any permits required

We believe in fair, honest pricing, so you'll know exactly what you're paying for before any work begins. Would you like to schedule a free estimate visit?"""
    
    elif context['intent'] == 'thanks':
        return f"""{greeting} You're very welcome! I'm so glad I could help you with your electrical needs.

Is there anything else electrical-related I can help you with today? Whether it's questions about the upcoming service, additional electrical work, or just general electrical advice, I'm here to help!"""
    
    else:
        return f"""{greeting} I'd be happy to help you with that! 

To make sure I understand exactly what you need, could you tell me more about your electrical situation? Whether it's a repair, installation, inspection, or something else, I'm here to help you get the right electrical service.

What's going on with your electrical system today?"""

def extract_customer_name(conversation_history):
    """Extract customer name from conversation history"""
    for msg in conversation_history:
        content = msg['content'].lower()
        if 'name is' in content or 'my name' in content or 'i am' in content:
            # Simple name extraction
            words = content.split()
            for i, word in enumerate(words):
                if word in ['is', 'am'] and i + 1 < len(words):
                    return words[i + 1].title()
    return None

# Extract booking information from conversation
def extract_booking_info(message, conversation_history):
    booking_info = {}
    
    # Extract name (look for patterns like "I'm John", "My name is Sarah", etc.)
    name_patterns = [
        r"my name is (\w+)",
        r"i'm (\w+)",
        r"i am (\w+)",
        r"this is (\w+)",
        r"call me (\w+)"
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, message.lower())
        if match:
            booking_info['name'] = match.group(1).title()
            break
    
    # Extract phone number
    phone_pattern = r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})'
    phone_match = re.search(phone_pattern, message)
    if phone_match:
        booking_info['phone'] = phone_match.group(1)
    
    # Extract job type
    job_keywords = {
        'repair': ['repair', 'fix', 'broken', 'not working', 'issue', 'problem'],
        'installation': ['install', 'new', 'add', 'put in'],
        'emergency': ['emergency', 'urgent', 'asap', 'immediately'],
        'inspection': ['inspect', 'check', 'safety', 'inspection'],
        'outlet': ['outlet', 'socket', 'plug'],
        'lighting': ['light', 'lamp', 'fixture', 'bulb'],
        'panel': ['panel', 'breaker', 'electrical panel']
    }
    
    message_lower = message.lower()
    for job_type, keywords in job_keywords.items():
        if any(keyword in message_lower for keyword in keywords):
            booking_info['job_type'] = job_type
            break
    
    # Extract date
    date_patterns = [
        r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
        r'(today|tomorrow)',
        r'(\d{1,2}[/-]\d{1,2}[/-]?\d{0,4})',
        r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, message_lower)
        if match:
            booking_info['date'] = match.group(1)
            break
    
    # Extract time
    time_patterns = [
        r'(\d{1,2}:\d{2}\s*(am|pm)?)',
        r'(\d{1,2}\s*(am|pm))',
        r'(morning|afternoon|evening)'
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, message_lower)
        if match:
            booking_info['time'] = match.group(1)
            break
    
    # Extract address
    address_keywords = ['address', 'location', 'at', 'live', 'located']
    if any(keyword in message_lower for keyword in address_keywords):
        # Simple extraction - look for street numbers
        address_match = re.search(r'(\d+\s+[a-zA-Z\s]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|way|blvd|boulevard))', message)
        if address_match:
            booking_info['address'] = address_match.group(1)
    
    return booking_info

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
    data = request.get_json()
        user_message = data.get('message', '')
    conversation_history = data.get('history', [])
    
        # Add user message to history
        conversation_history.append({'role': 'user', 'content': user_message})
    
    # Extract booking information
        booking_info = extract_booking_info(user_message, conversation_history)
        
        # Get AI response using enhanced system
        ai_response = get_ai_response(user_message, conversation_history)
        
        # Add AI response to history
        conversation_history.append({'role': 'assistant', 'content': ai_response})
        
        # If we have enough booking info, save it
        if booking_info.get('name') and booking_info.get('phone') and booking_info.get('job_type'):
            save_booking(booking_info, conversation_history)
        
        return jsonify({
            'response': ai_response,
            'booking_info': booking_info,
            'history': conversation_history
        })
        
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({
            'response': "I'm sorry, I'm having trouble processing your request. Please try again.",
            'booking_info': {},
            'history': conversation_history
        })

def save_booking(booking_info, conversation_history):
            try:
                conn = sqlite3.connect('bookings.db')
                cursor = conn.cursor()
        
        # Get additional info from conversation
        description = ""
        for msg in conversation_history[-3:]:
            if msg['role'] == 'user':
                description += msg['content'] + " "
        
                cursor.execute('''
            INSERT INTO bookings (customer_name, phone_number, job_type, preferred_date, 
                                preferred_time, description, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            booking_info.get('name', ''),
            booking_info.get('phone', ''),
            booking_info.get('job_type', ''),
            booking_info.get('date', ''),
            booking_info.get('time', ''),
            description.strip(),
            'pending'
        ))
        
                conn.commit()
                conn.close()
        print(f"Booking saved: {booking_info}")
                
            except Exception as e:
        print(f"Error saving booking: {e}")

@app.route('/bookings')
def view_bookings():
    try:
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings ORDER BY created_at DESC')
    bookings = cursor.fetchall()
    conn.close()
    
    return render_template('bookings.html', bookings=bookings)
        
    except Exception as e:
        return f"Error retrieving bookings: {e}"

@app.route('/api/bookings')
def api_bookings():
    try:
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings ORDER BY created_at DESC')
    bookings = cursor.fetchall()
    conn.close()
    
    # Convert to list of dictionaries
    booking_list = []
    for booking in bookings:
        booking_list.append({
            'id': booking[0],
            'customer_name': booking[1],
                'phone_number': booking[2],
            'job_type': booking[3],
            'preferred_date': booking[4],
            'preferred_time': booking[5],
            'address': booking[6],
            'description': booking[7],
            'status': booking[8],
            'created_at': booking[9]
        })
    
    return jsonify(booking_list)
        
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    init_db()
    print("Starting Electrician Chatbot...")
    print("Make sure Ollama is running with: ollama serve")
    print("And pull a model with: ollama pull mistral")
    app.run(debug=True, host='0.0.0.0', port=5000)
