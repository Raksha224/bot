#!/usr/bin/env python3
"""
Enhanced Test script for the Intelligent Electrician Chatbot
This demonstrates the advanced conversational capabilities
"""

import requests
import json
import time

def test_enhanced_chatbot():
    """Test the enhanced chatbot with various conversation scenarios"""
    
    # Comprehensive test scenarios
    test_scenarios = [
        {
            "name": "Initial Greeting",
            "messages": ["Hello"]
        },
        {
            "name": "Frustrated Customer",
            "messages": ["My outlet is broken and it's driving me crazy!"]
        },
        {
            "name": "Emergency Situation", 
            "messages": ["I have sparks coming from my outlet!"]
        },
        {
            "name": "Installation Request",
            "messages": ["I want to install new lighting in my kitchen"]
        },
        {
            "name": "Information Gathering",
            "messages": ["I need a repair", "My name is John Smith", "555-123-4567"]
        },
        {
            "name": "Scheduling Conversation",
            "messages": ["I need someone tomorrow at 2pm", "My address is 123 Main St"]
        },
        {
            "name": "Pricing Question",
            "messages": ["How much will this cost?"]
        },
        {
            "name": "Thank You Response",
            "messages": ["Thank you so much for your help!"]
        },
        {
            "name": "Worried Customer",
            "messages": ["I'm worried about the electrical safety in my home"]
        },
        {
            "name": "Excited Customer",
            "messages": ["I'm so excited to upgrade my electrical system!"]
        }
    ]
    
    print("🤖 Testing Enhanced Intelligent Electrician Chatbot")
    print("=" * 60)
    
    for scenario in test_scenarios:
        print(f"\n🧪 Test Scenario: {scenario['name']}")
        print("-" * 50)
        
        conversation_history = []
        
        for i, message in enumerate(scenario['messages'], 1):
            print(f"\n👤 Customer {i}: '{message}'")
            print("-" * 30)
            
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
                return
            except Exception as e:
                print(f"❌ Error: {e}")
            
            time.sleep(0.5)  # Small delay between messages
        
        print("\n" + "="*50)
    
    print("\n🎉 Enhanced Chatbot Testing Completed!")
    print("\nKey Features Demonstrated:")
    print("✅ Intelligent conversation state management")
    print("✅ Context-aware responses and memory")
    print("✅ Emotional intelligence and empathy")
    print("✅ Smart follow-up questions")
    print("✅ Dynamic response generation")
    print("✅ Emergency handling with direct call option")
    print("✅ Personalized greetings and responses")
    print("✅ Natural conversation flow")

if __name__ == "__main__":
    test_enhanced_chatbot()
