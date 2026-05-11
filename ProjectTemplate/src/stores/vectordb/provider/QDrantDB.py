from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from ..VectorDBInterface import VectorDBInterface
from helpers import get_settings
from controllers.BaseController import BaseController
from models.db_schemes.data_chunk import RetrievalDocument

class QDrantDB(VectorDBInterface):
    def __init__(self):
        self.settings = get_settings()
        # هنجيب المسار اللي هنحفظ فيه قاعدة البيانات من الـ BaseController
        base_ctrl = BaseController()
        db_path = base_ctrl.get_db_path(self.settings.VECTOR_DB_PATH)
        
        # إنشاء الاتصال بقاعدة البيانات (وحفظها في الهارد ديسك)
        self.client = QdrantClient(url="http://qdrant_service:6333")
        self.dimension = self.settings.EMBEDDING_DIMENSION

    def create_collection(self, collection_name: str):
        # التأكد الأول إن الـ Collection مش موجود عشان منعملوش مرتين
        collections = self.client.get_collections().collections
        if not any(c.name == collection_name for c in collections):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=self.dimension, distance=Distance.COSINE)
            )

    def add_documents(self, collection_name: str, chunks: list, embeddings: list):
        points = []
        for idx, chunk in enumerate(chunks):
            # Qdrant بيحتاج البيانات في شكل (PointStruct)
            points.append(PointStruct(
                id=idx, # رقم تعريفي مميز
                vector=embeddings[idx], # الـ Vector (الأرقام)
                payload={ # الـ Payload ده اللي بيشيل النص والـ Metadata
                    "text": chunk["chunk_text"], 
                    "metadata": chunk["chunk_metadata"]
                }
            ))
        # الحفظ الفعلي
        self.client.upsert(collection_name=collection_name, points=points)

    def search_by_vector(self, collection_name: str, vector: list, limit: int = 5) -> list[RetrievalDocument]:
        # التحديث الجديد لـ Qdrant بيستخدم query_points بدل search القديمة
        response = self.client.query_points(
            collection_name=collection_name,
            query=vector,
            limit=limit
        )
        
        results = []
        # النتائج بتبقى موجودة جوه response.points
        for hit in response.points:
            # تغليف النتيجة في الـ Schema اللي عملناها قبل كده
            results.append(RetrievalDocument(text=hit.payload["text"], score=hit.score))
        return results