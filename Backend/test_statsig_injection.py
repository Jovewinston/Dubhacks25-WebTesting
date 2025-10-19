#!/usr/bin/env python3
"""
Test StatSig Injection

This script tests the StatSig injection functionality
by injecting it into a simple website.
"""

import os
import sys
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.statsig_injector import inject_statsig_sdk, log_custom_event, wait_for_statsig_ready, check_statsig_status

# Load environment variables
load_dotenv()


def test_statsig_injection():
    """Test StatSig injection on a simple website."""
    
    print("🧪 Testing StatSig Injection")
    print("=" * 30)
    
    # Check if StatSig client key is configured
    client_key = os.getenv('STATSIG_CLIENT_KEY')
    if not client_key:
        print("❌ STATSIG_CLIENT_KEY not found in environment variables")
        print("   Please add it to your .env file")
        return False
    
    print(f"✅ StatSig Client Key: {client_key[:20]}...{client_key[-10:]}")
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # Navigate to the calculator app
            test_url = "http://localhost:8000"
            print(f"🌐 Navigating to: {test_url}")
            page.goto(test_url)
            
            # Inject StatSig SDK
            print("📊 Injecting StatSig SDK...")
            injection_success = inject_statsig_sdk(
                page=page,
                client_key=client_key,
                user_id="test_injection_user",
                custom_properties={
                    "app": "injection_test",
                    "version": "1.0.0",
                    "test_type": "manual_injection"
                }
            )
            
            if injection_success:
                print("✅ StatSig injection script executed")
                
                # Wait for StatSig to be ready
                if wait_for_statsig_ready(page, timeout=10000):
                    print("✅ StatSig is ready!")
                    
                    # Check StatSig status
                    status = check_statsig_status(page)
                    print(f"📊 StatSig Status: {status}")
                    
                    # Log some test events
                    print("📝 Logging test events...")
                    
                    result1 = log_custom_event(page, "test_event_1", {
                        "message": "First test event",
                        "timestamp": "test_time"
                    })
                    print(f"   Event 1 logged: {result1}")
                    
                    result2 = log_custom_event(page, "test_event_2", {
                        "message": "Second test event",
                        "data": {"key": "value"}
                    })
                    print(f"   Event 2 logged: {result2}")
                    
                    # Simulate calculator interactions
                    print("🧮 Testing Calculator Functionality:")
                    print("-" * 35)
                    
                    # Test 1: Basic addition
                    print("1. Testing addition: 5 + 3 = 8")
                    page.click('button:has-text("5")')
                    page.click('button:has-text("+")')
                    page.click('button:has-text("3")')
                    page.click('button:has-text("=")')
                    page.wait_for_timeout(1000)
                    
                    # Test 2: Multiplication
                    print("2. Testing multiplication: 4 × 7 = 28")
                    page.click('button:has-text("C")')  # Clear
                    page.click('button:has-text("4")')
                    page.click('button:has-text("×")')
                    page.click('button:has-text("7")')
                    page.click('button:has-text("=")')
                    page.wait_for_timeout(1000)
                    
                    # Test 3: Division
                    print("3. Testing division: 15 ÷ 3 = 5")
                    page.click('button:has-text("C")')  # Clear
                    page.click('button:has-text("1")')
                    page.click('button:has-text("5")')
                    page.click('button:has-text("/")')
                    page.click('button:has-text("3")')
                    page.click('button:has-text("=")')
                    page.wait_for_timeout(1000)
                    
                    # Test 4: Decimal operations
                    print("4. Testing decimal: 2.5 + 1.5 = 4")
                    page.click('button:has-text("C")')  # Clear
                    page.click('button:has-text("2")')
                    page.click('button:has-text(".")')
                    page.click('button:has-text("5")')
                    page.click('button:has-text("+")')
                    page.click('button:has-text("1")')
                    page.click('button:has-text(".")')
                    page.click('button:has-text("5")')
                    page.click('button:has-text("=")')
                    page.wait_for_timeout(1000)
                    
                    # Test 5: Clear and delete functions
                    print("5. Testing clear and delete functions")
                    page.click('button:has-text("1")')
                    page.click('button:has-text("2")')
                    page.click('button:has-text("3")')
                    page.click('button:has-text("⌫")')  # Delete last
                    page.click('button:has-text("C")')  # Clear all
                    page.wait_for_timeout(1000)
                    
                    # Scroll to see the calculator
                    print("6. Scrolling to view calculator")
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(1000)
                    
                    # Log calculator test completion
                    result3 = log_custom_event(page, "calculator_test_completed", {
                        "test_type": "injection_test",
                        "operations_tested": ["addition", "multiplication", "division", "decimal", "clear_delete"],
                        "url": page.url
                    })
                    print(f"   Calculator test completion logged: {result3}")
                    print("✅ Calculator test completed")
                    
                    # Wait a bit to capture session data
                    print("⏳ Waiting for session data to be captured...")
                    page.wait_for_timeout(5000)
                    
                    return True
                else:
                    print("❌ StatSig not ready within timeout")
                    return False
            else:
                print("❌ StatSig injection failed")
                return False
                
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            return False
            
        finally:
            print("✅ StatSig injection test completed successfully!")
            print("📊 Check your StatSig dashboard for:")
            print("   - Session replay of calculator interactions")
            print("   - Custom events (test_event_1, test_event_2, calculator_test_completed)")
            print("   - Calculator button clicks and calculations")
            print("   - Auto-captured events from StatSig injection")
            # Wait a bit before closing
            page.wait_for_timeout(2000)
            browser.close()


def main():
    """Main function."""
    
    print("🚀 StatSig Injection Test")
    print("=" * 25)
    
    # Check prerequisites
    print("📋 Prerequisites:")
    print("1. StatSig client key should be configured in .env")
    print("2. Internet connection required for CDN access")
    print("3. Browser will open in headful mode for observation")
    print()
    
    # Run the test
    success = test_statsig_injection()
    
    if success:
        print("\n🎉 StatSig injection test completed!")
        print("📊 Your session replay should be available in StatSig dashboard within ~1 hour")
        print("⚡ Custom events should appear within 2-5 minutes")
        print("\n🔍 How to check results:")
        print("1. Go to https://console.statsig.com/analytics")
        print("2. Look for events: test_event_1, test_event_2, calculator_test_completed")
        print("3. Go to https://console.statsig.com/session-replay")
        print("4. Look for sessions with calculator interactions from injection test")
    else:
        print("\n❌ StatSig injection test failed")
        print("🔍 Check the error messages above for troubleshooting")


if __name__ == "__main__":
    main()
