# CLAUDE.md

이 파일은 Claude Code(claude.ai/code)가 이 저장소의 코드로 작업할 때 참고할 지침을 제공합니다.

## 📊 프로젝트 개요

**월간 AI 투자 제안 도구**로, 사용자가 입력한 여유자금을 기반으로 AI가 자동으로 투자 배분을 추천하고 맞춤형 투자 제안을 제시하는 웹 애플리케이션입니다.

**기술 스택:**
- **프론트엔드/프레임워크**: Streamlit (웹 UI 프레임워크)
- **AI**: Claude API (Anthropic)
- **HTTP 클라이언트**: httpx (Claude API 호출용)
- **데이터 처리**: json (JSON 형식 응답 처리)

---

## 🏗️ 아키텍처

### 데이터 흐름
1. 사용자가 웹 앱에 접속 (`http://localhost:8501`)
2. 사용자가 투자 정보 입력:
   - 여유자금 (금액)
   - 투자 성향 (안전/공격)
   - 투자 지역 (국내/해외)
3. [AI 제안 받기] 버튼 클릭 → 로딩 화면 표시
4. Claude API에 구조화된 프롬프트 전송
5. API 응답을 JSON으로 파싱
6. 결과 화면에 다음 항목 렌더링:
   - 📈 시장 분석 (3개 포인트)
   - 💡 투자 배분 (안전 30% / 공격 70% 고정)
   - 🎯 추천 상품 5개 (상품명, 타입, 추천 금액, 이유, 특징)
   - ✅ 액션 아이템 (3개)
7. [결과 복사하기] 버튼으로 한 번에 클립보드 복사

### 주요 UI 흐름

| 화면 | 설명 |
|------|------|
| **입력 화면** | 여유자금, 투자 성향, 투자 지역 입력 필드 + [AI 제안 받기] 버튼 |
| **로딩 화면** | 애니메이션 + "AI가 분석 중입니다..." (약 2~3초) |
| **결과 화면** | 분석 내용, 배분, 추천 상품, 액션 아이템 + [결과 복사하기] 버튼 |

### 투자 비중 (고정)
- **안전자산 30%**: KODEX 국고채 3년, iShares 글로벌 고배당
- **공격투자 70%**: TIGER AI 반도체, Magnificent 7, 에코프로비엠

### 월간 인기 상품 (5개 고정)
1. KODEX 국고채 3년 (안전자산)
2. iShares 글로벌 고배당 ETF (안전자산)
3. TIGER AI 반도체 ETF (공격투자)
4. Magnificent 7 ETF (공격투자)
5. 에코프로비엠 / 롯데정밀화학 (공격투자)

---

## 🚀 자주 사용하는 명령어

### 초기 설정
```powershell
# 가상환경 생성
python -m venv .venv

# 활성화 (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# 의존성 설치
pip install -r requirements.txt
```

### 앱 실행
```powershell
# 가상환경 활성화 후 실행
python -m streamlit run app.py
```
앱은 `http://localhost:8501`에서 접속 가능

### 앱 종료
터미널에서 `Ctrl+C` 입력

### Streamlit 캐시 초기화
```powershell
Remove-Item -Path $env:USERPROFILE\.streamlit\cache -Recurse -Force
```

---

## ⚙️ 설정

### Claude API 인증정보
프로젝트 루트에 `.streamlit/secrets.toml` 파일 생성:
```toml
anthropic_api_key = "sk-ant-[your-key]"
```

**보안:** `.streamlit/secrets.toml`을 `.gitignore`에 추가하여 절대 커밋하지 않기.

### Streamlit 설정
`.streamlit/config.toml` (선택사항):
```toml
[theme]
primaryColor = "#FF6B6B"
```

---

## 💡 중요한 구현 세부사항

### Claude API 프롬프트 구조
Claude API에 보낼 프롬프트는 다음 JSON 형식의 응답을 기대합니다:

```json
{
  "market_analysis": {
    "point1": "시장 분석 포인트 1",
    "point2": "시장 분석 포인트 2",
    "point3": "시장 분석 포인트 3"
  },
  "allocation": {
    "safe_percentage": 30,
    "aggressive_percentage": 70,
    "safe_amount": 금액,
    "aggressive_amount": 금액
  },
  "recommended_products": [
    {
      "rank": 1,
      "category": "안전자산 or 공격투자",
      "product_name": "상품명",
      "type": "상품타입",
      "recommended_amount": 금액,
      "monthly_trading_signal": "거래신호",
      "reason": "추천이유",
      "features": ["특징1", "특징2"]
    }
  ],
  "action_items": ["액션1", "액션2", "액션3"]
}
```

