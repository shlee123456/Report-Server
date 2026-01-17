# Ubuntu 서버 월간 모니터링 & PDF 리포트 시스템

Ubuntu 서버의 시스템 메트릭(CPU, 메모리, 디스크)을 자동으로 수집하고, 로그를 분석하여 차트, 통계, 권장 조치 사항이 포함된 월간 PDF 보고서를 생성하는 Python 기반 모니터링 시스템입니다.

## 주요 기능

- **일일 자동 메트릭 수집**: CPU, 메모리, 디스크 사용량 추적
- **로그 분석**: syslog, auth.log, 커널 로그에서 오류 및 보안 이벤트 분석
- **임계값 모니터링**: 경고/위험 수준 설정 가능
- **지능형 권장 사항**: 패턴 기반 개선 제안 자동 생성
- **전문 PDF 보고서**: 차트, 테이블, 상세 분석 포함
- **Cron 자동화**: cron 작업을 통한 완전 자동화
- **추세 분석**: 리소스 사용량 증가/감소 패턴 식별

## 시스템 요구사항

- Ubuntu Server 18.04 이상
- Python 3.8 이상
- sudo 권한 (로그 파일 읽기용, 사용자가 `adm` 그룹에 속해야 함)
- Python 의존성 설치용 디스크 공간 ~50MB
- 연간 메트릭 데이터용 디스크 공간 ~100MB

## 빠른 시작

### 1. 설치

```bash
# 저장소 클론 또는 다운로드
cd /path/to/Report-Server

# 설치 스크립트 실행
bash scripts/install_deps.sh

# 로그 접근을 위해 사용자를 adm 그룹에 추가
sudo usermod -aG adm $USER

# 그룹 변경 적용을 위해 로그아웃 후 재로그인
```

### 2. 설정

`config/` 디렉토리의 설정 파일을 편집합니다:

| 파일 | 설명 |
|------|------|
| `config.yaml` | 메인 설정 (경로, 보관 기간 등) |
| `thresholds.yaml` | 경고/위험 임계값 |
| `log_patterns.yaml` | 로그 패턴 매칭 규칙 |

### 3. 테스트 실행

```bash
# 가상환경 활성화
source venv/bin/activate

# 메트릭 수집 테스트
python src/main.py --collect-only

# 보고서 생성 테스트 (이전 달)
python src/main.py --generate-report
```

### 4. 자동화 설정

```bash
# cron 작업 설치
bash scripts/setup_cron.sh
```

다음 cron 작업이 생성됩니다:
- **매일 23:59**: 시스템 메트릭 수집
- **매월 1일 02:00**: PDF 보고서 생성

## 사용법

### CLI 명령어

```bash
# 메트릭만 수집
python src/main.py --collect-only

# 보고서만 생성 (이전 달)
python src/main.py --generate-report

# 특정 월 보고서 생성
python src/main.py --generate-report --year 2026 --month 1

# 전체 워크플로우 실행 (수집 + 보고서)
python src/main.py
```

### 생성된 보고서

보고서는 `reports/` 디렉토리에 다음 형식으로 저장됩니다:

```
server_report_{호스트명}_{YYYY}_{MM}.pdf
```

예시: `server_report_myserver_2026_01.pdf`

## 프로젝트 구조

```
Report-Server/
├── src/
│   ├── main.py                      # 메인 CLI 진입점
│   ├── collectors/                  # 데이터 수집 모듈
│   │   ├── system_monitor.py       # CPU/메모리/디스크 수집
│   │   └── log_analyzer.py         # 로그 파싱 및 분석
│   ├── analyzers/                   # 데이터 분석 모듈
│   │   ├── metrics_analyzer.py     # 통계 분석
│   │   ├── threshold_checker.py    # 임계값 위반 감지
│   │   └── recommendation_engine.py # 자동 권장사항
│   ├── reporters/                   # 보고서 생성
│   │   ├── pdf_generator.py        # PDF 오케스트레이터
│   │   ├── chart_builder.py        # Matplotlib 차트
│   │   └── table_builder.py        # 테이블 포매팅
│   ├── storage/                     # 데이터 저장
│   │   └── data_store.py           # JSON 저장소
│   └── utils/                       # 유틸리티
│       ├── config_loader.py        # YAML 설정 로더
│       └── logger.py               # 로깅 설정
├── config/                          # 설정 파일
│   ├── config.yaml
│   ├── thresholds.yaml
│   └── log_patterns.yaml
├── scripts/                         # 자동화 스크립트
│   ├── install_deps.sh
│   └── setup_cron.sh
├── data/metrics/                    # 저장된 메트릭 (YYYY/MM/)
├── reports/                         # 생성된 PDF 보고서
├── logs/                            # 애플리케이션 로그
└── requirements.txt                 # Python 의존성
```

