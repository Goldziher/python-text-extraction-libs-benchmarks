"""Table extraction analysis for benchmarking frameworks."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import msgspec
import pandas as pd

from .types import BenchmarkResult, ExtractionStatus


class TableExtractionAnalyzer:
    """Analyze table extraction quality across frameworks."""

    def __init__(self, results: list[BenchmarkResult]) -> None:
        """Initialize with benchmark results."""
        self.results = results
        self.table_files = self._identify_table_files()

    def _identify_table_files(self) -> list[str]:
        """Identify files that likely contain tables."""
        table_keywords = [
            "table",
            "spreadsheet",
            "excel",
            "csv",
            "xlsx",
            "xls",
            "stanley-cups",
            "embedded-images-tables",
            "docx-tables",
            "word_tables",
            "tablecell",
        ]

        table_files = []
        for result in self.results:
            file_path = Path(result.file_path).name.lower()
            if any(keyword in file_path for keyword in table_keywords):
                table_files.append(result.file_path)

        return list(set(table_files))

    def analyze_table_extraction_quality(self) -> dict[str, Any]:
        """Analyze table extraction quality across frameworks."""
        analysis = {
            "total_table_files": len(self.table_files),
            "framework_analysis": {},
            "file_analysis": {},
            "table_structure_preservation": {},
            "summary": {},
        }

        # Group results by framework and file
        framework_results = {}
        for result in self.results:
            if result.file_path in self.table_files:
                framework = result.framework.value
                if framework not in framework_results:
                    framework_results[framework] = []
                framework_results[framework].append(result)

        # Analyze each framework
        for framework, results in framework_results.items():
            analysis["framework_analysis"][framework] = self._analyze_framework_tables(results)

        # Analyze each file
        for file_path in self.table_files:
            file_results = [r for r in self.results if r.file_path == file_path]
            analysis["file_analysis"][file_path] = self._analyze_file_tables(file_results)

        # Generate summary
        analysis["summary"] = self._generate_table_summary(analysis["framework_analysis"])

        return analysis

    def _analyze_framework_tables(self, results: list[BenchmarkResult]) -> dict[str, Any]:
        """Analyze table extraction for a specific framework."""
        total_files = len(results)
        successful_extractions = [r for r in results if r.status == ExtractionStatus.SUCCESS and r.extracted_text]

        analysis = {
            "total_table_files_attempted": total_files,
            "successful_extractions": len(successful_extractions),
            "success_rate": len(successful_extractions) / total_files if total_files > 0 else 0,
            "table_structure_scores": [],
            "table_detection_scores": [],
            "avg_extraction_time": 0,
            "format_support": {},
        }

        # Analyze successful extractions
        extraction_times = []
        for result in successful_extractions:
            if result.extraction_time:
                extraction_times.append(result.extraction_time)

            # Analyze table structure preservation
            if result.extracted_text:
                structure_score = self._analyze_table_structure(result.extracted_text, result.file_path)
                analysis["table_structure_scores"].append(structure_score)

                detection_score = self._analyze_table_detection(result.extracted_text, result.file_path)
                analysis["table_detection_scores"].append(detection_score)

            # Track format support
            file_ext = Path(result.file_path).suffix.lower()
            if file_ext not in analysis["format_support"]:
                analysis["format_support"][file_ext] = {"attempted": 0, "successful": 0}
            analysis["format_support"][file_ext]["attempted"] += 1
            if result.status == ExtractionStatus.SUCCESS:
                analysis["format_support"][file_ext]["successful"] += 1

        if extraction_times:
            analysis["avg_extraction_time"] = sum(extraction_times) / len(extraction_times)

        if analysis["table_structure_scores"]:
            analysis["avg_structure_score"] = sum(analysis["table_structure_scores"]) / len(
                analysis["table_structure_scores"]
            )
        else:
            analysis["avg_structure_score"] = 0

        if analysis["table_detection_scores"]:
            analysis["avg_detection_score"] = sum(analysis["table_detection_scores"]) / len(
                analysis["table_detection_scores"]
            )
        else:
            analysis["avg_detection_score"] = 0

        return analysis

    def _analyze_file_tables(self, results: list[BenchmarkResult]) -> dict[str, Any]:
        """Analyze table extraction for a specific file across frameworks."""
        analysis = {
            "file_path": results[0].file_path if results else "",
            "file_type": Path(results[0].file_path).suffix.lower() if results else "",
            "framework_results": {},
            "best_extraction": None,
            "table_complexity": "unknown",
        }

        best_score = -1
        for result in results:
            framework = result.framework.value

            framework_analysis = {
                "status": result.status.value,
                "extraction_time": result.extraction_time,
                "character_count": result.character_count,
                "table_structure_score": 0,
                "table_detection_score": 0,
            }

            if result.status == ExtractionStatus.SUCCESS and result.extracted_text:
                structure_score = self._analyze_table_structure(result.extracted_text, result.file_path)
                detection_score = self._analyze_table_detection(result.extracted_text, result.file_path)

                framework_analysis["table_structure_score"] = structure_score
                framework_analysis["table_detection_score"] = detection_score

                # Combined score for ranking
                combined_score = (structure_score + detection_score) / 2
                if combined_score > best_score:
                    best_score = combined_score
                    analysis["best_extraction"] = framework

            analysis["framework_results"][framework] = framework_analysis

        # Determine table complexity
        analysis["table_complexity"] = self._determine_table_complexity(results[0].file_path)

        return analysis

    def _analyze_table_structure(self, extracted_text: str, file_path: str) -> float:
        """Analyze how well table structure is preserved in extracted text."""
        if not extracted_text:
            return 0.0

        score = 0.0
        file_ext = Path(file_path).suffix.lower()

        # Check for different table representations
        structure_indicators = {
            "markdown_tables": r"\|.*\|.*\|",  # Markdown table format
            "html_tables": r"<table.*?>.*?</table>",  # HTML table tags
            "csv_format": r".*,.*,.*",  # CSV-like comma separation
            "tab_separated": r".*\t.*\t.*",  # Tab-separated values
            "aligned_columns": r"  +\w+  +\w+",  # Space-aligned columns
            "table_headers": r"(Name|Product|Item|Price|Total|Amount|Quantity)",  # Common table headers
            "numeric_data": r"\$?\d+\.?\d*",  # Numeric data (prices, quantities)
        }

        text_lower = extracted_text.lower()

        for indicator_name, pattern in structure_indicators.items():
            if re.search(pattern, extracted_text, re.IGNORECASE | re.MULTILINE):
                if indicator_name in {"markdown_tables", "html_tables"}:
                    score += 0.25
                elif indicator_name in {"csv_format", "tab_separated"}:
                    score += 0.20
                elif indicator_name == "aligned_columns":
                    score += 0.15
                elif indicator_name == "table_headers":
                    score += 0.10
                elif indicator_name == "numeric_data":
                    score += 0.05

        # File-specific scoring adjustments
        if file_ext == ".csv":
            # CSV files should preserve comma structure
            if "," in extracted_text:
                score += 0.3
        elif file_ext in [".xlsx", ".xls"]:
            # Excel files should preserve tabular data
            if "\t" in extracted_text or "," in extracted_text:
                score += 0.2
        elif file_ext == ".html" and ("<table>" in text_lower or "|" in extracted_text):
            # HTML should preserve table structure
            score += 0.2

        return min(1.0, score)

    def _analyze_table_detection(self, extracted_text: str, file_path: str) -> float:
        """Analyze how well tables are detected and extracted."""
        if not extracted_text:
            return 0.0

        score = 0.0
        file_name = Path(file_path).name.lower()

        # Expected content based on known test files
        expected_content = {}

        if "stanley-cups" in file_name:
            expected_content = {
                "teams": ["blues", "flyers", "maple leafs"],
                "locations": ["stl", "phi", "tor"],
                "numbers": ["1", "2", "13"],
            }
        elif "simple-table" in file_name:
            expected_content = {
                "items": ["juicy apples", "bananas", "laptop", "desk chair"],
                "prices": ["1.99", "1.89", "999.99", "199.99"],
                "categories": ["electronics", "furniture", "kitchen"],
            }
        elif "complex-table" in file_name:
            expected_content = {
                "regions": ["usa", "canada", "uk", "germany", "france"],
                "quarters": ["q1", "q2", "q3", "q4"],
                "totals": ["695", "205", "373", "295"],
            }

        # Check for expected content
        text_lower = extracted_text.lower()
        for items in expected_content.values():
            found_items = sum(1 for item in items if item in text_lower)
            if items:
                category_score = found_items / len(items)
                score += category_score * 0.3

        # Check for general table indicators
        table_indicators = [
            ("column_headers", r"(product|name|price|total|amount|category|region|quarter)"),
            ("structured_data", r"\d+\.\d+|\$\d+|[A-Z]{2,3}"),  # Prices, currencies, codes
            ("table_separators", r"[\|,\t]"),  # Common separators
            ("row_structure", r"\n.*\n.*\n"),  # Multi-row structure
        ]

        for _indicator_name, pattern in table_indicators:
            matches = len(re.findall(pattern, extracted_text, re.IGNORECASE))
            if matches > 0:
                score += min(0.2, matches * 0.05)

        return min(1.0, score)

    def _determine_table_complexity(self, file_path: str) -> str:
        """Determine the complexity level of tables in the file."""
        file_name = Path(file_path).name.lower()

        if "simple" in file_name:
            return "simple"
        if "complex" in file_name or "embedded" in file_name:
            return "complex"
        if file_name.endswith((".xlsx", ".xls")):
            return "spreadsheet"
        if file_name.endswith(".csv"):
            return "simple"
        if file_name.endswith(".html"):
            return "moderate"
        return "moderate"

    def _generate_table_summary(self, framework_analysis: dict[str, Any]) -> dict[str, Any]:
        """Generate summary statistics for table extraction."""
        if not framework_analysis:
            return {}

        summary = {
            "best_framework_structure": None,
            "best_framework_detection": None,
            "best_framework_speed": None,
            "framework_rankings": {},
            "format_support_matrix": {},
        }

        # Find best frameworks for different metrics
        best_structure_score = -1
        best_detection_score = -1
        best_speed = float("inf")

        for framework, analysis in framework_analysis.items():
            structure_score = analysis.get("avg_structure_score", 0)
            detection_score = analysis.get("avg_detection_score", 0)
            speed = analysis.get("avg_extraction_time", float("inf"))

            if structure_score > best_structure_score:
                best_structure_score = structure_score
                summary["best_framework_structure"] = framework

            if detection_score > best_detection_score:
                best_detection_score = detection_score
                summary["best_framework_detection"] = framework

            if speed < best_speed and speed > 0:
                best_speed = speed
                summary["best_framework_speed"] = framework

            # Create ranking score (structure + detection + speed factor)
            speed_factor = 1.0 / speed if speed > 0 else 0
            ranking_score = (structure_score + detection_score) / 2 + speed_factor * 0.1
            summary["framework_rankings"][framework] = {
                "structure_score": structure_score,
                "detection_score": detection_score,
                "speed": speed,
                "ranking_score": ranking_score,
            }

        # Create format support matrix
        for framework, analysis in framework_analysis.items():
            for format_ext, support_data in analysis.get("format_support", {}).items():
                if format_ext not in summary["format_support_matrix"]:
                    summary["format_support_matrix"][format_ext] = {}

                success_rate = (
                    support_data["successful"] / support_data["attempted"] if support_data["attempted"] > 0 else 0
                )
                summary["format_support_matrix"][format_ext][framework] = {
                    "success_rate": success_rate,
                    "attempted": support_data["attempted"],
                    "successful": support_data["successful"],
                }

        return summary

    def generate_table_analysis_report(self, output_dir: Path) -> None:
        """Generate a comprehensive table analysis report."""
        output_dir.mkdir(parents=True, exist_ok=True)

        analysis = self.analyze_table_extraction_quality()

        # Save detailed JSON analysis
        json_file = output_dir / "table_extraction_analysis.json"
        with open(json_file, "w") as f:
            import json

            json.dump(analysis, f, indent=2, default=str)

        # Generate markdown report
        self._generate_markdown_report(analysis, output_dir / "table_extraction_report.md")

        # Generate CSV summary
        self._generate_csv_summary(analysis, output_dir / "table_extraction_summary.csv")

        print(f"Table analysis reports generated in {output_dir}/")

    def _generate_markdown_report(self, analysis: dict[str, Any], output_file: Path) -> None:
        """Generate a markdown report for table extraction analysis."""
        md_content = []
        md_content.append("# Table Extraction Analysis Report\n")

        # Summary section
        summary = analysis.get("summary", {})
        md_content.append("## Executive Summary\n")
        md_content.append(f"- **Total table files analyzed**: {analysis['total_table_files']}")
        md_content.append(
            f"- **Best framework for structure preservation**: {summary.get('best_framework_structure', 'N/A')}"
        )
        md_content.append(f"- **Best framework for table detection**: {summary.get('best_framework_detection', 'N/A')}")
        md_content.append(f"- **Fastest framework**: {summary.get('best_framework_speed', 'N/A')}\n")

        # Framework rankings
        rankings = summary.get("framework_rankings", {})
        if rankings:
            md_content.append("## Framework Rankings\n")
            md_content.append("| Framework | Structure Score | Detection Score | Avg Speed (s) | Overall Ranking |")
            md_content.append("|-----------|----------------|-----------------|---------------|-----------------|")

            sorted_frameworks = sorted(rankings.items(), key=lambda x: x[1]["ranking_score"], reverse=True)

            for framework, scores in sorted_frameworks:
                structure = f"{scores['structure_score']:.3f}"
                detection = f"{scores['detection_score']:.3f}"
                speed = f"{scores['speed']:.2f}" if scores["speed"] != float("inf") else "N/A"
                ranking = f"{scores['ranking_score']:.3f}"
                md_content.append(f"| {framework} | {structure} | {detection} | {speed} | {ranking} |")
            md_content.append("")

        # Format support matrix
        format_matrix = summary.get("format_support_matrix", {})
        if format_matrix:
            md_content.append("## Format Support Matrix\n")

            frameworks = set()
            for format_data in format_matrix.values():
                frameworks.update(format_data.keys())
            frameworks = sorted(frameworks)

            header = "| Format |" + "".join(f" {fw} |" for fw in frameworks)
            separator = "|--------|" + "".join("------|" for _ in frameworks)
            md_content.append(header)
            md_content.append(separator)

            for file_format, framework_data in sorted(format_matrix.items()):
                row = f"| {file_format} |"
                for framework in frameworks:
                    if framework in framework_data:
                        success_rate = framework_data[framework]["success_rate"]
                        row += f" {success_rate:.1%} |"
                    else:
                        row += " N/A |"
                md_content.append(row)
            md_content.append("")

        # File-specific analysis
        md_content.append("## File-Specific Analysis\n")
        for file_path, file_analysis in analysis.get("file_analysis", {}).items():
            file_name = Path(file_path).name
            md_content.append(f"### {file_name}")
            md_content.append(f"- **File type**: {file_analysis['file_type']}")
            md_content.append(f"- **Table complexity**: {file_analysis['table_complexity']}")
            md_content.append(f"- **Best extraction**: {file_analysis.get('best_extraction', 'N/A')}\n")

        # Write the report
        with open(output_file, "w") as f:
            f.write("\n".join(md_content))

    def _generate_csv_summary(self, analysis: dict[str, Any], output_file: Path) -> None:
        """Generate a CSV summary of table extraction performance."""
        rows = []

        for framework, framework_analysis in analysis.get("framework_analysis", {}).items():
            row = {
                "Framework": framework,
                "Success_Rate": framework_analysis.get("success_rate", 0),
                "Avg_Structure_Score": framework_analysis.get("avg_structure_score", 0),
                "Avg_Detection_Score": framework_analysis.get("avg_detection_score", 0),
                "Avg_Extraction_Time": framework_analysis.get("avg_extraction_time", 0),
                "Total_Files_Attempted": framework_analysis.get("total_table_files_attempted", 0),
                "Successful_Extractions": framework_analysis.get("successful_extractions", 0),
            }

            # Add format-specific success rates
            for format_ext, support_data in framework_analysis.get("format_support", {}).items():
                format_key = f"Success_Rate_{format_ext.replace('.', '').upper()}"
                success_rate = (
                    support_data["successful"] / support_data["attempted"] if support_data["attempted"] > 0 else 0
                )
                row[format_key] = success_rate

            rows.append(row)

        if rows:
            df = pd.DataFrame(rows)
            df.to_csv(output_file, index=False)


def analyze_table_extraction_from_results(results_file: Path, output_dir: Path) -> None:
    """Analyze table extraction from benchmark results file."""
    # Load results
    with open(results_file, "rb") as f:
        results = msgspec.json.decode(f.read(), type=list[BenchmarkResult])

    # Run table analysis
    analyzer = TableExtractionAnalyzer(results)
    analyzer.generate_table_analysis_report(output_dir)