### JSON 응답 파싱
Claude API 응답에서 JSON을 추출할 때:
1. 응답 텍스트에서 ````json ... ```" 블록 찾기
2. `json.loads()`로 파싱
3. 파싱 실패 시 사용자에게 오류 메시지 표시

### 결과 복사 기능
`pyperclip` 라이브러리 사용:
```python
import pyperclip
# 결과를 텍스트로 포매팅 후
pyperclip.copy(formatted_text)
```

### 로딩 애니메이션
Streamlit의 내장 기능 사용:
```python
with st.spinner("AI가 분석 중입니다..."):
    # API 호출 및 처리
```

---

## 📁 파일 구조

```
.
├── app.py                          # 메인 Streamlit 앱
├── requirements.txt                # Python 패키지 목록
├── .streamlit/
│   ├── config.toml                # Streamlit 설정 (선택사항)
│   └── secrets.toml               # Claude API 키 (git 제외)
├── .gitignore
├── prd.md                         # 제품 요구사항 문서
└── CLAUDE.md                      # 이 파일
```

---

## 🛠️ 핵심 개발 포인트

### Streamlit 세션 상태 관리
- `st.session_state`를 사용하여 화면 전환 시 상태 유지
- 예: `st.session_state.show_results` (입력 vs 결과 화면 표시)

### API 에러 처리
Claude API 호출 시 다음 에러 처리 필수:
- `httpx.TimeoutException`: 타임아웃 발생 시 재시도 로직
- `httpx.HTTPError`: HTTP 에러 시 사용자 안내
- JSON 파싱 에러: 응답 형식 검증

### 금액 포매팅
모든 금액은 한글 세 자리 수 구분 기호로 표시:
```python
f"{amount:,}원"  # 예: 1,000,000원
```

### 타입 힌팅
Python 타입 힌팅 사용하여 코드 가독성 향상:
```python
def get_investment_recommendation(amount: int, risk_level: str) -> dict:
    ...
```

---

## ⚠️ 주의사항

### 사용자 입력 검증
- 여유자금: 100만원 이상 5,000만원 이하만 허용
- 유효하지 않은 값 입력 시 명확한 오류 메시지 표시

### API 비용 관리
Claude API는 토큰 기반 요금 청구. 프롬프트 길이와 응답 길이를 최소화하되, 품질 유지.

### 하드코딩된 데이터
투자 상품 5개와 비중(30/70)은 프로그램 내 하드코딩. 향후 데이터베이스 연동 시 고려.

---

## 🐛 디버깅

### 자주 발생하는 문제

| 문제 | 해결 방법 |
|------|---------|
| "API 키를 찾을 수 없습니다" | `secrets.toml` 파일 존재 여부 및 `anthropic_api_key` 확인 |
| JSON 파싱 에러 | Claude API 응답 형식이 예상 JSON과 일치하는지 확인 |
| 결과 복사 버튼 동작 안 함 | `pyperclip` 라이브러리 설치 여부 확인 |
| 로딩이 너무 길다 | API 타임아웃 또는 네트워크 문제 - 인터넷 연결 확인 |

### 로컬 테스트
앱 실행 후 다음 시나리오 테스트:
1. 여유자금만 입력 후 제출
2. 전체 정보 입력 후 제출 → 결과 복사
3. 다시 다른 금액으로 제출

---

## 📝 단계별 개발 가이드

### Phase 1: 프로젝트 초기 설정 & 기본 UI 구축
**목표:** 입력 폼과 세션 상태 관리 구현

**구현 항목:**
- `requirements.txt` 작성 (streamlit, httpx, python-dotenv)
- `app.py` 기본 구조 (페이지 제목, 설명)
- `.streamlit/secrets.toml` 설정 (API 키 로드)
- 입력 섹션 UI:
  - 💰 여유자금 입력 (슬라이더 또는 숫자 입력 1M~50M)
  - 🎯 투자 성향 선택 (라디오 버튼: 안전/공격)
  - 🌍 투자 지역 선택 (라디오 버튼: 국내/해외)
  - [AI 제안 받기] 버튼
- 세션 상태 관리:
  - `st.session_state.show_results`: 입력 vs 결과 화면 표시
  - `st.session_state.input_data`: 사용자 입력값 저장

**검증:**
```bash
python -m streamlit run app.py
# 브라우저에서 입력 폼이 정상 표시되는지 확인
# 입력값 변경 후 [AI 제안 받기] 클릭하면 상태 변경 확인
```

**산출물:**
- `app.py` (200줄 내외)
- `requirements.txt`

---

### Phase 2: Claude API 연동 & 응답 파싱
**목표:** Claude API 호출 및 JSON 응답 처리 구현

**구현 항목:**
- Claude API 호출 함수 `call_claude_api()`:
  - 입력 파라미터: 여유자금, 투자 성향, 투자 지역
  - Anthropic SDK 또는 httpx로 API 호출
  - 구조화된 프롬프트 작성 (JSON 응답 형식 지정)
  - 타임아웃 설정 (기본 30초)
- JSON 응답 파싱 함수 `parse_api_response()`:
  - 응답에서 JSON 블록 추출 (```json ... ```)
  - `json.loads()`로 파싱
  - 스키마 검증 (필수 필드 확인)
- 에러 처리:
  - API 키 누락 시 안내 메시지
  - 네트워크 에러 시 사용자 알림
  - JSON 파싱 실패 시 재시도 또는 오류 메시지

**검증:**
```python
# test_api.py에서 직접 테스트
from app import call_claude_api, parse_api_response

