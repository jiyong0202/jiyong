# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    response = requests.get("https://hsmoa.com/", headers=headers, timeout=10)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.content, 'html.parser')

    # JSON 데이터 추출
    scripts = soup.find_all('script', type='application/json')

    all_data = {}
    if scripts:
        try:
            data = json.loads(scripts[0].string)
            all_data = data

            # 데이터 구조 분석
            if 'props' in data:
                props = data['props']
                print("Props keys:", list(props.keys())[:10])

                if 'initialState' in props:
                    state = props['initialState']
                    print("\ninitialState keys:", list(state.keys())[:10])

                if 'pageProps' in props:
                    page_props = props['pageProps']
                    print("\npageProps keys:", list(page_props.keys())[:10])

        except json.JSONDecodeError:
            print("JSON 파싱 실패")

    # 편성표 div 찾기
    schedule_divs = soup.find_all('div', class_=re.compile('schedule|program', re.I))
    print(f"\n편성표 div 개수: {len(schedule_divs)}")

    # 데이터 구조 분석
    for div in schedule_divs[:3]:
        print(f"\nDiv content sample: {div.get_text()[:100]}")

    # 링크 찾기 (홈쇼핑별 편성표)
    links = soup.find_all('a', href=True)
    schedule_links = [link for link in links if 'schedule' in link['href'].lower() or '편성' in link.get_text()]
    print(f"\n편성표 관련 링크 개수: {len(schedule_links)}")

    for link in schedule_links[:5]:
        print(f"Link: {link.get_text().strip()} -> {link['href']}")

    # 홈쇼핑 채널 찾기
    channel_texts = soup.find_all(text=re.compile(r'CJ|GS|NS|WM|SK|롯데', re.I))
    print(f"\n채널 키워드 발견: {len(channel_texts)}개")

    # 전체 페이지 텍스트에서 편성표 데이터 찾기
    page_text = soup.get_text()
    lines = [line.strip() for line in page_text.split('\n') if line.strip()]

    # 시간 패턴이 있는 라인 찾기
    time_pattern = re.compile(r'\d{1,2}:\d{2}')
    time_lines = [line for line in lines if time_pattern.search(line)]

    print(f"\n시간 정보 포함 라인: {len(time_lines)}개")
    for line in time_lines[:5]:
        print(f"  {line[:100]}")

except Exception as e:
    print(f"에러: {e}")
    import traceback
    traceback.print_exc()
