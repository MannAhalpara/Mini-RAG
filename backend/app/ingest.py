import os
import uuid
from typing import Dict, Any

from qdrant_client.http import models as qmodels
from google import genai

from .qdrant_db import get_qdrant_client
from .vector_store import ensure_collection
from .config import QDRANT_COLLECTION
from .utils import simple_chunk_text

# Gemini embedding model (cloud)
EMBED_MODEL = "text-embedding-004"


def embed_texts(texts):
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("GEMINI_API_KEY missing in environment")

    client = genai.Client(api_key=api_key)

    vectors = []
    for t in texts:
        res = client.models.embed_content(
            model=EMBED_MODEL,
            contents=t
        )
        vectors.append(res.embeddings[0].values)

    return vectors


def ingest_text(title: str, text: str) -> Dict[str, Any]:
    client = get_qdrant_client()
    ensure_collection(client)

    chunks = simple_chunk_text(text)

    if not chunks:
        return {"inserted": 0, "message": "No text provided"}

    vectors = embed_texts(chunks)

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
