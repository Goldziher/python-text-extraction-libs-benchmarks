"""Command-line interface for the benchmarking suite."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

if sys.version_info >= (3, 13):
    pass
else:
    pass

import click
from rich.console import Console

from .benchmark import ComprehensiveBenchmarkRunner
from .types import (
    BenchmarkConfig,
    DocumentCategory,
    FileType,
    Framework,
)

console = Console()


@click.group()
def main() -> None:
    """Python text extraction libraries benchmarking suite."""


@main.command(name="benchmark")
@click.option(
    "--framework",
    "-f",
    type=str,
    default="all",
    help="Framework to benchmark (comma-separated or 'all')",
)
@click.option(
    "--category",
    "-c",
    type=str,
    default="all",
    help="Document category to test (comma-separated or 'all')",
)
@click.option(
    "--iterations",
    "-i",
    type=int,
    default=3,
    help="Number of benchmark iterations",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default="results",
    help="Output directory for results",
)
@click.option(
    "--warmup-runs",
    "-w",
    type=int,
    default=1,
    help="Number of warmup runs",
)
@click.option(
    "--timeout",
    "-t",
    type=int,
    default=600,
    help="Timeout in seconds for each extraction",
)
@click.option(
    "--continue-on-error/--fail-fast",
    default=True,
    help="Continue benchmarking even if some files fail",
)
def benchmark(
    framework: str,
    category: str,
    iterations: int,
    output_dir: Path,
    warmup_runs: int,
    timeout: int,
    continue_on_error: bool,
) -> None:
    """Run comprehensive benchmarks for text extraction frameworks."""
    console.print("[bold blue]Starting comprehensive benchmark run...[/bold blue]")

    # Parse frameworks
    if framework == "all":
        frameworks = list(Framework)
    else:
        frameworks = []
        for fw_name in framework.split(","):
            fw_name_clean = fw_name.strip()
            try:
                frameworks.append(Framework(fw_name_clean))
            except ValueError:
                console.print(f"[red]Invalid framework: {fw_name_clean}[/red]")
                sys.exit(1)

    # Parse categories
    if category == "all":
        categories = list(DocumentCategory)
    else:
        categories = []
        for cat_name in category.split(","):
            cat_name_clean = cat_name.strip()
            try:
                categories.append(DocumentCategory(cat_name_clean))
            except ValueError:
                console.print(f"[red]Invalid category: {cat_name_clean}[/red]")
                sys.exit(1)

    # Create configuration
    config = BenchmarkConfig(
        frameworks=frameworks,
        categories=categories,
        iterations=iterations,
        output_dir=Path(output_dir),
        warmup_runs=warmup_runs,
        timeout_seconds=timeout,
        continue_on_error=continue_on_error,
    )

    # Run benchmarks
    runner = ComprehensiveBenchmarkRunner(config)

    try:
        results = asyncio.run(runner.run_benchmark_suite())
        console.print(f"[green]✓ Completed {len(results)} benchmarks[/green]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Benchmark interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]✗ Benchmark failed: {e}[/red]")
        sys.exit(1)


@main.command(name="aggregate")
@click.argument("input_dirs", nargs=-1, type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default="aggregated-results",
    help="Output directory for aggregated results",
)
def aggregate(input_dirs: tuple[Path, ...], output_dir: Path) -> None:
    """Aggregate results from multiple benchmark runs."""
    console.print("[bold blue]Aggregating benchmark results...[/bold blue]")

    from .aggregate import ResultAggregator

    aggregator = ResultAggregator()

    # If no input dirs provided, use current directory
    if not input_dirs:
        input_dirs = (Path(),)

    # Find all result files from all input directories
    result_files = []
    for input_dir in input_dirs:
        result_files.extend(input_dir.rglob("benchmark_results.json"))

    if not result_files:
        console.print("[red]No result files found[/red]")
        sys.exit(1)

    console.print(f"Found {len(result_files)} result files from {len(input_dirs)} directories")

    try:
        aggregated = aggregator.aggregate_results([f.parent for f in result_files])

        # Save aggregated results
        output_dir.mkdir(parents=True, exist_ok=True)
        aggregator.save_results(aggregated, output_dir)

        console.print(f"[green]✓ Results aggregated to {output_dir}[/green]")
    except Exception as e:
        console.print(f"[red]✗ Aggregation failed: {e}[/red]")
        sys.exit(1)


@main.command(name="report")
@click.option(
    "--aggregated-file",
    "-a",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    help="Path to aggregated results JSON file",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default="reports",
    help="Output directory for generated reports",
)
@click.option(
    "--format",
    "output_formats",
    multiple=True,
    type=click.Choice(["markdown", "json", "html"]),
    default=["markdown"],
    help="Output format(s) to generate",
)
def report(aggregated_file: Path | None, output_dir: Path, output_formats: tuple[str, ...]) -> None:
    """Generate reports from aggregated benchmark results."""
    console.print("[bold blue]Generating benchmark report...[/bold blue]")

    from .report import ReportGenerator

    generator = ReportGenerator()

    try:
        # Load aggregated results
        if aggregated_file:
            import msgspec

            with open(aggregated_file, "rb") as f:
                aggregated = msgspec.json.decode(f.read())
        else:
            # Default to looking for aggregated results in current directory
            default_file = Path("aggregated-results/aggregated_results.json")
            if default_file.exists():
                import msgspec

                with open(default_file, "rb") as f:
                    aggregated = msgspec.json.decode(f.read())
            else:
                console.print("[red]No aggregated results found. Use --aggregated-file or run aggregate first.[/red]")
                sys.exit(1)

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate reports
        for fmt in output_formats:
            if fmt == "markdown":
                report_path = output_dir / "benchmark_report.md"
                generator.generate_markdown_report(aggregated, report_path)
                console.print(f"[green]✓ Generated markdown report: {report_path}[/green]")
            elif fmt == "json":
                metrics_path = output_dir / "benchmark_metrics.json"
                generator.generate_json_metrics(aggregated, metrics_path)
                console.print(f"[green]✓ Generated JSON metrics: {metrics_path}[/green]")
            elif fmt == "html":
                html_path = output_dir / "benchmark_report.html"
                generator.generate_html_report(aggregated, html_path)
                console.print(f"[green]✓ Generated HTML report: {html_path}[/green]")

    except Exception as e:
        console.print(f"[red]✗ Report generation failed: {e}[/red]")
        sys.exit(1)


@main.command(name="list-frameworks")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON array")
def list_frameworks(output_json: bool) -> None:
    """List all supported frameworks."""
    frameworks = [framework.value for framework in Framework]

    if output_json:
        import json

        print(json.dumps(frameworks))
    else:
        console.print("[bold blue]Available Frameworks:[/bold blue]")
        for framework in frameworks:
            console.print(f"  - {framework}")


@main.command(name="list-categories")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON array")
def list_categories(output_json: bool) -> None:
    """List all available document categories."""
    categories = [cat.value for cat in DocumentCategory]

    if output_json:
        import json

        print(json.dumps(categories))
    else:
        console.print("[bold blue]Available Document Categories:[/bold blue]")
        for cat in categories:
            console.print(f"  - {cat}")


@main.command(name="list-file-types")
def list_file_types() -> None:
    """List all supported file types."""
    console.print("[bold blue]Supported File Types:[/bold blue]")
    for file_type in FileType:
        console.print(f"  - {file_type.value}")


if __name__ == "__main__":
    main()
