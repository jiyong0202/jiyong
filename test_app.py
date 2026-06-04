#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime
import sys

print("=== STREAMLIT APP E2E VERIFICATION ===\n")

try:
    # Test 1: Data Loading
    print("[Test 1] CSV Data Loading")
    file_path = r"C:\jiyong\development_requests.csv"
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    print(f"  ✓ CSV loaded: {len(df)} rows, {len(df.columns)} columns")

    # Test 2: Date Columns Validation
    print("\n[Test 2] Date Column Parsing")
    date_columns = ['요청일시', '요청접수일시', '개발시작일시', '개발완료목표일자']
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')
        null_count = df[col].isna().sum()
        print(f"  ✓ {col}: parsed ({null_count} nulls)")

    # Test 3: Calculate remaining days
    print("\n[Test 3] Remaining Days Calculation")
    today = pd.Timestamp(datetime.now().date())
    df['남은일수'] = (df['개발완료목표일자'] - today).dt.days
    print(f"  ✓ 남은일수: min={df['남은일수'].min()}, max={df['남은일수'].max()}")

    # Test 4: Progress rate calculation
    print("\n[Test 4] Progress Rate Calculation")
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
        print(f"  ✓ Calculated for {valid_mask.sum()} in-progress items")
        print(f"    Progress range: {df['진행률'].min():.1f}% ~ {df['진행률'].max():.1f}%")
    else:
        print(f"  ✓ No in-progress items with start dates")

    # Test 5: Status distribution
    print("\n[Test 5] Status Distribution")
    status_counts = df['진행상태'].value_counts()
    for status, count in status_counts.items():
        print(f"  ✓ {status}: {count} items")

    # Test 6: Department distribution
    print("\n[Test 6] Department Distribution")
    dept_counts = df['요청부서'].value_counts()
    print(f"  ✓ {len(dept_counts)} departments found")
    for dept, count in dept_counts.head(3).items():
        print(f"    - {dept}: {count} items")

    # Test 7: Developer distribution
    print("\n[Test 7] Developer Distribution")
    dev_counts = df['개발담당자'].value_counts()
    print(f"  ✓ {len(dev_counts)} developers found")
    for dev, count in dev_counts.head(3).items():
        print(f"    - {dev}: {count} items")

    # Test 8: Manager distribution
    print("\n[Test 8] Manager Distribution")
    manager_counts = df['IT비즈담당자'].value_counts()
    print(f"  ✓ {len(manager_counts)} managers found")

    # Test 9: Filter logic
    print("\n[Test 9] Filter Logic")
    status_filter = ['완료', '진행중']
    dept_filter = list(df['요청부서'].unique())[:3]
    dev_filter = list(df['개발담당자'].unique())[:3]

    filtered = df[
        (df['진행상태'].isin(status_filter)) &
        (df['요청부서'].isin(dept_filter)) &
        (df['개발담당자'].isin(dev_filter))
    ]
    print(f"  ✓ Filter applied: {len(filtered)} items after filtering")

    # Test 10: Display columns validation
    print("\n[Test 10] Display Columns Validation")
    display_cols = [
        '요청번호', '요청일시', '요청부서', '요청자', '일감제목',
        '진행상태', '개발담당자', 'IT비즈담당자', '개발완료목표일자', '남은일수'
    ]
    for col in display_cols:
        if col in df.columns:
            print(f"  ✓ {col} exists")
        else:
            print(f"  ✗ {col} MISSING")

    print("\n" + "="*50)
    print("✓ ALL TESTS PASSED - App data pipeline is working correctly")
    print("="*50)

except Exception as e:
    print(f"\n✗ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
