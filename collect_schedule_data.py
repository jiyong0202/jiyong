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
from datetime import datetime, timedelta

options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--disable-blink-features=AutomationControlled')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# 데이터 저장소
all_data = {
    'schedule': [],  # 편성표
    'products': []   # 상품
}

try:
    print("웹사이트 접속 중...")
    driver.get("https://hsmoa.com/")
    time.sleep(4)

    # 네트워크 요청 모니터링을 위해 콘솔 메시지 확인
    # JavaScript에서 데이터 추출
    print("\n=== JavaScript 데이터 추출 ===")

    try:
        # window 객체에서 데이터 확인
        data = driver.execute_script("""
            // Next.js의 __NEXT_DATA__ 확인
            if (window.__NEXT_DATA__) {
                return {
                    'nextData': 'found',
                    'keys': Object.keys(window.__NEXT_DATA__)
                };
            }

            // 페이지의 모든 데이터 출력
            return {
                'window_keys': Object.keys(window).filter(k => k.includes('schedule') || k.includes('program') || k.includes('broadcast')),
                'page_title': document.title
            };
        """)
        print("JavaScript 결과:", json.dumps(data, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"JavaScript 실행 오류: {e}")

    # 날짜 선택 요소 찾기
    print("\n=== 날짜 선택 요소 찾기 ===")
    date_inputs = driver.find_elements(By.TAG_NAME, "input")
    print(f"입력 요소 개수: {len(date_inputs)}")

    for i, inp in enumerate(date_inputs[:5]):
        input_type = inp.get_attribute("type")
        input_id = inp.get_attribute("id")
        input_name = inp.get_attribute("name")
        print(f"  Input {i}: type={input_type}, id={input_id}, name={input_name}")

    # 드롭다운/선택 요소 찾기
    print("\n=== 드롭다운 요소 찾기 ===")
    selects = driver.find_elements(By.TAG_NAME, "select")
    print(f"Select 요소 개수: {len(selects)}")

    for i, select in enumerate(selects):
        options_list = select.find_elements(By.TAG_NAME, "option")
        print(f"  Select {i}: {len(options_list)} 옵션")
        for j, opt in enumerate(options_list[:5]):
            print(f"    - {opt.text}")

    # 모든 버튼 찾기
    print("\n=== 버튼 요소 찾기 ===")
    buttons = driver.find_elements(By.TAG_NAME, "button")
    print(f"버튼 개수: {len(buttons)}")

    for i, btn in enumerate(buttons[:10]):
        btn_text = btn.text.strip()
        btn_class = btn.get_attribute("class")
        if btn_text:
            print(f"  Button {i}: {btn_text[:30]}")

    # 현재 페이지의 모든 텍스트 콘텐츠 추출
    print("\n=== 페이지 콘텐츠 추출 ===")
    body = driver.find_element(By.TAG_NAME, "body")

    # 편성표 관련 정보
    print("\nSchedule divs:")
    schedule_divs = driver.find_elements(By.CSS_SELECTOR, "[class*='schedule']")
    for div in schedule_divs:
        text = div.text.strip()
        if text and len(text) < 500:
            print(f"  {text[:100]}")

    # 상품 정보 추출
    print("\n\n=== 상품 정보 추출 ===")
    product_containers = driver.find_elements(By.CSS_SELECTOR, "[class*='product'], [class*='item'], [data-product]")
    print(f"상품 컨테이너 개수: {len(product_containers)}")

    products_data = []
    for container in product_containers[:20]:  # 처음 20개만
        try:
            product_text = container.text.strip()
            if product_text and len(product_text) > 10:
                # 가격, 할인율 등 추출
                lines = product_text.split('\n')
                if len(lines) >= 2:
                    products_data.append({
                        'name': lines[0][:100],
                        'raw_text': product_text[:200]
                    })
        except:
            pass

    print(f"\n수집된 상품 ({len(products_data)}개):")
    for product in products_data[:10]:
        print(f"  상품명: {product['name']}")
        print(f"  정보: {product['raw_text']}\n")

    # 현재 URL 확인
    print(f"\n현재 URL: {driver.current_url}")

finally:
    driver.quit()
    print("\n수집 완료")
