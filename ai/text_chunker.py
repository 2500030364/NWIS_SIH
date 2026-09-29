"""
===============================================================================
NWIS Text Chunker - Semantic Report Chunking with Rich Metadata
===============================================================================
Splits extracted document pages into meaningful, overlapping chunks while
preserving and enriching drilling metadata for semantic vector indexing.
===============================================================================
"""

import os
import uuid
import re
from typing import List, Dict, Any, Optional


class TextChunker:
    """Chunks text into balanced sections with metadata propagation."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(
        self,
        pages: List[Dict[str, Any]],
        source_file: str,
        report_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Splits a list of extracted document pages into semantic chunks.
        """
        chunks = []
        filename = os.path.basename(source_file)
        report_type = self._infer_report_type(filename)

        for page in pages:
            page_num = page.get("page_number", 1)
            page_text = page.get("text", "")
            page_meta = page.get("metadata", {})

            if not page_text or len(page_text.strip()) < 40:
                continue

            # Split page text into chunks
            page_chunks = self._split_text(page_text)

            for idx, chunk_text in enumerate(page_chunks):
                # Also detect any local keywords in this specific chunk
                chunk_meta = self._extract_chunk_specific_meta(chunk_text, page_meta)

                chunk_obj = {
                    "chunk_id": f"{filename}_p{page_num}_c{idx + 1}_{uuid.uuid4().hex[:6]}",
                    "report_id": report_id,
                    "well_id": chunk_meta.get("well_id") or page_meta.get("well_id"),
                    "well_name": chunk_meta.get("well_name") or page_meta.get("well_name"),
                    "report_name": filename,
                    "report_type": report_type,
                    "page": page_num,
                    "source_file": source_file,
                    "event_type": chunk_meta.get("event_type") or page_meta.get("event_type"),
                    "formation": chunk_meta.get("formation") or page_meta.get("formation"),
                    "depth": chunk_meta.get("depth") or page_meta.get("depth"),
                    "severity": chunk_meta.get("severity") or page_meta.get("severity"),
                    "text": chunk_text
                }
                chunks.append(chunk_obj)

        return chunks

    def _split_text(self, text: str) -> List[str]:
        """Splits text using paragraph boundaries with sliding window fallback."""
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if not current_chunk:
                current_chunk = para
            elif len(current_chunk) + len(para) + 2 <= self.chunk_size:
                current_chunk += "\n\n" + para
            else:
                chunks.append(current_chunk)
                # Overlap: keep the tail of current_chunk if long enough
                overlap_text = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else ""
                current_chunk = (overlap_text + "\n\n" + para).strip()

        if current_chunk and len(current_chunk.strip()) >= 40:
            chunks.append(current_chunk)

        # If document had no double newlines, fallback to windowing
        if not chunks:
            words = text.split()
            current_words = []
            for word in words:
                current_words.append(word)
                if len(" ".join(current_words)) >= self.chunk_size:
                    chunks.append(" ".join(current_words))
                    # Overlap ~20 words
                    current_words = current_words[-20:]
            if current_words and len(" ".join(current_words)) >= 40:
                chunks.append(" ".join(current_words))

        return chunks

    @staticmethod
    def _infer_report_type(filename: str) -> str:
        """Determines report category from filename."""
        fn = filename.upper()
        if "DDR" in fn or "DAILY" in fn:
            return "DDR"
        elif "WCR" in fn or "COMPLETION" in fn:
            return "WCR"
        elif "MUD" in fn:
            return "MUD_LOG"
        elif "INCIDENT" in fn or "HAZARD" in fn:
            return "INCIDENT_REPORT"
        elif "DRILLING" in fn:
            return "DRILLING_REPORT"
        return "GENERAL_REPORT"

    @staticmethod
    def _extract_chunk_specific_meta(text: str, fallback_meta: Dict[str, Any]) -> Dict[str, Any]:
        """Refines event and depth metadata specifically mentioned inside the chunk."""
        meta = {}
        # Match event type in chunk
        for et in ["MUD_LOSS", "STUCK_PIPE", "KICK", "TORQUE_SPIKE", "CEMENTING_ISSUE", "LOST_CIRCULATION", "HIGH_PRESSURE", "NPT"]:
            pattern = r"\b" + re.escape(et).replace("_", r"[\s_-]?") + r"\b"
            if re.search(pattern, text, re.IGNORECASE):
                meta["event_type"] = et
                break

        # Match depth in chunk
        depth_match = re.search(r"\b(\d{3,4}(?:\.\d+)?)\s*(?:m|meters)\b", text, re.IGNORECASE)
        if depth_match:
            try:
                meta["depth"] = float(depth_match.group(1))
            except ValueError:
                pass

        return meta
