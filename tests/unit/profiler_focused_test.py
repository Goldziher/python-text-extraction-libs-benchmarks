"""Focused tests for profiler module error handling and edge cases."""

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from src.profiler import EnhancedResourceMonitor, PerformanceMetrics
from src.types import ResourceMetrics


class TestEnhancedResourceMonitorCore:
    """Core functionality tests for EnhancedResourceMonitor."""

    def setup_method(self):
        """Set up test environment."""
        self.monitor = EnhancedResourceMonitor(sampling_interval_ms=10)

    def teardown_method(self):
        """Clean up after tests."""
        if self.monitor._monitor_task:
            self.monitor._monitor_task.cancel()

    def test_monitor_initialization(self):
        """Test monitor initialization."""
        assert self.monitor.sampling_interval == 0.01  # 10ms converted to seconds
        assert self.monitor.metrics_buffer == []
        assert self.monitor.monitoring is False
        assert self.monitor._monitor_task is None

    @pytest.mark.asyncio
    async def test_basic_monitoring_cycle(self):
        """Test basic start/stop monitoring cycle."""
        await self.monitor.start()

        # Should be monitoring
        assert self.monitor.monitoring is True
        assert self.monitor._monitor_task is not None
        assert len(self.monitor.metrics_buffer) >= 1  # At least baseline

        # Brief monitoring period
        await asyncio.sleep(0.05)

        metrics = await self.monitor.stop()

        # Should have stopped
        assert self.monitor.monitoring is False
        assert isinstance(metrics, PerformanceMetrics)
        assert len(self.monitor.metrics_buffer) >= 1

    @pytest.mark.asyncio
    async def test_error_handling_during_monitoring(self):
        """Test error handling during monitoring."""
        with patch.object(self.monitor.process, "cpu_percent", side_effect=Exception("CPU error")):
            with patch.object(self.monitor.process, "memory_info", side_effect=Exception("Memory error")):
                await self.monitor.start()
                await asyncio.sleep(0.02)
                metrics = await self.monitor.stop()

                # Should still produce metrics despite errors
                assert isinstance(metrics, PerformanceMetrics)

    @pytest.mark.asyncio
    async def test_baseline_metric_creation_failure(self):
        """Test handling when baseline metric creation fails."""
        with patch.object(self.monitor.process, "memory_info", side_effect=Exception("Memory error")):
            await self.monitor.start()

            # Should have emergency baseline metric
            assert len(self.monitor.metrics_buffer) >= 1
            baseline = self.monitor.metrics_buffer[0]
            assert baseline.memory_rss == 1024 * 1024  # Emergency fallback value

    def test_io_counters_error_handling(self):
        """Test I/O counters error handling."""
        with patch.object(self.monitor.process, "io_counters", side_effect=Exception("I/O error")):
            io_result = self.monitor._get_io_counters()
            assert io_result is None

    def test_open_files_error_handling(self):
        """Test open files count error handling."""
        with patch.object(self.monitor.process, "open_files", side_effect=Exception("Files error")):
            files_count = self.monitor._get_open_files_count()
            assert files_count == 0  # Fallback value

    @pytest.mark.asyncio
    async def test_monitor_with_no_samples(self):
        """Test monitor behavior when no samples are collected."""
        # Mock to prevent any samples from being collected
        with patch.object(self.monitor, "_monitor_loop", return_value=None):
            await self.monitor.start()
            self.monitor.metrics_buffer.clear()  # Force empty buffer
            metrics = await self.monitor.stop()

            # Should still return valid metrics with fallback values
            assert isinstance(metrics, PerformanceMetrics)

    @pytest.mark.asyncio
    async def test_concurrent_monitoring_sessions(self):
        """Test multiple concurrent monitoring sessions."""
        monitor1 = EnhancedResourceMonitor(sampling_interval_ms=10)
        monitor2 = EnhancedResourceMonitor(sampling_interval_ms=10)

        try:
            # Start both monitors
            await asyncio.gather(monitor1.start(), monitor2.start())

            await asyncio.sleep(0.03)

            # Stop both monitors
            results = await asyncio.gather(monitor1.stop(), monitor2.stop())

            # Both should have collected metrics
            assert isinstance(results[0], PerformanceMetrics)
            assert isinstance(results[1], PerformanceMetrics)

        finally:
            if monitor1._monitor_task:
                monitor1._monitor_task.cancel()
            if monitor2._monitor_task:
                monitor2._monitor_task.cancel()

    def test_performance_metrics_calculation_with_valid_data(self):
        """Test performance metrics calculation with valid sample data."""
        # Add sample metrics to buffer
        self.monitor.metrics_buffer = [
            ResourceMetrics(
                timestamp=1.0,
                cpu_percent=50.0,
                memory_rss=100 * 1024 * 1024,  # 100MB
                memory_vms=150 * 1024 * 1024,  # 150MB
                num_threads=2,
                open_files=5,
            ),
            ResourceMetrics(
                timestamp=2.0,
                cpu_percent=75.0,
                memory_rss=200 * 1024 * 1024,  # 200MB
                memory_vms=250 * 1024 * 1024,  # 250MB
                num_threads=3,
                open_files=8,
            ),
            ResourceMetrics(
                timestamp=3.0,
                cpu_percent=60.0,
                memory_rss=150 * 1024 * 1024,  # 150MB
                memory_vms=200 * 1024 * 1024,  # 200MB
                num_threads=2,
                open_files=6,
            ),
        ]

        metrics = self.monitor._calculate_metrics()

        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.peak_memory_mb == 200.0  # Peak RSS
        assert metrics.avg_memory_mb == pytest.approx(150.0, abs=0.1)  # Average RSS
        assert metrics.peak_cpu_percent == 75.0
        assert metrics.avg_cpu_percent == pytest.approx(61.67, abs=0.1)

    def test_performance_metrics_calculation_with_empty_buffer(self):
        """Test performance metrics calculation with empty buffer."""
        self.monitor.metrics_buffer = []

        # Mock process info for emergency sample creation
        with patch.object(self.monitor.process, "memory_info") as mock_mem:
            with patch.object(self.monitor.process, "num_threads", return_value=1):
                with patch.object(self.monitor, "_get_open_files_count", return_value=5):
                    mock_mem.return_value = MagicMock(rss=50 * 1024 * 1024, vms=75 * 1024 * 1024)

                    metrics = self.monitor._calculate_metrics()

                    assert isinstance(metrics, PerformanceMetrics)
                    assert metrics.peak_memory_mb == 50.0
                    assert metrics.avg_memory_mb == 50.0

    def test_performance_metrics_calculation_with_exception(self):
        """Test performance metrics calculation when emergency sample creation fails."""
        self.monitor.metrics_buffer = []

        # Mock all process calls to fail
        with patch.object(self.monitor.process, "memory_info", side_effect=Exception("Memory error")):
            with patch.object(self.monitor.process, "num_threads", side_effect=Exception("Threads error")):
                with patch.object(self.monitor, "_get_open_files_count", side_effect=Exception("Files error")):
                    metrics = self.monitor._calculate_metrics()

                    # Should still return valid metrics with absolute fallback values
                    assert isinstance(metrics, PerformanceMetrics)
                    assert metrics.extraction_time == 0.0
                    assert metrics.peak_memory_mb == 0.0
                    assert metrics.avg_memory_mb == 0.0


