import pytest


def test_kreuzberg_import():
    try:
        import kreuzberg

        assert hasattr(kreuzberg, "extract_file_sync")
    except ImportError:
        pytest.skip("kreuzberg not installed")


def test_docling_import():
    try:
        from docling.document_converter import DocumentConverter

        assert DocumentConverter is not None
    except ImportError:
        pytest.skip("docling not installed")


def test_markitdown_import():
    try:
        from markitdown import MarkItDown

        assert MarkItDown is not None
    except ImportError:
        pytest.skip("markitdown not installed")


def test_unstructured_import():
    try:
        from unstructured.partition.auto import partition

        assert partition is not None
    except ImportError:
        pytest.skip("unstructured not installed")


def test_extractors_import():
    from src.extractors import (
        DoclingExtractor,
        KreuzbergAsyncExtractor,
        KreuzbergSyncExtractor,
        MarkItDownExtractor,
        UnstructuredExtractor,
        get_extractor,
    )

    assert KreuzbergSyncExtractor is not None
    assert KreuzbergAsyncExtractor is not None
    assert DoclingExtractor is not None
    assert MarkItDownExtractor is not None
    assert UnstructuredExtractor is not None
    assert get_extractor is not None
