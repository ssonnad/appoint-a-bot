#!/usr/bin/env python3
"""
C1A96 Brake Pad Critical DTC Demo

This script demonstrates sending the C1A96 brake pad critical DTC code
with location data to trigger automatic booking.
"""

import requests
import json
from datetime import datetime
import sys
import logging
import random
from pprint import pprint

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# DTC API URL (assumes the API is running locally)
API_URL = "http://localhost:8080"

def send_brake_pad_dtc():
    """
    Send a C1A96 brake pad critical DTC with location information
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
    
    logger.info(f"Sending C1A96 brake pad critical DTC data: {json.dumps(dtc_data, indent=2)}")
    
    try:
        # Print all API endpoints we're trying to access
        print(f"Attempting to access the following API endpoints:")
        print(f"- Health check: {API_URL}/health")
        print(f"- Send DTC: {API_URL}/api/dtc")
        print(f"- Get bookings: {API_URL}/api/dtc/bookings")
        
        # Try to send the DTC
        response = requests.post(f"{API_URL}/api/dtc", json=dtc_data)
        response.raise_for_status()
        result = response.json()
        
        logger.info(f"DTC API response: {json.dumps(result, indent=2)}")
        
        return result
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending DTC: {e}")
        
        # If we get a 404 error, try some alternative API paths
        if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 404:
            print("\nTrying alternative API paths...")
            
            alternative_paths = [
                "/dtc",                 # No 'api' prefix
                "/api/dtcs",            # Plural form
                "/api/v1/dtc",          # With version
                "/bookings/dtc"         # Different order
            ]
            
            for path in alternative_paths:
                try:
                    print(f"Trying: {API_URL}{path}")
                    alt_response = requests.post(f"{API_URL}{path}", json=dtc_data)
                    if alt_response.status_code == 200 or alt_response.status_code == 201:
                        print(f"SUCCESS! Found working API endpoint: {API_URL}{path}")
                        return alt_response.json()
                except:
                    pass
                    
            print("All alternative paths failed.")
        
        # Try to get some debug information from the API
        try:
            health_response = requests.get(f"{API_URL}/health")
            print(f"\nAPI health check: {health_response.status_code}")
            if health_response.status_code == 200:
                print(f"API health response: {health_response.json()}")
        except:
            print("Could not reach API health endpoint")
            
        return None
        
def run_demo():
    """
    Run the C1A96 brake pad DTC demo
    """
    print("\n=== C1A96 Brake Pad Critical DTC Demo ===\n")
    print("This demo simulates sending a critical brake pad DTC code (C1A96)")
    print("with location data to trigger automatic booking.\n")
    
    # Check if the API is running
    try:
        health_check = requests.get(f"{API_URL}/health")
        health_check.raise_for_status()
        print(f"API is running! Health check response: {health_check.json()}")
    except requests.exceptions.RequestException:
        print(f"ERROR: Could not connect to the API at {API_URL}")
        print("Please make sure the API server is running by executing:")
        print("  python -m src.appoint_a_bot.main start-api")
        return 1
        
    # Send the C1A96 brake pad DTC
    print("\nSending C1A96 brake pad critical DTC...\n")
    result = send_brake_pad_dtc()
    
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
        print(f"API response: {json.dumps(result, indent=2)}")
        
    # Check all bookings
    print("\nChecking all DTC bookings...\n")
    try:
        bookings_response = requests.get(f"{API_URL}/api/dtc/bookings")
        bookings_response.raise_for_status()
        bookings = bookings_response.json()
        
        print(f"Found {len(bookings['bookings'])} total bookings:")
        for idx, booking in enumerate(bookings['bookings'], 1):
            print(f"\n-- Booking {idx} --")
            print(f"ID: {booking.get('booking_id', 'Unknown')}")
            print(f"Vehicle: {booking.get('vehicle_id', 'Unknown')}")
            if 'dtc_info' in booking:
                print(f"DTC: {booking['dtc_info'].get('dtc_code', 'Unknown')} - {booking['dtc_info'].get('description', 'Unknown')}")
            if 'session_id' in booking:
                print(f"Interactive Session: Yes (ID: {booking['session_id']})")
            else:
                print("Interactive Session: No (Auto-booked)")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching bookings: {e}")
        
    print("\nDemo completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(run_demo()) 