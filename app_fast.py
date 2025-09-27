"""
Fast, optimized version of the Electrician Chatbot with export features.
This version prioritizes speed while maintaining clean architecture principles.
"""
from flask import Flask, render_template, request, jsonify, send_file, Response
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
import random
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import threading
from functools import lru_cache
from typing import List, Tuple, Optional

load_dotenv()
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": os.environ.get("CORS_ORIGINS", "*")}})
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    storage_uri=os.environ.get("RATE_LIMIT_STORAGE", "memory://"),
    default_limits=[os.environ.get("RATE_LIMIT", "60 per minute")]
)

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
            elif name.lower().endswith('.csv') and name.lower() != 'faq.csv':
                # Read small head only for speed
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    head = ''.join([next(f, '') for _ in range(6)])
                    snippets.append(head)
            elif name.lower().endswith('.pdf'):
                # Avoid heavy parsing; use filename as tag
                snippets.append(f"PDF: {name}")
    except Exception as e:
        app.logger.warning(f"KB load warning: {e}")
    return snippets

KB_SNIPPETS = _load_kb_snippets()

# Load FAQ pairs for precise instant answers
def _load_faq() -> List[Tuple[str, str]]:
    faq_path = os.path.join(KB_DIR, 'faq.csv')
    items: List[Tuple[str, str]] = []
    if os.path.exists(faq_path):
        try:
            import csv
            with open(faq_path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                for row in reader:
                    if len(row) >= 2:
                        items.append((row[0].strip(), row[1].strip()))
        except Exception as e:
            app.logger.warning(f"FAQ load warning: {e}")
    return items

FAQ_QA: List[Tuple[str, str]] = _load_faq()

def _simple_similarity(a: str, b: str) -> float:
    aset = set(a.lower().split())
    bset = set(b.lower().split())
    if not aset or not bset:
        return 0.0
    inter = len(aset & bset)
    union = len(aset | bset)
    return inter / union

def answer_from_faq(message: str) -> str | None:
    best = (0.0, None)
    for q, a in FAQ_QA:
        s = _simple_similarity(message, q)
        if s > best[0]:
            best = (s, a)
    return best[1] if best[0] >= 0.35 else None

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
    # FAQ shortcut (exact business answers)
    faq_ans = answer_from_faq(message)
    if faq_ans:
        # add a small conversational follow-up to avoid feeling repetitive
        tails = [
            " Would you like to schedule a visit?",
            " Do you want me to book a slot for you?",
            " I can arrange an electrician—what day works for you?"
        ]
        return faq_ans + random.choice(tails)
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
        return get_cached_response("greeting")

    if any(word in message_lower for word in ['emergency', 'urgent', 'spark', 'burning', 'smoke', 'fire']):
        return get_cached_response("emergency")

    # Services overview
    if any(phrase in message_lower for phrase in ['what services', 'services you', 'do you offer', 'do you handle', 'service list', 'which services']):
        return _services_overview()

    # Repair intent (electrical only)
    if any(word in message_lower for word in ['broken', 'not working', 'fix', 'repair', 'outlet', 'switch', 'short', 'sparking', 'tripping', 'breaker']):
        variants = [
            "I can help with that repair—outlets, switches, lights, or breakers. ",
            "No problem—our electricians handle outlet/switch/light/breaker issues every day. ",
            "We’ll get that sorted. We fix outlets, switches, lighting and breakers. "
        ]
        return random.choice(variants) + _precise_repair_followups()

    # Installation intent
    if any(word in message_lower for word in ['install', 'new', 'add', 'put in', 'wiring', 'replace fixture', 'ceiling fan (electric wiring)']):
        variants = [
            "We install lighting, outlets/switches, dedicated circuits and smart switches. ",
            "Installations are our thing—lighting upgrades, smart switches, new outlets. ",
            "Happy to install—lighting, outlets, smart devices, new circuits. "
        ]
        return random.choice(variants) + "What are you looking to install and where?"

    if any(word in message_lower for word in ['price', 'cost', 'how much', 'estimate', 'quote']):
        return (
            "We provide free on-site estimates for electrical work. "
            "Share the issue or installation details and your zip/address to schedule."
        )

    if any(word in message_lower for word in ['thank', 'thanks', 'appreciate']):
        return get_cached_response("thanks")

    # 3) Fall back to local model (fast) else a conversational default
    try:
        return get_ollama_response_fast(message, conversation_history)
    except:
        openers = [
            "Happy to help—",
            "Got it—",
            "Sure—",
            "Thanks for reaching out—"
        ]
        prompts = [
            "could you describe the electrical issue or installation you need?",
            "what room and devices are affected?",
            "do you notice any tripping breakers, smells, or sparks?",
            "when would you like us to come by?"
        ]
        return random.choice(openers) + random.choice(prompts)

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

def stream_ollama_tokens(message, conversation_history):
    """Yield tokens from Ollama when streaming is enabled; fallback to full text chunks."""
    try:
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        model_name = os.getenv('OLLAMA_MODEL', 'mistral')
        use_ollama = os.getenv('USE_OLLAMA', 'true').lower() == 'true'
        if not use_ollama:
            raise Exception('Ollama disabled via USE_OLLAMA=false')

        history_text = ""
        for msg in conversation_history[-6:]:
            role = "Customer" if msg['role'] == 'user' else "Sarah"
            history_text += f"{role}: {msg['content']}\n"

        system_prompt = "You are Sarah, an expert electrical service receptionist. ONLY discuss electrical work. Be concise, warm, and never repeat the user's question."
        kb_text = '\n'.join(KB_SNIPPETS[:5])
        full_prompt = f"{system_prompt}\n\nCONVERSATION HISTORY:\n{history_text}\n\nCURRENT MESSAGE: {message}\n\nKNOWLEDGE HINTS:\n{kb_text}\n\nRESPOND AS SARAH:"

        with requests.post(
            f"{base_url}/api/generate",
            json={
                'model': model_name,
                'prompt': full_prompt,
                'stream': True,
                'options': {'temperature': 0.7, 'max_tokens': 300}
            },
            stream=True,
            timeout=15
        ) as r:
            r.raise_for_status()
            buffer = ''
            for line in r.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    token = obj.get('response', '')
                    if token:
                        yield token
                        buffer += token
                except Exception:
                    continue
    except Exception as e:
        yield ""

# Fast information extraction
def extract_booking_info_fast(message, conversation_history):
    """Fast booking information extraction that also looks back in history.
    This prevents asking again for details already given earlier."""
    booking_info = {}

    # Extract name
    name_patterns = [
        r"my name is (\w+)",
        r"i'm (\w+)",
        r"i am (\w+)",
        r"this is (\w+)",
        r"call me (\w+)"
    ]

    def find_name(text: str):
        for pattern in name_patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1).title()
        return None

    # Heuristic: bare name like "raksha singh" without prefix
    def is_name_like(text: str) -> str | None:
        t = text.strip()
        if any(ch.isdigit() for ch in t):
            return None
        # allow 1-3 words letters/space/.-'
        import string
        allowed = set(string.ascii_letters + " .-'”’“‘")
        if not all(ch in allowed for ch in t):
            return None
        words = [w for w in re.split(r"\s+", t) if w]
        if 1 <= len(words) <= 3 and 2 <= len(t) <= 40:
            return t.title()
        return None

    nm = find_name(message) or is_name_like(message)
    if nm:
        booking_info['name'] = nm
    else:
        for msg in reversed(conversation_history[-10:]):
            if msg.get('role') == 'user':
                nm = find_name(msg.get('content', '')) or is_name_like(msg.get('content', ''))
                if nm:
                    booking_info['name'] = nm
                    break

    # Extract phone
    phone_pattern = r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})'
    def find_phone(text: str):
        m = re.search(phone_pattern, text)
        return m.group(1) if m else None

    ph = find_phone(message)
    if ph:
        booking_info['phone'] = ph
    else:
        for msg in reversed(conversation_history[-10:]):
            if msg.get('role') == 'user':
                ph = find_phone(msg.get('content', ''))
                if ph:
                    booking_info['phone'] = ph
                    break

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
    if 'job_type' not in booking_info:
        for msg in reversed(conversation_history[-10:]):
            if msg.get('role') == 'user':
                txt = msg.get('content', '').lower()
                for job_type, keywords in job_keywords.items():
                    if any(keyword in txt for keyword in keywords):
                        booking_info['job_type'] = job_type
                        break
                if 'job_type' in booking_info:
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
    if 'date' not in booking_info:
        for msg in reversed(conversation_history[-10:]):
            if msg.get('role') == 'user':
                txt = msg.get('content', '').lower()
                for pattern in date_patterns:
                    match = re.search(pattern, txt)
                    if match:
                        booking_info['date'] = match.group(1)
                        break
                if 'date' in booking_info:
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
    if 'time' not in booking_info:
        for msg in reversed(conversation_history[-10:]):
            if msg.get('role') == 'user':
                txt = msg.get('content', '').lower()
                for pattern in time_patterns:
                    match = re.search(pattern, txt)
                    if match:
                        booking_info['time'] = match.group(1)
                        break
                if 'time' in booking_info:
                    break

    # Extract address (very simple heuristic)
    address_keywords = ['address', 'location', 'at', 'live', 'located']
    if any(keyword in message_lower for keyword in address_keywords):
        address_match = re.search(r'(\d+\s+[a-zA-Z\s]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|way|blvd|boulevard))', message)
        if address_match:
            booking_info['address'] = address_match.group(1)
    if 'address' not in booking_info:
        for msg in reversed(conversation_history[-10:]):
            if msg.get('role') == 'user':
                txt = msg.get('content', '')
                if any(k in txt.lower() for k in address_keywords):
                    m = re.search(r'(\d+\s+[a-zA-Z\s]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|way|blvd|boulevard))', txt)
                    if m:
                        booking_info['address'] = m.group(1)
                        break

    return booking_info

