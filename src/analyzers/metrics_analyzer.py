"""
Metrics analysis module for statistical calculations.
"""
import numpy as np
from typing import Dict, List, Any
import logging


class MetricsAnalyzer:
    """Analyze system metrics and calculate statistics."""

    def __init__(self):
        """Initialize metrics analyzer."""
        self.logger = logging.getLogger('monitoring_system')

    def analyze_monthly_metrics(self, metrics_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze monthly metrics data.

        Args:
            metrics_list: List of daily metrics dictionaries

        Returns:
            Dictionary containing analyzed statistics
        """
        if not metrics_list:
            self.logger.warning("No metrics data to analyze")
            return {}

        self.logger.info(f"Analyzing {len(metrics_list)} days of metrics")

        analysis = {
            'period': {
                'days_collected': len(metrics_list),
                'start_date': metrics_list[0].get('timestamp'),
                'end_date': metrics_list[-1].get('timestamp')
            },
            'cpu': self._analyze_cpu_metrics(metrics_list),
            'memory': self._analyze_memory_metrics(metrics_list),
            'disk': self._analyze_disk_metrics(metrics_list)
        }

        return analysis

    def _analyze_cpu_metrics(self, metrics_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze CPU metrics.

        Args:
            metrics_list: List of metrics dictionaries

        Returns:
            CPU statistics dictionary
        """
        cpu_usage = []
        load_1m = []
        load_5m = []
        load_15m = []

        for metrics in metrics_list:
            cpu_data = metrics.get('cpu', {})
            if cpu_data:
                usage = cpu_data.get('usage_percent')
                if usage is not None:
                    cpu_usage.append(usage)

                load_avg = cpu_data.get('load_average', {})
                if load_avg.get('1min') is not None:
                    load_1m.append(load_avg['1min'])
                if load_avg.get('5min') is not None:
                    load_5m.append(load_avg['5min'])
                if load_avg.get('15min') is not None:
                    load_15m.append(load_avg['15min'])

        stats = {
            'usage': self._calculate_stats(cpu_usage),
            'load_average': {
                '1min': self._calculate_stats(load_1m),
                '5min': self._calculate_stats(load_5m),
                '15min': self._calculate_stats(load_15m)
            }
        }

        # Add trend analysis
        if len(cpu_usage) > 1:
            stats['trend'] = self._analyze_trend(cpu_usage)

        return stats

    def _analyze_memory_metrics(self, metrics_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze memory metrics.

        Args:
            metrics_list: List of metrics dictionaries

        Returns:
            Memory statistics dictionary
        """
        ram_percent = []
        swap_percent = []
        ram_used = []
        swap_used = []

        for metrics in metrics_list:
            mem_data = metrics.get('memory', {})
            if mem_data:
                ram = mem_data.get('ram', {})
                swap = mem_data.get('swap', {})

                if ram.get('percent') is not None:
                    ram_percent.append(ram['percent'])
                if ram.get('used') is not None:
                    ram_used.append(ram['used'])
                if swap.get('percent') is not None:
                    swap_percent.append(swap['percent'])
                if swap.get('used') is not None:
                    swap_used.append(swap['used'])

        stats = {
            'ram': {
                'usage_percent': self._calculate_stats(ram_percent),
                'usage_bytes': self._calculate_stats(ram_used)
            },
            'swap': {
                'usage_percent': self._calculate_stats(swap_percent),
                'usage_bytes': self._calculate_stats(swap_used)
            }
        }

        # Add trend analysis
        if len(ram_percent) > 1:
            stats['ram']['trend'] = self._analyze_trend(ram_percent)
        if len(swap_percent) > 1:
            stats['swap']['trend'] = self._analyze_trend(swap_percent)

        return stats

    def _analyze_disk_metrics(self, metrics_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze disk metrics.

        Args:
            metrics_list: List of metrics dictionaries

        Returns:
            Disk statistics dictionary
        """
        # Collect metrics per partition
        partition_metrics = {}

        for metrics in metrics_list:
            disk_data = metrics.get('disk', {})
            partitions = disk_data.get('partitions', [])

            for partition in partitions:
                mountpoint = partition.get('mountpoint')
                if not mountpoint:
                    continue

                if mountpoint not in partition_metrics:
                    partition_metrics[mountpoint] = {
                        'device': partition.get('device'),
                        'fstype': partition.get('fstype'),
                        'usage_percent': [],
                        'used_bytes': [],
                        'free_bytes': []
                    }

                if partition.get('percent') is not None:
                    partition_metrics[mountpoint]['usage_percent'].append(partition['percent'])
                if partition.get('used') is not None:
                    partition_metrics[mountpoint]['used_bytes'].append(partition['used'])
                if partition.get('free') is not None:
                    partition_metrics[mountpoint]['free_bytes'].append(partition['free'])

        # Calculate statistics for each partition
        stats = {}
        for mountpoint, data in partition_metrics.items():
            stats[mountpoint] = {
                'device': data['device'],
                'fstype': data['fstype'],
                'usage_percent': self._calculate_stats(data['usage_percent']),
                'used_bytes': self._calculate_stats(data['used_bytes']),
                'free_bytes': self._calculate_stats(data['free_bytes'])
            }

            # Add trend analysis
            if len(data['usage_percent']) > 1:
                stats[mountpoint]['trend'] = self._analyze_trend(data['usage_percent'])

        return stats

    def _calculate_stats(self, values: List[float]) -> Dict[str, float]:
        """
        Calculate statistical measures for a list of values.

        Args:
            values: List of numeric values

        Returns:
            Dictionary containing statistical measures
        """
        if not values:
            return {
                'min': None,
                'max': None,
                'mean': None,
                'median': None,
                'std': None
            }

        arr = np.array(values)

        return {
            'min': float(np.min(arr)),
            'max': float(np.max(arr)),
            'mean': float(np.mean(arr)),
            'median': float(np.median(arr)),
            'std': float(np.std(arr))
        }

    def _analyze_trend(self, values: List[float]) -> str:
        """
        Analyze trend in values.

        Args:
            values: List of numeric values

        Returns:
            Trend description ('increasing', 'decreasing', 'stable')
        """
        if len(values) < 2:
            return 'stable'

        # Simple linear regression slope
        x = np.arange(len(values))
        y = np.array(values)

        # Calculate slope
        slope = np.polyfit(x, y, 1)[0]

        # Threshold for considering trend significant (relative to mean)
        mean_value = np.mean(y)
        threshold = mean_value * 0.01  # 1% of mean

        if abs(slope) < threshold:
            return 'stable'
        elif slope > 0:
            return 'increasing'
        else:
            return 'decreasing'

    def get_summary_statistics(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate summary statistics from analysis.

        Args:
            analysis: Analysis dictionary from analyze_monthly_metrics

        Returns:
            Summary statistics dictionary
        """
        summary = {
            'collection_period': analysis.get('period', {}),
            'cpu_summary': {},
            'memory_summary': {},
            'disk_summary': {}
        }

        # CPU summary
        cpu = analysis.get('cpu', {})
        if cpu.get('usage'):
            summary['cpu_summary'] = {
                'avg_usage': cpu['usage'].get('mean'),
                'max_usage': cpu['usage'].get('max'),
                'trend': cpu.get('trend', 'stable')
            }

        # Memory summary
        memory = analysis.get('memory', {})
        if memory.get('ram', {}).get('usage_percent'):
            summary['memory_summary'] = {
                'avg_ram_usage': memory['ram']['usage_percent'].get('mean'),
                'max_ram_usage': memory['ram']['usage_percent'].get('max'),
                'avg_swap_usage': memory.get('swap', {}).get('usage_percent', {}).get('mean'),
                'trend': memory.get('ram', {}).get('trend', 'stable')
            }

        # Disk summary (for root partition)
        disk = analysis.get('disk', {})
        root_disk = disk.get('/', disk.get('/home', {}))
        if root_disk.get('usage_percent'):
            summary['disk_summary'] = {
                'avg_usage': root_disk['usage_percent'].get('mean'),
                'max_usage': root_disk['usage_percent'].get('max'),
                'trend': root_disk.get('trend', 'stable')
            }

        return summary
