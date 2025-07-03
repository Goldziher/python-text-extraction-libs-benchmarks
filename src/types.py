"""Type definitions for the benchmarking system."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Protocol

import msgspec


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
    PDF_SCANNED = "pdf_scanned"
    DOCX = "docx"
    PPTX = "pptx"
    XLSX = "xlsx"
    XLS = "xls"
    ODT = "odt"
    HTML = "html"
    MARKDOWN = "md"
    TXT = "txt"
    RTF = "rtf"
    EPUB = "epub"
    MSG = "msg"
    EML = "eml"
    CSV = "csv"
    JSON = "json"
    YAML = "yaml"
    RST = "rst"
    ORG = "org"
    IMAGE_PNG = "png"
    IMAGE_JPG = "jpg"
    IMAGE_JPEG = "jpeg"
    IMAGE_BMP = "bmp"


class DocumentCategory(str, Enum):
    """Document categories for organized testing."""

    # Size-based categories
    TINY = "tiny"  # < 100KB
    SMALL = "small"  # 100KB - 1MB
    MEDIUM = "medium"  # 1MB - 10MB
    LARGE = "large"  # 10MB - 50MB
    HUGE = "huge"  # > 50MB

    # Format-based categories
    PDF_STANDARD = "pdf_standard"
    PDF_SCANNED = "pdf_scanned"
    PDF_COMPLEX = "pdf_complex"
    OFFICE = "office"
    WEB = "web"
    TEXT = "text"
    EMAIL = "email"
    EBOOK = "ebook"
    DATA = "data"
    IMAGES = "images"

    # Language-based categories
    ENGLISH = "english"
    UNICODE = "unicode"
    MIXED_LANGUAGE = "mixed_language"


class ExtractionStatus(str, Enum):
    """Status of an extraction attempt."""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"


class ExtractorProtocol(Protocol):
    """Protocol for synchronous text extractors."""

    def extract_text(self, file_path: str | Path) -> str:
        """Extract text from a file."""
        ...


class AsyncExtractorProtocol(Protocol):
    """Protocol for asynchronous text extractors."""

    async def extract_text(self, file_path: str | Path) -> str:
        """Extract text from a file asynchronously."""
        ...


class ResourceMetrics(msgspec.Struct):
    """Detailed resource usage metrics."""

    timestamp: float
    cpu_percent: float
    memory_rss: int
    memory_vms: int
    num_threads: int
    open_files: int
    io_read_bytes: int | None = None
    io_write_bytes: int | None = None
    io_read_count: int | None = None
    io_write_count: int | None = None


class ExtractionResult(msgspec.Struct, kw_only=True):
    """Result of a single extraction attempt."""

    file_path: str
    file_size: int
    framework: Framework
    status: ExtractionStatus
    extraction_time: float | None = None
    extracted_text: str | None = None
    character_count: int | None = None
    word_count: int | None = None
    error_type: str | None = None
    error_message: str | None = None
    attempt_number: int = 1
    resource_metrics: list[ResourceMetrics] = msgspec.field(default_factory=list)


class BenchmarkResult(msgspec.Struct, kw_only=True):
    """Complete benchmark result for a single file."""

    file_path: str
    file_size: int
    file_type: FileType
    category: DocumentCategory
    framework: Framework
    iteration: int

    # Timing metrics
    extraction_time: float
    startup_time: float | None = None

    # Resource metrics
    peak_memory_mb: float
    avg_memory_mb: float
    peak_cpu_percent: float
    avg_cpu_percent: float
    total_io_mb: float | None = None

    # Results
    status: ExtractionStatus
    character_count: int | None = None
    word_count: int | None = None
    error_type: str | None = None
    error_message: str | None = None

    # Quality metrics (optional, added by quality assessment)
    quality_metrics: dict[str, Any] | None = None
    overall_quality_score: float | None = None
    extracted_text: str | None = None

    # Metadata
    attempts: int = 1
    timestamp: float = msgspec.field(default_factory=lambda: __import__("time").time())
    platform: str = msgspec.field(default_factory=lambda: __import__("platform").system())
    python_version: str = msgspec.field(default_factory=lambda: __import__("platform").python_version())


class BenchmarkSummary(msgspec.Struct, kw_only=True):
    """Summary statistics for a framework/category combination."""

    framework: Framework
    category: DocumentCategory
    total_files: int
    successful_files: int
    failed_files: int
    partial_files: int
    timeout_files: int

    # Timing statistics (only for successful extractions)
    avg_extraction_time: float | None = None
    median_extraction_time: float | None = None
    min_extraction_time: float | None = None
    max_extraction_time: float | None = None
    std_extraction_time: float | None = None

    # Resource statistics
    avg_peak_memory_mb: float | None = None
    avg_cpu_percent: float | None = None

    # Throughput metrics
    files_per_second: float | None = None
    mb_per_second: float | None = None

    # Success metrics
    success_rate: float
    avg_character_count: int | None = None
    avg_word_count: int | None = None


class AggregatedResults(msgspec.Struct, kw_only=True):
    """Aggregated results from multiple benchmark runs."""

    total_runs: int
    total_files_processed: int
    total_time_seconds: float

    # Results by framework
    framework_summaries: dict[Framework, list[BenchmarkSummary]]

    # Results by category
    category_summaries: dict[DocumentCategory, list[BenchmarkSummary]]

    # Cross-tabulation
    framework_category_matrix: dict[tuple[Framework, DocumentCategory], BenchmarkSummary]

    # Failure analysis
    failure_patterns: dict[str, int]  # error_type -> count
    timeout_files: list[str]

    # Performance trends
    performance_over_iterations: dict[Framework, list[float]]

    # Platform-specific results
    platform_results: dict[str, dict[Framework, BenchmarkSummary]]


class BenchmarkConfig(msgspec.Struct, kw_only=True):
    """Configuration for benchmark execution."""

    # Execution settings
    iterations: int = 3
    warmup_runs: int = 1
    cooldown_seconds: int = 5
    concurrent_files: int = 1  # For async frameworks

    # Resource limits
    timeout_seconds: int = 600  # 10 minutes per file
    max_memory_mb: int = 4096  # 4GB limit
    max_cpu_percent: int = 800  # 8 cores at 100%

    # Failure handling
    max_retries: int = 3
    retry_backoff: float = 2.0
    continue_on_error: bool = True
    skip_on_repeated_failure: bool = True

    # Selection
    frameworks: list[Framework] = msgspec.field(default_factory=list)
    categories: list[DocumentCategory] = msgspec.field(default_factory=list)
    file_types: list[FileType] = msgspec.field(default_factory=list)

    # Output settings
    output_dir: Path = msgspec.field(default_factory=lambda: Path("results"))
    save_intermediate: bool = True
    save_extracted_text: bool = False
    compression: bool = True
    detailed_errors: bool = True

    # Profiling settings
    sampling_interval_ms: int = 50
    profile_startup: bool = True
    profile_io: bool = True
