"""Text extraction implementations for different frameworks."""

from __future__ import annotations

import sys
from pathlib import Path

if sys.version_info >= (3, 13):
    pass
else:
    pass

try:
    import kreuzberg
    from kreuzberg import ExtractionConfig, PSMMode, TesseractConfig
except ImportError:
    kreuzberg = None  # type: ignore[assignment]
    ExtractionConfig = None  # type: ignore[assignment,misc]
    TesseractConfig = None  # type: ignore[assignment,misc]
    PSMMode = None  # type: ignore[assignment,misc]

try:
    from kreuzberg import EasyOCRConfig
except ImportError:
    EasyOCRConfig = None  # type: ignore[assignment,misc]

try:
    from kreuzberg import PaddleOCRConfig
except ImportError:
    PaddleOCRConfig = None  # type: ignore[assignment,misc]

try:
    from docling.document_converter import DocumentConverter
except ImportError:
    DocumentConverter = None  # type: ignore[assignment,misc]

try:
    from markitdown import MarkItDown
except ImportError:
    MarkItDown = None  # type: ignore[assignment,misc]


try:
    from unstructured.partition.auto import partition
except ImportError:
    partition = None  # type: ignore[assignment]


try:
    from extractous import Extractor
except ImportError:
    Extractor = None  # type: ignore[assignment,misc]

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None  # type: ignore[assignment]

try:
    import pdfplumber
except ImportError:
    pdfplumber = None  # type: ignore[assignment]

from typing import Any

from .types import AsyncExtractorProtocol, ExtractorProtocol


def get_language_config(file_path: str | Path) -> str:
    """Determine language configuration based on file path and content hints.

    Returns language codes appropriate for the framework being used.
    For Tesseract: eng, deu, heb, chi_sim, jpn, kor
    For EasyOCR: en, de, he, ch_sim, ja, ko
    For PaddleOCR: en, german, ch, japan, korean
    """
    file_path = Path(file_path)
    filename = file_path.name.lower()

    # Check for specific language indicators in filename
    if any(x in filename for x in ["hebrew", "israel", "tel_aviv", "heb", "he_"]):
        return "heb"  # Hebrew
    if any(x in filename for x in ["german", "germany", "berlin", "deu", "de_"]):
        return "deu"  # German
    if any(x in filename for x in ["chinese", "china", "beijing", "chi_sim", "zh_", "cn_"]):
        return "chi_sim"  # Simplified Chinese
    if any(x in filename for x in ["japanese", "japan", "jpn", "jp_", "ja_", "vert"]):  # jpn-vert.jpeg
        return "jpn"  # Japanese
    if any(x in filename for x in ["korean", "korea", "kor", "kr_", "ko_"]):
        return "kor"  # Korean
    # Default to English only for better performance
    return "eng"  # English


class KreuzbergSyncExtractor:
    """Synchronous Kreuzberg text extractor."""

    def extract_text(self, file_path: str) -> str:
        """Extract text using Kreuzberg synchronously."""
        if kreuzberg is None:
            msg = "Kreuzberg is not installed"
            raise ImportError(msg)
        result = kreuzberg.extract_file_sync(file_path)
        return result.content

    def extract_with_metadata(self, file_path: str) -> tuple[str, dict[str, Any]]:
        """Extract text and metadata using Kreuzberg synchronously."""
        if kreuzberg is None:
            msg = "Kreuzberg is not installed"
            raise ImportError(msg)
        result = kreuzberg.extract_file_sync(file_path)
        # Convert metadata to dict if it's a TypedDict
        metadata = dict(result.metadata) if hasattr(result, "metadata") else {}
        return result.content, metadata


