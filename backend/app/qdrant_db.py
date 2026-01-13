from qdrant_client import QdrantClient
from .config import QDRANT_URL, QDRANT_API_KEY

def get_qdrant_client() -> QdrantClient:
    if not QDRANT_URL or not QDRANT_API_KEY:
        raise ValueError("QDRANT_URL or QDRANT_API_KEY missing. Check your .env file.")
    return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
