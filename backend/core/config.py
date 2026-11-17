import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "GISAP — Genomic & Multi-Omics Analysis Platform"
    VERSION: str = "0.1.0-alpha"
    
    # Storage
    S3_ENDPOINT: str = os.getenv("S3_ENDPOINT", "http://localhost:9000")
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY", "minioadmin")
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY", "miniopassword")
    S3_BUCKET_RAW: str = os.getenv("S3_BUCKET_RAW", "raw-sequences")
    S3_BUCKET_INTERMEDIATES: str = os.getenv("S3_BUCKET_INTERMEDIATES", "intermediates")
    S3_BUCKET_RESULTS: str = os.getenv("S3_BUCKET_RESULTS", "results")
    S3_BUCKET_REFERENCE: str = os.getenv("S3_BUCKET_REFERENCE", "reference-dbs")
    S3_SECURE: bool = os.getenv("S3_SECURE", "false").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./gisap_metadata.db")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Auth & Multi-Tenancy
    JWT_SECRET: str = os.getenv("JWT_SECRET", "gisap_development_secret_key_change_in_production_32bytes")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    DEFAULT_TENANT_ID: str = os.getenv("DEFAULT_TENANT_ID", "ssit-tumakuru")

    # External Research
    FIRECRAWL_API_KEY: str = os.getenv("FIRECRAWL_API_KEY", "")

    # AI Annotation (Gemini Free Tier)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    # Annotation outputs are always tagged ai_suggested_hypothesis — never biological fact
    AI_ANNOTATION_ENABLED: bool = os.getenv("GEMINI_API_KEY", "") != ""

settings = Settings()
