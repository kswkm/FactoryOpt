# 🏭 FACTORYOPT - Machine Uptime Dashboard

Smart Factory 제조 설비 운영 가동률 모니터링 대시보드

## 📋 프로젝트 구조

```
FACTORYOPT/
├── run.py                          # Flask 서버 메인 파일
├── requirements.txt                # Python 의존성 정의
├── machine_uptime_export.csv       # 설비 운영 데이터
├── README.md                       # 프로젝트 설명서
└── templates/
    └── machine_uptime_dashboard.html  # 대시보드 UI
```

## 🚀 빠른 시작

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 서버 실행
```bash
python run.py
```

### 3. 브라우저에서 접속
```
http://127.0.0.1:5000
```

## 📊 기능

- **실시간 대시보드**: 제조 설비의 가동률 모니터링
- **설비별 성능 지표**:
  - 가용성 (Availability)
  - 다운타임 (Downtime)
  - 불량률 (Defect Rate)
  - 생산성 (Productivity)
  - 에너지 효율 (Energy Efficiency)
  
- **이상 탐지**: 자동 이상 현상 감지 및 알림
- **상세 분석**: 다운타임 사유, 월별 추이 분석

## 🔧 API 엔드포인트

### GET `/`
대시보드 HTML 페이지 반환

### GET `/api/data`
전체 설비 운영 데이터 JSON 반환
```json
{
  "success": true,
  "data": [...],
  "columns": [...]
}
```

### GET `/api/summary`
요약 통계 정보 반환
```json
{
  "success": true,
  "summary": {
    "total_records": 720,
    "machines": 12,
    "avg_availability": 90.5,
    "avg_defect_rate": 4.2,
    "total_downtime": 3500,
    "date_range": {
      "start": "2026-01-01",
      "end": "2026-12-31"
    }
  }
}
```

## 📈 데이터 포맷

CSV 파일 컬럼:
- `date`: 운영 날짜
- `machine_id`: 설비 ID (A-01, B-02 등)
- `plan_min`: 계획 운영 시간 (분)
- `run_min`: 실제 운영 시간 (분)
- `downtime_min`: 다운타임 (분)
- `downtime_reason`: 다운타임 사유
- `prod_qty`: 생산 수량
- `good_qty`: 양품 수량
- `energy_kWh`: 에너지 소비량
- `availability`: 가용성 (%)
- `defect_rate`: 불량률 (%)
- `yield_rate`: 수율 (%)
- 기타 성능 지표들

## 🛠️ 기술 스택

- **Backend**: Flask 3.0.0
- **Data Processing**: Pandas 2.1.4
- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Chart.js 4.4.1
- **Font**: Pretendard

## 💻 시스템 요구사항

- Python 3.8+
- pip (Python 패키지 관리자)

## 🔍 문제 해결

### 포트 5000이 이미 사용 중인 경우
run.py의 마지막 줄을 수정하세요:
```python
app.run(debug=True, host='127.0.0.1', port=5001)  # 포트 5001로 변경
```

### CSV 파일을 찾을 수 없는 경우
`machine_uptime_export.csv` 파일이 `run.py`와 같은 디렉토리에 있는지 확인하세요.

### 의존성 설치 오류
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 📝 라이선스

Internal Use Only

## 📧 문의

설비 모니터링 시스템 관련 문의는 팀리드에게 연락하세요.
