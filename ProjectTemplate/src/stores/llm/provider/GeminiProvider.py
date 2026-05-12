import os
from google import genai
from ..LLMInterface import LLMInterface
from helpers.config import get_settings

class GeminiProvider(LLMInterface):
    def __init__(self):
        self.settings = get_settings()
        api_key = os.environ.get("GEMINI_API_KEY")
        self.model_name = os.environ.get("GENERATE_RESPONSE_MODEL", "gemini-2.5-flash")
        
        self.client = genai.Client(api_key=api_key)

    def generate_response(self, prompt: str) -> str:
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"عذراً، حدث خطأ في الاتصال بسيرفرات جوجل: {e}"

    def embed_text(self, text: str, document_type: str = "") -> list[float]:
        pass