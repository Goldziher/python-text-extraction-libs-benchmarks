"""Text extraction implementations for different frameworks."""

from __future__ import annotations

import sys

if sys.version_info >= (3, 13):
    pass
else:
    pass

try:
    import kreuzberg
except ImportError:
    kreuzberg = None  # type: ignore[assignment]

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
        """Initialize Docling converter."""
        if DocumentConverter is None:
            msg = "Docling is not installed"
            raise ImportError(msg)
        self.converter = DocumentConverter()

    def extract_text(self, file_path: str) -> str:
        """Extract text using Docling."""
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
        result = self.converter.convert(file_path)
        return result.text_content


class UnstructuredExtractor:
    """Unstructured text extractor."""

    def extract_text(self, file_path: str) -> str:
        """Extract text using Unstructured."""
        if partition is None:
            msg = "Unstructured is not installed"
            raise ImportError(msg)
        elements = partition(filename=file_path)
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
        "docling": DoclingExtractor,
        "markitdown": MarkItDownExtractor,
        "unstructured": UnstructuredExtractor,
    }

    if framework not in extractors:
        msg = f"Unsupported framework: {framework}"
        raise ValueError(msg)

    return extractors[framework]()  # type: ignore[return-value]
