import os
import time
from typing import Dict, Any, List, Tuple

from google import genai

from .config import QDRANT_COLLECTION
from .qdrant_db import get_qdrant_client


EMBED_MODEL = "text-embedding-004"


def cosine_similarity(a, b) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def embed_text(text: str) -> List[float]:
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("GEMINI_API_KEY missing in environment")

    client = genai.Client(api_key=api_key)
    res = client.models.embed_content(model=EMBED_MODEL, contents=text)
    return res.embeddings[0].values


def build_prompt(question: str, contexts: List[str]) -> str:
    context_block = "\n\n".join([f"[{i+1}] {c}" for i, c in enumerate(contexts)])
    return f"""
You are a helpful assistant.
Answer the user question ONLY using the context below.
If the context is not enough, say: "I don't know based on the provided text."

CONTEXT:
{context_block}

QUESTION:
{question}

RULES:
- Use inline citations like [1], [2] based on the context chunks.
- Do NOT use any outside knowledge.
- Keep the answer short and clear.
""".strip()


def ask_rag(question: str, gemini_api_key: str, top_k: int = 5) -> Dict[str, Any]:
    t0 = time.time()

    # Query embedding (Gemini)
    query_vector = embed_text(question)

    # Retrieve from Qdrant
    qdrant = get_qdrant_client()

    result = qdrant.query_points(
        collection_name=QDRANT_COLLECTION,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    )

    hits = result.points
    if not hits:
        return {
            "answer": "I couldn't find relevant info in the provided data.",
            "sources": [],
            "latency_ms": int((time.time() - t0) * 1000),
        }

    # Free reranker (cosine similarity between query embedding and chunk embedding)
    reranked: List[Tuple[float, Any]] = []
    for hit in hits:
        payload = hit.payload or {}
        chunk_text = payload.get("text", "")
        if not chunk_text:
            continue

        chunk_vec = embed_text(chunk_text)
        score2 = cosine_similarity(query_vector, chunk_vec)
        reranked.append((score2, hit))

    reranked.sort(key=lambda x: x[0], reverse=True)

    # Filter out irrelevant sources
    MIN_SCORE = 0.55
    final_hits = []
    for score2, hit in reranked:
        if score2 >= MIN_SCORE:
            final_hits.append((score2, hit))
        if len(final_hits) == 3:
            break

    if not final_hits and len(reranked) > 0:
        final_hits = [reranked[0]]

    contexts = []
    sources = []
    for idx, (score2, hit) in enumerate(final_hits):
        payload = hit.payload or {}
        chunk_text = payload.get("text", "")
        contexts.append(chunk_text)

        sources.append(
            {
                "ref": idx + 1,
                "id": str(hit.id),
                "title": payload.get("title", "User Document"),
                "chunk_index": payload.get("chunk_index", idx),
                "rerank_score": float(score2),
                "text": chunk_text,
            }
        )

    prompt = build_prompt(question, contexts)

    # Gemini answer
    client = genai.Client(api_key=gemini_api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    answer = response.text if response and response.text else "No answer generated."

    return {
        "answer": answer,
        "sources": sources,
        "latency_ms": int((time.time() - t0) * 1000),
    }
