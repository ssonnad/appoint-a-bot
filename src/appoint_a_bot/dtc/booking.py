"""
Booking API for handling appointment bookings based on DTC codes.
This module provides booking functionality with mock data for demonstration.
"""
from datetime import datetime, timedelta
import random
import logging
import uuid
from typing import List, Dict, Any, Optional, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BookingService:
    """
    Service for handling appointment bookings with mock data.
    Provides functionality to find available slots and create bookings.
    """
    
    def __init__(self):
        """Initialize the Booking Service."""
        self.bookings = []  # Store created bookings
        logger.info("Booking Service initialized")
    
    def find_available_slots(self, start_date: datetime, end_date: datetime, 
                            location_id: Optional[str] = None,
                            include_transport: bool = False) -> List[Dict[str, Any]]:
        """
        Find available appointment slots within the given date range.
        
        Args:
            start_date: Start date for the search
            end_date: End date for the search
            location_id: Optional location identifier
            include_transport: Whether to include transport options
            
        Returns:
            A list of available time slots with their details
        """
        mock_slots = []
        current_date = start_date.replace(hour=8, minute=0, second=0, microsecond=0)
        
        # Define service durations (in minutes)
        service_durations = [30, 45, 60, 90, 120]
        
        # Define service types
        service_types = ["maintenance", "repair", "inspection", "tire_replacement", "oil_change", "brake_service"]
        
        # Define locations
        locations = {
            "loc1": {"name": "Downtown Service Center", "address": "123 Main St"},
            "loc2": {"name": "Eastside Auto Care", "address": "456 Oak Ave"},
            "loc3": {"name": "Westside Car Clinic", "address": "789 Pine Blvd"}
        }
        
        # Use provided location_id or pick a random one
        location_ids = [location_id] if location_id else list(locations.keys())
        
        # Generate slots for each day between start_date and end_date
        while current_date.date() <= end_date.date():
            # Skip weekends (can be adjusted if needed)
            if current_date.weekday() < 5:  # Monday=0, Sunday=6
                # Generate 4-8 slots per day
                daily_slots = random.randint(4, 8)
                
                for _ in range(daily_slots):
                    # Random hour between 8 AM and 5 PM
                    hour = random.randint(8, 16)
                    # Random minute (0, 15, 30, 45)
                    minute = random.choice([0, 15, 30, 45])
                    
                    slot_time = current_date.replace(hour=hour, minute=minute)
                    
                    # Ensure slot time is within the requested range
                    if slot_time < start_date or slot_time > end_date:
                        continue
                    
                    # Random service duration
                    duration = random.choice(service_durations)
                    
                    # Random selected location
                    selected_location_id = random.choice(location_ids)
                    location_info = locations.get(selected_location_id, {"name": "Unknown", "address": "Unknown"})
                    
                    # Determine if this slot has transport options
                    has_transport = random.random() < 0.7 if include_transport else False
                    
                    # Create the time slot
                    time_slot = {
                        "id": f"slot-{slot_time.strftime('%Y%m%d%H%M')}-{selected_location_id}",
                        "start_time": slot_time.isoformat(),
                        "end_time": (slot_time + timedelta(minutes=duration)).isoformat(),
                        "duration": duration,
                        "location_id": selected_location_id,
                        "location_name": location_info["name"],
                        "location_address": location_info["address"],
                        "service_type": random.choice(service_types),
                        "has_transport": has_transport,
                        "transport_details": {
                            "pickup_available": has_transport,
                            "dropoff_available": has_transport,
                            "shuttle_service": random.random() < 0.5 if has_transport else False,
                            "loaner_car": random.random() < 0.3 if has_transport else False
                        } if has_transport else None
                    }
                    
                    mock_slots.append(time_slot)
            
            # Move to the next day
            current_date = current_date + timedelta(days=1)
        
        # Sort slots by start time
        mock_slots.sort(key=lambda slot: slot["start_time"])
        
        logger.info(f"Found {len(mock_slots)} available slots between {start_date.date()} and {end_date.date()}")
        return mock_slots
    
    def create_booking(self, slot: Dict[str, Any], customer_info: Dict[str, Any], 
                      dtc_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a booking for the specified slot.
        
        Args:
            slot: The time slot to book
            customer_info: Information about the customer
            dtc_info: Optional DTC information that triggered the booking
            
        Returns:
            Booking confirmation details
        """
        booking_id = f"BOOK-{str(uuid.uuid4())[:8]}"
        
        booking = {
            "booking_id": booking_id,
            "slot": slot,
            "customer_info": customer_info,
            "dtc_info": dtc_info,
            "status": "confirmed",
            "created_at": datetime.now().isoformat(),
            "confirmation_number": f"CNF{random.randint(100000, 999999)}",
            "vehicle_id": customer_info.get("vehicle_id")
        }
        
        self.bookings.append(booking)
        
        logger.info(f"Created booking {booking_id} for {customer_info.get('vehicle_id')} at {slot.get('start_time')}")
        return booking
    
    def get_booking(self, booking_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a booking by ID.
        
        Args:
            booking_id: The ID of the booking to retrieve
            
        Returns:
            The booking details or None if not found
        """
        for booking in self.bookings:
            if booking["booking_id"] == booking_id:
                return booking
        return None
    
    def get_bookings_by_vehicle(self, vehicle_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all bookings for a specific vehicle.
        
        Args:
            vehicle_id: The ID of the vehicle
            
        Returns:
            List of bookings for the vehicle
        """
        return [booking for booking in self.bookings if booking.get("vehicle_id") == vehicle_id]
    
    def get_all_bookings(self) -> List[Dict[str, Any]]:
        """
        Retrieve all bookings.
        
        Returns:
            List of all bookings
        """
        return self.bookings
    
    def find_optimal_slot(self, start_date: datetime, end_date: datetime, 
                        urgency: int = 7, include_transport: bool = False,
                        location_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Find the optimal slot based on urgency.
        
        Args:
            start_date: Start date for the search
            end_date: End date for the search
            urgency: Days of urgency (lower = more urgent)
            include_transport: Whether to include transport options
            location_id: Optional location identifier
            
        Returns:
            The optimal time slot or None if none available
        """
        # For urgent cases (1-3 days), find the earliest available slot
        if urgency <= 3:
            slots = self.find_available_slots(start_date, end_date, location_id, include_transport)
            if slots:
                return slots[0]  # Return the earliest slot
        
        # For less urgent cases, find a slot with preferred timing
        else:
            slots = self.find_available_slots(start_date, end_date, location_id, include_transport)
            
            # Try to find a slot during business hours (10 AM - 2 PM)
            preferred_slots = []
            for slot in slots:
                slot_time = datetime.fromisoformat(slot["start_time"])
                if 10 <= slot_time.hour <= 14:
                    preferred_slots.append(slot)
            
            if preferred_slots:
                return preferred_slots[0]
            elif slots:
                return slots[0]
        
        return None
    
    def create_dtc_booking(self, dtc_data: Dict[str, Any], 
                         appointment_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a booking based on DTC data and preferences.
        
        Args:
            dtc_data: The DTC data
            appointment_preferences: Appointment preferences
            
        Returns:
            Booking confirmation or error
        """
        # Extract information from the preferences
        start_date = datetime.fromisoformat(appointment_preferences.get("start_date").replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(appointment_preferences.get("end_date").replace('Z', '+00:00'))
        transport_required = appointment_preferences.get("transport_required", False)
        urgency = appointment_preferences.get("urgency", 7)
        
        # Find the optimal slot based on urgency
        optimal_slot = self.find_optimal_slot(
            start_date=start_date,
            end_date=end_date,
            urgency=urgency,
            include_transport=transport_required
        )
        
        if not optimal_slot:
            return {
                "status": "error",
                "message": "No suitable time slots found for this DTC",
                "timestamp": datetime.now().isoformat()
            }
        
        # Extract customer info from DTC data
        additional_info = dtc_data.get("additional_info", {})
        
        customer_info = {
            "vehicle_id": dtc_data.get("vehicle_id"),
            "customer_id": additional_info.get("customer_id", "unknown"),
            "vehicle_make": additional_info.get("vehicle_make", "unknown"),
            "vehicle_model": additional_info.get("vehicle_model", "unknown"),
            "vehicle_year": additional_info.get("vehicle_year", "unknown"),
            "mileage": additional_info.get("mileage", 0),
            "dtc_code": dtc_data.get("dtc_code")
        }
        
        # Create the booking
        booking = self.create_booking(
            slot=optimal_slot,
            customer_info=customer_info,
            dtc_info=dtc_data
        )
        
        return {
            "status": "booked",
            "message": f"Appointment automatically booked based on DTC {dtc_data.get('dtc_code')}",
            "booking": booking,
            "timestamp": datetime.now().isoformat()
        }

# Create a singleton instance for the application to use
booking_service = BookingService() 