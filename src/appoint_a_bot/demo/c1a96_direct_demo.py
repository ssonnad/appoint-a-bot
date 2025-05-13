#!/usr/bin/env python3
"""
C1A96 Brake Pad Critical DTC Direct Demo

This script demonstrates processing the C1A96 brake pad critical DTC code
directly using the DTCProcessor, bypassing the API for troubleshooting.
"""

import json
from datetime import datetime, timedelta
import sys
import logging
import random
from pprint import pprint

from src.appoint_a_bot.dtc.dtc_processor import DTCProcessor
from src.appoint_a_bot.connector.mcp_connector import MCPConnector
from src.appoint_a_bot.analyzer.analyzer import Analyzer
from src.appoint_a_bot.agent.agent import Agent

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_brake_pad_dtc():
    """
    Process a C1A96 brake pad critical DTC directly using the DTCProcessor
    """
    dtc_data = {
        "dtc_code": "C1A96",  # High severity brake pad thickness critical
        "vehicle_id": f"VIN-BRAKE-{random.randint(10000, 99999)}",
        "timestamp": datetime.now().isoformat(),
        "location": {
            "coordinates": {
                "latitude": 37.7749,
                "longitude": -122.4194
            },
            "address": {
                "street": "123 Main St",
                "city": "San Francisco",
                "state": "CA",
                "zip": "94105"
            },
            "preferred_location_id": f"LOC-{random.randint(100, 999)}",
            "distance_willing_to_travel": 30
        },
        "additional_info": {
            "mileage": random.randint(10000, 50000),
            "customer_id": f"CUST-{random.randint(1000, 9999)}",
            "vehicle_make": "Toyota",
            "vehicle_model": "Camry",
            "vehicle_year": 2020,
            "brake_pad_thickness": "1.8mm"  # Critical thickness
        }
    }
    
    logger.info(f"Processing C1A96 brake pad critical DTC data: {json.dumps(dtc_data, indent=2)}")
    
    # Create the components directly
    dtc_processor = DTCProcessor()
    connector = MCPConnector(api_url="https://example-mcp-api.com/slots", api_key="your_api_key")
    analyzer = Analyzer()
    agent = Agent(mcp_connector=connector, analyzer=analyzer)
    
    # Process the DTC
    processed_data = dtc_processor.process_dtc(dtc_data)
    
    # Check result
    if processed_data["status"] == "error":
        logger.error(f"Error processing DTC: {processed_data['message']}")
        return None
        
    # Display the processed data
    logger.info(f"DTC Processor output: {json.dumps(processed_data, indent=2)}")
    
    # Extract appointment preferences
    appointment_prefs = processed_data.get("appointment_preferences", {})
    
    # Convert ISO format strings to datetime objects
    start_date = datetime.fromisoformat(appointment_prefs.get("start_date").replace('Z', '+00:00'))
    end_date = datetime.fromisoformat(appointment_prefs.get("end_date").replace('Z', '+00:00'))
    transport_required = appointment_prefs.get("transport_required", False)
    location_data = appointment_prefs.get("location", {})
    
    # Set up the agent with customer preferences
    agent.customer_preferences = {
        "start_date": start_date,
        "end_date": end_date,
        "transport_required": transport_required,
        "location_id": location_data.get("customer_preferred_location_id"),
        "vehicle_id": dtc_data.get("vehicle_id"),
        "dtc_data": dtc_data,
        "location": location_data
    }
    
    # Create mock slots for demonstration
    mock_slots = [
        {
            "slot_id": "SLOT-001",
            "start_time": (datetime.now() + timedelta(hours=2)).isoformat(),
            "end_time": (datetime.now() + timedelta(hours=3)).isoformat(),
            "available": True,
            "service_type": "brake_service",
            "location": {
                "name": "Downtown Service Center",
                "address": "123 Service St, San Francisco, CA 94105",
                "coordinates": {
                    "latitude": 37.7749,
                    "longitude": -122.4194
                }
            },
            "transport_included": transport_required
        },
        {
            "slot_id": "SLOT-002",
            "start_time": (datetime.now() + timedelta(hours=4)).isoformat(),
            "end_time": (datetime.now() + timedelta(hours=5)).isoformat(),
            "available": True,
            "service_type": "brake_service",
            "location": {
                "name": "Sunset Service Center",
                "address": "456 Auto Ave, San Francisco, CA 94122",
                "coordinates": {
                    "latitude": 37.7500,
                    "longitude": -122.4800
                }
            },
            "transport_included": transport_required
        }
    ]
    
    # Find the best time slot
    filtered_slots = analyzer.filter_slots_by_criteria(mock_slots, agent.customer_preferences)
    closest_slot = analyzer.find_closest_time_slot(filtered_slots)[0] if filtered_slots else None
    
    if not closest_slot:
        logger.warning("No suitable slots found after filtering")
        return {
            "status": "no_slots",
            "message": "No suitable time slots found after filtering",
            "dtc_info": processed_data
        }
        
    # Auto-confirm the booking for the best available slot
    agent.current_recommendation = closest_slot
    booking_confirmation = agent._handle_booking_confirmation()
    
    # Create a booking record
    booking_record = {
        "booking_id": f"BOOK-{random.randint(1000, 9999)}",
        "slot": closest_slot,
        "dtc_info": processed_data,
        "vehicle_id": dtc_data.get("vehicle_id"),
        "location": location_data,
        "timestamp": datetime.now().isoformat(),
        "customer_id": dtc_data.get("additional_info", {}).get("customer_id")
    }
    
    # Return both DTC info and booking confirmation
    result = {
        "status": "booked",
        "message": f"Appointment automatically booked based on DTC {processed_data['dtc_code']}",
        "dtc_info": processed_data,
        "booking": booking_record,
        "confirmation": booking_confirmation
    }
    
    logger.info(f"Automatically booked appointment for DTC {processed_data['dtc_code']} - Vehicle: {dtc_data.get('vehicle_id')}")
    return result
    
