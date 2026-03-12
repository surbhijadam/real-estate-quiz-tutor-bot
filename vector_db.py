"""
vector_db.py
------------
Builds a FAISS index from embeddings and provides
semantic similarity search to retrieve relevant context chunks.
"""

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from embeddings import load_and_embed, MODEL_NAME


class VectorDB:
    """
    In-memory FAISS vector store for real estate document chunks.
    Supports semantic similarity search (RAG retrieval).
    """

    def __init__(self, doc_path: str):
        """
        Build the FAISS index on initialization.
        Args:
            doc_path: Path to real_estate_docs.txt
        """
        self.model = SentenceTransformer(MODEL_NAME)
        self.chunks, embeddings = load_and_embed(doc_path)

        # Build a flat L2 index (exact search — fine for small corpora)
        embedding_dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.index.add(embeddings)

        print(f"[VectorDB] Indexed {len(self.chunks)} chunks | dim={embedding_dim}")

    def search(self, query: str, top_k: int = 3) -> list[str]:
        """
        Find the top_k most semantically relevant chunks for a query.

        Args:
            query  : The question or topic to search for
            top_k  : Number of chunks to retrieve

        Returns:
            List of text chunks ranked by relevance
        """
        # Embed the query
        query_vec = self.model.encode([query], convert_to_numpy=True).astype("float32")

        # FAISS search — returns distances and indices
        distances, indices = self.index.search(query_vec, top_k)

        results = []
        for idx in indices[0]:
            if idx != -1:                          # -1 means no result found
                results.append(self.chunks[idx])
        return results

    def get_context(self, query: str, top_k: int = 3) -> str:
        """
        Retrieve and join top_k chunks into a single context string
        ready to be injected into a Claude prompt.
        """
        chunks = self.search(query, top_k=top_k)
        return "\n\n---\n\n".join(chunks)


if __name__ == "__main__":
    import os
    base_dir = os.path.dirname(__file__)
    doc_path = os.path.join(base_dir, "data", "real_estate_docs.txt")

    db = VectorDB(doc_path)

    # Test retrieval
    query = "What is a cap rate and how is it calculated?"
    context = db.get_context(query)
    print(f"\nQuery  : {query}")
    print(f"\nTop chunks retrieved:\n{context[:600]}...")   