"""
===============================================================================
NWIS Embeddings - SentenceTransformer Vector Representation
===============================================================================
Generates normalized 384-dimensional dense vector embeddings for semantic
similarity search over historical drilling reports using SentenceTransformers.
===============================================================================
"""

import math
import re
from typing import List, Union
import numpy as np

# Try importing sentence_transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class EmbeddingModel:
    """Wrapper around SentenceTransformer with fallback support."""

    DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"
    DIMENSION = 384

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        self.model_name = model_name
        self.model = None
        self._is_transformer = False

        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                # Load pre-trained model (cached locally)
                self.model = SentenceTransformer(model_name)
                self._is_transformer = True
            except Exception as e:
                print(f"[WARN] Could not load SentenceTransformer '{model_name}': {e}. Using deterministic dense fallback.")
                self.model = None
                self._is_transformer = False
        else:
            print("[WARN] sentence-transformers not installed. Using deterministic dense fallback.")

    @property
    def dimension(self) -> int:
        return self.DIMENSION

    def encode(self, texts: Union[str, List[str]], batch_size: int = 32) -> np.ndarray:
        """
        Generates L2-normalized float32 embeddings for a single string or list of strings.
        Output shape: [N, 384]
        """
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return np.empty((0, self.DIMENSION), dtype=np.float32)

        if self._is_transformer and self.model is not None:
            try:
                # generate embeddings with SentenceTransformer
                embeddings = self.model.encode(
                    texts,
                    batch_size=batch_size,
                    show_progress_bar=False,
                    normalize_embeddings=True
                )
                return np.array(embeddings, dtype=np.float32)
            except Exception as e:
                print(f"[WARN] Error during transformer encoding: {e}. Falling back to dense term hashing.")

        # Fallback: Deterministic dense semantic hash embedding (384-dim, unit normalized)
        return self._dense_hash_encode(texts)

    def _dense_hash_encode(self, texts: List[str]) -> np.ndarray:
        """
        Lightweight deterministic term-hashing embedding generator for offline
        or test environments. Produces unit-length float32 vectors of length 384.
        """
        vectors = []
        for text in texts:
            vec = np.zeros(self.DIMENSION, dtype=np.float32)
            words = re.findall(r"\b\w+\b", text.lower())
            for i, word in enumerate(words):
                # Hash word to dimension index
                h = abs(hash(word)) % self.DIMENSION
                # Position-weighted value
                vec[h] += 1.0 / math.sqrt(i + 1)
            # L2 normalize
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            vectors.append(vec)

        return np.array(vectors, dtype=np.float32)
