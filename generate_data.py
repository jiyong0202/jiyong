import pandas as pd
from datetime import datetime, timedelta
import random

# 기존 팀과 요청자 유지
teams = [
    ('IT기획팀', '김철수'),
    ('마케팅팀', '박영미'),
    ('영업팀', '손민준'),
    ('고객서비스팀', '이현정'),
    ('운영팀', '장지훈'),
    ('상품기획팀', '정수진')
]

developers = ['이영희', '박준호', '최다영', '류지수', '김다은', '오승현', '정현우', '이미영', '최준호', '박영수']
it_biz_managers = ['강준호', '장수현', '임지은']

tasks = [
    '검색 기능 개선',
    '할인 쿠폰 시스템',
    '재고 대시보드',
    '문의 자동 분류',
    '배송 추적 개선',
    '카테고리 추가',
    '푸시 알림 기능',
    '매출 리포트',
    'SNS 공유 기능',
    '판매 실적 현황',
    '채팅 지원 시스템',
    '점포별 대시보드',
    '권한 관리 시스템',
    '이메일 마케팅',
    '리뷰 시스템',
    '일정 관리',
    'API 모니터링',
    '피드백 관리',
    '브랜드 포탈',
    '재고 자동화',
    '신상품 출시 관리',
    '데이터베이스 백업',
    '계약 관리',
    '설문조사 플랫폼',
    '광고 캠페인 관리',
    '보안 감시',
    '비용 관리',
    '번들 상품 관리',
    '로그 분석',
    'VOC 관리',
    '콘텐츠 관리',
    '고객 관계 관리',
    '배포 자동화',
    '자산 관리',
    '계절 상품 관리',
    '이슈 추적',
    '소셜 분석',
    '클라우드 마이그레이션',
    '인센티브 관리',
    '휴가 신청',
    '가격 전략',
    '만족도 조사',
    '네트워크 모니터링',
    '영상 마케팅',
    '거래처 관리',
    '교육 자료 관리',
    '상품 추천',
    'SLA 관리',
    '보안 패치',
    '세일 이벤트 관리'
]

data = []
req_num = 1
start_date = datetime(2026, 5, 1)

for i in range(50):
    request_date = start_date + timedelta(days=random.randint(0, 24))
    accept_date = request_date + timedelta(hours=random.randint(1, 6))

    team, requester = random.choice(teams)
    developer = random.choice(developers)
    it_biz = random.choice(it_biz_managers)

    status = random.choice(['완료', '진행중', '대기'])

    if status == '완료':
        start_date_time = accept_date + timedelta(days=random.randint(1, 3))
        target_date = start_date_time + timedelta(days=random.randint(7, 20))
    elif status == '진행중':
        start_date_time = accept_date + timedelta(days=random.randint(1, 3))
        target_date = start_date_time + timedelta(days=random.randint(7, 25))
    else:
        start_date_time = None
        target_date = accept_date + timedelta(days=random.randint(15, 40))

    task = tasks[i % len(tasks)]

    data.append({
        '요청번호': f'REQ-2026-{req_num:03d}',
        '요청일시': request_date.strftime('%Y-%m-%d %H:%M'),
        '요청부서': team,
        '요청자': requester,
        '요청접수일시': accept_date.strftime('%Y-%m-%d %H:%M'),
        '개발시작일시': start_date_time.strftime('%Y-%m-%d %H:%M') if start_date_time else '',
        '개발완료목표일자': target_date.strftime('%Y-%m-%d %H:%M'),
        '개발담당자': developer,
        'IT비즈담당자': it_biz,
        '일감제목': task,
        '요청내용': f'{team} {requester}님이 요청하신 {task}입니다.',
        '진행상태': status
    })
    req_num += 1

df = pd.DataFrame(data)
df.to_csv('c:\\jiyong\\development_requests.csv', index=False, encoding='utf-8-sig')
print('[완료] CSV 파일이 50줄로 업데이트되었습니다.')
