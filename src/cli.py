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
from rich.console import Console

from .benchmark import ComprehensiveBenchmarkRunner
from .html_report import HTMLReportGenerator
from .types import (
    BenchmarkConfig,
    DocumentCategory,
    FileType,
    Framework,
)
from .visualize import BenchmarkVisualizer

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
@click.option(
    "--enable-quality-assessment",
    is_flag=True,
    default=False,
    help="Enable quality assessment by saving extracted text for analysis",
)
@click.option(
    "--common-formats-only",
    is_flag=True,
    default=False,
    help="Only test formats supported by ALL frameworks (legacy, use --format-tier instead)",
)
@click.option(
    "--format-tier",
    type=click.Choice(["universal", "common", "all"], case_sensitive=False),
    default=None,
    help="Format tier to test: universal (5/5), common (4/5), or all",
)
@click.option(
    "--table-extraction-only",
    is_flag=True,
    default=False,
    help="Run benchmarks only on table extraction documents",
)
def benchmark(  # noqa: PLR0915, C901, PLR0912, PLR0913
    framework: str,
    category: str,
    iterations: int,
    output_dir: Path,
    warmup_runs: int,
    timeout: int,
    continue_on_error: bool,
    enable_quality_assessment: bool,
    common_formats_only: bool,
    format_tier: str | None,
    table_extraction_only: bool,
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

    # Show format tier info if specified
    if format_tier or common_formats_only:
        tier = format_tier or ("universal" if common_formats_only else None)
        if tier:
            from .config import TIER1_FORMATS, TIER2_FORMATS

            if tier == "universal":
                console.print(
                    f"[yellow]Testing only universal formats (5/5 frameworks): {sorted(TIER1_FORMATS)}[/yellow]"
                )
            elif tier == "common":
                console.print(f"[yellow]Testing common formats (4/5 frameworks): {sorted(TIER2_FORMATS)}[/yellow]")

    # Show table extraction mode info
    if table_extraction_only:
        console.print("[yellow]🔢 Table extraction mode: Only testing documents with tables[/yellow]")

    # Create configuration
    config = BenchmarkConfig(
        frameworks=frameworks,
        categories=categories,
        iterations=iterations,
        output_dir=output_dir,
        warmup_runs=warmup_runs,
        timeout_seconds=timeout,
        continue_on_error=continue_on_error,
        save_extracted_text=enable_quality_assessment,
        common_formats_only=common_formats_only,
        format_tier=format_tier if format_tier != "all" else None,
        table_extraction_only=table_extraction_only,
    )

    # Run benchmarks
    runner = ComprehensiveBenchmarkRunner(config)

    try:
        results = asyncio.run(runner.run_benchmark_suite())
        console.print(f"[green]✓ Completed {len(results)} benchmarks[/green]")

        # Automatically run quality assessment if enabled
        if enable_quality_assessment:
            console.print("[bold blue]Running quality assessment...[/bold blue]")
            results_file = output_dir / "benchmark_results.json"
            if results_file.exists():
                from .quality_assessment import enhance_benchmark_results_with_quality

                enhanced_file = enhance_benchmark_results_with_quality(results_file)
                console.print(f"[green]✓ Quality assessment completed: {enhanced_file}[/green]")
            else:
                console.print("[yellow]Warning: Could not find results file for quality assessment[/yellow]")

        # Run installation size check after benchmarks
        console.print("[bold blue]Collecting installation size information...[/bold blue]")
        try:
            from .check_installation_sizes import main as check_sizes

            check_sizes()

            # Move installation_sizes.json to output directory
            import shutil
            from pathlib import Path

            generated_file = Path("installation_sizes.json")
            if generated_file.exists():
                target_file = output_dir / "installation_sizes.json"
                shutil.move(str(generated_file), str(target_file))
                console.print(f"[green]✓ Installation sizes saved to {target_file}[/green]")

        except Exception as e:
            console.print(f"[yellow]Warning: Could not collect installation sizes: {e}[/yellow]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Benchmark interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]✗ Benchmark failed: {e}[/red]")
        import traceback

        console.print(f"[dim]{traceback.format_exc()}[/dim]")
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

            from .types import AggregatedResults

            with open(aggregated_file, "rb") as f:
                aggregated = msgspec.json.decode(f.read(), type=AggregatedResults)
        else:
            # Default to looking for aggregated results in current directory
            default_file = Path("aggregated-results/aggregated_results.json")
            if default_file.exists():
                import msgspec

                from .types import AggregatedResults

                with open(default_file, "rb") as f:
                    aggregated = msgspec.json.decode(f.read(), type=AggregatedResults)
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
                # First generate visualizations
                visualizer = BenchmarkVisualizer(output_dir / "charts")
                # Use the already loaded aggregated file path
                if aggregated_file:
                    agg_path = aggregated_file
                else:
                    agg_path = Path("aggregated-results/aggregated_results.json")
                    if not agg_path.exists():
                        agg_path = Path("results/aggregated_results.json")
                
                if agg_path.exists():
                    visualizer.generate_all_visualizations(agg_path)
                
                # Then generate HTML report
                html_generator = HTMLReportGenerator(output_dir / "charts")
                html_generator.generate_report(agg_path, html_path)
                console.print(f"[green]✓ Generated HTML report with visualizations: {html_path}[/green]")

    except Exception as e:
        console.print(f"[red]✗ Report generation failed: {e}[/red]")
        sys.exit(1)


@main.command(name="visualize")
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
    default="visualizations",
    help="Output directory for generated visualizations",
)
def visualize(aggregated_file: Path | None, output_dir: Path) -> None:
    """Generate comprehensive visualizations from benchmark results."""
    console.print("[bold blue]Generating benchmark visualizations...[/bold blue]")

    from .visualize import BenchmarkVisualizer

    visualizer = BenchmarkVisualizer(output_dir)

    try:
        # Find aggregated file if not provided
        if not aggregated_file:
            default_file = Path("aggregated-results/aggregated_results.json")
            if default_file.exists():
                aggregated_file = default_file
            else:
                console.print("[red]No aggregated results found. Use --aggregated-file or run aggregate first.[/red]")
                sys.exit(1)

        # Generate all visualizations
        generated_files = visualizer.generate_all_visualizations(aggregated_file)

        console.print(f"[green]✓ Generated {len(generated_files)} visualizations:[/green]")
        for file_path in generated_files:
            console.print(f"  - {file_path}")

        # Generate summary metrics for README
        import json

        summary = visualizer.generate_summary_metrics(aggregated_file)
        summary_file = output_dir / "summary_metrics.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        console.print(f"[green]✓ Generated summary metrics: {summary_file}[/green]")

        # Generate installation size chart if data exists
        installation_sizes_file = Path("installation_sizes.json")
        if installation_sizes_file.exists():
            try:
                visualizer.generate_installation_size_chart(installation_sizes_file)
                console.print("[green]✓ Generated installation size chart[/green]")
            except Exception as e:
                console.print(f"[yellow]Warning: Could not generate installation size chart: {e}[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Visualization generation failed: {e}[/red]")
        sys.exit(1)


