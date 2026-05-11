from motor.motor_asyncio import AsyncIOMotorClient
from helpers import get_settings

class DataBaseModel:
    def __init__(self):
        self.app_settings = get_settings()
        
        # فتح الاتصال مع MongoDB باستخدام المسار اللي في ملف .env
        self.db_client = AsyncIOMotorClient(self.app_settings.MONGODB_URI)
        
        # اختيار قاعدة البيانات (mini_rag)
        self.db = self.db_client[self.app_settings.MONGODB_DB_NAME]