class TestResourceMetricsEdgeCases:
    """Test edge cases for ResourceMetrics."""

    def test_resource_metrics_with_optional_fields(self):
        """Test ResourceMetrics with optional I/O fields."""
        metrics = ResourceMetrics(
            timestamp=1234567890.0,
            cpu_percent=50.0,
            memory_rss=100 * 1024 * 1024,
            memory_vms=150 * 1024 * 1024,
            num_threads=2,
            open_files=10,
            io_read_bytes=1024,
            io_write_bytes=2048,
            io_read_count=5,
            io_write_count=3,
        )

        assert metrics.io_read_bytes == 1024
        assert metrics.io_write_bytes == 2048
        assert metrics.io_read_count == 5
        assert metrics.io_write_count == 3

    def test_resource_metrics_without_optional_fields(self):
        """Test ResourceMetrics without optional I/O fields."""
        metrics = ResourceMetrics(
            timestamp=1234567890.0,
            cpu_percent=50.0,
            memory_rss=100 * 1024 * 1024,
            memory_vms=150 * 1024 * 1024,
            num_threads=2,
            open_files=10,
        )

        assert metrics.io_read_bytes is None
        assert metrics.io_write_bytes is None
        assert metrics.io_read_count is None
        assert metrics.io_write_count is None

    def test_resource_metrics_extreme_values(self):
        """Test ResourceMetrics with extreme values."""
        metrics = ResourceMetrics(
            timestamp=0.0, cpu_percent=0.0, memory_rss=0, memory_vms=0, num_threads=0, open_files=0
        )

        assert metrics.cpu_percent == 0.0
        assert metrics.memory_rss == 0
        assert metrics.num_threads == 0

        # Test very high values
        high_metrics = ResourceMetrics(
            timestamp=999999999.9,
            cpu_percent=800.0,  # Multi-core systems can exceed 100%
            memory_rss=8 * 1024 * 1024 * 1024,  # 8GB
            memory_vms=16 * 1024 * 1024 * 1024,  # 16GB
            num_threads=1000,
            open_files=10000,
        )

        assert high_metrics.cpu_percent == 800.0
        assert high_metrics.memory_rss == 8 * 1024 * 1024 * 1024
        assert high_metrics.num_threads == 1000


class TestPerformanceMetricsEdgeCases:
    """Test edge cases for PerformanceMetrics."""

    def test_performance_metrics_creation(self):
        """Test PerformanceMetrics creation with all fields."""
        sample_metrics = [
            ResourceMetrics(
                timestamp=1.0,
                cpu_percent=50.0,
                memory_rss=100 * 1024 * 1024,
                memory_vms=150 * 1024 * 1024,
                num_threads=2,
                open_files=5,
            )
        ]

        metrics = PerformanceMetrics(
            extraction_time=2.5,
            peak_memory_mb=100.0,
            avg_memory_mb=90.0,
            peak_cpu_percent=75.0,
            avg_cpu_percent=60.0,
            total_io_read_mb=1.5,
            total_io_write_mb=0.8,
            samples=sample_metrics,
            startup_time=0.5,
        )

        assert metrics.extraction_time == 2.5
        assert metrics.peak_memory_mb == 100.0
        assert metrics.total_io_read_mb == 1.5
        assert metrics.startup_time == 0.5
        assert len(metrics.samples) == 1

    def test_performance_metrics_with_minimal_fields(self):
        """Test PerformanceMetrics with minimal required fields."""
        metrics = PerformanceMetrics(
            extraction_time=1.0, peak_memory_mb=50.0, avg_memory_mb=45.0, peak_cpu_percent=30.0, avg_cpu_percent=25.0
        )

        assert metrics.extraction_time == 1.0
        assert metrics.total_io_read_mb is None
        assert metrics.startup_time is None
        assert len(metrics.samples) == 0  # Default empty list
