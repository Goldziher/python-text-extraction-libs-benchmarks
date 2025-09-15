"""Text extraction implementations for different frameworks."""

from __future__ import annotations

import os
import signal
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


from typing import Any, Never

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

    if any(x in filename for x in ["hebrew", "israel", "tel_aviv", "heb", "he_"]):
        return "heb"
    if any(x in filename for x in ["german", "germany", "berlin", "deu", "de_"]):
        return "deu"
    if any(x in filename for x in ["chinese", "china", "beijing", "chi_sim", "zh_", "cn_"]):
        return "chi_sim"
    if any(x in filename for x in ["japanese", "japan", "jpn", "jp_", "ja_", "vert"]):
        return "jpn"
    if any(x in filename for x in ["korean", "korea", "kor", "kr_", "ko_"]):
        return "kor"
    return "eng"


class KreuzbergSyncExtractor:
    """Synchronous Kreuzberg text extractor with optimized configuration."""

    def extract_text(self, file_path: str) -> str:
        """Extract text using Kreuzberg synchronously."""
        if kreuzberg is None:
            msg = "Kreuzberg is not installed"
            raise ImportError(msg)
        config = self._get_optimized_config(file_path)
        result = kreuzberg.extract_file_sync(file_path, config=config)
        return result.content

    def extract_with_metadata(self, file_path: str) -> tuple[str, dict[str, Any]]:
        """Extract text and metadata using Kreuzberg synchronously."""
        if kreuzberg is None:
            msg = "Kreuzberg is not installed"
            raise ImportError(msg)
        config = self._get_optimized_config(file_path)
        result = kreuzberg.extract_file_sync(file_path, config=config)
        metadata = dict(result.metadata) if hasattr(result, "metadata") else {}
        return result.content, metadata

    def _get_optimized_config(self, file_path: str) -> ExtractionConfig:
        """Get optimized configuration for sync extraction with high-quality Tesseract settings."""
        lang_code = get_language_config(file_path)

        tesseract_config = TesseractConfig(language=lang_code, psm=PSMMode.AUTO, output_format="text")

        return ExtractionConfig(ocr_backend="tesseract", ocr_config=tesseract_config, use_cache=False)


class KreuzbergAsyncExtractor:
    """Asynchronous Kreuzberg text extractor with optimized configuration."""

    async def extract_text(self, file_path: str) -> str:
        """Extract text using Kreuzberg asynchronously."""
        if kreuzberg is None:
            msg = "Kreuzberg is not installed"
            raise ImportError(msg)
        config = self._get_optimized_config(file_path)
        result = await kreuzberg.extract_file(file_path, config=config)
        return result.content

    async def extract_with_metadata(self, file_path: str) -> tuple[str, dict[str, Any]]:
        """Extract text and metadata using Kreuzberg asynchronously."""
        if kreuzberg is None:
            msg = "Kreuzberg is not installed"
            raise ImportError(msg)
        config = self._get_optimized_config(file_path)
        result = await kreuzberg.extract_file(file_path, config=config)
        metadata = dict(result.metadata) if hasattr(result, "metadata") else {}
        return result.content, metadata

    def _get_optimized_config(self, file_path: str) -> ExtractionConfig:
        """Get optimized configuration for async extraction with high-quality Tesseract settings."""
        lang_code = get_language_config(file_path)

        tesseract_config = TesseractConfig(language=lang_code, psm=PSMMode.AUTO, output_format="text")

        return ExtractionConfig(ocr_backend="tesseract", ocr_config=tesseract_config, use_cache=False)


