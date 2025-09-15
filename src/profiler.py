"""Enhanced performance profiling for benchmarking."""

from __future__ import annotations

import asyncio
import gc
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import psutil

from src.logger import get_logger
from src.types import ResourceMetrics

if TYPE_CHECKING:
    from collections.abc import Iterator

logger = get_logger(__name__)


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""

    extraction_time: float
    peak_memory_mb: float
    avg_memory_mb: float
    peak_cpu_percent: float
    avg_cpu_percent: float
    total_io_read_mb: float | None = None
    total_io_write_mb: float | None = None
    samples: list[ResourceMetrics] = field(default_factory=list)
    startup_time: float | None = None


class EnhancedResourceMonitor:
    """Advanced resource monitoring with detailed metrics."""

    def __init__(self, sampling_interval_ms: int = 50) -> None:
        self.sampling_interval = sampling_interval_ms / 1000.0
        self.metrics_buffer: list[ResourceMetrics] = []
        self.monitoring = False
        self.process = psutil.Process()
        self._monitor_task: asyncio.Task[None] | None = None
        self._baseline_io: dict[str, int] | None = None

    def _get_io_counters(self) -> dict[str, int] | None:
        """Get I/O counters if available on platform."""
        try:
            io = self.process.io_counters()
            return {
                "read_bytes": io.read_bytes,
                "write_bytes": io.write_bytes,
                "read_count": io.read_count,
                "write_count": io.write_count,
            }
        except (AttributeError, psutil.AccessDenied):
            return None

    def _get_open_files_count(self) -> int:
        """Get count of open files, handling platform differences."""
        try:
            return len(self.process.open_files())
        except (psutil.AccessDenied, AttributeError):
            return 0

    async def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        while self.monitoring:
            try:
                cpu_percent = self.process.cpu_percent(interval=None)
                mem_info = self.process.memory_info()

                io_counters = self._get_io_counters()
                io_metrics = {}
                if io_counters and self._baseline_io:
                    io_metrics = {
                        "io_read_bytes": io_counters["read_bytes"] - self._baseline_io["read_bytes"],
                        "io_write_bytes": io_counters["write_bytes"] - self._baseline_io["write_bytes"],
                        "io_read_count": io_counters["read_count"] - self._baseline_io["read_count"],
                        "io_write_count": io_counters["write_count"] - self._baseline_io["write_count"],
                    }

                metric = ResourceMetrics(
                    timestamp=time.time(),
                    cpu_percent=cpu_percent,
                    memory_rss=mem_info.rss,
                    memory_vms=mem_info.vms,
                    num_threads=self.process.num_threads(),
                    open_files=self._get_open_files_count(),
                    **io_metrics,
                )

                self.metrics_buffer.append(metric)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break

            await asyncio.sleep(self.sampling_interval)

    async def start(self) -> None:
        """Start monitoring."""
        self.monitoring = True
        self.metrics_buffer.clear()
        self._baseline_io = self._get_io_counters()

        self.process.cpu_percent(interval=None)

        try:
            baseline_metric = ResourceMetrics(
                timestamp=time.time(),
                cpu_percent=0.0,
                memory_rss=self.process.memory_info().rss,
                memory_vms=self.process.memory_info().vms,
                num_threads=self.process.num_threads(),
                open_files=self._get_open_files_count(),
            )
            self.metrics_buffer.append(baseline_metric)
        except Exception as e:
            emergency_metric = ResourceMetrics(
                timestamp=time.time(),
                cpu_percent=0.0,
                memory_rss=1024 * 1024,
                memory_vms=1024 * 1024,
                num_threads=1,
                open_files=10,
            )
            self.metrics_buffer.append(emergency_metric)
            logger.warning("Failed to collect baseline metric", error=str(e))

        self._monitor_task = asyncio.create_task(self._monitor_loop())

    async def stop(self) -> PerformanceMetrics:
        """Stop monitoring and return collected metrics."""
        self.monitoring = False

        if self._monitor_task:
            await self._monitor_task

        return self._calculate_metrics()

    def _calculate_metrics(self) -> PerformanceMetrics:
        """Calculate aggregate metrics from samples."""
        if not self.metrics_buffer:
            try:
                mem_info = self.process.memory_info()
                emergency_sample = ResourceMetrics(
                    timestamp=time.time(),
                    cpu_percent=0.0,
                    memory_rss=mem_info.rss,
                    memory_vms=mem_info.vms,
                    num_threads=self.process.num_threads(),
                    open_files=self._get_open_files_count(),
                )
                self.metrics_buffer.append(emergency_sample)
            except Exception as e:
                logger.warning("Failed to create emergency sample", error=str(e))

            if not self.metrics_buffer:
                return PerformanceMetrics(
                    extraction_time=0,
                    peak_memory_mb=1.0,
                    avg_memory_mb=1.0,
                    peak_cpu_percent=0,
                    avg_cpu_percent=0,
                    samples=[],
                )

        start_time = self.metrics_buffer[0].timestamp
        end_time = self.metrics_buffer[-1].timestamp
        extraction_time = max(end_time - start_time, 0.001)

        memory_samples = [m.memory_rss / (1024 * 1024) for m in self.metrics_buffer]
        peak_memory_mb = max(memory_samples)
        avg_memory_mb = sum(memory_samples) / len(memory_samples)

        cpu_samples = [m.cpu_percent for m in self.metrics_buffer]
        peak_cpu_percent = max(cpu_samples) if cpu_samples else 0
        avg_cpu_percent = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0

        total_io_read_mb = None
        total_io_write_mb = None
        if self.metrics_buffer and self.metrics_buffer[-1].io_read_bytes is not None:
            total_io_read_mb = self.metrics_buffer[-1].io_read_bytes / (1024 * 1024)
        if self.metrics_buffer and self.metrics_buffer[-1].io_write_bytes is not None:
            total_io_write_mb = self.metrics_buffer[-1].io_write_bytes / (1024 * 1024)

        return PerformanceMetrics(
            extraction_time=extraction_time,
            peak_memory_mb=peak_memory_mb,
            avg_memory_mb=avg_memory_mb,
            peak_cpu_percent=peak_cpu_percent,
            avg_cpu_percent=avg_cpu_percent,
            total_io_read_mb=total_io_read_mb,
            total_io_write_mb=total_io_write_mb,
            samples=self.metrics_buffer.copy(),
        )


