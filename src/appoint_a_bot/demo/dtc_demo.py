#!/usr/bin/env python3
"""
DTC API Demo Script

This script demonstrates how to use the DTC API to process vehicle diagnostic trouble codes
and automatically book appointments based on the severity of the issues.
"""

import json
import requests
from datetime import datetime
import time
import threading
import logging
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.appoint_a_bot.dtc.api import start_api
from src.appoint_a_bot.dtc.dtc_processor import DTCProcessor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API port (changed to avoid conflicts with macOS AirPlay)
API_PORT = 8080

# API endpoint (when running locally)
API_URL = f"http://localhost:{API_PORT}/api/dtc"
BOOKINGS_URL = f"http://localhost:{API_PORT}/api/dtc/bookings"
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

def send_dtc_data(dtc_code, vehicle_id, additional_info=None):
    """Send DTC data to the API"""
    if additional_info is None:
        additional_info = {}
        
    data = {
        "dtc_code": dtc_code,
        "vehicle_id": vehicle_id,
        "timestamp": datetime.now().isoformat(),
        "additional_info": additional_info
    }
    
    logger.info(f"Sending DTC data: {data}")
    
    try:
        response = requests.post(API_URL, json=data)
        logger.info(f"Response status code: {response.status_code}")
        
        if response.status_code in (200, 201):
            result = response.json()
            logger.info(f"Successfully processed DTC data. Response: {json.dumps(result, indent=2)}")
            return result
        else:
            logger.error(f"Error response: {response.text}")
            return None
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None

def get_all_bookings():
    """Get all DTC-triggered bookings"""
    try:
        response = requests.get(BOOKINGS_URL)
        if response.status_code == 200:
            return response.json()["bookings"]
        else:
            logger.error(f"Error fetching bookings: {response.text}")
            return []
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return []

def run_demo():
    """Run the full DTC API demo"""
    logger.info("Starting DTC API Demo")
    
    # Start the API server in a separate thread
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    
    # Wait for the API server to be ready
    if not wait_for_api_ready():
        return
    
    # Demonstration cases
    demo_cases = [
        # High severity engine issue
        {
            "dtc_code": "P0001",
            "vehicle_id": "VIN12345",
            "additional_info": {
                "mileage": 35000,
                "customer_id": "CUST123",
                "vehicle_make": "Toyota",
                "vehicle_model": "Camry",
                "vehicle_year": 2020
            }
        },
        # Medium severity issue
        {
            "dtc_code": "P0100",
            "vehicle_id": "VIN67890",
            "additional_info": {
                "mileage": 52000,
                "customer_id": "CUST456",
                "vehicle_make": "Honda",
                "vehicle_model": "Accord",
                "vehicle_year": 2019
            }
        },
        # Low severity body issue
        {
            "dtc_code": "B0001",
            "vehicle_id": "VIN24680",
            "additional_info": {
                "mileage": 15000,
                "customer_id": "CUST789",
                "vehicle_make": "Ford",
                "vehicle_model": "F-150",
                "vehicle_year": 2021
            }
        },
        # Urgent brake pad replacement issue
        {
            "dtc_code": "C0045",
            "vehicle_id": "VIN13579",
            "additional_info": {
                "mileage": 45000,
                "customer_id": "CUST321",
                "vehicle_make": "BMW",
                "vehicle_model": "X5",
                "vehicle_year": 2022,
                "brake_pad_thickness": "2mm"
            }
        }
    ]
    
    # Process each demo case
    for case in demo_cases:
        logger.info(f"\n{'-'*50}")
        logger.info(f"Processing DTC: {case['dtc_code']} for vehicle: {case['vehicle_id']}")
        result = send_dtc_data(
            case["dtc_code"],
            case["vehicle_id"],
            case["additional_info"]
        )
        
        if result:
            severity = result["dtc_info"]["severity"]
            message = result["message"]
            logger.info(f"Result: {message}")
            logger.info(f"Severity: {severity}")
            
            # Add a delay between requests
            time.sleep(1)
    
    # Display all bookings
    logger.info(f"\n{'-'*50}")
    logger.info("All DTC-triggered bookings:")
    bookings = get_all_bookings()
    
    for booking in bookings:
        dtc = booking["dtc_info"]["dtc_code"]
        vehicle = booking["vehicle_id"]
        severity = booking["dtc_info"]["severity"]
        slot_time = datetime.fromisoformat(booking["slot"]["start_time"].replace('Z', '+00:00'))
        formatted_time = slot_time.strftime("%A, %B %d at %I:%M %p")
        
        logger.info(f"Booking ID: {booking['booking_id']}")
        logger.info(f"Vehicle: {vehicle} - DTC: {dtc} (Severity: {severity})")
        logger.info(f"Appointment: {formatted_time}")
        logger.info(f"{'-'*30}")
    
    logger.info("Demo completed successfully!")
    
    # Keep the main thread running so we can see the results
    try:
        while api_thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Demo terminated by user")

if __name__ == "__main__":
    run_demo() 