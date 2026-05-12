import os
import requests
from ..LLMInterface import LLMInterface
from helpers.config import get_settings 

class GroqProvider(LLMInterface):
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.GROQ_API_KEY 
        self.model_name = "llama-3.1-8b-instant" 
        self.url = "https://api.groq.com/openai/v1/chat/completions"

    def generate_response(self, prompt: str) -> str:
        if not self.api_key:
            return "خطأ: مفتاح Groq API غير موجود في الإعدادات."
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }
        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=10)
            
            if response.status_code != 200:
                try:
                    error_details = response.json().get("error", {}).get("message", response.text)
                except:
                    error_details = response.text
                return f"تم الرفض من Groq. السبب: {error_details}"
                
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"عذراً، حدث خطأ في الاتصال بـ Groq: {str(e)}"

    def embed_text(self, text: str, document_type: str = "") -> list[float]:
        pass