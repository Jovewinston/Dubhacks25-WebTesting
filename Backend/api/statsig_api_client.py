"""
StatSig Console API client for fetching performance events.
"""
import os
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class StatSigAPIClient:
    """Client for interacting with StatSig Console API."""
    
    def __init__(self):
        self.api_key = os.getenv('STATSIG_API_KEY')
        self.project_id = os.getenv('STATSIG_PROJECT_ID')
        self.base_url = "https://statsigapi.net"
        
        if not self.api_key:
            logger.warning("STATSIG_API_KEY not found in environment variables")
        if not self.project_id:
            logger.warning("STATSIG_PROJECT_ID not found in environment variables")
    
    def is_configured(self) -> bool:
        """Check if the API client is properly configured."""
        return bool(self.api_key and self.project_id)
    
    def get_most_recent_performance_events(self, limit: int = 10) -> List[Dict]:
        """
        Fetch the most recent auto_capture::performance events from StatSig Console API.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of most recent performance events
        """
        if not self.is_configured():
            logger.error("StatSig API client not properly configured")
            return []
        
        try:
            # Use the correct StatSig Console API endpoint
            url = f"{self.base_url}/console/v1/events/auto_capture::performance"
            
            headers = {
                "STATSIG-API-KEY": self.api_key,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            params = {
                "limit": limit,
                "page": 1
            }
            
            logger.info(f"Fetching performance events from StatSig Console API: {url}")
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                events = data.get("data", [])
                logger.info(f"✅ Retrieved {len(events)} performance events from StatSig Console API")
                return events
            else:
                logger.error(f"StatSig Console API request failed: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching StatSig performance events: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching StatSig performance events: {str(e)}")
            return []
    
    def get_most_recent_web_vitals_events(self, limit: int = 10) -> List[Dict]:
        """
        Fetch the most recent auto_capture::web_vitals events from StatSig Console API.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of most recent web vitals events
        """
        if not self.is_configured():
            logger.error("StatSig API client not properly configured")
            return []
        
        try:
            # Use the correct StatSig Console API endpoint
            url = f"{self.base_url}/console/v1/events/auto_capture::web_vitals"
            
            headers = {
                "STATSIG-API-KEY": self.api_key,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            params = {
                "limit": limit,
                "page": 1
            }
            
            logger.info(f"Fetching web vitals events from StatSig Console API: {url}")
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                events = data.get("data", [])
                logger.info(f"✅ Retrieved {len(events)} web vitals events from StatSig Console API")
                return events
            else:
                logger.error(f"StatSig Console API request failed: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching StatSig web vitals events: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching StatSig web vitals events: {str(e)}")
            return []
    
    def get_most_recent_performance_details(self) -> Dict[str, any]:
        """
        Fetch detailed information from the most recent performance and web vitals events.
        
        Returns:
            Dictionary with detailed performance and web vitals data
        """
        if not self.is_configured():
            logger.error("StatSig API client not properly configured")
            return {}
        
        try:
            # Get the most recent performance event
            perf_events = self.get_most_recent_performance_events(limit=1)
            most_recent_perf = perf_events[0] if perf_events else None
            
            # Get the most recent web vitals event
            vitals_events = self.get_most_recent_web_vitals_events(limit=1)
            most_recent_vitals = vitals_events[0] if vitals_events else None
            
            result = {
                "fetch_timestamp": datetime.now().isoformat(),
                "performance_event": None,
                "web_vitals_event": None,
                "summary": {
                    "has_performance_data": most_recent_perf is not None,
                    "has_web_vitals_data": most_recent_vitals is not None,
                    "total_events_found": len(perf_events) + len(vitals_events)
                }
            }
            
            # Process most recent performance event
            if most_recent_perf:
                # Extract detailed performance metrics from the event data
                performance_metrics = self._extract_performance_metrics(most_recent_perf)
                
                result["performance_event"] = {
                    "event_name": most_recent_perf.get("name", "auto_capture::performance"),
                    "user_id": most_recent_perf.get("userID"),
                    "timestamp": most_recent_perf.get("timestamp"),
                    "timestamp_readable": datetime.fromtimestamp(int(most_recent_perf.get("timestamp", 0)) / 1000).isoformat() if most_recent_perf.get("timestamp") else None,
                    "source": most_recent_perf.get("source"),
                    "value": most_recent_perf.get("value"),
                    "metadata": most_recent_perf.get("metadata", {}),
                    "performance_metrics": performance_metrics,
                    "raw_data": most_recent_perf
                }
            
            # Process most recent web vitals event
            if most_recent_vitals:
                # Extract detailed web vitals metrics from the event data
                web_vitals_metrics = self._extract_web_vitals_metrics(most_recent_vitals)
                
                result["web_vitals_event"] = {
                    "event_name": most_recent_vitals.get("name", "auto_capture::web_vitals"),
                    "user_id": most_recent_vitals.get("userID"),
                    "timestamp": most_recent_vitals.get("timestamp"),
                    "timestamp_readable": datetime.fromtimestamp(int(most_recent_vitals.get("timestamp", 0)) / 1000).isoformat() if most_recent_vitals.get("timestamp") else None,
                    "source": most_recent_vitals.get("source"),
                    "value": most_recent_vitals.get("value"),
                    "metadata": most_recent_vitals.get("metadata", {}),
                    "web_vitals_metrics": web_vitals_metrics,
                    "raw_data": most_recent_vitals
                }
            
            logger.info(f"Retrieved detailed performance data: {result['summary']}")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching detailed performance data: {str(e)}")
            return {
                "error": str(e),
                "fetch_timestamp": datetime.now().isoformat(),
                "summary": {
                    "has_performance_data": False,
                    "has_web_vitals_data": False,
                    "total_events_found": 0
                }
            }
    
    def _extract_performance_metrics(self, event_data: Dict) -> Dict[str, str]:
        """
        Extract detailed performance metrics from StatSig event data.
        
        Args:
            event_data: Raw event data from StatSig API
            
        Returns:
            Dictionary with formatted performance metrics
        """
        metrics = {}
        
        try:
            # Extract from metadata
            metadata = event_data.get("metadata", {})
            value = event_data.get("value", {})
            
            # Performance timing metrics
            if isinstance(value, dict):
                # Load time metrics
                if "load_time_ms" in value:
                    metrics["load_time_ms"] = str(value["load_time_ms"])
                if "dom_interactive_time_ms" in value:
                    metrics["dom_interactive_time_ms"] = str(value["dom_interactive_time_ms"])
                if "first_contentful_paint_time_ms" in value:
                    metrics["first_contentful_paint_time_ms"] = str(value["first_contentful_paint_time_ms"])
                
                # Network metrics
                if "redirect_count" in value:
                    metrics["redirect_count"] = str(value["redirect_count"])
                if "transfer_bytes" in value:
                    metrics["transfer_bytes"] = str(value["transfer_bytes"])
                
                # Connection metrics
                if "effective_connection_type" in value:
                    metrics["effective_connection_type"] = str(value["effective_connection_type"])
                if "downlink_mbps" in value:
                    metrics["downlink_mbps"] = str(value["downlink_mbps"])
                if "downlink_kbps" in value:
                    metrics["downlink_kbps"] = str(value["downlink_kbps"])
                
                # Location metrics
                if "city" in value:
                    metrics["city"] = str(value["city"])
                if "state" in value:
                    metrics["state"] = str(value["state"])
                if "country" in value:
                    metrics["country"] = str(value["country"])
                
                # Additional performance metrics
                if "largest_contentful_paint_ms" in value:
                    metrics["largest_contentful_paint_ms"] = str(value["largest_contentful_paint_ms"])
                if "cumulative_layout_shift" in value:
                    metrics["cumulative_layout_shift"] = str(value["cumulative_layout_shift"])
                if "first_input_delay_ms" in value:
                    metrics["first_input_delay_ms"] = str(value["first_input_delay_ms"])
                if "time_to_first_byte_ms" in value:
                    metrics["time_to_first_byte_ms"] = str(value["time_to_first_byte_ms"])
            
            # Also check metadata for additional metrics
            if isinstance(metadata, dict):
                for key, val in metadata.items():
                    if key not in metrics and any(keyword in key.lower() for keyword in 
                        ['time', 'ms', 'bytes', 'count', 'type', 'mbps', 'kbps', 'city', 'state', 'country']):
                        metrics[key] = str(val)
            
            logger.info(f"Extracted {len(metrics)} performance metrics from event data")
            
        except Exception as e:
            logger.warning(f"Error extracting performance metrics: {e}")
        
        return metrics
    
    def _extract_web_vitals_metrics(self, event_data: Dict) -> Dict[str, str]:
        """
        Extract detailed web vitals metrics from StatSig event data.
        
        Args:
            event_data: Raw event data from StatSig API
            
        Returns:
            Dictionary with formatted web vitals metrics
        """
        metrics = {}
        
        try:
            # Extract from metadata and value
            metadata = event_data.get("metadata", {})
            value = event_data.get("value", {})
            
            # Core Web Vitals
            if isinstance(value, dict):
                # Largest Contentful Paint (LCP)
                if "lcp" in value:
                    metrics["lcp_ms"] = str(value["lcp"])
                elif "largest_contentful_paint" in value:
                    metrics["lcp_ms"] = str(value["largest_contentful_paint"])
                
                # First Input Delay (FID)
                if "fid" in value:
                    metrics["fid_ms"] = str(value["fid"])
                elif "first_input_delay" in value:
                    metrics["fid_ms"] = str(value["first_input_delay"])
                
                # Cumulative Layout Shift (CLS)
                if "cls" in value:
                    metrics["cls_score"] = str(value["cls"])
                elif "cumulative_layout_shift" in value:
                    metrics["cls_score"] = str(value["cumulative_layout_shift"])
                
                # First Contentful Paint (FCP)
                if "fcp" in value:
                    metrics["fcp_ms"] = str(value["fcp"])
                elif "first_contentful_paint" in value:
                    metrics["fcp_ms"] = str(value["first_contentful_paint"])
                
                # Time to First Byte (TTFB)
                if "ttfb" in value:
                    metrics["ttfb_ms"] = str(value["ttfb"])
                elif "time_to_first_byte" in value:
                    metrics["ttfb_ms"] = str(value["time_to_first_byte"])
            
            # Also check metadata for web vitals
            if isinstance(metadata, dict):
                for key, val in metadata.items():
                    if key not in metrics and any(keyword in key.lower() for keyword in 
                        ['lcp', 'fid', 'cls', 'fcp', 'ttfb', 'paint', 'delay', 'shift']):
                        metrics[key] = str(val)
            
            logger.info(f"Extracted {len(metrics)} web vitals metrics from event data")
            
        except Exception as e:
            logger.warning(f"Error extracting web vitals metrics: {e}")
        
        return metrics

# Global instance
statsig_api_client = StatSigAPIClient()
