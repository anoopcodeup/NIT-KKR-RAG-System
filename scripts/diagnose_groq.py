import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))
from groq import Groq

def diagnose():
    print("--- Groq API Diagnosis ---")
    
    # Load .env from root
    root_dir = Path(__file__).parent.parent
    env_path = root_dir / ".env"
    load_dotenv(dotenv_path=env_path, override=True)
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("No GROQ_API_KEY found in environment or .env file.")
        return
    
    print(f"Key found: {api_key[:10]}...{api_key[-5:]}")
    print(f"Key length: {len(api_key)}")
    
    try:
        client = Groq(api_key=api_key)
        print("Testing chat completion...")
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Hello",
                }
            ],
            model="llama-3.1-8b-instant",
        )
        print("[SUCCESS] Connection successful!")
        print(f"Response: {chat_completion.choices[0].message.content[:50]}...")
    except Exception as e:
        print(f"[FAILURE] Connection failed: {e}")
        if "401" in str(e):
            print("   Hint: This is an authentication error. The key is likely invalid.")
        elif "403" in str(e):
            print("   Hint: Access forbidden. Check if your account is active.")
        elif "429" in str(e):
            print("   Hint: Rate limit exceeded or quota reached.")

if __name__ == "__main__":
    diagnose()
