"""
WizTree Disk Map Engine - Treemap visualization API
"""
from fastapi import APIRouter, Depends
from auth import get_current_active_user, User
from typing import Dict, List
import os
from pathlib import Path

router = APIRouter(prefix="/api", tags=["Disk Analysis"])


# Folders to skip to avoid hangs/permission issues
SKIP_FOLDERS = {
    'System Volume Information', '$RECYCLE.BIN', '$Recycle.Bin', 
    'Recovery', 'Documents and Settings', 'Config.Msi'
}

def get_directory_size_fast(path: str, max_depth: int = 1) -> int:
    """Get total size of directory with limited depth to avoid hangs"""
    total = 0
    try:
        # Quick check for skipped folders
        if os.path.basename(path) in SKIP_FOLDERS:
            return 0
            
        stack = [(path, 0)]
        while stack:
            curr_path, depth = stack.pop()
            if depth > max_depth:
                continue
            
            try:
                with os.scandir(curr_path) as it:
                    for entry in it:
                        try:
                            if entry.is_file(follow_symlinks=False):
                                total += entry.stat(follow_symlinks=False).st_size
                            elif entry.is_dir(follow_symlinks=False):
                                if entry.name not in SKIP_FOLDERS and depth < max_depth:
                                    stack.append((entry.path, depth + 1))
                        except (PermissionError, OSError):
                            pass
            except (PermissionError, OSError):
                pass
    except Exception:
        pass
    return total


def build_treemap(path: str, max_depth: int = 3, current_depth: int = 0, max_items: int = 40) -> Dict:
    """Build treemap structure recursively with strict limits and skip list"""
    try:
        name = os.path.basename(path) or path
        if name in SKIP_FOLDERS:
            return {"name": name, "path": path, "size": 0}

        if current_depth >= max_depth:
            return {"name": name, "path": path, "size": 0}

        items = []
        total_size = 0
        
        entries = []
        try:
            with os.scandir(path) as it:
                for entry in it:
                    if entry.name not in SKIP_FOLDERS:
                        entries.append(entry)
        except (PermissionError, OSError):
            return {"name": name, "path": path, "size": 0, "children": []}

        entry_data = []
        for entry in entries:
            try:
                if entry.is_file(follow_symlinks=False):
                    size = entry.stat(follow_symlinks=False).st_size
                else:
                    # Estimate directory size: 1 level deep for root items, 0 for others
                    depth_limit = 1 if current_depth == 0 else 0
                    size = get_directory_size_fast(entry.path, max_depth=depth_limit)
                
                entry_data.append((entry, size))
                total_size += size
            except (PermissionError, OSError):
                pass

        entry_data.sort(key=lambda x: x[1], reverse=True)
        top_entries = entry_data[:max_items]

        for entry, size in top_entries:
            item = {
                "name": entry.name,
                "size": size,
                "path": entry.path
            }
            
            # Recurse for directories
            if entry.is_dir(follow_symlinks=False) and current_depth < max_depth - 1:
                child_treemap = build_treemap(entry.path, max_depth, current_depth + 1, max_items // 2)
                if child_treemap and child_treemap.get("children"):
                    item["children"] = child_treemap["children"]
                    item["size"] = max(size, child_treemap.get("size", 0))
            
            items.append(item)

        return {
            "name": name,
            "path": path,
            "size": total_size,
            "children": items
        }
    except Exception:
        return {"name": os.path.basename(path) or path, "path": path, "size": 0, "children": []}


@router.get("/drives")
async def get_drives():
    """Get list of available logical drives (C:, D:, E:, etc.)"""
    import psutil
    drives = []
    try:
        for part in psutil.disk_partitions(all=False):
            if os.name == 'nt':
                # On Windows, partition device is like 'C:\\'
                drive_name = part.device.rstrip('\\')
                if drive_name:
                    drives.append(drive_name)
            else:
                drives.append(part.mountpoint)
        
        # Ensure C, D, E are present if they exist but weren't caught
        # (psutil misses some sometimes on certain setups)
        system_drives = ['C:', 'D:', 'E:']
        for sd in system_drives:
            if os.path.exists(sd + '\\') and sd not in drives:
                drives.append(sd)
                
        return {"success": True, "drives": sorted(list(set(drives)))}
    except Exception as e:
        return {"success": False, "error": str(e), "drives": ["C:", "D:"]}


@router.get("/disk-map")
async def get_disk_map(
    drive: str = "C:",
    max_depth: int = 3
):
    """Optimized disk map API with system folder skipping"""
    try:
        drive = drive.strip()
        if len(drive) == 1:
            drive = drive + ":"
        
        drive_path = drive + "\\" if os.name == 'nt' else drive + "/"
        
        if not os.path.exists(drive_path):
            return {"success": False, "error": f"Drive {drive} not found"}
        
        import psutil
        try:
            disk_usage = psutil.disk_usage(drive_path)
            stats = {"total": disk_usage.total, "used": disk_usage.used, "free": disk_usage.free}
        except:
            stats = {"total": 0, "used": 0, "free": 0}
        
        # Reduced max_items at root for faster initial response
        treemap = build_treemap(drive_path, max_depth=min(max_depth, 3), max_items=50)
        
        return {
            "success": True,
            "drive": drive,
            "total_size": stats["total"],
            "used_size": stats["used"],
            "free_size": stats["free"],
            "treemap": treemap
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

