"""
StatSig Injector for Web Testing

This module provides functionality to inject StatSig JavaScript SDK
into any website through Playwright browser automation.
"""

import os
import json
import uuid
from typing import Optional, Dict, Any
from playwright.sync_api import Page


def inject_statsig_sdk(
    page: Page,
    client_key: str,
    user_id: Optional[str] = None,
    custom_properties: Optional[Dict[str, Any]] = None,
    enable_session_replay: bool = True,
    enable_auto_capture: bool = True,
    session_replay_sampling_rate: float = 1.0
) -> bool:
    """
    Inject StatSig SDK into a Playwright page.
    
    Args:
        page: Playwright page object
        client_key: StatSig client key
        user_id: Unique user ID (generated if not provided)
        custom_properties: Custom properties to attach to user
        enable_session_replay: Whether to enable session replay
        enable_auto_capture: Whether to enable auto-capture
        session_replay_sampling_rate: Sampling rate for session replay (0.0 to 1.0, default 1.0 = 100%)
        
    Returns:
        bool: True if injection was successful, False otherwise
    """
    try:
        # Generate user ID if not provided
        if not user_id:
            user_id = f"test_user_{uuid.uuid4().hex[:8]}"
        
        # Default custom properties
        if custom_properties is None:
            custom_properties = {
                "app": "web_testing",
                "version": "1.0.0",
                "device": "desktop",
                "browser": "playwright"
            }
        
        # Convert custom properties to JSON string for injection
        custom_props_str = json.dumps(custom_properties)
        
        # StatSig injection script - exact same as working calculator
        injection_script = f"""
        (function() {{
            // Check if StatSig is already loaded
            if (window.statsigClient) {{
                console.log('StatSig already initialized');
                return;
            }}
            
            // Create unique user ID for this session
            const userId = '{user_id}';
            
            // StatSig injection script
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/@statsig/js-client@3/build/statsig-js-client+session-replay+web-analytics.min.js';
            script.onload = function() {{
                console.log('StatSig SDK loaded, initializing...');
                
                // Wait a bit for the SDK to load
                setTimeout(async function() {{
                    try {{
                        // Check what's available in the global scope
                        console.log('Available globals:', Object.keys(window).filter(key => key.toLowerCase().includes('statsig')));
                        
                        // Try different approaches to access StatSig
                        let StatsigClientClass = null;
                        let StatsigSessionReplayPlugin = null;
                        let StatsigAutoCapturePlugin = null;

                        // Check for different possible global names
                        if (typeof window.StatsigClient !== 'undefined') {{
                            StatsigClientClass = window.StatsigClient;
                        }} else if (typeof window.Statsig !== 'undefined' && window.Statsig.StatsigClient) {{
                            StatsigClientClass = window.Statsig.StatsigClient;
                        }} else if (typeof window.__STATSIG__ !== 'undefined' && window.__STATSIG__.StatsigClient) {{
                            StatsigClientClass = window.__STATSIG__.StatsigClient;
                        }}

                        // Check for plugin classes
                        if (typeof window.StatsigSessionReplayPlugin !== 'undefined') {{
                            StatsigSessionReplayPlugin = window.StatsigSessionReplayPlugin;
                        }} else if (typeof window.Statsig !== 'undefined' && window.Statsig.StatsigSessionReplayPlugin) {{
                            StatsigSessionReplayPlugin = window.Statsig.StatsigSessionReplayPlugin;
                        }} else if (typeof window.__STATSIG__ !== 'undefined' && window.__STATSIG__.StatsigSessionReplayPlugin) {{
                            StatsigSessionReplayPlugin = window.__STATSIG__.StatsigSessionReplayPlugin;
                        }}

                        if (typeof window.StatsigAutoCapturePlugin !== 'undefined') {{
                            StatsigAutoCapturePlugin = window.StatsigAutoCapturePlugin;
                        }} else if (typeof window.Statsig !== 'undefined' && window.Statsig.StatsigAutoCapturePlugin) {{
                            StatsigAutoCapturePlugin = window.Statsig.StatsigAutoCapturePlugin;
                        }} else if (typeof window.__STATSIG__ !== 'undefined' && window.__STATSIG__.StatsigAutoCapturePlugin) {{
                            StatsigAutoCapturePlugin = window.__STATSIG__.StatsigAutoCapturePlugin;
                        }}

                        if (!StatsigClientClass) {{
                            throw new Error('StatSig SDK not loaded - StatsigClient not found');
                        }}

                        // Initialize StatSig with plugins exactly as per documentation
                        const plugins = [];
                        
                        if (StatsigSessionReplayPlugin && {str(enable_session_replay).lower()}) {{
                            // Set configurable sampling rate (default 100%)
                            plugins.push(new StatsigSessionReplayPlugin({{ sampleRate: {session_replay_sampling_rate} }}));
                            console.log('Session replay plugin added with sampling rate: {session_replay_sampling_rate}');
                        }} else {{
                            console.log('Session replay plugin not found or disabled');
                        }}
                        
                        if (StatsigAutoCapturePlugin && {str(enable_auto_capture).lower()}) {{
                            plugins.push(new StatsigAutoCapturePlugin());
                            console.log('Auto-capture plugin added');
                        }} else {{
                            console.log('Auto-capture plugin not found or disabled');
                        }}

                        window.statsigClient = new StatsigClientClass(
                            '{client_key}',
                            {{ 
                                userID: userId,
                                custom: {custom_props_str}
                            }},
                            {{
                                plugins: plugins,
                            }}
                        );

                        // Initialize the client
                        await window.statsigClient.initializeAsync();

                        console.log('✅ StatSig Connected!');
                        
                        // Log initial event
                        window.statsigClient.logEvent('statsig_injected', {{
                            user_id: userId,
                            timestamp: new Date().toISOString(),
                            url: window.location.href
                        }});
                        
                        // Dispatch custom event to notify injection is complete
                        window.dispatchEvent(new CustomEvent('statsigReady', {{
                            detail: {{ 
                                userId: userId,
                                client: window.statsigClient 
                            }}
                        }}));
                        
                    }} catch (error) {{
                        console.error('StatSig initialization failed:', error);
                        window.dispatchEvent(new CustomEvent('statsigError', {{
                            detail: {{ error: error.message }}
                        }}));
                    }}
                }}, 1000);
            }};
            script.onerror = function() {{
                console.error('Failed to load StatSig SDK');
                window.dispatchEvent(new CustomEvent('statsigError', {{
                    detail: {{ error: 'Failed to load StatSig SDK' }}
                }}));
            }};
            document.head.appendChild(script);
        }})();
        """
        
        # Inject the script into the page
        page.evaluate(injection_script)
        
        print(f"📊 StatSig injection script executed for user: {user_id}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to inject StatSig: {e}")
        return False


