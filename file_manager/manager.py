from .telegram_chache import TelegramCache
from file_manager import download_file
import os 
from utils import FileSent

TELEGRAM_CACHE_PATH = "config/telegram_cache.json"
class FileManager:
    def __init__(self, bot, drive_service):
        '''
            Initializes the FileManager with a Telegram bot, Google Drive service, and cache path.
        '''
        self.bot = bot
        self.cache = TelegramCache(TELEGRAM_CACHE_PATH)
        self.drive = drive_service
         
    async def get_file(self, chat_id, drive_id:str):
        cached_id = self.cache.get(drive_id)
        if cached_id:
            
            return FileSent(telegram_file_id= cached_id, status = False)
        #  download from drive 
        local_path = await download_file(self.drive, drive_id, TELEGRAM_CACHE_PATH)
        msg = await self.bot.send_document(
            chat_id = chat_id,
            document = open(local_path, 'rb')
        )
        telegram_id = msg.document.file_id
        #  save in cache 
        self.cache.set(drive_id, telegram_id)

        try:
            os.remove(local_path)
        except Exception as e:
            print(f"Failed to delete temp file {local_path} with error: {e}")
        
        return FileSent(telegram_file_id= telegram_id, status = True)
         