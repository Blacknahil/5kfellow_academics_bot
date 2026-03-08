import os
import redis
class TelegramCache:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            raise RuntimeError("REDIS_URL environment variable is not set.")
        # decode_responses=True returns strings instead of bytes
        self.client = redis.from_url(redis_url, decode_responses=True)
        print("Initialized TelegramCache with Redis")
    
    def _key(self, drive_id:str) -> str:
        """Namespace Redis keys to avoid collisions."""
        return f"telegram_cache:{drive_id}"
    
    def get(self, drive_id:str):
        """
        Retrieve cached telegram file ID for a given drive ID.
        """
        return self.client.get(self._key(drive_id))
    
    def set(self, drive_id:str, telegram_file_id:str):
        """Store a mapping drive_id → telegram file_id."""
        self.client.set(self._key(drive_id), telegram_file_id)
        
    def is_cached(self, drive_id:str) -> bool:
        """
        Check if drive_id already exists in cache.
        """
        return self.client.exists(self._key(drive_id)) == 1
        