"""Command-line interface for the benchmarking suite."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 13):
    pass
else:
    pass

import click
import msgspec
from rich.console import Console

from .benchmark import BenchmarkRunner
from .reporting import BenchmarkReporter
from .types import FileType, Framework

console = Console()


@click.group()
def main() -> None:
    """Python text extraction libraries benchmarking suite."""


@main.command()
@click.option(
    "--test-files-dir",
    "-t",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=True,
    help="Directory containing test files",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default="results",
    help="Output directory for results",
)
@click.option(
    "--frameworks",
    "-f",
    multiple=True,
    type=click.Choice([f.value for f in Framework]),
    help="Frameworks to benchmark (default: all)",
)
@click.option(
    "--file-types",
    multiple=True,
    type=click.Choice([ft.value for ft in FileType]),
    help="File types to test (default: all)",
)
@click.option(
    "--timeout",
    default=300,
    help="Timeout in seconds for each extraction",
)
@click.option(
    "--save-charts/--no-charts",
    default=True,
    help="Generate and save performance charts",
)
def run(
    test_files_dir: Path,
    output_dir: Path,
    frameworks: tuple[str, ...],
    file_types: tuple[str, ...],
    timeout: int,
    save_charts: bool,
) -> None:
    """Run benchmarks for text extraction frameworks."""
    console.print("[bold green]Starting Text Extraction Benchmarks[/bold green]")

    # Parse framework and file type selections
    selected_frameworks = [Framework(f) for f in frameworks] if frameworks else list(Framework)
    selected_file_types = [FileType(ft) for ft in file_types] if file_types else list(FileType)

    console.print(f"Selected frameworks: {[f.value for f in selected_frameworks]}")
    console.print(f"Selected file types: {[ft.value for ft in selected_file_types]}")
    console.print(f"Test files directory: {test_files_dir}")
    console.print(f"Output directory: {output_dir}")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run benchmarks
    runner = BenchmarkRunner(
        frameworks=selected_frameworks,
        file_types=selected_file_types,
        timeout_seconds=timeout,
    )

    try:
        results = asyncio.run(runner.run_benchmarks(test_files_dir))
        summaries = runner.generate_summary()

        console.print(f"[bold green]Completed {len(results)} benchmark runs[/bold green]")

        # Generate reports
        reporter = BenchmarkReporter(results, summaries)

        # Print summary to console
        reporter.print_summary_table()

        # Save results
        reporter.save_results_csv(output_dir / "detailed_results.csv")
        reporter.save_summary_csv(output_dir / "summary_results.csv")

        # Save results as JSON using msgspec
        with open(output_dir / "results.json", "w") as f:
            encoded = msgspec.json.encode(results)
            f.write(encoded.decode())

        with open(output_dir / "summaries.json", "w") as f:
            encoded = msgspec.json.encode(summaries)
            f.write(encoded.decode())

        # Generate charts if requested
        if save_charts:
            reporter.create_performance_charts(output_dir / "charts")

        console.print(f"[bold green]All results saved to: {output_dir}[/bold green]")

    except Exception as e:
        console.print(f"[bold red]Error running benchmarks: {e}[/bold red]")
        sys.exit(1)


@main.command()
@click.option(
    "--results-dir",
    "-r",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=True,
    help="Directory containing benchmark results",
)
@click.option(
    "--output-format",
    type=click.Choice(["table", "csv", "json", "charts"]),
    default="table",
    help="Output format for the report",
)
def report(results_dir: Path, output_format: str) -> None:
    """Generate reports from existing benchmark results."""
    console.print("[bold blue]Generating Benchmark Report[/bold blue]")

    try:
        # Load results
        results_file = results_dir / "results.json"
        summaries_file = results_dir / "summaries.json"

        if not results_file.exists() or not summaries_file.exists():
            console.print("[bold red]Results files not found. Please run benchmarks first.[/bold red]")
            sys.exit(1)

        with open(results_file) as f:
            results = msgspec.json.decode(f.read().encode(), type=list[Any])  # TODO: Fix type

        with open(summaries_file) as f:
            summaries = msgspec.json.decode(f.read().encode(), type=list[Any])  # TODO: Fix type

        reporter = BenchmarkReporter(results, summaries)

        if output_format == "table":
            reporter.print_summary_table()
        elif output_format == "csv":
            reporter.save_results_csv(results_dir / "report_detailed.csv")
            reporter.save_summary_csv(results_dir / "report_summary.csv")
        elif output_format == "charts":
            reporter.create_performance_charts(results_dir / "charts")
        elif output_format == "json":
            console.print("Results are already in JSON format in the results directory")

    except Exception as e:
        console.print(f"[bold red]Error generating report: {e}[/bold red]")
        sys.exit(1)


@main.command()
def list_frameworks() -> None:
    """List all supported frameworks."""
    console.print("[bold blue]Supported Frameworks:[/bold blue]")
    for framework in Framework:
        console.print(f"  - {framework.value}")


@main.command()
def list_file_types() -> None:
    """List all supported file types."""
    console.print("[bold blue]Supported File Types:[/bold blue]")
    for file_type in FileType:
        console.print(f"  - {file_type.value}")


if __name__ == "__main__":
    main()
