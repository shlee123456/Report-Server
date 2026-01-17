"""
Recommendation engine for generating improvement suggestions.
한글 권장 사항 메시지 적용
"""
from typing import Dict, List, Any
import logging


class RecommendationEngine:
    """Generate recommendations based on metrics analysis and violations (Korean)."""

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
        Generate recommendations from threshold violations (Korean).

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
                    'title': 'CPU 사용량 높음',
                    'description': violation.get('message', 'CPU 사용률이 임계값을 초과했습니다.'),
                    'actions': [
                        'top 또는 htop 명령으로 CPU 집중 사용 프로세스 확인',
                        '리소스를 많이 사용하는 애플리케이션 최적화 또는 제한 검토',
                        '예약된 cron 작업 및 배치 작업 검토',
                        '지속적인 고사용량 시 CPU 업그레이드 또는 코어 추가 고려'
                    ]
                })

            elif 'RAM' in metric:
                recommendations.append({
                    'category': '메모리',
                    'priority': 'high' if severity == 'critical' else 'medium',
                    'title': '메모리 사용량 높음',
                    'description': violation.get('message', 'RAM 사용률이 임계값을 초과했습니다.'),
                    'actions': [
                        'top 또는 htop 명령으로 메모리 집중 사용 프로세스 확인',
                        '애플리케이션의 메모리 누수 점검',
                        '애플리케이션 설정 검토 및 최적화',
                        '지속적인 고사용량 시 RAM 추가 고려',
                        'SWAP이 설정되지 않았다면 활성화 검토'
                    ]
                })

            elif 'SWAP' in metric:
                recommendations.append({
                    'category': '메모리',
                    'priority': 'high' if severity == 'critical' else 'medium',
                    'title': 'SWAP 사용량 높음',
                    'description': violation.get('message', 'SWAP 사용률이 임계값을 초과했습니다.'),
                    'actions': [
                        'SWAP 사용량 증가는 RAM 부족을 의미합니다',
                        '물리적 RAM 증설을 통해 SWAP 의존도 감소',
                        '메모리 집중 사용 애플리케이션 검토',
                        'swappiness 값 조정 고려 (기본값: 60)'
                    ]
                })

            elif 'Disk' in metric:
                recommendations.append({
                    'category': '디스크',
                    'priority': 'high' if severity == 'critical' else 'medium',
                    'title': '디스크 사용량 높음',
                    'description': violation.get('message', '디스크 사용률이 임계값을 초과했습니다.'),
                    'actions': [
                        '오래된 로그 파일 및 임시 파일 정리',
                        '로그 로테이션 정책 검토 및 최적화',
                        'ncdu 또는 du 명령으로 대용량 파일/디렉토리 확인',
                        '디스크 용량 확장 또는 새 볼륨 추가 고려',
                        '오래된 백업 및 스냅샷 아카이브 또는 삭제'
                    ]
                })

            elif 'Log Errors' in metric:
                recommendations.append({
                    'category': '로그',
                    'priority': 'high' if severity == 'critical' else 'medium',
                    'title': '로그 오류 다수 발생',
                    'description': violation.get('message', '시스템 로그에서 많은 오류가 감지되었습니다.'),
                    'actions': [
                        '반복되는 오류 패턴에 대한 시스템 로그 검토',
                        '오류를 유발하는 근본 원인 해결',
                        '애플리케이션 상태 및 안정성 모니터링',
                        '중요 오류에 대한 자동 알림 설정 고려'
                    ]
                })

            elif 'Kernel' in metric:
                recommendations.append({
                    'category': '시스템',
                    'priority': 'critical',
                    'title': '커널 오류 감지',
                    'description': violation.get('message', '커널 수준의 오류가 감지되었습니다.'),
                    'actions': [
                        '하드웨어 문제에 대한 커널 로그 즉시 검토',
                        '시스템 메모리 및 디스크 상태 점검',
                        '시스템 펌웨어 및 드라이버 업데이트',
                        '하드웨어 진단 도구 실행 고려',
                        '하드웨어 장애 징후 지속적 모니터링'
                    ]
                })

        return recommendations

    def _recommendations_from_trends(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on metric trends (Korean).

        Args:
            analysis: Metrics analysis dictionary

        Returns:
            List of recommendations
        """
        recommendations = []

        # CPU 추세 권장사항
        cpu = analysis.get('cpu', {})
        if cpu.get('trend') == 'increasing':
            avg_usage = cpu.get('usage', {}).get('mean', 0)
            if avg_usage > 50:
                recommendations.append({
                    'category': 'CPU',
                    'priority': 'medium',
                    'title': 'CPU 사용량 증가 추세',
                    'description': f'CPU 사용량이 지속적으로 증가하고 있습니다 (평균: {avg_usage:.1f}%)',
                    'actions': [
                        '다음 달까지 CPU 사용량 추이 면밀히 모니터링',
                        '사용량 증가에 기여하는 프로세스 식별',
                        '추세가 지속될 경우 용량 업그레이드 계획 수립'
                    ]
                })

        # 메모리 추세 권장사항
        memory = analysis.get('memory', {})
        ram_trend = memory.get('ram', {}).get('trend')
        if ram_trend == 'increasing':
            avg_ram = memory.get('ram', {}).get('usage_percent', {}).get('mean', 0)
            if avg_ram > 60:
                recommendations.append({
                    'category': '메모리',
                    'priority': 'medium',
                    'title': '메모리 사용량 증가 추세',
                    'description': f'메모리 사용량이 지속적으로 증가하고 있습니다 (평균: {avg_ram:.1f}%)',
                    'actions': [
                        '잠재적인 메모리 누수 조사',
                        '메모리 사용 패턴 모니터링',
                        '추세가 지속될 경우 RAM 업그레이드 계획 수립',
                        '애플리케이션 메모리 설정 검토'
                    ]
                })

        # 디스크 추세 권장사항
        disk = analysis.get('disk', {})
        for mountpoint, stats in disk.items():
            if stats.get('trend') == 'increasing':
                avg_usage = stats.get('usage_percent', {}).get('mean', 0)
                if avg_usage > 60:
                    recommendations.append({
                        'category': '디스크',
                        'priority': 'medium',
                        'title': f'디스크 사용량 증가 추세 ({mountpoint})',
                        'description': f'{mountpoint} 디스크 사용량이 지속적으로 증가하고 있습니다 (평균: {avg_usage:.1f}%)',
                        'actions': [
                            f'{mountpoint} 디스크 사용량 모니터링',
                            '로그 로테이션 정책 구현 또는 검토',
                            '필요시 스토리지 확장 계획 수립',
                            '오래된 데이터 아카이브 고려'
                        ]
                    })

        return recommendations

    def _recommendations_from_logs(self, log_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on log analysis (Korean).

        Args:
            log_analysis: Log analysis dictionary

        Returns:
            List of recommendations
        """
        recommendations = []

        # 보안 이벤트 권장사항
        auth_log = log_analysis.get('auth_log', {})
        security_events = auth_log.get('security_events', 0)

        if security_events > 10:
            recommendations.append({
                'category': '보안',
                'priority': 'high',
                'title': '다수의 보안 이벤트 감지',
                'description': f'인증 로그에서 {security_events}건의 보안 관련 이벤트가 발견되었습니다',
                'actions': [
                    '의심스러운 활동에 대한 인증 로그 검토',
                    '반복적인 로그인 시도 차단을 위해 fail2ban 구현 고려',
                    'SSH 보안 강화 (root 로그인 비활성화, 키 기반 인증 사용)',
                    '사용자 접근 권한 검토',
                    '방화벽 활성화 및 구성 (ufw 또는 iptables)'
                ]
            })

        # 커널 오류 권장사항
        kernel_log = log_analysis.get('kernel_log', {})
        kernel_errors = kernel_log.get('error_count', 0)

        if kernel_errors > 5:
            recommendations.append({
                'category': '시스템',
                'priority': 'critical',
                'title': '커널 오류 주의 필요',
                'description': f'{kernel_errors}건의 커널 오류가 발견되었습니다',
                'actions': [
                    '하드웨어 문제에 대한 커널 로그 즉시 검토',
                    '시스템 안정성 및 가동 시간 확인',
                    '하드웨어 진단 도구 실행',
                    '커널을 최신 안정 버전으로 업데이트',
                    '시스템 충돌 또는 프리즈 모니터링'
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
        # 제목 기준 중복 제거
        seen_titles = set()
        unique_recommendations = []

        for rec in recommendations:
            title = rec.get('title', '')
            if title not in seen_titles:
                seen_titles.add(title)
                unique_recommendations.append(rec)

        # 우선순위 정렬: critical > high > medium > low
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
