from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from .config import QDRANT_COLLECTION

# Gemini text-embedding-004 output dimension
EMBEDDING_DIM = 768


def ensure_collection(client: QdrantClient) -> None:
    existing = [c.name for c in client.get_collections().collections]

    if QDRANT_COLLECTION in existing:
        return

    client.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=qmodels.VectorParams(
            size=EMBEDDING_DIM,
            distance=qmodels.Distance.COSINE,
        ),
    )
