import re
from typing import List


def simple_chunk_text(text: str, chunk_size_chars: int = 1200, overlap_chars: int = 150) -> List[str]:
    """
    Simple chunking by characters (free + easy).
    Later in README we will mention approx token range.
    """
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size_chars, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break
        start = end - overlap_chars  # overlap

    return chunks
