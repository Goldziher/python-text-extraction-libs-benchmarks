#!/bin/bash
set -e  # Exit on error

echo "Running Kreuzberg Async benchmarks..."

# Run each category separately
uv run python -m src.cli benchmark --framework kreuzberg_async --category tiny --iterations 3 --timeout 14400
uv run python -m src.cli benchmark --framework kreuzberg_async --category small --iterations 3 --timeout 14400
uv run python -m src.cli benchmark --framework kreuzberg_async --category medium --iterations 3 --timeout 14400
uv run python -m src.cli benchmark --framework kreuzberg_async --category large --iterations 3 --timeout 14400
uv run python -m src.cli benchmark --framework kreuzberg_async --category huge --iterations 3 --timeout 14400

echo "All Kreuzberg Async benchmarks completed!"