@main.command(name="quality-assess")
@click.option(
    "--results-file",
    "-r",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    required=True,
    help="Path to benchmark results JSON file",
)
@click.option(
    "--reference-dir",
    "-ref",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Directory containing reference text files for comparison",
)
@click.option(
    "--output-file",
    "-o",
    type=click.Path(file_okay=True, dir_okay=False, path_type=Path),
    help="Output file for enhanced results (default: enhanced_<original_name>)",
)
def quality_assess(results_file: Path, reference_dir: Path | None, output_file: Path | None) -> None:
    """Enhance benchmark results with ML-based quality assessment."""
    console.print("[bold blue]Running quality assessment on benchmark results...[/bold blue]")

    try:
        from .quality_assessment import enhance_benchmark_results_with_quality

        # Enhance results with quality metrics
        enhanced_file = enhance_benchmark_results_with_quality(results_file, reference_dir)

        # Move to custom output file if specified
        if output_file:
            enhanced_file.rename(output_file)
            enhanced_file = output_file

        console.print(f"[green]✓ Enhanced results saved to: {enhanced_file}[/green]")

        # Show quality summary
        import msgspec

        with open(enhanced_file, "rb") as f:
            results = msgspec.json.decode(f.read())

        quality_scores = [
            result["overall_quality_score"]
            for result in results
            if isinstance(result, dict) and result.get("overall_quality_score") is not None
        ]

        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)
            console.print("[cyan]📊 Quality Summary:[/cyan]")
            console.print(f"  - Results with quality scores: {len(quality_scores)}")
            console.print(f"  - Average quality score: {avg_quality:.3f}")
            console.print(f"  - Quality range: {min(quality_scores):.3f} - {max(quality_scores):.3f}")
        else:
            console.print("[yellow]No quality scores generated (no successful extractions with text)[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Quality assessment failed: {e}[/red]")
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


