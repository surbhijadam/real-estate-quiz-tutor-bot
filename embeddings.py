"""
embeddings.py
-------------
Loads real_estate_docs.txt, splits it into chunks,
and generates sentence-transformer embeddings for each chunk.
"""

from sentence_transformers import SentenceTransformer
import numpy as np
import os

# Embedding model — lightweight, fast, good semantic quality
MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 400        # characters per chunk
CHUNK_OVERLAP = 80      # overlap between consecutive chunks


def load_documents(filepath: str) -> str:
    """Read the raw text knowledge base."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Split text into overlapping chunks.
    Overlap ensures context is not lost at chunk boundaries.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def generate_embeddings(chunks: list[str], model_name: str = MODEL_NAME) -> np.ndarray:
    """
    Convert text chunks into dense vector embeddings.
    Returns a 2D numpy array of shape (num_chunks, embedding_dim).
    """
    model = SentenceTransformer(model_name)
    embeddings = model.encode(chunks, show_progress_bar=False, convert_to_numpy=True)
    return embeddings.astype("float32")


def load_and_embed(filepath: str) -> tuple[list[str], np.ndarray]:
    """
    Full pipeline: load → chunk → embed.
    Returns (chunks, embeddings) ready for FAISS indexing.
    """
    raw_text = load_documents(filepath)
    chunks = chunk_text(raw_text)
    embeddings = generate_embeddings(chunks)
    return chunks, embeddings


if __name__ == "__main__":
    # Quick test
    base_dir = os.path.dirname(__file__)
    doc_path = os.path.join(base_dir, "data", "real_estate_docs.txt")
    chunks, embeddings = load_and_embed(doc_path)
    print(f"Total chunks  : {len(chunks)}")
    print(f"Embedding dim : {embeddings.shape[1]}")
    print(f"Sample chunk  :\n{chunks[0]}\n")