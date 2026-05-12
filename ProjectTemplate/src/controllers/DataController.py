from fastapi import UploadFile
from .BaseController import BaseController

class DataController(BaseController):
    def __init__(self):
        super().__init__()

        # (1024 * 1024) = 1048576
        self.size_scale = 1048576 
        
    def validate_file(self, file: UploadFile) -> tuple[bool, str]:
        """
             نتأكد من تايب و سايز الفايل 
        """
        if file.content_type not in self.app_settings.FILE_ALLOWED_EXTENSIONS:
            return False, "نوع الملف غير مدعوم. يرجى رفع ملفات نصية أو PDF فقط."
            
        
        file.file.seek(0, 2)
        file_size = file.file.tell() / self.size_scale
        
        file.file.seek(0)
        
        if file_size > self.app_settings.FILE_MAX_SIZE_MB:
            return False, f"حجم الملف أكبر من المسموح به ({self.app_settings.FILE_MAX_SIZE_MB} ميجابايت)."
            
        return True, "الملف سليم ومطابق للشروط."