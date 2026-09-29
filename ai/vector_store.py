"""
===============================================================================
NWIS Vector Store - FAISS Vector Index & Metadata Persistence
===============================================================================
Manages dense vector storage and cosine similarity search over report chunks.
Includes FAISS (IndexFlatIP) and numpy cosine fallback.
===============================================================================
"""

import os
import json
from typing import List, Dict, Any, Optional
import numpy as np

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False


class VectorStore:
    """FAISS-powered vector store with metadata persistence."""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.chunks_metadata: List[Dict[str, Any]] = []
        self.index = None
        self._numpy_vectors: Optional[np.ndarray] = None

        if FAISS_AVAILABLE:
            # IndexFlatIP uses Inner Product (Cosine similarity when vectors are unit normalized)
            self.index = faiss.IndexFlatIP(dimension)
        else:
            self.index = None

    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: np.ndarray):
        """Adds text chunks and their embeddings to the vector store."""
        if len(chunks) == 0:
            return

        if embeddings.shape[0] != len(chunks):
            raise ValueError(f"Mismatch: {len(chunks)} chunks vs {embeddings.shape[0]} embeddings")

        # Ensure float32 and normalized
        embeddings = embeddings.astype(np.float32)

        if FAISS_AVAILABLE and self.index is not None:
            self.index.add(embeddings)
        else:
            if self._numpy_vectors is None:
                self._numpy_vectors = embeddings
            else:
                self._numpy_vectors = np.vstack([self._numpy_vectors, embeddings])

        self.chunks_metadata.extend(chunks)

    def total_count(self) -> int:
        """Returns total number of chunks indexed."""
        return len(self.chunks_metadata)

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Executes semantic nearest-neighbor search.
        query_vector: shape [1, dimension] or [dimension]
        """
        if self.total_count() == 0:
            return []

        if query_vector.ndim == 1:
            query_vector = np.expand_dims(query_vector, axis=0)

        query_vector = query_vector.astype(np.float32)

        results = []

        if FAISS_AVAILABLE and self.index is not None and self.index.ntotal > 0:
            scores, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))
            for score, idx in zip(scores[0], indices[0]):
                if 0 <= idx < len(self.chunks_metadata):
                    meta = self.chunks_metadata[idx]
                    results.append(self._format_result(meta, float(score)))
        elif self._numpy_vectors is not None and len(self._numpy_vectors) > 0:
            # Fallback cosine similarity
            sims = np.dot(self._numpy_vectors, query_vector.T).flatten()
            top_indices = np.argsort(sims)[::-1][:top_k]
            for idx in top_indices:
                meta = self.chunks_metadata[idx]
                results.append(self._format_result(meta, float(sims[idx])))

        return results

    @staticmethod
    def _format_result(meta: Dict[str, Any], score: float) -> Dict[str, Any]:
        """Formats standard search response object."""
        return {
            "score": round(max(0.0, min(1.0, score)), 4),
            "well_name": meta.get("well_name") or "Unknown Well",
            "report_name": meta.get("report_name", ""),
            "report_type": meta.get("report_type", "GENERAL_REPORT"),
            "page": meta.get("page", 1),
            "text": meta.get("text", ""),
            "event_type": meta.get("event_type"),
            "formation": meta.get("formation"),
            "depth": meta.get("depth"),
            "severity": meta.get("severity"),
            "metadata": {
                "chunk_id": meta.get("chunk_id"),
                "report_id": meta.get("report_id"),
                "well_id": meta.get("well_id"),
                "source_file": meta.get("source_file")
            }
        }

    def save(self, index_file: str, metadata_file: str):
        """Saves FAISS index binary and metadata JSON to disk."""
        os.makedirs(os.path.dirname(os.path.abspath(index_file)), exist_ok=True)
        os.makedirs(os.path.dirname(os.path.abspath(metadata_file)), exist_ok=True)

        # Save metadata JSON
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(self.chunks_metadata, f, indent=2)

        # Save FAISS index
        if FAISS_AVAILABLE and self.index is not None:
            faiss.write_index(self.index, index_file)
        elif self._numpy_vectors is not None:
            np.save(index_file + ".npy", self._numpy_vectors)

    def load(self, index_file: str, metadata_file: str) -> bool:
        """Loads FAISS index binary and metadata JSON from disk."""
        if not os.path.exists(metadata_file):
            return False

        with open(metadata_file, "r", encoding="utf-8") as f:
            self.chunks_metadata = json.load(f)

        if FAISS_AVAILABLE and os.path.exists(index_file):
            self.index = faiss.read_index(index_file)
            return True
        elif os.path.exists(index_file + ".npy"):
            self._numpy_vectors = np.load(index_file + ".npy")
            return True

        return False
