import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

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
        Fetch available time slots from the MCP API.
        
        Args:
            start_date: Start date for time slots
            end_date: End date for time slots
            location_id: Preferred service location ID
            include_transport: Whether to include slots with transport options
            
        Returns:
            List of available time slots
        """
        # In a real implementation, this would make an API call to the MCP API
        # For demo purposes, we'll return mock data
        
        # Convert to datetime if string
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Make sure we're dealing with datetimes
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            raise ValueError("start_date and end_date must be datetime objects or ISO format strings")
        
        # Mock data for demo purposes - always generate some slots
        mock_slots = []
        current_date = start_date
        
        # Generate slots for the next 7 days (or until end_date)
        while current_date <= end_date and len(mock_slots) < 10:
            # Morning slots (9am-12pm)
            for hour in range(9, 12):
                slot_start = datetime(
                    current_date.year, current_date.month, current_date.day,
                    hour, 0, 0, tzinfo=current_date.tzinfo
                )
                slot_end = datetime(
                    current_date.year, current_date.month, current_date.day,
                    hour + 1, 0, 0, tzinfo=current_date.tzinfo
                )
                
                # Skip slots in the past
                if slot_start < datetime.now(slot_start.tzinfo):
                    continue
                
                mock_slots.append({
                    "slot_id": f"slot-{len(mock_slots) + 1}",
                    "start_time": slot_start.isoformat(),
                    "end_time": slot_end.isoformat(),
                    "available": True,
                    "service_type": "general_service",
                    "location": {
                        "name": "Downtown Service Center",
                        "address": "123 Service St, San Francisco, CA 94105",
                        "coordinates": {
                            "latitude": 37.7749,
                            "longitude": -122.4194
                        }
                    },
                    "transport_included": include_transport
                })
            
            # Afternoon slots (2pm-5pm)
            for hour in range(14, 17):
                slot_start = datetime(
                    current_date.year, current_date.month, current_date.day,
                    hour, 0, 0, tzinfo=current_date.tzinfo
                )
                slot_end = datetime(
                    current_date.year, current_date.month, current_date.day,
                    hour + 1, 0, 0, tzinfo=current_date.tzinfo
                )
                
                # Skip slots in the past
                if slot_start < datetime.now(slot_start.tzinfo):
                    continue
                
                mock_slots.append({
                    "slot_id": f"slot-{len(mock_slots) + 1}",
                    "start_time": slot_start.isoformat(),
                    "end_time": slot_end.isoformat(),
                    "available": True,
                    "service_type": "general_service",
                    "location": {
                        "name": "Sunset Service Center",
                        "address": "456 Auto Ave, San Francisco, CA 94122",
                        "coordinates": {
                            "latitude": 37.7500,
                            "longitude": -122.4800
                        }
                    },
                    "transport_included": include_transport
                })
            
            current_date += timedelta(days=1)
            
        # If location ID is provided, filter by location
        if location_id:
            filtered_slots = [
                slot for slot in mock_slots 
                if slot.get("location", {}).get("id") == location_id
            ]
            return filtered_slots if filtered_slots else mock_slots
            
        return mock_slots
            
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