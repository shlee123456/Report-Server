"""
Threshold checking module for detecting violations.
"""
from typing import Dict, List, Any
from datetime import datetime
import logging


class ThresholdChecker:
    """Check metrics against configured thresholds."""

    def __init__(self, thresholds: Dict[str, Any]):
        """
        Initialize threshold checker.

        Args:
            thresholds: Threshold configuration dictionary
        """
        self.thresholds = thresholds
        self.logger = logging.getLogger('monitoring_system')

    def check_all_thresholds(
        self,
        analysis: Dict[str, Any],
        log_analysis: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Check all metrics against thresholds.

        Args:
            analysis: Analyzed metrics dictionary
            log_analysis: Log analysis results (optional)

        Returns:
            List of threshold violations
        """
        violations = []

        # Check CPU thresholds
        violations.extend(self._check_cpu_thresholds(analysis.get('cpu', {})))

        # Check memory thresholds
        violations.extend(self._check_memory_thresholds(analysis.get('memory', {})))

        # Check disk thresholds
        violations.extend(self._check_disk_thresholds(analysis.get('disk', {})))

        # Check log thresholds
        if log_analysis:
            violations.extend(self._check_log_thresholds(log_analysis))

        self.logger.info(f"Found {len(violations)} threshold violations")
        return violations

    def _check_cpu_thresholds(self, cpu_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check CPU metrics against thresholds.

        Args:
            cpu_analysis: CPU analysis dictionary

        Returns:
            List of violations
        """
        violations = []
        cpu_thresholds = self.thresholds.get('cpu', {})

        usage_stats = cpu_analysis.get('usage', {})
        if not usage_stats:
            return violations

        avg_usage = usage_stats.get('mean')
        max_usage = usage_stats.get('max')

        # Check critical thresholds
        critical = cpu_thresholds.get('critical', {})
        if avg_usage and avg_usage >= critical.get('avg_usage', 100):
            violations.append({
                'metric': 'CPU Average Usage',
                'value': avg_usage,
                'threshold': critical['avg_usage'],
                'severity': 'critical',
                'message': f"CPU average usage ({avg_usage:.1f}%) exceeds critical threshold ({critical['avg_usage']}%)"
            })

        if max_usage and max_usage >= critical.get('max_usage', 100):
            violations.append({
                'metric': 'CPU Maximum Usage',
                'value': max_usage,
                'threshold': critical['max_usage'],
                'severity': 'critical',
                'message': f"CPU maximum usage ({max_usage:.1f}%) exceeds critical threshold ({critical['max_usage']}%)"
            })

        # Check warning thresholds
        warning = cpu_thresholds.get('warning', {})
        if avg_usage and avg_usage >= warning.get('avg_usage', 100):
            violations.append({
                'metric': 'CPU Average Usage',
                'value': avg_usage,
                'threshold': warning['avg_usage'],
                'severity': 'warning',
                'message': f"CPU average usage ({avg_usage:.1f}%) exceeds warning threshold ({warning['avg_usage']}%)"
            })

        if max_usage and max_usage >= warning.get('max_usage', 100):
            violations.append({
                'metric': 'CPU Maximum Usage',
                'value': max_usage,
                'threshold': warning['max_usage'],
                'severity': 'warning',
                'message': f"CPU maximum usage ({max_usage:.1f}%) exceeds warning threshold ({warning['max_usage']}%)"
            })

        return violations

    def _check_memory_thresholds(self, memory_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check memory metrics against thresholds.

        Args:
            memory_analysis: Memory analysis dictionary

        Returns:
            List of violations
        """
        violations = []
        memory_thresholds = self.thresholds.get('memory', {})

        ram_stats = memory_analysis.get('ram', {}).get('usage_percent', {})
        swap_stats = memory_analysis.get('swap', {}).get('usage_percent', {})

        avg_ram = ram_stats.get('mean')
        max_ram = ram_stats.get('max')
        avg_swap = swap_stats.get('mean')

        # Check critical thresholds
        critical = memory_thresholds.get('critical', {})
        if avg_ram and avg_ram >= critical.get('ram_usage', 100):
            violations.append({
                'metric': 'RAM Average Usage',
                'value': avg_ram,
                'threshold': critical['ram_usage'],
                'severity': 'critical',
                'message': f"RAM average usage ({avg_ram:.1f}%) exceeds critical threshold ({critical['ram_usage']}%)"
            })

        if avg_swap and avg_swap >= critical.get('swap_usage', 100):
            violations.append({
                'metric': 'SWAP Average Usage',
                'value': avg_swap,
                'threshold': critical['swap_usage'],
                'severity': 'critical',
                'message': f"SWAP average usage ({avg_swap:.1f}%) exceeds critical threshold ({critical['swap_usage']}%)"
            })

        # Check warning thresholds
        warning = memory_thresholds.get('warning', {})
        if avg_ram and avg_ram >= warning.get('ram_usage', 100):
            violations.append({
                'metric': 'RAM Average Usage',
                'value': avg_ram,
                'threshold': warning['ram_usage'],
                'severity': 'warning',
                'message': f"RAM average usage ({avg_ram:.1f}%) exceeds warning threshold ({warning['ram_usage']}%)"
            })

        if avg_swap and avg_swap >= warning.get('swap_usage', 100):
            violations.append({
                'metric': 'SWAP Average Usage',
                'value': avg_swap,
                'threshold': warning['swap_usage'],
                'severity': 'warning',
                'message': f"SWAP average usage ({avg_swap:.1f}%) exceeds warning threshold ({warning['swap_usage']}%)"
            })

        return violations

    def _check_disk_thresholds(self, disk_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check disk metrics against thresholds.

        Args:
            disk_analysis: Disk analysis dictionary

        Returns:
            List of violations
        """
        violations = []
        disk_thresholds = self.thresholds.get('disk', {})

        for mountpoint, stats in disk_analysis.items():
            usage_stats = stats.get('usage_percent', {})
            avg_usage = usage_stats.get('mean')
            max_usage = usage_stats.get('max')

            if not avg_usage:
                continue

            # Check critical threshold
            critical = disk_thresholds.get('critical', {})
            if avg_usage >= critical.get('usage', 100):
                violations.append({
                    'metric': f'Disk Usage ({mountpoint})',
                    'value': avg_usage,
                    'threshold': critical['usage'],
                    'severity': 'critical',
                    'message': f"Disk usage for {mountpoint} ({avg_usage:.1f}%) exceeds critical threshold ({critical['usage']}%)"
                })

            # Check warning threshold
            warning = disk_thresholds.get('warning', {})
            if avg_usage >= warning.get('usage', 100):
                violations.append({
                    'metric': f'Disk Usage ({mountpoint})',
                    'value': avg_usage,
                    'threshold': warning['usage'],
                    'severity': 'warning',
                    'message': f"Disk usage for {mountpoint} ({avg_usage:.1f}%) exceeds warning threshold ({warning['usage']}%)"
                })

        return violations

    def _check_log_thresholds(self, log_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check log metrics against thresholds.

        Args:
            log_analysis: Log analysis dictionary

        Returns:
            List of violations
        """
        violations = []
        log_thresholds = self.thresholds.get('logs', {})

        summary = log_analysis.get('summary', {})
        total_errors = summary.get('total_errors', 0)

        kernel_errors = log_analysis.get('kernel_log', {}).get('error_count', 0)

        # Check critical thresholds
        critical = log_thresholds.get('critical', {})
        if total_errors >= critical.get('error_count', float('inf')):
            violations.append({
                'metric': 'Total Log Errors',
                'value': total_errors,
                'threshold': critical['error_count'],
                'severity': 'critical',
                'message': f"Total log errors ({total_errors}) exceeds critical threshold ({critical['error_count']})"
            })

        if kernel_errors >= critical.get('kernel_errors', float('inf')):
            violations.append({
                'metric': 'Kernel Errors',
                'value': kernel_errors,
                'threshold': critical['kernel_errors'],
                'severity': 'critical',
                'message': f"Kernel errors ({kernel_errors}) exceeds critical threshold ({critical['kernel_errors']})"
            })

        # Check warning thresholds
        warning = log_thresholds.get('warning', {})
        if total_errors >= warning.get('error_count', float('inf')):
            violations.append({
                'metric': 'Total Log Errors',
                'value': total_errors,
                'threshold': warning['error_count'],
                'severity': 'warning',
                'message': f"Total log errors ({total_errors}) exceeds warning threshold ({warning['error_count']})"
            })

        return violations

    def get_severity_summary(self, violations: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Get summary of violations by severity.

        Args:
            violations: List of violations

        Returns:
            Dictionary with counts by severity
        """
        summary = {
            'critical': 0,
            'warning': 0,
            'total': len(violations)
        }

        for violation in violations:
            severity = violation.get('severity', 'warning')
            if severity in summary:
                summary[severity] += 1

        return summary
