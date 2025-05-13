from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
import json

from src.appoint_a_bot.connector.mcp_connector import MCPConnector
from src.appoint_a_bot.analyzer.analyzer import Analyzer

class Agent:
    """
    Agent that manages customer interaction and coordinates between the MCP Connector and Analyzer.
    """
    
    def __init__(self, mcp_connector: MCPConnector, analyzer: Analyzer):
        """
        Initialize the Agent with required components.
        
        Args:
            mcp_connector: Instance of MCPConnector for fetching time slots
            analyzer: Instance of Analyzer for processing time slots
        """
        self.mcp_connector = mcp_connector
        self.analyzer = analyzer
        self.customer_preferences = {}
        self.current_recommendation = None
        self.conversation_state = "initial"  # Track the state of the conversation
        
    def start_conversation(self) -> Dict[str, Any]:
        """
        Start a new conversation with the customer.
        
        Returns:
            Initial response to present to the customer
        """
        # Default date range (e.g., next 7 days)
        start_date = datetime.now()
        end_date = start_date + timedelta(days=7)
        
        # Store initial preferences
        self.customer_preferences = {
            "start_date": start_date,
            "end_date": end_date,
            "transport_required": False,
            "location_id": None
        }
        
        # Fetch initial time slots
        slots = self.mcp_connector.fetch_time_slots(
            start_date=start_date,
            end_date=end_date,
            include_transport=False
        )
        
        if not slots:
            self.conversation_state = "no_slots"
            return {
                "status": "no_slots",
                "message": "No available time slots found. Would you like to try different dates?",
                "require_input": True,
                "input_type": "date_range"
            }
        
        # Find the closest time slot
        closest_slot = self.analyzer.find_closest_time_slot(slots)[0] if slots else None
        self.current_recommendation = closest_slot
        self.conversation_state = "initial_recommendation"
        
        if closest_slot:
            slot_time = datetime.fromisoformat(closest_slot.get("start_time"))
            formatted_time = slot_time.strftime("%A, %B %d at %I:%M %p")
            
            return {
                "status": "recommendation",
                "message": f"I found an available appointment on {formatted_time}. Would you like to book this appointment?",
                "slot": closest_slot,
                "require_input": True,
                "input_type": "yes_no"
            }
        else:
            self.conversation_state = "no_slots"
            return {
                "status": "error",
                "message": "Sorry, I couldn't find any suitable time slots. Would you like to try different dates?",
                "require_input": True,
                "input_type": "date_range"
            }
    
    def handle_response(self, customer_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the customer's response and take appropriate actions.
        
        Args:
            customer_response: Dictionary containing the customer's response
            
        Returns:
            Next response to present to the customer
        """
        response_type = customer_response.get("type")
        
        if response_type == "start":
            # Special case for starting the conversation
            # No action needed, just return the current recommendation
            if self.current_recommendation:
                slot_time = datetime.fromisoformat(self.current_recommendation.get("start_time"))
                formatted_time = slot_time.strftime("%A, %B %d at %I:%M %p")
                
                return {
                    "status": "recommendation",
                    "message": f"I found an available appointment on {formatted_time}. Would you like to book this appointment?",
                    "slot": self.current_recommendation,
                    "require_input": True,
                    "input_type": "yes_no"
                }
            else:
                # If no recommendation yet, just ask for preferences
                self.conversation_state = "awaiting_date_range"
                return {
                    "status": "date_request",
                    "message": "What date range would you prefer for your appointment?",
                    "require_input": True,
                    "input_type": "date_range"
                }
        
        elif response_type == "accept":
            # Customer accepted the recommendation
            return self._handle_booking_confirmation()
            
        elif response_type == "reject":
            # Customer rejected, ask for date range
            self.conversation_state = "awaiting_date_range"
            return {
                "status": "date_request",
                "message": "What date range would you prefer? (e.g., 'next week', 'June 15-20')",
                "require_input": True,
                "input_type": "date_range"
            }
            
        elif response_type == "date_range":
            # Customer provided a date range
            start_date = customer_response.get("start_date")
            end_date = customer_response.get("end_date")
            
            # Convert string dates to datetime if needed
            if isinstance(start_date, str):
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                
            if isinstance(end_date, str):
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
            # Update preferences
            self.customer_preferences["start_date"] = start_date
            self.customer_preferences["end_date"] = end_date
            self.conversation_state = "awaiting_transport_preference"
            
            # Ask about transport
            return {
                "status": "transport_request",
                "message": "Do you need transport options for your appointment?",
                "require_input": True,
                "input_type": "yes_no"
            }
            
        elif response_type == "transport_preference":
            # Customer provided transport preference
            transport_required = customer_response.get("transport_required", False)
            self.customer_preferences["transport_required"] = transport_required
            self.conversation_state = "awaiting_recommendation"
            
            # Fetch new recommendations based on updated preferences
            return self._get_updated_recommendations()
            
        else:
            # If we're in the no_slots state and get an unknown response,
            # interpret it as wanting to try different dates
            if self.conversation_state == "no_slots" and self.current_recommendation:
                return {
                    "status": "recommendation",
                    "message": f"I found an earlier appointment. Would you like to book it?",
                    "slot": self.current_recommendation,
                    "require_input": True,
                    "input_type": "yes_no"
                }
            else:
                # Unknown response type
                return {
                    "status": "error",
                    "message": "I didn't understand your response. Would you like to book the recommended appointment?",
                    "require_input": True,
                    "input_type": "yes_no"
                }
    
    def _handle_booking_confirmation(self) -> Dict[str, Any]:
        """
        Handle the booking confirmation process.
        
        Returns:
            Confirmation response
        """
        try:
            if not self.current_recommendation:
                self.conversation_state = "error"
                return {
                    "status": "error",
                    "message": "No appointment was selected. Let's start over.",
                    "require_input": False
                }
                
            slot_time_str = self.current_recommendation.get("start_time")
            slot_time = datetime.fromisoformat(slot_time_str.replace('Z', '+00:00') if isinstance(slot_time_str, str) else slot_time_str)
            formatted_time = slot_time.strftime("%A, %B %d at %I:%M %p")
            
            # In a real system, this would make an API call to book the appointment
            self.conversation_state = "completed"
            
            return {
                "status": "confirmation",
                "message": f"Great! Your appointment is confirmed for {formatted_time}.",
                "slot": self.current_recommendation,
                "require_input": False
            }
        except Exception as e:
            import traceback
            print(f"DEBUG ERROR in booking confirmation: {str(e)}")
            print(traceback.format_exc())
            self.conversation_state = "error"
            return {
                "status": "error",
                "message": f"Sorry, I encountered an error while confirming your booking: {str(e)}.",
                "require_input": False
            }
    
    def _get_updated_recommendations(self) -> Dict[str, Any]:
        """
        Get updated recommendations based on customer preferences.
        
        Returns:
            Updated recommendation response
        """
        try:
            # Ensure start_date and end_date are datetime objects
            start_date = self.customer_preferences["start_date"]
            end_date = self.customer_preferences["end_date"]
            
            print(f"DEBUG: start_date type={type(start_date)}, value={start_date}")
            print(f"DEBUG: end_date type={type(end_date)}, value={end_date}")
            
            # Convert string dates to datetime if needed
            if isinstance(start_date, str):
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                self.customer_preferences["start_date"] = start_date
                
            if isinstance(end_date, str):
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                self.customer_preferences["end_date"] = end_date
            
            # Fetch time slots with updated preferences
            slots = self.mcp_connector.fetch_time_slots(
                start_date=start_date,
                end_date=end_date,
                location_id=self.customer_preferences["location_id"],
                include_transport=self.customer_preferences["transport_required"]
            )
            
            # Filter slots based on criteria
            filtered_slots = self.analyzer.filter_slots_by_criteria(slots, self.customer_preferences)
            
            if not filtered_slots:
                self.conversation_state = "no_slots"
                return {
                    "status": "no_slots",
                    "message": "I couldn't find any appointments matching your preferences. Would you like to try different dates?",
                    "require_input": True,
                    "input_type": "date_range"
                }
            
            # Find the closest time slot
            closest_slot = self.analyzer.find_closest_time_slot(filtered_slots)[0]
            self.current_recommendation = closest_slot
            self.conversation_state = "recommendation"
            
            print(f"DEBUG: closest_slot={closest_slot}")
            
            slot_time_str = closest_slot.get("start_time")
            print(f"DEBUG: slot_time_str type={type(slot_time_str)}, value={slot_time_str}")
            
            slot_time = datetime.fromisoformat(slot_time_str.replace('Z', '+00:00') if isinstance(slot_time_str, str) else slot_time_str)
            formatted_time = slot_time.strftime("%A, %B %d at %I:%M %p")
            
            transport_msg = " with transport included" if self.customer_preferences["transport_required"] else ""
            
            return {
                "status": "recommendation",
                "message": f"I found an available appointment on {formatted_time}{transport_msg}. Would you like to book this appointment?",
                "slot": closest_slot,
                "require_input": True,
                "input_type": "yes_no"
            }
        except Exception as e:
            import traceback
            print(f"DEBUG ERROR: {str(e)}")
            print(traceback.format_exc())
            self.conversation_state = "error"
            return {
                "status": "error",
                "message": f"Sorry, I encountered an error: {str(e)}. Would you like to try different dates?",
                "require_input": True,
                "input_type": "date_range"
            }

# Example usage
if __name__ == "__main__":
    # Set up the components
    connector = MCPConnector(api_url="https://example-mcp-api.com/slots", api_key="your_api_key")
    analyzer = Analyzer()
    agent = Agent(mcp_connector=connector, analyzer=analyzer)
    
    # Simulate a conversation
    print("Starting conversation...")
    response = agent.start_conversation()
    print(f"Agent: {response['message']}")
    
    # Simulate customer rejecting the initial recommendation
    customer_response = {"type": "reject"}
    response = agent.handle_response(customer_response)
    print(f"Agent: {response['message']}")
    
    # Simulate customer providing a date range
    customer_response = {
        "type": "date_range",
        "start_date": datetime.now() + timedelta(days=10),
        "end_date": datetime.now() + timedelta(days=15)
    }
    response = agent.handle_response(customer_response)
    print(f"Agent: {response['message']}")
    
    # Simulate customer requesting transport
    customer_response = {"type": "transport_preference", "transport_required": True}
    response = agent.handle_response(customer_response)
    print(f"Agent: {response['message']}")
    
    # Simulate customer accepting the recommendation
    customer_response = {"type": "accept"}
    response = agent.handle_response(customer_response)
    print(f"Agent: {response['message']}") 