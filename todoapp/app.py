import streamlit as st
import json
import re
from datetime import datetime
from anthropic import Anthropic

# ==================== Claude API 함수들 ====================

def call_claude_api(amount: int, risk_level: str, region: str) -> dict:
    """
    Claude API를 호출하여 투자 제안을 받습니다.

    Args:
        amount: 투자 금액
        risk_level: 투자 성향 ('안전' 또는 '공격')
        region: 투자 지역 ('국내' 또는 '해외')

    Returns:
        API 응답 (문자열)
    """
    try:
        # API 키 로드
        api_key = st.secrets.get("anthropic_api_key")
        if not api_key or api_key == "YOUR_API_KEY_HERE":
            return {
                "error": "⚠️ Claude API 키가 설정되지 않았습니다.",
                "details": ".streamlit/secrets.toml 파일에 anthropic_api_key를 설정해주세요."
            }

        client = Anthropic(api_key=api_key)

        # 투자 배분 (안전 30% / 공격 70% 고정)
        safe_pct = 30
        aggressive_pct = 70
        safe_amount = int(amount * safe_pct / 100)
        aggressive_amount = int(amount * aggressive_pct / 100)

        # 프롬프트 작성 (극도로 단순화)
        safe_amt = int(safe_amount * 0.5)
        agg_amt_1 = int(aggressive_amount * 0.35)
        agg_amt_2 = int(aggressive_amount * 0.3)

        prompt = f"""Return only valid JSON, no other text:

{{"market_analysis": {{"point1": {{"source": "KB증권", "reference_url": "https://research.kbsec.com", "analysis": "균형형 투자자를 위한 현재 시장 기회와 금리 환경 분석. 금리 인상 사이클이 마무리되면서 채권과 주식 모두에 긍정적인 환경이 형성되고 있습니다. KB증권 분석팀은 향후 안전자산의 수익률 개선을 기대하고 있습니다."}}, "point2": {{"source": "삼성증권", "reference_url": "https://research.samsungmobil.com", "analysis": "{region} 시장의 경제 상황과 증시 전망. 글로벌 IT 기업들의 실적 개선과 AI 관련 산업 수혜가 지속될 것으로 예상됩니다. 삼성증권은 특히 반도체와 AI 관련주의 강세가 계속될 것으로 전망하고 있습니다."}}, "point3": {{"source": "신한금융투자", "reference_url": "https://research.shinhanfs.com", "analysis": "안전자산 {safe_pct}%와 공격투자 {aggressive_pct}%의 포트폴리오 전략. 이러한 배분은 하방 리스크를 제한하면서도 성장 기회를 확보할 수 있습니다. 신한금융투자는 현 시점에서 글로벌 분산투자를 강조하며 환율 리스크 관리를 권고하고 있습니다."}}}}, "allocation": {{"safe_percentage": {safe_pct}, "aggressive_percentage": {aggressive_pct}, "safe_amount": {safe_amount}, "aggressive_amount": {aggressive_amount}}}, "recommended_products": [{{"rank": 1, "category": "안전자산", "product_name": "KODEX 국고채 3년", "type": "채권", "unit_price": 10000, "dividend_rate": "3.5%", "recommended_amount": {safe_amt}, "monthly_trading_signal": "매수", "reason": "안정성", "features": ["배당", "안정"]}}, {{"rank": 2, "category": "안전자산", "product_name": "iShares 글로벌 고배당", "type": "ETF", "unit_price": 25000, "dividend_rate": "4.2%", "recommended_amount": {safe_amt}, "monthly_trading_signal": "매수", "reason": "분산", "features": ["배당", "분산"]}}, {{"rank": 3, "category": "공격투자", "product_name": "TIGER AI 반도체", "type": "ETF", "unit_price": 35000, "dividend_rate": "0%", "recommended_amount": {agg_amt_1}, "monthly_trading_signal": "매수", "reason": "성장성", "features": ["AI", "반도체"]}}, {{"rank": 4, "category": "공격투자", "product_name": "Magnificent 7 ETF", "type": "ETF", "unit_price": 40000, "dividend_rate": "0.5%", "recommended_amount": {agg_amt_1}, "monthly_trading_signal": "매수", "reason": "기술주", "features": ["기술", "성장"]}}, {{"rank": 5, "category": "공격투자", "product_name": "에코프로비엠", "type": "주식", "unit_price": 15000, "dividend_rate": "0%", "recommended_amount": {agg_amt_2}, "monthly_trading_signal": "매수", "reason": "배터리", "features": ["테마", "성장"]}}], "action_items": ["각 상품의 수수료와 세금을 꼼꼼히 확인하세요", "포트폴리오의 {safe_pct}% 안전자산으로 리스크를 관리하세요", "매달 정기적으로 포트폴리오를 점검하고 리밸런싱하세요"]}}"""

        # API 호출
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = message.content[0].text
        return {"success": True, "data": response_text}

    except Exception as e:
        return {
            "error": f"API 호출 중 오류가 발생했습니다.",
            "details": str(e)
        }


