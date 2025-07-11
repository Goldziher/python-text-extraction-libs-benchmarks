#!/usr/bin/env python3
"""Load all available benchmark data and run per-file-type analysis."""

import json
from pathlib import Path
from typing import Any

from src.file_type_analysis import FileTypeAnalyzer


def find_all_benchmark_results() -> list[Path]:
    """Find all benchmark result JSON files in the repository."""
    base_dir = Path()
    result_files = []

    # Look for benchmark_results.json files
    for pattern in ["**/benchmark_results.json", "**/results.json", "**/*results*.json"]:
        result_files.extend(base_dir.glob(pattern))

    # Filter out cache and other non-benchmark files
    filtered_files = []
    for file_path in result_files:
        if any(exclude in str(file_path) for exclude in [".mypy_cache", "node_modules", ".git"]):
            continue
        filtered_files.append(file_path)

    return filtered_files


def _parse_json_data(data: Any, file_path: str) -> list[dict[str, Any]]:
    """Parse JSON data and extract benchmark results."""
    results = []

    if isinstance(data, list):
        # Direct list of benchmark results
        results.extend(data)
        print(f"  ✅ {file_path}: {len(data)} results")
    elif isinstance(data, dict) and "results" in data:
        # Wrapped in results key
        if isinstance(data["results"], list):
            results.extend(data["results"])
            print(f"  ✅ {file_path}: {len(data['results'])} results")
    elif isinstance(data, dict) and any(key.endswith("_results") for key in data):
        # Multiple result sets
        count = _extract_multiple_result_sets(data, results)
        if count > 0:
            print(f"  ✅ {file_path}: {count} results")
    elif _is_single_benchmark_result(data):
        # Individual result
        results.append(data)
        print(f"  ✅ {file_path}: 1 result")
    else:
        print(f"  ⚠️  {file_path}: Unknown format, skipping")

    return results


def _extract_multiple_result_sets(data: dict[str, Any], results: list[dict[str, Any]]) -> int:
    """Extract results from multiple result sets in data."""
    count = 0
    for key, value in data.items():
        if key.endswith("_results") and isinstance(value, list):
            results.extend(value)
            count += len(value)
    return count


def _is_single_benchmark_result(data: Any) -> bool:
    """Check if data looks like a single BenchmarkResult."""
    return isinstance(data, dict) and "file_path" in data and "framework" in data and "file_type" in data


def _load_file_data(file_path: str) -> list[dict[str, Any]]:
    """Load and parse a single result file."""
    try:
        with open(file_path) as f:
            data = json.load(f)
        return _parse_json_data(data, file_path)
    except json.JSONDecodeError as e:
        print(f"  ❌ {file_path}: JSON decode error - {e}")
        return []
    except Exception as e:
        print(f"  ❌ {file_path}: Error - {e}")
        return []


def _print_result_breakdown(all_results: list[dict[str, Any]]) -> None:
    """Print breakdown of results by framework and file type."""
    # Framework breakdown
    framework_counts = {}
    for result in all_results:
        fw = result.get("framework", "unknown")
        framework_counts[fw] = framework_counts.get(fw, 0) + 1

    print("\n🔧 Results by framework:")
    for framework, count in sorted(framework_counts.items()):
        print(f"  - {framework}: {count}")

    # File type breakdown
    file_type_counts = {}
    for result in all_results:
        ft = result.get("file_type", "unknown")
        file_type_counts[ft] = file_type_counts.get(ft, 0) + 1

    print("\n📄 Results by file type:")
    for file_type, count in sorted(file_type_counts.items()):
        print(f"  - {file_type}: {count}")


def load_all_benchmark_data() -> list[dict[str, Any]]:
    """Load and combine all available benchmark results."""
    result_files = find_all_benchmark_results()
    all_results = []

    print(f"Found {len(result_files)} potential result files:")

    for file_path in result_files:
        file_results = _load_file_data(file_path)
        all_results.extend(file_results)

    print(f"\n📊 Total results loaded: {len(all_results)}")
    _print_result_breakdown(all_results)

    return all_results


def main():
    """Main function to load data and run analysis."""
    print("🔍 Loading all available benchmark data...\n")

    # Load data
    all_results = load_all_benchmark_data()

    if not all_results:
        print("\n❌ No benchmark results found!")
        print("💡 Try running some benchmarks first:")
        print("   uv run python -m src.cli benchmark --framework extractous --category tiny")
        return

    # Run file type analysis
    print(f"\n📈 Running per-file-type analysis on {len(all_results)} results...")

    analyzer = FileTypeAnalyzer(all_results)
    output_dir = Path("file_type_analysis")

    analyzer.generate_file_type_performance_report(output_dir)
    analyzer.generate_insights_report(output_dir)

    print("\n✅ Analysis complete!")
    print(f"📁 Results saved in: {output_dir}/")
    print(f"📊 Charts: {output_dir}/*.png")
    print(f"📝 Insights: {output_dir}/performance_insights.md")
    print(f"📋 CSV: {output_dir}/file_type_performance_summary.csv")

    # Show top insights
    print("\n🏆 Quick insights:")

    top_success = analyzer.get_top_performing_frameworks("success_rate")
    top_speed = analyzer.get_top_performing_frameworks("files_per_second")

    print("  Top success rates:")
    for file_type, data in list(top_success.items())[:5]:  # Show top 5
        print(f"    {file_type}: {data['framework']} ({data['value']:.1f}%)")

    print("  Top speeds:")
    for file_type, data in list(top_speed.items())[:5]:  # Show top 5
        print(f"    {file_type}: {data['framework']} ({data['value']:.2f} files/sec)")


if __name__ == "__main__":
    main()
