# Streamlit 대시보드 + Supabase 환경 설정 가이드

이 문서는 개발 진행 현황 대시보드를 Supabase와 함께 구축하는 전체 과정을 기록합니다.

---

## 📋 목차
1. [Git 저장소 초기화](#1-git-저장소-초기화)
2. [프로젝트 구조](#2-프로젝트-구조)
3. [Python 패키지 관리](#3-python-패키지-관리)
4. [Supabase 설정](#4-supabase-설정)
5. [Streamlit 실행](#5-streamlit-실행)
6. [GitHub 배포](#6-github-배포)

---

## 1. Git 저장소 초기화

### 1.1 로컬 저장소 초기화
```bash
git init
git remote add origin https://github.com/jiyong0202/jiyong.git
git branch -M streamlit
```

### 1.2 Git 사용자 설정
```bash
git config --global user.email "nanreal820202@gmail.com"
git config --global user.name "jiyong"
```

### 1.3 첫 커밋
```bash
git add .
git commit -m "Add Streamlit dashboard project with data collection and management scripts"
git push -u origin streamlit
```

---

## 2. 프로젝트 구조

```
jiyong/
├── .streamlit/
│   └── secrets.toml          # Supabase 연결 정보 (보안)
├── .gitignore               # git에서 추적할 파일 제외
├── app.py                   # 메인 Streamlit 앱
├── requirements.txt         # Python 패키지 목록
├── development_requests.csv # 샘플 데이터
├── SETUP_GUIDE.md          # 이 문서
└── ... (기타 파일들)
```

### 2.1 주요 파일 설명

| 파일 | 설명 |
|------|------|
| `app.py` | Streamlit 대시보드 메인 앱 |
| `requirements.txt` | 필요한 Python 패키지 목록 |
| `.streamlit/secrets.toml` | Supabase 인증정보 (git 제외) |
| `.gitignore` | git에서 제외할 파일/폴더 |

---

## 3. Python 패키지 관리

### 3.1 requirements.txt 생성

```bash
pip install -r requirements.txt
```

### 3.2 requirements.txt 내용

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

**패키지 설명:**
- `streamlit`: 대시보드 UI 프레임워크
- `pandas`: 데이터 처리
- `plotly`: 대화형 차트
- `httpx`: Supabase API 통신
- `openpyxl`: Excel 파일 처리
- `selenium`, `beautifulsoup4`: 웹 스크래핑

---

## 4. Supabase 설정

### 4.1 Supabase 프로젝트 생성

1. [Supabase](https://supabase.com) 접속
2. 새 프로젝트 생성
3. Settings → API에서 정보 확인

### 4.2 .streamlit/secrets.toml 파일 생성

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

### 4.3 Supabase 테이블 생성

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

### 4.4 Supabase 연결 테스트

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

print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✅ 연결 성공!")
else:
    print(f"❌ 연결 실패: {response.text}")
EOF
```

---

## 5. Streamlit 실행

### 5.1 로컬에서 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# Streamlit 앱 실행
python -m streamlit run app.py
```

**접속 주소:**
- Local: `http://localhost:8501`
- Network: `http://192.168.10.106:8501`

### 5.2 앱 종료

```bash
# 터미널에서 Ctrl+C 입력
```

### 5.3 캐시 초기화

```bash
rm -r $env:USERPROFILE\.streamlit\cache
```

---

## 6. GitHub 배포

### 6.1 Streamlit Cloud에 배포

1. [Streamlit Community Cloud](https://share.streamlit.io) 접속
2. GitHub 계정으로 로그인
3. "New app" → streamlit 브랜치 선택
4. Deploy

### 6.2 Streamlit Cloud Secrets 설정

**Settings → Secrets에 다음 추가:**
```toml
supabase_url = "https://wxinpgftwueeocfwsyqt.supabase.co"
supabase_key = "sb_publishable_RIH7gPUM2AQxrzPu9Tj-HQ_vYPAuhkR"
```

### 6.3 커밋 및 푸시

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

## 7. app.py 주요 코드

### 7.1 Supabase 데이터 로드

```python
import streamlit as st
import pandas as pd
import httpx

@st.cache_data(ttl=300)
def load_data():
    supabase_url = st.secrets.get("supabase_url")
    supabase_key = st.secrets.get("supabase_key")
    
    url = f"{supabase_url}/rest/v1/development_requests?select=*"
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }
    
    with httpx.Client() as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
    
    df = pd.DataFrame(data)
    return df
```

### 7.2 대시보드 메인 섹션

```python
st.set_page_config(page_title="개발 진행 현황", layout="wide")
st.title("📊 개발 진행 현황")

df = load_data()

# 메트릭 카드 표시
col1, col2, col3, col4 = st.columns(4)
col1.metric("전체 건수", len(df))
col2.metric("완료", len(df[df['progress_status'] == '완료']))
col3.metric("진행중", len(df[df['progress_status'] == '진행중']))
col4.metric("대기", len(df[df['progress_status'] == '대기']))

# 탭별 분석
tab1, tab2, tab3, tab4 = st.tabs(["📈 현황 분석", "📋 상세 데이터", "👥 담당자별 현황", "📅 타임라인"])
```

---

## 8. 자주 하는 실수와 해결법

| 문제 | 원인 | 해결법 |
|------|------|--------|
| ModuleNotFoundError | 패키지 미설치 | `pip install -r requirements.txt` |
| KeyError | 컬럼명 불일치 | Supabase 테이블 컬럼명 확인 |
| Supabase 연결 실패 | API 키 오류 | secrets.toml 파일 확인 |
| 캐시 문제 | Streamlit 캐시 오래됨 | 캐시 초기화 후 재시작 |

---

## 9. 유용한 명령어

```bash
# Git 상태 확인
git status

# 최근 커밋 확인
git log --oneline -5

# 파일 변경사항 확인
git diff

# 특정 파일만 커밋
git add <filename>
git commit -m "message"

# 모든 파일 커밋
git add .
git commit -m "message"

# 원격 저장소에 푸시
git push origin streamlit

# 캐시 삭제
rm -r ~/.streamlit/cache
```

---

## 10. 참고 자료

- [Streamlit 공식 문서](https://docs.streamlit.io)
- [Supabase 공식 문서](https://supabase.com/docs)
- [Streamlit Community Cloud](https://share.streamlit.io)
- [Supabase Community Cloud](https://supabase.com)

---

**최종 업데이트:** 2026-06-04
**작성자:** Claude Code