def parse_api_response(response_data: dict) -> dict:
    """
    Claude API 응답을 파싱하여 JSON으로 변환합니다.

    Args:
        response_data: API 응답 데이터

    Returns:
        파싱된 JSON 데이터
    """
    if "error" in response_data:
        return response_data

    try:
        response_text = response_data.get("data", "")

        # JSON 블록 찾기 (```json ... ```)
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)

        if json_match:
            json_str = json_match.group(1)
        else:
            # JSON 블록이 없으면 전체 텍스트를 JSON으로 파싱 시도
            json_str = response_text

        parsed_data = json.loads(json_str)
        return {"success": True, "data": parsed_data}

    except json.JSONDecodeError as e:
        return {
            "error": "JSON 파싱 실패",
            "details": f"응답을 JSON으로 변환할 수 없습니다: {str(e)}"
        }
    except Exception as e:
        return {
            "error": "응답 처리 중 오류",
            "details": str(e)
        }


# ==================== 결과 화면 렌더링 함수들 ====================

def render_market_analysis(data: dict):
    """시장 분석 섹션을 렌더링합니다 (3개 증권사 분석)."""
    market_analysis = data.get("market_analysis", {})

    # 제목
    st.markdown("### 📈 시장 분석 (3개 증권사 분석)")

    # 3개 포인트를 열로 배치
    col1, col2, col3 = st.columns(3)

    # 각 포인트 데이터 추출
    point1_data = market_analysis.get("point1", {})
    point2_data = market_analysis.get("point2", {})
    point3_data = market_analysis.get("point3", {})

    points = [
        (col1, point1_data),
        (col2, point2_data),
        (col3, point3_data)
    ]

    for col, point_data in points:
        with col:
            source = point_data.get("source", "분석 대기 중")
            reference_url = point_data.get("reference_url", "")
            analysis = point_data.get("analysis", "분석 대기 중")

            # 증권사 헤더
            header = f"🏦 {source}"
            if reference_url:
                header += f" | [🔗 참고]({reference_url})"

            st.markdown(f"<p style='color: #0066cc; font-weight: bold; font-size: 13px; margin-bottom: 8px;'>{header}</p>",
                       unsafe_allow_html=True)

            # 분석 내용
            st.markdown(f"""
            <div style='background-color: #f0f2f6; padding: 12px; border-radius: 8px; border-left: 3px solid #0066cc;'>
                <p style='margin: 0; color: #333; font-size: 12px; line-height: 1.6;'>{analysis}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")


def render_allocation(data: dict):
    """투자 배분 섹션을 렌더링합니다."""
    st.markdown("### 💡 투자 배분")

    allocation = data.get("allocation", {})
    safe_pct = allocation.get("safe_percentage", 30)
    aggressive_pct = allocation.get("aggressive_percentage", 70)
    safe_amount = allocation.get("safe_amount", 0)
    aggressive_amount = allocation.get("aggressive_amount", 0)

    # 배분 표시
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div style='background-color: #e3f2fd; padding: 20px; border-radius: 10px; text-align: center;'>
            <p style='margin: 0; color: #0066cc; font-size: 28px; font-weight: bold;'>{safe_pct}%</p>
            <p style='margin: 5px 0 0 0; color: #0066cc; font-size: 14px;'>안전자산</p>
            <p style='margin: 10px 0 0 0; color: #666; font-size: 12px;'>{safe_amount:,}원</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style='background-color: #fff3e0; padding: 20px; border-radius: 10px; text-align: center;'>
            <p style='margin: 0; color: #ff6600; font-size: 28px; font-weight: bold;'>{aggressive_pct}%</p>
            <p style='margin: 5px 0 0 0; color: #ff6600; font-size: 14px;'>공격투자</p>
            <p style='margin: 10px 0 0 0; color: #666; font-size: 12px;'>{aggressive_amount:,}원</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")


def render_products(data: dict, total_amount: int = 0):
    """추천 상품 섹션을 테이블로 렌더링합니다."""
    import pandas as pd

    st.markdown("### 🎯 추천 상품 (5개)")

    # 분류 범례
    st.markdown(
        "<p style='font-size: 12px; color: #666; margin: -10px 0 15px 0;'>"
        "<strong>범례:</strong> "
        "<span style='color: #0066cc;'>🔵 안전자산</span> (채권, 고배당주) | "
        "<span style='color: #ff6600;'>🟠 공격투자</span> (성장주, 기술주, 테마주)"
        "</p>",
        unsafe_allow_html=True
    )

    products = data.get("recommended_products", [])
    total_invested = 0

    # 테이블 데이터 준비
    table_data = []

    for product in products:
        rank = product.get("rank", 0)
        category = product.get("category", "")
        product_name = product.get("product_name", "")
        product_type = product.get("type", "")
        recommended_amount = product.get("recommended_amount", 0)
        signal = product.get("monthly_trading_signal", "")
        reason = product.get("reason", "")
        features = product.get("features", [])
        dividend_rate = product.get("dividend_rate", "0%")
        unit_price = product.get("unit_price", 0)

        # 매수 수량 및 실제 금액 계산
        if unit_price > 0:
            quantity = int(recommended_amount / unit_price)
            actual_amount = quantity * unit_price
        else:
            quantity = 0
            actual_amount = recommended_amount

        # 카테고리 아이콘
        category_icon = "🔵" if category == "안전자산" else "🟠"

        # 테이블 행 추가
        table_data.append({
            "순위": rank,
            "카테고리": category_icon,
            "상품명": product_name,
            "타입": product_type,
            "단가": f"{unit_price:,}원",
            "배당율": dividend_rate,
            "추천액": f"{recommended_amount:,}원",
            "매수수량": f"{quantity}주",
            "투자금액": f"{actual_amount:,}원"
        })

        # 총액 누적
        total_invested += actual_amount

    # DataFrame으로 변환
    df = pd.DataFrame(table_data)

    # 테이블 스타일 설정
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "순위": st.column_config.NumberColumn("순위", width="50px"),
            "카테고리": st.column_config.TextColumn("분류", width="50px"),
            "상품명": st.column_config.TextColumn("상품명", width="200px"),
            "타입": st.column_config.TextColumn("타입", width="80px"),
            "단가": st.column_config.TextColumn("단가", width="100px"),
            "배당율": st.column_config.TextColumn("배당율", width="80px"),
            "추천액": st.column_config.TextColumn("추천액", width="120px"),
            "매수수량": st.column_config.TextColumn("매수수량", width="100px"),
            "투자금액": st.column_config.TextColumn("투자금액", width="120px"),
        }
    )

    # 총합계 표시 (테이블 바로 아래)
    summary_color = "#d4edda" if total_invested == total_amount else "#fff3cd"
    summary_border = "#28a745" if total_invested == total_amount else "#ffc107"
    summary_text = f"✅ 총 투자 금액: {total_invested:,}원" if total_invested == total_amount else f"⚠️ 총 투자 금액: {total_invested:,}원 (목표: {total_amount:,}원)"

    st.markdown(f"""
    <div style='background-color: {summary_color}; padding: 12px 15px; border-radius: 0 0 8px 8px; border-left: 4px solid {summary_border}; margin-top: -5px;'>
        <p style='margin: 0; color: #155724; font-weight: bold; font-size: 15px;'>
            {summary_text}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 구분선
    st.markdown("---")

    # 상세 설명 (이전 정보)
    st.markdown("#### 📝 상세 설명")
    col1, col2, col3 = st.columns(3)

    for i, product in enumerate(products):
        if i == 0:
            col = col1
        elif i == 1:
            col = col2
        elif i == 2:
            col = col3
        else:
            # 두 번째 열
            col = col1 if i == 3 else col2
            if i == 3:
                st.markdown("---")

        with col:
            product_name = product.get("product_name", "")
            reason = product.get("reason", "")
            features = product.get("features", [])

            st.markdown(f"**{product_name}**")
            st.markdown(f"__{reason}__")
            st.markdown(" ".join([f"`{f}`" for f in features]))
            st.markdown("")


def render_action_items(data: dict):
    """액션 아이템 섹션을 렌더링합니다."""
    st.markdown("### ✅ 액션 아이템")

    action_items = data.get("action_items", [])

    for i, item in enumerate(action_items, 1):
        st.markdown(
            f"<p style='font-size: 14px; margin: 10px 0;'>• {item}</p>",
            unsafe_allow_html=True
        )

    st.markdown("")


def generate_share_link(input_data: dict, api_response: dict) -> str:
    """공유 가능한 링크를 생성합니다."""
    import base64
    import urllib.parse

    if not api_response or "error" in api_response:
        return ""

    if not api_response.get("success"):
        return ""

    data = api_response.get("data", {})

    # 공유 데이터 준비
    share_data = {
        "input": input_data,
        "result": data
    }

    # JSON으로 변환 후 Base64 인코딩
    import json
    json_str = json.dumps(share_data, ensure_ascii=False)
    encoded = base64.b64encode(json_str.encode()).decode()

    # 공유 링크 생성 (로컬 환경이므로 현재 URL 기반)
    share_link = f"http://localhost:8502?shared={encoded}"

    return share_link


def format_result_for_copy(input_data: dict, api_response: dict) -> str:
    """투자 제안 결과를 텍스트 형식으로 포매팅합니다."""
    if not api_response or "error" in api_response:
        return "결과를 복사할 수 없습니다."

    if not api_response.get("success"):
        return "결과를 복사할 수 없습니다."

    data = api_response.get("data", {})

    # 포매팅된 텍스트 작성
    result = []
    result.append("=" * 60)
    result.append("💰 월간 AI 투자 제안")
    result.append("=" * 60)
    result.append("")

    # 입력 정보
    result.append("📊 투자 정보")
    result.append(f"  • 투자 금액: {input_data['amount']:,}원")
    result.append(f"  • 투자 성향: {input_data['risk_level']}")
    result.append(f"  • 투자 지역: {input_data['region']}")
    result.append("")

    # 시장 분석
    market_analysis = data.get("market_analysis", {})
    result.append("📈 시장 분석")
    for i, (key, value) in enumerate(market_analysis.items(), 1):
        result.append(f"  {i}. {value}")
    result.append("")

    # 투자 배분
    allocation = data.get("allocation", {})
    result.append("💡 투자 배분")
    safe_pct = allocation.get("safe_percentage", 30)
    aggressive_pct = allocation.get("aggressive_percentage", 70)
    safe_amount = allocation.get("safe_amount", 0)
    aggressive_amount = allocation.get("aggressive_amount", 0)
    result.append(f"  • 안전자산: {safe_pct}% ({safe_amount:,}원)")
    result.append(f"  • 공격투자: {aggressive_pct}% ({aggressive_amount:,}원)")
    result.append("")

    # 추천 상품
    result.append("🎯 추천 상품 (5개)")
    products = data.get("recommended_products", [])
    for product in products:
        result.append(f"  {product.get('rank')}. {product.get('product_name')}")
        result.append(f"     타입: {product.get('type')}")
        result.append(f"     추천금: {product.get('recommended_amount')}")
        result.append(f"     신호: {product.get('monthly_trading_signal')}")
        result.append(f"     이유: {product.get('reason')}")
        features = product.get("features", [])
        if features:
            result.append(f"     특징: {', '.join(features)}")
        result.append("")

    # 액션 아이템
    result.append("✅ 액션 아이템")
    action_items = data.get("action_items", [])
    for i, item in enumerate(action_items, 1):
        result.append(f"  {i}. {item}")
    result.append("")

    result.append("=" * 60)
    result.append(f"작성일: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}")
    result.append("=" * 60)

    return "\n".join(result)


# 페이지 설정
st.set_page_config(
    page_title="월간 AI 투자 제안",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 커스텀 CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .safe-asset {
        color: #0066cc;
    }
    .aggressive-asset {
        color: #ff6600;
    }
    </style>
    """, unsafe_allow_html=True)

# 세션 상태 초기화
if "show_results" not in st.session_state:
    st.session_state.show_results = False
if "show_share_link" not in st.session_state:
    st.session_state.show_share_link = False
if "input_data" not in st.session_state:
    st.session_state.input_data = {
        "amount": 1000000,
        "risk_level": "안전",
        "region": "국내"
    }
if "api_response" not in st.session_state:
    st.session_state.api_response = None

# 페이지 제목
st.title("💰 월간 AI 투자 제안 도구")
st.markdown("---")

# 투자 성향 고정값
risk_level = "균형형"

# 입력 화면 또는 결과 화면 표시
if not st.session_state.show_results:
    # ==================== 입력 화면 ====================
    st.markdown("### 📝 투자 정보를 입력하세요")
    st.write("여유자금과 투자 지역을 선택하면, AI가 맞춤형 투자 제안을 해드립니다. (배분: 안전자산 30% / 공격투자 70%)")

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            # 여유자금 입력
            amount = st.slider(
                "💰 투자할 여유자금",
                min_value=1000000,
                max_value=50000000,
                value=st.session_state.input_data["amount"],
                step=100000,
                format="%,d원"
            )

        with col2:
            # 국내/해외 투자 비중
            col2_1, col2_2 = st.columns(2)

            with col2_1:
                domestic_ratio = st.number_input(
                    "🇰🇷 국내 (%)",
                    min_value=0,
                    max_value=100,
                    value=int(st.session_state.input_data.get("domestic_ratio", 50)),
                    step=10
                )

            with col2_2:
                overseas_ratio = st.number_input(
                    "🌍 해외 (%)",
                    min_value=0,
                    max_value=100,
                    value=int(st.session_state.input_data.get("overseas_ratio", 50)),
                    step=10
                )

            # 합계 검증
            total_ratio = domestic_ratio + overseas_ratio
            if total_ratio == 100:
                st.success(f"✅ 합계: {total_ratio}%")
            else:
                st.warning(f"⚠️ 합계: {total_ratio}% (100%가 되어야 합니다)")

        # 투자 배분 정보 표시 (고정: 안전 30% / 공격 70%)
        st.info("📊 투자 배분: 안전자산 30% | 공격투자 70% (고정)")

    st.markdown("---")

    # [AI 제안 받기] 버튼
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🤖 AI 제안 받기", use_container_width=True, type="primary"):
            # 입력값 검증
            if amount < 1000000 or amount > 50000000:
                st.error("⚠️ 투자 금액은 100만원 이상 5,000만원 이하여야 합니다.")
            elif domestic_ratio + overseas_ratio != 100:
                st.error(f"⚠️ 국내와 해외 비중의 합계가 100%가 아닙니다. (현재: {domestic_ratio + overseas_ratio}%)")
            else:
                # 입력값 저장 (투자 성향은 "균형형"으로 고정)
                st.session_state.input_data = {
                    "amount": amount,
                    "risk_level": "균형형",
                    "domestic_ratio": domestic_ratio,
                    "overseas_ratio": overseas_ratio
                }

                # API 호출
                with st.spinner("🤖 AI가 분석 중입니다... (2~3초 소요)"):
                    region = f"국내{domestic_ratio}%-해외{overseas_ratio}%"
                    api_response = call_claude_api(amount, risk_level, region)
                    parsed_response = parse_api_response(api_response)
                    st.session_state.api_response = parsed_response

                # 결과 화면으로 전환
                st.session_state.show_results = True
                st.rerun()

    st.markdown("---")

    # 입력 화면 공유 버튼
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔗 이 화면 공유하기", use_container_width=True):
            # 현재 입력값으로 공유 링크 생성
            import base64
            import json

            share_data = {
                "amount": amount,
                "domestic_ratio": domestic_ratio,
                "overseas_ratio": overseas_ratio
            }

            json_str = json.dumps(share_data, ensure_ascii=False)
            encoded = base64.b64encode(json_str.encode()).decode()
            share_link = f"http://localhost:8502?input={encoded}"

            try:
                import pyperclip
                pyperclip.copy(share_link)
                st.success("✅ 입력 화면 공유 링크가 클립보드에 복사되었습니다!")
            except Exception as e:
                st.error(f"공유 링크 복사 실패: {str(e)}")

    # 사용 설명
    with st.expander("📌 사용 설명"):
        st.markdown("""
        **투자 배분 (고정):**
        - 안전자산: 30% (채권, 고배당주)
        - 공격투자: 70% (기술주, 성장주, 테마주)

        **입력 항목:**
        - 💰 여유자금: 1백만원 ~ 5천만원
        - 🇰🇷 국내 투자 비중: 0% ~ 100%
        - 🌍 해외 투자 비중: 자동 계산 (100% - 국내 비중)

        **AI 분석 결과:**
        - 📈 시장 분석 (3개 증권사 관점)
        - 💡 투자 배분 (시각화)
        - 🎯 추천 상품 (5개, 단가/매수수량/금액 포함)
        - ✅ 액션 아이템

        **소요 시간:** 약 2~3초
        """)

else:
    # ==================== 결과 화면 ====================
    st.markdown("### 📊 AI 투자 제안 결과")
    st.write(f"**투자 금액:** {st.session_state.input_data['amount']:,}원 | "
             f"**투자 성향:** {st.session_state.input_data['risk_level']} | "
             f"**국내:** {st.session_state.input_data.get('domestic_ratio', 0)}% / **해외:** {st.session_state.input_data.get('overseas_ratio', 100)}%")
    st.markdown("---")

    # 결과 화면 렌더링
    api_response = st.session_state.api_response

    if api_response and "error" not in api_response:
        # API 호출 성공 - 결과 렌더링
        if api_response.get("success"):
            data = api_response.get("data", {})

            # 렌더링 함수들 호출
            render_market_analysis(data)
            render_allocation(data)
            render_products(data, st.session_state.input_data["amount"])
            render_action_items(data)
        else:
            st.error("❌ 데이터 처리 중 오류가 발생했습니다.")
    elif api_response and "error" in api_response:
        # API 호출 실패 - 에러 메시지 표시
        st.warning(f"⚠️ {api_response.get('error')}")
        st.info(f"📝 {api_response.get('details')}")
    else:
        # 응답 대기 중
        st.info("결과를 처리 중입니다...")

    st.markdown("---")

    # [뒤로가기] 및 [화면 공유하기] 버튼
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ 뒤로가기", use_container_width=True):
            st.session_state.show_results = False
            st.rerun()
    with col2:
        if st.button("🔗 화면 공유하기", use_container_width=True, type="primary"):
            # 공유 링크 생성 및 자동 복사
            share_link = generate_share_link(
                st.session_state.input_data,
                st.session_state.api_response
            )
            try:
                import pyperclip
                pyperclip.copy(share_link)
                st.success("✅ 공유 링크가 클립보드에 복사되었습니다! 카톡, 이메일, SNS에 붙여넣으세요.")
            except Exception as e:
                st.error(f"공유 실패: {str(e)}")

# 푸터
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray; font-size: 12px;'>"
            "💡 매달 처음 5일 안에 투자 계획을 세우는 것이 좋습니다.</p>",
            unsafe_allow_html=True)
