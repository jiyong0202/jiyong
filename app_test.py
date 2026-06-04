import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="개발 요청 관리 대시보드", layout="wide")

st.title("📊 개발 요청 관리 대시보드")
st.markdown("홈앤쇼핑 개발 요청 현황 및 관리 시스템")

df = pd.read_csv('c:\\jiyong\\development_requests.csv')

df['요청일시'] = pd.to_datetime(df['요청일시'])
df['요청접수일시'] = pd.to_datetime(df['요청접수일시'])
df['개발시작일시'] = pd.to_datetime(df['개발시작일시'], errors='coerce')
df['개발완료목표일자'] = pd.to_datetime(df['개발완료목표일자'])

df['상태'] = df['개발시작일시'].apply(lambda x: '진행중' if pd.notna(x) else '대기중')

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📋 총 요청 건수", len(df))
with col2:
    진행중 = len(df[df['상태'] == '진행중'])
    st.metric("⚙️ 진행중", 진행중)
with col3:
    대기중 = len(df[df['상태'] == '대기중'])
    st.metric("⏳ 대기중", 대기중)
with col4:
    개발담당자수 = df['개발담당자'].nunique()
    st.metric("👨‍💻 개발담당자", 개발담당자수)

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["📈 현황 분석", "📋 상세 데이터", "👥 담당자별", "📅 타임라인"])

with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("부서별 요청 현황")
        dept_count = df['요청부서'].value_counts()
        fig_dept = px.bar(
            x=dept_count.values,
            y=dept_count.index,
            orientation='h',
            labels={'x': '요청 건수', 'y': '부서'},
            color=dept_count.values,
            color_continuous_scale='Blues'
        )
        fig_dept.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_dept, use_container_width=True)

    with col2:
        st.subheader("요청 상태 분포")
        status_count = df['상태'].value_counts()
        fig_status = px.pie(
            values=status_count.values,
            names=status_count.index,
            labels={'values': '건수'},
            color_discrete_map={'진행중': '#1f77b4', '대기중': '#ff7f0e'}
        )
        fig_status.update_layout(height=400)
        st.plotly_chart(fig_status, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("개발담당자별 작업량")
        dev_count = df['개발담당자'].value_counts()
        fig_dev = px.bar(
            x=dev_count.index,
            y=dev_count.values,
            labels={'x': '개발담당자', 'y': '담당 건수'},
            color=dev_count.values,
            color_continuous_scale='Greens'
        )
        fig_dev.update_layout(height=400, showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig_dev, use_container_width=True)

    with col2:
        st.subheader("일일 요청 현황")
        df_sorted = df.sort_values('요청일시')
        daily_requests = df_sorted.groupby(df_sorted['요청일시'].dt.date).size()
        fig_timeline = px.line(
            x=daily_requests.index,
            y=daily_requests.values,
            labels={'x': '요청 날짜', 'y': '요청 건수'},
            markers=True
        )
        fig_timeline.update_layout(height=400, hovermode='x unified')
        st.plotly_chart(fig_timeline, use_container_width=True)

with tab2:
    st.subheader("전체 요청 데이터")

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        selected_status = st.multiselect("상태 필터", df['상태'].unique(), default=df['상태'].unique())

    with filter_col2:
        selected_dept = st.multiselect("부서 필터", df['요청부서'].unique(), default=df['요청부서'].unique())

    with filter_col3:
        selected_dev = st.multiselect("담당자 필터", df['개발담당자'].unique(), default=df['개발담당자'].unique())

    filtered_df = df[
        (df['상태'].isin(selected_status)) &
        (df['요청부서'].isin(selected_dept)) &
        (df['개발담당자'].isin(selected_dev))
    ].copy()

    display_df = filtered_df[[
        '요청번호', '요청부서', '요청자', '일감제목', '상태', '개발담당자', 'IT비즈담당자', '요청일시', '개발완료목표일자'
    ]].sort_values('요청일시', ascending=False)

    st.dataframe(display_df, use_container_width=True, height=600)

    st.markdown(f"**표시된 건수: {len(display_df)} / 전체: {len(df)}**")

with tab3:
    st.subheader("개발담당자별 상세 현황")

    for dev in sorted(df['개발담당자'].unique()):
        dev_data = df[df['개발담당자'] == dev]

        with st.expander(f"👤 {dev} ({len(dev_data)}건)"):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("담당 건수", len(dev_data))
            with col2:
                진행_건수 = len(dev_data[dev_data['상태'] == '진행중'])
                st.metric("진행중", 진행_건수)

            st.dataframe(
                dev_data.sort_values('요청일시', ascending=False)[[
                    '요청번호', '요청부서', '일감제목', '상태', '개발완료목표일자'
                ]],
                use_container_width=True
            )

with tab4:
    st.subheader("요청 처리 타임라인")

    timeline_df = df[['요청번호', '일감제목', '요청일시', '개발시작일시', '개발완료목표일자', '상태']].copy()
    timeline_df = timeline_df.sort_values('요청일시')

    for idx, row in timeline_df.iterrows():
        col1, col2 = st.columns([1, 4])

        with col1:
            if row['상태'] == '진행중':
                st.write("🟢")
            else:
                st.write("🟡")

        with col2:
            st.markdown(f"""
            **{row['요청번호']}** - {row['일감제목']}
            - 요청: {row['요청일시'].strftime('%Y-%m-%d %H:%M')}
            - 목표: {row['개발완료목표일자'].strftime('%Y-%m-%d')}
            - 상태: {row['상태']}
            """)

st.markdown("---")
st.caption("마지막 업데이트: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
