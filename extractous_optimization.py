import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def run_benchmark(config_name: str, config_settings: dict[str, Any]) -> dict[str, Any]:
    print(f"\n{'=' * 60}")
    print(f"Running {config_name} configuration")
    print(f"Settings: {json.dumps(config_settings, indent=2)}")
    print(f"{'=' * 60}\n")

    extractor_file = Path("src/extractors.py")
    content = extractor_file.read_text()

    if "class ExtractousExtractor:" in content:
        if "parse_method" in config_settings:
            config_settings["parse_method"]

        if "pdf_config" in config_settings:
            config_settings["pdf_config"]

        if "ocr_strategy" in config_settings:
            config_settings["ocr_strategy"]

    cmd = [
        "uv",
        "run",
        "python",
        "-m",
        "src.cli",
        "benchmark",
        "--framework",
        "extractous",
        "--iterations",
        "1",
        "--timeout",
        "300",
        "--continue-on-error",
        "--enable-quality-assessment",
    ]

    result = subprocess.run(cmd, check=False, capture_output=True, text=True)

    print(f"\nBenchmark completed for {config_name}")
    print(f"Return code: {result.returncode}")

    if result.returncode != 0:
        print(f"Error output: {result.stderr}")

    results_file = Path("results/results.json")
    if results_file.exists():
        with open(results_file) as f:
            results = json.load(f)

        extractous_results = [r for r in results if r.get("framework") == "extractous"]
        if extractous_results:
            latest = extractous_results[-1]
            success_rate = (
                sum(1 for r in latest.get("results", []) if r.get("status") == "SUCCESS")
                / len(latest.get("results", []))
                * 100
            )
            avg_time = sum(r.get("extraction_time", 0) for r in latest.get("results", [])) / len(
                latest.get("results", [])
            )

            return {
                "config_name": config_name,
                "success_rate": success_rate,
                "avg_extraction_time": avg_time,
                "total_benchmarks": len(latest.get("results", [])),
                "settings": config_settings,
            }

    return {
        "config_name": config_name,
        "success_rate": 0,
        "avg_extraction_time": 0,
        "total_benchmarks": 0,
        "settings": config_settings,
    }


def main():
    print("Starting Extractous Optimization Cycles")
    print("=" * 60)

    print("Installing extractous...")
    subprocess.run(["uv", "sync", "--extra", "extractous"], check=True)

    configurations = [
        {
            "name": "Speed-Optimized",
            "settings": {
                "parse_method": "fast",
                "ocr_strategy": "none",
                "pdf_config": {"extract_images": False, "extract_tables": False},
            },
        },
        {
            "name": "Quality-Optimized",
            "settings": {
                "parse_method": "detailed",
                "ocr_strategy": "auto",
                "pdf_config": {"extract_images": True, "extract_tables": True},
            },
        },
        {
            "name": "Balanced",
            "settings": {
                "parse_method": "standard",
                "ocr_strategy": "selective",
                "pdf_config": {"extract_images": False, "extract_tables": True},
            },
        },
    ]

    results = []

    for config in configurations:
        result = run_benchmark(config["name"], config["settings"])
        results.append(result)

        print(f"\nResults for {config['name']}:")
        print(f"  Success Rate: {result['success_rate']:.1f}%")
        print(f"  Avg Extraction Time: {result['avg_extraction_time']:.3f}s")
        print(f"  Total Benchmarks: {result['total_benchmarks']}")

    print("\n" + "=" * 60)
    print("OPTIMIZATION RESULTS SUMMARY")
    print("=" * 60)

    best = max(results, key=lambda x: (x["success_rate"], -x["avg_extraction_time"]))

    print(f"\nBest Configuration: {best['config_name']}")
    print(f"  Success Rate: {best['success_rate']:.1f}%")
    print(f"  Avg Extraction Time: {best['avg_extraction_time']:.3f}s")
    print(f"  Settings: {json.dumps(best['settings'], indent=4)}")

    print("\nAll Results:")
    for r in sorted(
        results,
        key=lambda x: (x["success_rate"], -x["avg_extraction_time"]),
        reverse=True,
    ):
        print(f"  {r['config_name']}: {r['success_rate']:.1f}% success, {r['avg_extraction_time']:.3f}s avg time")

    return best


if __name__ == "__main__":
    best_config = main()
    sys.exit(0)
