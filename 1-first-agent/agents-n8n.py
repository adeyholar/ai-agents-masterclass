import os
from datetime import datetime
import requests
import json

# Local Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:latest"

def chat_with_ollama(prompt):
    """Chat with your local Ollama AI"""
    data = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=data)
        result = response.json()
        return result.get('response', 'No response')
    except Exception as e:
        return f"Error: {e}"

def main():
    print("🤖 Your Local AI Assistant is ready!")
    print("Ask me to help you with anything!")
    print("Type 'quit' to exit\n")
    
    conversation_history = []
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'q', 'exit']:
            print("👋 Goodbye!")
            break
        
        # Build conversation context
        context = f"You are a helpful personal assistant. Current date: {datetime.now().date()}\n"
        for msg in conversation_history[-5:]:  # Keep last 5 messages for context
            context += f"{msg}\n"
        context += f"Human: {user_input}\nAssistant:"
        
        print("🤖 Thinking...")
        ai_response = chat_with_ollama(context)
        
        print(f"AI: {ai_response}\n")
        
        # Store conversation
        conversation_history.append(f"Human: {user_input}")
        conversation_history.append(f"Assistant: {ai_response}")

if __name__ == "__main__":
    main()