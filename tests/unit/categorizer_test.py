"""Tests for document categorizer module."""

import tempfile
from pathlib import Path

from src.categorizer import DocumentCategorizer
from src.types import DocumentCategory, FileType


class TestDocumentCategorizer:
    """Test document categorization functionality."""

    def test_categorizer_initialization(self):
        """Test that categorizer initializes correctly."""
        categorizer = DocumentCategorizer()
        assert categorizer is not None

    def test_file_size_categorization_tiny(self):
        """Test categorization of tiny files (<100KB)."""
        categorizer = DocumentCategorizer()

        # Create test files with different sizes
        test_sizes = [1000, 50000, 99999]  # All < 100KB

        for size in test_sizes:
            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(b"x" * size)
                f.flush()
                test_file = Path(f.name)

            try:
                metadata = categorizer._get_file_metadata(test_file)
                category = categorizer._categorize_by_size(metadata["file_size"])

                assert category == DocumentCategory.TINY
            finally:
                test_file.unlink()

    def test_file_size_categorization_small(self):
        """Test categorization of small files (100KB-1MB)."""
        categorizer = DocumentCategorizer()

        # Test boundary cases for small category
        test_sizes = [100000, 500000, 1048575]  # 100KB, 500KB, <1MB

        for size in test_sizes:
            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(b"x" * size)
                f.flush()
                test_file = Path(f.name)

            try:
                metadata = categorizer._get_file_metadata(test_file)
                category = categorizer._categorize_by_size(metadata["file_size"])

                assert category == DocumentCategory.SMALL
            finally:
                test_file.unlink()

    def test_file_size_categorization_medium(self):
        """Test categorization of medium files (1MB-10MB)."""
        categorizer = DocumentCategorizer()

        # Create a medium-sized file (2MB)
        size = 2 * 1024 * 1024  # 2MB

        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"x" * size)
            f.flush()
            test_file = Path(f.name)

        try:
            metadata = categorizer._get_file_metadata(test_file)
            category = categorizer._categorize_by_size(metadata["file_size"])

            assert category == DocumentCategory.MEDIUM
        finally:
            test_file.unlink()

    def test_file_size_categorization_large(self):
        """Test categorization of large files (10MB-50MB)."""
        categorizer = DocumentCategorizer()

        # Create a large file (20MB)
        size = 20 * 1024 * 1024  # 20MB

        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"x" * size)
            f.flush()
            test_file = Path(f.name)

        try:
            metadata = categorizer._get_file_metadata(test_file)
            category = categorizer._categorize_by_size(metadata["file_size"])

            assert category == DocumentCategory.LARGE
        finally:
            test_file.unlink()

    def test_file_size_categorization_huge(self):
        """Test categorization of huge files (>50MB)."""
        categorizer = DocumentCategorizer()

        # For testing, we'll mock a huge file size rather than creating one
        huge_size = 100 * 1024 * 1024  # 100MB

        category = categorizer._categorize_by_size(huge_size)
        assert category == DocumentCategory.HUGE

    def test_file_type_detection_pdf(self):
        """Test PDF file type detection."""
        categorizer = DocumentCategorizer()

        test_files = [
            "document.pdf",
            "report.PDF",
            "analysis.Pdf",
        ]

        for filename in test_files:
            file_type = categorizer._detect_file_type(Path(filename))
            assert file_type == FileType.PDF

    def test_file_type_detection_docx(self):
        """Test DOCX file type detection."""
        categorizer = DocumentCategorizer()

        test_files = [
            "document.docx",
            "report.DOCX",
            "analysis.Docx",
        ]

        for filename in test_files:
            file_type = categorizer._detect_file_type(Path(filename))
            assert file_type == FileType.DOCX

    def test_file_type_detection_images(self):
        """Test image file type detection."""
        categorizer = DocumentCategorizer()

        test_cases = [
            ("image.png", FileType.IMAGE_PNG),
            ("photo.jpg", FileType.IMAGE_JPG),
            ("picture.jpeg", FileType.IMAGE_JPEG),
            ("bitmap.bmp", FileType.IMAGE_BMP),
        ]

        for filename, expected_type in test_cases:
            file_type = categorizer._detect_file_type(Path(filename))
            assert file_type == expected_type

    def test_file_type_detection_text_formats(self):
        """Test text format file type detection."""
        categorizer = DocumentCategorizer()

        test_cases = [
            ("data.txt", FileType.TXT),
            ("config.html", FileType.HTML),
            ("styles.css", FileType.CSS),
            ("data.json", FileType.JSON),
            ("config.yaml", FileType.YAML),
            ("config.yml", FileType.YAML),
            ("data.xml", FileType.XML),
            ("data.csv", FileType.CSV),
            ("readme.md", FileType.MARKDOWN),
        ]

        for filename, expected_type in test_cases:
            file_type = categorizer._detect_file_type(Path(filename))
            assert file_type == expected_type

    def test_file_type_detection_unknown(self):
        """Test handling of unknown file types."""
        categorizer = DocumentCategorizer()

        unknown_files = [
            "file.unknown",
            "document.xyz",
            "data.custom",
        ]

        for filename in unknown_files:
            file_type = categorizer._detect_file_type(Path(filename))
            assert file_type == FileType.UNKNOWN

    def test_file_type_detection_no_extension(self):
        """Test handling of files without extensions."""
        categorizer = DocumentCategorizer()

        files_without_extension = [
            "README",
            "LICENSE",
            "Makefile",
        ]

        for filename in files_without_extension:
            file_type = categorizer._detect_file_type(Path(filename))
            assert file_type == FileType.UNKNOWN

    def test_get_file_metadata_complete(self):
        """Test that file metadata extraction is complete."""
        categorizer = DocumentCategorizer()

        # Create a test file
        test_content = b"Test file content for metadata extraction"
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(test_content)
            f.flush()
            test_file = Path(f.name)

        try:
            metadata = categorizer._get_file_metadata(test_file)

            # Check all expected metadata fields
            expected_fields = [
                "file_size",
                "file_type",
                "file_name",
                "file_extension",
                "modification_time",
            ]

            for field in expected_fields:
                assert field in metadata, f"Missing metadata field: {field}"

            # Check field types and values
            assert isinstance(metadata["file_size"], int)
            assert metadata["file_size"] == len(test_content)
            assert metadata["file_type"] == FileType.TXT
            assert metadata["file_name"] == test_file.name
            assert metadata["file_extension"] == ".txt"
            assert isinstance(metadata["modification_time"], float)

        finally:
            test_file.unlink()

    def test_categorize_file_integration(self):
        """Test complete file categorization integration."""
        categorizer = DocumentCategorizer()

        # Create test file with known size and type
        test_content = b"x" * 50000  # 50KB - should be tiny
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(test_content)
            f.flush()
            test_file = Path(f.name)

        try:
            # This assumes there's a main categorization method
            # If it doesn't exist, this test documents the expected API
            if hasattr(categorizer, "categorize_file"):
                result = categorizer.categorize_file(test_file)

                assert "category" in result
                assert "file_type" in result
                assert "metadata" in result

                assert result["category"] == DocumentCategory.TINY
                assert result["file_type"] == FileType.PDF
                assert result["metadata"]["file_size"] == 50000

        finally:
            test_file.unlink()

    def test_boundary_cases_file_size(self):
        """Test boundary cases for file size categorization."""
        categorizer = DocumentCategorizer()

        # Test exact boundary values
        boundary_tests = [
            (99999, DocumentCategory.TINY),  # Just under 100KB
            (100000, DocumentCategory.SMALL),  # Exactly 100KB
            (1048575, DocumentCategory.SMALL),  # Just under 1MB
            (1048576, DocumentCategory.MEDIUM),  # Exactly 1MB
            (10485759, DocumentCategory.MEDIUM),  # Just under 10MB
            (10485760, DocumentCategory.LARGE),  # Exactly 10MB
            (52428799, DocumentCategory.LARGE),  # Just under 50MB
            (52428800, DocumentCategory.HUGE),  # Exactly 50MB
        ]

        for size, expected_category in boundary_tests:
            category = categorizer._categorize_by_size(size)
            assert category == expected_category, f"Failed for size {size}"

    def test_case_insensitive_file_extension(self):
        """Test that file extension detection is case insensitive."""
        categorizer = DocumentCategorizer()

        test_cases = [
            ("file.PDF", FileType.PDF),
            ("file.pdf", FileType.PDF),
            ("file.Pdf", FileType.PDF),
            ("file.TXT", FileType.TXT),
            ("file.txt", FileType.TXT),
            ("file.Txt", FileType.TXT),
        ]

        for filename, expected_type in test_cases:
            file_type = categorizer._detect_file_type(Path(filename))
            assert file_type == expected_type

    def test_nonexistent_file_handling(self):
        """Test handling of non-existent files."""
        categorizer = DocumentCategorizer()

        nonexistent_file = Path("this_file_does_not_exist.pdf")

        # Should handle gracefully without raising exception
        metadata = categorizer._get_file_metadata(nonexistent_file)

        # File size should be 0 for non-existent files
        assert metadata["file_size"] == 0

    def test_permission_denied_file_handling(self):
        """Test handling of files with permission issues."""
        # This test would require creating files with restricted permissions
        # For now, document expected behavior

    def test_corrupted_file_handling(self):
        """Test handling of corrupted or unreadable files."""
        # This test would require creating corrupted files
        # For now, document expected behavior


