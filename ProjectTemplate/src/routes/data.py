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
    #  نتأكد ان التايب فاليد pdf
    data_controller = DataController()
    is_valid, msg = data_controller.validate_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=msg)

    # نعمل البروجيكت ف ال mongo db
    project_model = ProjectModel()
    await project_model.get_project_or_create_one(project_id)

    # نعمل dir نحط فيه الفايل
    file_controller = FileController()
    project_dir = file_controller.get_file_path(project_id)
    file_path = os.path.join(project_dir, file.filename)
    

    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    return {"message": "تم رفع الملف بنجاح", "file_name": file.filename}

@data_router.post("/process/{project_id}")
async def process_file(project_id: str, file_name: str):
    # نعمل بري بروسيسينج 
    process_controller = ProcessController(project_id)
    chunks = process_controller.process_files(file_name)
    
    if not chunks:
        raise HTTPException(status_code=400, detail="فشل تقطيع الملف أو الملف غير موجود")

    # نجط المواد ف ال mongo db
    chunk_model = ChunkModel()
    
    await chunk_model.delete_chunks_by_project_id(project_id)
    
    data_chunks = [DataChunk(**chunk, chunk_project_id=project_id) for chunk in chunks]
    inserted_count = await chunk_model.insert_many_chunks(data_chunks)
    
    return {"message": f"تم تقطيع وحفظ {inserted_count} مادة دستورية بنجاح"}