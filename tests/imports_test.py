"""Test that all frameworks can be imported successfully."""


def test_kreuzberg_import():
    """Test kreuzberg import."""
    import kreuzberg

    assert hasattr(kreuzberg, "extract_file_sync")


def test_docling_import():
    """Test docling import."""
    from docling.document_converter import DocumentConverter

    assert DocumentConverter is not None


def test_markitdown_import():
    """Test markitdown import."""
    from markitdown import MarkItDown

    assert MarkItDown is not None


def test_unstructured_import():
    """Test unstructured import."""
    from unstructured.partition.auto import partition

    assert partition is not None


def test_extractors_import():
    """Test our extractor implementations."""
    from src.extractors import (
        DoclingExtractor,
        KreuzbergAsyncExtractor,
        KreuzbergSyncExtractor,
        MarkItDownExtractor,
        UnstructuredExtractor,
        get_extractor,
    )

    # Test that all classes are importable
    assert KreuzbergSyncExtractor is not None
    assert KreuzbergAsyncExtractor is not None
    assert DoclingExtractor is not None
    assert MarkItDownExtractor is not None
    assert UnstructuredExtractor is not None
    assert get_extractor is not None
