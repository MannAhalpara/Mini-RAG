# Mini RAG Playground (Track B)
**FastAPI + Qdrant + Gemini + Citations + File Upload**

Mini RAG Playground is a lightweight Retrieval-Augmented Generation (RAG) application. It lets users paste text or upload files, stores chunk embeddings in a cloud-hosted vector database, retrieves the most relevant chunks for a question, applies a lightweight reranking step, and generates a grounded answer with inline citations.

---

## Live URLs 

- **Frontend (Vercel):** https://minirag-three.vercel.app/
- **Backend (Render):** https://mini-rag-backendd.onrender.com

---

## Key Features

### RAG Pipeline
- Ingest text (paste) or upload a document (`.txt` / `.pdf`)
- Chunking + metadata storage
- Vector search in **Qdrant Cloud**
- Lightweight reranking using similarity scoring
- Answer generation using **Gemini** with inline citations like `[1]`

### Production-minded Setup
- Hosted backend + frontend
- Secrets stored server-side only (API keys never exposed in frontend)
- Clean API design and responses
- Practical no-answer handling
- Reset endpoint for testing

---

## Architecture

```text
+---------------------------+
| Frontend (Vercel)         |
| Static UI (HTML/CSS/JS)   |
+-------------+-------------+
              |
              | REST API calls
              v
+---------------------------+
| Backend (Render)          |
| FastAPI                   |
| /ingest /upload /ask      |
+-------------+-------------+
              |
              | Embeddings + Retrieval
              v
+---------------------------+
| Qdrant Cloud Vector DB    |
| Stores vectors + payload  |
| (metadata + chunk text)   |
+---------------------------+
              |
              v
+---------------------------+
| Gemini 2.5 Flash (LLM)    |
| Answer + inline citations |
+---------------------------+
```

---

## How It Works (Flow)

### 1) Ingestion
User provides input using:
- Paste text in the UI, OR
- Upload `.txt/.pdf`

Backend workflow:
- Extract text (PDF parsing)
- Chunk text + overlap
- Embed chunks
- Store vectors + metadata + chunk text in Qdrant

### 2) Retrieval + Reranking
When the user asks a question:
- Embed the question
- Retrieve top-k chunks from Qdrant
- Re-score chunks using lightweight reranking logic
- Keep best results and filter irrelevant chunks using a threshold + fallback strategy

### 3) Answer Generation + Citations
Gemini receives:
- the user question
- retrieved context chunks labeled as `[1]`, `[2]`, `[3]`

Gemini produces a grounded answer and adds citations.

---

## Vector DB Configuration (Qdrant)

- **Provider:** Qdrant Cloud (Free Tier)
- **Collection name:** `mini_rag_docs`
- **Distance metric:** Cosine similarity
- **Embedding model:** Gemini `text-embedding-004`
- **Embedding dimension:** `768`

### Stored payload (metadata)
Each chunk is stored as a separate point with:
- `title`
- `chunk_index`
- `source`
- `text`

---

## Chunking Strategy

Chunking is character-based to keep the pipeline simple and fast:

- `chunk_size_chars`: **1200**
- `overlap_chars`: **150**

---

## Retriever + Reranker Setup

### Retriever
- Vector search in Qdrant using query embedding
- `top_k = 5` retrieved candidates

### Reranker (lightweight, free)
- Re-scores retrieved chunks
- Keeps best `top_n = 3`
- Filters low-relevance results with a threshold (with fallback to avoid false “no-answer” cases)

---

## API Endpoints

### GET `/health`
Health check.

**Response**
```json
{ "status": "ok" }
```

---

### POST `/ingest`
Ingest pasted text.

**Request**
```json
{
  "title": "Leave Policy",
  "text": "...."
}
```

---

### POST `/upload`
Upload file and ingest (`.txt`, `.pdf`).

**Form-data**
- `title`: `My File`
- `file`: upload `.pdf` or `.txt`

---

### POST `/ask`
Ask a question.

**Request**
```json
{
  "question": "How many annual leave days do employees get?"
}
```

**Response**
```json
{
  "answer": "Employees get 18 days of annual leave per year [1].",
  "sources": [
    {
      "ref": 1,
      "title": "Leave Policy",
      "chunk_index": 0,
      "rerank_score": 0.82,
      "text": "Each full-time employee receives 18 days..."
    }
  ],
  "latency_ms": 4029
}
```

---

### POST `/reset`
Deletes and recreates the collection (useful during testing).

---

### POST `/init`
Ensures the vector collection exists.

---

### GET `/stats`
Returns Qdrant collection stats like `points_count`.

---

## Environment Variables

Backend uses environment variables (kept server-side):

```env
QDRANT_URL=...
QDRANT_API_KEY=...
QDRANT_COLLECTION=mini_rag_docs
GEMINI_API_KEY=...
```

`.env.example` is included  
`.env` is not committed  

---

## Local Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at:  
`http://127.0.0.1:8000`

### Frontend
Open this file in browser:

```text
frontend/index.html
```

---

## Known Limitations
- File upload supports `.txt` and `.pdf` only
- Chunking is character-based (token-based chunking can improve accuracy)
- Reranker is lightweight (external rerankers like Cohere/Jina can improve results further)

---

## Future Improvements
- Token-based chunking + better metadata extraction (sections/headings)
- Multiple-document filtering (search within selected title)
- Streaming responses
- Stronger evaluation metrics dashboard
- Authentication for write endpoints

---

## Resume
https://drive.google.com/file/d/1v2fil1I7i0_tqNGQSavIkv38i57x0OZ-/view?usp=drive_link

---

## Author
**Mann Ahalpara**  
- GitHub: https://github.com/MannAhalpara  
- LinkedIn: https://www.linkedin.com/in/mannahalpara/
