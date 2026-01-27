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

### 네이티브 실행 (pyenv)
- Ubuntu Server 18.04 이상 (macOS도 지원)
- Python 3.11+ (pyenv로 관리)
- [pyenv](https://github.com/pyenv/pyenv) + [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)
- sudo 권한 (로그 파일 읽기용, Linux에서 사용자가 `adm` 그룹에 속해야 함)
- Python 의존성 설치용 디스크 공간 ~50MB
- 연간 메트릭 데이터용 디스크 공간 ~100MB

### Docker 실행 (권장)
- Docker Engine 20.10 이상
- Docker Compose 2.0 이상
- 디스크 공간 ~200MB (이미지 + 데이터)
- sudo 권한 (Docker 실행 및 호스트 시스템 모니터링용)

## 설치 방법

두 가지 설치 방법 중 선택할 수 있습니다:

1. **Docker 방식 (권장)**: Python/pyenv 설치 불필요, 격리된 환경
2. **네이티브 방식**: 직접 시스템에 설치

## 빠른 시작 - Docker 방식 (권장)

> **중요**: Docker 방식은 호스트 시스템을 모니터링하기 위해 특별한 권한이 필요합니다.
> - `pid: "host"` 모드 사용 (호스트 프로세스 네임스페이스 공유)
> - `/proc`, `/sys`, `/var/log` 디렉토리를 호스트에서 마운트
> - 프로덕션 환경에서는 보안 정책을 검토하세요.

### 1. Docker 설치 확인

```bash
docker --version
docker-compose --version
```

### 2. 프로젝트 클론

```bash
git clone git@github.com:shlee123456/Report-Server.git
cd Report-Server
```

### 3. 환경 변수 설정 (중요!)

Docker 환경에서는 서버의 실제 호스트명을 설정해야 합니다:

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집하여 실제 서버 호스트명 입력
# REPORT_HOSTNAME=your-server-name
```

**중요**: `REPORT_HOSTNAME`을 설정하지 않으면 보고서 파일명이 컨테이너명으로 생성됩니다.

### 4. 기타 설정 (선택사항)

`config/` 디렉토리의 설정 파일을 편집합니다 (기본값으로도 사용 가능).

### 5. Docker 이미지 빌드

```bash
bash scripts/docker-run.sh build
```

### 6. 테스트 실행

```bash
# 메트릭 수집 테스트
bash scripts/docker-run.sh collect

# 보고서 생성 테스트
bash scripts/docker-run.sh report
```

### 7. 자동화 설정 (스케줄러 시작)

```bash
# cron 스케줄러 컨테이너 시작
bash scripts/docker-run.sh start-cron

# 로그 확인
bash scripts/docker-run.sh logs-cron
```

다음 작업이 자동으로 실행됩니다:
- **매일 23:59**: 시스템 메트릭 수집
- **매월 1일 02:00**: PDF 보고서 생성

### Docker 명령어

```bash
# 이미지 빌드
bash scripts/docker-run.sh build

# 메트릭 수집
bash scripts/docker-run.sh collect

# 보고서 생성 (이전 달)
bash scripts/docker-run.sh report

# 특정 월 보고서 생성
bash scripts/docker-run.sh report-month 2026 1

# 스케줄러 시작/중지
bash scripts/docker-run.sh start-cron
bash scripts/docker-run.sh stop-cron

# 로그 확인
bash scripts/docker-run.sh logs        # 애플리케이션 로그
bash scripts/docker-run.sh logs-cron   # 스케줄러 로그

# 컨테이너 셸 접속
bash scripts/docker-run.sh shell

# 정리
bash scripts/docker-run.sh clean
```

또는 docker-compose를 직접 사용:

```bash
# 일회성 명령 실행
docker-compose run --rm report-server python src/main.py --collect-only

# 스케줄러 시작
docker-compose up -d report-server-cron

# 로그 확인
docker-compose logs -f report-server-cron
```

## 빠른 시작 - 네이티브 방식

pyenv와 Python을 직접 설치하여 실행하는 방법입니다.

### 1. pyenv 설치 (없는 경우)

```bash
# macOS (Homebrew)
brew install pyenv pyenv-virtualenv

# Linux
curl https://pyenv.run | bash

# ~/.bashrc 또는 ~/.zshrc에 추가
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

### 2. 프로젝트 설치

```bash
# 저장소 클론
git clone git@github.com:shlee123456/Report-Server.git
cd Report-Server

# 설치 스크립트 실행 (pyenv 가상환경 자동 생성)
bash scripts/install_deps.sh

# (Linux만 해당) 로그 접근을 위해 사용자를 adm 그룹에 추가
sudo usermod -aG adm $USER
# 그룹 변경 적용을 위해 로그아웃 후 재로그인
```

### 3. 설정

`config/` 디렉토리의 설정 파일을 편집합니다:

| 파일 | 설명 |
|------|------|
| `config.yaml` | 메인 설정 (경로, 보관 기간 등) |
| `thresholds.yaml` | 경고/위험 임계값 |
| `log_patterns.yaml` | 로그 패턴 매칭 규칙 |

### 4. 테스트 실행

```bash
# pyenv가 자동으로 가상환경 활성화 (.python-version 파일)
cd Report-Server

# 메트릭 수집 테스트
python src/main.py --collect-only

# 보고서 생성 테스트 (이전 달)
python src/main.py --generate-report
```

### 5. 자동화 설정

```bash
# cron 작업 설치
bash scripts/setup_cron.sh
```

다음 cron 작업이 생성됩니다:
- **매일 23:59**: 시스템 메트릭 수집
- **매월 1일 02:00**: PDF 보고서 생성

## 사용법

### Docker 방식

```bash
# 메트릭만 수집
bash scripts/docker-run.sh collect

# 보고서만 생성 (이전 달)
bash scripts/docker-run.sh report

# 특정 월 보고서 생성
bash scripts/docker-run.sh report-month 2026 1

# 또는 docker-compose 직접 사용
docker-compose run --rm report-server python src/main.py --collect-only
docker-compose run --rm report-server python src/main.py --generate-report --year 2026 --month 1
```

### 네이티브 방식

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
│   ├── install_deps.sh             # pyenv 환경 설치
│   ├── setup_cron.sh               # 네이티브 cron 설정
│   ├── docker-run.sh               # Docker 헬퍼 스크립트
│   └── docker-cron.sh              # Docker 내부 스케줄러
├── data/metrics/                    # 저장된 메트릭 (YYYY/MM/)
├── reports/                         # 생성된 PDF 보고서
├── logs/                            # 애플리케이션 로그
├── Dockerfile                       # Docker 이미지 정의
├── docker-compose.yml               # Docker Compose 설정
├── .dockerignore                    # Docker 빌드 제외 파일
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

### Docker 관련

#### Docker 컨테이너가 시작되지 않음

```bash
# 컨테이너 로그 확인
docker-compose logs report-server

# 이미지 재빌드
bash scripts/docker-run.sh build
```

#### 호스트 시스템 메트릭이 수집되지 않음

Docker는 기본적으로 컨테이너 내부 메트릭만 수집합니다. 호스트 시스템 메트릭을 수집하려면:

1. `/proc`, `/sys`, `/var/log`가 올바르게 마운트되었는지 확인
2. `docker-compose.yml`에 볼륨이 정의되어 있는지 확인

```bash
# 마운트 확인
docker-compose run --rm report-server ls -la /host/proc
docker-compose run --rm report-server ls -la /host/var/log
```

#### 권한 오류 (Docker)

Docker 컨테이너에서 로그 파일 접근 시 권한 오류:

```bash
# 호스트에서 로그 디렉토리 권한 확인
ls -la /var/log/syslog

# 필요시 Docker 사용자를 호스트의 adm 그룹에 매핑
# docker-compose.yml에서 user: 설정 조정 필요
```

#### 보고서 파일명이 잘못된 호스트명으로 생성됨

Docker에서 보고서 파일이 `server_report_report-server_2026_01.pdf` 같은 이름으로 생성되는 경우:

```bash
# .env 파일이 있는지 확인
ls -la .env

# 없으면 생성
cp .env.example .env

# .env 파일 편집하여 실제 서버 호스트명 설정
nano .env
# REPORT_HOSTNAME=your-actual-server-name

# 환경 변수가 적용되었는지 확인
docker-compose run --rm report-server printenv | grep REPORT_HOSTNAME

# 컨테이너 재시작
docker-compose restart
```

**또는** 일회성으로 호스트명 지정:

```bash
REPORT_HOSTNAME=myserver bash scripts/docker-run.sh collect
REPORT_HOSTNAME=myserver bash scripts/docker-run.sh report
```

#### 스케줄러가 작동하지 않음 (Docker)

```bash
# 스케줄러 컨테이너 상태 확인
docker-compose ps

# 스케줄러 로그 확인
bash scripts/docker-run.sh logs-cron

# 컨테이너 재시작
bash scripts/docker-run.sh stop-cron
bash scripts/docker-run.sh start-cron
```

### 네이티브 방식 관련

#### 권한 거부 오류

로그 파일 읽기 시 권한 오류가 발생하면:

```bash
# 사용자를 adm 그룹에 추가
sudo usermod -aG adm $USER

# 로그아웃 후 재로그인, 확인
groups | grep adm
```

#### Cron 작업이 실행되지 않음

cron 로그 확인:
```bash
tail -f logs/cron.log
```

cron 작업 설치 확인:
```bash
crontab -l
```

#### Python 모듈 오류

가상환경이 활성화되어 있는지 확인:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 공통 문제

#### 보고서용 데이터 누락

메트릭이 수집되고 있는지 확인:

```bash
# Docker 방식
docker-compose run --rm report-server ls -la data/metrics/2026/01/

# 네이티브 방식
ls -la data/metrics/2026/01/
```

#### 로그 파일을 찾을 수 없음

macOS에서는 `/var/log/syslog`가 없을 수 있습니다. `config/config.yaml`에서 로그 경로를 조정하세요:

```yaml
logs:
  syslog: /var/log/system.log  # macOS
  auth_log: /var/log/system.log
  kern_log: /var/log/system.log
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
