"""Comprehensive system integration test covering all major code paths."""

import tempfile
from pathlib import Path

import pytest

from src.categorizer import DocumentCategorizer
from src.types import BenchmarkConfig, DocumentCategory, Framework


class TestComprehensiveSystemIntegration:
    """Test complete system integration with real test documents."""

    def setup_method(self):
        """Set up test environment."""
        self.test_docs_dir = Path("test_documents")
        self.categorizer = DocumentCategorizer()

        if not self.test_docs_dir.exists():
            pytest.skip("test_documents directory not found")

    def test_end_to_end_file_discovery_and_categorization(self):
        """Test complete file discovery and categorization pipeline."""
        # Test file discovery across all categories
        for category in DocumentCategory:
            files = self.categorizer.get_files_by_category(category)

            # Should return a list (may be empty for some categories)
            assert isinstance(files, list)

            # If files exist, they should be valid paths
            for file_path in files:
                assert isinstance(file_path, Path)
                assert file_path.exists()

    def test_multi_format_file_type_detection(self):
        """Test file type detection across multiple formats."""
        file_count = 0
        format_counts = {}

        # Walk through all test documents
        for file_path in self.test_docs_dir.rglob("*"):
            if file_path.is_file():
                file_count += 1

                # Test file type detection
                file_type = self.categorizer._detect_file_type(file_path)
                format_counts[file_type] = format_counts.get(file_type, 0) + 1

        # Should have processed files
        assert file_count > 0, "No test files found"

        # Should have detected multiple formats
        assert len(format_counts) >= 5, f"Only detected {len(format_counts)} formats: {format_counts}"

        # Should detect common formats in test suite
        detected_formats = set(format_counts.keys())
        expected_formats = {"PDF", "DOCX", "JSON", "TXT", "MARKDOWN", "HTML"}

        # At least some expected formats should be present
        overlap = len(detected_formats.intersection(expected_formats))
        assert overlap >= 3, f"Expected more common formats, got: {detected_formats}"

    def test_size_based_categorization_accuracy(self):
        """Test accuracy of size-based categorization."""
        category_file_counts = {}

        # Count files in each category
        for category in DocumentCategory:
            files = self.categorizer.get_files_by_category(category)
            category_file_counts[category] = len(files)

        # Should have files in multiple categories
        non_empty_categories = [cat for cat, count in category_file_counts.items() if count > 0]
        assert len(non_empty_categories) >= 2, f"Files only in {non_empty_categories}"

        # Validate size categorization makes sense
        for category in non_empty_categories:
            files = self.categorizer.get_files_by_category(category)

            for file_path in files[:5]:  # Sample first 5 files
                file_size = file_path.stat().st_size
                detected_category = self.categorizer._categorize_by_size(file_size)

                assert detected_category == category, (
                    f"File {file_path} size {file_size} categorized as {detected_category}, expected {category}"
                )

    def test_benchmark_config_validation_with_real_frameworks(self):
        """Test benchmark configuration with actual framework values."""
        # Test with single framework
        config = BenchmarkConfig(
            frameworks=[Framework.KREUZBERG_SYNC],
            categories=[DocumentCategory.TINY],
            iterations=1,
            warmup_runs=0,
            timeout_seconds=30,
            max_run_duration_minutes=1,
            output_dir=Path("test_output"),
        )

        assert len(config.frameworks) == 1
        assert config.frameworks[0] == Framework.KREUZBERG_SYNC
        assert config.categories[0] == DocumentCategory.TINY

        # Test with multiple frameworks
        multi_config = BenchmarkConfig(
            frameworks=[Framework.KREUZBERG_SYNC, Framework.KREUZBERG_ASYNC, Framework.MARKITDOWN],
            categories=[DocumentCategory.TINY, DocumentCategory.SMALL],
            iterations=2,
            warmup_runs=1,
            timeout_seconds=300,
            max_run_duration_minutes=30,
            output_dir=Path("test_output"),
        )

        assert len(multi_config.frameworks) == 3
        assert len(multi_config.categories) == 2

    def test_document_language_detection_patterns(self):
        """Test document language detection patterns with real files."""
        language_indicators = {
            "english": ["english", "en_", "eng"],
            "hebrew": ["hebrew", "heb", "israel"],
            "german": ["german", "deu", "germany"],
            "chinese": ["chinese", "chi", "china"],
            "japanese": ["japanese", "jpn", "japan"],
            "korean": ["korean", "kor", "korea"],
        }

        detected_languages = set()

        # Scan for language-specific files
        for file_path in self.test_docs_dir.rglob("*"):
            if file_path.is_file():
                file_name_lower = file_path.name.lower()

                for language, indicators in language_indicators.items():
                    if any(indicator in file_name_lower for indicator in indicators):
                        detected_languages.add(language)

        # Should detect at least English files
        assert "english" in detected_languages or len(detected_languages) == 0, (
            f"Detected languages: {detected_languages}"
        )

    def test_system_memory_and_performance_boundaries(self):
        """Test system behavior within reasonable memory and performance boundaries."""
        import os
        import time

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        start_time = time.time()

        # Perform representative system operations
        file_count = 0
        for file_path in self.test_docs_dir.rglob("*"):
            if file_path.is_file() and file_count < 50:  # Limit to prevent excessive testing time
                try:
                    # Perform categorization operations
                    metadata = self.categorizer._get_file_metadata(file_path)
                    file_type = self.categorizer._detect_file_type(file_path)
                    category = self.categorizer._categorize_by_size(metadata["file_size"])

                    # Basic validation
                    assert isinstance(metadata, dict)
                    assert "file_size" in metadata

                    file_count += 1

                except Exception:
                    # Skip files that can't be processed
                    continue

        end_time = time.time()
        final_memory = process.memory_info().rss

        elapsed_time = end_time - start_time
        memory_increase = final_memory - initial_memory

        # Performance assertions
        assert elapsed_time < 30.0, f"Processing took too long: {elapsed_time:.2f} seconds"
        assert memory_increase < 100 * 1024 * 1024, f"Memory usage increased by {memory_increase / 1024 / 1024:.2f} MB"
        assert file_count > 0, "No files were processed successfully"

    def test_error_recovery_with_problematic_files(self):
        """Test system error recovery with various problematic files."""
        error_count = 0
        success_count = 0

        # Test with all files, expecting some to fail
        for file_path in self.test_docs_dir.rglob("*"):
            if file_path.is_file():
                try:
                    # Attempt basic operations
                    metadata = self.categorizer._get_file_metadata(file_path)
                    file_type = self.categorizer._detect_file_type(file_path)

                    # If we get here, operation succeeded
                    success_count += 1

                    # Validate results
                    assert isinstance(metadata, dict)
                    assert metadata["file_size"] >= 0

                except Exception:
                    # Expected for some files (corrupted, binary, etc.)
                    error_count += 1

        total_files = success_count + error_count

        # Should process some files successfully
        assert success_count > 0, "No files processed successfully"
        assert total_files > 0, "No files found to test"

        # Error rate should be reasonable (< 50% for a good test suite)
        error_rate = error_count / total_files
        assert error_rate < 0.5, f"Error rate too high: {error_rate:.2%} ({error_count}/{total_files})"

    def test_concurrent_operations_stability(self):
        """Test system stability under concurrent operations."""
        import queue
        import threading

        results = queue.Queue()

        def worker_thread(thread_id):
            """Worker thread that performs categorization operations."""
            try:
                local_categorizer = DocumentCategorizer()
                files_processed = 0

                for file_path in self.test_docs_dir.rglob("*"):
                    if file_path.is_file() and files_processed < 10:  # Limit per thread
                        try:
                            metadata = local_categorizer._get_file_metadata(file_path)
                            files_processed += 1
                        except Exception:
                            continue

                results.put(("success", thread_id, files_processed))

            except Exception as e:
                results.put(("error", thread_id, str(e)))

        # Start multiple worker threads
        threads = []
        num_threads = 3

        for i in range(num_threads):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=30.0)  # 30 second timeout

        # Collect results
        thread_results = []
        while not results.empty():
            thread_results.append(results.get())

        # Validate results
        assert len(thread_results) == num_threads, f"Only {len(thread_results)} threads completed"

        successful_threads = [r for r in thread_results if r[0] == "success"]
        assert len(successful_threads) >= num_threads // 2, f"Too many thread failures: {thread_results}"

    def test_benchmark_configuration_edge_cases(self):
        """Test benchmark configuration with edge case values."""
        # Test with minimal configuration
        minimal_config = BenchmarkConfig(
            frameworks=[Framework.KREUZBERG_SYNC],
            categories=[DocumentCategory.TINY],
            iterations=1,
            warmup_runs=0,
            timeout_seconds=1,
            max_run_duration_minutes=1,
            output_dir=Path("minimal_test"),
        )

        assert minimal_config.iterations == 1
        assert minimal_config.timeout_seconds == 1

        # Test with maximal reasonable configuration
        maximal_config = BenchmarkConfig(
            frameworks=list(Framework),  # All frameworks
            categories=list(DocumentCategory),  # All categories
            iterations=10,
            warmup_runs=3,
            timeout_seconds=3600,  # 1 hour
            max_run_duration_minutes=120,  # 2 hours
            output_dir=Path("maximal_test"),
        )

        assert len(maximal_config.frameworks) >= 6  # Should have multiple frameworks
        assert len(maximal_config.categories) == 5  # All document categories
        assert maximal_config.iterations == 10

    def test_output_directory_handling(self):
        """Test output directory creation and handling."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "benchmark_results"

            # Test configuration with non-existent directory
            config = BenchmarkConfig(
                frameworks=[Framework.KREUZBERG_SYNC],
                categories=[DocumentCategory.TINY],
                iterations=1,
                warmup_runs=0,
                timeout_seconds=30,
                max_run_duration_minutes=1,
                output_dir=output_path,
            )

            # Directory doesn't exist yet
            assert not output_path.exists()

            # Configuration should be valid
            assert config.output_dir == output_path

            # Create the directory to test it works
            output_path.mkdir(parents=True, exist_ok=True)
            assert output_path.exists()
            assert output_path.is_dir()

    def test_file_metadata_extraction_comprehensive(self):
        """Test comprehensive file metadata extraction."""
        metadata_samples = []
        file_types_seen = set()

        for file_path in self.test_docs_dir.rglob("*"):
            if file_path.is_file() and len(metadata_samples) < 20:
                try:
                    metadata = self.categorizer._get_file_metadata(file_path)
                    file_type = self.categorizer._detect_file_type(file_path)

                    metadata_samples.append((file_path, metadata, file_type))
                    file_types_seen.add(file_type)

                except Exception:
                    continue

        # Should have processed some files
        assert len(metadata_samples) > 0, "No metadata extracted from any files"

        # Validate metadata structure
        for file_path, metadata, file_type in metadata_samples:
            # Required metadata fields
            assert "file_name" in metadata
            assert "file_size" in metadata
            assert "file_type" in metadata
            assert "file_extension" in metadata

            # Validate values
            assert metadata["file_name"] == file_path.name
            assert metadata["file_size"] >= 0
            assert metadata["file_size"] == file_path.stat().st_size

            # File type should be consistent
            assert metadata["file_type"] == file_type

        # Should see multiple file types
        assert len(file_types_seen) >= 3, f"Only saw {len(file_types_seen)} file types: {file_types_seen}"
