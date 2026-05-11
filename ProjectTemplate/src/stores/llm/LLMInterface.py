from abc import ABC, abstractmethod

class LLMInterface(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """دالة توليد الإجابات من النص"""
        pass

    @abstractmethod
    def embed_text(self, text: str, document_type: str = "") -> list[float]:
        """دالة تحويل النص إلى Vectors (أرقام)"""
        pass