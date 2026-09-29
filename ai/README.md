# NWIS Document Intelligence (Phase 3)
### Nearby Wells Intelligence System — Phase 3: Document Processing, Embeddings & Semantic Search

---

## 1. Overview

**NWIS Document Intelligence** transforms unstructured historical drilling reports (Well Completion Reports, Daily Drilling Reports, Mud Logs, and Incident Reports) into a searchable semantic knowledge base.

During drilling operations, engineers can query historical hazard narratives in plain English (e.g., *"stuck pipe in Demo-Barail around 3000m"* or *"mud loss mitigation in depleted sands"*). The system uses **SentenceTransformer embeddings** and a **FAISS vector index** to retrieve the most relevant historical operational excerpts, root causes, and engineering mitigations from offset wells.

> [!NOTE]
> **Data Disclaimer:**
> All sample reports and text excerpts in this directory and `data/reports/` are **100% synthetic demonstration documents** created for the SIH prototype. They do **NOT** represent actual, operational, or confidential data from Oil India Limited (OIL), ONGC, or any other commercial operator.

---

## 2. Architecture & Pipeline

```
Drilling Documents (data/reports/*.pdf, *.txt)
                     │
                     ▼
       1. DocumentProcessor (PyMuPDF + OCR Fallback)
          - Extracts raw text page by page
          - Falls back to Tesseract OCR for scanned/image pages
          - Cleans text and extracts well/depth/formation metadata
                     │
                     ▼
       2. TextChunker (Semantic Overlapping Window)
          - Chunks text into ~500-char semantic paragraphs
          - Enriches each chunk with well_name, depth, formation, event_type
                     │
                     ▼
       3. EmbeddingModel (SentenceTransformers: all-MiniLM-L6-v2)
          - Generates 384-dimensional normalized dense vectors
                     │
                     ▼
       4. VectorStore (FAISS IndexFlatIP)
          - Fast cosine similarity nearest-neighbor lookup
          - Persists faiss_index.bin and faiss_metadata.json
                     │
                     ▼
       5. REST API: GET /api/search?query=...
          - Exposes semantic search to future frontend dashboard
```

---

## 3. Directory Structure

```
ai/
├── __init__.py
├── document_processor.py      # PDF text extraction (PyMuPDF) + OCR fallback + metadata tagger
├── text_chunker.py            # Balanced semantic text chunking & metadata propagation
├── embeddings.py              # SentenceTransformers (all-MiniLM-L6-v2, 384-dim) + normalized vectors
├── vector_store.py            # FAISS IndexFlatIP (cosine similarity) + metadata storage
├── generate_sample_pdfs.py    # Generates 8 realistic synthetic demonstration PDF reports
├── ingest.py                  # CLI pipeline: extract -> chunk -> embed -> index
└── README.md                  # This documentation guide
```

---

## 4. Ingestion Workflow

To ingest all reports in `data/reports/` and build the FAISS vector index:

```powershell
# From project root (d:\SIH\NWIS)
py -m ai.ingest
```

### What Happens During Ingestion:
1. **Generates Synthetic Demonstration PDFs**: If no PDFs exist, generates 8 realistic demonstration reports (DDR, WCR, Mud Log, Incident Reports) covering known offset well hazards (Barail mud loss, Kopili stuck pipe, Tipam gas kicks).
2. **Extracts & Cleans Text**: Processes PDF and text documents page by page.
3. **Semantic Chunking**: Splits reports into balanced chunks while preserving metadata (`well_name`, `formation`, `depth`, `event_type`).
4. **Dense Embeddings**: Computes 384-dimensional embeddings using SentenceTransformers.
5. **FAISS Indexing**: Builds `data/generated/faiss_index.bin` and `data/generated/faiss_metadata.json`.

---

## 5. Semantic Search API (`GET /api/search`)

Once ingested, the FastAPI backend exposes semantic search:

### Request:
```http
GET /api/search?query=stuck pipe in Demo-Barail around 3000m&top_k=3 HTTP/1.1
Host: localhost:8000
```

### Example Response:
```json
{
  "query": "stuck pipe in Demo-Barail around 3000m",
  "total_results": 3,
  "results": [
    {
      "score": 0.8142,
      "well_name": "NWIS-W002",
      "report_name": "NWIS-W002_Daily_Drilling_Report_Mud_Loss.pdf",
      "report_type": "DDR",
      "page": 1,
      "event_type": "MUD_LOSS",
      "formation": "Demo-Barail",
      "depth": 2980.0,
      "severity": "HIGH",
      "text": "At 2980m measured depth, severe dynamic mud loss was observed at surface. Loss rate abruptly exceeded 45 bbls/hr. Penetrated depleted pore pressure sandstone reservoir with subnormal pressure gradient (~0.38 psi/ft)... Mixed and spotted 50 bbls coarse calcium carbonate (CaCO3) Loss Circulation Material (LCM) pill.",
      "metadata": {
        "well_id": 2,
        "source_file": "data/reports/NWIS-W002_Daily_Drilling_Report_Mud_Loss.pdf"
      }
    }
  ]
}
```

---

## 6. Example Test Queries to Try

You can test these in your browser at `http://localhost:8000/docs` or via curl/PowerShell:

1. **Mud Loss in Depleted Sand:**
   `GET /api/search?query=mud loss in Demo-Barail sandstone`
   *Matches:* `NWIS-W002` and `NWIS-W007` Barail thief zone reports.

2. **Stuck Pipe in Reactive Shale:**
   `GET /api/search?query=stuck pipe and jar overpull in Kopili shale`
   *Matches:* `NWIS-W004` and `NWIS-W008` Kopili shale sloughing incident reports.

3. **Gas Kick and Well Control:**
   `GET /api/search?query=shallow gas kick drilling break in Tipam`
   *Matches:* `NWIS-W003` Tipam sandstone kick and Wait-and-Weight kill report.

4. **Cementing Channeling:**
   `GET /api/search?query=casing cement channeling CBL log`
   *Matches:* `NWIS-W005` casing cement squeeze report.
