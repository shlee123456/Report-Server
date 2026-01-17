"""
Recommendation engine for generating improvement suggestions.
"""
from typing import Dict, List, Any
import logging


class RecommendationEngine:
    """Generate recommendations based on metrics analysis and violations."""

    def __init__(self):
        """Initialize recommendation engine."""
        self.logger = logging.getLogger('monitoring_system')

    def generate_recommendations(
        self,
        analysis: Dict[str, Any],
        violations: List[Dict[str, Any]],
        log_analysis: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on analysis and violations.

        Args:
            analysis: Metrics analysis dictionary
            violations: List of threshold violations
            log_analysis: Log analysis results (optional)

        Returns:
            List of recommendations with priority
        """
        recommendations = []

        # Generate recommendations based on violations
        recommendations.extend(self._recommendations_from_violations(violations))

        # Generate recommendations based on trends
        recommendations.extend(self._recommendations_from_trends(analysis))

        # Generate recommendations based on log analysis
        if log_analysis:
            recommendations.extend(self._recommendations_from_logs(log_analysis))

        # Deduplicate and prioritize recommendations
        recommendations = self._prioritize_recommendations(recommendations)

        self.logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations

    def _recommendations_from_violations(self, violations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate recommendations from threshold violations.

        Args:
            violations: List of violations

        Returns:
            List of recommendations
        """
        recommendations = []

        for violation in violations:
            metric = violation.get('metric', '')
            severity = violation.get('severity', 'warning')

            if 'CPU' in metric:
                recommendations.append({
                    'category': 'CPU',
                    'priority': 'high' if severity == 'critical' else 'medium',
                    'title': 'High CPU Usage Detected',
                    'description': violation.get('message', ''),
                    'actions': [
                        'Identify CPU-intensive processes using top or htop',
                        'Consider optimizing or limiting resource-heavy applications',
                        'Review cron jobs and scheduled tasks',
                        'Consider upgrading CPU or adding more cores if sustained high usage'
                    ]
                })

            elif 'RAM' in metric:
                recommendations.append({
                    'category': 'Memory',
                    'priority': 'high' if severity == 'critical' else 'medium',
                    'title': 'High Memory Usage Detected',
                    'description': violation.get('message', ''),
                    'actions': [
                        'Identify memory-intensive processes using top or htop',
                        'Check for memory leaks in applications',
                        'Review and optimize application configurations',
                        'Consider adding more RAM if consistently high usage',
                        'Enable or tune swap if not already configured'
                    ]
                })

            elif 'SWAP' in metric:
                recommendations.append({
                    'category': 'Memory',
                    'priority': 'high' if severity == 'critical' else 'medium',
                    'title': 'High SWAP Usage Detected',
                    'description': violation.get('message', ''),
                    'actions': [
                        'High swap usage indicates RAM pressure',
                        'Increase physical RAM to reduce swap dependency',
                        'Review memory-intensive applications',
                        'Consider adjusting swappiness value (default: 60)'
                    ]
                })

            elif 'Disk' in metric:
                recommendations.append({
                    'category': 'Disk',
                    'priority': 'high' if severity == 'critical' else 'medium',
                    'title': 'High Disk Usage Detected',
                    'description': violation.get('message', ''),
                    'actions': [
                        'Clean up old log files and temporary files',
                        'Review and optimize log rotation policies',
                        'Use ncdu or du to identify large files and directories',
                        'Consider expanding disk space or adding new volumes',
                        'Archive or delete old backups and snapshots'
                    ]
                })

            elif 'Log Errors' in metric:
                recommendations.append({
                    'category': 'Logs',
                    'priority': 'high' if severity == 'critical' else 'medium',
                    'title': 'High Error Count in Logs',
                    'description': violation.get('message', ''),
                    'actions': [
                        'Review system logs for recurring error patterns',
                        'Address underlying issues causing errors',
                        'Monitor application health and stability',
                        'Consider setting up automated alerting for critical errors'
                    ]
                })

            elif 'Kernel' in metric:
                recommendations.append({
                    'category': 'System',
                    'priority': 'critical',
                    'title': 'Kernel Errors Detected',
                    'description': violation.get('message', ''),
                    'actions': [
                        'Review kernel logs for hardware issues',
                        'Check system memory and disk health',
                        'Update system firmware and drivers',
                        'Consider running hardware diagnostics',
                        'Monitor for signs of failing hardware'
                    ]
                })

        return recommendations

    def _recommendations_from_trends(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on metric trends.

        Args:
            analysis: Metrics analysis dictionary

        Returns:
            List of recommendations
        """
        recommendations = []

        # CPU trend recommendations
        cpu = analysis.get('cpu', {})
        if cpu.get('trend') == 'increasing':
            avg_usage = cpu.get('usage', {}).get('mean', 0)
            if avg_usage > 50:
                recommendations.append({
                    'category': 'CPU',
                    'priority': 'medium',
                    'title': 'Increasing CPU Usage Trend',
                    'description': f'CPU usage is trending upward (average: {avg_usage:.1f}%)',
                    'actions': [
                        'Monitor CPU usage closely over the next month',
                        'Identify processes contributing to increased usage',
                        'Plan for capacity upgrade if trend continues'
                    ]
                })

        # Memory trend recommendations
        memory = analysis.get('memory', {})
        ram_trend = memory.get('ram', {}).get('trend')
        if ram_trend == 'increasing':
            avg_ram = memory.get('ram', {}).get('usage_percent', {}).get('mean', 0)
            if avg_ram > 60:
                recommendations.append({
                    'category': 'Memory',
                    'priority': 'medium',
                    'title': 'Increasing Memory Usage Trend',
                    'description': f'Memory usage is trending upward (average: {avg_ram:.1f}%)',
                    'actions': [
                        'Investigate potential memory leaks',
                        'Monitor memory usage patterns',
                        'Plan for RAM upgrade if trend continues',
                        'Review application memory configurations'
                    ]
                })

        # Disk trend recommendations
        disk = analysis.get('disk', {})
        for mountpoint, stats in disk.items():
            if stats.get('trend') == 'increasing':
                avg_usage = stats.get('usage_percent', {}).get('mean', 0)
                if avg_usage > 60:
                    recommendations.append({
                        'category': 'Disk',
                        'priority': 'medium',
                        'title': f'Increasing Disk Usage Trend ({mountpoint})',
                        'description': f'Disk usage for {mountpoint} is trending upward (average: {avg_usage:.1f}%)',
                        'actions': [
                            f'Monitor disk usage on {mountpoint}',
                            'Implement or review log rotation policies',
                            'Plan for storage expansion if needed',
                            'Consider archiving old data'
                        ]
                    })

        return recommendations

    def _recommendations_from_logs(self, log_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on log analysis.

        Args:
            log_analysis: Log analysis dictionary

        Returns:
            List of recommendations
        """
        recommendations = []

        # Security event recommendations
        auth_log = log_analysis.get('auth_log', {})
        security_events = auth_log.get('security_events', 0)

        if security_events > 10:
            recommendations.append({
                'category': 'Security',
                'priority': 'high',
                'title': 'Multiple Security Events Detected',
                'description': f'Found {security_events} security-related events in authentication logs',
                'actions': [
                    'Review authentication logs for suspicious activity',
                    'Consider implementing fail2ban to block repeated login attempts',
                    'Strengthen SSH security (disable root login, use key-based auth)',
                    'Review user access and permissions',
                    'Enable and configure firewall (ufw or iptables)'
                ]
            })

        # Kernel error recommendations
        kernel_log = log_analysis.get('kernel_log', {})
        kernel_errors = kernel_log.get('error_count', 0)

        if kernel_errors > 5:
            recommendations.append({
                'category': 'System',
                'priority': 'critical',
                'title': 'Kernel Errors Require Attention',
                'description': f'Found {kernel_errors} kernel errors',
                'actions': [
                    'Review kernel logs immediately for hardware issues',
                    'Check system stability and uptime',
                    'Run hardware diagnostics',
                    'Update kernel to latest stable version',
                    'Monitor system for crashes or freezes'
                ]
            })

        return recommendations

    def _prioritize_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicate and prioritize recommendations.

        Args:
            recommendations: List of recommendations

        Returns:
            Sorted and deduplicated list
        """
        # Remove duplicates based on title
        seen_titles = set()
        unique_recommendations = []

        for rec in recommendations:
            title = rec.get('title', '')
            if title not in seen_titles:
                seen_titles.add(title)
                unique_recommendations.append(rec)

        # Sort by priority: critical > high > medium > low
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}

        sorted_recommendations = sorted(
            unique_recommendations,
            key=lambda x: priority_order.get(x.get('priority', 'low'), 3)
        )

        return sorted_recommendations

    def get_top_recommendations(self, recommendations: List[Dict[str, Any]], count: int = 3) -> List[Dict[str, Any]]:
        """
        Get top N recommendations.

        Args:
            recommendations: List of all recommendations
            count: Number of top recommendations to return

        Returns:
            Top N recommendations
        """
        return recommendations[:count]
