import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="개발 진행 현황", layout="wide")

@st.cache_data
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), "development_requests.csv")
    df = pd.read_csv(file_path, encoding='utf-8-sig')

    date_columns = ['요청일시', '요청접수일시', '개발시작일시', '개발완료목표일자']
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    today = pd.Timestamp(datetime.now().date())
    df['남은일수'] = (df['개발완료목표일자'] - today).dt.days

    df['진행률'] = 0.0
    mask_in_progress = df['진행상태'] == '진행중'
    mask_has_start = df['개발시작일시'].notna()

    valid_mask = mask_in_progress & mask_has_start
    if valid_mask.any():
        start_dates = df.loc[valid_mask, '개발시작일시']
        end_dates = df.loc[valid_mask, '개발완료목표일자']
        total_days = (end_dates - start_dates).dt.days
        elapsed_days = (today - start_dates).dt.days
        progress = (elapsed_days / total_days.clip(lower=1) * 100).clip(0, 100)
        df.loc[valid_mask, '진행률'] = progress.values

    return df

def get_status_color(status):
    colors = {
        '완료': '#2ecc71',
        '진행중': '#3498db',
        '대기': '#f39c12'
    }
    return colors.get(status, '#95a5a6')

def apply_filters(df, status_filter, dept_filter, dev_filter, manager_filter=None):
    result = df[
        (df['진행상태'].isin(status_filter)) &
        (df['요청부서'].isin(dept_filter)) &
        (df['개발담당자'].isin(dev_filter))
    ]

    if manager_filter:
        result = result[result['IT비즈담당자'].isin(manager_filter)]

    return result

def render_metric_card(col, label, value, color='#3498db'):
    with col:
        st.markdown(f"""
            <div style="background-color: {color}; padding: 20px; border-radius: 10px; text-align: center;">
                <p style="color: white; margin: 0; font-size: 14px;">{label}</p>
                <p style="color: white; margin: 5px 0 0 0; font-size: 32px; font-weight: bold;">{value}</p>
            </div>
        """, unsafe_allow_html=True)

df = load_data()

st.title("📊 개발 진행 현황")
st.markdown("---")

if 'filters' not in st.session_state:
    st.session_state.filters = {
        'status': list(df['진행상태'].unique()),
        'dept': list(df['요청부서'].unique()),
        'dev': list(df['개발담당자'].unique()),
        'manager': list(df['IT비즈담당자'].unique())
    }

filtered_df = apply_filters(
    df,
    st.session_state.filters['status'],
    st.session_state.filters['dept'],
    st.session_state.filters['dev'],
    st.session_state.filters['manager']
)

total_count = len(filtered_df)
completed_count = len(filtered_df[filtered_df['진행상태'] == '완료'])
in_progress_count = len(filtered_df[filtered_df['진행상태'] == '진행중'])
waiting_count = len(filtered_df[filtered_df['진행상태'] == '대기'])

col1, col2, col3, col4 = st.columns(4)

render_metric_card(col1, "전체 건수", total_count, '#34495e')
render_metric_card(col2, "완료", completed_count, '#2ecc71')
render_metric_card(col3, "진행중", in_progress_count, '#3498db')
render_metric_card(col4, "대기", waiting_count, '#f39c12')

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["📈 현황 분석", "📋 상세 데이터", "👥 담당자별 현황", "📅 타임라인"])

with tab1:
    st.subheader("현황 분석")

    col1, col2 = st.columns(2)

    with col1:
        status_counts = filtered_df['진행상태'].value_counts()
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="진행상태별 현황",
            color_discrete_map={
                '완료': '#2ecc71',
                '진행중': '#3498db',
                '대기': '#f39c12'
            }
        )
        fig_status.update_layout(height=400)
        st.plotly_chart(fig_status, use_container_width=True)

    with col2:
        dept_counts = filtered_df['요청부서'].value_counts().sort_values(ascending=True)
        fig_dept = px.bar(
            x=dept_counts.values,
            y=dept_counts.index,
            title="부서별 요청 현황",
            labels={'x': '건수', 'y': '부서'},
            color=dept_counts.values,
            color_continuous_scale='Blues',
            orientation='h'
        )
        fig_dept.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_dept, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        dev_counts = filtered_df['개발담당자'].value_counts().sort_values(ascending=False)
        fig_dev = px.bar(
            x=dev_counts.index,
            y=dev_counts.values,
            title="개발담당자별 작업량",
            labels={'x': '개발담당자', 'y': '건수'},
            color=dev_counts.values,
            color_continuous_scale='Greens'
        )
        fig_dev.update_layout(height=400, showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig_dev, use_container_width=True)

    with col4:
        daily_counts = filtered_df.groupby(filtered_df['요청일시'].dt.date).size()
        fig_daily = px.line(
            x=daily_counts.index,
            y=daily_counts.values,
            title="일일 요청 현황",
            labels={'x': '요청일시', 'y': '건수'},
            markers=True
        )
        fig_daily.update_traces(fill='tozeroy')
        fig_daily.update_layout(height=400, hovermode='x unified')
        st.plotly_chart(fig_daily, use_container_width=True)