class DoclingExtractor:
    """Docling text extractor with optimized configuration and robust error handling."""

    def __init__(self) -> None:
        """Initialize Docling converter with optimized configuration for performance and reliability."""
        if DocumentConverter is None:
            msg = "Docling is not installed"
            raise ImportError(msg)

        try:
            from docling.datamodel.base_models import InputFormat
            from docling.datamodel.pipeline_options import (
                EasyOcrOptions,
                LayoutOptions,
                TableStructureOptions,
                ThreadedPdfPipelineOptions,
            )

            ocr_options = EasyOcrOptions(
                lang=["en", "de", "fr", "es"], confidence_threshold=0.3, suppress_mps_warnings=True
            )

            table_options = TableStructureOptions(do_cell_matching=True, mode="accurate")

            layout_options = LayoutOptions(create_orphan_clusters=True, keep_empty_clusters=False)

            pdf_options = ThreadedPdfPipelineOptions(
                do_table_structure=True,
                do_ocr=True,
                do_picture_classification=False,
                do_picture_description=False,
                ocr_options=ocr_options,
                table_structure_options=table_options,
                layout_options=layout_options,
                ocr_batch_size=2,
                layout_batch_size=2,
                table_batch_size=2,
                batch_timeout_seconds=30.0,
                queue_max_size=50,
            )

            format_options = {InputFormat.PDF: pdf_options}

            self.converter = DocumentConverter(format_options=format_options)
            self.max_file_size = 1024 * 1024 * 1024
            self.timeout = 600

        except ImportError:
            self.converter = DocumentConverter()
            self.max_file_size = 1024 * 1024 * 1024
            self.timeout = 600

    def _validate_file(self, file_path: str) -> bool:
        """Validate file before processing."""
        try:
            path_obj = Path(file_path)
            if not path_obj.exists():
                return False

            file_size = path_obj.stat().st_size
            return not file_size > self.max_file_size
        except Exception:
            return False

    def extract_text(self, file_path: str) -> str:
        """Extract text using Docling with robust error handling."""
        if not self._validate_file(file_path):
            return ""

        try:
            result = self.converter.convert(file_path)
            text = result.document.export_to_text()
            return text if text else ""
        except Exception:
            return ""

    def extract_with_metadata(self, file_path: str) -> tuple[str, dict[str, Any]]:
        """Extract text and metadata using Docling with robust error handling."""
        if not self._validate_file(file_path):
            return "", {"error": "file_validation_failed"}

        try:
            result = self.converter.convert(file_path)
            text = result.document.export_to_text()
            text = text if text else ""

            metadata = {}
            if hasattr(result.document, "origin"):
                metadata["origin"] = {
                    "mimetype": getattr(result.document.origin, "mimetype", None),
                    "binary_hash": getattr(result.document.origin, "binary_hash", None),
                    "filename": getattr(result.document.origin, "filename", None),
                }
            if hasattr(result.document, "pages"):
                metadata["page_count"] = len(result.document.pages)

            if hasattr(result, "status"):
                metadata["extraction_status"] = str(result.status)

            try:
                file_size = Path(file_path).stat().st_size
                metadata["file_size_mb"] = round(file_size / 1024 / 1024, 2)
            except Exception:
                pass

            return text, metadata
        except Exception as e:
            return "", {"error": str(e)[:100]}


class MarkItDownExtractor:
    """MarkItDown text extractor with robust error handling and timeout management."""

    def __init__(self) -> None:
        """Initialize MarkItDown converter with optimized settings."""
        if MarkItDown is None:
            msg = "MarkItDown is not installed"
            raise ImportError(msg)

        self.converter = MarkItDown(enable_builtins=True)
        self.timeout = 90
        self.max_file_size = 100 * 1024 * 1024

    def _validate_file(self, file_path: str) -> bool:
        """Validate file before processing."""
        try:
            path_obj = Path(file_path)
            if not path_obj.exists():
                return False

            file_size = path_obj.stat().st_size
            if file_size > self.max_file_size:
                return False

            return os.access(file_path, os.R_OK)
        except Exception:
            return False

    def _extract_with_timeout(self, file_path: str) -> Any:
        """Extract with timeout protection."""

        def timeout_handler(signum: int, frame: Any) -> Never:  # noqa: ARG001
            raise TimeoutError(f"MarkItDown extraction timed out after {self.timeout}s")

        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(self.timeout)

        try:
            result = self.converter.convert(file_path)
            signal.alarm(0)
            return result
        except Exception as e:
            signal.alarm(0)
            raise e
        finally:
            signal.signal(signal.SIGALRM, old_handler)

    def extract_text(self, file_path: str) -> str:
        """Extract text using MarkItDown with robust error handling."""
        if not self._validate_file(file_path):
            return ""

        try:
            result = self._extract_with_timeout(file_path)
            return result.text_content if result.text_content else ""
        except TimeoutError:
            return ""
        except Exception:
            return ""

    def extract_with_metadata(self, file_path: str) -> tuple[str, dict[str, Any]]:
        """Extract text and metadata using MarkItDown with robust error handling."""
        if not self._validate_file(file_path):
            return "", {}

        try:
            result = self._extract_with_timeout(file_path)

            text = result.text_content if result.text_content else ""
            metadata = {}

            if hasattr(result, "title") and result.title:
                metadata["title"] = str(result.title)
            if hasattr(result, "content_type") and result.content_type:
                metadata["content_type"] = str(result.content_type)

            return text, metadata

        except TimeoutError:
            return "", {"error": "timeout"}
        except Exception as e:
            return "", {"error": str(e)[:100]}


