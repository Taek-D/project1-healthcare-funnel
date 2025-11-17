
# Project 1: Healthcare App Funnel/Cohort/AARRR Analysis

## 📌 개요

건강앱 사용자의 Funnel, Cohort, AARRR 분석을 통해 사용자 여정을 분석하고 개선 전략을 수립하는 프로젝트입니다.

## 📊 분석 결과

### Funnel Analysis (사용자 여정)
- **전체 통과율**: 35.7%
- 가입(50K) → 첫운동(40K, 79.9%) → 리워드(30K, 75%) → 재방문(18K, 59.7%)

### Cohort Analysis (월별 리텐션)
- Month 0: 100% (모든 사용자)
- Month 1: 15.3% (평균)
- 월이 지날수록 점진적 감소

### AARRR Metrics (사용자 생명주기)
- Acquisition: 월 ~4,100명 (안정적)
- Activation: 80% (첫운동 시작)
- Retention: 35.7% (재방문)
- Revenue: 월 ~1.3억원 (안정적)
- Referral: 10% (추천)

### A/B Test (리워드 효과)
- **리워드 제공**: 59.71% 재방문율
- **리워드 미제공**: 0% 재방문율
- **차이**: 59.71%p (p-value < 0.001, 통계적 유의)

## 🗂️ 파일 구조
project1_healthcare_funnel/
├── notebooks/
│ ├── 01_generate_sample_data.py # 샘플 데이터 생성
│ └── 02_funnel_analysis.py # Funnel/Cohort/AARRR 분석
├── data/
│ ├── users.csv # 사용자 기본정보 (50K)
│ ├── events.csv # 앱 사용 이벤트 (150K)
│ └── rewards.csv # 리워드 지급기록 (30K)
├── results/
│ ├── funnel_chart.png # Funnel 깔때기 차트
│ ├── cohort_heatmap.png # Cohort 리텐션 히트맵
│ ├── aarrr_chart.png # AARRR 월별 추이
│ ├── ab_test_chart.png # A/B Test 비교
│ ├── cohort_retention.csv # Cohort 상세 데이터
│ └── aarrr_analysis.csv # AARRR 상세 데이터
├── sql/ # SQL 쿼리 (향후 추가)
├── README.md # 이 파일
└── requirements.txt # Python 라이브러리

## 🚀 실행 방법

### 1. 환경 설정
cd ~/Documents/project1_healthcare_funnel

라이브러리 설치
pip3 install pandas numpy matplotlib seaborn scipy

### 2. 데이터 생성
python3 notebooks/01_generate_sample_data.py

### 3. 분석 실행
python3 notebooks/02_funnel_analysis.py

### 결과
- `data/` 폴더에 CSV 파일 생성
- `results/` 폴더에 시각화 이미지 생성

## 💡 주요 발견

1. **Funnel 최적화**: 첫운동 단계 이탈율 20% 개선 필요
   - 온보딩 개선 (튜토리얼, 가이드 추가)
   - 초기 운동 난이도 조정

2. **리워드 효과 입증**: A/B Test로 리워드의 강력한 효과 확인
   - 리워드 제공 시 재방문율 60% 증가
   - 리워드 정책 강화 권장

3. **안정적 매출**: 월별 AARRR 지표가 일정
   - 신규 획득과 매출이 안정적
   - 향후 스케일링 가능

## 📚 기술 스택

- **데이터 생성**: Python (NumPy, Pandas)
- **분석**: Python (Pandas, SciPy 통계)
- **시각화**: Matplotlib, Seaborn
- **도구**: VS Code, Jupyter Notebook
- **버전 관리**: Git, GitHub

## 🔬 통계 방법

- **Funnel**: 단계별 전환율 계산 (CASE WHEN)
- **Cohort**: Pivot 테이블로 월별 리텐션 분석
- **AARRR**: 월별 지표 집계
- **A/B Test**: Chi-square 검정 (p-value < 0.05)

## 📝 라이센스

MIT License

## 👨‍💻 작성자

Taek-D (데이터분석가 지망생)
- GitHub: https://github.com/Taek-D
- 목표: 데이터 기반 의사결정 문화 조성
