import uuid
from typing import Dict, Any

from fastembed import TextEmbedding
from qdrant_client.http import models as qmodels

from .qdrant_db import get_qdrant_client
from .vector_store import ensure_collection
from .config import QDRANT_COLLECTION
from .utils import simple_chunk_text

# Free embedding model (FastEmbed)
EMBED_MODEL_NAME = "BAAI/bge-small-en-v1.5"

embedder = TextEmbedding(model_name=EMBED_MODEL_NAME)


def ingest_text(title: str, text: str) -> Dict[str, Any]:
    client = get_qdrant_client()
    ensure_collection(client)

    chunks = simple_chunk_text(text)

    if not chunks:
        return {"inserted": 0, "message": "No text provided"}

    vectors = list(embedder.embed(chunks))  # returns list of vectors

    points = []
    for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
        points.append(
            qmodels.PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "title": title,
                    "chunk_index": i,
                    "text": chunk,
                    "source": "pasted_text",
                },
            )
        )

    client.upsert(collection_name=QDRANT_COLLECTION, points=points)

    return {"inserted": len(points), "chunks": len(chunks)}
