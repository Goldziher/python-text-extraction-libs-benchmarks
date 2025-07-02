"""Performance profiling utilities for benchmarking."""

from __future__ import annotations

import asyncio
import gc
import sys
import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

if sys.version_info >= (3, 13):
    pass
else:
    pass

import psutil


class PerformanceMetrics:
    """Container for performance metrics."""

    def __init__(self) -> None:
        """Initialize metrics container."""
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self.start_memory: float = 0.0
        self.peak_memory: float = 0.0
        self.start_cpu: float = 0.0
        self.total_cpu: float = 0.0
        self.cpu_samples: list[float] = []

    @property
    def duration_seconds(self) -> float:
        """Get the total duration in seconds."""
        return self.end_time - self.start_time

    @property
    def memory_peak_mb(self) -> float:
        """Get the peak memory usage in MB."""
        return self.peak_memory

    @property
    def average_cpu_percent(self) -> float:
        """Get the average CPU usage percentage."""
        return sum(self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0.0


@contextmanager
def profile_performance() -> Generator[PerformanceMetrics]:
    """Context manager for profiling performance metrics.

    Yields:
        PerformanceMetrics: Object containing performance data.
    """
    metrics = PerformanceMetrics()
    process = psutil.Process()

    # Force garbage collection before starting
    gc.collect()

    # Record starting metrics
    metrics.start_time = time.perf_counter()
    metrics.start_memory = process.memory_info().rss / 1024 / 1024  # MB
    metrics.peak_memory = metrics.start_memory

    # Start CPU monitoring
    process.cpu_percent()  # First call to initialize

    try:
        yield metrics
    finally:
        # Record ending metrics
        metrics.end_time = time.perf_counter()
        final_cpu = process.cpu_percent()
        if final_cpu > 0:
            metrics.cpu_samples.append(final_cpu)

        # Get final memory
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        metrics.peak_memory = max(metrics.peak_memory, final_memory)


async def profile_performance_async() -> AsyncPerformanceProfiler:
    """Async context manager for profiling performance metrics.

    Returns:
        AsyncPerformanceProfiler: Async profiler instance.
    """
    return AsyncPerformanceProfiler()


class AsyncPerformanceProfiler:
    """Async performance profiler."""

    def __init__(self) -> None:
        """Initialize async profiler."""
        self.metrics = PerformanceMetrics()
        self.process = psutil.Process()
        self._monitoring_task: asyncio.Task[None] | None = None

    async def __aenter__(self) -> PerformanceMetrics:
        """Start async profiling."""
        # Force garbage collection before starting
        gc.collect()

        # Record starting metrics
        self.metrics.start_time = time.perf_counter()
        self.metrics.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.metrics.peak_memory = self.metrics.start_memory

        # Start CPU monitoring
        self.process.cpu_percent()  # First call to initialize

        # Start background monitoring
        self._monitoring_task = asyncio.create_task(self._monitor_resources())

        return self.metrics

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Stop async profiling."""
        # Stop monitoring
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

        # Record ending metrics
        self.metrics.end_time = time.perf_counter()
        final_cpu = self.process.cpu_percent()
        if final_cpu > 0:
            self.metrics.cpu_samples.append(final_cpu)

        # Get final memory
        final_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.metrics.peak_memory = max(self.metrics.peak_memory, final_memory)

    async def _monitor_resources(self) -> None:
        """Monitor CPU and memory usage in the background."""
        try:
            while True:
                await asyncio.sleep(0.1)  # Sample every 100ms

                # Monitor CPU
                cpu_percent = self.process.cpu_percent()
                if cpu_percent > 0:
                    self.metrics.cpu_samples.append(cpu_percent)

                # Monitor memory
                current_memory = self.process.memory_info().rss / 1024 / 1024  # MB
                self.metrics.peak_memory = max(self.metrics.peak_memory, current_memory)

        except asyncio.CancelledError:
            # Task was cancelled, this is expected
            pass
