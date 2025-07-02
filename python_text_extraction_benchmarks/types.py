"""Type definitions for the benchmarking suite."""

from __future__ import annotations

import sys
from enum import Enum
from typing import Protocol

if sys.version_info >= (3, 13):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from msgspec import Struct


class Framework(str, Enum):
    """Supported text extraction frameworks."""

    KREUZBERG_SYNC = "kreuzberg_sync"
    KREUZBERG_ASYNC = "kreuzberg_async"
    DOCLING = "docling"
    MARKITDOWN = "markitdown"
    UNSTRUCTURED = "unstructured"


class FileType(str, Enum):
    """Supported file types for benchmarking."""

    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    XLSX = "xlsx"
    HTML = "html"
    MARKDOWN = "md"
    TXT = "txt"
    IMAGE_PDF = "image_pdf"  # PDF with images requiring OCR


class BenchmarkResult(Struct):
    """Result of a single benchmark run."""

    framework: Framework
    file_type: FileType
    file_path: str
    file_size_bytes: int
    extraction_time_seconds: float
    memory_peak_mb: float
    cpu_percent: float
    success: bool
    error_message: str | None = None
    extracted_text_length: int | None = None
    extracted_text_preview: str | None = None


class BenchmarkSummary(Struct):
    """Summary statistics for a benchmark run."""

    framework: Framework
    file_type: FileType
    total_files: int
    successful_extractions: int
    failed_extractions: int
    average_time_seconds: float
    median_time_seconds: float
    min_time_seconds: float
    max_time_seconds: float
    average_memory_mb: float
    average_cpu_percent: float
    total_time_seconds: float


class ExtractorProtocol(Protocol):
    """Protocol that all text extractors must implement."""

    def extract_text(self, file_path: str) -> str:
        """Extract text from a file.

        Args:
            file_path: Path to the file to extract text from.

        Returns:
            Extracted text content.

        Raises:
            Exception: If extraction fails.
        """
        ...


class AsyncExtractorProtocol(Protocol):
    """Protocol that async text extractors must implement."""

    async def extract_text(self, file_path: str) -> str:
        """Extract text from a file asynchronously.

        Args:
            file_path: Path to the file to extract text from.

        Returns:
            Extracted text content.

        Raises:
            Exception: If extraction fails.
        """
        ...


class BenchmarkConfig(TypedDict, total=False):
    """Configuration for benchmark runs."""

    frameworks: list[Framework]
    file_types: list[FileType]
    test_files_dir: str
    output_dir: str
    num_runs: int
    timeout_seconds: int
    include_memory_profiling: bool
    include_cpu_profiling: bool
    save_extracted_text: bool
