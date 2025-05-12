#!/usr/bin/env python3
from datetime import datetime, timedelta
import json
import time  # For simulating delays

from src.appoint_a_bot.connector.mcp_connector import MCPConnector
from src.appoint_a_bot.analyzer.analyzer import Analyzer
from src.appoint_a_bot.agent.agent import Agent

def print_with_delay(message, delay=1.0):
    """Print a message with a short delay to simulate conversation flow."""
    print(message)
    time.sleep(delay)

def run_successful_transport_demo():
    """
    Run a demonstration of successfully booking an appointment with transport.
    """
    print("\n\n=== SCENARIO 1: BOOKING WITH TRANSPORT ===")
    print("In this scenario, the customer will find and book an appointment with transport options.")
    
    # Initialize components
    mcp_connector = MCPConnector(
        api_url="https://example-mcp-api.com/slots",
        api_key="demo_api_key"
    )
    
    analyzer = Analyzer()
    agent = Agent(mcp_connector=mcp_connector, analyzer=analyzer)
    
    # Set up our dates - we'll ensure transport is available
    today = datetime.now()
    transport_date = today + timedelta(days=3)
    
    # Create mock implementation with guaranteed transport options
    def mock_transport_slots(*args, **kwargs):
        include_transport = kwargs.get("include_transport", False)
        
        # Always return at least one slot
        slots = [{
            "id": "morning_slot", 
            "start_time": (today + timedelta(days=1)).replace(hour=9, minute=0).isoformat(),
            "end_time": (today + timedelta(days=1)).replace(hour=9, minute=45).isoformat(),
            "location_id": "loc_1",
            "has_transport": False,
            "provider_name": "Dr. Smith"
        }]
        
        # Add transport slot
        transport_slot = {
            "id": "transport_slot",
            "start_time": transport_date.replace(hour=14, minute=0).isoformat(),
            "end_time": transport_date.replace(hour=14, minute=45).isoformat(),
            "location_id": "loc_2",
            "has_transport": True,
            "provider_name": "Dr. Johnson"
        }
        
        # Only filter by transport if requested
        if include_transport:
            return [transport_slot]
        else:
            return slots + [transport_slot]
    
    # Replace the method
    mcp_connector.fetch_time_slots = mock_transport_slots
    
    # Start conversation
    print_with_delay("\n=== Starting Conversation ===")
    response = agent.start_conversation()
    print_with_delay(f"Agent: {response['message']}")
    
    # Customer rejects initial recommendation
    print_with_delay("\nCustomer: I need a different time.")
    response = agent.handle_response({"type": "reject"})
    print_with_delay(f"Agent: {response['message']}")
    
    # Customer provides date range containing transport option
    print_with_delay(f"\nCustomer: I'm looking for dates around day {transport_date.day}.")
    customer_response = {
        "type": "date_range",
        "start_date": transport_date - timedelta(days=1),
        "end_date": transport_date + timedelta(days=1)
    }
    response = agent.handle_response(customer_response)
    print_with_delay(f"Agent: {response['message']}")
    
    # Customer requests transport
    print_with_delay("\nCustomer: Yes, I'll need transport.")
    response = agent.handle_response({"type": "transport_preference", "transport_required": True})
    print_with_delay(f"Agent: {response['message']}")
    
    # Customer accepts
    print_with_delay("\nCustomer: Perfect! I'll take that appointment.")
    response = agent.handle_response({"type": "accept"})
    print_with_delay(f"Agent: {response['message']}")
    
    # Show booking details
    if response["status"] == "confirmation" and "slot" in response:
        slot = response["slot"]
        print_with_delay("\n=== Booking Complete ===")
        print_with_delay("\nAppointment Details:")
        print_with_delay(f"Date: {datetime.fromisoformat(slot['start_time']).strftime('%A, %B %d, %Y')}")
        print_with_delay(f"Time: {datetime.fromisoformat(slot['start_time']).strftime('%I:%M %p')} - {datetime.fromisoformat(slot['end_time']).strftime('%I:%M %p')}")
        print_with_delay(f"Provider: {slot['provider_name']}")
        print_with_delay(f"Location ID: {slot['location_id']}")
        print_with_delay(f"Transport Included: Yes")

