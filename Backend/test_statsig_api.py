#!/usr/bin/env python3
"""
Test script to verify StatSig API configuration and connectivity.
"""
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.statsig_api_client import statsig_api_client

def test_statsig_api():
    """Test StatSig API configuration and connectivity."""
    print("🔍 StatSig API Configuration Test")
    print("=" * 50)
    
    # Check environment variables
    api_key = os.getenv('STATSIG_API_KEY')
    project_id = os.getenv('STATSIG_PROJECT_ID')
    
    print(f"✅ STATSIG_API_KEY: {'Set' if api_key else '❌ Not Set'}")
    if api_key:
        print(f"   Key: {api_key[:10]}...{api_key[-5:]}")
    
    print(f"✅ STATSIG_PROJECT_ID: {'Set' if project_id else '❌ Not Set'}")
    if project_id:
        print(f"   Project ID: {project_id}")
    
    # Test API client configuration
    print(f"\n🔧 API Client Configuration:")
    print(f"   Configured: {statsig_api_client.is_configured()}")
    print(f"   Base URL: {statsig_api_client.base_url}")
    
    if not statsig_api_client.is_configured():
        print("\n❌ StatSig API client is not properly configured!")
        print("   Please set both STATSIG_API_KEY and STATSIG_PROJECT_ID environment variables.")
        return False
    
    # Test API connectivity
    print(f"\n🌐 Testing API Connectivity...")
    try:
        # Try to fetch recent performance events
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=1)
        
        print(f"   Fetching events from {start_time} to {end_time}")
        events = statsig_api_client.get_all_performance_events(
            start_time=start_time,
            end_time=end_time,
            limit=10
        )
        
        performance_count = len(events.get("performance", []))
        web_vitals_count = len(events.get("web_vitals", []))
        
        print(f"   ✅ API Connection Successful!")
        print(f"   📊 Performance Events: {performance_count}")
        print(f"   📊 Web Vitals Events: {web_vitals_count}")
        
        if performance_count > 0 or web_vitals_count > 0:
            print(f"   🎉 Found performance data!")
        else:
            print(f"   ⚠️  No performance events found in the last hour")
            print(f"      This might be normal if no tests have run recently")
        
        return True
        
    except Exception as e:
        print(f"   ❌ API Connection Failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_statsig_api()
    
    if success:
        print(f"\n🎉 StatSig API integration is working correctly!")
    else:
        print(f"\n❌ StatSig API integration needs configuration.")
        print(f"\n📋 Next Steps:")
        print(f"   1. Find your Project ID in StatSig Console")
        print(f"   2. Add STATSIG_PROJECT_ID to your .env file")
        print(f"   3. Run this test again")
