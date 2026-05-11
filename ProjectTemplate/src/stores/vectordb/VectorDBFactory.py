from .provider.QDrantDB import QDrantDB

class VectorDBFactory:
    @staticmethod
    def get_vectordb(provider: str = "qdrant"):
        if provider == "qdrant":
            return QDrantDB()
        return None