@main.command(name="installation-sizes")
@click.option("--output-file", "-o", type=click.Path(), help="Save results to JSON file")
@click.option("--include-charts", is_flag=True, help="Generate visualization charts")
def installation_sizes(output_file: str | None, include_charts: bool) -> None:
    """Check installation sizes of all frameworks."""
    import shutil
    from pathlib import Path

    from .check_installation_sizes import main as check_sizes

    console.print("[bold blue]Checking framework installation sizes...[/bold blue]")

    # Run the size check
    try:
        check_sizes()

        # If output file specified, copy the generated file
        if output_file:
            generated_file = Path("installation_sizes.json")
            if generated_file.exists():
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(generated_file, output_path)
                console.print(f"[green]✓ Results saved to {output_path}[/green]")
            else:
                console.print("[yellow]Warning: Generated file not found[/yellow]")

        if include_charts:
            console.print("[yellow]Chart generation for installation sizes coming soon![/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Installation size check failed: {e}[/red]")
        sys.exit(1)


@main.command(name="file-type-analysis")
@click.option(
    "--results-dir",
    "-r",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=".",
    help="Directory containing benchmark results",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    default="file_type_analysis",
    help="Output directory for analysis results",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["all", "charts", "csv", "insights"], case_sensitive=False),
    default="all",
    help="Output format(s) to generate",
)
@click.option(
    "--interactive",
    is_flag=True,
    help="Generate interactive HTML dashboard",
)
def _find_benchmark_result_files(results_dir: Path) -> list[Path]:
    """Find and filter benchmark result files."""
    result_files = []
    for pattern in ["**/benchmark_results.json", "**/results.json", "**/*results*.json"]:
        result_files.extend(results_dir.glob(pattern))

    # Filter out cache and other non-benchmark files
    exclude_patterns = [".mypy_cache", "node_modules", ".git"]
    return [
        file_path for file_path in result_files if not any(exclude in str(file_path) for exclude in exclude_patterns)
    ]


def _load_benchmark_results(filtered_files: list[Path]) -> list[dict[str, Any]]:
    """Load benchmark results from files."""
    import json

    all_results = []
    for file_path in filtered_files:
        try:
            with open(file_path) as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_results.extend(data)
                    console.print(f"[green]✓ Loaded {len(data)} results from {file_path.name}[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠ Skipped {file_path.name}: {e}[/yellow]")

    return all_results


def _generate_analysis_outputs(analyzer: Any, output_dir: Path, output_format: str) -> None:
    """Generate analysis outputs based on format selection."""
    if output_format in ["all", "charts"]:
        console.print("[cyan]📈 Generating performance charts...[/cyan]")

    if output_format in ["all", "csv"]:
        console.print("[cyan]📋 Generating CSV summary...[/cyan]")

    if output_format in ["all", "insights"]:
        console.print("[cyan]🏆 Generating insights report...[/cyan]")

    analyzer.generate_file_type_performance_report(output_dir)
    analyzer.generate_insights_report(output_dir)