class KreuzbergAsyncExtractor:
    """Asynchronous Kreuzberg text extractor."""

    async def extract_text(self, file_path: str) -> str:
        """Extract text using Kreuzberg asynchronously."""
        if kreuzberg is None:
            msg = "Kreuzberg is not installed"
            raise ImportError(msg)
        result = await kreuzberg.extract_file(file_path)
        return result.content

    async def extract_with_metadata(self, file_path: str) -> tuple[str, dict[str, Any]]:
        """Extract text and metadata using Kreuzberg asynchronously."""
        if kreuzberg is None:
            msg = "Kreuzberg is not installed"
            raise ImportError(msg)
        result = await kreuzberg.extract_file(file_path)
        # Convert metadata to dict if it's a TypedDict
        metadata = dict(result.metadata) if hasattr(result, "metadata") else {}
        return result.content, metadata


class DoclingExtractor:
    """Docling text extractor."""

    def __init__(self) -> None:
        """Initialize Docling converter with minimal configuration.

        Note: We use mostly default settings to provide fair comparison,
        only applying the recommended faster PDF backend which is a
        configuration option rather than disabling features.
        """
        if DocumentConverter is None:
            msg = "Docling is not installed"
            raise ImportError(msg)

        # Try to use the faster PDF backend if available (recommended best practice)
        try:
            from docling.datamodel.base_models import InputFormat
            from docling.format_options import PdfFormatOption
            from docling.pdf_backend import DoclingParseV2DocumentBackend

            # Use faster PDF backend (DoclingParseV2) which is ~10x faster
            # This is a recommended configuration, not disabling features
            self.converter = DocumentConverter(
                format_options={InputFormat.PDF: PdfFormatOption(backend=DoclingParseV2DocumentBackend)}
            )
        except ImportError:
            # Fallback to completely default converter if imports fail
            self.converter = DocumentConverter()

    def extract_text(self, file_path: str) -> str:
        """Extract text using Docling."""
        # Docling handles language detection automatically
        # No explicit language configuration needed
        result = self.converter.convert(file_path)
        # Use text export instead of markdown for better performance
        return result.document.export_to_text()

    def extract_with_metadata(self, file_path: str) -> tuple[str, dict[str, Any]]:
        """Extract text and metadata using Docling."""
        result = self.converter.convert(file_path)
        text = result.document.export_to_text()

        # Extract metadata from Docling result
        metadata = {}
        if hasattr(result.document, "origin"):
            metadata["origin"] = {
                "mimetype": getattr(result.document.origin, "mimetype", None),
                "binary_hash": getattr(result.document.origin, "binary_hash", None),
                "filename": getattr(result.document.origin, "filename", None),
            }
        if hasattr(result.document, "pages"):
            metadata["page_count"] = len(result.document.pages)

        return text, metadata


class MarkItDownExtractor:
    """MarkItDown text extractor."""

    def __init__(self) -> None:
        """Initialize MarkItDown converter."""
        if MarkItDown is None:
            msg = "MarkItDown is not installed"
            raise ImportError(msg)
        self.converter = MarkItDown()

    def extract_text(self, file_path: str) -> str:
        """Extract text using MarkItDown."""
        # MarkItDown uses ONNX models that handle multiple languages automatically
        # No explicit language configuration available
        result = self.converter.convert(file_path)
        return result.text_content

    def extract_with_metadata(self, file_path: str) -> tuple[str, dict[str, Any]]:
        """Extract text and metadata using MarkItDown."""
        result = self.converter.convert(file_path)
        metadata = {}
        # MarkItDown has minimal metadata - check for title
        if hasattr(result, "title") and result.title:
            metadata["title"] = result.title
        return result.text_content, metadata


class KreuzbergTesseractExtractor:
    """Kreuzberg with Tesseract OCR backend."""

    def extract_text(self, file_path: str) -> str:
        """Extract text using Kreuzberg with Tesseract OCR."""
        if kreuzberg is None or TesseractConfig is None:
            msg = "Kreuzberg is not installed"
            raise ImportError(msg)

        # Detect language from filename
        lang_code = get_language_config(file_path)

        # Use default configuration
        config = ExtractionConfig(
            ocr_backend="tesseract",
            ocr_config=TesseractConfig(language=lang_code),
        )

        result = kreuzberg.extract_file_sync(file_path, config=config)
        return result.content

    def extract_with_metadata(self, file_path: str) -> tuple[str, dict[str, Any]]:
        """Extract text and metadata using Kreuzberg with Tesseract OCR."""
        if kreuzberg is None or TesseractConfig is None:
            msg = "Kreuzberg is not installed"
            raise ImportError(msg)

        lang_code = get_language_config(file_path)
        config = ExtractionConfig(
            ocr_backend="tesseract",
            ocr_config=TesseractConfig(language=lang_code),
        )

        result = kreuzberg.extract_file_sync(file_path, config=config)
        metadata = dict(result.metadata) if hasattr(result, "metadata") else {}
        return result.content, metadata


