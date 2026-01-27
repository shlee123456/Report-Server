# Ubuntu 서버 모니터링 & 월간 리포트 시스템

**서버의 CPU, 메모리, 디스크 사용량을 매일 자동으로 수집하고, 월말에 통계와 차트가 포함된 PDF 보고서를 자동 생성하는 시스템입니다.**

---

## 🎯 이 프로젝트는 무엇인가요?

### 비개발자를 위한 설명
매달 말이면 서버가 얼마나 사용되었는지 궁금하신가요? 이 시스템은 서버를 24/7 모니터링하여:
- 📊 **매일 밤 11:59**에 CPU, 메모리, 디스크 사용량을 기록
- 📈 **매월 1일 새벽 2시**에 지난 달 전체 통계를 계산하여 PDF 보고서 자동 생성
- 💡 문제가 있으면 권장 조치사항까지 자동으로 제안

설치 후 아무것도 하지 않아도, 매달 자동으로 보고서가 생성됩니다.

### 엔지니어를 위한 설명
Python 기반 서버 모니터링 시스템으로, `psutil`로 시스템 메트릭 수집 → JSON 저장 → 통계 분석 → PDF 리포트 생성의 자동화된 파이프라인을 제공합니다.

**핵심 특징:**
- 일일 메트릭 수집 (CPU, RAM, Swap, Disk, Load Average)
- 로그 분석 (syslog, auth.log, kern.log)
- 월간 통계 계산 (평균, 최대, 최소, 중앙값, 표준편차, 추세)
- 임계값 기반 알림 및 권장사항 엔진
- Docker 지원 (호스트 시스템 모니터링)
- 스케줄러 내장 (cron 또는 Docker 내부 루프)

---

## 📋 월 평균 사용량 체크 기능

**네, 가능합니다!** 매일 23:59에 데이터를 수집하고, 매월 1일에 다음 통계를 계산합니다:

| 항목 | 제공하는 통계 |
|------|---------------|
| **CPU** | 월 평균 사용률, 최대/최소값, 추세(증가/감소/안정) |
| **메모리** | RAM/Swap 월 평균 사용률, 최대/최소값, 추세 |
| **디스크** | 파티션별 월 평균 사용률, 최대/최소값, 추세 |

**예시:** 1월 한 달 동안 31일 데이터 수집 → 2월 1일에 자동으로 "1월 평균 CPU: 35.5%, 최대: 78.2%" 같은 통계를 PDF로 생성

---

## 🚀 빠른 시작 (Docker 권장)

### 필요한 것
- Docker & Docker Compose
- Ubuntu Server (또는 Linux)

### 설치 (3단계)

```bash
# 1. 프로젝트 복사
git clone https://github.com/yourusername/Report-Server.git
cd Report-Server

# 2. 서버 이름 설정 (중요!)
cp .env.example .env
nano .env  # REPORT_HOSTNAME=실제서버이름 입력

# 3. 스케줄러 시작
docker-compose up -d report-server-cron
```

끝! 이제 자동으로:
- **매일 23:59** → 메트릭 수집
- **매월 1일 02:00** → `reports/` 폴더에 PDF 생성

### 테스트 실행 (선택)

```bash
# 지금 당장 메트릭 수집해보기
docker-compose run --rm report-server python src/main.py --collect-only

# 로그 확인
docker-compose logs -f report-server-cron
```

---

## 🛠️ Docker 없이 설치 (네이티브)

### 필요한 것
- Python 3.11+
- pyenv + pyenv-virtualenv

### 설치

```bash
# 1. 프로젝트 복사
git clone https://github.com/yourusername/Report-Server.git
cd Report-Server

# 2. Python 환경 자동 설정
bash scripts/install_deps.sh

# 3. (Linux만) 로그 읽기 권한 부여
sudo usermod -aG adm $USER
# 로그아웃 후 재로그인

# 4. cron 자동화 설정
bash scripts/setup_cron.sh
```

---

## 📊 생성되는 보고서

PDF 보고서는 `reports/` 폴더에 다음 형식으로 저장됩니다:

```
server_report_서버이름_2026_01.pdf
```

**보고서 내용:**
1. **요약 테이블**: 월 평균 CPU/메모리/디스크 사용률, 추세
2. **CPU 분석**: 일일 사용률 차트, 상세 통계
3. **메모리 분석**: RAM/Swap 추세 그래프
4. **디스크 분석**: 파티션별 사용량
5. **로그 분석**: 에러/경고 카운트
6. **임계값 위반**: 경고/위험 수준 초과 항목
7. **권장 조치**: 자동 생성된 개선 제안

---

## ⚙️ 설정

### 임계값 조정 (config/thresholds.yaml)

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

