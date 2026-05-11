import os
import aiofiles
from fastapi import APIRouter, UploadFile, File, HTTPException
from controllers.DataController import DataController
from controllers.FileController import FileController
from controllers.ProcessController import ProcessController
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.db_schemes.data_chunk import DataChunk

data_router = APIRouter(prefix="/api/data", tags=["Data"])

@data_router.post("/upload/{project_id}")
async def upload_file(project_id: str, file: UploadFile = File(...)):
    # 1. التحقق من أمان الملف
    data_controller = DataController()
    is_valid, msg = data_controller.validate_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=msg)

    # 2. إنشاء المشروع في قاعدة البيانات
    project_model = ProjectModel()
    await project_model.get_project_or_create_one(project_id)

    # 3. حفظ الملف في الفولدر الخاص بالمشروع
    file_controller = FileController()
    project_dir = file_controller.get_file_path(project_id)
    file_path = os.path.join(project_dir, file.filename)
    
    # استخدام aiofiles للحفظ بشكل غير متزامن (سريع)
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    return {"message": "تم رفع الملف بنجاح", "file_name": file.filename}

@data_router.post("/process/{project_id}")
async def process_file(project_id: str, file_name: str):
    # 1. تقطيع الملف باستخدام الـ Controller الخاص بنا
    process_controller = ProcessController(project_id)
    chunks = process_controller.process_files(file_name)
    
    if not chunks:
        raise HTTPException(status_code=400, detail="فشل تقطيع الملف أو الملف غير موجود")

    # 2. حفظ المواد الدستورية المقطعة في MongoDB
    chunk_model = ChunkModel()
    
    # مسح أي مواد قديمة لنفس المشروع (عشان التكرار)
    await chunk_model.delete_chunks_by_project_id(project_id)
    
    # تحضير البيانات وحفظها
    data_chunks = [DataChunk(**chunk, chunk_project_id=project_id) for chunk in chunks]
    inserted_count = await chunk_model.insert_many_chunks(data_chunks)
    
    return {"message": f"تم تقطيع وحفظ {inserted_count} مادة دستورية بنجاح"}