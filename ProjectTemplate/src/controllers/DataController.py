from fastapi import UploadFile
from .BaseController import BaseController

class DataController(BaseController):
    def __init__(self):
        super().__init__()
        # دي حسبة بسيطة عشان نحول الميجا بايت لـ بايت 
        # (1024 * 1024) = 1048576
        self.size_scale = 1048576 
        
    def validate_file(self, file: UploadFile) -> tuple[bool, str]:
        """
        بتتأكد إن الملف المرفوع نوعه وحجمه مسموح بيهم في الإعدادات
        """
        # 1. فحص نوع الملف (هل هو PDF أو TXT زي ما حددنا في الـ .env؟)
        if file.content_type not in self.app_settings.FILE_ALLOWED_EXTENSIONS:
            return False, "نوع الملف غير مدعوم. يرجى رفع ملفات نصية أو PDF فقط."
            
        # 2. فحص حجم الملف
        # الخدعة هنا: بننقل مؤشر قراءة الملف للآخر عشان نعرف هو كام بايت
        file.file.seek(0, 2)
        file_size = file.file.tell() / self.size_scale
        
        # لازم نرجع المؤشر لأول الفايل تاني عشان الـ API يقدر يقراه ويحفظه بعدين
        file.file.seek(0)
        
        if file_size > self.app_settings.FILE_MAX_SIZE_MB:
            return False, f"حجم الملف أكبر من المسموح به ({self.app_settings.FILE_MAX_SIZE_MB} ميجابايت)."
            
        return True, "الملف سليم ومطابق للشروط."