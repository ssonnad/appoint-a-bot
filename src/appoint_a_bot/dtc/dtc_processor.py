"""
DTC Processor for handling vehicle diagnostic trouble codes.
"""
from typing import Dict, Any, Optional, List, Tuple
import logging
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DTCProcessor:
    """
    Processes Diagnostic Trouble Codes (DTCs) from vehicles and determines
    appointment needs based on the severity of the codes.
    """
    
    # Mapping of DTC codes to their severity levels and appointment urgency
    DTC_SEVERITY = {
        # Engine Codes (P0xxx)
        "P0001": {"severity": "high", "urgency_days": 1, "description": "Fuel Volume Regulator Control Circuit/Open"},
        "P0002": {"severity": "high", "urgency_days": 1, "description": "Fuel Volume Regulator Control Circuit Range/Performance"},
        "P0100": {"severity": "medium", "urgency_days": 7, "description": "Mass or Volume Air Flow Circuit Malfunction"},
        "P0101": {"severity": "medium", "urgency_days": 7, "description": "Mass or Volume Air Flow Circuit Range/Performance Problem"},
        
        # Transmission Codes (P0xxx)
        "P0700": {"severity": "high", "urgency_days": 3, "description": "Transmission Control System Malfunction"},
        "P0701": {"severity": "high", "urgency_days": 3, "description": "Transmission Control System Range/Performance"},
        
        # Body Codes (B0xxx)
        "B0001": {"severity": "low", "urgency_days": 14, "description": "Body Code - Driver's Frontal Squib 1 Circuit Resistance Low"},
        "B0002": {"severity": "low", "urgency_days": 14, "description": "Body Code - Driver's Frontal Squib 1 Circuit Resistance High"},
        
        # Chassis Codes (C0xxx)
        "C0001": {"severity": "medium", "urgency_days": 5, "description": "Chassis Code - Vehicle Speed Information Circuit"},
        "C0035": {"severity": "high", "urgency_days": 2, "description": "Left Front Wheel Speed Circuit Malfunction"},
        "C0045": {"severity": "high", "urgency_days": 1, "description": "Brake Pad Wear Sensor Circuit - Critical Pad Thickness"},
        "C1A96": {"severity": "high", "urgency_days": 1, "description": "Brake Pad Thickness Critical - Immediate Replacement Required"},
        
        # Default case
        "default": {"severity": "medium", "urgency_days": 7, "description": "Unknown DTC code"}
    }
    
    def __init__(self):
        """Initialize the DTC Processor."""
        logger.info("DTC Processor initialized")
    
    def process_dtc(self, dtc_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the DTC data and determine appointment needs.
        
        Args:
            dtc_data: Dictionary containing DTC information
                - dtc_code: The diagnostic trouble code
                - vehicle_id: Unique identifier for the vehicle
                - timestamp: When the DTC was generated
                - location: Customer location information (coordinates, address)
                - additional_info: Any extra information provided
                
        Returns:
            Dictionary with appointment recommendations
        """
        dtc_code = dtc_data.get("dtc_code", "").upper()
        vehicle_id = dtc_data.get("vehicle_id")
        timestamp = dtc_data.get("timestamp")
        location = dtc_data.get("location", {})
        
        if not dtc_code or not vehicle_id:
            return {
                "status": "error",
                "message": "Missing required fields: dtc_code or vehicle_id",
                "timestamp": datetime.now().isoformat()
            }
            
        # Get DTC severity info or use default if not found
        dtc_info = self.DTC_SEVERITY.get(dtc_code, self.DTC_SEVERITY["default"])
        severity = dtc_info["severity"]
        urgency_days = dtc_info["urgency_days"]
        description = dtc_info["description"]
        
        # Calculate appointment date range based on urgency
        start_date = datetime.now()
        end_date = start_date + timedelta(days=urgency_days)
        
        # Transport recommendation based on severity
        needs_transport = severity == "high"
        
        # Process location data
        location_data = {}
        if location:
            location_data = {
                "coordinates": location.get("coordinates", {}),
                "address": location.get("address", {}),
                "customer_preferred_location_id": location.get("preferred_location_id"),
                "distance_willing_to_travel": location.get("distance_willing_to_travel", 25)  # Default 25 miles/km
            }
        
        appointment_recommendation = {
            "status": "processed",
            "dtc_code": dtc_code,
            "vehicle_id": vehicle_id,
            "severity": severity,
            "description": description,
            "appointment_needed": True,
            "appointment_preferences": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "transport_required": needs_transport,
                "urgency": urgency_days,
                "location": location_data,
                "interactive_booking": severity != "high"  # For high severity, auto-book; otherwise interactive
            },
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Processed DTC {dtc_code} for vehicle {vehicle_id} with {severity} severity")
        return appointment_recommendation
        
    def get_dtc_details(self, dtc_code: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific DTC code.
        
        Args:
            dtc_code: The diagnostic trouble code
            
        Returns:
            Dictionary with DTC details
        """
        dtc_code = dtc_code.upper()
        dtc_info = self.DTC_SEVERITY.get(dtc_code, self.DTC_SEVERITY["default"])
        
        return {
            "dtc_code": dtc_code,
            "severity": dtc_info["severity"],
            "description": dtc_info["description"],
            "urgency_days": dtc_info["urgency_days"]
        }
        
    def determine_service_type(self, dtc_code: str) -> str:
        """
        Determine the type of service needed based on the DTC.
        
        Args:
            dtc_code: The diagnostic trouble code
            
        Returns:
            Service type as a string
        """
        dtc_prefix = dtc_code[:1].upper() if dtc_code else "P"
        
        service_types = {
            "P": "engine_service",
            "B": "body_service",
            "C": "chassis_service",
            "U": "network_service"
        }
        
        return service_types.get(dtc_prefix, "general_service") 