#!/usr/bin/env python3
from datetime import datetime, timedelta
import json

from src.appoint_a_bot.connector.mcp_connector import MCPConnector
from src.appoint_a_bot.analyzer.analyzer import Analyzer
from src.appoint_a_bot.agent.agent import Agent

def run_demo():
    """
    Run a realistic conversation demo that demonstrates the appointment booking system.
    """
    print("=== Appoint-a-Bot Interactive Demo ===")
    
    # Initialize components
    mcp_connector = MCPConnector(
        api_url="https://example-mcp-api.com/slots",
        api_key="demo_api_key"
    )
    
    analyzer = Analyzer()
    agent = Agent(mcp_connector=mcp_connector, analyzer=analyzer)
    
    # Set up mock data and dates for our demo
    # Date with transport options
    transport_date = datetime.now() + timedelta(days=3)
    transport_formatted = transport_date.strftime("%Y-%m-%d")
    
    # Create a mock implementation that handles specific test cases
    def mock_fetch_time_slots(*args, **kwargs):
        include_transport = kwargs.get("include_transport", False)
        start_date = kwargs.get("start_date", datetime.now())
        end_date = kwargs.get("end_date", datetime.now() + timedelta(days=14))
        
        # Generate slots for different scenarios
        slots = []
        
        # Case 1: Standard slots without transport
        standard_date = datetime.now() + timedelta(days=1)
        slots.append({
            "id": "standard_morning",
            "start_time": standard_date.replace(hour=9, minute=0, second=0).isoformat(),
            "end_time": standard_date.replace(hour=9, minute=45, second=0).isoformat(),
            "location_id": "loc_1",
            "has_transport": False,
            "provider_name": "Dr. Smith"
        })
        
        # Case 2: Transport-enabled slots
        # Check date range overlap
        date_range_contains_transport = (
            transport_date.date() >= start_date.date() and 
            transport_date.date() <= end_date.date()
        )
        
        # Add transport slot if either we're not filtering by transport yet or if we are and it's in range
        if not include_transport or (include_transport and date_range_contains_transport):
            transport_slot_time = transport_date.replace(hour=14, minute=0, second=0)
            slots.append({
                "id": "transport_afternoon",
                "start_time": transport_slot_time.isoformat(),
                "end_time": (transport_slot_time + timedelta(minutes=45)).isoformat(),
                "location_id": "loc_2",
                "has_transport": True,
                "provider_name": "Dr. Johnson"
            })
        
        # Filter by transport if needed
        if include_transport:
            slots = [slot for slot in slots if slot.get("has_transport", True)]
            
        return slots
    
    # Replace the actual method with our mock
    mcp_connector.fetch_time_slots = mock_fetch_time_slots
    
    # Begin the demonstration
    print("\nIn this demonstration, we'll simulate a conversation with the Appoint-a-Bot system.")
    print("The system will suggest appointments and respond to customer preferences.")
    print("\n=== Starting Conversation ===")
    
    # Start the conversation
    response = agent.start_conversation()
    print(f"Agent: {response['message']}")
    
    # Scenario 1: Customer rejects the initial recommendation
    print("\nCustomer: I need a different time.")
    customer_response = {"type": "reject"}
    response = agent.handle_response(customer_response)
    print(f"Agent: {response['message']}")
    
    # Scenario 2: Customer provides date range that includes transport options
    print(f"\nCustomer: I'm looking for dates around {transport_formatted}.")
    customer_response = {
        "type": "date_range",
        "start_date": transport_date - timedelta(days=1),
        "end_date": transport_date + timedelta(days=1)
    }
    response = agent.handle_response(customer_response)
    print(f"Agent: {response['message']}")
    
    # Scenario 3: Customer requests transport
    print("\nCustomer: Yes, I'll need transport.")
    customer_response = {"type": "transport_preference", "transport_required": True}
    response = agent.handle_response(customer_response)
    
    # Display the response based on whether transport is available
    print(f"Agent: {response['message']}")
    
    if response["status"] == "recommendation":
        # Transport appointment found - accept it
        print("\nCustomer: That works perfectly. I'll take that appointment.")
        customer_response = {"type": "accept"}
        response = agent.handle_response(customer_response)
        print(f"Agent: {response['message']}")
        
        # Display appointment details
        if response["status"] == "confirmation" and "slot" in response:
            slot = response["slot"]
            slot_time = datetime.fromisoformat(slot['start_time'])
            end_time = datetime.fromisoformat(slot['end_time'])
            
            print("\n=== Booking Complete ===")
            print("\nAppointment Details:")
            print(f"Date: {slot_time.strftime('%A, %B %d, %Y')}")
            print(f"Time: {slot_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}")
            print(f"Provider: {slot['provider_name']}")
            print(f"Location ID: {slot['location_id']}")
            print(f"Transport Included: {'Yes' if slot.get('has_transport', False) else 'No'}")
            
    else:
        # No transport appointments found - try without transport
        print("\nCustomer: I can manage without transport. Let's look at all available appointments.")
        customer_response = {"type": "transport_preference", "transport_required": False}
        response = agent.handle_response(customer_response)
        print(f"Agent: {response['message']}")
        
        # Accept whatever is available
        print("\nCustomer: I'll take that appointment.")
        customer_response = {"type": "accept"}
        response = agent.handle_response(customer_response)
        print(f"Agent: {response['message']}")
        
        # Display appointment details
        if response["status"] == "confirmation" and "slot" in response:
            slot = response["slot"]
            slot_time = datetime.fromisoformat(slot['start_time'])
            end_time = datetime.fromisoformat(slot['end_time'])
            
            print("\n=== Booking Complete ===")
            print("\nAppointment Details:")
            print(f"Date: {slot_time.strftime('%A, %B %d, %Y')}")
            print(f"Time: {slot_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}")
            print(f"Provider: {slot['provider_name']}")
            print(f"Location ID: {slot['location_id']}")
            print(f"Transport Included: {'Yes' if slot.get('has_transport', False) else 'No'}")

if __name__ == "__main__":
    run_demo() 