def run_demo():
    """
    Run the C1A96 brake pad DTC direct demo
    """
    print("\n=== C1A96 Brake Pad Critical DTC Direct Demo ===\n")
    print("This demo simulates processing a critical brake pad DTC code (C1A96)")
    print("directly with the DTCProcessor, bypassing the API layer.\n")
    
    # Process the C1A96 brake pad DTC
    print("\nProcessing C1A96 brake pad critical DTC...\n")
    result = process_brake_pad_dtc()
    
    if not result:
        print("Failed to process the DTC. Check the logs for details.")
        return 1
        
    # Check the result
    status = result.get("status")
    if status == "booked":
        print(f"\nSUCCESS: Brake pad DTC (C1A96) was automatically booked!")
        print(f"Message: {result.get('message')}")
        
        # Display booking details
        booking = result.get("booking", {})
        booking_id = booking.get("booking_id", "Unknown")
        slot = booking.get("slot", {})
        
        print("\nBooking Details:")
        print(f"Booking ID: {booking_id}")
        print(f"Vehicle: {booking.get('vehicle_id')}")
        
        # Try to get the slot details
        if slot:
            start_time = slot.get("start_time", "Unknown")
            if start_time != "Unknown":
                try:
                    start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00')).strftime("%A, %B %d at %I:%M %p")
                except:
                    pass
            
            print(f"Appointment: {start_time}")
            print(f"Transport included: {'Yes' if slot.get('transport_included') else 'No'}")
            
            if slot.get("location"):
                location = slot.get("location")
                print(f"Location: {location.get('name', 'Unknown')} - {location.get('address', 'Unknown')}")
    elif status == "no_slots":
        print(f"\nNOTE: No available slots found for the brake pad DTC (C1A96)")
        print(f"Message: {result.get('message')}")
        print("\nDTC was processed correctly but booking could not be completed due to no available slots.")
        
        # Display DTC info
        dtc_info = result.get("dtc_info", {})
        print("\nDTC Details:")
        print(f"Code: {dtc_info.get('dtc_code')} - {dtc_info.get('description')}")
        print(f"Severity: {dtc_info.get('severity')}")
        
        # Display appointment preferences
        prefs = dtc_info.get("appointment_preferences", {})
        print("\nAppointment Preferences:")
        print(f"Urgency: {prefs.get('urgency', 'Unknown')} days")
        print(f"Transport required: {'Yes' if prefs.get('transport_required') else 'No'}")
        print(f"Interactive booking: {'Yes' if prefs.get('interactive_booking') else 'No - Automatic booking'}")
    else:
        print(f"\nUnexpected status: {status}")
        print(f"Response: {json.dumps(result, indent=2)}")
        
    print("\nDemo completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(run_demo()) 