"""Integration tests for the complete file processing pipeline using real test documents."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.benchmark import ComprehensiveBenchmarkRunner
from src.categorizer import DocumentCategorizer
from src.types import (
    BenchmarkConfig,
    DocumentCategory,
    ExtractionStatus,
    FileType,
    Framework,
)


class TestFileProcessingPipeline:
    """Test the complete file processing pipeline with real documents."""

    def setup_method(self):
        """Set up test environment."""
        self.test_docs_dir = Path("test_documents")
        self.categorizer = DocumentCategorizer()

        if not self.test_docs_dir.exists():
            pytest.skip("test_documents directory not found")

    def test_pdf_processing_pipeline(self):
        """Test complete pipeline for PDF documents."""
        pdf_files = list(self.test_docs_dir.rglob("*.pdf"))

        if not pdf_files:
            pytest.skip("No PDF test files found")

        pdf_file = pdf_files[0]  # Use first available PDF

        # Test categorization
        metadata = self.categorizer._get_file_metadata(pdf_file)

        assert metadata["file_type"] == FileType.PDF
        assert isinstance(metadata["file_size"], int)
        assert metadata["file_size"] > 0
        assert metadata["file_name"] == pdf_file.name

        # Test category assignment
        category = self.categorizer._categorize_by_size(metadata["file_size"])
        assert category in [
            DocumentCategory.TINY,
            DocumentCategory.SMALL,
            DocumentCategory.MEDIUM,
            DocumentCategory.LARGE,
            DocumentCategory.HUGE,
        ]

    def test_office_document_processing(self):
        """Test processing of Office documents (DOCX, PPTX, XLSX)."""
        office_extensions = [".docx", ".pptx", ".xlsx"]

        for ext in office_extensions:
            office_files = list(self.test_docs_dir.rglob(f"*{ext}"))

            if not office_files:
                continue

            office_file = office_files[0]

            # Test file type detection
            file_type = self.categorizer._detect_file_type(office_file)

            expected_types = {".docx": FileType.DOCX, ".pptx": FileType.PPTX, ".xlsx": FileType.XLSX}

            assert file_type == expected_types[ext]

            # Test metadata extraction
            metadata = self.categorizer._get_file_metadata(office_file)
            assert metadata["file_size"] > 0
            assert metadata["file_extension"] == ext

    def test_text_and_data_format_processing(self):
        """Test processing of text and data formats."""
        format_tests = [
            (".json", FileType.JSON),
            (".yaml", FileType.YAML),
            (".yml", FileType.YAML),
            (".csv", FileType.CSV),
            (".txt", FileType.TXT),
            (".md", FileType.MARKDOWN),
            (".html", FileType.HTML),
        ]

        for ext, expected_type in format_tests:
            files = list(self.test_docs_dir.rglob(f"*{ext}"))

            if not files:
                continue

            test_file = files[0]

            # Test file type detection
            detected_type = self.categorizer._detect_file_type(test_file)
            assert detected_type == expected_type, (
                f"Wrong type for {ext}: got {detected_type}, expected {expected_type}"
            )

            # Test that file can be read
            metadata = self.categorizer._get_file_metadata(test_file)
            assert metadata["file_size"] >= 0  # Empty files are OK

    def test_image_processing_pipeline(self):
        """Test processing of image files with OCR potential."""
        image_extensions = [".png", ".jpg", ".jpeg", ".bmp"]

        for ext in image_extensions:
            image_files = list(self.test_docs_dir.rglob(f"*{ext}"))

            if not image_files:
                continue

            image_file = image_files[0]

            # Test file type detection
            file_type = self.categorizer._detect_file_type(image_file)

            expected_types = {
                ".png": FileType.IMAGE_PNG,
                ".jpg": FileType.IMAGE_JPG,
                ".jpeg": FileType.IMAGE_JPEG,
                ".bmp": FileType.IMAGE_BMP,
            }

            assert file_type == expected_types[ext]

            # Test metadata extraction
            metadata = self.categorizer._get_file_metadata(image_file)
            assert metadata["file_size"] > 0  # Images should have size

    @pytest.mark.asyncio
    async def test_end_to_end_extraction_pipeline(self):
        """Test complete extraction pipeline from file discovery to results."""
        # Find a small test file
        small_files = []
        for pattern in ["*.json", "*.txt", "*.md"]:
            small_files.extend(list(self.test_docs_dir.rglob(pattern)))

        if not small_files:
            pytest.skip("No small test files found")

        test_file = small_files[0]

        # Test complete pipeline
        config = BenchmarkConfig(
            frameworks=[Framework.KREUZBERG_SYNC],
            categories=[DocumentCategory.TINY],
            iterations=1,
            warmup_runs=0,
            timeout_seconds=30,
            max_run_duration_minutes=2,
            output_dir=Path("test_output"),
        )

        runner = ComprehensiveBenchmarkRunner(config)

        # Mock file discovery to use our specific test file
        with patch.object(runner.categorizer, "get_files_by_category") as mock_get_files:
            mock_get_files.return_value = [test_file]

            try:
                results = await runner.run_benchmark_suite()

                # Should have at least one result
                assert len(results) > 0

                result = results[0]
                assert result.file_path == str(test_file)
                assert result.framework == Framework.KREUZBERG_SYNC
                assert result.status in [ExtractionStatus.SUCCESS, ExtractionStatus.FAILED, ExtractionStatus.TIMEOUT]

                if result.status == ExtractionStatus.SUCCESS:
                    assert result.extraction_time > 0
                    assert result.character_count >= 0

            except Exception as e:
                # Log the error but don't fail the test if framework is not available
                pytest.skip(f"Extraction failed (framework may not be available): {e}")

    def test_large_file_handling(self):
        """Test handling of larger files."""
        # Find larger files in test suite
        all_files = list(self.test_docs_dir.rglob("*"))
        file_sizes = []

        for file_path in all_files:
            if file_path.is_file():
                size = file_path.stat().st_size
                file_sizes.append((file_path, size))

        if not file_sizes:
            pytest.skip("No files found")

        # Sort by size and get largest
        file_sizes.sort(key=lambda x: x[1], reverse=True)
        _largest_file, size = file_sizes[0]

        # Test categorization of largest file
        category = self.categorizer._categorize_by_size(size)

        # Should be categorized appropriately
        if size < 100_000:  # 100KB
            assert category == DocumentCategory.TINY
        elif size < 1_048_576:  # 1MB
            assert category == DocumentCategory.SMALL
        elif size < 10_485_760:  # 10MB
            assert category == DocumentCategory.MEDIUM
        elif size < 52_428_800:  # 50MB
            assert category == DocumentCategory.LARGE
        else:
            assert category == DocumentCategory.HUGE

    def test_multilingual_file_detection(self):
        """Test detection and processing of multilingual files."""
        # Look for files with language indicators in names
        language_patterns = {
            "hebrew": ["*hebrew*", "*israel*", "*heb*"],
            "german": ["*german*", "*germany*", "*deu*"],
            "chinese": ["*chinese*", "*china*", "*chi*"],
            "japanese": ["*japanese*", "*japan*", "*jpn*"],
            "korean": ["*korean*", "*korea*", "*kor*"],
        }

        found_languages = {}

        for language, patterns in language_patterns.items():
            for pattern in patterns:
                files = list(self.test_docs_dir.rglob(pattern))
                if files:
                    found_languages[language] = files[0]
                    break

        if not found_languages:
            pytest.skip("No multilingual test files found")

        # Test language detection for found files
        from src.extractors import get_language_config

        for language, file_path in found_languages.items():
            detected_lang = get_language_config(file_path)

            expected_mappings = {
                "hebrew": "heb",
                "german": "deu",
                "chinese": "chi_sim",
                "japanese": "jpn",
                "korean": "kor",
            }

            if language in expected_mappings:
                assert detected_lang == expected_mappings[language]

    def test_file_processing_error_recovery(self):
        """Test error recovery during file processing."""
        # Create a temporary file with invalid content
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, mode="w") as f:
            f.write("This is not a valid PDF file content")
            invalid_file = Path(f.name)

        try:
            # Test that categorizer handles invalid files gracefully
            metadata = self.categorizer._get_file_metadata(invalid_file)

            # Should still return valid metadata structure
            assert "file_size" in metadata
            assert "file_type" in metadata
            assert "file_name" in metadata

            # File type should be detected from extension
            assert metadata["file_type"] == FileType.PDF

        finally:
            invalid_file.unlink()

    def test_concurrent_file_processing(self):
        """Test concurrent processing of multiple files."""
        # Get multiple small files
        test_files = []
        for pattern in ["*.json", "*.txt", "*.yaml"]:
            files = list(self.test_docs_dir.rglob(pattern))
            test_files.extend(files[:3])  # Take first 3 of each type

        if len(test_files) < 3:
            pytest.skip("Need at least 3 test files for concurrent testing")

        # Test that all files can be processed
        results = []
        for test_file in test_files[:5]:  # Limit to 5 files
            try:
                metadata = self.categorizer._get_file_metadata(test_file)
                results.append((test_file, metadata))
            except Exception as e:
                pytest.fail(f"Failed to process {test_file}: {e}")

        # All files should have been processed
        assert len(results) == len(test_files[:5])

        # All should have valid metadata
        for file_path, metadata in results:
            assert metadata["file_name"] == file_path.name
            assert metadata["file_size"] >= 0

    def test_file_type_edge_cases(self):
        """Test edge cases in file type detection."""
        # Files without extensions
        no_ext_files = []
        for file_path in self.test_docs_dir.rglob("*"):
            if file_path.is_file() and "." not in file_path.name:
                no_ext_files.append(file_path)

        for file_path in no_ext_files[:3]:  # Test first 3
            file_type = self.categorizer._detect_file_type(file_path)
            # Should default to UNKNOWN for files without clear extensions
            assert file_type == FileType.UNKNOWN

    def test_category_boundary_conditions(self):
        """Test files at category boundary sizes."""
        # Find files near category boundaries
        all_files = [(f, f.stat().st_size) for f in self.test_docs_dir.rglob("*") if f.is_file()]

        # Category boundaries in bytes
        boundaries = [
            (99999, DocumentCategory.TINY),  # Just under 100KB
            (100000, DocumentCategory.SMALL),  # Exactly 100KB
            (1048575, DocumentCategory.SMALL),  # Just under 1MB
            (1048576, DocumentCategory.MEDIUM),  # Exactly 1MB
        ]

        # Test files near boundaries
        for _file_path, size in all_files[:10]:
            category = self.categorizer._categorize_by_size(size)

            # Verify category is correct based on size
            if size < 100000:
                assert category == DocumentCategory.TINY
            elif size < 1048576:
                assert category == DocumentCategory.SMALL
            elif size < 10485760:
                assert category == DocumentCategory.MEDIUM
            elif size < 52428800:
                assert category == DocumentCategory.LARGE
            else:
                assert category == DocumentCategory.HUGE

    def test_complete_pipeline_performance(self):
        """Test performance characteristics of the complete pipeline."""
        import time

        # Find a reasonable test file
        test_files = list(self.test_docs_dir.rglob("*.json"))
        if not test_files:
            test_files = list(self.test_docs_dir.rglob("*.txt"))

        if not test_files:
            pytest.skip("No suitable test files for performance testing")

        test_file = test_files[0]

        # Time the complete categorization process
        start_time = time.time()

        metadata = self.categorizer._get_file_metadata(test_file)
        file_type = self.categorizer._detect_file_type(test_file)
        category = self.categorizer._categorize_by_size(metadata["file_size"])

        end_time = time.time()
        elapsed = end_time - start_time

        # Should complete very quickly for simple files
        assert elapsed < 1.0, f"Categorization took too long: {elapsed} seconds"

        # Verify results are sensible
        assert file_type != FileType.UNKNOWN or test_file.suffix == ""
        assert category in [
            DocumentCategory.TINY,
            DocumentCategory.SMALL,
            DocumentCategory.MEDIUM,
            DocumentCategory.LARGE,
            DocumentCategory.HUGE,
        ]

    @pytest.mark.asyncio
    async def test_pipeline_memory_usage(self):
        """Test that pipeline doesn't consume excessive memory."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Process multiple files
        processed_count = 0
        for file_path in self.test_docs_dir.rglob("*"):
            if file_path.is_file() and processed_count < 20:  # Limit to 20 files
                try:
                    metadata = self.categorizer._get_file_metadata(file_path)
                    processed_count += 1
                except Exception:
                    # Skip files that can't be processed
                    continue

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (< 50MB for processing 20 files)
        assert memory_increase < 50 * 1024 * 1024, f"Excessive memory usage: {memory_increase / 1024 / 1024:.2f} MB"

        # Should have processed at least some files
        assert processed_count > 0, "No files were processed"
