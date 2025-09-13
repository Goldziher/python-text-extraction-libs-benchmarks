"""Configuration for benchmark file format filtering."""

from __future__ import annotations

from src.types import Framework

UNIVERSAL_FORMATS = {
    ".pdf",
    ".pptx",
    ".xlsx",
    ".png",
    ".bmp",
    ".html",
    ".csv",
}

COMMON_FORMATS = {
    ".xls",
    ".md",
    ".jpeg",
    ".txt",
}

TIER1_FORMATS = UNIVERSAL_FORMATS
TIER2_FORMATS = UNIVERSAL_FORMATS | COMMON_FORMATS

COMMON_SUPPORTED_FORMATS = UNIVERSAL_FORMATS

FRAMEWORK_EXCLUSIONS = {
    Framework.KREUZBERG_SYNC: {".eml", ".msg", ".json", ".yaml"},
    Framework.KREUZBERG_ASYNC: {".eml", ".msg", ".json", ".yaml"},
    Framework.KREUZBERG_TESSERACT: {".eml", ".msg", ".json", ".yaml"},
    Framework.KREUZBERG_EASYOCR: {".eml", ".msg", ".json", ".yaml"},
    Framework.KREUZBERG_PADDLEOCR: {".eml", ".msg", ".json", ".yaml"},
    Framework.DOCLING: {".eml", ".msg", ".json", ".yaml", ".odt", ".org", ".rst", ".txt", ".xls"},
    Framework.MARKITDOWN: {".docx", ".md", ".odt"},
    Framework.UNSTRUCTURED: {".jpeg", ".jpg", ".odt", ".org", ".rst"},
    Framework.EXTRACTOUS: {".docx", ".jpg"},
}


def should_test_file(file_path: str, framework: Framework | str, format_tier: str | None = None) -> bool:
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

    if format_tier:
        if format_tier == "universal":
            return ext in TIER1_FORMATS
        if format_tier == "common":
            return ext in TIER2_FORMATS
        if format_tier == "common_only":
            return ext in UNIVERSAL_FORMATS

    # Convert string to Framework enum if needed
    if isinstance(framework, str):
        try:
            framework = Framework(framework)
        except ValueError as e:
            raise ValueError(f"Unknown framework: {framework}. Valid frameworks: {[f.value for f in Framework]}") from e

    if framework in FRAMEWORK_EXCLUSIONS:
        return ext not in FRAMEWORK_EXCLUSIONS[framework]

    return True
