from .provider.GeminiProvider import GeminiProvider
from .provider.GroqProvider import GroqProvider
from .provider.EmbeddingProvider import EmbeddingProvider # ضفنا دي هنا

class LLMFactory:
    @staticmethod
    def get_llm(provider_name: str):
        provider_name = provider_name.lower()
        
        if provider_name == "gemini":
            return GeminiProvider()
        elif provider_name == "groq": 
            return GroqProvider()
        else:
            raise ValueError(f"الموديل '{provider_name}' غير مدعوم.")

    @staticmethod
    def get_embedding_provider(provider_name: str):
        if provider_name == "local":
            return EmbeddingProvider()
        else:
            raise ValueError(f"Embedding provider '{provider_name}' غير مدعوم.")