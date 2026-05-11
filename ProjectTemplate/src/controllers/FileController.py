import os
from .BaseController import BaseController

class FileController(BaseController):
    def __init__(self):
        # السطر ده معناه "يا أب، شغل دالة الـ __init__ بتاعتك الأول عشان تجيبلي الإعدادات والمسارات"
        super().__init__()
        
    def get_file_path(self, project_id: str) -> str:
        """
        بتعمل فولدر خاص بكل مشروع بناءً على اسمه أو الـ ID بتاعه
        """
        # دمج مسار الفولدر الرئيسي للملفات مع اسم المشروع
        project_dir = os.path.join(self.file_dir, project_id)
        
        # لو الفولدر مش موجود، اعمله
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
            
        return project_dir