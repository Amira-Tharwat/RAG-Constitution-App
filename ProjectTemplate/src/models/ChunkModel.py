from .DataBaseModel import DataBaseModel
from .db_schemes.data_chunk import DataChunk

class ChunkModel(DataBaseModel):
    def __init__(self):
        super().__init__()
        # اختيار الـ Collection اللي اسمه chunks
        self.collection = self.db["chunks"]

    async def insert_many_chunks(self, chunks: list[DataChunk]) -> int:
        """حفظ مجموعة كبيرة من الـ chunks دفعة واحدة"""
        if not chunks:
            return 0
        
        # تحويل القائمة لـ Dictionaries
        docs = [chunk.model_dump(by_alias=True, exclude={"id"}) for chunk in chunks]
        result = await self.collection.insert_many(docs)
        
        # إرجاع عدد العناصر اللي تم حفظها
        return len(result.inserted_ids)

    async def delete_chunks_by_project_id(self, project_id: str) -> int:
        """مسح كل الـ chunks الخاصة بمشروع معين (مفيدة لو هنعمل Update أو Reset)"""
        result = await self.collection.delete_many({"chunk_project_id": project_id})
        return result.deleted_count

    async def get_chunks_by_project_id(self, project_id: str) -> list[DataChunk]:
        """استرجاع كل الـ chunks الخاصة بمشروع مترتبة حسب ترتيبها الأصلي"""
        cursor = self.collection.find({"chunk_project_id": project_id}).sort("chunk_order", 1)
        
        chunks = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            chunks.append(DataChunk(**doc))
            
        return chunks