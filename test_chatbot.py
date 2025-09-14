#!/usr/bin/env python3
"""
Test script for the Electrician Chatbot
This script tests the chatbot responses without needing the full web interface
"""

import requests
import json
import time

def test_chatbot():
    """Test the chatbot with various scenarios"""
    
    # Test cases
    test_cases = [
        "Hello",
        "I need to fix my broken outlet",
        "My name is John Smith, phone is 555-123-4567",
        "I need an emergency repair",
        "Can you install new lighting?",
        "What are your prices?",
        "I need someone tomorrow at 2pm",
        "Thank you for your help"
    ]
    
    print("🤖 Testing Electrician Chatbot Responses")
    print("=" * 50)
    
    conversation_history = []
    
    for i, message in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: Customer says: '{message}'")
        print("-" * 40)
        
        try:
            # Send request to chatbot
            response = requests.post('http://localhost:5000/chat', 
                                   json={
                                       'message': message,
                                       'history': conversation_history
                                   },
                                   timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data['response']
                booking_info = data.get('booking_info', {})
                
                print(f"🤖 Sarah responds: {ai_response}")
                
                if booking_info:
                    print(f"📝 Booking info captured: {booking_info}")
                
                # Update conversation history
                conversation_history.append({'role': 'user', 'content': message})
                conversation_history.append({'role': 'assistant', 'content': ai_response})
                
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Error: Could not connect to chatbot. Make sure it's running on localhost:5000")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 50)
    print("✅ Chatbot testing completed!")
    print("\nTo start the full chatbot:")
    print("1. Make sure Ollama is running: ollama serve")
    print("2. Run the app: python app.py")
    print("3. Visit: http://localhost:5000")

if __name__ == "__main__":
    test_chatbot()
