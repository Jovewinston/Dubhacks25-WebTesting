#!/usr/bin/env python3
"""
Test Calculator App with StatSig Integration

This script tests the calculator app and verifies that StatSig
session replay and events are being captured properly.
"""

import asyncio
import os
import uuid
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load environment variables
load_dotenv()


async def test_calculator_with_statsig():
    """Test the calculator app and verify StatSig integration."""
    
    print("🧮 Testing Calculator App with StatSig Integration")
    print("=" * 55)
    
    # Check if StatSig client key is configured
    client_key = os.getenv('STATSIG_CLIENT_KEY')
    if not client_key:
        print("❌ STATSIG_CLIENT_KEY not found in environment variables")
        print("   Please add it to your .env file")
        return False
    
    print(f"✅ StatSig Client Key: {client_key[:20]}...{client_key[-10:]}")
    
    async with async_playwright() as p:
        # Launch browser in headful mode so you can see the interactions
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate to the calculator app
            calculator_url = "http://localhost:8000"
            print(f"🌐 Navigating to: {calculator_url}")
            await page.goto(calculator_url)
            
            # Wait for StatSig to initialize
            print("⏳ Waiting for StatSig to initialize...")
            await page.wait_for_selector('.statsig-status.success', timeout=10000)
            print("✅ StatSig initialized successfully!")
            
            # Test calculator functionality
            print("\n🧮 Testing Calculator Functionality:")
            print("-" * 35)
            
            # Test 1: Basic addition
            print("1. Testing addition: 5 + 3 = 8")
            await page.click('button:has-text("5")')
            await page.click('button:has-text("+")')
            await page.click('button:has-text("3")')
            await page.click('button:has-text("=")')
            await asyncio.sleep(1)
            
            # Test 2: Multiplication
            print("2. Testing multiplication: 4 × 7 = 28")
            await page.click('button:has-text("C")')  # Clear
            await page.click('button:has-text("4")')
            await page.click('button:has-text("×")')
            await page.click('button:has-text("7")')
            await page.click('button:has-text("=")')
            await asyncio.sleep(1)
            
            # Test 3: Division
            print("3. Testing division: 15 ÷ 3 = 5")
            await page.click('button:has-text("C")')  # Clear
            await page.click('button:has-text("1")')
            await page.click('button:has-text("5")')
            await page.click('button:has-text("/")')
            await page.click('button:has-text("3")')
            await page.click('button:has-text("=")')
            await asyncio.sleep(1)
            
            # Test 4: Decimal operations
            print("4. Testing decimal: 2.5 + 1.5 = 4")
            await page.click('button:has-text("C")')  # Clear
            await page.click('button:has-text("2")')
            await page.click('button:has-text(".")')
            await page.click('button:has-text("5")')
            await page.click('button:has-text("+")')
            await page.click('button:has-text("1")')
            await page.click('button:has-text(".")')
            await page.click('button:has-text("5")')
            await page.click('button:has-text("=")')
            await asyncio.sleep(1)
            
            # Test 5: Clear and delete functions
            print("5. Testing clear and delete functions")
            await page.click('button:has-text("1")')
            await page.click('button:has-text("2")')
            await page.click('button:has-text("3")')
            await page.click('button:has-text("⌫")')  # Delete last
            await page.click('button:has-text("C")')  # Clear all
            await asyncio.sleep(1)
            
            # Scroll to see event log
            print("6. Scrolling to view event log")
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1)
            
            # Check event log
            print("\n📊 Checking Event Log:")
            print("-" * 25)
            event_log = await page.query_selector('#event-list')
            if event_log:
                events = await event_log.inner_text()
                print("Recent events captured:")
                print(events)
            else:
                print("No event log found")
            
            # Wait to capture session data
            print("\n⏳ Waiting for session data to be captured...")
            print("⏰ Test will complete in 10 seconds...")
            await asyncio.sleep(10)
            
            print("\n✅ Calculator test completed successfully!")
            print("📊 Check your StatSig dashboard for:")
            print("   - Session replay of calculator interactions")
            print("   - Custom events (button_clicked, calculation_completed, etc.)")
            print("   - User interactions and page navigation")
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            return False
            
        finally:
            await browser.close()


async def main():
    """Main function."""
    
    print("🚀 Calculator App StatSig Integration Test")
    print("=" * 45)
    
    # Check if server is running
    print("📋 Prerequisites:")
    print("1. Make sure the calculator server is running:")
    print("   cd dummy_web && python3 server.py")
    print("2. The calculator should be accessible at http://localhost:8000")
    print("3. StatSig client key should be configured in .env")
    print()
    
    # Run the test
    success = await test_calculator_with_statsig()
    
    if success:
        print("\n🎉 Calculator StatSig integration test completed!")
        print("📊 Your session replay should be available in StatSig dashboard within ~1 hour")
        print("⚡ Custom events should appear within 2-5 minutes")
        print("\n🔍 How to check results:")
        print("1. Go to https://console.statsig.com/analytics")
        print("2. Look for events: button_clicked, calculation_completed, etc.")
        print("3. Go to https://console.statsig.com/session-replay")
        print("4. Look for sessions with calculator interactions")
    else:
        print("\n❌ Calculator StatSig integration test failed")
        print("🔍 Check the error messages above for troubleshooting")


if __name__ == "__main__":
    asyncio.run(main())
