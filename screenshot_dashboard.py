#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
from playwright.async_api import async_playwright
import time

async def capture_dashboard():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print("Navigating to dashboard...")
        await page.goto('http://localhost:8501', wait_until='networkidle')

        # Wait for Streamlit to fully load
        await page.wait_for_timeout(3000)

        # Scroll to see all content
        print("Capturing full page screenshot...")
        await page.screenshot(path='C:\\jiyong\\dashboard_full.png', full_page=True)
        print("[OK] Full page: dashboard_full.png")

        # Capture individual tabs
        print("\nCapturing Tab 1: Analysis...")
        await page.screenshot(path='C:\\jiyong\\dashboard_tab1_analysis.png')
        print("[OK] Tab 1: dashboard_tab1_analysis.png")

        # Click on Tab 2
        print("\nCapturing Tab 2: Detailed Data...")
        tab_buttons = await page.query_selector_all('button')
        for btn in tab_buttons:
            text = await btn.text_content()
            if text and "상세 데이터" in text:
                await btn.click()
                break
        await page.wait_for_timeout(2000)
        await page.screenshot(path='C:\\jiyong\\dashboard_tab2_data.png', full_page=True)
        print("[OK] Tab 2: dashboard_tab2_data.png")

        # Click on Tab 3
        print("\nCapturing Tab 3: Manager View...")
        tab_buttons = await page.query_selector_all('button')
        for btn in tab_buttons:
            text = await btn.text_content()
            if text and "담당자별" in text:
                await btn.click()
                break
        await page.wait_for_timeout(2000)
        await page.screenshot(path='C:\\jiyong\\dashboard_tab3_manager.png', full_page=True)
        print("[OK] Tab 3: dashboard_tab3_manager.png")

        # Click on Tab 4
        print("\nCapturing Tab 4: Timeline...")
        tab_buttons = await page.query_selector_all('button')
        for btn in tab_buttons:
            text = await btn.text_content()
            if text and "타임라인" in text:
                await btn.click()
                break
        await page.wait_for_timeout(3000)
        await page.screenshot(path='C:\\jiyong\\dashboard_tab4_timeline.png', full_page=True)
        print("[OK] Tab 4: dashboard_tab4_timeline.png")

        await browser.close()
        print("\n[SUCCESS] All screenshots captured!")

if __name__ == '__main__':
    asyncio.run(capture_dashboard())