class KreuzbergEasyOCRExtractor:
    """Kreuzberg with EasyOCR backend (async only)."""

    async def extract_text(self, file_path: str) -> str:
        """Extract text using Kreuzberg with EasyOCR."""
        if kreuzberg is None or EasyOCRConfig is None:
            msg = "Kreuzberg with EasyOCR is not installed. Install with: pip install kreuzberg[easyocr]"
            raise ImportError(msg)

        # Map language codes for EasyOCR
        lang_code = get_language_config(file_path)
        easyocr_langs = {
            "eng": "en",
            "deu": "de",
            "heb": "en",  # Hebrew not supported, fallback to English
            "chi_sim": "ch_sim",
            "jpn": "ja",
            "kor": "ko",
        }

        easyocr_lang = easyocr_langs.get(lang_code, "en")

        # Default EasyOCR configuration
        config = ExtractionConfig(
            ocr_backend="easyocr",
            ocr_config=EasyOCRConfig(
                language=easyocr_lang,
                use_gpu=False,  # CPU-only for fair benchmarking
            ),
        )

        result = await kreuzberg.extract_file(file_path, config=config)
        return result.content

    async def extract_with_metadata(self, file_path: str) -> tuple[str, dict[str, Any]]:
        """Extract text and metadata using Kreuzberg with EasyOCR."""
        if kreuzberg is None or EasyOCRConfig is None:
            msg = "Kreuzberg with EasyOCR is not installed. Install with: pip install kreuzberg[easyocr]"
            raise ImportError(msg)

        lang_code = get_language_config(file_path)
        easyocr_langs = {
            "eng": "en",
            "deu": "de",
            "heb": "en",  # Hebrew not supported, fallback to English
            "chi_sim": "ch_sim",
            "jpn": "ja",
            "kor": "ko",
        }

        easyocr_lang = easyocr_langs.get(lang_code, "en")
        config = ExtractionConfig(
            ocr_backend="easyocr",
            ocr_config=EasyOCRConfig(
                language=easyocr_lang,
                use_gpu=False,
            ),
        )

        result = await kreuzberg.extract_file(file_path, config=config)
        metadata = dict(result.metadata) if hasattr(result, "metadata") else {}
        return result.content, metadata


class KreuzbergPaddleOCRExtractor:
    """Kreuzberg with PaddleOCR backend (async only)."""

    async def extract_text(self, file_path: str) -> str:
        """Extract text using Kreuzberg with PaddleOCR."""
        if kreuzberg is None or PaddleOCRConfig is None:
            msg = "Kreuzberg with PaddleOCR is not installed. Install with: pip install kreuzberg[paddleocr]"
            raise ImportError(msg)

        # Map language codes for PaddleOCR
        lang_code = get_language_config(file_path)
        paddle_langs = {
            "eng": "en",
            "deu": "german",
            "chi_sim": "ch",
            "jpn": "japan",
            "kor": "korean",
            "eng+deu+fra": "en",  # PaddleOCR doesn't support multiple languages
        }

        paddle_lang = paddle_langs.get(lang_code, "en")

        # Default PaddleOCR configuration
        config = ExtractionConfig(
            ocr_backend="paddleocr",
            ocr_config=PaddleOCRConfig(
                language=paddle_lang,
                use_gpu=False,  # CPU-only for fair benchmarking
            ),
        )

        result = await kreuzberg.extract_file(file_path, config=config)
        return result.content

    async def extract_with_metadata(self, file_path: str) -> tuple[str, dict[str, Any]]:
        """Extract text and metadata using Kreuzberg with PaddleOCR."""
        if kreuzberg is None or PaddleOCRConfig is None:
            msg = "Kreuzberg with PaddleOCR is not installed. Install with: pip install kreuzberg[paddleocr]"
            raise ImportError(msg)

        lang_code = get_language_config(file_path)
        paddle_langs = {
            "eng": "en",
            "deu": "german",
            "chi_sim": "ch",
            "jpn": "japan",
            "kor": "korean",
            "eng+deu+fra": "en",
        }

        paddle_lang = paddle_langs.get(lang_code, "en")
        config = ExtractionConfig(
            ocr_backend="paddleocr",
            ocr_config=PaddleOCRConfig(
                language=paddle_lang,
                use_gpu=False,
            ),
        )

        result = await kreuzberg.extract_file(file_path, config=config)
        metadata = dict(result.metadata) if hasattr(result, "metadata") else {}
        return result.content, metadata


