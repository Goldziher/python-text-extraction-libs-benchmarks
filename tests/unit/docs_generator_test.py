from pathlib import Path

import msgspec
import pytest

from src.docs_generator import DocsGenerator
from src.types import BenchmarkResult, Framework


@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path


@pytest.fixture
def sample_benchmark_results():
    return [
        BenchmarkResult(
            file_path="test_documents/sample.pdf",
            file_size=1024,
            file_type="pdf",
            category=None,
            framework=Framework.KREUZBERG_SYNC,
            iteration=1,
            extraction_time=1.5,
            startup_time=0.1,
            peak_memory_mb=256.0,
            avg_memory_mb=200.0,
            peak_cpu_percent=50.0,
            avg_cpu_percent=30.0,
            total_io_mb=0.1,
            status="SUCCESS",
            character_count=1000,
            word_count=150,
            error_type=None,
            error_message=None,
            quality_metrics=None,
            overall_quality_score=85.0,
            extracted_text="Sample text content",
            extracted_metadata={"title": "Sample Document"},
            metadata_field_count=1,
            attempts=1,
            timestamp="2025-01-01T12:00:00Z",
            platform="linux",
            python_version="3.13.7",
        ),
        BenchmarkResult(
            file_path="test_documents/sample.docx",
            file_size=2048,
            file_type="docx",
            category=None,
            framework=Framework.UNSTRUCTURED,
            iteration=1,
            extraction_time=2.0,
            startup_time=0.2,
            peak_memory_mb=512.0,
            avg_memory_mb=400.0,
            peak_cpu_percent=60.0,
            avg_cpu_percent=40.0,
            total_io_mb=0.2,
            status="SUCCESS",
            character_count=2000,
            word_count=300,
            error_type=None,
            error_message=None,
            quality_metrics=None,
            overall_quality_score=90.0,
            extracted_text="Sample docx content",
            extracted_metadata={"title": "Sample DOCX", "author": "Test"},
            metadata_field_count=2,
            attempts=1,
            timestamp="2025-01-01T12:00:00Z",
            platform="linux",
            python_version="3.13.7",
        ),
    ]


def test_docs_generator_init_default_paths() -> None:
    generator = DocsGenerator()

    assert generator.docs_dir == Path("docs")
    assert generator.results_dir == Path("docs/results")
    assert generator.raw_data_dir == Path("docs/raw-data")


def test_docs_generator_init_custom_paths(temp_dir: Path) -> None:
    custom_docs = temp_dir / "custom_docs"
    generator = DocsGenerator(custom_docs)

    assert generator.docs_dir == custom_docs
    assert generator.results_dir == custom_docs / "results"
    assert generator.raw_data_dir == custom_docs / "raw-data"


def test_generate_all_creates_directories(sample_benchmark_results, temp_dir: Path) -> None:
    results_file = temp_dir / "results.json"
    with open(results_file, "wb") as f:
        f.write(msgspec.json.encode(sample_benchmark_results))

    generator = DocsGenerator(temp_dir / "docs")
    generator.generate_all(results_file=results_file)

    assert (temp_dir / "docs" / "results").exists()
    assert (temp_dir / "docs" / "results" / "by-file-type").exists()
    assert (temp_dir / "docs" / "results" / "by-file-size").exists()
    assert (temp_dir / "docs" / "results" / "by-framework").exists()
    assert (temp_dir / "docs" / "raw-data").exists()
    assert (temp_dir / "docs" / "methodology").exists()


def test_generate_all_creates_pages(sample_benchmark_results, temp_dir: Path) -> None:
    results_file = temp_dir / "results.json"
    with open(results_file, "wb") as f:
        f.write(msgspec.json.encode(sample_benchmark_results))

    generator = DocsGenerator(temp_dir / "docs")
    generator.generate_all(results_file=results_file)

    assert (temp_dir / "docs" / "index.md").exists()
    assert (temp_dir / "docs" / "results" / "overview.md").exists()

    assert (temp_dir / "docs" / "results" / "by-file-type" / "index.md").exists()
    assert (temp_dir / "docs" / "results" / "by-file-size" / "index.md").exists()
    assert (temp_dir / "docs" / "results" / "by-framework" / "index.md").exists()

    assert (temp_dir / "docs" / "methodology" / "benchmarking.md").exists()
    assert (temp_dir / "docs" / "methodology" / "metrics.md").exists()
    assert (temp_dir / "docs" / "methodology" / "quality.md").exists()

    assert (temp_dir / "docs" / "raw-data" / "downloads.md").exists()
    assert (temp_dir / "docs" / "raw-data" / "full-results.csv").exists()


