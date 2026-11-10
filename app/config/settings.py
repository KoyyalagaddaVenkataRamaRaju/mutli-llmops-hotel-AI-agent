from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY")
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "stayease-hotel-apex")


    ALLOWED_MODEL_NAMES = [
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
        "qwen/qwen3.8-27b",
    ]

settings = Settings()