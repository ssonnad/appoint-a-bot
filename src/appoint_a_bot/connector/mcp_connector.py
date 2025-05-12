import requests
from datetime import datetime, timedelta
import json
from typing import List, Dict, Any, Optional

class MCPConnector:
    """
    MCP Connector responsible for retrieving available time slots from an external service.
    """
    
    def __init__(self, api_url: str, api_key: Optional[str] = None):
        """
        Initialize the MCP Connector.
        
        Args:
            api_url: The URL of the external service API
            api_key: Optional API key for authentication
        """
        self.api_url = api_url
        self.api_key = api_key
        self.headers = {}
        
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        
    def fetch_time_slots(self, start_date: datetime, end_date: datetime, 
                        location_id: Optional[str] = None,
                        include_transport: bool = False) -> List[Dict[str, Any]]:
        """
        Fetch available time slots from the external API.
        
        Args:
            start_date: Start date for the time slot search
            end_date: End date for the time slot search
            location_id: Optional location identifier
            include_transport: Whether to include transport options
            
        Returns:
            A list of available time slots with their details
        """
        params = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "include_transport": include_transport
        }
        
        if location_id:
            params["location_id"] = location_id
            
        try:
            response = requests.get(
                self.api_url, 
                params=params,
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json().get("time_slots", [])
            
        except requests.RequestException as e:
            print(f"Error fetching time slots: {e}")
            return []
            
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """
        Handle errors that occur during API communication.
        
        Args:
            error: The exception that was raised
            
        Returns:
            A dictionary with error details
        """
        return {
            "error": str(error),
            "timestamp": datetime.now().isoformat(),
            "status": "error"
        }
        
# Example usage
if __name__ == "__main__":
    # This is just for demonstration
    connector = MCPConnector(api_url="https://example-mcp-api.com/slots", api_key="your_api_key")
    
    start = datetime.now()
    end = start + timedelta(days=7)
    
    slots = connector.fetch_time_slots(start, end, include_transport=True)
    print(f"Found {len(slots)} available time slots") 