"""
===============================================================================
NWIS Backend - Semantic Search Router (Phase 3)
===============================================================================
Exposes semantic search endpoint over ingested historical drilling reports
using SentenceTransformer embeddings and the FAISS vector index.
===============================================================================
"""

import os
import sys
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status

# Ensure project root is in sys.path so 'ai' package is importable
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.dirname(APP_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ai.embeddings import EmbeddingModel
from ai.vector_store import VectorStore
from app.schemas.search import SearchResponse, SearchResultItem

router = APIRouter(prefix="/api/search", tags=["Semantic Search"])

# Paths to persisted FAISS index and metadata
INDEX_PATH = os.path.join(PROJECT_ROOT, "data", "generated", "faiss_index.bin")
METADATA_PATH = os.path.join(PROJECT_ROOT, "data", "generated", "faiss_metadata.json")

# Global singleton cache for embedding model and vector store to avoid reloads
_embedding_model: Optional[EmbeddingModel] = None
_vector_store: Optional[VectorStore] = None


def get_search_components():
    """Lazily loads and caches the embedding model and vector index."""
    global _embedding_model, _vector_store

    if not os.path.exists(METADATA_PATH):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Vector index not found. Please run 'python -m ai.ingest' "
                "to process and index historical drilling reports first."
            )
        )

    if _embedding_model is None:
        _embedding_model = EmbeddingModel()

    if _vector_store is None:
        store = VectorStore(dimension=_embedding_model.dimension)
        success = store.load(INDEX_PATH, METADATA_PATH)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to load vector index. Please run 'python -m ai.ingest' to rebuild it."
            )
        _vector_store = store

    return _embedding_model, _vector_store


@router.get(
    "",
    response_model=SearchResponse,
    summary="Semantic Search across drilling reports",
    description=(
        "Executes a natural language semantic search across ingested drilling reports "
        "(DDR, WCR, Mud Logs, Incident Reports) using dense vector embeddings and FAISS. "
        "Returns the most relevant report excerpts ranked by cosine similarity score."
    )
)
def semantic_search(
    query: str = Query(
        ...,
        min_length=2,
        max_length=500,
        description="Search question or hazard query (e.g., 'stuck pipe in Demo-Barail around 3000m')"
    ),
    top_k: int = Query(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of relevant excerpts to return"
    )
):
    embedding_model, vector_store = get_search_components()

    # Encode query
    query_vector = embedding_model.encode(query)

    # Search FAISS index
    raw_results = vector_store.search(query_vector, top_k=top_k)

    items = [
        SearchResultItem(
            score=r["score"],
            well_name=r["well_name"],
            report_name=r["report_name"],
            report_type=r.get("report_type", "GENERAL_REPORT"),
            page=r.get("page", 1),
            text=r["text"],
            event_type=r.get("event_type"),
            formation=r.get("formation"),
            depth=r.get("depth"),
            severity=r.get("severity"),
            metadata=r.get("metadata", {})
        )
        for r in raw_results
    ]

    return SearchResponse(
        query=query,
        total_results=len(items),
        results=items
    )
