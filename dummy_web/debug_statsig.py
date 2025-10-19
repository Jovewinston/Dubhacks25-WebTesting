#!/usr/bin/env python3
"""
Debug StatSig Integration

This script helps debug what's happening with StatSig initialization
in the calculator app.
"""

import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load environment variables
load_dotenv()


async def debug_statsig():
    """Debug StatSig integration issues."""
    
    print("🔍 Debugging StatSig Integration")
    print("=" * 35)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate to calculator
            print("🌐 Navigating to calculator...")
            await page.goto("http://localhost:8000")
            
            # Wait a bit for page to load
            await asyncio.sleep(3)
            
            # Check if StatSig SDK loaded
            print("🔍 Checking StatSig SDK status...")
            
            # Check for StatSig global objects
            statsig_available = await page.evaluate("""
                () => {
                    return {
                        StatsigClient: typeof StatsigClient !== 'undefined',
                        runStatsigSessionReplay: typeof runStatsigSessionReplay !== 'undefined',
                        runStatsigAutoCapture: typeof runStatsigAutoCapture !== 'undefined',
                        statsigClient: typeof window.statsigClient !== 'undefined'
                    };
                }
            """)
            
            print("📊 StatSig SDK Status:")
            for key, value in statsig_available.items():
                status = "✅" if value else "❌"
                print(f"   {status} {key}: {value}")
            
            # Check console logs
            print("\n📝 Console Logs:")
            console_logs = await page.evaluate("""
                () => {
                    return window.consoleLogs || [];
                }
            """)
            
            if console_logs:
                for log in console_logs[-10:]:  # Last 10 logs
                    print(f"   {log}")
            else:
                print("   No console logs captured")
            
            # Check for errors
            print("\n🚨 Console Errors:")
            console_errors = await page.evaluate("""
                () => {
                    return window.consoleErrors || [];
                }
            """)
            
            if console_errors:
                for error in console_errors:
                    print(f"   ❌ {error}")
            else:
                print("   ✅ No console errors")
            
            # Check the status element
            print("\n📊 Status Element:")
            status_element = await page.query_selector('#statsig-status')
            if status_element:
                status_text = await status_element.inner_text()
                status_class = await status_element.get_attribute('class')
                print(f"   Text: {status_text}")
                print(f"   Class: {status_class}")
            else:
                print("   ❌ Status element not found")
            
            # Wait for user to see the page
            print("\n⏰ Waiting 10 seconds for you to see the page...")
            await asyncio.sleep(10)
            
        except Exception as e:
            print(f"❌ Debug failed: {e}")
        
        finally:
            await browser.close()


async def main():
    """Main function."""
    print("🚀 StatSig Integration Debugger")
    print("=" * 30)
    
    await debug_statsig()


if __name__ == "__main__":
    asyncio.run(main())
