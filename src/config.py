"""Configuration for benchmark file format filtering."""

from __future__ import annotations

# Tier 1: Universal formats supported by ALL frameworks (5/5)
UNIVERSAL_FORMATS = {
    ".pdf",
    ".pptx",
    ".xlsx",
    ".png",
    ".bmp",
    ".html",
    ".csv",
}

# Tier 2: Common formats supported by most frameworks (4/5)
COMMON_FORMATS = {
    ".xls",  # Not supported by Docling
    ".md",  # Not supported by MarkItDown (ironically)
    ".jpeg",  # Not supported by Unstructured
    ".txt",  # Not supported by Docling
}

# Combined sets for different benchmarking scenarios
TIER1_FORMATS = UNIVERSAL_FORMATS  # 7 formats
TIER2_FORMATS = UNIVERSAL_FORMATS | COMMON_FORMATS  # 11 formats

# Legacy alias for backward compatibility
COMMON_SUPPORTED_FORMATS = UNIVERSAL_FORMATS

# Framework-specific exclusions (formats that are known to fail)
FRAMEWORK_EXCLUSIONS = {
    "kreuzberg_sync": {".eml", ".msg", ".json", ".yaml"},
    "kreuzberg_async": {".eml", ".msg", ".json", ".yaml"},
    "kreuzberg_tesseract": {".eml", ".msg", ".json", ".yaml"},
    "kreuzberg_easyocr": {".eml", ".msg", ".json", ".yaml"},
    "kreuzberg_paddleocr": {".eml", ".msg", ".json", ".yaml"},
    "docling": {".eml", ".msg", ".json", ".yaml", ".odt", ".org", ".rst", ".txt", ".xls"},
    "markitdown": {".docx", ".md", ".odt"},
    "unstructured": {".jpeg", ".jpg", ".odt", ".org", ".rst"},
    "extractous": {".docx", ".jpg"},
    "pymupdf": {
        ".eml",
        ".msg",
        ".json",
        ".yaml",
        ".docx",
        ".pptx",
        ".xlsx",
        ".xls",
        ".odt",
        ".org",
        ".rst",
        ".md",
        ".txt",
        ".csv",
    },  # PDF specialist
    "pdfplumber": {
        ".eml",
        ".msg",
        ".json",
        ".yaml",
        ".docx",
        ".pptx",
        ".xlsx",
        ".xls",
        ".odt",
        ".org",
        ".rst",
        ".md",
        ".txt",
        ".csv",
        ".html",
        ".png",
        ".jpeg",
        ".jpg",
        ".bmp",
    },  # PDF only
    "playa": {
        ".eml",
        ".msg",
        ".json",
        ".yaml",
        ".docx",
        ".pptx",
        ".xlsx",
        ".xls",
        ".odt",
        ".org",
        ".rst",
        ".md",
        ".txt",
        ".csv",
        ".html",
        ".png",
        ".jpeg",
        ".jpg",
        ".bmp",
    },  # PDF only (playa-pdf specialist)
}


def should_test_file(file_path: str, framework: str, format_tier: str | None = None) -> bool:
    """Determine if a file should be tested for a given framework.

    Args:
        file_path: Path to the file
        framework: Framework name
        format_tier: Format tier to use ('universal', 'common', or None for all)

    Returns:
        True if the file should be tested, False otherwise
    """
    from pathlib import Path

    ext = Path(file_path).suffix.lower()

    # Apply tier-based filtering if specified
    if format_tier:
        if format_tier == "universal":
            return ext in TIER1_FORMATS
        if format_tier == "common":
            return ext in TIER2_FORMATS
        # Legacy support
        if format_tier == "common_only":
            return ext in UNIVERSAL_FORMATS

    # Otherwise, check framework-specific exclusions
    if framework in FRAMEWORK_EXCLUSIONS:
        return ext not in FRAMEWORK_EXCLUSIONS[framework]

    # Default to testing all files
    return True