class KreuzbergEasyOCRSyncExtractor:
    """Kreuzberg with EasyOCR backend (synchronous)."""

    def extract_text(self, file_path: str) -> str:
        """Extract text using Kreuzberg with EasyOCR synchronously."""
        if kreuzberg is None or EasyOCRConfig is None:
            msg = "Kreuzberg with EasyOCR is not installed. Install with: pip install kreuzberg[easyocr]"
            raise ImportError(msg)

        # Map language codes for EasyOCR
        lang_code = get_language_config(file_path)
        easyocr_langs = {
            "eng": "en",
            "deu": "de",
            "heb": "en",  # Hebrew not supported, fallback to English
            "chi_sim": "ch_sim",
            "jpn": "ja",
            "kor": "ko",
        }

        easyocr_lang = easyocr_langs.get(lang_code, "en")

        # Default EasyOCR configuration
        config = ExtractionConfig(
            ocr_backend="easyocr",
            ocr_config=EasyOCRConfig(
                language=easyocr_lang,
                use_gpu=False,  # CPU-only for fair benchmarking
            ),
        )

        result = kreuzberg.extract_file_sync(file_path, config=config)
        return result.content

    def extract_with_metadata(self, file_path: str) -> tuple[str, dict[str, Any]]:
        """Extract text and metadata using Kreuzberg with EasyOCR synchronously."""
        if kreuzberg is None or EasyOCRConfig is None:
            msg = "Kreuzberg with EasyOCR is not installed. Install with: pip install kreuzberg[easyocr]"
            raise ImportError(msg)

        lang_code = get_language_config(file_path)
        easyocr_langs = {
            "eng": "en",
            "deu": "de",
            "heb": "en",
            "chi_sim": "ch_sim",
            "jpn": "ja",
            "kor": "ko",
        }

        easyocr_lang = easyocr_langs.get(lang_code, "en")
        config = ExtractionConfig(
            ocr_backend="easyocr",
            ocr_config=EasyOCRConfig(
                language=easyocr_lang,
                use_gpu=False,
            ),
        )

        result = kreuzberg.extract_file_sync(file_path, config=config)
        metadata = dict(result.metadata) if hasattr(result, "metadata") else {}
        return result.content, metadata


