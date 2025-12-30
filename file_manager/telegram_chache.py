from threading import Lock
import os
import json
class TelegramCache:
    def __init__(self, cache_path:str = "config/telegram_cache.json"):
        self.cache_path = cache_path
        self._lock = Lock()
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                self.cache = json.load(f)
        else:
            self.cache = {}
            self._save()
    
    def _save(self):
        '''
        Saves the current cache to the JSON file.
        
        :param self: Instance of TelegramCache
        '''
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, indent=4)
    
    def get(self, drive_id:str):
        '''
        Retrieves the cached telegram file ID for a given drive unique ID if it exists else None.
        
        :param self: Instance of TelegramCache
        :param drive_id: Unique identifier of the drive file
        :type drive_id: str
        '''
        return self.cache.get(drive_id)
    
    def set(self, drive_id:str, telegram_file_id:str):
         """Store a mapping drive_id → telegram file_id."""
         with self._lock:
             self.cache[drive_id] = telegram_file_id
             self._save()
    def is_cached(self, drive_id:str) -> bool:
        return drive_id in self.cache
        