#!/usr/bin/env python3
"""
Booking API Demo Script

This script demonstrates how to use the Booking API to:
1. Find available time slots
2. Create a manual booking
3. Process a DTC-triggered booking
4. Retrieve booking information
"""

import json
import requests
from datetime import datetime, timedelta
import time
import threading
import logging
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.appoint_a_bot.dtc.booking_api import start_api
from src.appoint_a_bot.dtc.dtc_processor import DTCProcessor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API port
API_PORT = 8080

# API endpoints
BASE_URL = f"http://localhost:{API_PORT}/api"
SLOTS_URL = f"{BASE_URL}/slots"
BOOKINGS_URL = f"{BASE_URL}/bookings"
DTC_BOOKING_URL = f"{BASE_URL}/dtc-booking"
HEALTH_URL = f"http://localhost:{API_PORT}/health"

def start_api_server():
    """Start the API server in a separate thread"""
    start_api(port=API_PORT, debug=False)

def wait_for_api_ready():
    """Wait until the API server is ready"""
    max_attempts = 10
    attempts = 0
    
    while attempts < max_attempts:
        try:
            response = requests.get(HEALTH_URL)
            if response.status_code == 200:
                logger.info("API server is ready")
                return True
        except requests.RequestException:
            pass
            
        attempts += 1
        logger.info(f"Waiting for API server to start (attempt {attempts}/{max_attempts})...")
        time.sleep(1)
        
    logger.error("API server failed to start")
    return False

