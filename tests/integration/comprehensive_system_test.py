import tempfile
from pathlib import Path

import pytest

from src.categorizer import DocumentCategorizer
from src.types import BenchmarkConfig, DocumentCategory, Framework


class TestComprehensiveSystemIntegration:
    def setup_method(self):
        self.test_docs_dir = Path("test_documents")
        self.categorizer = DocumentCategorizer()

        if not self.test_docs_dir.exists():
            pytest.skip("test_documents directory not found")

    def test_end_to_end_file_discovery_and_categorization(self):
        for category in DocumentCategory:
            files = self.categorizer.get_files_by_category(category)

            assert isinstance(files, list)

            for file_path in files:
                assert isinstance(file_path, Path)
                assert file_path.exists()

    def test_multi_format_file_type_detection(self):
        file_count = 0
        format_counts = {}

        for file_path in self.test_docs_dir.rglob("*"):
            if file_path.is_file():
                file_count += 1

                file_type = self.categorizer._detect_file_type(file_path)
                format_counts[file_type] = format_counts.get(file_type, 0) + 1

        assert file_count > 0, "No test files found"

        assert len(format_counts) >= 5, f"Only detected {len(format_counts)} formats: {format_counts}"

        detected_formats = set(format_counts.keys())
        expected_formats = {"PDF", "DOCX", "JSON", "TXT", "MARKDOWN", "HTML"}

        overlap = len(detected_formats.intersection(expected_formats))
        assert overlap >= 3, f"Expected more common formats, got: {detected_formats}"

    def test_size_based_categorization_accuracy(self):
        category_file_counts = {}

        for category in DocumentCategory:
            files = self.categorizer.get_files_by_category(category)
            category_file_counts[category] = len(files)

        non_empty_categories = [cat for cat, count in category_file_counts.items() if count > 0]
        assert len(non_empty_categories) >= 2, f"Files only in {non_empty_categories}"

        for category in non_empty_categories:
            files = self.categorizer.get_files_by_category(category)

            for file_path in files[:5]:
                file_size = file_path.stat().st_size
                detected_category = self.categorizer._categorize_by_size(file_size)

                assert detected_category == category, (
                    f"File {file_path} size {file_size} categorized as {detected_category}, expected {category}"
                )

    def test_benchmark_config_validation_with_real_frameworks(self):
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
        language_indicators = {
            "english": ["english", "en_", "eng"],
            "hebrew": ["hebrew", "heb", "israel"],
            "german": ["german", "deu", "germany"],
            "chinese": ["chinese", "chi", "china"],
            "japanese": ["japanese", "jpn", "japan"],
            "korean": ["korean", "kor", "korea"],
        }

        detected_languages = set()

        for file_path in self.test_docs_dir.rglob("*"):
            if file_path.is_file():
                file_name_lower = file_path.name.lower()

                for language, indicators in language_indicators.items():
                    if any(indicator in file_name_lower for indicator in indicators):
                        detected_languages.add(language)

        assert "english" in detected_languages or len(detected_languages) == 0, (
            f"Detected languages: {detected_languages}"
        )

    def test_system_memory_and_performance_boundaries(self):
        import os
        import time

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        start_time = time.time()

        file_count = 0
        for file_path in self.test_docs_dir.rglob("*"):
            if file_path.is_file() and file_count < 50:
                try:
                    metadata = self.categorizer._get_file_metadata(file_path)
                    file_type = self.categorizer._detect_file_type(file_path)
                    category = self.categorizer._categorize_by_size(metadata["file_size"])

                    assert isinstance(metadata, dict)
                    assert "file_size" in metadata

                    file_count += 1

                except Exception:
                    continue

        end_time = time.time()
        final_memory = process.memory_info().rss

        elapsed_time = end_time - start_time
        memory_increase = final_memory - initial_memory

        assert elapsed_time < 30.0, f"Processing took too long: {elapsed_time:.2f} seconds"
        assert memory_increase < 100 * 1024 * 1024, f"Memory usage increased by {memory_increase / 1024 / 1024:.2f} MB"
        assert file_count > 0, "No files were processed successfully"

    def test_error_recovery_with_problematic_files(self):
        error_count = 0
        success_count = 0

        for file_path in self.test_docs_dir.rglob("*"):
            if file_path.is_file():
                try:
                    metadata = self.categorizer._get_file_metadata(file_path)
                    file_type = self.categorizer._detect_file_type(file_path)

                    success_count += 1

                    assert isinstance(metadata, dict)
                    assert metadata["file_size"] >= 0

                except Exception:
                    error_count += 1

        total_files = success_count + error_count

        assert success_count > 0, "No files processed successfully"
        assert total_files > 0, "No files found to test"

        error_rate = error_count / total_files
        assert error_rate < 0.5, f"Error rate too high: {error_rate:.2%} ({error_count}/{total_files})"

    def test_concurrent_operations_stability(self):
        import queue
        import threading

        results = queue.Queue()

        def worker_thread(thread_id):
            try:
                local_categorizer = DocumentCategorizer()
                files_processed = 0

                for file_path in self.test_docs_dir.rglob("*"):
                    if file_path.is_file() and files_processed < 10:
                        try:
                            metadata = local_categorizer._get_file_metadata(file_path)
                            files_processed += 1
                        except Exception:
                            continue

                results.put(("success", thread_id, files_processed))

            except Exception as e:
                results.put(("error", thread_id, str(e)))

        threads = []
        num_threads = 3

        for i in range(num_threads):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join(timeout=30.0)

        thread_results = []
        while not results.empty():
            thread_results.append(results.get())

        assert len(thread_results) == num_threads, f"Only {len(thread_results)} threads completed"

        successful_threads = [r for r in thread_results if r[0] == "success"]
        assert len(successful_threads) >= num_threads // 2, f"Too many thread failures: {thread_results}"

    def test_benchmark_configuration_edge_cases(self):
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

        maximal_config = BenchmarkConfig(
            frameworks=list(Framework),
            categories=list(DocumentCategory),
            iterations=10,
            warmup_runs=3,
            timeout_seconds=3600,
            max_run_duration_minutes=120,
            output_dir=Path("maximal_test"),
        )

        assert len(maximal_config.frameworks) >= 6
        assert len(maximal_config.categories) == 5
        assert maximal_config.iterations == 10

    def test_output_directory_handling(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "benchmark_results"

            config = BenchmarkConfig(
                frameworks=[Framework.KREUZBERG_SYNC],
                categories=[DocumentCategory.TINY],
                iterations=1,
                warmup_runs=0,
                timeout_seconds=30,
                max_run_duration_minutes=1,
                output_dir=output_path,
            )

            assert not output_path.exists()

            assert config.output_dir == output_path

            output_path.mkdir(parents=True, exist_ok=True)
            assert output_path.exists()
            assert output_path.is_dir()

    def test_file_metadata_extraction_comprehensive(self):
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

        assert len(metadata_samples) > 0, "No metadata extracted from any files"

        for file_path, metadata, file_type in metadata_samples:
            assert "file_name" in metadata
            assert "file_size" in metadata
            assert "file_type" in metadata
            assert "file_extension" in metadata

            assert metadata["file_name"] == file_path.name
            assert metadata["file_size"] >= 0
            assert metadata["file_size"] == file_path.stat().st_size

            assert metadata["file_type"] == file_type

        assert len(file_types_seen) >= 3, f"Only saw {len(file_types_seen)} file types: {file_types_seen}"
