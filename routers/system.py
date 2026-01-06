"""
Microsoft PC Manager Features API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, OptimizationHistory, Alerts
from auth import get_current_active_user, User
from pydantic import BaseModel
import psutil
import os
import gc
import ctypes
from datetime import datetime
from typing import List, Optional

router = APIRouter(prefix="/api", tags=["System Management"])


class ProcessKillRequest(BaseModel):
    force: bool = False


@router.post("/boost-ram")
async def boost_ram(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """One-click RAM boost"""
    try:
        memory_before = psutil.virtual_memory().percent
        
        # Force garbage collection
        gc.collect()
        
        # On Windows, clear working set
        if os.name == 'nt':
            try:
                ctypes.windll.kernel32.SetProcessWorkingSetSize(-1, -1, -1)
            except:
                pass
        
        # Small delay to see effect
        import time
        time.sleep(0.5)
        
        memory_after = psutil.virtual_memory().percent
        freed = max(0, memory_before - memory_after)
        
        # Store in history
        history = OptimizationHistory(
            optimization_type="ram_boost",
            before_value=memory_before,
            after_value=memory_after,
            success=True,
            details=f"Freed {freed:.1f}% RAM"
        )
        db.add(history)
        db.commit()
        
        return {
            "success": True,
            "memory_before": round(memory_before, 2),
            "memory_after": round(memory_after, 2),
            "freed_percent": round(freed, 2),
            "message": f"RAM boost successful! Freed {freed:.1f}% memory."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/startup-apps")
async def get_startup_apps(
    current_user: User = Depends(get_current_active_user)
):
    """Get list of startup applications"""
    try:
        startup_apps = []
        
        if os.name == 'nt':  # Windows
            try:
                import winreg
                # Common startup registry keys
                keys = [
                    (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                    (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                ]
                
                for hkey, subkey in keys:
                    try:
                        key = winreg.OpenKey(hkey, subkey)
                        i = 0
                        while True:
                            try:
                                name, value, _ = winreg.EnumValue(key, i)
                                startup_apps.append({
                                    "name": name,
                                    "path": value,
                                    "location": "HKCU" if hkey == winreg.HKEY_CURRENT_USER else "HKLM"
                                })
                                i += 1
                            except WindowsError:
                                break
                        winreg.CloseKey(key)
                    except Exception as e:
                        pass
            except ImportError:
                pass
        
        return {
            "success": True,
            "startup_apps": startup_apps,
            "count": len(startup_apps)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/junk-files/scan")
async def scan_junk_files(
    current_user: User = Depends(get_current_active_user)
):
    """Scan for junk files"""
    try:
        junk_files = []
        total_size = 0
        
        # Common junk file locations
        junk_paths = []
        
        if os.name == 'nt':  # Windows
            temp_paths = [
                os.path.join(os.environ.get('TEMP', ''), '*'),
                os.path.join(os.environ.get('TMP', ''), '*'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp', '*'),
            ]
            
            for path_pattern in temp_paths:
                base_path = os.path.dirname(path_pattern)
                if os.path.exists(base_path):
                    try:
                        for root, dirs, files in os.walk(base_path):
                            for file in files:
                                try:
                                    file_path = os.path.join(root, file)
                                    size = os.path.getsize(file_path)
                                    total_size += size
                                    junk_files.append({
                                        "path": file_path,
                                        "size": size,
                                        "type": "temp"
                                    })
                                except:
                                    pass
                    except:
                        pass
        
        return {
            "success": True,
            "junk_files": junk_files[:100],  # Limit to first 100
            "total_count": len(junk_files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "estimated_time_seconds": len(junk_files) * 0.01
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/junk-files/clean")
async def clean_junk_files(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Clean junk files"""
    try:
        scan_result = await scan_junk_files(current_user)
        junk_files = scan_result.get("junk_files", [])
        
        cleaned = 0
        freed_size = 0
        errors = []
        
        for junk in junk_files:
            try:
                file_path = junk["path"]
                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)
                    os.remove(file_path)
                    cleaned += 1
                    freed_size += size
            except Exception as e:
                errors.append(str(e))
        
        # Store in history
        history = OptimizationHistory(
            optimization_type="junk_clean",
            before_value=scan_result.get("total_size_mb", 0),
            after_value=scan_result.get("total_size_mb", 0) - (freed_size / (1024 * 1024)),
            success=True,
            details=f"Cleaned {cleaned} files, freed {freed_size / (1024 * 1024):.2f} MB"
        )
        db.add(history)
        db.commit()
        
        return {
            "success": True,
            "cleaned_files": cleaned,
            "freed_size_mb": round(freed_size / (1024 * 1024), 2),
            "errors": errors[:10]  # Limit errors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
async def get_alerts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    resolved: Optional[bool] = None
):
    """Get system health alerts"""
    try:
        query = db.query(Alerts)
        if resolved is not None:
            query = query.filter(Alerts.resolved == resolved)
        
        alerts = query.order_by(Alerts.timestamp.desc()).limit(50).all()
        
        # Also check current system state for new alerts
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cpu = psutil.cpu_percent(interval=1)
        
        current_alerts = []
        
        if memory.percent > 90:
            current_alerts.append({
                "type": "critical",
                "title": "Critical Memory Usage",
                "message": f"Memory usage is at {memory.percent:.1f}%",
                "timestamp": datetime.utcnow()
            })
        
        if disk.percent > 90:
            current_alerts.append({
                "type": "critical",
                "title": "Critical Disk Space",
                "message": f"Disk usage is at {disk.percent:.1f}%",
                "timestamp": datetime.utcnow()
            })
        
        if cpu > 90:
            current_alerts.append({
                "type": "warning",
                "title": "High CPU Usage",
                "message": f"CPU usage is at {cpu:.1f}%",
                "timestamp": datetime.utcnow()
            })
        
        return {
            "success": True,
            "stored_alerts": [
                {
                    "id": alert.id,
                    "type": alert.alert_type,
                    "title": alert.title,
                    "message": alert.message,
                    "resolved": alert.resolved,
                    "timestamp": alert.timestamp.isoformat()
                }
                for alert in alerts
            ],
            "current_alerts": current_alerts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/processes/{pid}/kill")
async def kill_process(
    pid: int,
    request: ProcessKillRequest = None,
    current_user: User = Depends(get_current_active_user)
):
    """Kill a process by PID"""
    try:
        if request is None:
            request = ProcessKillRequest()
        
        proc = psutil.Process(pid)
        proc_name = proc.name()
        
        if request.force:
            proc.kill()
        else:
            proc.terminate()
        
        # Wait a bit
        import time
        time.sleep(0.5)
        
        # Check if still running
        if proc.is_running():
            proc.kill()
        
        return {
            "success": True,
            "pid": pid,
            "name": proc_name,
            "message": f"Process {proc_name} (PID: {pid}) terminated successfully"
        }
    except psutil.NoSuchProcess:
        raise HTTPException(status_code=404, detail="Process not found")
    except psutil.AccessDenied:
        raise HTTPException(status_code=403, detail="Access denied. Run as administrator.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

