# Streamlit 대시보드 + Supabase 환경 설정 가이드

이 문서는 개발 진행 현황 대시보드를 Supabase와 함께 구축하는 전체 과정을 기록합니다.
실제 작업에서 사용된 프롬프트와 해결 과정을 포함합니다.

---

## 📋 목차
1. [작업 플로우 및 주요 프롬프트](#1-작업-플로우-및-주요-프롬프트)
2. [Git 저장소 초기화](#2-git-저장소-초기화)
3. [프로젝트 구조](#3-프로젝트-구조)
4. [Python 패키지 관리](#4-python-패키지-관리)
5. [Supabase 설정](#5-supabase-설정)
6. [Streamlit 실행](#6-streamlit-실행)
7. [GitHub 배포](#7-github-배포)
8. [자주 하는 실수와 해결법](#8-자주-하는-실수와-해결법)
9. [참고 자료](#9-참고-자료)

---

## 1. 작업 플로우 및 주요 프롬프트

이 섹션은 실제 작업 중에 사용된 주요 프롬프트와 해결 과정을 기록합니다.

### 1.1 초기 요청: GitHub에 커밋 및 푸시

**프롬프트:** 
```
streamlit 대시보드 여기에 커밋 푸시 해줘
https://github.com/jiyong0202/jiyong.git
```

**작업 과정:**
1. Git 저장소 초기화
2. GitHub 리모트 추가
3. 프로젝트 파일들 스테이징
4. 초기 커밋 및 푸시

**결과:**
```
[streamlit faafc1c] Add Streamlit dashboard project with data collection and management scripts
 14 files changed, 1552 insertions(+)
```

---

### 1.2 의존성 설정: requirements.txt 생성

**프롬프트:**
```
니가 커밋한거 올려서 app.py를 실행해보니
ModuleNotFoundError: This app has encountered an error. 
Traceback:
File "/mount/src/jiyong/app.py", line 3, in <module>
    import plotly.express as px
```

**문제:** plotly 패키지가 설치되지 않음

**해결:**
1. requirements.txt 파일 생성
2. 모든 필수 패키지 명시
3. pip install -r requirements.txt로 설치

**생성된 파일:**
```txt
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
openpyxl>=3.1.0
selenium>=4.10.0
beautifulsoup4>=4.12.0
requests>=2.31.0
httpx>=0.26.0
```

---

### 1.3 파일 경로 수정: 상대 경로로 변경

**프롬프트:**
```
어 수정해줘
```

**문제:** app.py에 하드코딩된 절대 경로
```python
file_path = r"C:\jiyong\development_requests.csv"
```

**해결:** 상대 경로로 수정
```python
file_path = os.path.join(os.path.dirname(__file__), "development_requests.csv")
```

**커밋:**
```
Fix hardcoded file path to use relative path
```

---

### 1.4 Supabase 연동: 데이터베이스 통합

**프롬프트:**
```
supabase 데이터로 대시보드 전환해줘
```

**작업 과정:**
1. app.py를 CSV 기반에서 Supabase 기반으로 수정
2. httpx를 사용한 Supabase API 직접 호출 구현
3. 컬럼 매핑 및 데이터 변환 로직 추가

**핵심 코드 변경:**
```python
# Before: CSV 파일에서 로드
df = pd.read_csv(file_path, encoding='utf-8-sig')

# After: Supabase에서 로드
url = f"{supabase_url}/rest/v1/development_requests?select=*"
with httpx.Client() as client:
    response = client.get(url, headers=headers)
    data = response.json()
df = pd.DataFrame(data)
```

**커밋:**
```
Convert dashboard to use Supabase as data source
Simplify Supabase integration to use httpx instead of supabase library
```

---

### 1.5 Supabase 설정: secrets.toml 생성

**프롬프트:**
```
니가 만들어!
```

**작업 과정:**
1. Supabase URL과 API 키 수집
2. `.streamlit/secrets.toml` 파일 생성
3. `.gitignore`에 secrets.toml 추가 (보안)

**생성된 파일 위치:** `.streamlit/secrets.toml`

**파일 내용:**
```toml
supabase_url = "https://wxinpgftwueeocfwsyqt.supabase.co"
supabase_key = "sb_publishable_RIH7gPUM2AQxrzPu9Tj-HQ_vYPAuhkR"
```

**보안 설정:**
```
.gitignore에 추가:
.streamlit/secrets.toml
```

---

### 1.6 앱 실행: Streamlit 앱 시작

**프롬프트:**
```
니가 하라고!
```

**작업 과정:**
1. 의존성 설치 (pip install -r requirements.txt)
2. Streamlit 앱 실행 (python -m streamlit run app.py)
3. 로컬호스트에서 접근 (http://localhost:8501)

**실행 명령:**
```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

**접속 주소:**
- Local: `http://localhost:8501`
- Network: `http://192.168.10.106:8501`

---

### 1.7 Supabase 연결 검증: API 키 확인

**프롬프트:**
```
니가 그냥 연결된 supabase가서 알아와줘. 
니가 뭘 원하는지 모르겠어
```

**작업 과정:**
1. Python 스크립트로 Supabase API 직접 테스트
2. 테이블 구조 확인
3. 샘플 데이터 조회

**테스트 결과:**
```
HTTP Status: 200
[SUCCESS] Connected!
Data count: 1

[COLUMNS]
- request_number
- request_datetime
- request_department
- requester
- request_received_datetime
- development_start_datetime
- development_completion_target_date
- development_manager
- it_biz_manager
- task_title
- request_content
- progress_status
```

---

### 1.8 최종 검증: Streamlit과 Supabase 연동 완료

**상태:** ✅ 완료
- Streamlit 앱이 정상 실행
- Supabase 데이터가 대시보드에 표시
- GitHub에 모든 코드 커밋 및 푸시
- 환경 설정 가이드 문서 작성

---

## 2. Git 저장소 초기화

### 2.1 로컬 저장소 초기화

```bash
git init
git remote add origin https://github.com/jiyong0202/jiyong.git
git branch -M streamlit
```

### 2.2 Git 사용자 설정

```bash
git config --global user.email "nanreal820202@gmail.com"
git config --global user.name "jiyong"
```

### 2.3 첫 커밋

```bash
git add .
git commit -m "Add Streamlit dashboard project with data collection and management scripts"
git push -u origin streamlit
```

---

## 3. 프로젝트 구조

```
jiyong/
├── .streamlit/
│   └── secrets.toml          # Supabase 연결 정보 (보안 - git 제외)
├── .gitignore               # git에서 추적할 파일 제외
├── app.py                   # 메인 Streamlit 앱
├── requirements.txt         # Python 패키지 목록
├── SETUP_GUIDE.md          # 이 문서
├── development_requests.csv # 샘플 데이터
├── collect_schedule_data.py # 데이터 수집 스크립트
├── scrape_*.py             # 웹 스크래핑 스크립트
└── ... (기타 파일들)
```

### 3.1 주요 파일 설명

| 파일 | 설명 |
|------|------|
| `app.py` | Streamlit 대시보드 메인 앱 |
| `requirements.txt` | 필요한 Python 패키지 목록 |
| `.streamlit/secrets.toml` | Supabase 인증정보 (git 제외) |
| `.gitignore` | git에서 제외할 파일/폴더 |
| `SETUP_GUIDE.md` | 환경 설정 가이드 문서 |

---

## 4. Python 패키지 관리

### 4.1 의존성 설치

```bash
pip install -r requirements.txt
```

### 4.2 requirements.txt 내용

```txt
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
openpyxl>=3.1.0
selenium>=4.10.0
beautifulsoup4>=4.12.0
requests>=2.31.0
httpx>=0.26.0
```

### 4.3 패키지 설명

| 패키지 | 용도 |
|--------|------|
| `streamlit` | 대시보드 UI 프레임워크 |
| `pandas` | 데이터 처리 및 분석 |
| `plotly` | 대화형 차트 및 그래프 |
| `httpx` | Supabase API 통신 |
| `openpyxl` | Excel 파일 처리 |
| `selenium` | 웹 자동화 및 스크래핑 |
| `beautifulsoup4` | HTML/XML 파싱 |
| `requests` | HTTP 요청 |

---

## 5. Supabase 설정

### 5.1 Supabase 프로젝트 생성

1. [Supabase](https://supabase.com) 접속
2. 새 프로젝트 생성
3. Settings → API에서 정보 확인

### 5.2 .streamlit/secrets.toml 파일 생성

**위치:** `C:\jiyong\.streamlit\secrets.toml`

**내용:**
```toml
supabase_url = "https://[your-project].supabase.co"
supabase_key = "sb_publishable_[your-key]"
```

**예시:**
```toml
supabase_url = "https://wxinpgftwueeocfwsyqt.supabase.co"
supabase_key = "sb_publishable_RIH7gPUM2AQxrzPu9Tj-HQ_vYPAuhkR"
```

### 5.3 Supabase 테이블 생성

**테이블 이름:** `development_requests`

**필수 컬럼:**
```sql
- request_number (TEXT)
- request_datetime (TIMESTAMP)
- request_department (TEXT)
- requester (TEXT)
- request_received_datetime (TIMESTAMP)
- development_start_datetime (TIMESTAMP)
- development_completion_target_date (DATE)
- development_manager (TEXT)
- it_biz_manager (TEXT)
- task_title (TEXT)
- request_content (TEXT)
- progress_status (TEXT)  -- '완료', '진행중', '대기'
```

### 5.4 Supabase 연결 테스트

```bash
python << 'EOF'
import requests
import json

supabase_url = "https://wxinpgftwueeocfwsyqt.supabase.co"
supabase_key = "sb_publishable_RIH7gPUM2AQxrzPu9Tj-HQ_vYPAuhkR"

headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json"
}

url = f"{supabase_url}/rest/v1/development_requests?select=*&limit=1"
response = requests.get(url, headers=headers, timeout=10)

if response.status_code == 200:
    print("✅ 연결 성공!")
    data = response.json()
    if data:
        print("테이블 컬럼:", list(data[0].keys()))
else:
    print(f"❌ 연결 실패: {response.status_code}")
EOF
```

---

## 6. Streamlit 실행

### 6.1 로컬에서 실행

```bash
# 1단계: 의존성 설치
pip install -r requirements.txt

# 2단계: Streamlit 앱 실행
python -m streamlit run app.py
```

### 6.2 접속 주소

- **Local:** `http://localhost:8501`
- **Network:** `http://192.168.10.106:8501`

### 6.3 앱 종료

터미널에서 **Ctrl+C** 입력

### 6.4 캐시 초기화

```bash
# Windows PowerShell
Remove-Item -Path $env:USERPROFILE\.streamlit\cache -Recurse -Force

# MacOS/Linux
rm -rf ~/.streamlit/cache
```

---

## 7. GitHub 배포

### 7.1 Streamlit Cloud에 배포

1. [Streamlit Community Cloud](https://share.streamlit.io) 접속
2. GitHub 계정으로 로그인
3. "New app" → streamlit 브랜치 선택
4. Deploy

### 7.2 Streamlit Cloud Secrets 설정

**Settings → Secrets에 다음 추가:**
```toml
supabase_url = "https://wxinpgftwueeocfwsyqt.supabase.co"
supabase_key = "sb_publishable_RIH7gPUM2AQxrzPu9Tj-HQ_vYPAuhkR"
```

### 7.3 커밋 및 푸시

```bash
# 변경사항 확인
git status

# 파일 추가
git add app.py requirements.txt .gitignore

# 커밋
git commit -m "Update Streamlit dashboard with Supabase integration"

# 푸시
git push origin streamlit
```

---

## 8. 자주 하는 실수와 해결법

| 문제 | 원인 | 해결법 |
|------|------|--------|
| `ModuleNotFoundError` | 패키지 미설치 | `pip install -r requirements.txt` |
| `KeyError: 'column_name'` | 컬럼명 불일치 | Supabase 테이블 컬럼명 확인 |
| Supabase 연결 실패 | API 키 오류 | secrets.toml 파일 확인 |
| 캐시 문제 | Streamlit 캐시 오래됨 | 캐시 초기화 후 재시작 |
| `secrets.toml` 찾을 수 없음 | 잘못된 경로 | `.streamlit/secrets.toml` 위치 확인 |
| 파일 경로 오류 | 절대 경로 사용 | `os.path.join(os.path.dirname(__file__), ...)` 사용 |

---

## 9. 참고 자료

- [Streamlit 공식 문서](https://docs.streamlit.io)
- [Supabase 공식 문서](https://supabase.com/docs)
- [Streamlit Community Cloud](https://share.streamlit.io)
- [Supabase Community Cloud](https://supabase.com)
- [Python requests 라이브러리](https://requests.readthedocs.io)
- [httpx 라이브러리](https://www.python-httpx.org)

---

## 10. 유용한 Git 명령어

```bash
# 저장소 상태 확인
git status

# 변경 내용 보기
git diff

# 최근 커밋 확인
git log --oneline -5

# 파일 추가 및 커밋
git add <filename>
git commit -m "Commit message"

# 모든 파일 커밋
git add .
git commit -m "Commit message"

# 원격 저장소에 푸시
git push origin streamlit

# 특정 파일의 변경 이력 보기
git log --oneline <filename>

# 이전 커밋으로 돌아가기
git checkout <commit-hash>
```

---

**최종 업데이트:** 2026-06-04  
**작성자:** Claude Code  
**프로젝트:** Streamlit 대시보드 + Supabase 통합
