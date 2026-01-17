"""
Log analysis module for parsing system logs.
"""
import re
import os
import subprocess
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict
import logging


class LogAnalyzer:
    """Analyze system logs for errors and warnings."""

    def __init__(self, log_paths: Dict[str, str], log_patterns: Dict[str, Any]):
        """
        Initialize log analyzer.

        Args:
            log_paths: Dictionary of log file paths
            log_patterns: Dictionary of log patterns to search for
        """
        self.log_paths = log_paths
        self.log_patterns = log_patterns
        self.logger = logging.getLogger('monitoring_system')

    def analyze_all_logs(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """
        Analyze all configured log files.

        Args:
            start_date: Start date for log analysis (optional)
            end_date: End date for log analysis (optional)

        Returns:
            Dictionary containing log analysis results
        """
        self.logger.info("Starting log analysis")

        results = {
            'timestamp': datetime.now().isoformat(),
            'syslog': self.analyze_syslog(),
            'auth_log': self.analyze_auth_log(),
            'kernel_log': self.analyze_kernel_log(),
            'summary': {}
        }

        # Calculate summary statistics
        total_errors = sum(r.get('error_count', 0) for r in results.values() if isinstance(r, dict))
        total_warnings = sum(r.get('warning_count', 0) for r in results.values() if isinstance(r, dict))

        results['summary'] = {
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'total_events': total_errors + total_warnings
        }

        self.logger.info(f"Log analysis completed: {total_errors} errors, {total_warnings} warnings")
        return results

    def analyze_syslog(self) -> Dict[str, Any]:
        """
        Analyze syslog for errors and warnings.

        Returns:
            Dictionary containing syslog analysis results
        """
        log_path = self.log_paths.get('syslog')
        if not log_path or not os.path.exists(log_path):
            self.logger.warning(f"Syslog not found: {log_path}")
            return {'error': 'Log file not found', 'error_count': 0, 'warning_count': 0}

        try:
            patterns = self.log_patterns.get('syslog', {})
            error_patterns = patterns.get('error_patterns', [])
            warning_patterns = patterns.get('warning_patterns', [])

            errors = self._search_patterns(log_path, error_patterns)
            warnings = self._search_patterns(log_path, warning_patterns)

            return {
                'error_count': len(errors),
                'warning_count': len(warnings),
                'errors': errors[:10],  # Top 10 errors
                'warnings': warnings[:10]  # Top 10 warnings
            }

        except Exception as e:
            self.logger.error(f"Error analyzing syslog: {e}")
            return {'error': str(e), 'error_count': 0, 'warning_count': 0}

    def analyze_auth_log(self) -> Dict[str, Any]:
        """
        Analyze auth.log for security events.

        Returns:
            Dictionary containing auth log analysis results
        """
        log_path = self.log_paths.get('auth_log')
        if not log_path or not os.path.exists(log_path):
            self.logger.warning(f"Auth log not found: {log_path}")
            return {'error': 'Log file not found', 'security_events': 0}

        try:
            patterns = self.log_patterns.get('auth_log', {}).get('security_events', [])

            security_events = []
            event_counts = defaultdict(int)

            for pattern_config in patterns:
                pattern = pattern_config.get('regex')
                severity = pattern_config.get('severity', 'warning')

                matches = self._search_patterns(log_path, [pattern_config])

                for match in matches:
                    security_events.append({
                        'severity': severity,
                        'message': match['message'],
                        'timestamp': match.get('timestamp', 'Unknown')
                    })
                    event_counts[severity] += 1

            return {
                'security_events': len(security_events),
                'event_counts': dict(event_counts),
                'recent_events': security_events[:10],  # Top 10 recent events
                'error_count': event_counts.get('critical', 0),
                'warning_count': event_counts.get('warning', 0)
            }

        except Exception as e:
            self.logger.error(f"Error analyzing auth log: {e}")
            return {'error': str(e), 'security_events': 0}

    def analyze_kernel_log(self) -> Dict[str, Any]:
        """
        Analyze kernel log and dmesg for hardware errors.

        Returns:
            Dictionary containing kernel log analysis results
        """
        # Try to read kern.log
        log_path = self.log_paths.get('kern_log')
        kern_errors = []

        if log_path and os.path.exists(log_path):
            try:
                patterns = self.log_patterns.get('kernel_log', {}).get('hardware_errors', [])
                kern_errors = self._search_patterns(log_path, patterns)
            except Exception as e:
                self.logger.warning(f"Error reading kern.log: {e}")

        # Also check dmesg
        dmesg_errors = []
        try:
            dmesg_cmd = self.log_paths.get('dmesg_command', '/usr/bin/dmesg')
            if os.path.exists(dmesg_cmd):
                result = subprocess.run(
                    [dmesg_cmd],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    dmesg_output = result.stdout
                    patterns = self.log_patterns.get('kernel_log', {}).get('hardware_errors', [])
                    dmesg_errors = self._search_patterns_in_text(dmesg_output, patterns)
        except Exception as e:
            self.logger.warning(f"Error running dmesg: {e}")

        all_errors = kern_errors + dmesg_errors

        return {
            'error_count': len(all_errors),
            'hardware_errors': all_errors[:10],  # Top 10 errors
            'sources': {
                'kern_log': len(kern_errors),
                'dmesg': len(dmesg_errors)
            }
        }

    def _search_patterns(self, log_path: str, patterns: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Search for patterns in a log file.

        Args:
            log_path: Path to log file
            patterns: List of pattern configurations

        Returns:
            List of matching log entries
        """
        matches = []

        try:
            with open(log_path, 'r', errors='ignore') as f:
                lines = f.readlines()

            for pattern_config in patterns:
                if isinstance(pattern_config, dict):
                    pattern = pattern_config.get('regex')
                    case_sensitive = pattern_config.get('case_sensitive', True)
                else:
                    pattern = pattern_config
                    case_sensitive = True

                flags = 0 if case_sensitive else re.IGNORECASE
                compiled_pattern = re.compile(pattern, flags)

                for line in lines:
                    if compiled_pattern.search(line):
                        matches.append({
                            'message': line.strip(),
                            'timestamp': self._extract_timestamp(line)
                        })

        except PermissionError:
            self.logger.error(f"Permission denied reading {log_path}. Add user to 'adm' group.")
        except Exception as e:
            self.logger.error(f"Error searching patterns in {log_path}: {e}")

        return matches

    def _search_patterns_in_text(self, text: str, patterns: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Search for patterns in text content.

        Args:
            text: Text content to search
            patterns: List of pattern configurations

        Returns:
            List of matching entries
        """
        matches = []
        lines = text.split('\n')

        for pattern_config in patterns:
            if isinstance(pattern_config, dict):
                pattern = pattern_config.get('regex')
                case_sensitive = pattern_config.get('case_sensitive', True)
            else:
                pattern = pattern_config
                case_sensitive = True

            flags = 0 if case_sensitive else re.IGNORECASE
            compiled_pattern = re.compile(pattern, flags)

            for line in lines:
                if compiled_pattern.search(line):
                    matches.append({
                        'message': line.strip(),
                        'timestamp': self._extract_timestamp(line)
                    })

        return matches

    def _extract_timestamp(self, log_line: str) -> str:
        """
        Extract timestamp from log line.

        Args:
            log_line: Log line text

        Returns:
            Extracted timestamp or 'Unknown'
        """
        # Try to match common timestamp formats
        timestamp_patterns = [
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',  # ISO format
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',  # YYYY-MM-DD HH:MM:SS
            r'[A-Z][a-z]{2}\s+\d{1,2} \d{2}:\d{2}:\d{2}',  # Mon DD HH:MM:SS
        ]

        for pattern in timestamp_patterns:
            match = re.search(pattern, log_line)
            if match:
                return match.group(0)

        return 'Unknown'
