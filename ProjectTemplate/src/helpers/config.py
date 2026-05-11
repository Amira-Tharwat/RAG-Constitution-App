"""
TIP: Implement the Settings class using pydantic_settings to load configuration from the .env file.
"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str
    APP_VERSION: str
    
    # File Settings
    FILE_ALLOWED_EXTENSIONS: list[str]
    FILE_MAX_SIZE_MB: int
    FILE_CHUNK_SIZE: int
    
    # Database Settings
    MONGODB_URI: str
    MONGODB_DB_NAME: str
    
    # AI & Model Settings
    # خلينا المفاتيح اختيارية عشان Pydantic ميزعلش لو مسحناها من الـ .env
    GEMINI_API_KEY: Optional[str] = None 
    GROQ_API_KEY: Optional[str] = None
    
    GENERATE_RESPONSE_MODEL: str
    EMBEDDINGS_MODEL: str
    EMBEDDING_DIMENSION: int
    MAX_INPUT_TOKENS: int
    MAX_RESPONSE_TOKENS: int
    TEMPERATURE: float
    
    # Vector DB Settings
    VECTOR_DB_PATH: str
    VECTOR_DISTANCE_METRIC: str

    # Configuration to read from .env file
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

def get_settings():
    return Settings()