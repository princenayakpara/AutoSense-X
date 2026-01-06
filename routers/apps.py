"""
Revo Uninstaller Pro - App Management API
"""
from fastapi import APIRouter, Depends, HTTPException
from auth import get_current_active_user, User
from typing import List, Dict
import os
import subprocess
import winreg
from pathlib import Path

router = APIRouter(prefix="/api/apps", tags=["App Management"])


def get_installed_apps_windows() -> List[Dict]:
    """Get list of installed applications on Windows"""
    apps = []
    
    # Registry keys for installed programs
    registry_keys = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]
    
    for hkey, subkey in registry_keys:
        try:
            key = winreg.OpenKey(hkey, subkey)
            i = 0
            while True:
                try:
                    app_key_name = winreg.EnumKey(key, i)
                    app_key = winreg.OpenKey(key, app_key_name)
                    
                    app_info = {}
                    try:
                        app_info["name"] = winreg.QueryValueEx(app_key, "DisplayName")[0]
                    except:
                        app_info["name"] = app_key_name
                    
                    try:
                        app_info["version"] = winreg.QueryValueEx(app_key, "DisplayVersion")[0]
                    except:
                        app_info["version"] = "Unknown"
                    
                    try:
                        app_info["publisher"] = winreg.QueryValueEx(app_key, "Publisher")[0]
                    except:
                        app_info["publisher"] = "Unknown"
                    
                    try:
                        app_info["install_date"] = winreg.QueryValueEx(app_key, "InstallDate")[0]
                    except:
                        app_info["install_date"] = None
                    
                    try:
                        app_info["uninstall_string"] = winreg.QueryValueEx(app_key, "UninstallString")[0]
                    except:
                        app_info["uninstall_string"] = None
                    
                    try:
                        app_info["install_location"] = winreg.QueryValueEx(app_key, "InstallLocation")[0]
                    except:
                        app_info["install_location"] = None
                    
                    try:
                        size = winreg.QueryValueEx(app_key, "EstimatedSize")[0]
                        app_info["size_mb"] = size if size else 0
                    except:
                        app_info["size_mb"] = 0
                    
                    app_info["registry_key"] = app_key_name
                    
                    if app_info["name"] and app_info["name"] not in [a["name"] for a in apps]:
                        apps.append(app_info)
                    
                    winreg.CloseKey(app_key)
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except Exception as e:
            pass
    
    return sorted(apps, key=lambda x: x["name"].lower())


@router.get("")
async def get_installed_apps(
    current_user: User = Depends(get_current_active_user)
):
    """Get list of all installed applications"""
    try:
        if os.name == 'nt':
            apps = get_installed_apps_windows()
        else:
            # For Linux/Mac, use alternative methods
            apps = []
        
        return {
            "success": True,
            "apps": apps,
            "count": len(apps)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{app_name}/remove")
async def smart_uninstall(
    app_name: str,
    current_user: User = Depends(get_current_active_user)
):
    """Smart uninstall application"""
    try:
        # Find app in registry
        apps = get_installed_apps_windows()
        app = next((a for a in apps if a["name"].lower() == app_name.lower()), None)
        
        if not app:
            raise HTTPException(status_code=404, detail="Application not found")
        
        uninstall_string = app.get("uninstall_string")
        if not uninstall_string:
            raise HTTPException(status_code=400, detail="No uninstall string found")
        
        # Execute uninstall
        try:
            # Handle quoted paths
            if uninstall_string.startswith('"'):
                parts = uninstall_string.split('"')
                exe = parts[1]
                args = parts[2].strip() if len(parts) > 2 else ""
            else:
                parts = uninstall_string.split()
                exe = parts[0]
                args = " ".join(parts[1:])
            
            subprocess.Popen([exe, args] if args else [exe], shell=True)
            
            return {
                "success": True,
                "message": f"Uninstall process started for {app_name}",
                "app": app
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to start uninstall: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{app_name}/leftovers")
async def scan_leftovers(
    app_name: str,
    current_user: User = Depends(get_current_active_user)
):
    """Scan for leftover files and registry entries after uninstall"""
    try:
        apps = get_installed_apps_windows()
        app = next((a for a in apps if a["name"].lower() == app_name.lower()), None)
        
        if not app:
            raise HTTPException(status_code=404, detail="Application not found")
        
        leftovers = {
            "files": [],
            "folders": [],
            "registry_entries": []
        }
        
        # Check install location
        install_location = app.get("install_location")
        if install_location and os.path.exists(install_location):
            leftovers["folders"].append({
                "path": install_location,
                "type": "install_directory"
            })
        
        # Common leftover locations
        common_paths = [
            os.path.join(os.environ.get("APPDATA", ""), app_name),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), app_name),
            os.path.join(os.environ.get("PROGRAMDATA", ""), app_name),
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                leftovers["folders"].append({
                    "path": path,
                    "type": "data_directory"
                })
        
        return {
            "success": True,
            "app_name": app_name,
            "leftovers": leftovers,
            "count": len(leftovers["files"]) + len(leftovers["folders"]) + len(leftovers["registry_entries"])
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{app_name}/force")
async def force_remove(
    app_name: str,
    current_user: User = Depends(get_current_active_user)
):
    """Force remove application and all leftovers"""
    try:
        # First, try smart uninstall
        uninstall_result = await smart_uninstall(app_name, current_user)
        
        # Then scan and remove leftovers
        leftovers_result = await scan_leftovers(app_name, current_user)
        
        removed_items = []
        
        # Remove leftover folders
        for folder in leftovers_result["leftovers"]["folders"]:
            folder_path = folder["path"]
            if os.path.exists(folder_path):
                try:
                    import shutil
                    shutil.rmtree(folder_path, ignore_errors=True)
                    removed_items.append(f"Removed folder: {folder_path}")
                except Exception as e:
                    removed_items.append(f"Failed to remove {folder_path}: {str(e)}")
        
        return {
            "success": True,
            "message": f"Force removal initiated for {app_name}",
            "uninstall_started": uninstall_result["success"],
            "leftovers_removed": len(removed_items),
            "removed_items": removed_items
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

