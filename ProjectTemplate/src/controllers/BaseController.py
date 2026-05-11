import os
from helpers import get_settings

class BaseController:
    def __init__(self):
        # 1. جلب الإعدادات اللي عملناها في الخطوة اللي فاتت
        self.app_settings = get_settings()
        
        # 2. تحديد المسار الرئيسي للمشروع (مسار فولدر src)
        # os.path.dirname بيجيب مسار الفولدر اللي جواه الملف الحالي
        # وبما إننا جوه فولدر controllers، هنرجع خطوة لورا عشان نوصل لـ src
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 3. تحديد مسار الفولدرات اللي هنحفظ فيها الملفات (assets)
        self.assets_dir = os.path.join(self.base_dir, "assets")
        self.file_dir = os.path.join(self.assets_dir, "files")
        self.db_dir = os.path.join(self.assets_dir, "db")
        
    def get_db_path(self, db_name: str) -> str:
        """
        دالة بتعمل مسار جديد لقاعدة البيانات جوه فولدر assets/db/
        ولو الفولدر مش موجود بتنشئه تلقائياً
        """
        db_path = os.path.join(self.db_dir, db_name)
        
        # التأكد من إنشاء الفولدر لو مش موجود
        if not os.path.exists(db_path):
            os.makedirs(db_path)
            
        return db_path