"""
Advanced Security Center API
"""
from fastapi import APIRouter, Depends
from auth import get_current_active_user, User
import socket
import subprocess
import os
from typing import List, Dict

router = APIRouter(prefix="/api/security", tags=["Security"])


@router.get("/firewall")
async def get_firewall_status(
    current_user: User = Depends(get_current_active_user)
):
    """Get Windows Firewall status"""
    try:
        if os.name != 'nt':
            return {
                "success": False,
                "error": "Firewall status check only available on Windows"
            }
        
        # Check firewall status using netsh
        result = subprocess.run(
            ["netsh", "advfirewall", "show", "allprofiles", "state"],
            capture_output=True,
            text=True
        )
        
        firewall_status = {
            "enabled": False,
            "profiles": {}
        }
        
        if "ON" in result.stdout.upper():
            firewall_status["enabled"] = True
        
        # Parse profile states
        lines = result.stdout.split('\n')
        current_profile = None
        for line in lines:
            if "Profile" in line and "Settings" in line:
                current_profile = line.split()[0]
            elif "State" in line and current_profile:
                state = "ON" if "ON" in line.upper() else "OFF"
                firewall_status["profiles"][current_profile] = state == "ON"
        
        return {
            "success": True,
            "firewall": firewall_status
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/ports")
async def get_open_ports(
    current_user: User = Depends(get_current_active_user)
):
    """Get list of open ports and listening services"""
    try:
        import psutil
        
        connections = psutil.net_connections(kind='inet')
        open_ports = []
        
        seen_ports = set()
        for conn in connections:
            if conn.status == 'LISTEN':
                port = conn.laddr.port
                if port not in seen_ports:
                    seen_ports.add(port)
                    
                    # Get process info
                    process_info = None
                    if conn.pid:
                        try:
                            proc = psutil.Process(conn.pid)
                            process_info = {
                                "pid": conn.pid,
                                "name": proc.name(),
                                "exe": proc.exe() if proc.exe() else "N/A"
                            }
                        except:
                            pass
                    
                    open_ports.append({
                        "port": port,
                        "address": conn.laddr.ip,
                        "protocol": "TCP" if conn.type == socket.SOCK_STREAM else "UDP",
                        "process": process_info
                    })
        
        # Sort by port
        open_ports.sort(key=lambda x: x["port"])
        
        return {
            "success": True,
            "open_ports": open_ports,
            "count": len(open_ports)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/scan")
async def malware_scan(
    current_user: User = Depends(get_current_active_user)
):
    """AI-powered malware scan (heuristic analysis)"""
    try:
        import psutil
        
        suspicious_processes = []
        suspicious_files = []
        
        # Scan running processes
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cpu_percent', 'memory_percent']):
            try:
                proc_info = proc.info
                name = proc_info.get('name', '').lower()
                exe = proc_info.get('exe', '')
                
                # Heuristic checks
                suspicious_flags = []
                
                # High CPU with no visible window
                if proc_info.get('cpu_percent', 0) > 50:
                    suspicious_flags.append("High CPU usage")
                
                # Suspicious names
                suspicious_names = ['svchost', 'explorer', 'winlogon', 'csrss', 'lsass']
                if name not in suspicious_names and any(keyword in name for keyword in ['temp', 'tmp', 'cache', 'update']):
                    suspicious_flags.append("Suspicious name pattern")
                
                # Suspicious locations
                if exe:
                    suspicious_locations = ['temp', 'tmp', 'appdata\\local\\temp', 'downloads']
                    if any(loc in exe.lower() for loc in suspicious_locations):
                        suspicious_flags.append("Running from suspicious location")
                
                if suspicious_flags:
                    suspicious_processes.append({
                        "pid": proc_info['pid'],
                        "name": proc_info['name'],
                        "exe": exe,
                        "flags": suspicious_flags,
                        "risk_level": "medium" if len(suspicious_flags) < 2 else "high"
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Scan common malware locations
        malware_locations = [
            os.path.join(os.environ.get("TEMP", ""), ""),
            os.path.join(os.environ.get("APPDATA", ""), ""),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", ""),
        ]
        
        for location in malware_locations:
            if os.path.exists(location):
                try:
                    for root, dirs, files in os.walk(location):
                        for file in files[:50]:  # Limit scan
                            file_path = os.path.join(root, file)
                            file_lower = file.lower()
                            
                            # Check for suspicious extensions
                            suspicious_extensions = ['.exe', '.bat', '.cmd', '.scr', '.vbs']
                            if any(file_lower.endswith(ext) for ext in suspicious_extensions):
                                suspicious_files.append({
                                    "path": file_path,
                                    "name": file,
                                    "risk_level": "low"
                                })
                except:
                    pass
        
        # Calculate risk score
        risk_score = min(1.0, (len(suspicious_processes) * 0.1 + len(suspicious_files) * 0.05))
        
        return {
            "success": True,
            "scan_type": "heuristic",
            "risk_score": round(risk_score, 2),
            "risk_level": "low" if risk_score < 0.3 else "medium" if risk_score < 0.6 else "high",
            "suspicious_processes": suspicious_processes[:20],  # Limit results
            "suspicious_files": suspicious_files[:20],
            "total_threats": len(suspicious_processes) + len(suspicious_files),
            "recommendation": "Run a full antivirus scan" if risk_score > 0.5 else "System appears clean"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

