import time
from typing import Dict, Any, List, Tuple

from fastembed import TextEmbedding
import google.generativeai as genai

from .config import QDRANT_COLLECTION
from .qdrant_db import get_qdrant_client

# Free embedding model (FastEmbed)
EMBED_MODEL_NAME = "BAAI/bge-small-en-v1.5"
embedder = TextEmbedding(model_name=EMBED_MODEL_NAME)


def cosine_similarity(a, b) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def build_prompt(question: str, contexts: List[str]) -> str:
    """
    contexts are already reranked + filtered.
    We will label them as [1], [2], [3] so Gemini can cite properly.
    """
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
    """
    Pipeline:
    1) Embed user query
    2) Retrieve top_k from Qdrant
    3) Free reranker: cosine(query_emb, chunk_emb)
    4) Filter by MIN_SCORE
    5) LLM answer + citations
    """
    t0 = time.time()
    client = get_qdrant_client()

    # ✅ Query embedding
    query_vector = list(embedder.embed([question]))[0]

    # ✅ Retrieve from Qdrant
    result = client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    )

    search_result = result.points  # IMPORTANT

    # If nothing retrieved
    if not search_result:
        return {
            "answer": "I couldn't find relevant info in the provided data.",
            "sources": [],
            "latency_ms": int((time.time() - t0) * 1000),
        }

    # ✅ FREE reranker scoring (cosine with query)
    reranked: List[Tuple[float, Any]] = []
    for hit in search_result:
        payload = hit.payload or {}
        chunk_text = payload.get("text", "")
        if not chunk_text:
            continue

        chunk_vec = list(embedder.embed([chunk_text]))[0]
        score2 = cosine_similarity(query_vector, chunk_vec)
        reranked.append((score2, hit))

    # sort high -> low
    reranked.sort(key=lambda x: x[0], reverse=True)

    # ✅ Threshold to remove irrelevant sources
    MIN_SCORE = 0.65

    final_hits = []
    for score2, hit in reranked:
        if score2 >= MIN_SCORE:
            final_hits.append((score2, hit))
        if len(final_hits) == 3:
            break

    # If nothing passed threshold
    if not final_hits:
        return {
            "answer": "I couldn't find relevant info in the provided data.",
            "sources": [],
            "latency_ms": int((time.time() - t0) * 1000),
        }

    # ✅ Build contexts + sources (aligned indexing for citations)
    contexts: List[str] = []
    sources: List[Dict[str, Any]] = []

    for idx, (score2, hit) in enumerate(final_hits):
        payload = hit.payload or {}
        chunk_text = payload.get("text", "")

        contexts.append(chunk_text)

        sources.append(
            {
                "ref": idx + 1,  # this matches citation numbers [1], [2], [3]
                "id": str(hit.id),
                "title": payload.get("title", "User Document"),
                "chunk_index": payload.get("chunk_index", idx),
                "rerank_score": float(score2),
                "text": chunk_text,
            }
        )

    # ✅ Prompt for Gemini
    prompt = build_prompt(question, contexts)

    # ✅ Gemini call
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)

    answer = response.text if response and response.text else "No answer generated."

    return {
        "answer": answer,
        "sources": sources,
        "latency_ms": int((time.time() - t0) * 1000),
    }
