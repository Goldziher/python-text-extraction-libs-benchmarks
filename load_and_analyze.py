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


def load_all_benchmark_data() -> list[dict[str, Any]]:
    """Load and combine all available benchmark results."""
    result_files = find_all_benchmark_results()
    all_results = []

    print(f"Found {len(result_files)} potential result files:")

    for file_path in result_files:
        try:
            with open(file_path) as f:
                data = json.load(f)

                # Handle different data formats
                if isinstance(data, list):
                    # Direct list of benchmark results
                    all_results.extend(data)
                    print(f"  ✅ {file_path}: {len(data)} results")
                elif isinstance(data, dict) and "results" in data:
                    # Wrapped in results key
                    results = data["results"]
                    if isinstance(results, list):
                        all_results.extend(results)
                        print(f"  ✅ {file_path}: {len(results)} results")
                elif isinstance(data, dict) and any(key.endswith("_results") for key in data):
                    # Multiple result sets
                    count = 0
                    for key, value in data.items():
                        if key.endswith("_results") and isinstance(value, list):
                            all_results.extend(value)
                            count += len(value)
                    if count > 0:
                        print(f"  ✅ {file_path}: {count} results")
                # Try to extract individual result if it looks like a BenchmarkResult
                elif "file_path" in data and "framework" in data and "file_type" in data:
                    all_results.append(data)
                    print(f"  ✅ {file_path}: 1 result")
                else:
                    print(f"  ⚠️  {file_path}: Unknown format, skipping")

        except json.JSONDecodeError as e:
            print(f"  ❌ {file_path}: JSON decode error - {e}")
        except Exception as e:
            print(f"  ❌ {file_path}: Error - {e}")

    print(f"\n📊 Total results loaded: {len(all_results)}")

    # Show breakdown by framework
    framework_counts = {}
    for result in all_results:
        fw = result.get("framework", "unknown")
        framework_counts[fw] = framework_counts.get(fw, 0) + 1

    print("\n🔧 Results by framework:")
    for framework, count in sorted(framework_counts.items()):
        print(f"  - {framework}: {count}")

    # Show breakdown by file type
    file_type_counts = {}
    for result in all_results:
        ft = result.get("file_type", "unknown")
        file_type_counts[ft] = file_type_counts.get(ft, 0) + 1

    print("\n📄 Results by file type:")
    for file_type, count in sorted(file_type_counts.items()):
        print(f"  - {file_type}: {count}")

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
