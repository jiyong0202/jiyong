# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time
import json

options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--disable-blink-features=AutomationControlled')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    print("편성표 페이지 접속 중...")
    driver.get("https://hsmoa.com/show-program-home")

    # 페이지 로딩 대기
    time.sleep(4)

    # 페이지 텍스트 추출
    page_text = driver.find_element(By.TAG_NAME, "body").text
    print("페이지 텍스트 (처음 2000자):")
    print(page_text[:2000])

    # 모든 요소 검사
    print("\n\n=== 페이지 구조 분석 ===")

    # 테이블 찾기
    tables = driver.find_elements(By.TAG_NAME, "table")
    print(f"테이블 개수: {len(tables)}")

    if tables:
        for i, table in enumerate(tables):
            rows = table.find_elements(By.TAG_NAME, "tr")
            print(f"\nTable {i}: {len(rows)} 행")

            # 테이블 데이터 추출
            table_data = []
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, ["td", "th"])
                row_data = [cell.text.strip() for cell in cells]
                table_data.append(row_data)

            # 첫 5개 행 출력
            for j, row_data in enumerate(table_data[:5]):
                print(f"  Row {j}: {row_data}")

    # 편성표 정보를 포함한 div 찾기
    all_divs = driver.find_elements(By.TAG_NAME, "div")
    print(f"\n전체 div 개수: {len(all_divs)}")

    # class 속성을 검사해서 편성표 관련 요소 찾기
    schedule_data = []
    for div in all_divs:
        class_attr = div.get_attribute("class") or ""
        if any(keyword in class_attr.lower() for keyword in ['schedule', 'program', 'broadcast', 'channel']):
            text = div.text.strip()
            if text and len(text) > 0:
                schedule_data.append({
                    "class": class_attr,
                    "text": text[:200]
                })

    print(f"\n편성 관련 div ({len(schedule_data)}개):")
    for item in schedule_data[:10]:
        print(f"  Class: {item['class'][:50]}")
        print(f"  Text: {item['text']}\n")

    # 모든 링크 수집 (홈쇼핑 채널별)
    links = driver.find_elements(By.TAG_NAME, "a")
    print(f"\n전체 링크 개수: {len(links)}")

    for link in links:
        text = link.text.strip()
        href = link.get_attribute("href")
        if text and href:
            print(f"  {text} -> {href}")

finally:
    driver.quit()
