"""Interactive HTML dashboard generator for file type analysis."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .file_type_analysis import FileTypeAnalyzer


class InteractiveDashboardGenerator:
    """Generate interactive HTML dashboard with Plotly charts."""

    def __init__(self, analyzer: FileTypeAnalyzer) -> None:
        """Initialize with file type analyzer."""
        self.analyzer = analyzer
        self.file_type_stats = analyzer.file_type_stats

    def generate_dashboard(self, output_dir: Path) -> None:
        """Generate complete interactive dashboard."""
        # Prepare data
        summary_data = self._prepare_summary_data()

        # Generate HTML
        html_content = self._generate_html_template()

        # Write dashboard
        dashboard_path = output_dir / "interactive_dashboard.html"
        with open(dashboard_path, "w") as f:
            f.write(html_content.format(data_json=json.dumps(summary_data, indent=2)))

        print(f"Generated interactive dashboard: {dashboard_path}")

    def _prepare_summary_data(self) -> dict[str, Any]:
        """Prepare data for JavaScript consumption."""
        summary_data = []

        for file_type, frameworks in self.file_type_stats.items():
            for framework, stats in frameworks.items():
                summary_data.append(
                    {
                        "file_type": file_type,
                        "framework": framework,
                        "total_files": stats["total_files"],
                        "success_rate": stats["success_rate"],
                        "avg_extraction_time": stats["avg_extraction_time"],
                        "avg_memory_mb": stats["avg_memory_mb"],
                        "files_per_second": stats["files_per_second"],
                        "avg_chars_per_file": stats["avg_chars_per_file"],
                        "avg_words_per_file": stats["avg_words_per_file"],
                        "successful_files": stats["successful_files"],
                        "failed_files": stats["failed_files"],
                    }
                )

        # Organize data by chart type
        return {
            "summary": summary_data,
            "file_types": list(self.file_type_stats.keys()),
            "frameworks": list({fw for fw_dict in self.file_type_stats.values() for fw in fw_dict}),
            "metrics": {
                "success_rate": "Success Rate (%)",
                "files_per_second": "Speed (files/sec)",
                "avg_memory_mb": "Memory Usage (MB)",
                "avg_extraction_time": "Extraction Time (seconds)",
            },
        }

    def _generate_html_template(self) -> str:
        """Generate the complete HTML template with embedded JavaScript."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Type Performance Analysis - Interactive Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f7fa;
            color: #333;
        }}

        .header {{
            text-align: center;
            margin-bottom: 30px;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .controls {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            display: flex;
            gap: 20px;
            align-items: center;
            flex-wrap: wrap;
        }}

        .control-group {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}

        .control-group label {{
            font-weight: 600;
            color: #555;
            font-size: 14px;
        }}

        .control-group select {{
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background: white;
        }}

        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}

        .chart-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }}

        .chart-title {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #333;
        }}

        .summary-stats {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .stat-card {{
            background: rgba(255, 255, 255, 0.15);
            padding: 15px;
            border-radius: 6px;
            text-align: center;
        }}

        .stat-value {{
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 5px;
        }}

        .stat-label {{
            font-size: 14px;
            opacity: 0.9;
        }}

        @media (max-width: 768px) {{
            .chart-grid {{
                grid-template-columns: 1fr;
            }}

            .controls {{
                flex-direction: column;
                align-items: stretch;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 File Type Performance Analysis</h1>
        <p>Interactive dashboard for text extraction framework comparison by file type</p>
    </div>

    <div class="summary-stats">
        <h2>📈 Summary Statistics</h2>
        <div class="stats-grid" id="summaryStats">
            <!-- Will be populated by JavaScript -->
        </div>
    </div>

    <div class="controls">
        <div class="control-group">
            <label for="metricSelect">Primary Metric</label>
            <select id="metricSelect">
                <option value="success_rate">Success Rate (%)</option>
                <option value="files_per_second">Speed (files/sec)</option>
                <option value="avg_memory_mb">Memory Usage (MB)</option>
                <option value="avg_extraction_time">Extraction Time (sec)</option>
            </select>
        </div>

        <div class="control-group">
            <label for="frameworkFilter">Framework Filter</label>
            <select id="frameworkFilter">
                <option value="all">All Frameworks</option>
            </select>
        </div>

        <div class="control-group">
            <label for="fileTypeFilter">File Type Filter</label>
            <select id="fileTypeFilter">
                <option value="all">All File Types</option>
            </select>
        </div>

        <div class="control-group">
            <label for="minSuccessRate">Min Success Rate (%)</label>
            <select id="minSuccessRate">
                <option value="0">0%</option>
                <option value="50">50%</option>
                <option value="75" selected>75%</option>
                <option value="90">90%</option>
                <option value="95">95%</option>
            </select>
        </div>
    </div>

    <div class="chart-grid">
        <div class="chart-container">
            <div class="chart-title">Performance Heatmap</div>
            <div id="heatmapChart" style="height: 500px;"></div>
        </div>

        <div class="chart-container">
            <div class="chart-title">Framework Comparison</div>
            <div id="barChart" style="height: 500px;"></div>
        </div>
    </div>

    <div class="chart-grid">
        <div class="chart-container">
            <div class="chart-title">Speed vs Success Rate</div>
            <div id="scatterChart" style="height: 500px;"></div>
        </div>

        <div class="chart-container">
            <div class="chart-title">Memory Efficiency</div>
            <div id="memoryChart" style="height: 500px;"></div>
        </div>
    </div>

    <div class="chart-container">
        <div class="chart-title">Detailed File Type Analysis</div>
        <div id="detailedChart" style="height: 600px;"></div>
    </div>

    <script>
        // Data from Python
        const data = {data_json};

        // Global state
        let currentMetric = 'success_rate';
        let frameworkFilter = 'all';
        let fileTypeFilter = 'all';
        let minSuccessRate = 75;

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {{
            initializeControls();
            updateSummaryStats();
            updateAllCharts();
            setupEventListeners();
        }});

        function initializeControls() {{
            // Populate framework filter
            const frameworkSelect = document.getElementById('frameworkFilter');
            data.frameworks.forEach(fw => {{
                const option = document.createElement('option');
                option.value = fw;
                option.textContent = fw.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
                frameworkSelect.appendChild(option);
            }});

            // Populate file type filter
            const fileTypeSelect = document.getElementById('fileTypeFilter');
            data.file_types.forEach(ft => {{
                const option = document.createElement('option');
                option.value = ft;
                option.textContent = ft.toUpperCase();
                fileTypeSelect.appendChild(option);
            }});
        }}

        function updateSummaryStats() {{
            const filtered = getFilteredData();
            const stats = calculateSummaryStats(filtered);

            const summaryDiv = document.getElementById('summaryStats');
            summaryDiv.innerHTML = `
                <div class="stat-card">
                    <div class="stat-value">${{stats.totalFiles}}</div>
                    <div class="stat-label">Total Files Tested</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${{stats.avgSuccessRate.toFixed(1)}}%</div>
                    <div class="stat-label">Average Success Rate</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${{stats.topSpeed.toFixed(1)}}</div>
                    <div class="stat-label">Top Speed (files/sec)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${{stats.avgMemory.toFixed(0)}} MB</div>
                    <div class="stat-label">Average Memory</div>
                </div>
            `;
        }}

        function calculateSummaryStats(data) {{
            const totalFiles = data.reduce((sum, d) => sum + d.total_files, 0);
            const avgSuccessRate = data.length > 0 ?
                data.reduce((sum, d) => sum + d.success_rate, 0) / data.length : 0;
            const topSpeed = Math.max(...data.map(d => d.files_per_second));
            const avgMemory = data.filter(d => d.avg_memory_mb > 0).length > 0 ?
                data.filter(d => d.avg_memory_mb > 0).reduce((sum, d) => sum + d.avg_memory_mb, 0) /
                data.filter(d => d.avg_memory_mb > 0).length : 0;

            return {{ totalFiles, avgSuccessRate, topSpeed, avgMemory }};
        }}

        function getFilteredData() {{
            return data.summary.filter(d => {{
                if (frameworkFilter !== 'all' && d.framework !== frameworkFilter) return false;
                if (fileTypeFilter !== 'all' && d.file_type !== fileTypeFilter) return false;
                if (d.success_rate < minSuccessRate) return false;
                return true;
            }});
        }}

        function createHeatmap() {{
            const filtered = getFilteredData();

            // Create pivot table
            const fileTypes = [...new Set(filtered.map(d => d.file_type))];
            const frameworks = [...new Set(filtered.map(d => d.framework))];

            const z = [];
            const hovertext = [];

            fileTypes.forEach(ft => {{
                const row = [];
                const hoverRow = [];
                frameworks.forEach(fw => {{
                    const item = filtered.find(d => d.file_type === ft && d.framework === fw);
                    const value = item ? item[currentMetric] : null;
                    row.push(value);
                    hoverRow.push(item ?
                        `${{ft}} - ${{fw}}<br>${{data.metrics[currentMetric]}}: ${{value?.toFixed(2) || 'N/A'}}` :
                        `${{ft}} - ${{fw}}<br>No data`
                    );
                }});
                z.push(row);
                hovertext.push(hoverRow);
            }});

            const trace = {{
                x: frameworks.map(fw => fw.replace(/_/g, ' ')),
                y: fileTypes.map(ft => ft.toUpperCase()),
                z: z,
                type: 'heatmap',
                colorscale: 'Viridis',
                hovertemplate: '%{{hovertext}}<extra></extra>',
                hovertext: hovertext
            }};

            const layout = {{
                margin: {{ t: 20, r: 20, b: 100, l: 100 }},
                xaxis: {{ title: 'Framework' }},
                yaxis: {{ title: 'File Type' }}
            }};

            Plotly.newPlot('heatmapChart', [trace], layout, {{responsive: true}});
        }}

        function createBarChart() {{
            const filtered = getFilteredData();

            // Group by framework
            const frameworks = [...new Set(filtered.map(d => d.framework))];
            const traces = frameworks.map(fw => {{
                const fwData = filtered.filter(d => d.framework === fw);
                return {{
                    x: fwData.map(d => d.file_type.toUpperCase()),
                    y: fwData.map(d => d[currentMetric]),
                    name: fw.replace(/_/g, ' '),
                    type: 'bar'
                }};
            }});

            const layout = {{
                margin: {{ t: 20, r: 20, b: 100, l: 60 }},
                xaxis: {{ title: 'File Type' }},
                yaxis: {{ title: data.metrics[currentMetric] }},
                barmode: 'group'
            }};

            Plotly.newPlot('barChart', traces, layout, {{responsive: true}});
        }}

        function createScatterChart() {{
            const filtered = getFilteredData().filter(d => d.files_per_second > 0);

            const frameworks = [...new Set(filtered.map(d => d.framework))];
            const traces = frameworks.map(fw => {{
                const fwData = filtered.filter(d => d.framework === fw);
                return {{
                    x: fwData.map(d => d.files_per_second),
                    y: fwData.map(d => d.success_rate),
                    text: fwData.map(d => d.file_type.toUpperCase()),
                    mode: 'markers+text',
                    textposition: 'top center',
                    name: fw.replace(/_/g, ' '),
                    type: 'scatter',
                    marker: {{ size: 10 }}
                }};
            }});

            const layout = {{
                margin: {{ t: 20, r: 20, b: 60, l: 60 }},
                xaxis: {{ title: 'Speed (files/sec)', type: 'log' }},
                yaxis: {{ title: 'Success Rate (%)' }}
            }};

            Plotly.newPlot('scatterChart', traces, layout, {{responsive: true}});
        }}

        function createMemoryChart() {{
            const filtered = getFilteredData().filter(d => d.avg_memory_mb > 0);

            const trace = {{
                x: filtered.map(d => d.avg_memory_mb),
                y: filtered.map(d => d.files_per_second),
                text: filtered.map(d => `${{d.file_type.toUpperCase()}}<br>${{d.framework.replace(/_/g, ' ')}}`),
                mode: 'markers+text',
                textposition: 'top center',
                type: 'scatter',
                marker: {{
                    size: filtered.map(d => Math.sqrt(d.total_files) * 3),
                    color: filtered.map(d => d.success_rate),
                    colorscale: 'Viridis',
                    colorbar: {{ title: 'Success Rate (%)' }}
                }}
            }};

            const layout = {{
                margin: {{ t: 20, r: 60, b: 60, l: 60 }},
                xaxis: {{ title: 'Memory Usage (MB)' }},
                yaxis: {{ title: 'Speed (files/sec)', type: 'log' }}
            }};

            Plotly.newPlot('memoryChart', [trace], layout, {{responsive: true}});
        }}

        function createDetailedChart() {{
            const filtered = getFilteredData();

            // Create grouped bar chart with multiple metrics
            const fileTypes = [...new Set(filtered.map(d => d.file_type))];

            const traces = [
                {{
                    x: fileTypes.map(ft => ft.toUpperCase()),
                    y: fileTypes.map(ft => {{
                        const ftData = filtered.filter(d => d.file_type === ft);
                        return ftData.length > 0 ? ftData.reduce((sum, d) => sum + d.success_rate, 0) / ftData.length : 0;
                    }}),
                    name: 'Success Rate (%)',
                    type: 'bar',
                    yaxis: 'y'
                }},
                {{
                    x: fileTypes.map(ft => ft.toUpperCase()),
                    y: fileTypes.map(ft => {{
                        const ftData = filtered.filter(d => d.file_type === ft && d.files_per_second > 0);
                        return ftData.length > 0 ? ftData.reduce((sum, d) => sum + d.files_per_second, 0) / ftData.length : 0;
                    }}),
                    name: 'Avg Speed (files/sec)',
                    type: 'bar',
                    yaxis: 'y2'
                }}
            ];

            const layout = {{
                margin: {{ t: 20, r: 60, b: 100, l: 60 }},
                xaxis: {{ title: 'File Type' }},
                yaxis: {{ title: 'Success Rate (%)', side: 'left' }},
                yaxis2: {{ title: 'Speed (files/sec)', side: 'right', overlaying: 'y' }},
                barmode: 'group'
            }};

            Plotly.newPlot('detailedChart', traces, layout, {{responsive: true}});
        }}

        function updateAllCharts() {{
            createHeatmap();
            createBarChart();
            createScatterChart();
            createMemoryChart();
            createDetailedChart();
        }}

        function setupEventListeners() {{
            document.getElementById('metricSelect').addEventListener('change', function(e) {{
                currentMetric = e.target.value;
                updateSummaryStats();
                updateAllCharts();
            }});

            document.getElementById('frameworkFilter').addEventListener('change', function(e) {{
                frameworkFilter = e.target.value;
                updateSummaryStats();
                updateAllCharts();
            }});

            document.getElementById('fileTypeFilter').addEventListener('change', function(e) {{
                fileTypeFilter = e.target.value;
                updateSummaryStats();
                updateAllCharts();
            }});

            document.getElementById('minSuccessRate').addEventListener('change', function(e) {{
                minSuccessRate = parseInt(e.target.value);
                updateSummaryStats();
                updateAllCharts();
            }});
        }}
    </script>
</body>
</html>"""
