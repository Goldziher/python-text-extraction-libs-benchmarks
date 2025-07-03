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


class KreuzbergAsyncExtractor:
    """Asynchronous Kreuzberg text extractor."""

    async def extract_text(self, file_path: str) -> str:
        """Extract text using Kreuzberg asynchronously."""
        if kreuzberg is None:
            msg = "Kreuzberg is not installed"
            raise ImportError(msg)
        result = await kreuzberg.extract_file(file_path)
        return result.content


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
    }

    if framework not in extractors:
        msg = f"Unsupported framework: {framework}"
        raise ValueError(msg)

    return extractors[framework]()  # type: ignore[return-value]