def log_custom_event(
    page: Page,
    event_name: str,
    event_data: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Log a custom event to StatSig.
    
    Args:
        page: Playwright page object
        event_name: Name of the event
        event_data: Event data dictionary
        
    Returns:
        bool: True if event was logged successfully, False otherwise
    """
    try:
        if event_data is None:
            event_data = {}
        
        # Add timestamp to event data
        event_data["timestamp"] = "new Date().toISOString()"
        
        # Script to log event
        log_script = f"""
        (() => {{
            if (window.statsigClient) {{
                window.statsigClient.logEvent('{event_name}', {json.dumps(event_data)});
                console.log('Logged StatSig event: {event_name}', {json.dumps(event_data)});
                return true;
            }} else {{
                console.warn('StatSig client not available for event logging');
                return false;
            }}
        }})()
        """
        
        result = page.evaluate(log_script)
        return result
        
    except Exception as e:
        print(f"❌ Failed to log StatSig event '{event_name}': {e}")
        return False


def wait_for_statsig_ready(page: Page, timeout: int = 10000) -> bool:
    """
    Wait for StatSig to be ready.
    
    Args:
        page: Playwright page object
        timeout: Timeout in milliseconds
        
    Returns:
        bool: True if StatSig is ready, False if timeout
    """
    try:
        # Wait for the statsigReady event
        page.wait_for_function(
            "window.statsigClient !== undefined",
            timeout=timeout
        )
        print("✅ StatSig is ready")
        return True
        
    except Exception as e:
        print(f"⚠️ StatSig not ready within {timeout}ms: {e}")
        return False


def check_statsig_status(page: Page) -> Dict[str, Any]:
    """
    Check the current status of StatSig on the page.
    
    Args:
        page: Playwright page object
        
    Returns:
        dict: Status information
    """
    try:
        status_script = """
        ({
            isLoaded: typeof window.StatsigClient !== 'undefined',
            isInitialized: window.statsigClient !== undefined,
            hasSessionReplay: typeof window.StatsigSessionReplayPlugin !== 'undefined',
            hasAutoCapture: typeof window.StatsigAutoCapturePlugin !== 'undefined',
            userId: window.statsigClient ? window.statsigClient._user?.userID : null
        })
        """
        
        status = page.evaluate(status_script)
        return status
        
    except Exception as e:
        print(f"❌ Failed to check StatSig status: {e}")
        return {"error": str(e)}
