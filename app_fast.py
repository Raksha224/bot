"""
Fast, optimized version of the Electrician Chatbot with export features.
This version prioritizes speed while maintaining clean architecture principles.
"""
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import sqlite3
import json
import re
import requests
from datetime import datetime, timedelta
import os
import csv
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import threading
from functools import lru_cache
from typing import List

load_dotenv()
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": os.environ.get("CORS_ORIGINS", "*")}})
limiter = Limiter(get_remote_address, app=app, default_limits=[os.environ.get("RATE_LIMIT", "60 per minute")])

# Structured rotating file logs (production-friendly)
logs_dir = os.path.join(os.getcwd(), 'logs')
os.makedirs(logs_dir, exist_ok=True)
handler = RotatingFileHandler(os.path.join(logs_dir, 'app.log'), maxBytes=2_000_000, backupCount=5)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
app.logger.addHandler(handler)

# Performance optimizations
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['JSON_SORT_KEYS'] = False

# Response cache for common queries
@lru_cache(maxsize=100)
def get_cached_response(message_type, context_key=""):
    """Cache common responses for faster performance"""
    cached_responses = {
        "greeting": "Hi there! Thanks for reaching out to PowerPro Electrical! I'm Sarah, and I'm here to help you with all your electrical needs. What can I do for you today?",
        "emergency": "I understand this is an electrical emergency! For your safety, please call our emergency line immediately at (555) 911-ELECTRIC. Our certified electricians are available 24/7 for urgent situations.",
        "repair": "I'm sorry to hear you're having electrical issues! That can be really frustrating. I'd be happy to help you get that sorted out. Can you tell me a bit more about what's going on?",
        "installation": "Great! I'd love to help you with that installation. New electrical work is exciting! Can you tell me what you're looking to have installed?",
        "pricing": "Great question! We provide free, detailed estimates for all our electrical work. Our pricing is transparent and competitive, with no hidden fees. Would you like to schedule a free estimate visit?",
        "thanks": "You're very welcome! I'm so glad I could help you with your electrical needs. Is there anything else electrical-related I can help you with today?"
    }
    return cached_responses.get(message_type, "I'd be happy to help you with that! Can you tell me a bit more about what electrical service you need?")

# Database connection pool
class ConnectionPool:
    def __init__(self, db_path, max_connections=5):
        self.db_path = db_path
        self.max_connections = max_connections
        self.connections = []
        self.lock = threading.Lock()
        self._init_db()
    
    def _init_db(self):
        """Initialize database with optimized schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                job_type TEXT NOT NULL,
                preferred_date TEXT,
                preferred_time TEXT,
                address TEXT,
                description TEXT,
                urgency_level TEXT DEFAULT 'low',
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Create indexes for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON bookings(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON bookings(created_at)')
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get database connection from pool"""
        with self.lock:
            if self.connections:
                return self.connections.pop()
            else:
                return sqlite3.connect(self.db_path)
    
    def return_connection(self, conn):
        """Return connection to pool"""
        with self.lock:
            if len(self.connections) < self.max_connections:
                self.connections.append(conn)
            else:
                conn.close()

# Global connection pool
db_pool = ConnectionPool('bookings.db')

# Knowledge base: load small local snippets from kb/ (txt, csv header, pdf metadata only)
KB_DIR = os.path.join(os.getcwd(), 'kb')
os.makedirs(KB_DIR, exist_ok=True)

def _load_kb_snippets() -> List[str]:
    snippets: List[str] = []
    try:
        for name in os.listdir(KB_DIR):
            path = os.path.join(KB_DIR, name)
            if not os.path.isfile(path):
                continue
            if name.lower().endswith('.txt'):
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    snippets.append(f.read()[:4000])
            elif name.lower().endswith('.csv'):
                # Read header + first 3 rows only for speed
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    head = ''.join([next(f, '') for _ in range(4)])
                    snippets.append(head)
            elif name.lower().endswith('.pdf'):
                # Avoid heavy parsing; use filename as tag
                snippets.append(f"PDF: {name}")
    except Exception as e:
        app.logger.warning(f"KB load warning: {e}")
    return snippets

