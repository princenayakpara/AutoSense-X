"""
Setup script for AutoSense X
"""
import os
import sqlite3
from database import init_db

def setup_directories():
    """Create necessary directories"""
    directories = [
        "./models",
        "./temp",
        "./logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def setup_database():
    """Initialize database"""
    try:
        init_db()
        print("✓ Database initialized")
    except Exception as e:
        print(f"✗ Database initialization error: {e}")

def main():
    print("🔥 AutoSense X Setup")
    print("=" * 50)
    
    print("\n1. Creating directories...")
    setup_directories()
    
    print("\n2. Initializing database...")
    setup_database()
    
    print("\n3. Setup complete!")
    print("\nNext steps:")
    print("  - Copy .env.example to .env and configure")
    print("  - Install dependencies: pip install -r requirements.txt")
    print("  - Run server: python start_server.py")
    print("  - Open frontend/index.html in browser")

if __name__ == "__main__":
    main()

