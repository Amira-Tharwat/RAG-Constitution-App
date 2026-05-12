import os
from helpers import get_settings

class BaseController:
    def __init__(self):
        self.app_settings = get_settings()
        
        
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
       
        self.assets_dir = os.path.join(self.base_dir, "assets")
        self.file_dir = os.path.join(self.assets_dir, "files")
        self.db_dir = os.path.join(self.assets_dir, "db")
        
    def get_db_path(self, db_name: str) -> str:
        
        db_path = os.path.join(self.db_dir, db_name)
        
        if not os.path.exists(db_path):
            os.makedirs(db_path)
            
        return db_path