result = call_claude_api(amount=3000000, risk="공격", region="국내")
parsed = parse_api_response(result)
print(parsed)  # JSON 구조 확인
```

**산출물:**
- `app.py` 내 함수 추가 (100줄 내외)
- `test_api.py` (API 연동 테스트 스크립트)

---

### Phase 3: 결과 화면 UI 구축
**목표:** Claude API 응답을 보기 좋게 렌더링

**구현 항목:**
- 결과 화면 레이아웃:
  ```
  ┌─────────────────────────────────┐
  │ 📈 시장 분석                    │
  │  • 포인트 1                     │
  │  • 포인트 2                     │
  │  • 포인트 3                     │
  ├─────────────────────────────────┤
  │ 💡 투자 배분                    │
  │  • 안전자산 30% (금액)          │
  │  • 공격투자 70% (금액)          │
  ├─────────────────────────────────┤
  │ 🎯 추천 상품 (5개)              │
  │  1. [상품명] | 타입             │
  │     추천금: 금액                │
  │     신호: 거래신호              │
  │     이유: ...                   │
  │     특징: #태그1 #태그2         │
  ├─────────────────────────────────┤
  │ ✅ 액션 아이템                  │
  │  1. 액션 항목 1                 │
  │  2. 액션 항목 2                 │
  │  3. 액션 항목 3                 │
  ├─────────────────────────────────┤
  │ [뒤로가기] [결과 복사하기]      │
  └─────────────────────────────────┘
  ```
- 함수 작성:
  - `render_market_analysis()`: 시장 분석 섹션
  - `render_allocation()`: 배분 섹션 (진행 막대 차트)
  - `render_products()`: 추천 상품 섹션
  - `render_action_items()`: 액션 아이템 섹션
- 스타일링:
  - 컬러: 안전자산(파랑), 공격투자(주황)
  - 폰트: 금액은 굵게, 특징은 태그 스타일

**검증:**
```bash
# Phase 2의 test_api.py 출력 결과를 이용해
# 결과 화면 UI 시각적 확인
python -m streamlit run app.py
# 샘플 데이터로 결과 화면 렌더링 테스트
```

**산출물:**
- `app.py` 내 렌더 함수 추가 (150줄 내외)

---

### Phase 4: 입력값 검증 & 로딩 애니메이션
**목표:** UX 개선 및 데이터 무결성 보장

**구현 항목:**
- 입력값 검증 함수 `validate_input()`:
  - 여유자금: 1,000,000 이상 50,000,000 이하
  - 투자 성향: '안전' 또는 '공격'
  - 투자 지역: '국내' 또는 '해외'
  - 검증 실패 시 `st.error()` 표시
- 로딩 애니메이션:
  ```python
  with st.spinner("🤖 AI가 분석 중입니다... (2~3초 소요)"):
      result = call_claude_api(...)
  ```
- [AI 제안 받기] 버튼 클릭 시:
  - 입력값 검증
  - API 호출 (로딩 표시)
  - 결과 저장 및 화면 전환

**검증:**
```bash
# 잘못된 입력값으로 테스트
# 예: 50만원 입력 → 오류 메시지 표시 확인
# 예: 5천만원 입력 → 오류 메시지 표시 확인
# 정상 입력 → 로딩 화면 표시 후 결과 화면 이동 확인
```

**산출물:**
- `app.py` 내 검증 함수 추가 (50줄 내외)

---

### Phase 5: 결과 복사 기능 & 뒤로가기
**목표:** 사용자 편의성 완성

**구현 항목:**
- 결과 복사 함수 `format_result_for_copy()`:
  - 결과를 텍스트 형식으로 포매팅
  - 예:
    ```
    📊 월간 AI 투자 제안
    ━━━━━━━━━━━━━━━━━━━━━━
    📈 시장 분석
    • 포인트 1
    • 포인트 2
    • 포인트 3
    ...
    ```
- `pyperclip` 또는 Streamlit 내장 함수로 클립보드 복사
- [결과 복사하기] 버튼:
  - 클릭 시 "복사되었습니다!" 메시지 표시
  - 3초 후 자동 사라지기
- [뒤로가기] 버튼:
  - 입력 화면으로 돌아가기
  - 세션 상태 초기화

**검증:**
```bash
# [결과 복사하기] 클릭 후 메모장에 붙여넣기
# 포매팅이 정상인지 확인
# [뒤로가기] 클릭 후 입력 폼이 초기화되는지 확인
```

**산출물:**
- `app.py` 내 포매팅 함수 추가 (50줄 내외)

---

### Phase 6: 전체 통합 테스트 & 최적화
**목표:** 전체 기능 검증 및 성능 최적화

**테스트 시나리오:**
1. **정상 플로우:**
   - 여유자금 3백만원, 공격 성향, 국내 선택 → [AI 제안 받기]
   - 결과 화면 표시 확인
   - [결과 복사하기] → 클립보드 확인
   - [뒤로가기] → 입력 폼으로 이동 확인

2. **에러 케이스:**
   - 여유자금 50만원 입력 → 오류 메시지 표시
   - 여유자금 1억원 입력 → 오류 메시지 표시
   - API 키 누락 → 안내 메시지 표시
   - 네트워크 끊김 시뮬레이션 → 타임아웃 처리

3. **성능 테스트:**
   - API 응답 시간 측정 (목표: 2~3초)
   - Streamlit 캐싱 고려 (필요시 추가)
   - 메모리 사용량 확인

**최적화 항목:**
- 불필요한 API 호출 제거
- 응답 형식 최적화 (토큰 절감)
- UI 반응성 개선

**산출물:**
- `test_e2e.py` (엔드-투-엔드 테스트)
- `requirements.txt` 최종 버전
- README.md (사용자 가이드)

---

## 각 Phase별 예상 소요 시간
| Phase | 내용 | 예상 시간 |
|-------|------|---------|
| 1 | 초기 설정 & 기본 UI | 30분 |
| 2 | Claude API 연동 | 1시간 |
| 3 | 결과 화면 UI | 1시간 |
| 4 | 검증 & 애니메이션 | 30분 |
| 5 | 복사 기능 & 뒤로가기 | 30분 |
| 6 | 통합 테스트 & 최적화 | 1시간 |
| **총합** | | **약 4.5시간** |

---

## 각 Phase 완료 후 체크리스트

### Phase 1 완료 후
- [ ] `python -m streamlit run app.py` 실행 가능
- [ ] 입력 폼이 정상 표시됨
- [ ] 입력값이 세션 상태에 저장됨

### Phase 2 완료 후
- [ ] Claude API 호출 성공
- [ ] JSON 응답 파싱 성공
- [ ] 파싱된 데이터 구조 확인 (test_api.py로)

### Phase 3 완료 후
- [ ] 결과 화면이 예쁘게 렌더링됨
- [ ] 모든 섹션(시장분석, 배분, 상품, 액션)이 표시됨
- [ ] 금액 포매팅 (세 자리 쉼표) 확인

### Phase 4 완료 후
- [ ] 잘못된 금액 입력 시 오류 메시지 표시
- [ ] 로딩 애니메이션 표시됨
- [ ] 버튼 클릭으로 화면 전환 작동

### Phase 5 완료 후
- [ ] [결과 복사하기] 버튼 작동
- [ ] 복사된 텍스트 포매팅 확인
- [ ] [뒤로가기] 버튼 작동

### Phase 6 완료 후
- [ ] 모든 테스트 시나리오 통과
- [ ] 오류 메시지가 명확함
- [ ] API 응답 시간 2~3초 내

---

## 📚 참고 자료

- Streamlit 공식 문서: https://docs.streamlit.io
- Claude API 가이드: `anthropic-sdk` 패키지 문서
- PRD 상세 스펙: 이 디렉토리의 `prd.md` 참고
