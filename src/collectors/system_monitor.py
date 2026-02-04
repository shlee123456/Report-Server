"""
System metrics collection module using psutil and direct /proc parsing for host metrics.
"""
import psutil
import os
import time
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
import logging


class SystemMonitor:
    """Collect system metrics using psutil and direct /proc parsing for host metrics."""

    def __init__(self):
        """Initialize system monitor."""
        self.logger = logging.getLogger('monitoring_system')
        # Get host proc/sys paths from environment (defaults to /proc, /sys)
        self.host_proc = os.environ.get('HOST_PROC', '/proc')
        self.host_sys = os.environ.get('HOST_SYS', '/sys')
        self.use_host_metrics = self.host_proc != '/proc'
        
        if self.use_host_metrics:
            self.logger.info(f"Using host metrics from {self.host_proc}")
        else:
            self.logger.info("Using container/local metrics")

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

    def _read_proc_stat(self) -> Dict[str, List[int]]:
        """
        Read and parse /proc/stat file.

        Returns:
            Dictionary with CPU names as keys and timing values as lists
        """
        stat_file = os.path.join(self.host_proc, 'stat')
        cpu_stats = {}
        
        try:
            with open(stat_file, 'r') as f:
                for line in f:
                    if line.startswith('cpu'):
                        parts = line.split()
                        cpu_name = parts[0]
                        # Parse timing values (user, nice, system, idle, iowait, irq, softirq, steal, guest, guest_nice)
                        values = [int(x) for x in parts[1:]]
                        cpu_stats[cpu_name] = values
        except Exception as e:
            self.logger.error(f"Error reading {stat_file}: {e}")
            raise
        
        return cpu_stats

    def _calculate_cpu_usage(self, stat1: List[int], stat2: List[int]) -> float:
        """
        Calculate CPU usage percentage from two /proc/stat readings.

        Args:
            stat1: First reading of CPU timing values
            stat2: Second reading of CPU timing values

        Returns:
            CPU usage percentage (0-100)
        """
        # Calculate deltas
        deltas = [stat2[i] - stat1[i] for i in range(len(stat1))]
        
        # Total time is sum of all fields
        total_delta = sum(deltas)
        
        if total_delta == 0:
            return 0.0
        
        # Idle time is the 4th field (index 3)
        idle_delta = deltas[3] if len(deltas) > 3 else 0
        
        # Add iowait (5th field, index 4) to idle if available
        if len(deltas) > 4:
            idle_delta += deltas[4]
        
        # Calculate usage percentage
        usage_percent = 100.0 * (1.0 - (idle_delta / total_delta))
        
        return max(0.0, min(100.0, usage_percent))

    def _read_proc_cpuinfo(self) -> Dict[str, Any]:
        """
        Read and parse /proc/cpuinfo file.

        Returns:
            Dictionary with CPU information (model, cores, frequency)
        """
        cpuinfo_file = os.path.join(self.host_proc, 'cpuinfo')
        cpu_info = {
            'model_name': None,
            'cpu_mhz': None,
            'cores': 0
        }
        
        try:
            with open(cpuinfo_file, 'r') as f:
                for line in f:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        if key == 'model name' and cpu_info['model_name'] is None:
                            cpu_info['model_name'] = value
                        elif key == 'cpu MHz' and cpu_info['cpu_mhz'] is None:
                            try:
                                cpu_info['cpu_mhz'] = float(value)
                            except ValueError:
                                pass
                        elif key == 'processor':
                            cpu_info['cores'] += 1
        except Exception as e:
            self.logger.warning(f"Error reading {cpuinfo_file}: {e}")
        
        return cpu_info

    def _read_proc_loadavg(self) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """
        Read load averages from /proc/loadavg.

        Returns:
            Tuple of (load_1m, load_5m, load_15m)
        """
        loadavg_file = os.path.join(self.host_proc, 'loadavg')
        
        try:
            with open(loadavg_file, 'r') as f:
                line = f.readline().strip()
                parts = line.split()
                if len(parts) >= 3:
                    return float(parts[0]), float(parts[1]), float(parts[2])
        except Exception as e:
            self.logger.warning(f"Error reading {loadavg_file}: {e}")
        
        return None, None, None

    def collect_cpu_metrics(self) -> Dict[str, Any]:
        """
        Collect CPU metrics from host system.

        Returns:
            Dictionary containing CPU metrics
        """
        try:
            # If using host metrics, parse /proc directly
            if self.use_host_metrics:
                return self._collect_host_cpu_metrics()
            else:
                return self._collect_psutil_cpu_metrics()

        except Exception as e:
            self.logger.error(f"Error collecting CPU metrics: {e}")
            # Fallback to psutil if host metrics fail
            try:
                return self._collect_psutil_cpu_metrics()
            except:
                return {}

    def _collect_host_cpu_metrics(self) -> Dict[str, Any]:
        """
        Collect CPU metrics by parsing host /proc files directly.

        Returns:
            Dictionary containing CPU metrics
        """
        # Read /proc/stat twice with 1 second interval
        stat1 = self._read_proc_stat()
        time.sleep(1)
        stat2 = self._read_proc_stat()

        # Calculate overall CPU usage
        cpu_percent = 0.0
        if 'cpu' in stat1 and 'cpu' in stat2:
            cpu_percent = self._calculate_cpu_usage(stat1['cpu'], stat2['cpu'])

        # Calculate per-core CPU usage
        cpu_percent_per_core = []
        core_num = 0
        while True:
            core_name = f'cpu{core_num}'
            if core_name in stat1 and core_name in stat2:
                core_usage = self._calculate_cpu_usage(stat1[core_name], stat2[core_name])
                cpu_percent_per_core.append(core_usage)
                core_num += 1
            else:
                break

        # Get load averages
        load_1m, load_5m, load_15m = self._read_proc_loadavg()

        # Get CPU info
        cpu_info = self._read_proc_cpuinfo()

        # CPU count
        cpu_count = len(cpu_percent_per_core) if cpu_percent_per_core else cpu_info['cores']
        
        # Try to get physical core count (logical / 2 if hyperthreading)
        cpu_count_physical = cpu_count // 2 if cpu_count > 1 else cpu_count

        return {
            'usage_percent': round(cpu_percent, 1),
            'usage_per_core': [round(x, 1) for x in cpu_percent_per_core],
            'load_average': {
                '1min': load_1m,
                '5min': load_5m,
                '15min': load_15m
            },
            'cpu_count': {
                'logical': cpu_count,
                'physical': cpu_count_physical
            },
            'cpu_info': {
                'model_name': cpu_info['model_name'],
                'frequency_mhz': cpu_info['cpu_mhz']
            },
            'frequency': {
                'current': cpu_info['cpu_mhz'],
                'min': None,
                'max': None
            }
        }

    def _collect_psutil_cpu_metrics(self) -> Dict[str, Any]:
        """
        Collect CPU metrics using psutil (fallback method).

        Returns:
            Dictionary containing CPU metrics
        """
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

    def _read_proc_meminfo(self) -> Dict[str, int]:
        """
        Read and parse /proc/meminfo file.

        Returns:
            Dictionary with memory information in bytes
        """
        meminfo_file = os.path.join(self.host_proc, 'meminfo')
        meminfo = {}
        
        try:
            with open(meminfo_file, 'r') as f:
                for line in f:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Remove 'kB' and convert to bytes
                        if value.endswith(' kB'):
                            value = value[:-3].strip()
                        
                        try:
                            # Convert from kB to bytes
                            meminfo[key] = int(value) * 1024
                        except ValueError:
                            pass
        except Exception as e:
            self.logger.error(f"Error reading {meminfo_file}: {e}")
            raise
        
        return meminfo

    def collect_memory_metrics(self) -> Dict[str, Any]:
        """
        Collect memory metrics from host system.

        Returns:
            Dictionary containing memory metrics
        """
        try:
            # If using host metrics, parse /proc directly
            if self.use_host_metrics:
                return self._collect_host_memory_metrics()
            else:
                return self._collect_psutil_memory_metrics()

        except Exception as e:
            self.logger.error(f"Error collecting memory metrics: {e}")
            # Fallback to psutil if host metrics fail
            try:
                return self._collect_psutil_memory_metrics()
            except:
                return {}

    def _collect_host_memory_metrics(self) -> Dict[str, Any]:
        """
        Collect memory metrics by parsing host /proc/meminfo directly.

        Returns:
            Dictionary containing memory metrics
        """
        meminfo = self._read_proc_meminfo()
        
        # Extract key memory values
        mem_total = meminfo.get('MemTotal', 0)
        mem_free = meminfo.get('MemFree', 0)
        mem_available = meminfo.get('MemAvailable', mem_free)
        buffers = meminfo.get('Buffers', 0)
        cached = meminfo.get('Cached', 0)
        
        # Calculate used memory
        # used = total - free - buffers - cached
        mem_used = mem_total - mem_free - buffers - cached
        
        # Calculate percentage
        mem_percent = (mem_used / mem_total * 100) if mem_total > 0 else 0
        
        # Swap memory
        swap_total = meminfo.get('SwapTotal', 0)
        swap_free = meminfo.get('SwapFree', 0)
        swap_used = swap_total - swap_free
        swap_percent = (swap_used / swap_total * 100) if swap_total > 0 else 0
        
        return {
            'ram': {
                'total': mem_total,
                'available': mem_available,
                'used': mem_used,
                'free': mem_free,
                'percent': round(mem_percent, 1),
                'active': meminfo.get('Active', None),
                'inactive': meminfo.get('Inactive', None),
                'buffers': buffers,
                'cached': cached
            },
            'swap': {
                'total': swap_total,
                'used': swap_used,
                'free': swap_free,
                'percent': round(swap_percent, 1),
                'sin': 0,  # Not available from /proc/meminfo
                'sout': 0  # Not available from /proc/meminfo
            }
        }

    def _collect_psutil_memory_metrics(self) -> Dict[str, Any]:
        """
        Collect memory metrics using psutil (fallback method).

        Returns:
            Dictionary containing memory metrics
        """
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
            import socket

            boot_time = datetime.fromtimestamp(psutil.boot_time())

            # Get primary IP address
            ip_address = self._get_primary_ip()

            return {
                'hostname': platform.node(),
                'ip_address': ip_address,
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

    def _get_primary_ip(self) -> str:
        """
        Get the primary IP address of the server.

        Returns:
            IP address as string
        """
        try:
            import socket

            # Try to get the IP by connecting to an external address (doesn't actually send data)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0)
            try:
                # Connect to a public DNS server
                s.connect(('8.8.8.8', 80))
                ip_address = s.getsockname()[0]
            except Exception:
                # Fallback to hostname resolution
                ip_address = socket.gethostbyname(socket.gethostname())
            finally:
                s.close()

            return ip_address
        except Exception as e:
            self.logger.warning(f"Could not determine IP address: {e}")
            return "N/A"
