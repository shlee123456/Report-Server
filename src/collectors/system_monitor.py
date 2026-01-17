"""
System metrics collection module using psutil.
"""
import psutil
import os
from datetime import datetime
from typing import Dict, Any, List
import logging


class SystemMonitor:
    """Collect system metrics using psutil."""

    def __init__(self):
        """Initialize system monitor."""
        self.logger = logging.getLogger('monitoring_system')

    def collect_all_metrics(self) -> Dict[str, Any]:
        """
        Collect all system metrics.

        Returns:
            Dictionary containing all metrics
        """
        self.logger.info("Starting metrics collection")

        try:
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu': self.collect_cpu_metrics(),
                'memory': self.collect_memory_metrics(),
                'disk': self.collect_disk_metrics(),
            }

            self.logger.info("Metrics collection completed successfully")
            return metrics

        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
            raise

    def collect_cpu_metrics(self) -> Dict[str, Any]:
        """
        Collect CPU metrics.

        Returns:
            Dictionary containing CPU metrics
        """
        try:
            # Get CPU percentages
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_percent_per_core = psutil.cpu_percent(interval=1, percpu=True)

            # Get load averages (Unix-like systems only)
            if hasattr(os, 'getloadavg'):
                load_avg = os.getloadavg()
                load_1m, load_5m, load_15m = load_avg
            else:
                load_1m = load_5m = load_15m = None

            # Get CPU count
            cpu_count = psutil.cpu_count(logical=True)
            cpu_count_physical = psutil.cpu_count(logical=False)

            # Get CPU frequency
            cpu_freq = psutil.cpu_freq()
            freq_current = cpu_freq.current if cpu_freq else None
            freq_min = cpu_freq.min if cpu_freq else None
            freq_max = cpu_freq.max if cpu_freq else None

            return {
                'usage_percent': cpu_percent,
                'usage_per_core': cpu_percent_per_core,
                'load_average': {
                    '1min': load_1m,
                    '5min': load_5m,
                    '15min': load_15m
                },
                'cpu_count': {
                    'logical': cpu_count,
                    'physical': cpu_count_physical
                },
                'frequency': {
                    'current': freq_current,
                    'min': freq_min,
                    'max': freq_max
                }
            }

        except Exception as e:
            self.logger.error(f"Error collecting CPU metrics: {e}")
            return {}

    def collect_memory_metrics(self) -> Dict[str, Any]:
        """
        Collect memory metrics.

        Returns:
            Dictionary containing memory metrics
        """
        try:
            # Virtual memory (RAM)
            vm = psutil.virtual_memory()

            # Swap memory
            swap = psutil.swap_memory()

            return {
                'ram': {
                    'total': vm.total,
                    'available': vm.available,
                    'used': vm.used,
                    'free': vm.free,
                    'percent': vm.percent,
                    'active': getattr(vm, 'active', None),
                    'inactive': getattr(vm, 'inactive', None),
                    'buffers': getattr(vm, 'buffers', None),
                    'cached': getattr(vm, 'cached', None)
                },
                'swap': {
                    'total': swap.total,
                    'used': swap.used,
                    'free': swap.free,
                    'percent': swap.percent,
                    'sin': swap.sin,
                    'sout': swap.sout
                }
            }

        except Exception as e:
            self.logger.error(f"Error collecting memory metrics: {e}")
            return {}

    def collect_disk_metrics(self) -> Dict[str, Any]:
        """
        Collect disk metrics.

        Returns:
            Dictionary containing disk metrics
        """
        try:
            disk_metrics = {
                'partitions': [],
                'io_counters': None
            }

            # Get partition information
            partitions = psutil.disk_partitions(all=False)
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_metrics['partitions'].append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'opts': partition.opts,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent
                    })
                except PermissionError:
                    self.logger.warning(f"Permission denied for partition: {partition.mountpoint}")
                except Exception as e:
                    self.logger.warning(f"Error reading partition {partition.mountpoint}: {e}")

            # Get I/O statistics
            try:
                io_counters = psutil.disk_io_counters()
                if io_counters:
                    disk_metrics['io_counters'] = {
                        'read_count': io_counters.read_count,
                        'write_count': io_counters.write_count,
                        'read_bytes': io_counters.read_bytes,
                        'write_bytes': io_counters.write_bytes,
                        'read_time': io_counters.read_time,
                        'write_time': io_counters.write_time
                    }
            except Exception as e:
                self.logger.warning(f"Error collecting disk I/O counters: {e}")

            return disk_metrics

        except Exception as e:
            self.logger.error(f"Error collecting disk metrics: {e}")
            return {}

    def get_system_info(self) -> Dict[str, Any]:
        """
        Get general system information.

        Returns:
            Dictionary containing system information
        """
        try:
            import platform

            boot_time = datetime.fromtimestamp(psutil.boot_time())

            return {
                'hostname': platform.node(),
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'boot_time': boot_time.isoformat(),
                'uptime_seconds': (datetime.now() - boot_time).total_seconds()
            }

        except Exception as e:
            self.logger.error(f"Error collecting system info: {e}")
            return {}
