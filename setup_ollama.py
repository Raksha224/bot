#!/usr/bin/env python3
"""
Setup script for Ollama integration
This script helps you install and configure Ollama for the electrician chatbot
"""

import subprocess
import sys
import os
import platform

def run_command(command, shell=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_ollama_installed():
    """Check if Ollama is already installed"""
    success, stdout, stderr = run_command("ollama --version")
    return success

def install_ollama():
    """Install Ollama based on the operating system"""
    system = platform.system().lower()
    
    print("🔧 Installing Ollama...")
    
    if system == "windows":
        print("📥 Downloading Ollama for Windows...")
        # For Windows, we'll provide instructions
        print("Please download Ollama from: https://ollama.com/download")
        print("After installation, restart your terminal and run this script again.")
        return False
    
    elif system == "darwin":  # macOS
        print("📥 Installing Ollama for macOS...")
        success, stdout, stderr = run_command("curl -fsSL https://ollama.com/install.sh | sh")
        return success
    
    elif system == "linux":
        print("📥 Installing Ollama for Linux...")
        success, stdout, stderr = run_command("curl -fsSL https://ollama.com/install.sh | sh")
        return success
    
    else:
        print(f"❌ Unsupported operating system: {system}")
        return False

def start_ollama_service():
    """Start the Ollama service"""
    print("🚀 Starting Ollama service...")
    success, stdout, stderr = run_command("ollama serve")
    return success

def pull_model(model_name="mistral"):
    """Pull a model from Ollama"""
    print(f"📦 Pulling {model_name} model...")
    success, stdout, stderr = run_command(f"ollama pull {model_name}")
    return success

def main():
    print("⚡ Electrician Chatbot Setup")
    print("=" * 40)
    
    # Check if Ollama is already installed
    if check_ollama_installed():
        print("✅ Ollama is already installed!")
    else:
        print("❌ Ollama not found. Installing...")
        if not install_ollama():
            print("❌ Failed to install Ollama. Please install manually from https://ollama.com")
            return
        print("✅ Ollama installed successfully!")
    
    # Pull the model
    print("\n📦 Setting up AI model...")
    model_choice = input("Choose a model (1: mistral, 2: llama3, 3: phi3): ").strip()
    
    models = {
        "1": "mistral",
        "2": "llama3", 
        "3": "phi3"
    }
    
    model_name = models.get(model_choice, "mistral")
    print(f"Selected model: {model_name}")
    
    if pull_model(model_name):
        print(f"✅ {model_name} model downloaded successfully!")
    else:
        print(f"❌ Failed to download {model_name} model")
        return
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Start Ollama service: ollama serve")
    print("2. In another terminal, run: python app.py")
    print("3. Open your browser to: http://localhost:5000")
    
    # Ask if user wants to start Ollama now
    start_now = input("\nStart Ollama service now? (y/n): ").strip().lower()
    if start_now == 'y':
        print("🚀 Starting Ollama service...")
        print("Keep this terminal open to keep Ollama running.")
        print("Open another terminal to run: python app.py")
        start_ollama_service()

if __name__ == "__main__":
    main()
