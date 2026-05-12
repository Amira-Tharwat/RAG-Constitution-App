from fastembed import TextEmbedding
from ..LLMInterface import LLMInterface
from helpers import get_settings

class EmbeddingProvider(LLMInterface):
    def __init__(self):
        self.settings = get_settings()
        self.model = TextEmbedding(model_name=self.settings.EMBEDDINGS_MODEL)

    def embed_text(self, text: str, document_type: str = "") -> list[float]:
        
        embedding = list(self.model.embed([text]))[0]
        return embedding.tolist()

    def generate_response(self, prompt: str) -> str:
        pass