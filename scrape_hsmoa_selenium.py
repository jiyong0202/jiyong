# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time

# Chrome 드라이버 설정
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    print("웹사이트 접속 중...")
    driver.get("https://hsmoa.com/")

    # 페이지 로딩 대기
    time.sleep(3)

    # 편성표 데이터 추출
    print("데이터 추출 중...")

    # 현재 가능한 모든 텍스트 추출
    page_text = driver.find_element(By.TAG_NAME, "body").text
    print("\n=== 페이지 텍스트 (처음 1000자) ===")
    print(page_text[:1000])

    # 모든 링크 수집
    links = driver.find_elements(By.TAG_NAME, "a")
    print(f"\n=== 발견된 링크 개수: {len(links)} ===")

    schedule_links = []
    for link in links:
        href = link.get_attribute("href")
        text = link.text.strip()
        if href and text:
            # 편성표 관련 링크 필터링
            if any(keyword in text.lower() or keyword in (href or '').lower()
                   for keyword in ['편성', 'schedule', 'program', 'cj', 'gs', 'ns', 'wm', 'sk']):
                schedule_links.append({"text": text, "href": href})

    print(f"\n편성표 관련 링크 ({len(schedule_links)}개):")
    for link in schedule_links[:10]:
        print(f"  {link['text']} -> {link['href']}")

    # 테이블 데이터 추출
    tables = driver.find_elements(By.TAG_NAME, "table")
    print(f"\n=== 테이블 개수: {len(tables)} ===")

    if tables:
        for i, table in enumerate(tables[:2]):
            rows = table.find_elements(By.TAG_NAME, "tr")
            print(f"\nTable {i}: {len(rows)}개 행")

            # 첫 5개 행 출력
            for j, row in enumerate(rows[:5]):
                cells = row.find_elements(By.TAG_NAME, ["td", "th"])
                cell_texts = [cell.text.strip() for cell in cells]
                print(f"  Row {j}: {cell_texts}")

    # div 요소에서 편성표 데이터 찾기
    schedule_divs = driver.find_elements(By.CSS_SELECTOR, "[class*='schedule'], [class*='program']")
    print(f"\n=== 편성 관련 div 개수: {len(schedule_divs)} ===")

    if schedule_divs:
        for i, div in enumerate(schedule_divs[:3]):
            text = div.text.strip()[:200]
            if text:
                print(f"Div {i}: {text}")

finally:
    driver.quit()
    print("\n브라우저 종료")
