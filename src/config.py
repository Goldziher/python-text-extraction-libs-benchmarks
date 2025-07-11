"""Configuration for benchmark file format filtering."""

from __future__ import annotations

# Common formats supported by ALL frameworks
COMMON_SUPPORTED_FORMATS = {
    ".pdf",
    ".pptx",
    ".xlsx",
    ".png",
    ".bmp",
}

# Extended set for real-world benchmarking (most frameworks support these)
REALWORLD_FORMATS = {
    ".pdf",
    ".docx",
    ".pptx",
    ".xlsx",
    ".html",
    ".png",
}

# Framework-specific exclusions (formats that are known to fail)
FRAMEWORK_EXCLUSIONS = {
    "kreuzberg_sync": {".eml", ".msg", ".json", ".yaml", ".docx", ".odt", ".rst", ".org"},
    "kreuzberg_async": {".eml", ".msg", ".json", ".yaml", ".docx", ".odt", ".rst", ".org"},
    "kreuzberg_tesseract": {".eml", ".msg", ".json", ".yaml", ".docx", ".odt", ".rst", ".org"},
    "kreuzberg_easyocr": {".eml", ".msg", ".json", ".yaml", ".docx", ".odt", ".rst", ".org"},
    "kreuzberg_paddleocr": {".eml", ".msg", ".json", ".yaml", ".docx", ".odt", ".rst", ".org"},
    "docling": {".eml", ".msg", ".json", ".yaml", ".odt", ".org", ".rst", ".txt", ".xls"},
    "markitdown": {".docx", ".md", ".odt"},
    "unstructured": {".jpeg", ".jpg", ".odt", ".org", ".rst"},
    "extractous": {".docx", ".jpg"},
}


def should_test_file(file_path: str, framework: str, use_common_only: bool = False) -> bool:
    """Determine if a file should be tested for a given framework.

    Args:
        file_path: Path to the file
        framework: Framework name
        use_common_only: If True, only test formats supported by ALL frameworks

    Returns:
        True if the file should be tested, False otherwise
    """
    from pathlib import Path

    ext = Path(file_path).suffix.lower()

    # If using common only mode, only test files in the common set
    if use_common_only:
        return ext in COMMON_SUPPORTED_FORMATS

    # Otherwise, check framework-specific exclusions
    if framework in FRAMEWORK_EXCLUSIONS:
        return ext not in FRAMEWORK_EXCLUSIONS[framework]

    # Default to testing all files
    return True
