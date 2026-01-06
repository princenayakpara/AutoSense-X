"""
Startup script for AutoSense X
"""
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    print("🔥 Starting AutoSense X - Ultimate AI System Guardian...")
    print(f"Server running on http://{host}:{port}")
    print(f"API Documentation: http://{host}:{port}/docs")
    print(f"Frontend: Open frontend/index.html in your browser")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