class KreuzbergPaddleOCRSyncExtractor:
    """Kreuzberg with PaddleOCR backend (synchronous)."""

    def extract_text(self, file_path: str) -> str:
        """Extract text using Kreuzberg with PaddleOCR synchronously."""
        if kreuzberg is None or PaddleOCRConfig is None:
            msg = "Kreuzberg with PaddleOCR is not installed. Install with: pip install kreuzberg[paddleocr]"
            raise ImportError(msg)

        # Map language codes for PaddleOCR
        lang_code = get_language_config(file_path)
        paddleocr_langs = {
            "eng": "en",
            "deu": "german",
            "heb": "en",  # Hebrew not fully supported, fallback to English
            "chi_sim": "ch",
            "jpn": "japan",
            "kor": "korean",
        }

        paddleocr_lang = paddleocr_langs.get(lang_code, "en")

        # Default PaddleOCR configuration
        config = ExtractionConfig(
            ocr_backend="paddleocr",
            ocr_config=PaddleOCRConfig(
                language=paddleocr_lang,
                use_gpu=False,  # CPU-only for fair benchmarking
            ),
        )

        result = kreuzberg.extract_file_sync(file_path, config=config)
        return result.content

    def extract_with_metadata(self, file_path: str) -> tuple[str, dict[str, Any]]:
        """Extract text and metadata using Kreuzberg with PaddleOCR synchronously."""
        if kreuzberg is None or PaddleOCRConfig is None:
            msg = "Kreuzberg with PaddleOCR is not installed. Install with: pip install kreuzberg[paddleocr]"
            raise ImportError(msg)

        lang_code = get_language_config(file_path)
        paddleocr_langs = {
            "eng": "en",
            "deu": "german",
            "chi_sim": "ch",
            "jpn": "japan",
            "kor": "korean",
            "eng+deu+fra": "en",
        }

        paddle_lang = paddleocr_langs.get(lang_code, "en")
        config = ExtractionConfig(
            ocr_backend="paddleocr",
            ocr_config=PaddleOCRConfig(
                language=paddle_lang,
                use_gpu=False,
            ),
        )

        result = kreuzberg.extract_file_sync(file_path, config=config)
        metadata = dict(result.metadata) if hasattr(result, "metadata") else {}
        return result.content, metadata


class UnstructuredExtractor:
    """Unstructured text extractor."""

    def extract_text(self, file_path: str) -> str:
        """Extract text using Unstructured."""
        if partition is None:
            msg = "Unstructured is not installed"
            raise ImportError(msg)

        # Configure languages for Unstructured
        lang_code = get_language_config(file_path)
        # Unstructured uses ISO 639-1 codes
        unstructured_langs = {
            "eng": ["eng"],
            "deu": ["deu"],
            "heb": ["heb"],
            "chi_sim": ["chi"],
            "jpn": ["jpn"],
            "kor": ["kor"],
            "eng+deu+fra": ["eng", "deu", "fra"],
        }

        languages = unstructured_langs.get(lang_code, ["eng"])

        # Unstructured auto-detects OCR needs and language
        elements = partition(filename=file_path, languages=languages)
        return "\n".join(str(element) for element in elements)

    def extract_with_metadata(self, file_path: str) -> tuple[str, dict[str, Any]]:
        """Extract text and metadata using Unstructured."""
        if partition is None:
            msg = "Unstructured is not installed"
            raise ImportError(msg)

        lang_code = get_language_config(file_path)
        unstructured_langs = {
            "eng": ["eng"],
            "deu": ["deu"],
            "heb": ["heb"],
            "chi_sim": ["chi"],
            "jpn": ["jpn"],
            "kor": ["kor"],
            "eng+deu+fra": ["eng", "deu", "fra"],
        }

        languages = unstructured_langs.get(lang_code, ["eng"])
        elements = partition(filename=file_path, languages=languages)

        # Extract text
        text = "\n".join(str(element) for element in elements)

        # Extract metadata - Unstructured provides rich element-level metadata
        metadata = {}
        if elements:
            # Get file-level metadata from first element
            first_elem = elements[0]
            if hasattr(first_elem, "metadata"):
                elem_meta = first_elem.metadata
                # Extract common metadata fields
                if hasattr(elem_meta, "filename"):
                    metadata["filename"] = elem_meta.filename
                if hasattr(elem_meta, "file_directory"):
                    metadata["file_directory"] = elem_meta.file_directory
                if hasattr(elem_meta, "last_modified"):
                    metadata["last_modified"] = str(elem_meta.last_modified) if elem_meta.last_modified else None
                if hasattr(elem_meta, "filetype"):
                    metadata["filetype"] = elem_meta.filetype
                if hasattr(elem_meta, "page_number"):
                    metadata["page_number"] = elem_meta.page_number
                if hasattr(elem_meta, "languages"):
                    metadata["languages"] = elem_meta.languages

            # Count element types
            element_types = {}
            for elem in elements:
                elem_type = type(elem).__name__
                element_types[elem_type] = element_types.get(elem_type, 0) + 1
            metadata["element_types"] = element_types
            metadata["total_elements"] = len(elements)

        return text, metadata