def _print_analysis_results(output_dir: Path, output_format: str, interactive: bool) -> None:
    """Print analysis results and file locations."""
    console.print("\n[bold green]✅ Analysis complete![/bold green]")
    console.print(f"📁 Results saved in: {output_dir}/")

    if output_format in ["all", "charts"]:
        console.print(f"📊 Charts: {output_dir}/*.png")
    if output_format in ["all", "csv"]:
        console.print(f"📋 CSV: {output_dir}/file_type_performance_summary.csv")
    if output_format in ["all", "insights"]:
        console.print(f"📝 Insights: {output_dir}/performance_insights.md")
    if interactive:
        console.print(f"🌐 Dashboard: {output_dir}/interactive_dashboard.html")


def _print_quick_insights(analyzer: Any) -> None:
    """Print quick performance insights."""
    console.print("\n[bold cyan]🏆 Quick Insights:[/bold cyan]")
    top_success = analyzer.get_top_performing_frameworks("success_rate")
    top_speed = analyzer.get_top_performing_frameworks("files_per_second")

    console.print("  [green]Top success rates:[/green]")
    for file_type, data in list(top_success.items())[:3]:
        console.print(f"    {file_type}: {data['framework']} ({data['value']:.1f}%)")

    console.print("  [blue]Top speeds:[/blue]")
    for file_type, data in list(top_speed.items())[:3]:
        console.print(f"    {file_type}: {data['framework']} ({data['value']:.2f} files/sec)")


def file_type_analysis(
    results_dir: Path,
    output_dir: Path,
    output_format: str,
    interactive: bool,
) -> None:
    """Generate per-file-type performance and quality analysis."""
    try:
        from .file_type_analysis import FileTypeAnalyzer

        console.print("[bold blue]🔍 Loading benchmark results...[/bold blue]")

        # Find benchmark result files
        filtered_files = _find_benchmark_result_files(results_dir)
        if not filtered_files:
            console.print(f"[red]✗ No benchmark results found in {results_dir}[/red]")
            console.print("[yellow]💡 Try running benchmarks first:[/yellow]")
            console.print("   uv run python -m src.cli benchmark --framework extractous --category tiny")
            sys.exit(1)

        # Load all results
        all_results = _load_benchmark_results(filtered_files)
        if not all_results:
            console.print("[red]✗ No valid benchmark data found[/red]")
            sys.exit(1)

        console.print(f"[bold green]📊 Analyzing {len(all_results)} results...[/bold green]")

        # Run analysis
        analyzer = FileTypeAnalyzer(all_results)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate outputs
        if output_format in ["all", "charts", "csv", "insights"]:
            _generate_analysis_outputs(analyzer, output_dir, output_format)

        # Generate interactive dashboard if requested
        if interactive:
            console.print("[cyan]🌐 Generating interactive dashboard...[/cyan]")
            _generate_interactive_dashboard(analyzer, output_dir)

        # Print results
        _print_analysis_results(output_dir, output_format, interactive)
        _print_quick_insights(analyzer)

    except Exception as e:
        console.print(f"[red]✗ File type analysis failed: {e}[/red]")
        sys.exit(1)


def _generate_interactive_dashboard(analyzer: Any, output_dir: Path) -> None:
    """Generate an interactive HTML dashboard for file type analysis."""
    try:
        from .interactive_dashboard import InteractiveDashboardGenerator

        generator = InteractiveDashboardGenerator(analyzer)
        generator.generate_dashboard(output_dir)
        console.print("[green]✅ Interactive dashboard generated successfully![/green]")
    except Exception as e:
        console.print(f"[yellow]⚠ Dashboard generation failed: {e}[/yellow]")
        console.print("[yellow]Continuing with static analysis...[/yellow]")


