#!/usr/bin/env python3
"""
Setup script for Groq LLM integration.
This script helps users configure their Groq API key.
"""

import os
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

def create_env_file():
    """Create a .env file with Groq API key template."""
    env_file = ROOT_DIR / ".env"
    
    if env_file.exists():
        print("⚠️  .env file already exists.")
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print("Skipping .env file creation.")
            return
    
    api_key = input("Enter your Groq API key: ").strip()
    if not api_key:
        print("❌ No API key provided.")
        return
    
    # Get model preference
    print("\nAvailable Groq models:")
    print("1. llama-3.1-8b-instant (default, fast)")
    print("2. llama-3.1-70b-versatile (more capable)")
    print("3. mixtral-8x7b-32768 (balanced)")
    print("4. gemma2-9b-it (alternative)")
    
    model_choice = input("Choose model (1-4, default: 1): ").strip()
    models = {
        "1": "llama-3.1-8b-instant",
        "2": "llama-3.1-70b-versatile", 
        "3": "mixtral-8x7b-32768",
        "4": "gemma2-9b-it"
    }
    model = models.get(model_choice, "llama-3.1-8b-instant")
    
    # Write .env file
    env_content = f"""# Groq API Configuration
GROQ_API_KEY={api_key}
GROQ_MODEL={model}
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Created .env file with API key and model: {model}")

def set_environment_variable():
    """Set GROQ_API_KEY as environment variable."""
    api_key = input("Enter your Groq API key: ").strip()
    if not api_key:
        print("❌ No API key provided.")
        return
    
    # For Windows
    if os.name == 'nt':
        os.system(f'setx GROQ_API_KEY "{api_key}"')
        print("✅ Set GROQ_API_KEY environment variable (Windows)")
        print("Note: You may need to restart your terminal/IDE for the change to take effect.")
    else:
        # For Unix-like systems
        print(f"Run this command to set the environment variable:")
        print(f"export GROQ_API_KEY='{api_key}'")
        print("Or add it to your ~/.bashrc or ~/.zshrc file")

def test_groq_connection():
    """Test the Groq connection."""
    try:
        # Reload environment variables from .env
        try:
            from dotenv import load_dotenv
            load_dotenv(override=True)
        except ImportError:
            pass
            
        from groq_llm import create_groq_service
        
        print("🔍 Testing Groq connection...")
        service = create_groq_service()
        
        if service and service.test_connection():
            print("✅ Groq connection successful!")
            print(f"Model: {service.model}")
        else:
            print("❌ Groq connection failed.")
            
    except ImportError:
        print("❌ Groq SDK not installed. Run: pip install groq")
    except Exception as e:
        print(f"❌ Error testing connection: {e}")

def main():
    """Main setup function."""
    print("🚀 Groq LLM Setup for NIT Kurukshetra RAG System")
    print("=" * 50)
    print("Get your API key from: https://console.groq.com/keys")
    print()
    
    while True:
        print("Setup Options:")
        print("1. Create .env file (recommended)")
        print("2. Set environment variable")
        print("3. Test Groq connection")
        print("4. Exit")
        
        choice = input("\nChoose an option (1-4): ").strip()
        
        if choice == "1":
            create_env_file()
        elif choice == "2":
            set_environment_variable()
        elif choice == "3":
            test_groq_connection()
        elif choice == "4":
            print("👋 Setup complete!")
            break
        else:
            print("❌ Invalid choice. Please choose 1-4.")
        
        print("\n" + "-" * 30 + "\n")

if __name__ == "__main__":
    main()