class ExtractousExtractor:
    """Extractous text extractor."""

    def __init__(self) -> None:
        """Initialize Extractous extractor with optimal configuration."""
        if Extractor is None:
            msg = "Extractous is not installed. Install with: pip install extractous"
            raise ImportError(msg)

        # Configure with performance optimizations
        self.extractor = Extractor()

        # Set reasonable limits for text extraction
        self.extractor.set_extract_string_max_length(1000000)  # 1MB max text

    def extract_text(self, file_path: str) -> str:
        """Extract text using Extractous."""
        # Get language configuration for potential OCR
        lang_code = get_language_config(file_path)

        # Configure OCR if needed (for images and scanned documents)
        try:
            from extractous import TesseractOcrConfig

            # Map language codes for Tesseract OCR
            tesseract_langs = {
                "eng": "eng",
                "deu": "deu",
                "heb": "heb",
                "chi_sim": "chi_sim",
                "jpn": "jpn",
                "kor": "kor",
            }

            tesseract_lang = tesseract_langs.get(lang_code, "eng")

            # Configure OCR for image-based documents
            ocr_config = TesseractOcrConfig().set_language(tesseract_lang)
            self.extractor.set_ocr_config(ocr_config)

        except ImportError:
            # OCR config not available, use without OCR
            pass

        # Extract text directly to string (returns tuple of text and metadata)
        result = self.extractor.extract_file_to_string(file_path)
        return result[0] if isinstance(result, tuple) else result

    def extract_with_metadata(self, file_path: str) -> tuple[str, dict[str, Any]]:
        """Extract text and metadata using Extractous."""
        # Extractous returns a tuple of (text, metadata) from extract_file_to_string
        result = self.extractor.extract_file_to_string(file_path)

        if isinstance(result, tuple) and len(result) >= 2:
            text, raw_metadata = result[0], result[1]
            # Convert metadata to dict if it's not already
            metadata = dict(raw_metadata) if raw_metadata else {}
        else:
            # Fallback if result format is unexpected
            text = result[0] if isinstance(result, tuple) else result
            metadata = {}

        return text, metadata


class PyMuPDFExtractor:
    """PyMuPDF (fitz) text extractor for PDF documents."""

    def __init__(self) -> None:
        """Initialize PyMuPDF extractor."""
        if fitz is None:
            msg = "PyMuPDF is not installed. Install with: pip install PyMuPDF"
            raise ImportError(msg)

    def extract_text(self, file_path: str) -> str:
        """Extract text using PyMuPDF."""
        try:
            # Open the document
            doc = fitz.open(file_path)
            text_parts = []

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                # Extract text with layout preservation
                text = page.get_text()
                if text.strip():  # Only add non-empty pages
                    text_parts.append(text)

            doc.close()
            return "\n\n".join(text_parts)

        except Exception as e:
            # If not a PDF or other error, return empty string
            return ""

    def extract_with_metadata(self, file_path: str) -> tuple[str, dict[str, Any]]:
        """Extract text and metadata using PyMuPDF."""
        try:
            doc = fitz.open(file_path)
            text_parts = []

            # Extract text
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text.strip():
                    text_parts.append(text)

            # Extract metadata
            metadata = {}
            doc_metadata = doc.metadata
            if doc_metadata:
                metadata.update(
                    {
                        "title": doc_metadata.get("title", ""),
                        "author": doc_metadata.get("author", ""),
                        "subject": doc_metadata.get("subject", ""),
                        "creator": doc_metadata.get("creator", ""),
                        "producer": doc_metadata.get("producer", ""),
                        "creation_date": doc_metadata.get("creationDate", ""),
                        "modification_date": doc_metadata.get("modDate", ""),
                    }
                )

            metadata["page_count"] = len(doc)
            metadata["file_type"] = "pdf"

            doc.close()
            return "\n\n".join(text_parts), metadata

        except Exception:
            return "", {}


