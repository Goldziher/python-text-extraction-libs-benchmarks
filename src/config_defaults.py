"""Centralized configuration defaults for the benchmarking suite."""

from __future__ import annotations

from typing import ClassVar


class DefaultValues:
    """Centralized default values for all configuration parameters."""

    # Timeout configurations (in seconds)
    EXTRACTION_TIMEOUT_SECONDS = 1800  # 30 minutes per file
    MAX_RUN_DURATION_MINUTES = 30  # 30 minutes total benchmark

    # Performance monitoring
    SAMPLING_INTERVAL_MS = 50  # Resource sampling frequency
    COOLDOWN_SECONDS = 5  # Between iterations

    # Benchmark execution
    DEFAULT_ITERATIONS = 3  # Number of benchmark iterations
    DEFAULT_WARMUP_RUNS = 1  # Warmup iterations
    MAX_RETRIES = 3  # Retry attempts for failed extractions

    # Resource limits
    MAX_MEMORY_MB = 4096  # Memory limit per process
    MAX_CPU_PERCENT = 800  # CPU usage limit (8 cores = 800%)

    # File processing
    MAX_CONCURRENT_FILES = 1  # Concurrent file processing

    # Quality assessment
    TEXT_PREVIEW_LENGTH = 200  # Characters to save for quality check

    # Framework-specific
    KREUZBERG_CACHE_DISABLED = True  # Always disable cache for fair benchmarking


class LanguageMapper:
    """Language mapping configurations for different OCR backends."""

    TESSERACT_MAPPING: ClassVar[dict[str, str]] = {
        "eng": "eng",
        "deu": "deu",
        "heb": "heb",
        "chi_sim": "chi_sim",
        "jpn": "jpn",
        "kor": "kor",
    }

    EASYOCR_MAPPING: ClassVar[dict[str, str]] = {
        "eng": "en",
        "deu": "de",
        "heb": "he",
        "chi_sim": "ch_sim",
        "jpn": "ja",
        "kor": "ko",
    }

    PADDLEOCR_MAPPING: ClassVar[dict[str, str]] = {
        "eng": "en",
        "deu": "german",
        "heb": "en",  # Hebrew not supported, fallback to English
        "chi_sim": "ch",
        "jpn": "japan",
        "kor": "korean",
    }

    @classmethod
    def get_mapping(cls, ocr_backend: str) -> dict[str, str]:
        """Get language mapping for specific OCR backend."""
        mapping_name = f"{ocr_backend.upper()}_MAPPING"
        if not hasattr(cls, mapping_name):
            return cls.TESSERACT_MAPPING  # Fallback to Tesseract mapping
        return getattr(cls, mapping_name)
