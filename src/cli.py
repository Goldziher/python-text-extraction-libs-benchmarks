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
    """Main CLI command group for benchmark operations."""


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
    from .aggregate import ResultAggregator

    console.print("Aggregating benchmark results...")

    try:
        aggregator = ResultAggregator()
        result_dirs = [results_dir] if results_dir.is_dir() else []
        if result_dirs:
            aggregated = aggregator.aggregate_results(result_dirs)
            aggregator.save_results(aggregated, output_file.parent)
            console.print(f"[green]✓ Results aggregated to {output_file}[/green]")
        else:
            console.print("[yellow]No results found to aggregate[/yellow]")
    except Exception as e:
        console.print(f"[red]Aggregation failed: {e}[/red]")
        logger.error("Aggregation failed", error=str(e))
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
        logger.error("Documentation generation failed", error=str(e))
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
    from .report import ReportGenerator

    console.print("Generating benchmark report...")
    output_dir.mkdir(exist_ok=True)

    generator = ReportGenerator()

    try:
        with open(aggregated_file, "rb") as f:
            import msgspec

            from .types import AggregatedResults

            aggregated_results = msgspec.json.decode(f.read(), type=AggregatedResults)

        if output_format == "markdown":
            output_file = output_dir / "benchmark_report.md"
            generator.generate_markdown_report(aggregated_results, output_file)
        elif output_format == "html":
            output_file = output_dir / "benchmark_report.html"
            generator.generate_html_report(aggregated_results, output_file)
        else:
            output_file = output_dir / "benchmark_report.json"
            with open(output_file, "wb") as f:
                f.write(msgspec.json.encode(aggregated_results))

        console.print(f"[green]✓ Generated {output_format} report: {output_file}[/green]")
    except Exception as e:
        console.print(f"[red]Report generation failed: {e}[/red]")
        logger.error("Report generation failed", error=str(e))
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
    console.print("Generating benchmark visualizations...")
    output_dir.mkdir(exist_ok=True)

    visualizer = BenchmarkVisualizer(output_dir)

    try:
        generated_files = visualizer.generate_all_visualizations(results_file)
        console.print(f"[green]✓ Generated {len(generated_files)} visualizations:[/green]")
        for file in generated_files:
            console.print(f"  - {file}")
    except Exception as e:
        console.print(f"[red]Visualization failed: {e}[/red]")
        logger.error("Visualization failed", error=str(e))
        sys.exit(1)


@main.command(name="list-frameworks")
@click.option(
    "--output-format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def list_frameworks(output_format: str) -> None:
    from .config import get_supported_formats

    frameworks_info: dict[str, list[str]] = {}
    for framework in Framework:
        formats = get_supported_formats(framework)
        frameworks_info[framework.value] = sorted(formats)

    if output_format == "json":
        import json

        console.print(json.dumps(frameworks_info, indent=2))
    else:
        console.print("Available Frameworks and Supported Formats:\n")
        for fw_name, formats_list in frameworks_info.items():
            console.print(f"[bold]{fw_name}[/bold]")
            console.print(f"  Formats ({len(formats_list)}): {', '.join(formats_list[:10])}")
            if len(formats_list) > 10:
                console.print(f"  ... and {len(formats_list) - 10} more")
            console.print()


if __name__ == "__main__":
    main()