def save_booking_fast(booking_info, conversation_history) -> Optional[int]:
    """Fast booking save with connection pooling. Returns booking id."""
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
        
        booking_id = cursor.lastrowid
        conn.commit()
        db_pool.return_connection(conn)
        print(f"✅ Booking saved: {booking_info} -> id={booking_id}")
        return booking_id

    except Exception as e:
        print(f"❌ Error saving booking: {e}")
        if 'conn' in locals():
            db_pool.return_connection(conn)
        return None

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
        message_lower = user_message.lower()
        
        # Add user message to history
        conversation_history.append({'role': 'user', 'content': user_message})
        
        # Extract booking information
        booking_info = extract_booking_info_fast(user_message, conversation_history)
        
        # Get fast AI response
        ai_response = get_fast_ai_response(user_message, conversation_history)
        
        # Add AI response to history
        conversation_history.append({'role': 'assistant', 'content': ai_response})
        
        # Save when enough info; otherwise ask for the next missing field
        if booking_info.get('name') and booking_info.get('phone') and booking_info.get('job_type'):
            booking_id = save_booking_fast(booking_info, conversation_history)
            if booking_id:
                ai_response += f"\n\nI've saved your booking (ID {booking_id}). We'll confirm shortly."
        else:
            # Only nudge when the user is trying to book/schedule, not when asking info questions
            info_question = any(
                kw in message_lower for kw in [
                    'what', 'how', 'which', 'do you', 'can you', 'service', 'provide', 'offer', 'price', 'cost', 'list'
                ]
            )
            booking_trigger = any(
                kw in message_lower for kw in ['book', 'schedule', 'visit', 'come by', 'appointment', 'confirm']
            ) or bool(booking_info.get('job_type'))

            if booking_trigger and not info_question:
                missing = []
                for f in ['name','phone','address','job_type','date','time']:
                    if not booking_info.get(f):
                        missing.append(f)
                if missing:
                    prompts = {
                        'name': "What's your full name?",
                        'phone': "What's the best phone number to reach you?",
                        'address': "What's the service address?",
                        'job_type': "What electrical work do you need (repair, installation, panel, lighting, etc.)?",
                        'date': "What day works for you?",
                        'time': "Do you prefer morning, afternoon, or an exact time?",
                    }
                    ai_response += "\n\n" + prompts.get(missing[0], "Could you share a few more details?")
        
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
## Export endpoints removed per request