KB_SNIPPETS = _load_kb_snippets()

# Fast AI response system
def _services_overview() -> str:
    """Concise list of electrical services we provide."""
    return (
        "We handle electrical-only work: troubleshooting and repairs, outlet/switch install, lighting upgrades, "
        "panel/breaker work, GFCI/AFCI, smart home wiring, outdoor/landscape lighting, and safety inspections."
    )


def _precise_repair_followups() -> str:
    """Short targeted follow-up questions for repairs."""
    return (
        "Which circuit or device is affected (outlet, switch, light, breaker)? "
        "Do you notice tripping breakers, smells, sparks, or heat? When did it start?"
    )


def get_fast_ai_response(message, conversation_history):
    """Ultra-fast AI response with strict domain guard and precise templates"""
    message_lower = message.lower()

    # 1) STRICT DOMAIN CHECK FIRST
    non_electrical_keywords = [
        'car', 'automobile', 'vehicle', 'auto', 'mechanic', 'engine', 'tire', 'oil',
        'gas', 'fuel', 'brake', 'transmission', 'battery', 'car service', 'auto repair',
        'plumbing', 'plumber', 'pipe', 'water', 'drain', 'toilet', 'sink',
        'hvac', 'heating', 'cooling', 'air conditioning', 'furnace', 'ac',
        'roofing', 'roof', 'shingle', 'gutter', 'siding',
        'painting', 'paint', 'interior', 'exterior', 'wall',
        'cleaning', 'housekeeping', 'maid', 'janitorial',
        'landscaping', 'lawn', 'garden', 'tree', 'grass',
        'appliance', 'refrigerator', 'washer', 'dryer', 'dishwasher',
        'computer', 'laptop', 'phone', 'internet', 'wifi', 'software',
        'legal', 'lawyer', 'attorney', 'court', 'law',
        'medical', 'doctor', 'health', 'hospital', 'clinic',
        'insurance', 'finance', 'banking', 'loan', 'credit',
        'real estate', 'property', 'house', 'apartment', 'rental',
        'weather', 'food', 'travel', 'sports', 'music', 'movie', 'book', 'news'
    ]
    if any(word in message_lower for word in non_electrical_keywords):
        return (
            "I'm Sarah, your electrical service assistant at PowerPro Electrical. "
            "I specialize exclusively in electrical services. I can't help with AC/HVAC, car, plumbing, or other non-electrical work. "
            "How can I help with your electrical needs today?"
        )

    # 2) FAST INTENT TEMPLATES (concise and precise)
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
        return get_cached_response("greeting")

    if any(word in message_lower for word in ['emergency', 'urgent', 'spark', 'burning', 'smoke', 'fire']):
        return get_cached_response("emergency")

    # Services overview
    if any(phrase in message_lower for phrase in ['what services', 'services you', 'do you offer', 'do you handle', 'service list', 'which services']):
        return _services_overview()

    # Repair intent (electrical only)
    if any(word in message_lower for word in ['broken', 'not working', 'fix', 'repair', 'outlet', 'switch', 'short', 'sparking', 'tripping', 'breaker']):
        return (
            "We can help with electrical repairs like outlets, switches, lights, and breakers. "
            + _precise_repair_followups()
        )

    # Installation intent
    if any(word in message_lower for word in ['install', 'new', 'add', 'put in', 'wiring', 'replace fixture', 'ceiling fan (electric wiring)']):
        return (
            "We install and upgrade lighting, outlets/switches, dedicated circuits, and smart switches. "
            "What are you looking to install and where?"
        )

    if any(word in message_lower for word in ['price', 'cost', 'how much', 'estimate', 'quote']):
        return (
            "We provide free on-site estimates for electrical work. "
            "Share the issue or installation details and your zip/address to schedule."
        )

    if any(word in message_lower for word in ['thank', 'thanks', 'appreciate']):
        return get_cached_response("thanks")

    # 3) Fall back to local model (fast) else general cached
    try:
        return get_ollama_response_fast(message, conversation_history)
    except:
        return "Happy to help. Could you describe the electrical issue or installation you need?"