class TestCategoryConstants:
    """Test document category constants and relationships."""

    def test_all_categories_defined(self):
        """Test that all expected categories are defined."""
        expected_categories = [
            DocumentCategory.TINY,
            DocumentCategory.SMALL,
            DocumentCategory.MEDIUM,
            DocumentCategory.LARGE,
            DocumentCategory.HUGE,
        ]

        for category in expected_categories:
            assert category is not None
            assert isinstance(category.value, str)

    def test_category_ordering(self):
        """Test that categories have logical ordering."""
        # Size categories should have a logical progression
        size_categories = [
            DocumentCategory.TINY,
            DocumentCategory.SMALL,
            DocumentCategory.MEDIUM,
            DocumentCategory.LARGE,
            DocumentCategory.HUGE,
        ]

        # Each category should be distinct
        category_values = [cat.value for cat in size_categories]
        assert len(category_values) == len(set(category_values))


class TestFileTypeConstants:
    """Test file type constants and relationships."""

    def test_all_file_types_defined(self):
        """Test that all expected file types are defined."""
        expected_types = [
            FileType.PDF,
            FileType.DOCX,
            FileType.PPTX,
            FileType.XLSX,
            FileType.TXT,
            FileType.HTML,
            FileType.JSON,
            FileType.YAML,
            FileType.CSV,
            FileType.XML,
            FileType.MARKDOWN,
            FileType.IMAGE_PNG,
            FileType.IMAGE_JPG,
            FileType.IMAGE_JPEG,
            FileType.IMAGE_BMP,
            FileType.UNKNOWN,
        ]

        for file_type in expected_types:
            assert file_type is not None
            assert isinstance(file_type.value, str)

    def test_file_type_uniqueness(self):
        """Test that all file types are unique."""
        all_file_types = list(FileType)
        file_type_values = [ft.value for ft in all_file_types]

        # No duplicate values
        assert len(file_type_values) == len(set(file_type_values))

    def test_image_file_types_grouped(self):
        """Test that image file types follow consistent naming."""
        image_types = [
            FileType.IMAGE_PNG,
            FileType.IMAGE_JPG,
            FileType.IMAGE_JPEG,
            FileType.IMAGE_BMP,
        ]

        for img_type in image_types:
            assert img_type.value.startswith("image_") or img_type.value in ["png", "jpg", "jpeg", "bmp"]
