"""
Table builder module for formatting data tables.
한글 헤더 및 레이블 적용
"""
from typing import List, Dict, Any, Tuple
import logging


class TableBuilder:
    """Build formatted tables for PDF reports with Korean labels."""

    # 추세 한글 변환
    TREND_LABELS = {
        'increasing': '📈 증가',
        'decreasing': '📉 감소',
        'stable': '➡️ 안정',
    }

    def __init__(self):
        """Initialize table builder."""
        self.logger = logging.getLogger('monitoring_system')

    def build_summary_table(self, summary: Dict[str, Any]) -> List[List[str]]:
        """
        Build summary statistics table with horizontal layout for better readability.

        Args:
            summary: Summary statistics dictionary

        Returns:
            Table data as list of rows (horizontal layout)
        """
        # 수집 기간
        period = summary.get('collection_period', {})
        days = period.get('days_collected', 'N/A')

        # CPU 요약
        cpu = summary.get('cpu_summary', {})
        avg_cpu = cpu.get('avg_usage', 0) if cpu else 0
        max_cpu = cpu.get('max_usage', 0) if cpu else 0
        cpu_trend = cpu.get('trend', 'stable') if cpu else 'stable'

        # 메모리 요약
        memory = summary.get('memory_summary', {})
        avg_ram = memory.get('avg_ram_usage', 0) if memory else 0
        max_ram = memory.get('max_ram_usage', 0) if memory else 0
        mem_trend = memory.get('trend', 'stable') if memory else 'stable'

        # 디스크 요약
        disk = summary.get('disk_summary', {})
        avg_disk = disk.get('avg_usage', 0) if disk else 0
        max_disk = disk.get('max_usage', 0) if disk else 0
        disk_trend = disk.get('trend', 'stable') if disk else 'stable'

        # 가로 레이아웃 테이블
        table_data = [
            ['📊 항목', '🖥️ CPU', '💾 메모리', '💿 디스크'],
            ['평균 사용률', f'{avg_cpu:.1f}%', f'{avg_ram:.1f}%', f'{avg_disk:.1f}%'],
            ['최대 사용률', f'{max_cpu:.1f}%', f'{max_ram:.1f}%', f'{max_disk:.1f}%'],
            ['추세', 
             self.TREND_LABELS.get(cpu_trend, '➡️ 안정'),
             self.TREND_LABELS.get(mem_trend, '➡️ 안정'),
             self.TREND_LABELS.get(disk_trend, '➡️ 안정')],
        ]

        return table_data

    def build_cpu_stats_table(self, cpu_analysis: Dict[str, Any]) -> List[List[str]]:
        """
        Build CPU statistics table with Korean headers.

        Args:
            cpu_analysis: CPU analysis dictionary

        Returns:
            Table data as list of rows
        """
        table_data = [
            ['📊 통계', '📈 값']
        ]

        usage = cpu_analysis.get('usage', {})
        if usage:
            if usage.get('min') is not None:
                table_data.append(['최소값', f"{usage['min']:.2f}%"])
            if usage.get('max') is not None:
                table_data.append(['최대값', f"{usage['max']:.2f}%"])
            if usage.get('mean') is not None:
                table_data.append(['평균값', f"{usage['mean']:.2f}%"])
            if usage.get('median') is not None:
                table_data.append(['중앙값', f"{usage['median']:.2f}%"])
            if usage.get('std') is not None:
                table_data.append(['표준편차', f"{usage['std']:.2f}%"])

        # 로드 평균
        load_avg = cpu_analysis.get('load_average', {})
        load_1m = load_avg.get('1min', {})
        if load_1m and load_1m.get('mean') is not None:
            table_data.append(['평균 로드 (1분)', f"{load_1m['mean']:.2f}"])

        return table_data

    def build_memory_stats_table(self, memory_analysis: Dict[str, Any]) -> List[List[str]]:
        """
        Build memory statistics table with Korean headers.

        Args:
            memory_analysis: Memory analysis dictionary

        Returns:
            Table data as list of rows
        """
        table_data = [
            ['💾 항목', '📉 최소', '📈 최대', '📊 평균']
        ]

        # RAM 통계
        ram = memory_analysis.get('ram', {}).get('usage_percent', {})
        if ram:
            table_data.append([
                'RAM 사용률',
                f"{ram.get('min', 0):.1f}%",
                f"{ram.get('max', 0):.1f}%",
                f"{ram.get('mean', 0):.1f}%"
            ])

        # SWAP 통계
        swap = memory_analysis.get('swap', {}).get('usage_percent', {})
        if swap:
            table_data.append([
                'SWAP 사용률',
                f"{swap.get('min', 0):.1f}%",
                f"{swap.get('max', 0):.1f}%",
                f"{swap.get('mean', 0):.1f}%"
            ])

        return table_data

    def build_disk_stats_table(self, disk_analysis: Dict[str, Any]) -> List[List[str]]:
        """
        Build disk statistics table with Korean headers.

        Args:
            disk_analysis: Disk analysis dictionary

        Returns:
            Table data as list of rows
        """
        table_data = [
            ['💿 마운트', '🔧 장치', '📁 타입', '📊 평균', '📈 최대', '📉 추세']
        ]

        for mountpoint, stats in disk_analysis.items():
            device = stats.get('device', 'N/A')
            fstype = stats.get('fstype', 'N/A')
            usage_percent = stats.get('usage_percent', {})
            trend = stats.get('trend', 'stable')
            trend_label = self.TREND_LABELS.get(trend, trend)

            avg_usage = usage_percent.get('mean')
            max_usage = usage_percent.get('max')

            # 마운트포인트 간소화
            display_mount = mountpoint if len(mountpoint) <= 12 else '...' + mountpoint[-9:]

            table_data.append([
                display_mount,
                device,
                fstype,
                f"{avg_usage:.1f}%" if avg_usage is not None else 'N/A',
                f"{max_usage:.1f}%" if max_usage is not None else 'N/A',
                trend_label
            ])

        return table_data

    def build_violations_table(self, violations: List[Dict[str, Any]]) -> List[List[str]]:
        """
        Build threshold violations table with Korean headers.

        Args:
            violations: List of violations

        Returns:
            Table data as list of rows
        """
        table_data = [
            ['⚠️ 지표', '📈 값', '🎯 임계값', '🚨 심각도']
        ]

        severity_labels = {
            'critical': '🔴 긴급',
            'warning': '🟡 경고',
        }

        for violation in violations:
            metric = violation.get('metric', 'N/A')
            value = violation.get('value', 'N/A')
            threshold = violation.get('threshold', 'N/A')
            severity = violation.get('severity', 'warning')

            # 값 포맷
            if isinstance(value, (int, float)):
                value_str = f"{value:.1f}"
            else:
                value_str = str(value)

            severity_label = severity_labels.get(severity, severity)

            table_data.append([
                metric,
                value_str,
                str(threshold),
                severity_label
            ])

        if len(table_data) == 1:
            table_data.append(['✅ 위반 사항 없음', '-', '-', '-'])

        return table_data

    def build_log_summary_table(self, log_analysis: Dict[str, Any]) -> List[List[str]]:
        """
        Build log analysis summary table with Korean headers.

        Args:
            log_analysis: Log analysis dictionary

        Returns:
            Table data as list of rows
        """
        table_data = [
            ['📝 로그 소스', '🔴 오류', '🟡 경고', '📊 합계']
        ]

        # 시스템 로그
        syslog = log_analysis.get('syslog', {})
        syslog_errors = syslog.get('error_count', 0)
        syslog_warnings = syslog.get('warning_count', 0)
        table_data.append([
            '시스템 로그',
            str(syslog_errors),
            str(syslog_warnings),
            str(syslog_errors + syslog_warnings)
        ])

        # 인증 로그
        auth_log = log_analysis.get('auth_log', {})
        auth_errors = auth_log.get('error_count', 0)
        auth_warnings = auth_log.get('warning_count', 0)
        security_events = auth_log.get('security_events', 0)
        table_data.append([
            '인증 로그',
            str(auth_errors),
            str(auth_warnings),
            str(security_events)
        ])

        # 커널 로그
        kernel_log = log_analysis.get('kernel_log', {})
        kernel_errors = kernel_log.get('error_count', 0)
        table_data.append([
            '커널 로그',
            str(kernel_errors),
            '-',
            str(kernel_errors)
        ])

        # 합계
        summary = log_analysis.get('summary', {})
        table_data.append([
            '📊 합계',
            str(summary.get('total_errors', 0)),
            str(summary.get('total_warnings', 0)),
            str(summary.get('total_events', 0))
        ])

        return table_data

    def build_recommendations_table(self, recommendations: List[Dict[str, Any]]) -> List[List[str]]:
        """
        Build recommendations table with Korean headers.

        Args:
            recommendations: List of recommendations

        Returns:
            Table data as list of rows
        """
        table_data = [
            ['🚨 우선순위', '📁 분류', '📋 제목']
        ]

        priority_labels = {
            'CRITICAL': '🔴 긴급',
            'HIGH': '🟠 높음',
            'MEDIUM': '🟡 보통',
            'LOW': '🟢 낮음',
        }

        for rec in recommendations:
            priority = rec.get('priority', 'N/A').upper()
            category = rec.get('category', 'N/A')
            title = rec.get('title', 'N/A')

            priority_label = priority_labels.get(priority, priority)

            table_data.append([priority_label, category, title])

        if len(table_data) == 1:
            table_data.append(['✅ 없음', '-', '권장 사항이 없습니다'])

        return table_data

    def build_daily_usage_table(self, metrics_list: List[Dict[str, Any]]) -> List[List[str]]:
        """
        Build daily usage table with CPU and memory statistics.

        Args:
            metrics_list: List of daily metrics dictionaries

        Returns:
            Table data as list of rows
        """
        table_data = [
            ['기간', 'CPU 평균[%]', 'CPU 최고[%]', 'MEM 평균[%]', 'MEM 최대[%]', 'MEM 평균[KB]', 'MEM 최대[KB]']
        ]

        for metrics in metrics_list:
            # 날짜 파싱
            timestamp = metrics.get('timestamp', '')
            if timestamp:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp)
                    date_str = dt.strftime('%Y.%m.%d')
                except Exception:
                    date_str = timestamp.split('T')[0] if 'T' in timestamp else timestamp
            else:
                date_str = 'N/A'

            # CPU 데이터
            cpu_data = metrics.get('cpu', {})
            cpu_usage = cpu_data.get('usage_percent', 0)
            # CPU 최고값은 수집된 순간의 값을 사용 (일별 데이터이므로)
            cpu_max = cpu_usage

            # 메모리 데이터
            memory_data = metrics.get('memory', {})
            ram_data = memory_data.get('ram', {})
            ram_percent = ram_data.get('percent', 0)
            ram_used = ram_data.get('used', 0)

            # 메모리 KB 단위로 변환
            ram_used_kb = ram_used / 1024 if ram_used else 0

            table_data.append([
                date_str,
                f'{cpu_usage:.2f}' if cpu_usage else '0.00',
                f'{cpu_max:.2f}' if cpu_max else '0.00',
                f'{ram_percent:.2f}' if ram_percent else '0.00',
                f'{ram_percent:.2f}' if ram_percent else '0.00',  # 최대값도 동일 (일별 데이터)
                f'{ram_used_kb:,.0f}',
                f'{ram_used_kb:,.0f}'  # 최대값도 동일 (일별 데이터)
            ])

        if len(table_data) == 1:
            table_data.append(['데이터 없음', '-', '-', '-', '-', '-', '-'])

        return table_data

    def format_bytes(self, bytes_value: int) -> str:
        """
        Format bytes to human-readable format (Korean).

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