def get_available_slots(start_date=None, end_date=None, location_id=None, include_transport=False):
    """Get available slots for booking"""
    params = {}
    
    if start_date:
        params["start_date"] = start_date.isoformat()
    if end_date:
        params["end_date"] = end_date.isoformat()
    if location_id:
        params["location_id"] = location_id
    if include_transport:
        params["include_transport"] = "true"
        
    try:
        response = requests.get(SLOTS_URL, params=params)
        logger.info(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            slots = result.get("slots", [])
            logger.info(f"Found {len(slots)} available slots")
            return slots
        else:
            logger.error(f"Error response: {response.text}")
            return []
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return []

def create_manual_booking(slot_id, vehicle_id, customer_id):
    """Create a manual booking using a specific slot"""
    data = {
        "slot_id": slot_id,
        "customer_info": {
            "vehicle_id": vehicle_id,
            "customer_id": customer_id,
            "vehicle_make": "Test Make",
            "vehicle_model": "Test Model",
            "vehicle_year": 2020,
            "mileage": 30000
        }
    }
    
    logger.info(f"Creating manual booking with data: {data}")
    
    try:
        response = requests.post(BOOKINGS_URL, json=data)
        logger.info(f"Response status code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            logger.info(f"Successfully created booking")
            return result
        else:
            logger.error(f"Error response: {response.text}")
            return None
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None

def create_dtc_booking(dtc_code, vehicle_id, additional_info=None):
    """Create a booking from a DTC code"""
    if additional_info is None:
        additional_info = {}
        
    data = {
        "dtc_code": dtc_code,
        "vehicle_id": vehicle_id,
        "timestamp": datetime.now().isoformat(),
        "additional_info": additional_info
    }
    
    logger.info(f"Creating DTC-triggered booking with data: {data}")
    
    try:
        response = requests.post(DTC_BOOKING_URL, json=data)
        logger.info(f"Response status code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            logger.info(f"Successfully created DTC booking")
            return result
        else:
            logger.error(f"Error response: {response.text}")
            return None
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None

def get_booking(booking_id=None):
    """Get booking information"""
    url = f"{BOOKINGS_URL}/{booking_id}" if booking_id else BOOKINGS_URL
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error fetching booking: {response.text}")
            return None
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None

def run_demo():
    """Run the full Booking API demo"""
    logger.info("Starting Booking API Demo")
    
    # Start the API server in a separate thread
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    
    # Wait for the API server to be ready
    if not wait_for_api_ready():
        return
    
    # Step 1: Get available slots
    logger.info("\n" + "=" * 50)
    logger.info("STEP 1: Finding available slots")
    start_date = datetime.now()
    end_date = start_date + timedelta(days=7)
    
    # Get slots with transport options
    slots = get_available_slots(
        start_date=start_date, 
        end_date=end_date, 
        include_transport=True
    )
    
    if not slots:
        logger.error("No slots available. Demo cannot continue.")
        return
    
    # Print a few sample slots
    logger.info("\nSample available slots:")
    for i, slot in enumerate(slots[:3]):
        slot_time = datetime.fromisoformat(slot["start_time"])
        formatted_time = slot_time.strftime("%A, %B %d at %I:%M %p")
        logger.info(f"Slot {i+1}: {formatted_time} at {slot['location_name']}")
        logger.info(f"  ID: {slot['id']}")
        logger.info(f"  Duration: {slot['duration']} minutes")
        logger.info(f"  Transport: {'Available' if slot['has_transport'] else 'Not available'}")
        logger.info(f"  Service type: {slot['service_type']}")
        logger.info("-" * 30)
    
    # Step 2: Create a manual booking
    logger.info("\n" + "=" * 50)
    logger.info("STEP 2: Creating a manual booking")
    
    if slots:
        selected_slot = slots[0]
        booking_result = create_manual_booking(
            slot_id=selected_slot["id"],
            vehicle_id="TEST-VIN-001",
            customer_id="TEST-CUST-001"
        )
        
        if booking_result:
            booking = booking_result.get("booking", {})
            booking_id = booking.get("booking_id")
            logger.info(f"Successfully created manual booking: {booking_id}")
            
            # Step 3: Retrieve the booking
            logger.info("\n" + "=" * 50)
            logger.info("STEP 3: Retrieving booking information")
            
            booking_info = get_booking(booking_id)
            if booking_info:
                logger.info(f"Retrieved booking information for: {booking_id}")
                logger.info(f"Status: {booking_info.get('booking', {}).get('status')}")
                logger.info(f"Confirmation: {booking_info.get('booking', {}).get('confirmation_number')}")
    
    # Step 4: Create a DTC-triggered booking
    logger.info("\n" + "=" * 50)
    logger.info("STEP 4: Creating a DTC-triggered booking")
    
    dtc_result = create_dtc_booking(
        dtc_code="C0045",  # Brake pad wear sensor
        vehicle_id="TEST-VIN-002",
        additional_info={
            "customer_id": "TEST-CUST-002",
            "vehicle_make": "BMW",
            "vehicle_model": "X5",
            "vehicle_year": 2022,
            "mileage": 45000,
            "brake_pad_thickness": "2mm"
        }
    )
    
    if dtc_result:
        dtc_booking = dtc_result.get("booking", {})
        logger.info(f"Successfully created DTC-triggered booking")
        logger.info(f"DTC Code: {dtc_result.get('dtc_info', {}).get('dtc_code')}")
        logger.info(f"Severity: {dtc_result.get('dtc_info', {}).get('severity')}")
        
        # Get the slot information
        slot = dtc_booking.get("slot", {})
        if slot:
            slot_time = datetime.fromisoformat(slot.get("start_time", ""))
            formatted_time = slot_time.strftime("%A, %B %d at %I:%M %p")
            logger.info(f"Appointment scheduled for: {formatted_time}")
            logger.info(f"Location: {slot.get('location_name')}")
            logger.info(f"Transport: {'Included' if slot.get('has_transport') else 'Not included'}")
    
    # Step 5: List all bookings
    logger.info("\n" + "=" * 50)
    logger.info("STEP 5: Listing all bookings")
    
    all_bookings = get_booking()
    if all_bookings:
        bookings = all_bookings.get("bookings", [])
        logger.info(f"Total bookings: {len(bookings)}")
        
        for i, booking in enumerate(bookings):
            logger.info(f"\nBooking {i+1}:")
            logger.info(f"ID: {booking.get('booking_id')}")
            logger.info(f"Vehicle: {booking.get('vehicle_id')}")
            
            slot = booking.get("slot", {})
            if slot:
                slot_time = datetime.fromisoformat(slot.get("start_time", ""))
                formatted_time = slot_time.strftime("%A, %B %d at %I:%M %p")
                logger.info(f"Time: {formatted_time}")
                logger.info(f"Location: {slot.get('location_name')}")
    
    logger.info("\n" + "=" * 50)
    logger.info("Demo completed successfully!")
    
    # Keep the main thread running so we can see the results
    try:
        while api_thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Demo terminated by user")

if __name__ == "__main__":
    run_demo() 