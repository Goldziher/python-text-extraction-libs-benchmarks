"""Document categorization for organized benchmarking."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, ClassVar

from src.types import DocumentCategory, FileType


class DocumentCategorizer:
    """Categorize documents for organized testing."""

    # Size thresholds in bytes
    SIZE_THRESHOLDS: ClassVar[dict[DocumentCategory, tuple[int, float]]] = {
        DocumentCategory.TINY: (0, 100 * 1024),  # < 100KB
        DocumentCategory.SMALL: (100 * 1024, 1024 * 1024),  # 100KB - 1MB
        DocumentCategory.MEDIUM: (1024 * 1024, 10 * 1024 * 1024),  # 1MB - 10MB
        DocumentCategory.LARGE: (10 * 1024 * 1024, 50 * 1024 * 1024),  # 10MB - 50MB
        DocumentCategory.HUGE: (50 * 1024 * 1024, float("inf")),  # > 50MB
    }

    # File type to category mapping
    FORMAT_CATEGORIES: ClassVar[dict[DocumentCategory, list[FileType]]] = {
        DocumentCategory.PDF_STANDARD: [FileType.PDF],
        DocumentCategory.PDF_SCANNED: [FileType.PDF_SCANNED],
        DocumentCategory.OFFICE: [FileType.DOCX, FileType.PPTX, FileType.XLSX, FileType.XLS, FileType.ODT],
        DocumentCategory.WEB: [FileType.HTML],
        DocumentCategory.TEXT: [FileType.MARKDOWN, FileType.TXT, FileType.RST, FileType.ORG],
        DocumentCategory.EMAIL: [FileType.MSG, FileType.EML],
        DocumentCategory.EBOOK: [FileType.EPUB],
        DocumentCategory.DATA: [FileType.CSV, FileType.JSON, FileType.YAML],
        DocumentCategory.IMAGES: [FileType.IMAGE_PNG, FileType.IMAGE_JPG, FileType.IMAGE_JPEG, FileType.IMAGE_BMP],
    }

    # Patterns for detecting scanned/OCR PDFs
    SCANNED_PDF_PATTERNS: ClassVar[list[re.Pattern[str]]] = [
        re.compile(r"ocr", re.IGNORECASE),
        re.compile(r"scan(ned)?", re.IGNORECASE),
        re.compile(r"rotated", re.IGNORECASE),
    ]

    # Patterns for detecting complex PDFs
    COMPLEX_PDF_PATTERNS: ClassVar[list[re.Pattern[str]]] = [
        re.compile(r"table", re.IGNORECASE),
        re.compile(r"formula", re.IGNORECASE),
        re.compile(r"equation", re.IGNORECASE),
        re.compile(r"embed", re.IGNORECASE),
        re.compile(r"complex", re.IGNORECASE),
    ]

    # Language patterns
    UNICODE_PATTERNS: ClassVar[list[re.Pattern[str]]] = [
        re.compile(r"hebrew|german|chinese|japanese|korean", re.IGNORECASE),
        re.compile(r"中国|北京|日本|한국", re.IGNORECASE),
        re.compile(r"[\u0590-\u05FF]"),  # Hebrew
        re.compile(r"[\u4E00-\u9FFF]"),  # Chinese
        re.compile(r"[\u3040-\u309F\u30A0-\u30FF]"),  # Japanese
        re.compile(r"[\uAC00-\uD7AF]"),  # Korean
    ]

    # Patterns for detecting table-related files
    TABLE_FILE_PATTERNS: ClassVar[list[re.Pattern[str]]] = [
        re.compile(r"table", re.IGNORECASE),
        re.compile(r"spreadsheet", re.IGNORECASE),
        re.compile(r"stanley-cups", re.IGNORECASE),
        re.compile(r"embedded.*table", re.IGNORECASE),
        re.compile(r"complex.*table", re.IGNORECASE),
        re.compile(r"simple.*table", re.IGNORECASE),
    ]

    # File types that commonly contain tables
    TABLE_FILE_TYPES: ClassVar[list[FileType]] = [
        FileType.CSV,
        FileType.XLSX,
        FileType.XLS,
        FileType.HTML,  # when contains table in name
        FileType.MARKDOWN,  # when contains table in name
        FileType.PDF,  # when contains table in name
        FileType.DOCX,  # when contains table in name
    ]

    def __init__(self) -> None:
        self._file_type_map = self._build_file_type_map()

    def _build_file_type_map(self) -> dict[str, FileType]:
        """Build a mapping of file extensions to FileType enum values."""
        return {
            ".pdf": FileType.PDF,
            ".docx": FileType.DOCX,
            ".pptx": FileType.PPTX,
            ".xlsx": FileType.XLSX,
            ".xls": FileType.XLS,
            ".odt": FileType.ODT,
            ".html": FileType.HTML,
            ".htm": FileType.HTML,
            ".md": FileType.MARKDOWN,
            ".markdown": FileType.MARKDOWN,
            ".txt": FileType.TXT,
            ".text": FileType.TXT,
            ".rtf": FileType.RTF,
            ".epub": FileType.EPUB,
            ".msg": FileType.MSG,
            ".eml": FileType.EML,
            ".csv": FileType.CSV,
            ".json": FileType.JSON,
            ".yaml": FileType.YAML,
            ".yml": FileType.YAML,
            ".rst": FileType.RST,
            ".org": FileType.ORG,
            ".png": FileType.IMAGE_PNG,
            ".jpg": FileType.IMAGE_JPG,
            ".jpeg": FileType.IMAGE_JPEG,
            ".bmp": FileType.IMAGE_BMP,
        }

    def get_file_type(self, file_path: Path) -> FileType | None:
        """Determine the file type based on extension."""
        extension = file_path.suffix.lower()
        file_type = self._file_type_map.get(extension)

        # Special handling for PDFs
        if file_type == FileType.PDF and self._is_scanned_pdf(file_path):
            return FileType.PDF_SCANNED

        return file_type

    def _is_scanned_pdf(self, file_path: Path) -> bool:
        """Check if a PDF is scanned/OCR based on filename patterns."""
        filename = file_path.name
        return any(pattern.search(filename) for pattern in self.SCANNED_PDF_PATTERNS)

    def _is_complex_pdf(self, file_path: Path) -> bool:
        """Check if a PDF is complex based on filename patterns."""
        filename = file_path.name
        return any(pattern.search(filename) for pattern in self.COMPLEX_PDF_PATTERNS)

    def _has_unicode_content(self, file_path: Path) -> bool:
        """Check if file likely contains unicode content based on filename."""
        filename = file_path.name
        return any(pattern.search(filename) for pattern in self.UNICODE_PATTERNS)

    def categorize_by_size(self, file_path: Path) -> DocumentCategory | None:
        """Categorize document by file size."""
        try:
            size = file_path.stat().st_size
            for category, (min_size, max_size) in self.SIZE_THRESHOLDS.items():
                if min_size <= size < max_size:
                    return category
        except OSError:
            return None
        return None

    def categorize_by_format(self, file_path: Path) -> list[DocumentCategory]:
        """Categorize document by format type."""
        categories = []
        file_type = self.get_file_type(file_path)

        if not file_type:
            return categories

        # Check format categories
        for category, types in self.FORMAT_CATEGORIES.items():
            if file_type in types:
                categories.append(category)

        # Special handling for PDFs
        if file_type == FileType.PDF:
            if self._is_scanned_pdf(file_path):
                categories.append(DocumentCategory.PDF_SCANNED)
            elif self._is_complex_pdf(file_path):
                categories.append(DocumentCategory.PDF_COMPLEX)
            else:
                categories.append(DocumentCategory.PDF_STANDARD)

        return categories

    def categorize_by_language(self, file_path: Path) -> DocumentCategory | None:
        """Categorize document by language content."""
        if self._has_unicode_content(file_path):
            return DocumentCategory.UNICODE
        # Default to English for now (could be enhanced with content analysis)
        return DocumentCategory.ENGLISH

    def categorize_document(self, file_path: Path) -> dict[str, Any]:
        """Comprehensively categorize a document."""
        return {
            "file_path": file_path,
            "file_type": self.get_file_type(file_path),
            "size_category": self.categorize_by_size(file_path),
            "format_categories": self.categorize_by_format(file_path),
            "language_category": self.categorize_by_language(file_path),
            "file_size": file_path.stat().st_size if file_path.exists() else 0,
        }

    def categorize_documents(self, test_dir: Path) -> dict[DocumentCategory, list[Path]]:
        """Categorize all documents in a test directory."""
        categories: dict[DocumentCategory, list[Path]] = {category: [] for category in DocumentCategory}

        # Find all files recursively
        for file_path in test_dir.rglob("*"):
            if not file_path.is_file():
                continue

            categorization = self.categorize_document(file_path)

            # Add to size category
            if size_cat := categorization["size_category"]:
                categories[size_cat].append(file_path)

            # Add to format categories
            for format_cat in categorization["format_categories"]:
                categories[format_cat].append(file_path)

            # Add to language category
            if lang_cat := categorization["language_category"]:
                categories[lang_cat].append(file_path)

        return categories

    def get_files_for_category(
        self, test_dir: Path, category: DocumentCategory, table_extraction_only: bool = False
    ) -> list[tuple[Path, dict[str, Any]]]:
        """Get all files belonging to a specific category with their metadata."""
        files_with_metadata = []

        for file_path in test_dir.rglob("*"):
            if not file_path.is_file():
                continue

            categorization = self.categorize_document(file_path)

            # Check if file belongs to requested category
            belongs = False

            if (
                category == categorization["size_category"]
                or category in categorization["format_categories"]
                or category == categorization["language_category"]
            ):
                belongs = True

            # Apply table extraction filter if requested
            if belongs and table_extraction_only:
                belongs = self._is_table_file(file_path, categorization)

            if belongs:
                files_with_metadata.append((file_path, categorization))

        return files_with_metadata

    def _is_table_file(self, file_path: Path, categorization: dict[str, Any]) -> bool:
        """Check if a file likely contains tables."""
        file_name = file_path.name.lower()
        file_type = categorization.get("file_type")

        # Check filename patterns
        for pattern in self.TABLE_FILE_PATTERNS:
            if pattern.search(file_name):
                return True

        # CSV and Excel files are always table files
        if file_type in [FileType.CSV, FileType.XLSX, FileType.XLS]:
            return True

        # HTML/Markdown files with "table" in name
        if file_type in [FileType.HTML, FileType.MARKDOWN] and "table" in file_name:
            return True

        # DOCX files with "table" in name
        if file_type == FileType.DOCX and "table" in file_name:
            return True

        # PDF files with "table" in name
        return bool(file_type == FileType.PDF and any(keyword in file_name for keyword in ["table", "embedded"]))
