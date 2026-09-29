"""
===============================================================================
NWIS Document Ingestion Pipeline
===============================================================================
CLI workflow to ingest drilling documents from data/reports/:
1. Extracts text from PDFs (with OCR fallback for scans) and TXT reports
2. Cleans text and extracts operational drilling metadata
3. Chunks documents into semantic sections
4. Generates dense vector embeddings using SentenceTransformers
5. Builds and persists the FAISS vector index and metadata

Usage:
    python -m ai.ingest
    python -m ai.ingest --sample-query "mud loss in Demo-Barail"
===============================================================================
"""

import os
import sys
import glob
import argparse
from typing import List, Dict, Any

from ai.document_processor import DocumentProcessor
from ai.text_chunker import TextChunker
from ai.embeddings import EmbeddingModel
from ai.vector_store import VectorStore
from ai.generate_sample_pdfs import generate_all_sample_reports

# Base paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPORTS_DIR = os.path.join(PROJECT_ROOT, "data", "reports")
GENERATED_DIR = os.path.join(PROJECT_ROOT, "data", "generated")

FAISS_INDEX_PATH = os.path.join(GENERATED_DIR, "faiss_index.bin")
FAISS_METADATA_PATH = os.path.join(GENERATED_DIR, "faiss_metadata.json")


def ingest_reports(
    reports_dir: str = REPORTS_DIR,
    index_path: str = FAISS_INDEX_PATH,
    metadata_path: str = FAISS_METADATA_PATH,
    max_reports: int = 15
) -> Dict[str, Any]:
    """
    Executes full ingestion pipeline over documents in reports_dir.
    """
    print("=" * 70)
    print("NWIS DOCUMENT INTELLIGENCE INGESTION PIPELINE (PHASE 3)")
    print("=" * 70)

    # 1. Ensure sample demonstration PDFs exist
    pdf_files = glob.glob(os.path.join(reports_dir, "*.pdf"))
    if not pdf_files:
        print("[INFO] No PDF reports found. Generating 8 synthetic demonstration PDFs...")
        generate_all_sample_reports()
        pdf_files = glob.glob(os.path.join(reports_dir, "*.pdf"))

    txt_files = glob.glob(os.path.join(reports_dir, "*.txt"))
    # Prioritize all PDFs, then supplement with a selection of TXT reports
    candidate_files = pdf_files + txt_files[:max(0, max_reports - len(pdf_files))]

    print(f"[1/4] Found {len(candidate_files)} reports to ingest ({len(pdf_files)} PDFs, {len(candidate_files) - len(pdf_files)} TXTs)")

    processor = DocumentProcessor()
    chunker = TextChunker(chunk_size=500, chunk_overlap=100)

    all_chunks: List[Dict[str, Any]] = []
    processed_count = 0

    # 2. Extract and chunk each document
    print("[2/4] Extracting text and chunking documents...")
    for file_path in candidate_files:
        rel_path = os.path.relpath(file_path, PROJECT_ROOT).replace("\\", "/")
        try:
            pages = processor.extract_document(file_path)
            chunks = chunker.chunk_document(pages, source_file=rel_path)
            all_chunks.extend(chunks)
            processed_count += 1
            print(f"  [+] Ingested: {os.path.basename(file_path)} ({len(chunks)} chunks, method: {pages[0]['extraction_method'] if pages else 'None'})")
        except Exception as e:
            print(f"  [-] Error extracting {os.path.basename(file_path)}: {e}")

    if not all_chunks:
        print("[ERROR] No chunks were extracted. Ingestion aborted.")
        return {"processed": 0, "chunks": 0, "status": "failed"}

    print(f"\n[3/4] Generating embeddings for {len(all_chunks)} text chunks...")
    embedding_model = EmbeddingModel()
    chunk_texts = [c["text"] for c in all_chunks]
    embeddings = embedding_model.encode(chunk_texts)
    print(f"  [+] Generated embedding matrix of shape: {embeddings.shape}")

    # 4. Build and save FAISS vector store
    print(f"[4/4] Building FAISS vector index (dim={embedding_model.dimension})...")
    vector_store = VectorStore(dimension=embedding_model.dimension)
    vector_store.add_chunks(all_chunks, embeddings)

    vector_store.save(index_path, metadata_path)
    print(f"  [+] Saved FAISS index: {index_path}")
    print(f"  [+] Saved Metadata JSON: {metadata_path}")

    summary = {
        "reports_processed": processed_count,
        "chunks_created": len(all_chunks),
        "embedding_dimension": embedding_model.dimension,
        "index_path": index_path,
        "metadata_path": metadata_path,
        "status": "success"
    }

    print("\n" + "=" * 50)
    print("INGESTION SUMMARY")
    print("=" * 50)
    print(f"Reports processed:    {summary['reports_processed']}")
    print(f"Chunks created:       {summary['chunks_created']}")
    print(f"Embedding dimension:  {summary['embedding_dimension']}")
    print(f"Vector index status:  READY & PERSISTED")
    print("=" * 50)

    return summary


def run_test_query(query: str, top_k: int = 3):
    """Executes a test query directly against the stored FAISS index."""
    print(f"\n[TEST QUERY] '{query}'")
    embedding_model = EmbeddingModel()
    vector_store = VectorStore(dimension=embedding_model.dimension)
    loaded = vector_store.load(FAISS_INDEX_PATH, FAISS_METADATA_PATH)

    if not loaded:
        print("[ERROR] Could not load vector store.")
        return

    query_vec = embedding_model.encode(query)
    results = vector_store.search(query_vec, top_k=top_k)

    print(f"Found {len(results)} matching chunks:")
    for i, res in enumerate(results, 1):
        print(f"\n--- Result #{i} (Score: {res['score']}) ---")
        print(f"Well: {res['well_name']} | Report: {res['report_name']} | Page: {res['page']}")
        if res.get('event_type'):
            print(f"Hazard: {res['event_type']} | Severity: {res.get('severity')} | Formation: {res.get('formation')}")
        snippet = res['text'][:200].replace('\n', ' ')
        print(f"Text: \"{snippet}...\"")


def main():
    parser = argparse.ArgumentParser(description="NWIS Document Ingestion & Vector Indexing")
    parser.add_argument("--sample-query", type=str, default=None, help="Run an immediate test search query after ingestion")
    parser.add_argument("--max-reports", type=int, default=15, help="Maximum reports to ingest (default: 15)")
    args = parser.parse_args()

    summary = ingest_reports(max_reports=args.max_reports)

    if args.sample_query:
        run_test_query(args.sample_query)
    else:
        # Default verification query
        run_test_query("severe mud loss in Demo-Barail sandstone")


if __name__ == "__main__":
    main()