def run_standard_booking_demo():
    """
    Run a demonstration of booking a standard appointment without transport.
    """
    print("\n\n=== SCENARIO 2: STANDARD BOOKING WITHOUT TRANSPORT ===")
    print("In this scenario, the customer will book a standard appointment without transport.")
    
    # Initialize components
    mcp_connector = MCPConnector(
        api_url="https://example-mcp-api.com/slots",
        api_key="demo_api_key"
    )
    
    analyzer = Analyzer()
    agent = Agent(mcp_connector=mcp_connector, analyzer=analyzer)
    
    # Set up our dates
    today = datetime.now()
    target_date = today + timedelta(days=2)
    
    # Create mock implementation with standard slots
    def mock_standard_slots(*args, **kwargs):
        include_transport = kwargs.get("include_transport", False)
        
        # Create slots without transport
        slots = []
        for hour in [9, 11, 14]:
            slots.append({
                "id": f"slot_{hour}", 
                "start_time": target_date.replace(hour=hour, minute=0).isoformat(),
                "end_time": target_date.replace(hour=hour, minute=45).isoformat(),
                "location_id": "loc_1",
                "has_transport": False,
                "provider_name": "Dr. Smith"
            })
        
        # Filter by transport if needed (will return empty for transport=True)
        if include_transport:
            return [slot for slot in slots if slot.get("has_transport", False)]
        return slots
    
    # Replace the method
    mcp_connector.fetch_time_slots = mock_standard_slots
    
    # Start conversation
    print_with_delay("\n=== Starting Conversation ===")
    response = agent.start_conversation()
    print_with_delay(f"Agent: {response['message']}")
    
    # Customer provides specific date range
    print_with_delay("\nCustomer: I'd like to check for appointments next week.")
    customer_response = {
        "type": "date_range",
        "start_date": target_date,
        "end_date": target_date + timedelta(days=1)
    }
    response = agent.handle_response(customer_response)
    print_with_delay(f"Agent: {response['message']}")
    
    # Customer doesn't need transport
    print_with_delay("\nCustomer: No, I don't need transport.")
    response = agent.handle_response({"type": "transport_preference", "transport_required": False})
    print_with_delay(f"Agent: {response['message']}")
    
    # Customer accepts
    print_with_delay("\nCustomer: That time works well for me.")
    response = agent.handle_response({"type": "accept"})
    print_with_delay(f"Agent: {response['message']}")
    
    # Show booking details
    if response["status"] == "confirmation" and "slot" in response:
        slot = response["slot"]
        print_with_delay("\n=== Booking Complete ===")
        print_with_delay("\nAppointment Details:")
        print_with_delay(f"Date: {datetime.fromisoformat(slot['start_time']).strftime('%A, %B %d, %Y')}")
        print_with_delay(f"Time: {datetime.fromisoformat(slot['start_time']).strftime('%I:%M %p')} - {datetime.fromisoformat(slot['end_time']).strftime('%I:%M %p')}")
        print_with_delay(f"Provider: {slot['provider_name']}")
        print_with_delay(f"Location ID: {slot['location_id']}")
        print_with_delay(f"Transport Included: No")

def main():
    """Run the complete demonstration."""
    print("=== Appoint-a-Bot Complete Demonstration ===")
    print("This demo will show two scenarios:")
    print("1. Booking an appointment with transport options")
    print("2. Booking a standard appointment without transport")
    
    # Run both demos
    run_successful_transport_demo()
    run_standard_booking_demo()
    
    print("\n\n=== Demonstration Complete ===")
    print("The Appoint-a-Bot system successfully handled both booking scenarios.")

if __name__ == "__main__":
    main() 