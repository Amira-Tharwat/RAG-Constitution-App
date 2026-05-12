from .DataBaseModel import DataBaseModel
from .db_schemes.data_chunk import DataChunk

class ChunkModel(DataBaseModel):
    def __init__(self):
        super().__init__()
        # اختيار الـ Collection اللي اسمه chunks
        self.collection = self.db["chunks"]

    async def insert_many_chunks(self, chunks: list[DataChunk]) -> int:
        """حفظ الـ chunks مرة واحدة"""
        if not chunks:
            return 0
        
        # التحويل  لـ Dictionaries
        docs = [chunk.model_dump(by_alias=True, exclude={"id"}) for chunk in chunks]
        result = await self.collection.insert_many(docs)
        
       
        return len(result.inserted_ids)

    async def delete_chunks_by_project_id(self, project_id: str) -> int:
        result = await self.collection.delete_many({"chunk_project_id": project_id})
        return result.deleted_count

    async def get_chunks_by_project_id(self, project_id: str) -> list[DataChunk]:
        """بترجع ال chunks كلها"""
        cursor = self.collection.find({"chunk_project_id": project_id}).sort("chunk_order", 1)
        
        chunks = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            chunks.append(DataChunk(**doc))
            
        return chunks