@main.command(name="metadata-analysis")
@click.option(
    "--results-dir",
    type=click.Path(exists=True, path_type=Path),
    default=Path("results"),
    help="Directory containing benchmark results",
)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=Path("metadata_analysis"),
    help="Output directory for metadata analysis",
)
@click.option(
    "--exclude-kreuzberg",
    is_flag=True,
    default=True,
    help="Exclude Kreuzberg results (while it's being updated)",
)
def metadata_analysis(results_dir: Path, output_dir: Path, exclude_kreuzberg: bool) -> None:  # noqa: ARG001
    """Analyze metadata extraction capabilities across frameworks."""
    console.print("[bold blue]🔍 Metadata Extraction Analysis[/bold blue]")

    try:
        # Find results file
        results_file = results_dir / "results.json"
        if not results_file.exists():
            console.print(f"[red]✗ Results file not found: {results_file}[/red]")
            sys.exit(1)

        # Import and run metadata analysis
        from .metadata_analysis import analyze_metadata_from_results

        console.print(f"📊 Analyzing metadata from {results_file}...")
        analyze_metadata_from_results(results_file, output_dir)

        console.print("\n[green]✅ Metadata analysis complete![/green]")
        console.print(f"📁 Reports saved to: {output_dir}")

        # List generated files
        console.print("\n[bold cyan]Generated files:[/bold cyan]")
        for file in sorted(output_dir.glob("*")):
            if file.is_file():
                console.print(f"  • {file.name}")

    except Exception as e:
        console.print(f"[red]✗ Metadata analysis failed: {e}[/red]")
        sys.exit(1)


@main.command(name="table-analysis")
@click.option(
    "--results-dir",
    type=click.Path(exists=True, path_type=Path),
    default=Path("results"),
    help="Directory containing benchmark results",
)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=Path("table_analysis"),
    help="Output directory for table analysis",
)
def table_analysis(results_dir: Path, output_dir: Path) -> None:
    """Analyze table extraction capabilities across frameworks."""
    console.print("[bold blue]📊 Table Extraction Analysis[/bold blue]")

    try:
        # Find results file
        results_file = results_dir / "results.json"
        if not results_file.exists():
            # Try benchmark_results.json as fallback
            results_file = results_dir / "benchmark_results.json"
            if not results_file.exists():
                console.print(f"[red]✗ Results file not found in {results_dir}[/red]")
                console.print("[yellow]💡 Try running benchmarks first with table documents[/yellow]")
                sys.exit(1)

        # Import and run table analysis
        from .table_analysis import analyze_table_extraction_from_results

        console.print(f"📊 Analyzing table extraction from {results_file}...")
        analyze_table_extraction_from_results(results_file, output_dir)

        console.print("\n[green]✅ Table analysis complete![/green]")
        console.print(f"📁 Reports saved to: {output_dir}")

        # List generated files
        console.print("\n[bold cyan]Generated files:[/bold cyan]")
        for file in sorted(output_dir.glob("*")):
            if file.is_file():
                console.print(f"  • {file.name}")

        # Show quick insights
        json_file = output_dir / "table_extraction_analysis.json"
        if json_file.exists():
            import json

            with open(json_file) as f:
                analysis = json.load(f)

            summary = analysis.get("summary", {})
            console.print("\n[bold cyan]📋 Quick Insights:[/bold cyan]")
            console.print(f"  🏆 Best for structure: {summary.get('best_framework_structure', 'N/A')}")
            console.print(f"  🔍 Best for detection: {summary.get('best_framework_detection', 'N/A')}")
            console.print(f"  ⚡ Fastest: {summary.get('best_framework_speed', 'N/A')}")
            console.print(f"  📄 Table files analyzed: {analysis.get('total_table_files', 0)}")

    except Exception as e:
        console.print(f"[red]✗ Table analysis failed: {e}[/red]")
        import traceback

        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    main()
