"""
Table builder module for formatting data tables.
"""
from typing import List, Dict, Any, Tuple
import logging


class TableBuilder:
    """Build formatted tables for PDF reports."""

    def __init__(self):
        """Initialize table builder."""
        self.logger = logging.getLogger('monitoring_system')

    def build_summary_table(self, summary: Dict[str, Any]) -> List[List[str]]:
        """
        Build summary statistics table.

        Args:
            summary: Summary statistics dictionary

        Returns:
            Table data as list of rows
        """
        table_data = [
            ['Metric', 'Value']
        ]

        # Collection period
        period = summary.get('collection_period', {})
        days = period.get('days_collected', 'N/A')
        table_data.append(['Collection Period', f'{days} days'])

        # CPU summary
        cpu = summary.get('cpu_summary', {})
        if cpu:
            avg_cpu = cpu.get('avg_usage')
            max_cpu = cpu.get('max_usage')
            trend = cpu.get('trend', 'N/A')

            if avg_cpu is not None:
                table_data.append(['Avg CPU Usage', f'{avg_cpu:.1f}%'])
            if max_cpu is not None:
                table_data.append(['Max CPU Usage', f'{max_cpu:.1f}%'])
            table_data.append(['CPU Trend', trend.capitalize()])

        # Memory summary
        memory = summary.get('memory_summary', {})
        if memory:
            avg_ram = memory.get('avg_ram_usage')
            max_ram = memory.get('max_ram_usage')
            avg_swap = memory.get('avg_swap_usage')
            trend = memory.get('trend', 'N/A')

            if avg_ram is not None:
                table_data.append(['Avg RAM Usage', f'{avg_ram:.1f}%'])
            if max_ram is not None:
                table_data.append(['Max RAM Usage', f'{max_ram:.1f}%'])
            if avg_swap is not None:
                table_data.append(['Avg SWAP Usage', f'{avg_swap:.1f}%'])
            table_data.append(['Memory Trend', trend.capitalize()])

        # Disk summary
        disk = summary.get('disk_summary', {})
        if disk:
            avg_disk = disk.get('avg_usage')
            max_disk = disk.get('max_usage')
            trend = disk.get('trend', 'N/A')

            if avg_disk is not None:
                table_data.append(['Avg Disk Usage', f'{avg_disk:.1f}%'])
            if max_disk is not None:
                table_data.append(['Max Disk Usage', f'{max_disk:.1f}%'])
            table_data.append(['Disk Trend', trend.capitalize()])

        return table_data

    def build_cpu_stats_table(self, cpu_analysis: Dict[str, Any]) -> List[List[str]]:
        """
        Build CPU statistics table.

        Args:
            cpu_analysis: CPU analysis dictionary

        Returns:
            Table data as list of rows
        """
        table_data = [
            ['Statistic', 'Value']
        ]

        usage = cpu_analysis.get('usage', {})
        if usage:
            if usage.get('min') is not None:
                table_data.append(['Minimum', f"{usage['min']:.2f}%"])
            if usage.get('max') is not None:
                table_data.append(['Maximum', f"{usage['max']:.2f}%"])
            if usage.get('mean') is not None:
                table_data.append(['Average', f"{usage['mean']:.2f}%"])
            if usage.get('median') is not None:
                table_data.append(['Median', f"{usage['median']:.2f}%"])
            if usage.get('std') is not None:
                table_data.append(['Std Deviation', f"{usage['std']:.2f}%"])

        # Load averages
        load_avg = cpu_analysis.get('load_average', {})
        load_1m = load_avg.get('1min', {})
        if load_1m and load_1m.get('mean') is not None:
            table_data.append(['Avg Load (1min)', f"{load_1m['mean']:.2f}"])

        return table_data

    def build_memory_stats_table(self, memory_analysis: Dict[str, Any]) -> List[List[str]]:
        """
        Build memory statistics table.

        Args:
            memory_analysis: Memory analysis dictionary

        Returns:
            Table data as list of rows
        """
        table_data = [
            ['Metric', 'Min', 'Max', 'Average']
        ]

        # RAM statistics
        ram = memory_analysis.get('ram', {}).get('usage_percent', {})
        if ram:
            table_data.append([
                'RAM Usage (%)',
                f"{ram.get('min', 0):.1f}%",
                f"{ram.get('max', 0):.1f}%",
                f"{ram.get('mean', 0):.1f}%"
            ])

        # SWAP statistics
        swap = memory_analysis.get('swap', {}).get('usage_percent', {})
        if swap:
            table_data.append([
                'SWAP Usage (%)',
                f"{swap.get('min', 0):.1f}%",
                f"{swap.get('max', 0):.1f}%",
                f"{swap.get('mean', 0):.1f}%"
            ])

        return table_data

    def build_disk_stats_table(self, disk_analysis: Dict[str, Any]) -> List[List[str]]:
        """
        Build disk statistics table.

        Args:
            disk_analysis: Disk analysis dictionary

        Returns:
            Table data as list of rows
        """
        table_data = [
            ['Mountpoint', 'Device', 'Type', 'Avg Usage', 'Max Usage', 'Trend']
        ]

        for mountpoint, stats in disk_analysis.items():
            device = stats.get('device', 'N/A')
            fstype = stats.get('fstype', 'N/A')
            usage_percent = stats.get('usage_percent', {})
            trend = stats.get('trend', 'stable')

            avg_usage = usage_percent.get('mean')
            max_usage = usage_percent.get('max')

            table_data.append([
                mountpoint,
                device,
                fstype,
                f"{avg_usage:.1f}%" if avg_usage is not None else 'N/A',
                f"{max_usage:.1f}%" if max_usage is not None else 'N/A',
                trend.capitalize()
            ])

        return table_data

    def build_violations_table(self, violations: List[Dict[str, Any]]) -> List[List[str]]:
        """
        Build threshold violations table.

        Args:
            violations: List of violations

        Returns:
            Table data as list of rows
        """
        table_data = [
            ['Metric', 'Value', 'Threshold', 'Severity']
        ]

        for violation in violations:
            metric = violation.get('metric', 'N/A')
            value = violation.get('value', 'N/A')
            threshold = violation.get('threshold', 'N/A')
            severity = violation.get('severity', 'N/A')

            # Format value
            if isinstance(value, (int, float)):
                value_str = f"{value:.1f}"
            else:
                value_str = str(value)

            table_data.append([
                metric,
                value_str,
                str(threshold),
                severity.upper()
            ])

        if len(table_data) == 1:
            table_data.append(['No violations detected', '', '', ''])

        return table_data

    def build_log_summary_table(self, log_analysis: Dict[str, Any]) -> List[List[str]]:
        """
        Build log analysis summary table.

        Args:
            log_analysis: Log analysis dictionary

        Returns:
            Table data as list of rows
        """
        table_data = [
            ['Log Source', 'Errors', 'Warnings', 'Total Events']
        ]

        # Syslog
        syslog = log_analysis.get('syslog', {})
        table_data.append([
            'System Log',
            str(syslog.get('error_count', 0)),
            str(syslog.get('warning_count', 0)),
            str(syslog.get('error_count', 0) + syslog.get('warning_count', 0))
        ])

        # Auth log
        auth_log = log_analysis.get('auth_log', {})
        table_data.append([
            'Authentication Log',
            str(auth_log.get('error_count', 0)),
            str(auth_log.get('warning_count', 0)),
            str(auth_log.get('security_events', 0))
        ])

        # Kernel log
        kernel_log = log_analysis.get('kernel_log', {})
        table_data.append([
            'Kernel Log',
            str(kernel_log.get('error_count', 0)),
            'N/A',
            str(kernel_log.get('error_count', 0))
        ])

        # Total
        summary = log_analysis.get('summary', {})
        table_data.append([
            'TOTAL',
            str(summary.get('total_errors', 0)),
            str(summary.get('total_warnings', 0)),
            str(summary.get('total_events', 0))
        ])

        return table_data

    def build_recommendations_table(self, recommendations: List[Dict[str, Any]]) -> List[List[str]]:
        """
        Build recommendations table.

        Args:
            recommendations: List of recommendations

        Returns:
            Table data as list of rows
        """
        table_data = [
            ['Priority', 'Category', 'Title']
        ]

        for rec in recommendations:
            priority = rec.get('priority', 'N/A').upper()
            category = rec.get('category', 'N/A')
            title = rec.get('title', 'N/A')

            table_data.append([priority, category, title])

        if len(table_data) == 1:
            table_data.append(['N/A', 'N/A', 'No recommendations'])

        return table_data

    def format_bytes(self, bytes_value: int) -> str:
        """
        Format bytes to human-readable format.

        Args:
            bytes_value: Value in bytes

        Returns:
            Formatted string (e.g., "1.5 GB")
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
