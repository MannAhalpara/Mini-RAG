# Mini RAG Playground (Track B)
**FastAPI + Qdrant + Gemini + Citations + File Upload**

A small Retrieval-Augmented Generation (RAG) application that lets users paste text or upload files, stores chunk embeddings in a cloud-hosted vector database, retrieves the most relevant chunks for a question, applies a lightweight reranking step, and generates a grounded answer with inline citations.

---

## Live URL:
- **Frontend (Vercel):** https://minirag-three.vercel.app/
- **Backend (Render):** https://mini-rag-backendd.onrender.com

---

## Key Features 
### RAG Pipeline
- Ingest text(paste) or upload a document (**.txt / .pdf**)
- Chunking + metadata storage
- Vector search in **Qdrant Cloud**
- Reranking using free similarity scoring
- Answer generation using **Gemini** with **inline citations** like '[1]'

### Production-minded Setup
- Hosted backend + frontend
- Secrets stored server-side only
- Clean API design and reponses
- Helpful "no-answer" handling
- Easy reset endpoint for testing

---

## Architecture
      ┌───────────────────────────────┐
      │           Frontend            │
      │     (Vercel / Static UI)      │
      └───────────────┬───────────────┘
                      │  REST API Calls
                      ▼
      ┌───────────────────────────────┐
      │            Backend            │
      │            FastAPI            │
      │     /ingest  /upload  /ask    │
      └───────────────┬───────────────┘
                      │
      ┌───────────────┼─────────────────────────┐
      ▼               ▼                         ▼
┌──────────────┐ ┌──────────────┐ ┌─────────────────┐
│ Chunking     │ │ Embeddings   │ │ Answering (LLM) │
│ + Metadata   │ │ Gemini Embed │ │ Gemini 1.5 Flash│
└───────┬──────┘ └───────┬──────┘ └────────┬────────┘
        │                │                 │
        ▼                ▼                 ▼
┌────────────────────────────────────────────────────┐
│           Qdrant Vector DB (Cloud)                 │
│   Stores vectors + payload(metadata + chunk text)  │
└────────────────────────────────────────────────────┘

---

## How it works (Flow)

### 1) Ingestion
**Paste text** OR **Upload .txt/.pdf**
-> Extract text (for PDF)
-> Chunk it
-> Embed each chunk
->  Store '(vector + metadata + chunk text)' in Qdrant

### 2) Retrieval + Reranking 
User asks a question
-> Embed question
-> Retieve top-k vectors from Qdrant
-> Rerank retrieved chunks using a free similarity check
-> Filter irrelevant results using a small threshold + fallback logic

### 3) Answer Generation + Citations
LLM receives:

- User question
- Retrieved contexts labeled as '[1]', '[2]', '[3]'

LLM returns grounded answer with citations like:
> "Employees recieve 18 days of annual leave per year [1]."

Below, sources are displayed corresponding to the same citation indices.

---

## Vector DB Configuration (Qdrant)

- **Provider:** Qdrant Cloud (Free Tier)
- **Collection name:** 'mini_rag_docs'
- **Distance metric:** Cosine similarity
- **Embedding model:** Gemini 'text-embedding-004'
- **Embedding dimension:** '768'

### Upsert Strategy
Each chunk is upsert as an independent point with:
- auto-generated UUID as point ID
- payload includes:
  - 'title'
  - 'chunk_index'
  - 'text'
  - 'source'

---

## Chunking Strategy

**Chunking method:** simple character-based chunking
- 'chunk_size_chars': **1200**
- 'overlap_chars': **!50**

Metadata stored per chunk:
- 'title'
- 'chunk_index'
- 'source'

**Reasoning:**
Chunk overlap prevents losing context at boundaries and improves retrieval quality.

---

## Retriever + Reranker Stepup

### Retriever
- Vector search from Qdrant using question embedding
- 'top_k = 5' candidates retrieved
### Reranker (Free)
To satisfy **Retriever + Reranker**, a second scoring step is applied:
- Query embedding vs. chunk embedding cosine similarity
- Keep best `top_n = 3`
- Filter with minimum score threshold + fallback

This improves relevance while keeping the solution fully free.
