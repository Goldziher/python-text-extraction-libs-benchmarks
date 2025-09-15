"""Command-line interface for the benchmarking suite.

Simplified, idiomatic approach:
- Each framework tests against its supported formats only
- No complex filtering or tiers
- Automatic format detection based on framework capabilities
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import click
from rich.console import Console

from .benchmark import ComprehensiveBenchmarkRunner
from .logger import get_logger
from .types import BenchmarkConfig, DocumentCategory, Framework
from .visualize import BenchmarkVisualizer

console = Console()
logger = get_logger(__name__)


@click.group()
def main() -> None:
    """Python text extraction libraries benchmarking suite."""


@main.command(name="benchmark")
@click.option(
    "--framework",
    "-f",
    type=str,
    default="all",
    help="Framework to benchmark (name or 'all')",
)
@click.option(
    "--iterations",
    "-i",
    type=int,
    default=1,
    help="Number of benchmark iterations",
)
@click.option(
    "--timeout",
    "-t",
    type=int,
    default=300,
    help="Timeout in seconds for each extraction",
)
@click.option(
    "--continue-on-error",
    is_flag=True,
    default=True,
    help="Continue benchmarking even if some files fail",
)
@click.option(
    "--enable-quality-assessment/--no-quality-assessment",
    default=True,
    help="Save extracted text for quality analysis (enabled by default)",
)
def benchmark(
    framework: str,
    iterations: int,
    timeout: int,
    continue_on_error: bool,
    enable_quality_assessment: bool,
) -> None:
    """Run benchmarks for text extraction frameworks.

    Each framework automatically tests against its supported file formats.
    No need to specify categories or file types - the benchmark knows what
    each framework can handle based on 2025 documentation.
    """
    frameworks = [f.value for f in Framework] if framework.lower() == "all" else [framework]

    valid_frameworks = {f.value for f in Framework}
    invalid = [f for f in frameworks if f not in valid_frameworks]
    if invalid:
        console.print(f"[red]Invalid frameworks: {invalid}[/red]")
        console.print(f"Valid options: {list(valid_frameworks)}")
        sys.exit(1)

    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)

    framework_enums = []
    for fw in frameworks:
        try:
            framework_enums.append(Framework(fw))
        except ValueError as e:
            console.print(f"[red]Invalid framework: {fw}[/red]")
            console.print(f"Valid options: {[f.value for f in Framework]}")
            raise click.Abort from e

    config = BenchmarkConfig(
        frameworks=framework_enums,
        categories=list(DocumentCategory),
        file_types=None,
        iterations=iterations,
        warmup_runs=1,
        timeout_seconds=timeout,
        output_dir=output_dir,
        continue_on_error=continue_on_error,
        max_run_duration_minutes=30,
        save_extracted_text=enable_quality_assessment,
        enable_quality_assessment=enable_quality_assessment,
    )

    console.print("Starting comprehensive benchmark run...")
    runner = ComprehensiveBenchmarkRunner(config)

    try:
        results = asyncio.run(runner.run_benchmark_suite())
        console.print(f"[green]✓ Completed {len(results)} benchmarks[/green]")
    except KeyboardInterrupt:
        console.print("[yellow]Benchmark interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Benchmark failed: {e}[/red]")
        logger.error("Benchmark failed", error=str(e))
        sys.exit(1)


@main.command(name="aggregate")
@click.option(
    "--results-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default="results",
    help="Directory containing benchmark results",
)
@click.option(
    "--output-file",
    type=click.Path(dir_okay=False, path_type=Path),
    default="results/aggregated.json",
    help="Output file for aggregated results",
)
def aggregate(results_dir: Path, output_file: Path) -> None:
    """Aggregate benchmark results from multiple runs."""
    from .aggregate import aggregate_results

    console.print("Aggregating benchmark results...")

    try:
        result = aggregate_results(results_dir, output_file)
        if result:
            console.print(f"[green]✓ Results aggregated to {output_file}[/green]")
        else:
            console.print("[yellow]No results found to aggregate[/yellow]")
    except Exception as e:
        console.print(f"[red]Aggregation failed: {e}[/red]")
        logger.exception("Aggregation failed")
        sys.exit(1)


@main.command(name="docs")
@click.option(
    "--results-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default="results/results.json",
    help="Benchmark results file",
)
@click.option(
    "--aggregated-file",
    type=click.Path(dir_okay=False, path_type=Path),
    default="results/aggregated.json",
    help="Aggregated results file",
)
@click.option(
    "--docs-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default="docs",
    help="Documentation output directory",
)
def docs(results_file: Path, aggregated_file: Path, docs_dir: Path) -> None:
    """Generate comprehensive MkDocs documentation from benchmark results."""
    from .docs_generator import DocsGenerator

    console.print("Generating comprehensive documentation...")

    generator = DocsGenerator(docs_dir)

    try:
        generator.generate_all(
            results_file=results_file if results_file.exists() else None,
            aggregated_file=aggregated_file if aggregated_file.exists() else None,
        )
        console.print(f"[green]✓ Generated documentation in {docs_dir}[/green]")
        console.print("[blue]Run 'mkdocs serve' to preview the documentation[/blue]")
    except Exception as e:
        console.print(f"[red]Documentation generation failed: {e}[/red]")
        logger.exception("Documentation generation failed")
        sys.exit(1)


@main.command(name="report")
@click.option(
    "--output-format",
    type=click.Choice(["markdown", "json", "html"]),
    default="markdown",
    help="Report format",
)
@click.option(
    "--aggregated-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default="results/aggregated.json",
    help="Aggregated results file",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default="reports",
    help="Output directory for reports",
)
def report(output_format: str, aggregated_file: Path, output_dir: Path) -> None:
    """Generate benchmark reports from aggregated results."""
    from .reporting import ReportGenerator

    console.print("Generating benchmark report...")
    output_dir.mkdir(exist_ok=True)

    generator = ReportGenerator(aggregated_file)

    try:
        if output_format == "markdown":
            output_file = output_dir / "benchmark_report.md"
            generator.generate_markdown_report(output_file)
        elif output_format == "html":
            output_file = output_dir / "benchmark_report.html"
            generator.generate_html_report(output_file)
        else:
            output_file = output_dir / "benchmark_report.json"
            generator.generate_json_report(output_file)

        console.print(f"[green]✓ Generated {output_format} report: {output_file}[/green]")
    except Exception as e:
        console.print(f"[red]Report generation failed: {e}[/red]")
        logger.exception("Report generation failed")
        sys.exit(1)


@main.command(name="visualize")
@click.option(
    "--results-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default="results/aggregated.json",
    help="Aggregated results file",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default="visualizations",
    help="Output directory for visualizations",
)
def visualize(results_file: Path, output_dir: Path) -> None:
    """Generate visualization charts from benchmark results."""
    console.print("Generating benchmark visualizations...")
    output_dir.mkdir(exist_ok=True)

    visualizer = BenchmarkVisualizer(results_file, output_dir)

    try:
        generated_files = visualizer.generate_all_visualizations()
        console.print(f"[green]✓ Generated {len(generated_files)} visualizations:[/green]")
        for file in generated_files:
            console.print(f"  - {file}")
    except Exception as e:
        console.print(f"[red]Visualization failed: {e}[/red]")
        logger.exception("Visualization failed")
        sys.exit(1)


@main.command(name="list-frameworks")
@click.option(
    "--output-format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def list_frameworks(output_format: str) -> None:
    """List all available frameworks and their supported formats."""
    from .config import get_supported_formats

    frameworks_info = {}
    for framework in Framework:
        formats = get_supported_formats(framework)
        frameworks_info[framework.value] = sorted(formats)

    if output_format == "json":
        import json

        console.print(json.dumps(frameworks_info, indent=2))
    else:
        console.print("Available Frameworks and Supported Formats:\n")
        for fw_name, formats in frameworks_info.items():
            console.print(f"[bold]{fw_name}[/bold]")
            console.print(f"  Formats ({len(formats)}): {', '.join(formats[:10])}")
            if len(formats) > 10:
                console.print(f"  ... and {len(formats) - 10} more")
            console.print()


if __name__ == "__main__":
    main()
