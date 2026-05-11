from abc import ABC, abstractmethod

class VectorDBInterface(ABC):
    @abstractmethod
    def create_collection(self, collection_name: str):
        """إنشاء جدول جديد (Collection) في قاعدة البيانات"""
        pass

    @abstractmethod
    def add_documents(self, collection_name: str, chunks: list, embeddings: list):
        """إضافة النصوص والأرقام المعبرة عنها (Vectors)"""
        pass

    @abstractmethod
    def search_by_vector(self, collection_name: str, vector: list, limit: int) -> list:
        """البحث باستخدام الأرقام (Vector Search)"""
        pass