## 설정

### 메인 설정 (config/config.yaml)

```yaml
system:
  hostname: auto  # auto = 자동 감지

collection:
  sample_interval: 86400  # 1일 (초 단위)
  retention_months: 12

report:
  output_dir: reports
  filename_format: "server_report_{hostname}_{year}_{month}.pdf"

logs:
  syslog: /var/log/syslog
  auth_log: /var/log/auth.log
  kern_log: /var/log/kern.log
```

### 임계값 설정 (config/thresholds.yaml)

```yaml
cpu:
  warning: {avg_usage: 70, max_usage: 85}
  critical: {avg_usage: 85, max_usage: 95}

memory:
  warning: {ram_usage: 80, swap_usage: 30}
  critical: {ram_usage: 90, swap_usage: 50}

disk:
  warning: {usage: 80}
  critical: {usage: 90}
```

### 로그 패턴 설정 (config/log_patterns.yaml)

시스템 로그에서 오류/경고 감지를 위한 정규식 패턴을 커스터마이즈할 수 있습니다.

## PDF 보고서 구성

1. **요약 (Executive Summary)**: 주요 통계 및 발견사항
2. **CPU 분석**: 사용량 차트 및 통계
3. **메모리 분석**: RAM 및 SWAP 사용량 추세
4. **디스크 분석**: 마운트 지점별 파티션 사용량
5. **로그 분석**: 오류/경고 카운트 및 보안 이벤트
6. **임계값 위반**: 설정된 한계를 초과한 항목
7. **권장 사항**: 우선순위가 지정된 개선 제안

## 문제 해결

### 권한 거부 오류

로그 파일 읽기 시 권한 오류가 발생하면:

```bash
# 사용자를 adm 그룹에 추가
sudo usermod -aG adm $USER

# 로그아웃 후 재로그인, 확인
groups | grep adm
```

### Cron 작업이 실행되지 않음

cron 로그 확인:
```bash
tail -f logs/cron.log
```

cron 작업 설치 확인:
```bash
crontab -l
```

### 보고서용 데이터 누락

메트릭이 수집되고 있는지 확인:
```bash
ls -la data/metrics/2026/01/
```

### Python 모듈 오류

가상환경이 활성화되어 있는지 확인:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## 유지보수

### 로그 확인

```bash
# 애플리케이션 로그
tail -f logs/app.log

# Cron 작업 로그
tail -f logs/cron.log
```

### 오래된 데이터 정리

시스템은 보관 기간(기본: 12개월)보다 오래된 데이터를 자동으로 정리합니다.

수동 정리가 필요한 경우:
```bash
# 데이터는 data/metrics/YYYY/MM/ 에 저장됨
# 필요시 오래된 디렉토리를 수동으로 삭제
```

### 설정 업데이트

설정 파일 수정 후 재시작이 필요 없습니다. 다음 실행 시 변경 사항이 적용됩니다.

## 고급 사용법

### 특정 기간 보고서

원하는 월의 보고서 생성:
```bash
python src/main.py --generate-report --year 2025 --month 12
```

### 다른 도구와 연동

시스템은 다음과 연동 가능한 JSON 메트릭을 출력합니다:
- Prometheus 익스포터
- Grafana 대시보드
- 커스텀 모니터링 솔루션

메트릭 파일 위치: `data/metrics/YYYY/MM/metrics_YYYY-MM-DD.json`

## 보안 고려사항

- 설정 파일에 민감한 데이터 없음
- 로그 파일은 읽기 전용 접근
- 보고서는 오류를 요약 (전체 로그 덤프 없음)
- 메트릭은 로컬 저장 (외부 전송 없음)

## 향후 개선 계획

- 중요 알림 이메일 발송
- 웹 대시보드 인터페이스
- 멀티 서버 모니터링
- 데이터베이스 저장 백엔드
- 실시간 알림
- 머신러닝 기반 이상 탐지

## 라이선스

이 프로젝트는 Ubuntu 서버 모니터링을 위해 제공됩니다.

## 지원

문제나 질문이 있는 경우:
1. `logs/app.log`에서 로그 확인
2. `config/*.yaml`에서 설정 확인
3. `--collect-only` 또는 `--generate-report`로 개별 컴포넌트 테스트

## 기여하기

기능 확장 방법:
1. `src/collectors/`에 새 수집기 추가
2. `src/analyzers/`에 새 분석기 추가
3. `src/reporters/pdf_generator.py`에서 PDF 섹션 커스터마이즈
4. `config/`에서 설정 스키마 업데이트

## 버전

버전 1.0.0 - 초기 릴리스
