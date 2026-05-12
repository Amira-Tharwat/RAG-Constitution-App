from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from ..VectorDBInterface import VectorDBInterface
from helpers import get_settings
from controllers.BaseController import BaseController
from models.db_schemes.data_chunk import RetrievalDocument

class QDrantDB(VectorDBInterface):
    def __init__(self):
        self.settings = get_settings()
        # هنجيب الباث اللي هنحفظ فيه  البيانات من الـ BaseController
        base_ctrl = BaseController()
        db_path = base_ctrl.get_db_path(self.settings.VECTOR_DB_PATH)
        
        #  انشاء كونيكشن
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
            points.append(PointStruct(
                id=idx,
                vector=embeddings[idx], 
                payload={ # الـ Payload ده اللي بيشيل النص والـ Metadata
                    "text": chunk["chunk_text"], 
                    "metadata": chunk["chunk_metadata"]
                }
            ))
       
        self.client.upsert(collection_name=collection_name, points=points)

    def search_by_vector(self, collection_name: str, vector: list, limit: int = 5) -> list[RetrievalDocument]:\
     # بتاخد فيكتور السؤال و تدور علي ال top chunks (5)
        response = self.client.query_points(
            collection_name=collection_name,
            query=vector,
            limit=limit
        )
        
        results = []
        for hit in response.points:
            results.append(RetrievalDocument(text=hit.payload["text"], score=hit.score))
        return results