#!/usr/bin/env python3
"""
Debug script to test StatSig API and see what events are available.
"""
import os
import sys
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def debug_statsig_api():
    """Debug StatSig API to see what's available."""
    print("🔍 StatSig API Debug Test")
    print("=" * 50)
    
    api_key = os.getenv('STATSIG_API_KEY')
    project_id = os.getenv('STATSIG_PROJECT_ID')
    
    if not api_key or not project_id:
        print("❌ Missing API credentials")
        return
    
    print(f"✅ API Key: {api_key[:10]}...{api_key[-5:]}")
    print(f"✅ Project ID: {project_id}")
    
    base_url = "https://console.statsig.com/api/v1"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test different API endpoints
    endpoints_to_test = [
        f"/projects/{project_id}/events",
        f"/projects/{project_id}/metrics/events",
        f"/projects/{project_id}/analytics/events",
        f"/events",
        f"/metrics/events",
        f"/analytics/events"
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\n🌐 Testing endpoint: {endpoint}")
        try:
            url = f"{base_url}{endpoint}"
            
            # Try with different parameters
            params_list = [
                {},  # No params
                {"limit": 10},  # Basic limit
                {"event_name": "auto_capture::performance"},  # Specific event
                {"event_name": "auto_capture::web_vitals"},  # Web vitals
                {"start_time": (datetime.now() - timedelta(hours=1)).isoformat()},  # Time range
            ]
            
            for i, params in enumerate(params_list):
                print(f"   Attempt {i+1}: {params}")
                response = requests.get(url, headers=headers, params=params, timeout=10)
                
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"   ✅ Success! Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                        
                        # Look for events
                        if isinstance(data, dict):
                            if 'events' in data:
                                events = data['events']
                                print(f"   📊 Found {len(events)} events")
                                if events:
                                    print(f"   📋 Event names: {list(set([e.get('event_name', 'unknown') for e in events[:5]]))}")
                            elif 'data' in data:
                                print(f"   📊 Data keys: {list(data['data'].keys()) if isinstance(data['data'], dict) else 'Not a dict'}")
                        break  # Success, no need to try other params
                    except json.JSONDecodeError:
                        print(f"   ❌ Invalid JSON response")
                        print(f"   Response: {response.text[:200]}...")
                else:
                    print(f"   ❌ Error: {response.text[:100]}...")
                    
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {str(e)}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {str(e)}")
    
    # Try to get project info
    print(f"\n🏢 Testing project info endpoint...")
    try:
        url = f"{base_url}/projects/{project_id}"
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Project info: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        else:
            print(f"   ❌ Error: {response.text[:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    debug_statsig_api()
