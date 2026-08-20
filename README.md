# 🏭 FactoryOpt — Machine Uptime Dashboard

공장 설비의 가용률(availability), 불량률(defect_rate), 다운타임(downtime_min)을 실시간으로 모니터링하는 대시보드 시스템입니다. CSV 기반 프로토타입에서 시작하여 PostgreSQL + FastAPI 기반의 API 분리 아키텍처로 전환했습니다.

---

## 1. 기술 스택

| 구분 | 기술 | 용도 |
|---|---|---|
| Frontend/Dashboard | Flask, Jinja2 | 대시보드 렌더링 (`run.py`) |
| Backend API | FastAPI, Uvicorn | DB 접근을 전담하는 API 서버 (`api_server.py`) |
| Database | PostgreSQL | 설비 가동 데이터 저장 (정형/시계열) |
| ORM/DB 연동 | SQLAlchemy, psycopg2 | DB 커넥션 및 쿼리 |
| 데이터 처리 | pandas | CSV 파싱, 집계, DB 마이그레이션 |
| 통신 | requests | Flask ↔ FastAPI 간 내부 HTTP 호출 |
| 환경 관리 | python-dotenv | DB 자격증명 등 민감정보 분리 |
| 실행 환경 | Python venv (Windows) | 의존성 격리 |

---

## 2. 기술 선택 이유

### 왜 CSV → PostgreSQL인가
초기에는 `pandas.read_csv`로 정적 파일을 읽는 구조였으나, 다음 이유로 관계형 DB로 전환했습니다.
- 데이터가 `machine_id / date_str / availability / defect_rate / downtime_min` 등 명확한 스키마를 가진 정형 데이터라 관계형 모델에 적합
- 다중 클라이언트(대시보드, 향후 모바일/리포트 도구)가 동시에 같은 데이터를 조회해야 하는 요구를 CSV 파일 하나로는 감당할 수 없음
- 인덱스, 트랜잭션, 동시성 제어 등 실무 표준 기능이 필요

### 왜 PostgreSQL인가 (MySQL/SQLite 대비)
- 시계열·정형 데이터에 강하고, row-level security·SSL 등 보안 기능이 실무 환경(클라우드 RDS 등)과 동일하게 실습 가능
- SQLite는 파일 기반이라 동시 접속·확장성에 한계, MS SQL Server는 라이선스/설치 부담이 큼
- 무료·오픈소스이면서 프로덕션급 신뢰성 확보

### 왜 DB를 API(FastAPI)로 감쌌는가 — 직접 연결 대신 API 분리
- **자격증명 최소 노출**: DB 비밀번호를 대시보드 서버(`run.py`)가 아닌 API 서버 한 곳에만 보관
- **접근 통제 지점 확보**: API Key/JWT 인증, Rate Limiting을 API 레벨에서 적용 가능 (대시보드가 여러 개로 늘어나도 인증 로직 중복 없음)
- **WAF 적용 가능성**: 내부 DB에는 WAF를 붙일 수 없지만, API 앞단에는 리버스 프록시 + WAF를 배치할 수 있음
- **확장성**: 향후 모바일 앱, 다른 대시보드가 늘어나도 동일 API를 재사용
- FastAPI는 비동기 처리와 Swagger 자동 문서화(`/docs`)를 기본 제공해 API 서버로 적합

### 왜 Flask는 유지했는가
- 이미 존재하는 대시보드 렌더링 로직(`render_template`)을 유지하면서 데이터 소스만 API로 교체하는 최소 변경 전략
- 대시보드 자체는 무거운 프레임워크가 필요 없는 단순 렌더링 계층이므로 경량 Flask가 적합

---

## 3. 아키텍처

```
[PostgreSQL]
     ↑  (SQLAlchemy, DB 자격증명 보유)
[api_server.py : FastAPI, :8000]
     ↑  (HTTP GET, 무자격증명)
[run.py : Flask, :5000]
     ↑  (HTML/JSON)
[Browser]
```

**계층별 책임 분리**
- **PostgreSQL**: `machine_uptime` 테이블에 원본 데이터 저장
- **api_server.py**: DB 접근을 전담하는 유일한 컴포넌트. `/api/machine-uptime`, `/api/summary`, `/health` 제공
- **run.py**: DB에 직접 접속하지 않고 API만 호출, HTML 렌더링과 프론트용 JSON 응답만 담당
- **migrate_csv_to_db.py**: 기존 CSV 데이터를 PostgreSQL로 1회 이전하는 마이그레이션 스크립트