class PDFPlumberExtractor:
    """PDFPlumber text extractor specialized for PDF documents."""

    def __init__(self) -> None:
        """Initialize PDFPlumber extractor."""
        if pdfplumber is None:
            msg = "pdfplumber is not installed. Install with: pip install pdfplumber"
            raise ImportError(msg)

    def extract_text(self, file_path: str) -> str:
        """Extract text using pdfplumber."""
        try:
            text_parts = []

            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    # Extract text preserving layout
                    text = page.extract_text()
                    if text and text.strip():
                        text_parts.append(text)

            return "\n\n".join(text_parts)

        except Exception:
            # If not a PDF or other error, return empty string
            return ""

    def extract_with_metadata(self, file_path: str) -> tuple[str, dict[str, Any]]:
        """Extract text and metadata using pdfplumber."""
        try:
            text_parts = []
            metadata = {"tables": [], "file_type": "pdf"}

            with pdfplumber.open(file_path) as pdf:
                # Extract basic metadata
                if hasattr(pdf, "metadata") and pdf.metadata:
                    metadata.update(
                        {
                            "title": pdf.metadata.get("Title", ""),
                            "author": pdf.metadata.get("Author", ""),
                            "subject": pdf.metadata.get("Subject", ""),
                            "creator": pdf.metadata.get("Creator", ""),
                            "producer": pdf.metadata.get("Producer", ""),
                            "creation_date": str(pdf.metadata.get("CreationDate", "")),
                            "modification_date": str(pdf.metadata.get("ModDate", "")),
                        }
                    )

                metadata["page_count"] = len(pdf.pages)

                for page_num, page in enumerate(pdf.pages):
                    # Extract text
                    text = page.extract_text()
                    if text and text.strip():
                        text_parts.append(text)

                    # Extract tables (pdfplumber's specialty)
                    tables = page.extract_tables()
                    if tables:
                        for table_idx, table in enumerate(tables):
                            if table:  # table is not None and not empty
                                metadata["tables"].append(
                                    {
                                        "page": page_num + 1,
                                        "table_index": table_idx,
                                        "rows": len(table),
                                        "columns": len(table[0]) if table else 0,
                                        "data": table[:3] if len(table) > 3 else table,  # Sample first 3 rows
                                    }
                                )

                metadata["table_count"] = len(metadata["tables"])

            return "\n\n".join(text_parts), metadata

        except Exception:
            return "", {}


def get_extractor(framework: str) -> ExtractorProtocol | AsyncExtractorProtocol:
    """Get an extractor instance for the specified framework.

    Args:
        framework: The framework name to get an extractor for.

    Returns:
        An extractor instance.

    Raises:
        ValueError: If the framework is not supported.
    """
    extractors = {
        "kreuzberg_sync": KreuzbergSyncExtractor,
        "kreuzberg_async": KreuzbergAsyncExtractor,
        "kreuzberg_tesseract": KreuzbergTesseractExtractor,
        "kreuzberg_easyocr": KreuzbergEasyOCRExtractor,
        "kreuzberg_easyocr_sync": KreuzbergEasyOCRSyncExtractor,
        "kreuzberg_paddleocr": KreuzbergPaddleOCRExtractor,
        "kreuzberg_paddleocr_sync": KreuzbergPaddleOCRSyncExtractor,
        "docling": DoclingExtractor,
        "markitdown": MarkItDownExtractor,
        "unstructured": UnstructuredExtractor,
        "extractous": ExtractousExtractor,
        "pymupdf": PyMuPDFExtractor,
        "pdfplumber": PDFPlumberExtractor,
    }

    if framework not in extractors:
        msg = f"Unsupported framework: {framework}"
        raise ValueError(msg)

    return extractors[framework]()  # type: ignore[return-value]