class UnstructuredExtractor:
    """Unstructured text extractor with adaptive strategy selection and retry logic."""

    def __init__(self) -> None:
        """Initialize with strategy configuration."""
        self.max_retries = 2
        self.timeout = 180
        self.max_file_size = 150 * 1024 * 1024

    def _get_file_size(self, file_path: str) -> int:
        """Get file size safely."""
        try:
            return Path(file_path).stat().st_size
        except Exception:
            return 0

    def _get_adaptive_strategy(self, file_path: str, file_size: int) -> dict[str, Any]:
        """Select optimal strategy based on file characteristics."""
        lang_code = get_language_config(file_path)
        file_ext = Path(file_path).suffix.lower()

        unstructured_langs = {
            "eng": ["eng"],
            "deu": ["deu"],
            "heb": ["heb"],
            "chi_sim": ["chi_sim"],
            "jpn": ["jpn"],
            "kor": ["kor"],
        }
        languages = unstructured_langs.get(lang_code, ["eng"])

        config = {
            "languages": languages,
            "strategy": "auto",
            "include_metadata": True,
        }

        if file_size > 100 * 1024 * 1024:
            config["chunking_strategy"] = "by_title"
            config["max_characters"] = 10000
        elif file_size > 10 * 1024 * 1024:
            config["chunking_strategy"] = "basic"
            config["max_characters"] = 5000

        if file_ext in [".pdf"]:
            config["strategy"] = "hi_res"
            config["extract_images_in_pdf"] = False
        elif file_ext in [".docx", ".pptx", ".xlsx"]:
            config["strategy"] = "fast"
        elif file_ext in [".html", ".htm"]:
            config["strategy"] = "fast"
            config["skip_infer_table_types"] = True

        return config

    def _extract_with_strategy(self, file_path: str, config: dict[str, Any], attempt: int = 1) -> Any:
        """Extract with a specific strategy, with fallback options."""
        try:
            return partition(filename=file_path, **config)
        except Exception as e:
            if attempt < self.max_retries:
                if attempt == 1:
                    fallback_config = config.copy()
                    fallback_config["strategy"] = "fast"
                    fallback_config.pop("chunking_strategy", None)
                    return self._extract_with_strategy(file_path, fallback_config, attempt + 1)
                if attempt == 2:
                    minimal_config = {"languages": config["languages"], "strategy": "auto"}
                    return self._extract_with_strategy(file_path, minimal_config, attempt + 1)
            raise e

    def extract_text(self, file_path: str) -> str:
        """Extract text using Unstructured with adaptive strategy."""
        if partition is None:
            msg = "Unstructured is not installed"
            raise ImportError(msg)

        file_size = self._get_file_size(file_path)
        if file_size > self.max_file_size:
            return ""

        try:
            config = self._get_adaptive_strategy(file_path, file_size)
            elements = self._extract_with_strategy(file_path, config)
            return "\n".join(str(element) for element in elements)
        except Exception:
            return ""

    def extract_with_metadata(self, file_path: str) -> tuple[str, dict[str, Any]]:
        """Extract text and metadata using Unstructured with adaptive strategy."""
        if partition is None:
            msg = "Unstructured is not installed"
            raise ImportError(msg)

        file_size = self._get_file_size(file_path)
        if file_size > self.max_file_size:
            return "", {"error": "file_too_large"}

        try:
            config = self._get_adaptive_strategy(file_path, file_size)
            elements = self._extract_with_strategy(file_path, config)

            text = "\n".join(str(element) for element in elements)
            metadata = {"strategy_used": config.get("strategy", "auto")}

            if elements:
                first_elem = elements[0]
                if hasattr(first_elem, "metadata"):
                    elem_meta = first_elem.metadata
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

                element_types = {}
                for elem in elements:
                    elem_type = type(elem).__name__
                    element_types[elem_type] = element_types.get(elem_type, 0) + 1
                metadata["element_types"] = element_types
                metadata["total_elements"] = len(elements)

            return text, metadata
        except Exception as e:
            return "", {"error": str(e)[:100]}