def get_ollama_response_fast(message, conversation_history):
    """Fast Ollama response with timeout"""
    try:
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        model_name = os.getenv('OLLAMA_MODEL', 'mistral')
        use_ollama = os.getenv('USE_OLLAMA', 'true').lower() == 'true'
        if not use_ollama:
            raise Exception('Ollama disabled via USE_OLLAMA=false')
        # Format conversation history (limit to last 3 messages for speed)
        history_text = ""
        for msg in conversation_history[-3:]:
            role = "Customer" if msg['role'] == 'user' else "Sarah"
            history_text += f"{role}: {msg['content']}\n"
        
        # STRICT system prompt with domain restrictions
        system_prompt = """You are Sarah, an expert electrical service receptionist at PowerPro Electrical. 

STRICT RULES:
- ONLY discuss electrical services (repairs, installations, inspections, emergency electrical work)
- If asked about ANY non-electrical topic (car, plumbing, HVAC, etc.), immediately redirect to electrical services
- NEVER provide advice outside electrical domain
- Be concise and helpful
- Never repeat the user's question

ELECTRICAL SERVICES ONLY:
- Electrical repairs and troubleshooting
- Outlet and switch installation/repair
- Lighting installation and upgrades
- Electrical panel work
- GFCI/AFCI installation
- Emergency electrical services
- Electrical inspections and safety audits
- Smart home electrical work
- Outdoor electrical installations

If the user asks about anything non-electrical, respond: "I'm Sarah, your electrical service assistant at PowerPro Electrical. I specialize exclusively in electrical services. I cannot help with car services, plumbing, HVAC, or other non-electrical services. How can I help you with your electrical needs today?" """
        
        kb_text = '\n'.join(KB_SNIPPETS[:5])
        full_prompt = f"""{system_prompt}

CONVERSATION HISTORY:
{history_text}

CURRENT MESSAGE: {message}

KNOWLEDGE HINTS (local snippets):
{kb_text}

RESPOND AS SARAH:"""
        
        response = requests.post(f'{base_url}/api/generate', 
                               json={
                                   'model': model_name,
                                   'prompt': full_prompt,
                                   'stream': False,
                                   'options': {
                                       'temperature': 0.7,
                                       'max_tokens': 200  # Reduced for speed
                                   }
                               },
                               timeout=3)  # Short timeout
        
        if response.status_code == 200:
            return response.json()['response'].strip()
        else:
            return get_cached_response("general")
    
    except Exception as e:
        print(f"Ollama error: {e}")
        return get_cached_response("general")

# Fast information extraction
def extract_booking_info_fast(message, conversation_history):
    """Fast booking information extraction"""
    booking_info = {}
    
    # Extract name
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
    
    # Extract phone
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
    
    # Extract date/time
    date_patterns = [
        r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
        r'(today|tomorrow)',
        r'(\d{1,2}[/-]\d{1,2}[/-]?\d{0,4})'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, message_lower)
        if match:
            booking_info['date'] = match.group(1)
            break
    
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
        address_match = re.search(r'(\d+\s+[a-zA-Z\s]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|way|blvd|boulevard))', message)
        if address_match:
            booking_info['address'] = address_match.group(1)
    
    return booking_info

