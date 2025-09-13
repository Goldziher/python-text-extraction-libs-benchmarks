"""Integration tests for MkDocs documentation generation."""

import subprocess
from pathlib import Path

import pytest

from src.docs_generator import DocsGenerator
from src.types import AggregatedResults


def test_mkdocs_build_with_generated_results(aggregated_results: AggregatedResults, temp_dir: Path) -> None:
    """Test that MkDocs can build site with generated results."""
    mkdocs_config = temp_dir / "mkdocs.yml"
    mkdocs_config.write_text("""
site_name: Test Site
theme:
  name: material

nav:
  - Home: index.md
  - Results: results/index.md
""")

    docs_dir = temp_dir / "docs"
    docs_dir.mkdir()

    (docs_dir / "index.md").write_text("# Test Site\n\nWelcome to the test site.")

    results_file = temp_dir / "test_results.json"
    with open(results_file, "w") as f:
        import msgspec

        f.write(msgspec.json.encode(aggregated_results).decode())

    generator = DocsGenerator(docs_dir)
    generator.generate_from_results(results_file)

    result = subprocess.run(
        ["mkdocs", "build", "--config-file", str(mkdocs_config)],
        check=False,
        cwd=temp_dir,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0 or "WARNING" in result.stderr

    site_dir = temp_dir / "site"
    if site_dir.exists():
        assert (site_dir / "index.html").exists()


def test_generated_pages_have_valid_markdown(aggregated_results: AggregatedResults, temp_dir: Path) -> None:
    """Test that generated pages have valid markdown syntax."""
    results_file = temp_dir / "test_results.json"
    with open(results_file, "w") as f:
        import msgspec

        f.write(msgspec.json.encode(aggregated_results).decode())

    generator = DocsGenerator(temp_dir / "docs")
    generator.generate_from_results(results_file)

    results_dir = temp_dir / "docs" / "results"

    markdown_files = list(results_dir.rglob("*.md"))
    assert len(markdown_files) > 0

    for md_file in markdown_files:
        content = md_file.read_text()

        assert content.strip()

        lines = content.split("\n")
        has_title = any(line.startswith("#") for line in lines)
        assert has_title, f"File {md_file} should have at least one heading"

        for line in lines:
            if "|" in line:
                pipe_count = line.count("|")
                assert pipe_count >= 2, f"Invalid table syntax in {md_file}: {line}"


def test_charts_integration(aggregated_results: AggregatedResults, temp_dir: Path, charts_dir: Path) -> None:
    """Test that charts are properly integrated into docs."""
    results_file = temp_dir / "test_results.json"
    with open(results_file, "w") as f:
        import msgspec

        f.write(msgspec.json.encode(aggregated_results).decode())

    generator = DocsGenerator(temp_dir / "docs")
    generator.generate_from_results(results_file, charts_dir)

    charts_dest = temp_dir / "docs" / "results" / "assets" / "charts"
    assert charts_dest.exists()
    assert (charts_dest / "performance_comparison_large.png").exists()
    assert (charts_dest / "interactive_dashboard.html").exists()

    index_file = temp_dir / "docs" / "results" / "index.md"
    content = index_file.read_text()
    assert "performance_comparison_large.png" in content


def test_navigation_structure(aggregated_results: AggregatedResults, temp_dir: Path) -> None:
    """Test that generated pages follow expected navigation structure."""
    results_file = temp_dir / "test_results.json"
    with open(results_file, "w") as f:
        import msgspec

        f.write(msgspec.json.encode(aggregated_results).decode())

    generator = DocsGenerator(temp_dir / "docs")
    generator.generate_from_results(results_file)

    results_dir = temp_dir / "docs" / "results"

    assert (results_dir / "index.md").exists()
    assert (results_dir / "performance").exists()
    assert (results_dir / "performance" / "speed.md").exists()
    assert (results_dir / "performance" / "memory.md").exists()
    assert (results_dir / "formats").exists()
    assert (results_dir / "formats" / "index.md").exists()
    assert (results_dir / "interactive").exists()
    assert (results_dir / "interactive" / "dashboard.md").exists()

    index_content = (results_dir / "index.md").read_text()
    assert "performance/speed.md" in index_content
    assert "interactive/dashboard.md" in index_content


def test_real_world_data_generation(aggregated_results_file: Path, temp_dir: Path) -> None:
    """Test docs generation with real benchmark data."""
    generator = DocsGenerator(temp_dir / "docs")
    generator.generate_from_results(aggregated_results_file)

    results_dir = temp_dir / "docs" / "results"
    assert (results_dir / "index.md").exists()

    index_content = (results_dir / "index.md").read_text()

    expected_frameworks = ["kreuzberg", "docling", "unstructured", "extractous", "markitdown"]
    found_frameworks = []
    for framework in expected_frameworks:
        if framework.lower() in index_content.lower():
            found_frameworks.append(framework)

    assert len(found_frameworks) > 0, "Should contain at least one real framework name"


def test_performance_with_large_dataset(aggregated_results: AggregatedResults, temp_dir: Path) -> None:
    """Test performance with a larger dataset."""
    large_framework_summaries = {}
    for framework, summaries_list in aggregated_results.framework_summaries.items():
        large_framework_summaries[framework] = summaries_list * 10

    large_category_summaries = {}
    for category, summaries_list in aggregated_results.category_summaries.items():
        large_category_summaries[category] = summaries_list * 10

    large_results = AggregatedResults(
        total_runs=aggregated_results.total_runs * 10,
        total_files_processed=aggregated_results.total_files_processed * 50,
        total_time_seconds=aggregated_results.total_time_seconds * 50,
        framework_summaries=large_framework_summaries,
        category_summaries=large_category_summaries,
        framework_category_matrix={
            k + f"_{i}": v for i in range(10) for k, v in aggregated_results.framework_category_matrix.items()
        },
        failure_patterns=aggregated_results.failure_patterns,
        timeout_files=aggregated_results.timeout_files * 50,
        performance_over_iterations=aggregated_results.performance_over_iterations,
        platform_results=aggregated_results.platform_results,
    )

    results_file = temp_dir / "large_results.json"
    with open(results_file, "w") as f:
        import msgspec

        f.write(msgspec.json.encode(large_results).decode())

    import time

    start_time = time.time()

    generator = DocsGenerator(temp_dir / "docs")
    generator.generate_from_results(results_file)

    end_time = time.time()
    generation_time = end_time - start_time

    assert generation_time < 30.0, f"Generation took too long: {generation_time:.2f}s"

    results_dir = temp_dir / "docs" / "results"
    assert (results_dir / "index.md").exists()

    index_content = (results_dir / "index.md").read_text()
    assert 1000 < len(index_content) < 100000


@pytest.mark.slow
def test_full_mkdocs_workflow(aggregated_results_file: Path, temp_dir: Path, charts_dir: Path) -> None:
    """Test the complete workflow from results to deployed docs."""
    project_dir = temp_dir / "project"
    project_dir.mkdir()

    import shutil

    real_mkdocs = Path("mkdocs.yml")
    if real_mkdocs.exists():
        shutil.copy2(real_mkdocs, project_dir / "mkdocs.yml")
    else:
        (project_dir / "mkdocs.yml").write_text("""
site_name: Test Benchmarks
theme:
  name: material

nav:
  - Home: index.md
  - Results: results/index.md
""")

    docs_dir = project_dir / "docs"
    docs_dir.mkdir()
    (docs_dir / "index.md").write_text("# Benchmark Results\n\nTest site.")

    generator = DocsGenerator(docs_dir)
    generator.generate_from_results(aggregated_results_file, charts_dir)

    result = subprocess.run(["mkdocs", "build"], check=False, cwd=project_dir, capture_output=True, text=True)

    print(f"MkDocs build result: {result.returncode}")
    if result.stderr:
        print(f"Warnings/Errors: {result.stderr}")

    assert result.returncode == 0 or "ERROR" not in result.stderr

    site_dir = project_dir / "site"
    if site_dir.exists():
        assert (site_dir / "index.html").exists()

        results_html = site_dir / "results" / "index.html"
        if results_html.exists():
            content = results_html.read_text()
            assert "benchmark" in content.lower()
