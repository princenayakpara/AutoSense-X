"""
AutoSense X - Ultimate AI System Guardian
Main FastAPI Application
"""
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from database import init_db, get_db
from routers import ai, system, disk, apps, security, auth_router, voice
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AutoSense X - Ultimate AI System Guardian",
    description="World's most advanced AI PC Guardian combining Microsoft PC Manager, WizTree Disk Analyzer, Revo Uninstaller Pro, and a self-healing AI brain",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
async def startup_event():
    init_db()

# Serve frontend static files
frontend_path = Path(__file__).parent / "frontend"
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Helper to serve other static files directly if needed
@app.get("/app.js")
async def serve_js():
    return FileResponse(frontend_path / "app.js")

@app.get("/styles.css")
async def serve_css():
    return FileResponse(frontend_path / "styles.css")

@app.get("/logo.jpg")
async def serve_logo():
    return FileResponse(frontend_path / "logo.jpg")


# Include routers
app.include_router(auth_router.router)
app.include_router(ai.router)
app.include_router(system.router)
app.include_router(disk.router)
app.include_router(apps.router)
app.include_router(security.router)
app.include_router(voice.router)


# Root endpoint - Serve Frontend
@app.get("/")
async def root():
    return FileResponse(frontend_path / "index.html")

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "AutoSense X"}


# System info endpoint (no auth required for monitoring)
@app.get("/api/system/info")
async def get_system_info():
    """Get basic system information"""
    try:
        import psutil
        
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cpu_count = psutil.cpu_count()
        
        return {
            "success": True,
            "system": {
                "cpu_count": cpu_count,
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "memory_percent": memory.percent,
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "disk_used_gb": round(disk.used / (1024**3), 2),
                "disk_percent": disk.percent,
                "process_count": len(psutil.pids()),
                "total_processes": len(psutil.pids())
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)