with tab2:
    st.subheader("상세 데이터")

    col1, col2, col3 = st.columns(3)

    with col1:
        status_options = st.multiselect(
            "진행상태",
            options=df['진행상태'].unique(),
            default=st.session_state.filters['status'],
            key='tab2_status'
        )
        st.session_state.filters['status'] = status_options

    with col2:
        dept_options = st.multiselect(
            "요청부서",
            options=df['요청부서'].unique(),
            default=st.session_state.filters['dept'],
            key='tab2_dept'
        )
        st.session_state.filters['dept'] = dept_options

    with col3:
        dev_options = st.multiselect(
            "개발담당자",
            options=df['개발담당자'].unique(),
            default=st.session_state.filters['dev'],
            key='tab2_dev'
        )
        st.session_state.filters['dev'] = dev_options

    with st.expander("추가 필터"):
        col_exp1, col_exp2 = st.columns(2)

        with col_exp1:
            manager_options = st.multiselect(
                "IT비즈담당자",
                options=df['IT비즈담당자'].unique(),
                default=st.session_state.filters['manager'],
                key='tab2_manager'
            )
            st.session_state.filters['manager'] = manager_options

        with col_exp2:
            pass

    filtered_df = apply_filters(
        df,
        st.session_state.filters['status'],
        st.session_state.filters['dept'],
        st.session_state.filters['dev'],
        st.session_state.filters['manager']
    )

    display_df = filtered_df[[
        '요청번호', '요청일시', '요청부서', '요청자', '일감제목',
        '진행상태', '개발담당자', 'IT비즈담당자', '개발완료목표일자', '남은일수'
    ]].copy()

    display_df['요청일시'] = display_df['요청일시'].dt.strftime('%Y-%m-%d %H:%M')
    display_df['개발완료목표일자'] = display_df['개발완료목표일자'].dt.strftime('%Y-%m-%d')

    display_df = display_df.sort_values('요청일시', ascending=False)

    st.markdown(f"**표시된 건수: {len(display_df)} / 전체: {len(df)}**")

    st.dataframe(
        display_df,
        use_container_width=True,
        height=600,
        hide_index=True
    )

with tab3:
    st.subheader("IT비즈담당자별 현황")

    filtered_df = apply_filters(
        df,
        st.session_state.filters['status'],
        st.session_state.filters['dept'],
        st.session_state.filters['dev'],
        st.session_state.filters['manager']
    )

    managers = sorted(filtered_df['IT비즈담당자'].unique())

    for manager in managers:
        manager_df = filtered_df[filtered_df['IT비즈담당자'] == manager]
        total_tasks = len(manager_df)
        in_progress = len(manager_df[manager_df['진행상태'] == '진행중'])
        completed = len(manager_df[manager_df['진행상태'] == '완료'])

        with st.expander(f"👤 {manager} ({total_tasks})"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("담당 건수", total_tasks)
            with col2:
                st.metric("진행중", in_progress)
            with col3:
                st.metric("완료", completed)

            st.divider()

            task_df = manager_df[[
                '요청번호', '요청부서', '개발담당자', '일감제목',
                '진행상태', '개발완료목표일자'
            ]].copy()

            task_df['개발완료목표일자'] = task_df['개발완료목표일자'].dt.strftime('%Y-%m-%d')
            task_df = task_df.sort_values('요청번호')

            st.dataframe(
                task_df,
                use_container_width=True,
                hide_index=True
            )

with tab4:
    st.subheader("타임라인")

    filtered_df = apply_filters(
        df,
        st.session_state.filters['status'],
        st.session_state.filters['dept'],
        st.session_state.filters['dev'],
        st.session_state.filters['manager']
    )

    timeline_df = filtered_df[[
        '요청번호', '일감제목', '요청일시', '개발완료목표일자',
        '진행상태', '개발담당자', '남은일수', '진행률'
    ]].copy()

    timeline_df = timeline_df.sort_values('요청일시')

    timeline_df['Task'] = timeline_df['요청번호'] + ' - ' + timeline_df['일감제목'].str[:20]

    fig = px.timeline(
        timeline_df,
        x_start='요청일시',
        x_end='개발완료목표일자',
        y='Task',
        color='진행상태',
        hover_data=['개발담당자', '남은일수'],
        color_discrete_map={
            '완료': '#2ecc71',
            '진행중': '#3498db',
            '대기': '#f39c12'
        },
        title="개발 요청 타임라인"
    )

    fig.update_layout(
        height=max(400, len(timeline_df) * 25),
        hovermode='y unified',
        xaxis_title='날짜',
        yaxis_title='',
    )

    today = datetime.now().date()
    fig.add_vline(x=pd.Timestamp(today), line_dash='dash', line_color='red', annotation_text='오늘')

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown(f"*마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
