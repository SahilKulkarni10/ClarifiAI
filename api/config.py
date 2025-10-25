import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # MongoDB
    MONGODB_URI: str = os.getenv("MONGODB_URL", os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
    DATABASE_NAME: str = "finance_ai"
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    JWT_SECRET_KEY: str = os.getenv("SECRET_KEY", os.getenv("JWT_SECRET_KEY", "your-secret-key"))
    
    # JWT Settings
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Vector DB
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_data")
    
    # API Settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("PORT", os.getenv("API_PORT", "8000")))
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # CORS
    def get_cors_origins(self):
        """Get CORS origins from environment or use defaults"""
        cors_env = os.getenv("CORS_ORIGINS", "")
        if cors_env:
            if cors_env == "*":
                return ["*"]
            return [origin.strip() for origin in cors_env.split(",")]
        
        # Default development origins
        return [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
            "http://localhost:8080",  # Frontend Vite dev server
            "http://127.0.0.1:8080",
            "http://[::]:8080",
        ]
    
    CORS_ORIGINS: list = None  # Will be set dynamically
    
    # External APIs
    RBI_BASE_URL: str = "https://www.rbi.org.in"
    SEBI_BASE_URL: str = "https://www.sebi.gov.in"
    ECONOMIC_TIMES_URL: str = "https://economictimes.indiatimes.com"

settings = Settings()
# Set CORS origins dynamically
settings.CORS_ORIGINS = settings.get_cors_origins()
