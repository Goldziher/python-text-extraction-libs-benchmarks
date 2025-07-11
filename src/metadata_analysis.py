"""Metadata analysis system for benchmarking results."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

import msgspec
import pandas as pd
from rich.console import Console
from rich.table import Table

from src.types import BenchmarkResult, Framework


class MetadataFieldAnalyzer:
    """Analyzes metadata fields extracted by each framework."""
    
    def __init__(self, results: list[BenchmarkResult]) -> None:
        self.results = results
        self.console = Console()
        
    def analyze_metadata_coverage(self) -> dict[str, dict[str, Any]]:
        """Analyze metadata coverage by framework."""
        coverage = defaultdict(lambda: {
            'total_extractions': 0,
            'successful_with_metadata': 0,
            'fields_found': defaultdict(int),
            'unique_fields': set(),
            'avg_fields_per_doc': 0,
            'file_type_coverage': defaultdict(lambda: defaultdict(int))
        })
        
        for result in self.results:
            framework = result.framework.value
            coverage[framework]['total_extractions'] += 1
            
            if result.extracted_metadata:
                coverage[framework]['successful_with_metadata'] += 1
                
                # Count fields
                for field, value in result.extracted_metadata.items():
                    if value is not None and value != '':
                        coverage[framework]['fields_found'][field] += 1
                        coverage[framework]['unique_fields'].add(field)
                        coverage[framework]['file_type_coverage'][result.file_type.value][field] += 1
        
        # Calculate averages
        for framework, data in coverage.items():
            if data['successful_with_metadata'] > 0:
                total_fields = sum(data['fields_found'].values())
                data['avg_fields_per_doc'] = total_fields / data['successful_with_metadata']
            
            # Convert sets to lists for JSON serialization
            data['unique_fields'] = sorted(list(data['unique_fields']))
            
        return dict(coverage)
    
    def compare_metadata_fields(self) -> pd.DataFrame:
        """Create comparison matrix of metadata fields across frameworks."""
        # Collect all unique fields across all frameworks
        all_fields = set()
        framework_fields = defaultdict(dict)
        
        for result in self.results:
            if result.extracted_metadata:
                framework = result.framework.value
                for field, value in result.extracted_metadata.items():
                    if value is not None and value != '':
                        all_fields.add(field)
                        framework_fields[framework][field] = framework_fields[framework].get(field, 0) + 1
        
        # Create comparison matrix
        frameworks = sorted(framework_fields.keys())
        fields = sorted(all_fields)
        
        data = []
        for field in fields:
            row = {'field': field}
            for framework in frameworks:
                count = framework_fields[framework].get(field, 0)
                row[framework] = count
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Add totals
        for framework in frameworks:
            df[f'{framework}_pct'] = (df[framework] / df[framework].sum() * 100).round(1)
        
        return df
    
    def analyze_metadata_quality(self) -> dict[str, dict[str, Any]]:
        """Analyze quality and completeness of metadata by framework."""
        quality_metrics = defaultdict(lambda: {
            'completeness_scores': [],
            'avg_completeness': 0,
            'common_fields_coverage': {},
            'unique_value_examples': defaultdict(set)
        })
        
        # Define common/important metadata fields
        common_fields = [
            'title', 'author', 'authors', 'created', 'created_at', 'creation_date',
            'modified', 'modified_at', 'modification_date', 'language', 'languages',
            'page_count', 'word_count', 'mime_type', 'file_type', 'filetype'
        ]
        
        for result in self.results:
            if not result.extracted_metadata:
                continue
                
            framework = result.framework.value
            
            # Calculate completeness score
            fields_present = sum(1 for field in common_fields 
                               if result.extracted_metadata.get(field) is not None)
            completeness = fields_present / len(common_fields)
            quality_metrics[framework]['completeness_scores'].append(completeness)
            
            # Track coverage of common fields
            for field in common_fields:
                if field in result.extracted_metadata and result.extracted_metadata[field] is not None:
                    if field not in quality_metrics[framework]['common_fields_coverage']:
                        quality_metrics[framework]['common_fields_coverage'][field] = 0
                    quality_metrics[framework]['common_fields_coverage'][field] += 1
            
            # Collect unique value examples
            for field, value in result.extracted_metadata.items():
                if value and isinstance(value, (str, int, float)):
                    quality_metrics[framework]['unique_value_examples'][field].add(str(value)[:100])
        
        # Calculate averages and clean up
        for framework, metrics in quality_metrics.items():
            if metrics['completeness_scores']:
                metrics['avg_completeness'] = sum(metrics['completeness_scores']) / len(metrics['completeness_scores'])
            
            # Convert sets to lists, limit examples
            for field, examples in metrics['unique_value_examples'].items():
                metrics['unique_value_examples'][field] = sorted(list(examples))[:5]
        
        return dict(quality_metrics)
    
    def generate_metadata_report(self, output_dir: Path) -> None:
        """Generate comprehensive metadata analysis report."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Analyze coverage
        coverage = self.analyze_metadata_coverage()
        
        # Save detailed coverage analysis
        with open(output_dir / 'metadata_coverage.json', 'w') as f:
            json.dump(coverage, f, indent=2)
        
        # Generate comparison matrix
        comparison_df = self.compare_metadata_fields()
        comparison_df.to_csv(output_dir / 'metadata_field_comparison.csv', index=False)
        
        # Analyze quality
        quality = self.analyze_metadata_quality()
        with open(output_dir / 'metadata_quality.json', 'w') as f:
            json.dump(quality, f, indent=2, default=str)
        
        # Generate summary report
        self._generate_summary_report(coverage, quality, output_dir)
        
        # Display summary to console
        self._display_metadata_summary(coverage)
    
    def _generate_summary_report(self, coverage: dict, quality: dict, output_dir: Path) -> None:
        """Generate markdown summary report."""
        lines = [
            "# Metadata Extraction Analysis",
            "",
            "## Framework Coverage Summary",
            "",
            "| Framework | Total Files | With Metadata | Coverage % | Avg Fields | Unique Fields |",
            "|-----------|------------|---------------|------------|------------|---------------|"
        ]
        
        for framework, data in sorted(coverage.items()):
            total = data['total_extractions']
            with_meta = data['successful_with_metadata']
            coverage_pct = (with_meta / total * 100) if total > 0 else 0
            avg_fields = data['avg_fields_per_doc']
            unique_count = len(data['unique_fields'])
            
            lines.append(
                f"| {framework} | {total} | {with_meta} | "
                f"{coverage_pct:.1f}% | {avg_fields:.1f} | {unique_count} |"
            )
        
        lines.extend([
            "",
            "## Metadata Quality Scores",
            "",
            "| Framework | Avg Completeness | Common Fields Coverage |",
            "|-----------|-----------------|----------------------|"
        ])
        
        for framework, metrics in sorted(quality.items()):
            avg_complete = metrics.get('avg_completeness', 0) * 100
            common_fields = len(metrics.get('common_fields_coverage', {}))
            
            lines.append(f"| {framework} | {avg_complete:.1f}% | {common_fields} fields |")
        
        # Add unique fields per framework
        lines.extend([
            "",
            "## Unique Fields by Framework",
            ""
        ])
        
        for framework, data in sorted(coverage.items()):
            if data['unique_fields']:
                lines.append(f"### {framework}")
                lines.append(f"Fields: {', '.join(data['unique_fields'][:20])}")
                if len(data['unique_fields']) > 20:
                    lines.append(f"... and {len(data['unique_fields']) - 20} more")
                lines.append("")
        
        with open(output_dir / 'metadata_analysis_summary.md', 'w') as f:
            f.write('\n'.join(lines))
    
    def _display_metadata_summary(self, coverage: dict) -> None:
        """Display metadata summary to console."""
        table = Table(title="Metadata Extraction Coverage by Framework")
        
        table.add_column("Framework", style="cyan")
        table.add_column("Total Files", style="green")
        table.add_column("With Metadata", style="yellow")
        table.add_column("Coverage %", style="blue")
        table.add_column("Avg Fields", style="magenta")
        table.add_column("Unique Fields", style="red")
        
        for framework, data in sorted(coverage.items()):
            total = data['total_extractions']
            with_meta = data['successful_with_metadata']
            coverage_pct = (with_meta / total * 100) if total > 0 else 0
            avg_fields = data['avg_fields_per_doc']
            unique_count = len(data['unique_fields'])
            
            table.add_row(
                framework,
                str(total),
                str(with_meta),
                f"{coverage_pct:.1f}%",
                f"{avg_fields:.1f}",
                str(unique_count)
            )
        
        self.console.print(table)


def analyze_metadata_from_results(results_file: Path, output_dir: Path) -> None:
    """Analyze metadata from benchmark results file."""
    # Load results
    with open(results_file, 'rb') as f:
        results_data = msgspec.json.decode(f.read())
    
    # Convert to BenchmarkResult objects
    results = [BenchmarkResult(**r) for r in results_data]
    
    # Filter out Kreuzberg results for now
    results = [r for r in results if 'kreuzberg' not in r.framework.value.lower()]
    
    # Run analysis
    analyzer = MetadataFieldAnalyzer(results)
    analyzer.generate_metadata_report(output_dir)
    
    print(f"\nMetadata analysis complete. Reports saved to {output_dir}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        results_file = Path(sys.argv[1])
        output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("metadata_analysis")
        analyze_metadata_from_results(results_file, output_dir)
    else:
        print("Usage: python metadata_analysis.py <results.json> [output_dir]")