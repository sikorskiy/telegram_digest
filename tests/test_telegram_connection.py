import os
from dotenv import load_dotenv
from telethon import TelegramClient

def main():
    print("🔍 Current working directory:", os.getcwd())
    print("🔍 Looking for .env file...")
    
    env_path = os.path.join(os.getcwd(), '.env')
    print(f"🔍 .env path: {env_path}")
    print(f"🔍 .env exists: {os.path.exists(env_path)}")
    
    load_dotenv()
    
    api_id = os.getenv("TG_API_ID")
    api_hash = os.getenv("TG_API_HASH")
    session_path = "./storage/session_name.session"
    
    print(f"🔍 TG_API_ID: {'✓' if api_id else '✗'}")
    print(f"🔍 TG_API_HASH: {'✓' if api_hash else '✗'}")
    
    if not api_id or not api_hash:
        print("❌ TG_API_ID and TG_API_HASH must be set in .env file")
        return
    
    print(f"🔑 Using session file: {session_path}")
    
    client = TelegramClient(session_path, int(api_id), api_hash)
    
    try:
        with client:
            me = client.loop.run_until_complete(client.get_me())
            print(f"✅ Successfully connected as {me.first_name} (@{me.username})")
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")

if __name__ == "__main__":
    main() 