def save_booking_fast(booking_info, conversation_history):
    """Fast booking save with connection pooling"""
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()
        
        # Get description from conversation
        description = ""
        for msg in conversation_history[-3:]:
            if msg['role'] == 'user':
                description += msg['content'] + " "
        
        cursor.execute('''
            INSERT INTO bookings (customer_name, phone_number, job_type, preferred_date, 
                                preferred_time, address, description, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            booking_info.get('name', ''),
            booking_info.get('phone', ''),
            booking_info.get('job_type', ''),
            booking_info.get('date', ''),
            booking_info.get('time', ''),
            booking_info.get('address', ''),
            description.strip(),
            'pending'
        ))
        
        conn.commit()
        db_pool.return_connection(conn)
        print(f"✅ Booking saved: {booking_info}")
        
    except Exception as e:
        print(f"❌ Error saving booking: {e}")
        if 'conn' in locals():
            db_pool.return_connection(conn)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

class ChatPayload(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list = []


@app.route('/chat', methods=['POST'])
@limiter.limit(os.environ.get('CHAT_RATE_LIMIT', '20 per minute'))
def chat():
    try:
        data = request.get_json() or {}
        try:
            payload = ChatPayload(**data)
        except ValidationError as ve:
            return jsonify({'error': 'Invalid payload', 'detail': ve.errors()}), 400

        user_message = payload.message.strip()
        conversation_history = payload.history
        
        # Add user message to history
        conversation_history.append({'role': 'user', 'content': user_message})
        
        # Extract booking information
        booking_info = extract_booking_info_fast(user_message, conversation_history)
        
        # Get fast AI response
        ai_response = get_fast_ai_response(user_message, conversation_history)
        
        # Add AI response to history
        conversation_history.append({'role': 'assistant', 'content': ai_response})
        
        # Save booking if we have enough info
        if booking_info.get('name') and booking_info.get('phone') and booking_info.get('job_type'):
            save_booking_fast(booking_info, conversation_history)
        
        return jsonify({
            'response': ai_response,
            'booking_info': booking_info,
            'history': conversation_history
        })
        
    except Exception as e:
        app.logger.exception("Chat error")
        return jsonify({
            'response': "I'm sorry, I'm having trouble processing your request. Please try again.",
            'booking_info': {},
            'history': conversation_history
        }), 500

@app.route('/bookings')
def view_bookings():
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bookings ORDER BY created_at DESC')
        bookings = cursor.fetchall()
        db_pool.return_connection(conn)
        
        return render_template('bookings.html', bookings=bookings)
        
    except Exception as e:
        return f"Error retrieving bookings: {e}"

@app.route('/api/bookings')
def api_bookings():
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bookings ORDER BY created_at DESC')
        bookings = cursor.fetchall()
        db_pool.return_connection(conn)
        
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
                'urgency_level': booking[8],
                'status': booking[9],
                'created_at': booking[10],
                'updated_at': booking[11]
            })
        
        return jsonify(booking_list)
        
    except Exception as e:
        return jsonify({'error': str(e)})

# Export routes
@app.route('/export/csv')
def export_csv():
    """Export bookings as CSV"""
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bookings ORDER BY created_at DESC')
        bookings = cursor.fetchall()
        db_pool.return_connection(conn)
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Customer Name', 'Phone', 'Job Type', 'Date', 'Time', 'Address', 'Description', 'Urgency', 'Status', 'Created At', 'Updated At'])
        
        # Write data
        for booking in bookings:
            writer.writerow(booking)
        
        # Create response
        output.seek(0)
        csv_data = output.getvalue()
        output.close()
        
        return send_file(
            io.BytesIO(csv_data.encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'bookings_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/export/pdf')
def export_pdf():
    """Export bookings as PDF"""
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bookings ORDER BY created_at DESC')
        bookings = cursor.fetchall()
        db_pool.return_connection(conn)
        
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph("Electrician Bookings Report", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Create table
        table_data = [['ID', 'Customer', 'Phone', 'Job Type', 'Date', 'Time', 'Status']]
        
        for booking in bookings:
            table_data.append([
                str(booking[0]),
                booking[1],
                booking[2],
                booking[3],
                booking[4] or '',
                booking[5] or '',
                booking[9]
            ])
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        doc.build(story)
        
        buffer.seek(0)
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'bookings_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)})


# Basic health and readiness endpoints
@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200


@app.route('/ready')
def ready():
    try:
        conn = db_pool.get_connection()
        conn.execute('SELECT 1')
        db_pool.return_connection(conn)
        return jsonify({'status': 'ready'}), 200
    except Exception:
        return jsonify({'status': 'degraded'}), 503

if __name__ == '__main__':
    print("🚀 Starting Fast Electrician Chatbot...")
    print("⚡ Optimized for speed with caching and connection pooling")
    print("📊 Export features: CSV and PDF")
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '5000'))
    use_waitress = os.getenv('USE_WAITRESS', 'false').lower() == 'true'
    if use_waitress:
        from waitress import serve
        serve(app, host=host, port=port)
    else:
        app.run(debug=os.getenv('DEBUG', 'true').lower() == 'true', host=host, port=port)