class ExtractousExtractor:
    """Extractous text extractor with adaptive configuration and performance optimizations."""

    def __init__(self) -> None:
        """Initialize Extractous extractor with adaptive configuration."""
        if Extractor is None:
            msg = "Extractous is not installed. Install with: pip install extractous"
            raise ImportError(msg)

        self.extractor = Extractor()
        self.max_file_size = 200 * 1024 * 1024

        self.extractor.set_extract_string_max_length(5000000)

    def _get_file_characteristics(self, file_path: str) -> dict[str, Any]:
        """Analyze file to determine optimal extraction strategy."""
        try:
            path_obj = Path(file_path)
            file_size = path_obj.stat().st_size
            file_ext = path_obj.suffix.lower()

            return {
                "size": file_size,
                "extension": file_ext,
                "is_large": file_size > 100 * 1024 * 1024,
                "is_pdf": file_ext == ".pdf",
                "is_office": file_ext in [".docx", ".pptx", ".xlsx"],
                "is_image": file_ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"],
            }
        except Exception:
            return {
                "size": 0,
                "extension": "",
                "is_large": False,
                "is_pdf": False,
                "is_office": False,
                "is_image": False,
            }

    def _configure_adaptive_extraction(self, file_path: str, characteristics: dict[str, Any]) -> None:
        """Configure extractor based on file characteristics."""
        if characteristics["is_large"]:
            self.extractor.set_extract_string_max_length(2000000)
        else:
            self.extractor.set_extract_string_max_length(10000000)

    def extract_text(self, file_path: str) -> str:
        """Extract text using Extractous with adaptive configuration."""
        characteristics = self._get_file_characteristics(file_path)

        if characteristics["size"] > self.max_file_size:
            return ""

        try:
            self._configure_adaptive_extraction(file_path, characteristics)
            result = self.extractor.extract_file_to_string(file_path)
            return result[0] if isinstance(result, tuple) else result
        except Exception:
            return ""

    def extract_with_metadata(self, file_path: str) -> tuple[str, dict[str, Any]]:
        """Extract text and metadata using Extractous with adaptive configuration."""
        characteristics = self._get_file_characteristics(file_path)

        if characteristics["size"] > self.max_file_size:
            return "", {"error": "file_too_large", "size_mb": characteristics["size"] / 1024 / 1024}

        try:
            self._configure_adaptive_extraction(file_path, characteristics)
            result = self.extractor.extract_file_to_string(file_path)

            if isinstance(result, tuple) and len(result) >= 2:
                text, raw_metadata = result[0], result[1]
                metadata = dict(raw_metadata) if raw_metadata else {}
            else:
                text = result[0] if isinstance(result, tuple) else result
                metadata = {}

            metadata["file_size_mb"] = round(characteristics["size"] / 1024 / 1024, 2)
            metadata["extraction_strategy"] = "large_file" if characteristics["is_large"] else "standard"
            metadata["ocr_enabled"] = characteristics["is_image"] or characteristics["is_pdf"]

            return text, metadata
        except Exception as e:
            return "", {"error": str(e)[:100], "file_size_mb": round(characteristics["size"] / 1024 / 1024, 2)}


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
        "docling": DoclingExtractor,
        "markitdown": MarkItDownExtractor,
        "unstructured": UnstructuredExtractor,
        "extractous": ExtractousExtractor,
    }

    if framework not in extractors:
        msg = f"Unsupported framework: {framework}"
        raise ValueError(msg)

    return extractors[framework]()  # type: ignore[return-value]
