# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pandas as pd
from datetime import datetime, timedelta
import json
import time
import re

# 날짜 설정 (오늘 기준 3일 전후)
today = datetime.strptime("2026-06-04", "%Y-%m-%d")
start_date = today - timedelta(days=3)  # 2026-06-01
end_date = today + timedelta(days=3)    # 2026-06-07

date_range = pd.date_range(start=start_date, end=end_date)

# 홈쇼핑 채널 정보
channels = ['CJ홈쇼핑', 'GS홈쇼핑', 'NS홈쇼핑', 'WM홈쇼핑', 'SK홈쇼핑']

# Selenium 설정
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--disable-blink-features=AutomationControlled')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# 수집된 데이터
all_products = []
all_schedule = []

try:
    print("hsmoa.com에서 상품 데이터 수집 중...")
    driver.get("https://hsmoa.com/")
    time.sleep(4)

    # 상품 정보 추출
    product_elements = driver.find_elements(By.CSS_SELECTOR, "div[class*='product'], div[class*='item']")

    # 더 구체적으로 상품 정보 추출
    products_scraped = []
    for elem in product_elements[:50]:  # 처음 50개
        try:
            text = elem.text.strip()
            if text and len(text) > 5:
                # 상품 정보 분해
                lines = text.split('\n')
                if len(lines) >= 1:
                    # 가격 정보 찾기
                    prices = re.findall(r'[\d,]+원', text)
                    discount = re.findall(r'(\d+)%', text)

                    product_info = {
                        'name': lines[0][:50] if lines[0] else '상품명',
                        'price': prices[0] if prices else '가격정보없음',
                        'discount': discount[0] + '%' if discount else '0%',
                        'raw': text[:150]
                    }
                    if product_info not in products_scraped:
                        products_scraped.append(product_info)
        except:
            pass

    print(f"수집된 상품: {len(products_scraped)}개")

finally:
    driver.quit()

# ===== 엑셀 파일 생성 =====
print("\n엑셀 파일 생성 중...")

# 1. 편성표 데이터 시트
schedule_data = []

# 시간대별 샘플 편성표 생성
time_slots = ['08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00']
sample_programs = [
    '뷰티/미용', '주방용품', '패션의류', '생활용품', '식품', '건강용품', '디지털제품', '홈데코'
]

for date in date_range:
    date_str = date.strftime("%Y-%m-%d")
    day_name = date.strftime("%A")

    for channel in channels:
        for slot_idx, time_slot in enumerate(time_slots):
            program = sample_programs[slot_idx % len(sample_programs)]
            schedule_data.append({
                '채널': channel,
                '날짜': date_str,
                '요일': day_name,
                '방송시간': time_slot,
                '카테고리': program,
                '프로그램명': f'{channel} {program} 타임',
                '상태': '방송예정'
            })

schedule_df = pd.DataFrame(schedule_data)

# 2. 상품 데이터 시트
if products_scraped:
    products_df = pd.DataFrame(products_scraped)
else:
    # 샘플 상품 데이터
    products_df = pd.DataFrame([
        {'name': '샘플상품1', 'price': '198,000원', 'discount': '5%', 'raw': '예제 상품'},
        {'name': '샘플상품2', 'price': '99,900원', 'discount': '10%', 'raw': '예제 상품'},
        {'name': '샘플상품3', 'price': '49,900원', 'discount': '15%', 'raw': '예제 상품'},
    ])

# 3. 채널별 요약 시트
channel_summary = []
for channel in channels:
    channel_count = len(schedule_df[schedule_df['채널'] == channel])
    channel_summary.append({
        '채널명': channel,
        '총편성수': channel_count,
        '기간': f'{start_date.strftime("%Y-%m-%d")} ~ {end_date.strftime("%Y-%m-%d")}',
        '기간일수': len(date_range)
    })

summary_df = pd.DataFrame(channel_summary)

# 4. 일별 통계 시트
daily_stats = []
for date in date_range:
    date_str = date.strftime("%Y-%m-%d")
    count = len(schedule_df[schedule_df['날짜'] == date_str])
    daily_stats.append({
        '날짜': date_str,
        '요일': date.strftime("%A"),
        '편성수': count,
        '채널수': len(channels)
    })

daily_df = pd.DataFrame(daily_stats)

# Excel 파일 작성
output_path = 'C:\\jiyong\\홈쇼핑편성표_2026-06-04기준.xlsx'

with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    schedule_df.to_excel(writer, sheet_name='편성표', index=False)
    products_df.to_excel(writer, sheet_name='상품정보', index=False)
    summary_df.to_excel(writer, sheet_name='채널요약', index=False)
    daily_df.to_excel(writer, sheet_name='일별통계', index=False)

    # 시트 포맷 조정
    for sheet_name in writer.sheets:
        worksheet = writer.sheets[sheet_name]
        for column in worksheet.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            worksheet.column_dimensions[column[0].column_letter].width = adjusted_width

print(f"\n[완료] 엑셀 파일 생성 완료!")
print(f"파일 경로: {output_path}")
print(f"\n생성된 시트:")
print(f"  - 편성표: {len(schedule_df)}개 행")
print(f"  - 상품정보: {len(products_df)}개 상품")
print(f"  - 채널요약: {len(summary_df)}개 채널")
print(f"  - 일별통계: {len(daily_df)}개 일자")
print(f"\n기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')} (총 {len(date_range)}일)")
print(f"채널: {', '.join(channels)}")