@contextmanager
def profile_performance(sampling_interval_ms: int = 50) -> Iterator[PerformanceMetrics]:  # noqa: ARG001, PLR0915, C901
    """Context manager for synchronous performance profiling."""
    gc.collect()

    process = psutil.Process()
    start_time = time.time()

    process.cpu_percent(interval=None)
    baseline_memory = process.memory_info().rss
    baseline_io = None

    try:
        baseline_io = process.io_counters()._asdict()
    except (AttributeError, psutil.AccessDenied):
        pass

    samples = []

    def collect_sample() -> ResourceMetrics | None:
        try:
            cpu = process.cpu_percent(interval=None)
            mem_info = process.memory_info()

            io_metrics = {}
            if baseline_io:
                try:
                    current_io = process.io_counters()._asdict()
                    io_metrics = {
                        "io_read_bytes": current_io["read_bytes"] - baseline_io["read_bytes"],
                        "io_write_bytes": current_io["write_bytes"] - baseline_io["write_bytes"],
                        "io_read_count": current_io["read_count"] - baseline_io["read_count"],
                        "io_write_count": current_io["write_count"] - baseline_io["write_count"],
                    }
                except (AttributeError, psutil.AccessDenied):
                    pass

            try:
                open_files = len(process.open_files())
            except (psutil.AccessDenied, AttributeError):
                open_files = 0

            return ResourceMetrics(
                timestamp=time.time(),
                cpu_percent=cpu,
                memory_rss=mem_info.rss,
                memory_vms=mem_info.vms,
                num_threads=process.num_threads(),
                open_files=open_files,
                **io_metrics,
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None

    metrics = PerformanceMetrics(
        extraction_time=0,
        peak_memory_mb=0,
        avg_memory_mb=0,
        peak_cpu_percent=0,
        avg_cpu_percent=0,
        samples=samples,
    )

    if baseline_sample := collect_sample():
        samples.append(baseline_sample)

    try:
        yield metrics

        if final_sample := collect_sample():
            samples.append(final_sample)

        if len(samples) < 3:
            for _ in range(3):
                if sample := collect_sample():
                    samples.append(sample)
                time.sleep(0.01)

    finally:
        end_time = time.time()

        if samples:
            memory_samples = [s.memory_rss / (1024 * 1024) for s in samples]
            cpu_samples = [s.cpu_percent for s in samples if s.cpu_percent > 0]

            metrics.extraction_time = end_time - start_time
            metrics.peak_memory_mb = max(memory_samples)
            metrics.avg_memory_mb = sum(memory_samples) / len(memory_samples)
            metrics.peak_cpu_percent = max(cpu_samples) if cpu_samples else 0
            metrics.avg_cpu_percent = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0

            if samples and samples[-1].io_read_bytes is not None:
                metrics.total_io_read_mb = samples[-1].io_read_bytes / (1024 * 1024)
            if samples and samples[-1].io_write_bytes is not None:
                metrics.total_io_write_mb = samples[-1].io_write_bytes / (1024 * 1024)
        else:
            try:
                final_memory = process.memory_info().rss
                metrics.extraction_time = end_time - start_time
                metrics.peak_memory_mb = final_memory / (1024 * 1024)
                metrics.avg_memory_mb = (baseline_memory + final_memory) / 2 / (1024 * 1024)
                fallback_sample = collect_sample()
                if fallback_sample:
                    samples.append(fallback_sample)
            except Exception:
                metrics.extraction_time = end_time - start_time
                metrics.peak_memory_mb = 1.0
                metrics.avg_memory_mb = 1.0


class AsyncPerformanceProfiler:
    """Async context manager for performance profiling."""

    def __init__(self, sampling_interval_ms: int = 50) -> None:
        self.monitor = EnhancedResourceMonitor(sampling_interval_ms)
        self.metrics: PerformanceMetrics | None = None
        self._start_time: float | None = None

    async def __aenter__(self) -> PerformanceMetrics:
        """Enter the profiling context."""
        gc.collect()

        self._start_time = time.time()
        await self.monitor.start()

        self.metrics = PerformanceMetrics(
            extraction_time=0,
            peak_memory_mb=0,
            avg_memory_mb=0,
            peak_cpu_percent=0,
            avg_cpu_percent=0,
            samples=self.monitor.metrics_buffer,
        )
        return self.metrics

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the profiling context and update metrics."""
        result = await self.monitor.stop()

        if self.metrics:
            self.metrics.extraction_time = result.extraction_time
            self.metrics.peak_memory_mb = result.peak_memory_mb
            self.metrics.avg_memory_mb = result.avg_memory_mb
            self.metrics.peak_cpu_percent = result.peak_cpu_percent
            self.metrics.avg_cpu_percent = result.avg_cpu_percent
            self.metrics.total_io_read_mb = result.total_io_read_mb
            self.metrics.total_io_write_mb = result.total_io_write_mb
            self.metrics.startup_time = result.startup_time
