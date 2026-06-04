import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import json

# hsmoa.com에서 편성표 데이터 수집
url = "https://hsmoa.com/"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = 'utf-8'

    print(f"Status Code: {response.status_code}")
    print(f"URL: {response.url}")

    soup = BeautifulSoup(response.content, 'html.parser')

    # 페이지 구조 분석
    print("\n=== 페이지 구조 분석 ===")

    # 주요 컨테이너 찾기
    containers = soup.find_all(['div', 'section', 'table'], class_=True)

    # 홈쇼핑 관련 데이터 찾기
    all_text = soup.get_text()

    # 편성표 관련 키워드 확인
    keywords = ['편성', '시간', '방송', '프로그램', 'CJ', 'GS', 'NS', 'WM', 'SK']
    found_keywords = [kw for kw in keywords if kw in all_text]
    print(f"발견된 키워드: {found_keywords}")

    # JSON 데이터 찾기 (API 응답 형태)
    scripts = soup.find_all('script', type='application/json')
    print(f"\nJSON 스크립트 개수: {len(scripts)}")

    if scripts:
        for i, script in enumerate(scripts[:3]):  # 처음 3개만
            try:
                data = json.loads(script.string)
                print(f"\nScript {i} keys: {list(data.keys())[:5]}")
            except:
                print(f"Script {i}: JSON 파싱 실패")

    # 테이블 찾기
    tables = soup.find_all('table')
    print(f"\n테이블 개수: {len(tables)}")

    if tables:
        for i, table in enumerate(tables[:2]):
            rows = table.find_all('tr')
            cols = table.find_all('th')
            print(f"Table {i}: {len(rows)}행, {len(cols)}열")

    # 특정 div 구조 찾기
    divs_with_text = [div.get('class', []) for div in soup.find_all('div') if 'schedule' in str(div.get('class', [])).lower() or 'program' in str(div.get('class', [])).lower()]
    print(f"\n편성 관련 div 클래스: {divs_with_text[:5]}")

    # 저장된 HTML 일부 확인
    print("\n=== 페이지 소스 일부 (최대 500자) ===")
    print(all_text[:500])

except Exception as e:
    print(f"에러: {e}")
    import traceback
    traceback.print_exc()
