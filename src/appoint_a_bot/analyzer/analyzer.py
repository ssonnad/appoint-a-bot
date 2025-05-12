from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import pytz

class Analyzer:
    """
    Analyzer that processes time slots to find the most suitable options for the customer.
    """
    
    def __init__(self, default_timezone: str = "UTC"):
        """
        Initialize the Analyzer.
        
        Args:
            default_timezone: The default timezone to use for comparisons
        """
        self.default_timezone = default_timezone
        
    def find_closest_time_slot(self, time_slots: List[Dict[str, Any]], 
                               preferred_time: Optional[datetime] = None,
                               max_results: int = 1) -> List[Dict[str, Any]]:
        """
        Find the closest time slot to the preferred time.
        
        Args:
            time_slots: List of available time slots
            preferred_time: The customer's preferred time (defaults to now)
            max_results: Maximum number of results to return
            
        Returns:
            List of closest time slots, sorted by proximity
        """
        if not time_slots:
            return []
            
        if preferred_time is None:
            preferred_time = datetime.now(pytz.timezone(self.default_timezone))
            
        # Parse the time slot dates and calculate the time difference
        def get_time_difference(slot):
            slot_time_str = slot.get("start_time")
            slot_time = datetime.fromisoformat(slot_time_str)
            
            # Make timezone-aware if it isn't already
            if slot_time.tzinfo is None:
                slot_time = pytz.timezone(self.default_timezone).localize(slot_time)
                
            # Return absolute time difference in seconds
            return abs((slot_time - preferred_time).total_seconds())
        
        # Sort slots by time difference
        sorted_slots = sorted(time_slots, key=get_time_difference)
        
        # Return the specified number of closest slots
        return sorted_slots[:max_results]
        
    def filter_slots_by_criteria(self, time_slots: List[Dict[str, Any]], 
                                criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter time slots based on specific criteria.
        
        Args:
            time_slots: List of available time slots
            criteria: Dictionary of filtering criteria
            
        Returns:
            Filtered list of time slots
        """
        filtered_slots = time_slots
        
        # Filter by date range if provided
        if "start_date" in criteria and "end_date" in criteria:
            start_date = criteria["start_date"]
            end_date = criteria["end_date"]
            
            # Convert datetime objects to date objects for proper comparison
            if isinstance(start_date, datetime):
                start_date = start_date.date()
            if isinstance(end_date, datetime):
                end_date = end_date.date()
            
            filtered_slots = [
                slot for slot in filtered_slots
                if start_date <= datetime.fromisoformat(slot.get("start_time")).date() <= end_date
            ]
            
        # Filter by has_transport if needed
        if "transport_required" in criteria and criteria["transport_required"]:
            filtered_slots = [
                slot for slot in filtered_slots
                if slot.get("has_transport", False)
            ]
            
        # Filter by location if provided
        if "location_id" in criteria:
            filtered_slots = [
                slot for slot in filtered_slots
                if slot.get("location_id") == criteria["location_id"]
            ]
            
        return filtered_slots
        
    def analyze_availability_patterns(self, time_slots: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze patterns in available time slots.
        
        Args:
            time_slots: List of available time slots
            
        Returns:
            Analysis results with patterns and insights
        """
        if not time_slots:
            return {"status": "no_data", "patterns": {}}
            
        # Count slots by day of week
        days_count = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}  # Mon=0, Sun=6
        hours_count = {}  # Hours distribution
        
        for slot in time_slots:
            slot_time = datetime.fromisoformat(slot.get("start_time"))
            day = slot_time.weekday()
            hour = slot_time.hour
            
            days_count[day] += 1
            hours_count[hour] = hours_count.get(hour, 0) + 1
            
        # Find the most available day
        most_available_day = max(days_count.items(), key=lambda x: x[1])[0]
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # Find the most available hour
        most_available_hour = max(hours_count.items(), key=lambda x: x[1])[0] if hours_count else None
        
        return {
            "status": "success",
            "patterns": {
                "most_available_day": day_names[most_available_day],
                "most_available_hour": most_available_hour,
                "day_distribution": days_count,
                "hour_distribution": hours_count
            }
        }

# Example usage
if __name__ == "__main__":
    # Sample data for demonstration
    sample_slots = [
        {"id": "1", "start_time": "2023-06-01T09:00:00", "location_id": "loc1", "has_transport": True},
        {"id": "2", "start_time": "2023-06-01T14:00:00", "location_id": "loc1", "has_transport": False},
        {"id": "3", "start_time": "2023-06-02T10:00:00", "location_id": "loc2", "has_transport": True},
    ]
    
    analyzer = Analyzer()
    
    # Find closest time slot to now
    closest = analyzer.find_closest_time_slot(sample_slots)
    print(f"Closest time slot: {closest}")
    
    # Filter by criteria
    criteria = {
        "start_date": datetime(2023, 6, 1).date(),
        "end_date": datetime(2023, 6, 1).date(),
        "transport_required": True
    }
    
    filtered = analyzer.filter_slots_by_criteria(sample_slots, criteria)
    print(f"Filtered slots: {filtered}") 