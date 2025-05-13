#!/usr/bin/env python3
"""
Interactive DTC Demo Script

This script demonstrates the flow of creating an interactive booking session
through the DTC API with location information. It simulates both sending a DTC
and the customer interaction with the agent to complete a booking.
"""

import requests
import json
from datetime import datetime, timedelta
import time
import sys
import logging
import random
from pprint import pprint

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# DTC API URL (assumes the API is running locally)
API_URL = "http://localhost:8080"

def send_dtc_with_location():
    """
    Send a DTC with location information to trigger an interactive booking session.
    Uses a medium severity DTC to ensure we get the interactive flow.
    """
    dtc_data = {
        "dtc_code": "P0100",  # Medium severity Mass Air Flow sensor issue
        "vehicle_id": f"VIN-{random.randint(10000, 99999)}",
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
            "vehicle_year": 2020
        }
    }
    
    logger.info(f"Sending DTC data: {json.dumps(dtc_data, indent=2)}")
    
    try:
        response = requests.post(f"{API_URL}/api/dtc", json=dtc_data)
        response.raise_for_status()
        result = response.json()
        
        logger.info(f"DTC API response: {json.dumps(result, indent=2)}")
        
        if result.get("status") == "interactive_session_created":
            return result.get("session_id")
        else:
            logger.error("Did not receive an interactive session ID. Possibly a high severity DTC that was auto-booked.")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending DTC: {e}")
        return None

def start_interactive_session(session_id):
    """
    Start the interactive booking session with the agent
    """
    if not session_id:
        logger.error("No session ID provided")
        return False
        
    try:
        # First GET request to start the session and get the initial recommendation
        response = requests.get(f"{API_URL}/api/dtc/session/{session_id}")
        response.raise_for_status()
        session_data = response.json()
        
        logger.info(f"Session data: {json.dumps(session_data, indent=2)}")
        
        # Now POST to start the conversation
        start_response = requests.post(f"{API_URL}/api/dtc/session/{session_id}", json={"response": {"type": "start"}})
        start_response.raise_for_status()
        conversation = start_response.json()
        
        logger.info("=== CONVERSATION START ===")
        logger.info(f"Agent: {conversation['agent_response']['message']}")
        
        # Simulate user rejecting the first recommendation
        logger.info("Customer: I'd like to see other options")
        reject_response = requests.post(
            f"{API_URL}/api/dtc/session/{session_id}", 
            json={"response": {"type": "reject"}}
        )
        reject_response.raise_for_status()
        conversation = reject_response.json()
        logger.info(f"Agent: {conversation['agent_response']['message']}")
        
        # Simulate user providing a date range
        next_week_start = datetime.now() + timedelta(days=7)
        next_week_end = next_week_start + timedelta(days=5)
        logger.info(f"Customer: I'd prefer next week, from {next_week_start.strftime('%A, %B %d')} to {next_week_end.strftime('%A, %B %d')}")
        
        date_response = requests.post(
            f"{API_URL}/api/dtc/session/{session_id}", 
            json={
                "response": {
                    "type": "date_range",
                    "start_date": next_week_start.isoformat(),
                    "end_date": next_week_end.isoformat()
                }
            }
        )
        date_response.raise_for_status()
        conversation = date_response.json()
        logger.info(f"Agent: {conversation['agent_response']['message']}")
        
        # Respond to transport question
        logger.info("Customer: Yes, I'll need transport")
        transport_response = requests.post(
            f"{API_URL}/api/dtc/session/{session_id}", 
            json={
                "response": {
                    "type": "transport_preference",
                    "transport_required": True
                }
            }
        )
        transport_response.raise_for_status()
        conversation = transport_response.json()
        logger.info(f"Agent: {conversation['agent_response']['message']}")
        
        # Accept the appointment
        logger.info("Customer: That works for me, let's book it")
        accept_response = requests.post(
            f"{API_URL}/api/dtc/session/{session_id}", 
            json={"response": {"type": "accept"}}
        )
        accept_response.raise_for_status()
        confirmation = accept_response.json()
        
        logger.info(f"Agent: {confirmation['agent_response']['message']}")
        logger.info("=== BOOKING CONFIRMED ===")
        
        # Print the booking details
        if confirmation.get("booking"):
            logger.info("Booking Details:")
            booking = confirmation["booking"]
            logger.info(f"Booking ID: {booking['booking_id']}")
            logger.info(f"Service for: {booking['dtc_info']['description']}")
            
            slot = booking["slot"]
            start_time = datetime.fromisoformat(slot["start_time"].replace('Z', '+00:00')).strftime("%A, %B %d at %I:%M %p")
            logger.info(f"Appointment: {start_time}")
            
            if slot.get("location"):
                location = slot["location"]
                logger.info(f"Location: {location.get('name', 'Unknown')} - {location.get('address', 'No address')}")
                
            logger.info(f"Transport included: {'Yes' if slot.get('transport_included') else 'No'}")
        
        return True
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error in interactive session: {e}")
        return False
        
def run_demo():
    """
    Run the full interactive DTC demo
    """
    print("\n=== Interactive DTC Booking Demo ===\n")
    print("This demo simulates sending a DTC code with location data and")
    print("then going through an interactive booking session with the agent.\n")
    
    # Check if the API is running
    try:
        health_check = requests.get(f"{API_URL}/health")
        health_check.raise_for_status()
    except requests.exceptions.RequestException:
        print(f"ERROR: Could not connect to the API at {API_URL}")
        print("Please make sure the API server is running by executing:")
        print("  python -m src.appoint_a_bot.main start-api")
        return 1
        
    # Step 1: Send DTC with location and get a session ID
    print("\nStep 1: Sending DTC with location data...\n")
    session_id = send_dtc_with_location()
    
    if not session_id:
        print("Failed to create an interactive session. Check the logs for details.")
        return 1
        
    print(f"\nCreated interactive session: {session_id}\n")
    
    # Step 2: Go through the interactive booking flow
    print("\nStep 2: Starting interactive booking session...\n")
    time.sleep(1)  # Small delay for better readability
    
    success = start_interactive_session(session_id)
    
    if success:
        print("\nDemo completed successfully!")
        
        # Check all bookings
        print("\nFetching all DTC bookings...\n")
        try:
            bookings_response = requests.get(f"{API_URL}/api/dtc/bookings")
            bookings_response.raise_for_status()
            bookings = bookings_response.json()
            
            print(f"Found {len(bookings['bookings'])} total bookings:")
            for idx, booking in enumerate(bookings['bookings'], 1):
                print(f"\n-- Booking {idx} --")
                print(f"ID: {booking['booking_id']}")
                print(f"Vehicle: {booking['vehicle_id']}")
                if 'dtc_info' in booking:
                    print(f"DTC: {booking['dtc_info']['dtc_code']} - {booking['dtc_info'].get('description', 'Unknown')}")
                if 'session_id' in booking:
                    print(f"Interactive Session: Yes (ID: {booking['session_id']})")
                else:
                    print("Interactive Session: No (Auto-booked)")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching bookings: {e}")
    else:
        print("\nDemo encountered errors. Check the logs for details.")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(run_demo()) 