def test_generate_all_with_empty_results(temp_dir: Path) -> None:
    results_file = temp_dir / "results.json"
    with open(results_file, "wb") as f:
        f.write(msgspec.json.encode([]))

    generator = DocsGenerator(temp_dir / "docs")
    generator.generate_all(results_file=results_file)

    assert (temp_dir / "docs" / "index.md").exists()
    assert (temp_dir / "docs" / "methodology" / "benchmarking.md").exists()


def test_generate_all_no_results_file(temp_dir: Path) -> None:
    generator = DocsGenerator(temp_dir / "docs")
    generator.generate_all()

    assert (temp_dir / "docs" / "methodology" / "benchmarking.md").exists()
    assert (temp_dir / "docs" / "methodology" / "metrics.md").exists()
    assert (temp_dir / "docs" / "methodology" / "quality.md").exists()


def test_aggregate_by_file_type(sample_benchmark_results, temp_dir: Path) -> None:
    generator = DocsGenerator(temp_dir / "docs")
    by_file_type = generator._aggregate_by_file_type(sample_benchmark_results)

    assert "pdf" in by_file_type
    assert "docx" in by_file_type
    assert len(by_file_type["pdf"]) == 1
    assert len(by_file_type["docx"]) == 1


def test_aggregate_by_framework(sample_benchmark_results, temp_dir: Path) -> None:
    generator = DocsGenerator(temp_dir / "docs")
    by_framework = generator._aggregate_by_framework(sample_benchmark_results)

    assert Framework.KREUZBERG_SYNC in by_framework
    assert Framework.UNSTRUCTURED in by_framework
    assert len(by_framework[Framework.KREUZBERG_SYNC]) == 1
    assert len(by_framework[Framework.UNSTRUCTURED]) == 1


def test_aggregate_by_file_size(sample_benchmark_results, temp_dir: Path) -> None:
    generator = DocsGenerator(temp_dir / "docs")
    by_size = generator._aggregate_by_file_size(sample_benchmark_results)

    assert "tiny" in by_size
    assert len(by_size["tiny"]) == 2


def test_load_results_valid_file(sample_benchmark_results, temp_dir: Path) -> None:
    results_file = temp_dir / "results.json"
    with open(results_file, "wb") as f:
        f.write(msgspec.json.encode(sample_benchmark_results))

    generator = DocsGenerator()
    results = generator._load_results(results_file)

    assert len(results) == 2
    assert results[0].framework == Framework.KREUZBERG_SYNC
    assert results[1].framework == Framework.UNSTRUCTURED


def test_load_results_nonexistent_file(temp_dir: Path) -> None:
    generator = DocsGenerator()
    results = generator._load_results(temp_dir / "nonexistent.json")

    assert results == []


def test_load_results_malformed_file(temp_dir: Path) -> None:
    results_file = temp_dir / "malformed.json"
    with open(results_file, "w") as f:
        f.write("invalid json")

    generator = DocsGenerator()
    results = generator._load_results(results_file)

    assert results == []


def test_score_to_grade() -> None:
    generator = DocsGenerator()

    assert generator._score_to_grade(98) == "A+"
    assert generator._score_to_grade(92) == "A"
    assert generator._score_to_grade(87) == "B+"
    assert generator._score_to_grade(82) == "B"
    assert generator._score_to_grade(77) == "C+"
    assert generator._score_to_grade(72) == "C"
    assert generator._score_to_grade(65) == "D"
    assert generator._score_to_grade(45) == "F"


def test_grade_to_score() -> None:
    generator = DocsGenerator()

    assert generator._grade_to_score("A+") == 1.0
    assert generator._grade_to_score("A") == 0.93
    assert generator._grade_to_score("B+") == 0.87
    assert generator._grade_to_score("F") == 0.5
    assert generator._grade_to_score("Invalid") == 0.5


def test_csv_export_generation(sample_benchmark_results, temp_dir: Path) -> None:
    generator = DocsGenerator(temp_dir / "docs")
    generator._setup_directories()
    generator._generate_csv_exports(sample_benchmark_results)

    assert (temp_dir / "docs" / "raw-data" / "full-results.csv").exists()
    assert (temp_dir / "docs" / "raw-data" / "by-file-type.csv").exists()
    assert (temp_dir / "docs" / "raw-data" / "by-file-size.csv").exists()

    full_csv = temp_dir / "docs" / "raw-data" / "full-results.csv"
    content = full_csv.read_text()
    assert "framework" in content
    assert "kreuzberg_sync" in content
    assert "unstructured" in content