---

## 4. 주요 기능

| 기능 | 엔드포인트 | 설명 |
|---|---|---|
| 대시보드 렌더링 | `GET /` | `machine_uptime_dashboard.html` 서빙 |
| 전체 데이터 조회 | `GET /api/data` (Flask) → `GET /api/machine-uptime` (FastAPI) | 설비별 가동 데이터 전체 반환 |
| 설비별 필터 조회 | `GET /api/machine-uptime?machine_id=...` | 특정 설비 데이터만 필터링 |
| 요약 통계 | `GET /api/summary` | 평균 가용률/불량률, 총 다운타임, 데이터 기간 등 집계 |
| 헬스체크 | `GET /health` (FastAPI) | DB 연결 상태 확인 |
| 캐시 무효화 | `GET /api/refresh` | 캐시된 데이터 강제 재조회 |

---

## 5. 트러블슈팅

### `jinja2.exceptions.TemplateNotFound: machine_uptime_dashboard.html`
- **원인**: Flask는 앱 생성 위치(`run.py`) 기준 `templates/` 폴더만 인식. 폴더 부재, 경로 불일치, 파일명 오타/확장자 문제로 발생
- **해결**: `templates/` 폴더를 `run.py`와 동일 위치에 배치하고, `Flask(__name__, template_folder='templates')`로 명시적 지정. 실행 시 작업 디렉터리(cwd)가 프로젝트 루트인지 확인

### `ModuleNotFoundError: No module named 'pandas'`
- **원인**: 가상환경(`.venv`)이 활성화된 상태에서도 `python`/`pip`이 서로 다른 인터프리터 경로를 참조하는 경우 발생
- **해결**: `python -m pip install <package>` 형태로 항상 현재 활성 인터프리터에 종속된 pip을 사용. `where python`으로 실제 실행 경로 확인 후 `.venv\Scripts\python.exe`인지 검증

### `winget install PostgreSQL.PostgreSQL` → "입력 조건과 일치하는 패키지를 찾을 수 없음"
- **원인**: winget 패키지 ID가 버전별로 세분화(`PostgreSQL.PostgreSQL.17` 등)되어 있어 상위 ID만으로는 매칭 실패
- **해결**: `winget search postgresql`로 정확한 ID 확인 후 `-e`(정확히 일치) 옵션과 함께 재시도. 지속 실패 시 [postgresql.org](https://www.postgresql.org/download/windows/) 공식 인스톨러로 우회 설치

### DB 자격증명 관리
- **원인**: 초기 구조에서 DB 연결 문자열을 코드에 하드코딩할 위험
- **해결**: `.env` + `python-dotenv`로 분리, `.gitignore`에 `.env` 등록. 만약 이미 git에 커밋된 적이 있다면 `git rm --cached .env` 및 히스토리 제거(`git filter-repo`) 후 자격증명 교체

---

## 6. 실행 방법

### 사전 준비
```powershell
# 1. 가상환경 생성 및 활성화
python -m venv .venv
.venv\Scripts\activate

# 2. 의존성 설치
python -m pip install fastapi "uvicorn[standard]" sqlalchemy psycopg2-binary python-dotenv pandas requests flask
```

### PostgreSQL 준비
```powershell
# DB/테이블 생성 (psql -U postgres 접속 후)
CREATE DATABASE factoryopt;
```

### 환경변수 설정 (`.env`, 프로젝트 루트)
```
DB_URL=postgresql+psycopg2://postgres:your_password@localhost:5432/factoryopt
UPTIME_API_URL=http://127.0.0.1:8000/api/machine-uptime
UPTIME_API_SUMMARY_URL=http://127.0.0.1:8000/api/summary
```

### 데이터 마이그레이션 (최초 1회)
```powershell
python migrate_csv_to_db.py
```

### 서버 실행 (터미널 2개)
```powershell
# 터미널 1 — API 서버
uvicorn api_server:app --host 127.0.0.1 --port 8000 --reload

# 터미널 2 — 대시보드 서버
python run.py
```

### 접속
- 대시보드: http://127.0.0.1:5000
- API 문서(Swagger): http://127.0.0.1:8000/docs
