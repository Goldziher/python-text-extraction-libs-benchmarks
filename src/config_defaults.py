"""Centralized configuration defaults for the benchmarking suite."""

from __future__ import annotations

from typing import ClassVar


class DefaultValues:
    """Centralized default values for all configuration parameters."""

    EXTRACTION_TIMEOUT_SECONDS = 1800
    MAX_RUN_DURATION_MINUTES = 30

    SAMPLING_INTERVAL_MS = 50
    COOLDOWN_SECONDS = 5

    DEFAULT_ITERATIONS = 3
    DEFAULT_WARMUP_RUNS = 1
    MAX_RETRIES = 3

    MAX_MEMORY_MB = 4096
    MAX_CPU_PERCENT = 800

    MAX_CONCURRENT_FILES = 1

    TEXT_PREVIEW_LENGTH = 200

    KREUZBERG_CACHE_DISABLED = True


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
        "heb": "en",
        "chi_sim": "ch",
        "jpn": "japan",
        "kor": "korean",
    }

    @classmethod
    def get_mapping(cls, ocr_backend: str) -> dict[str, str]:
        """Get language mapping for specific OCR backend."""
        mapping_name = f"{ocr_backend.upper()}_MAPPING"
        if not hasattr(cls, mapping_name):
            return cls.TESSERACT_MAPPING
        return getattr(cls, mapping_name)
