"""
===============================================================================
NWIS Document Processor - PDF Text Extraction & OCR Fallback
===============================================================================
Handles PDF and plain text documents:
1. Primary extraction via PyMuPDF (fitz)
2. OCR fallback via pytesseract for scanned / rasterized pages
3. Text cleaning and operational metadata preservation (well, depth, formation,
   incident types, severity, causes, mitigations)
===============================================================================
"""

import os
import re
from typing import List, Dict, Any, Optional

# PyMuPDF import
try:
    import pymupdf as fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    try:
        import fitz
        PYMUPDF_AVAILABLE = True
    except ImportError:
        PYMUPDF_AVAILABLE = False

# Optional Tesseract / Pillow import
try:
    import pytesseract
    from PIL import Image
    import io
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


class DocumentProcessor:
    """Extracts, cleans, and structures text from PDF and text drilling reports."""

    def __init__(self, tesseract_cmd: Optional[str] = None):
        if tesseract_cmd and OCR_AVAILABLE:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def extract_document(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extracts pages from a PDF or text file with automated OCR fallback
        for scanned or low-text PDF pages.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document file not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            return self._extract_pdf(file_path)
        elif ext in [".txt", ".log", ".md"]:
            return self._extract_text_file(file_path)
        else:
            raise ValueError(f"Unsupported document format: {ext}. Expected .pdf or .txt")

    def _extract_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extracts text page-by-page from PDF, triggering OCR when text is sparse."""
        if not PYMUPDF_AVAILABLE:
            return self._extract_pdf_fallback(pdf_path)

        pages = []
        doc = fitz.open(pdf_path)

        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                method = "PyMuPDF"

                # Check if page text is insufficient (e.g. scanned image page)
                if len(text.strip()) < 50 and OCR_AVAILABLE:
                    ocr_text = self._ocr_page(page)
                    if ocr_text and len(ocr_text.strip()) >= 50:
                        text = ocr_text
                        method = "Tesseract OCR"

                cleaned_text = self.clean_text(text)
                metadata = self.extract_metadata_tags(cleaned_text, pdf_path)

                pages.append({
                    "page_number": page_num + 1,
                    "text": cleaned_text,
                    "extraction_method": method,
                    "metadata": metadata
                })
        finally:
            doc.close()

        return pages

    def _ocr_page(self, page: Any) -> str:
        """Renders PDF page to image and runs Tesseract OCR."""
        if not OCR_AVAILABLE:
            return ""
        try:
            pix = page.get_pixmap(dpi=200)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            text = pytesseract.image_to_string(img)
            return text
        except Exception:
            # If tesseract executable is missing, fail gracefully
            return ""

    def _extract_pdf_fallback(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extracts text streams directly from PDF files when PyMuPDF is unavailable."""
        with open(pdf_path, "rb") as f:
            content = f.read()

        text_pieces = []
        matches = re.findall(rb"\((.*?)\)", content)
        for m in matches:
            try:
                decoded = m.decode("latin-1", errors="ignore").replace("\\(", "(").replace("\\)", ")").replace("\\\\", "\\")
                if len(decoded.strip()) > 1:
                    text_pieces.append(decoded)
            except Exception:
                pass

        raw_text = "\n".join(text_pieces) if text_pieces else ""
        cleaned_text = self.clean_text(raw_text)
        metadata = self.extract_metadata_tags(cleaned_text, pdf_path)

        return [{
            "page_number": 1,
            "text": cleaned_text,
            "extraction_method": "PDF Stream Parser (Fallback)",
            "metadata": metadata
        }]

    def _extract_text_file(self, text_path: str) -> List[Dict[str, Any]]:
        """Reads plain text file as a single-page document."""
        with open(text_path, "r", encoding="utf-8", errors="replace") as f:
            raw_text = f.read()

        cleaned_text = self.clean_text(raw_text)
        metadata = self.extract_metadata_tags(cleaned_text, text_path)

        return [{
            "page_number": 1,
            "text": cleaned_text,
            "extraction_method": "Plain Text",
            "metadata": metadata
        }]

    @staticmethod
    def clean_text(text: str) -> str:
        """Normalizes whitespaces, strips junk characters, and standardizes lines."""
        if not text:
            return ""

        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Remove repetitive header/separator lines like '=========' or '--------'
        text = re.sub(r"^[=\-_*~]{4,}\s*$", "", text, flags=re.MULTILINE)

        # Remove excessive whitespace within lines
        text = re.sub(r"[ \t]+", " ", text)

        # Remove excessive blank lines (>2 blank lines -> 1 blank line)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    @staticmethod
    def extract_metadata_tags(text: str, filename: str) -> Dict[str, Any]:
        """
        Extracts operational drilling metadata (well, formation, depth, events)
        from document text and filename.
        """
        metadata: Dict[str, Any] = {
            "well_name": None,
            "well_id": None,
            "formation": None,
            "depth": None,
            "event_type": None,
            "severity": None,
        }

        # 1. Match Well Name (e.g. NWIS-W002)
        well_match = re.search(r"NWIS-W(\d{3})", text + " " + filename, re.IGNORECASE)
        if well_match:
            well_num = int(well_match.group(1))
            metadata["well_name"] = f"NWIS-W{well_num:03d}"
            metadata["well_id"] = well_num

        # 2. Match Formation
        formations = [
            "Demo-Alluvium",
            "Demo-Girujan Clay",
            "Demo-Girujan",
            "Demo-Tipam Sandstone",
            "Demo-Tipam",
            "Demo-Bokabil",
            "Demo-Barail",
            "Demo-Kopili Shale",
            "Demo-Kopili",
            "Demo-Sylhet Limestone"
        ]
        for f in formations:
            if re.search(r"\b" + re.escape(f) + r"\b", text, re.IGNORECASE):
                metadata["formation"] = f
                break

        # 3. Match Measured Depth (e.g. 2980m, 3520.5m)
        depth_match = re.search(r"\b(\d{3,4}(?:\.\d+)?)\s*(?:m|meters)\b", text, re.IGNORECASE)
        if depth_match:
            try:
                metadata["depth"] = float(depth_match.group(1))
            except ValueError:
                pass

        # 4. Match Event Type
        event_types = [
            "MUD_LOSS",
            "STUCK_PIPE",
            "KICK",
            "TORQUE_SPIKE",
            "CEMENTING_ISSUE",
            "LOST_CIRCULATION",
            "HIGH_PRESSURE",
            "NPT"
        ]
        for et in event_types:
            # Search for keyword or space-separated variant (e.g. 'MUD LOSS')
            pattern = r"\b" + re.escape(et).replace("_", r"[\s_-]?") + r"\b"
            if re.search(pattern, text, re.IGNORECASE):
                metadata["event_type"] = et
                break

        # 5. Match Severity
        severities = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        for sev in severities:
            if re.search(r"\bseverity(?:\s+level)?\s*[:=-]?\s*" + sev + r"\b", text, re.IGNORECASE):
                metadata["severity"] = sev
                break
        if not metadata["severity"]:
            for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                if re.search(r"\b" + sev + r"\s+severity\b", text, re.IGNORECASE):
                    metadata["severity"] = sev
                    break

        return metadata
