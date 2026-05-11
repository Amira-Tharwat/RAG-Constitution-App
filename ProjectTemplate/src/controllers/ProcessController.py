import os
import re
import fitz  # PyMuPDF
from .BaseController import BaseController
from .FileController import FileController

class ProcessController(BaseController):
    def __init__(self, project_id: str):
        super().__init__()
        self.project_id = project_id
        self.file_controller = FileController()

    def _extract_and_normalize_pdf(self, pdf_path: str) -> str:
        """
        دالة خاصة لاستخراج النص من الـ PDF مع قص الهوامش وتطبيع النص العربي
        """
        doc = fitz.open(pdf_path)
        full_text = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # قص الهوامش العلوية والسفلية
            rect = page.rect
            clip_rect = fitz.Rect(0, 50, rect.width, rect.height - 60)
            full_text += page.get_text("text", clip=clip_rect) + " "
            
        # خوارزمية التطبيع (Text Normalization)
        text = full_text.replace('\n', ' ')
        text = text.replace('األ', 'الأ').replace('اإل', 'الإ').replace('اآل', 'الآ')
        text = text.replace('ـ', '')
        
        text = re.sub(r'(\S)\s+ى\b', r'\1ى', text)
        text = re.sub(r'(\S)\s+ي\b', r'\1ي', text)
        text = text.replace('ال مادة', 'المادة')
       
        # تنظيف بقايا الهوامش
        text = text.replace('مكرر ا', 'مكررا')
        text = re.sub(r'ا?\s*ل\s*ب\s*ا\s*ب', 'الباب', text)
        text = re.sub(r'ا?\s*ل\s*ف\s*ص\s*ل', 'الفصل', text)
        
        arabic_to_english = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
        def fix_arabic_numbers(match):
            return match.group(0)[::-1].translate(arabic_to_english)
        text = re.sub(r'[٠-٩]+', fix_arabic_numbers, text)
        
        text = re.sub(r'م\s*ا\s*د\s*ة', 'مادة', text)
        text = re.sub(r'\s+', ' ', text)
        
        # قص الفهرس النهائي
        text = re.split(r'ا?\s*ل\s*ف\s*ه\s*ر\s*س', text)[0]
        
        return text

    def _chunk_by_article(self, text: str) -> list:
        """
        دالة خاصة لتقطيع النص إلى مواد دستورية واستخراج الميتا داتا
        """
        pattern = r'[\(\)]*\s*(?<![ء-ي])مادة\s*[\(\)]*\s*\d+\s*(?:مكرر[ااً]?)?\s*[\(\)]*'
        matches = list(re.finditer(pattern, text))
        
        chunks_with_metadata = []
        current_bab = "غير محدد"
        current_fasl = "بدون فصل"
        
        for i in range(len(matches)):
            start_idx = matches[i].start()
            end_idx = matches[i+1].start() if i + 1 < len(matches) else len(text)
            
            if i == 0:
                pre_text = text[:start_idx]
            else:
                pre_text = text[matches[i-1].end():start_idx]
                
            pre_text = pre_text.replace('ا ل', 'ال')
                
            search_window = pre_text[-150:] if len(pre_text) > 150 else pre_text
            
            bab_pattern = r'(الباب\s+(?:الأول|الثانى|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع|العاشر|الحادى\s*عشر))\s*(.{0,60}?)(?=\s*(?:الفصل|الفرع|مادة|الباب|$))'
            bab_match = re.search(bab_pattern, search_window)
            if bab_match:
                bab_num = bab_match.group(1).strip()
                bab_name = bab_match.group(2).replace(':', '').replace('-', '').strip()
                current_bab = f"{bab_num} ({bab_name})" if bab_name else bab_num
                current_fasl = "بدون فصل" 
                
            fasl_pattern = r'(الفصل\s+(?:الأول|الثانى|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع|العاشر|الحادى\s*عشر))\s*(.{0,60}?)(?=\s*(?:الفرع|مادة|الفصل|الباب|$))'
            fasl_match = re.search(fasl_pattern, search_window)
            if fasl_match:
                fasl_num = fasl_match.group(1).strip()
                fasl_name = fasl_match.group(2).replace(':', '').replace('-', '').strip()
                current_fasl = f"{fasl_num} ({fasl_name})" if fasl_name else fasl_num
                    
            chunk_text = text[start_idx:end_idx].strip()
            
            bab_end_match = re.search(r'\s+(الباب\s+(?:الأول|الثانى|الثالث|الرابع|الخامس|السادس|السابع)).*', chunk_text)
            if bab_end_match and bab_end_match.start() > len(chunk_text) - 150:
                chunk_text = chunk_text[:bab_end_match.start()]
                
            fasl_end_match = re.search(r'\s+(الفصل\s+(?:الأول|الثانى|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع|العاشر|الحادى\s*عشر)).*', chunk_text)
            if fasl_end_match and fasl_end_match.start() > len(chunk_text) - 150:
                chunk_text = chunk_text[:fasl_end_match.start()]
            
            if chunk_text:
                chunks_with_metadata.append({
                    "id": f"article_{i+1}",
                    "bab": current_bab,
                    "fasl": current_fasl,
                    "text": chunk_text.strip()
                })
                
        return chunks_with_metadata

    def process_files(self, filename: str):
        """
        المسار الأساسي للمعالجة، يستخدم الدوال الخاصة لإرجاع البيانات 
        بالتنسيق الذي تقبله قاعدة البيانات (MongoDB & Qdrant)
        """
        project_dir = self.file_controller.get_file_path(self.project_id)
        file_path = os.path.join(project_dir, filename)

        if not os.path.exists(file_path):
            return None

        # 1. استخراج النص وتنظيفه
        normalized_text = self._extract_and_normalize_pdf(file_path)

        # 2. التقطيع الدلالي (Semantic Chunking)
        article_chunks = self._chunk_by_article(normalized_text)

        # 3. تحضير المخرجات لتناسب الـ Models القادمة
        formatted_chunks = []
        for idx, chunk in enumerate(article_chunks):
            formatted_chunks.append({
                "chunk_text": chunk["text"],
                "chunk_metadata": {
                    "source": filename,
                    "bab": chunk["bab"],
                    "fasl": chunk["fasl"],
                    "article_id": chunk["id"]
                },
                "chunk_order": idx + 1
            })

        return formatted_chunks