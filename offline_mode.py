"""
Offline Fallback Mode - Cache system data when offline
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
import psutil

class OfflineMode:
    """Offline mode with local caching"""
    
    def __init__(self, cache_dir: str = "./cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_expiry = timedelta(minutes=5)
    
    def get_cached_data(self, key: str) -> Optional[Dict]:
        """Get cached data if not expired"""
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            # Check expiry
            cached_time = datetime.fromisoformat(data.get('timestamp', ''))
            if datetime.now() - cached_time > self.cache_expiry:
                return None
            
            return data.get('data')
        except Exception:
            return None
    
    def cache_data(self, key: str, data: Dict):
        """Cache data with timestamp"""
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        
        cache_entry = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_entry, f, indent=2)
        except Exception as e:
            print(f"Error caching data: {e}")
    
    def get_system_info_offline(self) -> Dict:
        """Get system info from cache or current system"""
        cached = self.get_cached_data('system_info')
        if cached:
            return cached
        
        # Get fresh data
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            system_info = {
                "success": True,
                "system": {
                    "cpu_count": psutil.cpu_count(),
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory_total_gb": round(memory.total / (1024**3), 2),
                    "memory_used_gb": round(memory.used / (1024**3), 2),
                    "memory_percent": memory.percent,
                    "disk_total_gb": round(disk.total / (1024**3), 2),
                    "disk_used_gb": round(disk.used / (1024**3), 2),
                    "disk_percent": disk.percent
                }
            }
            
            self.cache_data('system_info', system_info)
            return system_info
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def clear_cache(self):
        """Clear all cached data"""
        try:
            for file in os.listdir(self.cache_dir):
                if file.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, file))
        except Exception as e:
            print(f"Error clearing cache: {e}")