### 데이터 보관 기간 (config/config.yaml)

```yaml
collection:
  retention_months: 12  # 12개월 이상 된 데이터 자동 삭제
```

---

## 🔍 문제 해결

### Docker 컨테이너가 계속 재시작함

```bash
# 로그 확인
docker logs report-server

# 이미지 재빌드
docker-compose down
docker-compose up -d --build
```

### 보고서 파일명이 이상함 (report-server_2026_01.pdf)

`.env` 파일에 실제 서버 이름을 설정하세요:

```bash
# .env 파일 생성
cp .env.example .env

# 편집
nano .env
# REPORT_HOSTNAME=myserver
```

### 로그 읽기 권한 오류 (네이티브 설치)

```bash
# adm 그룹 추가
sudo usermod -aG adm $USER

# 로그아웃 후 재로그인하여 적용
```

### 데이터가 없어서 보고서 생성 안됨

최소 1일치 데이터가 필요합니다:

```bash
# 메트릭 수집 확인
ls -la data/metrics/2026/01/

# 수동으로 수집
docker-compose run --rm report-server python src/main.py --collect-only
```

---

## 📂 프로젝트 구조

```
Report-Server/
├── src/
│   ├── main.py                    # 메인 실행 파일
│   ├── collectors/                # 데이터 수집
│   │   ├── system_monitor.py     # CPU/메모리/디스크 수집
│   │   └── log_analyzer.py       # 로그 파싱
│   ├── analyzers/                 # 데이터 분석
│   │   ├── metrics_analyzer.py   # 평균/최대/추세 계산
│   │   ├── threshold_checker.py  # 임계값 체크
│   │   └── recommendation_engine.py  # 권장사항 생성
│   └── reporters/                 # PDF 생성
│       ├── pdf_generator.py      # PDF 조립
│       ├── chart_builder.py      # 그래프 생성
│       └── table_builder.py      # 테이블 생성
├── config/                        # 설정 파일
├── data/metrics/                  # 수집된 데이터 (JSON)
├── reports/                       # 생성된 PDF
├── logs/                          # 앱 로그
├── Dockerfile                     # Docker 이미지
├── docker-compose.yml             # Docker 설정
└── scripts/                       # 설치/자동화 스크립트
```

---

## 🎛️ 주요 명령어

### Docker 방식

```bash
# 메트릭 수집
docker-compose run --rm report-server python src/main.py --collect-only

# 보고서 생성 (전월)
docker-compose run --rm report-server python src/main.py --generate-report

# 특정 월 보고서
docker-compose run --rm report-server python src/main.py --generate-report --year 2025 --month 12

# 2026년 1월 보고서 예시
docker-compose run --rm report-server python src/main.py --generate-report --year 2026 --month 1

# 스케줄러 시작/중지
docker-compose up -d report-server-cron
docker-compose stop report-server-cron

# 로그 확인
docker-compose logs -f report-server-cron
```

### 네이티브 방식

```bash
# 메트릭 수집
python src/main.py --collect-only

# 보고서 생성 (전월)
python src/main.py --generate-report

# 특정 월 보고서
python src/main.py --generate-report --year 2025 --month 12

# 로그 확인
tail -f logs/app.log
tail -f logs/cron.log
```

---

## 🔒 보안 참고사항

### Docker 권한
Docker 방식은 호스트 시스템을 모니터링하기 위해 특수 권한이 필요합니다:
- `pid: "host"` - 호스트 프로세스 접근
- `/proc`, `/sys`, `/var/log` 마운트 - 시스템 정보 읽기

**모든 접근은 읽기 전용(`:ro`)입니다.** 시스템을 변경하지 않습니다.

### 데이터 보안
- 메트릭은 로컬에만 저장 (외부 전송 없음)
- 로그는 통계만 추출 (전체 내용 저장 안 함)
- 민감 정보 없음

---

## 💡 FAQ

**Q: 언제 보고서가 생성되나요?**
A: 매월 1일 새벽 2시에 전월 보고서가 자동 생성됩니다.

**Q: 수동으로 보고서를 만들 수 있나요?**
A: 네, `python src/main.py --generate-report --year 2025 --month 12` 명령으로 가능합니다.

**Q: 여러 서버를 모니터링할 수 있나요?**
A: 현재는 각 서버마다 별도로 설치해야 합니다. (향후 개선 예정)

**Q: 알림 기능이 있나요?**
A: 현재는 PDF 보고서만 생성합니다. 이메일 알림은 향후 추가 예정입니다.

**Q: Docker 없이 사용할 수 있나요?**
A: 네, 네이티브 설치 방법을 사용하세요 (위 참조).

---
