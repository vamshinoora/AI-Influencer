#!/usr/bin/env python3
"""
Environment setup script for AI Influencer MongoDB connection.
"""

import os

def setup_mongodb_env():
    """Set up MongoDB environment variables."""
    
    print("🔧 MongoDB Environment Setup")
    print("=" * 40)
    
    # Check if connection string is already set
    existing_connection = os.getenv('MONGODB_CONNECTION_STRING')
    if existing_connection:
        print(f"✅ MongoDB connection string already set")
        print(f"🔗 Current: {existing_connection[:50]}...")
        
        change = input("Do you want to change it? (y/N): ").lower().strip()
        if change != 'y':
            return existing_connection
    
    print("\n📝 Please provide your MongoDB connection details:")
    print("You can use either:")
    print("1. Full connection string (mongodb+srv://...)")
    print("2. Individual connection details")
    
    choice = input("\nEnter choice (1 for full string, 2 for details): ").strip()
    
    if choice == "1":
        connection_string = input("Enter MongoDB connection string: ").strip()
    else:
        print("\n📋 Individual Connection Details:")
        host = input("Host (default: localhost): ").strip() or "localhost"
        port = input("Port (default: 27017): ").strip() or "27017"
        
        use_auth = input("Use authentication? (y/N): ").lower().strip() == 'y'
        
        if use_auth:
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            database = input("Database (default: ai_influencer): ").strip() or "ai_influencer"
            
            # URL encode credentials
            import urllib.parse
            username = urllib.parse.quote_plus(username)
            password = urllib.parse.quote_plus(password)
            
            connection_string = f"mongodb://{username}:{password}@{host}:{port}/{database}"
        else:
            connection_string = f"mongodb://{host}:{port}/"
    
    # Set environment variable for current session
    os.environ['MONGODB_CONNECTION_STRING'] = connection_string
    
    print(f"\n✅ MongoDB connection string set!")
    print(f"🔗 Connection: {connection_string[:50]}...")
    
    # Optionally save to .env file
    save_env = input("\nSave to .env file? (y/N): ").lower().strip() == 'y'
    if save_env:
        env_path = os.path.join(os.getcwd(), '.env')
        with open(env_path, 'a') as f:
            f.write(f"\n# MongoDB Connection\nMONGODB_CONNECTION_STRING={connection_string}\n")
        print(f"💾 Saved to {env_path}")
    
    return connection_string

if __name__ == "__main__":
    setup_mongodb_env()