@app.route('/chat_stream', methods=['POST'])
@limiter.limit(os.environ.get('CHAT_RATE_LIMIT', '20 per minute'))
def chat_stream():
    try:
        data = request.get_json() or {}
        try:
            payload = ChatPayload(**data)
        except ValidationError as ve:
            return jsonify({'error': 'Invalid payload', 'detail': ve.errors()}), 400

        user_message = payload.message.strip()
        history = payload.history or []

        def generate():
            # first yield a short opener for responsiveness
            opener = ""
            faq_ans = answer_from_faq(user_message)
            if faq_ans:
                opener = faq_ans + " "
                yield opener

            # stream from ollama if enabled, else chunk the fast reply
            used_any = False
            for tok in stream_ollama_tokens(user_message, history):
                if tok:
                    used_any = True
                    yield tok
            if not used_any:
                # fallback chunking
                text = get_fast_ai_response(user_message, history)
                for i in range(0, len(text), 40):
                    yield text[i:i+40]

        return Response(generate(), mimetype='text/plain')
    except Exception:
        app.logger.exception('stream error')
        return jsonify({'error': 'stream failed'}), 500


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
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '5000'))
    print(f"🔗 Chat: http://localhost:{port}")
    print(f"📊 Admin: http://localhost:{port}/bookings")
    print(f"💚 Health: http://localhost:{port}/health")
    print(f"🌀 Streaming: POST http://localhost:{port}/chat_stream")
    use_waitress = os.getenv('USE_WAITRESS', 'false').lower() == 'true'
    if use_waitress:
        from waitress import serve
        serve(app, host=host, port=port)
    else:
        app.run(debug=os.getenv('DEBUG', 'true').lower() == 'true', host=host, port=port)
