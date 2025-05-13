"""
REST API for handling DTC (Diagnostic Trouble Code) data from vehicles.
This API receives DTC data and triggers the appointment booking process.
"""
from flask import Flask, request, jsonify, session
from flask_restful import Api, Resource
from datetime import datetime
import logging
import json
import uuid
from typing import Dict, Any, Optional, List, Tuple

from src.appoint_a_bot.dtc.dtc_processor import DTCProcessor
from src.appoint_a_bot.connector.mcp_connector import MCPConnector
from src.appoint_a_bot.analyzer.analyzer import Analyzer
from src.appoint_a_bot.agent.agent import Agent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'appoint-a-bot-secret-key'  # For session management
api = Api(app)

# Create instances of the core components
connector = MCPConnector(api_url="https://example-mcp-api.com/slots", api_key="your_api_key")
analyzer = Analyzer()
agent = Agent(mcp_connector=connector, analyzer=analyzer)
dtc_processor = DTCProcessor()

# Store completed bookings (in-memory, would be a database in production)
dtc_bookings = []

# Store interactive sessions (in-memory, would be a database in production)
interactive_sessions = {}

class DTCResource(Resource):
    """Resource for handling DTC data via REST API"""
    
    def post(self):
        """
        Receive DTC data from external sources and trigger appointment booking.
        
        Expected payload:
        {
            "dtc_code": "P0001",
            "vehicle_id": "VIN12345",
            "timestamp": "2023-06-01T12:00:00Z",
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
                "preferred_location_id": "LOC123",
                "distance_willing_to_travel": 30
            },
            "additional_info": {
                "mileage": 35000,
                "customer_id": "CUST123",
                "vehicle_make": "Toyota",
                "vehicle_model": "Camry",
                "vehicle_year": 2020
            }
        }
        """
        try:
            dtc_data = request.json
            
            if not dtc_data:
                return {"error": "No data provided"}, 400
                
            logger.info(f"Received DTC data: {dtc_data}")
            
            # Process the DTC data
            processed_data = dtc_processor.process_dtc(dtc_data)
            
            if processed_data.get("status") == "error":
                return processed_data, 400
                
            # Extract appointment preferences from processed data
            appointment_prefs = processed_data.get("appointment_preferences", {})
            
            # Check if this should be an interactive booking
            if appointment_prefs.get("interactive_booking", False):
                # Create an interactive session
                session_id = str(uuid.uuid4())
                
                # Convert ISO format strings back to datetime objects
                start_date = datetime.fromisoformat(appointment_prefs.get("start_date").replace('Z', '+00:00'))
                end_date = datetime.fromisoformat(appointment_prefs.get("end_date").replace('Z', '+00:00'))
                transport_required = appointment_prefs.get("transport_required", False)
                location_data = appointment_prefs.get("location", {})
                
                # Store session data
                interactive_sessions[session_id] = {
                    "dtc_data": dtc_data,
                    "processed_data": processed_data,
                    "customer_preferences": {
                        "start_date": start_date,
                        "end_date": end_date,
                        "transport_required": transport_required,
                        "location_id": location_data.get("customer_preferred_location_id"),
                        "vehicle_id": dtc_data.get("vehicle_id"),
                        "location": location_data
                    },
                    "agent_state": "initialized",
                    "last_response": None,
                    "created_at": datetime.now().isoformat()
                }
                
                # Return session information
                return {
                    "status": "interactive_session_created",
                    "message": "Interactive booking session created based on DTC data",
                    "session_id": session_id,
                    "dtc_info": processed_data,
                    "next_step": "Start the conversation with the agent using the session ID"
                }, 201
                
            else:
                # Auto-booking for high severity DTCs
                # Convert ISO format strings back to datetime objects
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
                
                # Fetch time slots based on the preferences
                slots = connector.fetch_time_slots(
                    start_date=start_date,
                    end_date=end_date,
                    location_id=location_data.get("customer_preferred_location_id"),
                    include_transport=transport_required
                )
                
                if not slots:
                    return {
                        "status": "no_slots",
                        "message": "No available time slots found for this DTC",
                        "dtc_info": processed_data
                    }, 404
                
                # Find the best time slot based on urgency
                filtered_slots = analyzer.filter_slots_by_criteria(slots, agent.customer_preferences)
                closest_slot = analyzer.find_closest_time_slot(filtered_slots)[0] if filtered_slots else None
                
                if not closest_slot:
                    return {
                        "status": "no_slots",
                        "message": "No suitable time slots found after filtering",
                        "dtc_info": processed_data
                    }, 404
                
                # Auto-confirm the booking for the best available slot
                agent.current_recommendation = closest_slot
                booking_confirmation = agent._handle_booking_confirmation()
                
                # Store the booking with DTC info
                booking_record = {
                    "booking_id": f"BOOK-{len(dtc_bookings) + 1}",
                    "slot": closest_slot,
                    "dtc_info": processed_data,
                    "vehicle_id": dtc_data.get("vehicle_id"),
                    "location": location_data,
                    "timestamp": datetime.now().isoformat(),
                    "customer_id": dtc_data.get("additional_info", {}).get("customer_id")
                }
                dtc_bookings.append(booking_record)
                
                # Return both DTC info and booking confirmation
                result = {
                    "status": "booked",
                    "message": f"Appointment automatically booked based on DTC {processed_data['dtc_code']}",
                    "dtc_info": processed_data,
                    "booking": booking_record,
                    "confirmation": booking_confirmation
                }
                
                logger.info(f"Automatically booked appointment for DTC {processed_data['dtc_code']} - Vehicle: {dtc_data.get('vehicle_id')}")
                return result, 201
            
        except Exception as e:
            logger.error(f"Error processing DTC data: {str(e)}")
            return {"error": str(e)}, 500

class InteractiveSessionResource(Resource):
    """Resource for managing interactive booking sessions"""
    
    def get(self, session_id):
        """
        Get the current state of an interactive session
        """
        if session_id not in interactive_sessions:
            return {"error": "Session not found"}, 404
            
        session_data = interactive_sessions[session_id]
        
        return {
            "session_id": session_id,
            "dtc_info": session_data["processed_data"],
            "agent_state": session_data["agent_state"],
            "last_response": session_data["last_response"],
            "created_at": session_data["created_at"]
        }, 200
    
    def post(self, session_id):
        """
        Continue an interactive booking session with customer responses
        
        Expected payload:
        {
            "response": {
                "type": "accept|reject|date_range|transport_preference",
                "start_date": "2023-06-01T00:00:00Z", # Optional, for date_range
                "end_date": "2023-06-07T00:00:00Z",   # Optional, for date_range
                "transport_required": true            # Optional, for transport_preference
            }
        }
        """
        if session_id not in interactive_sessions:
            return {"error": "Session not found"}, 404
            
        try:
            session_data = interactive_sessions[session_id]
            customer_response = request.json.get("response", {})
            
            if not customer_response:
                return {"error": "No response provided"}, 400
                
            # Initialize agent if this is the first interaction
            if session_data["agent_state"] == "initialized":
                # Set agent preferences based on session data
                agent.customer_preferences = session_data["customer_preferences"]
                
                # Start the conversation
                agent_response = agent.start_conversation()
                session_data["agent_state"] = "conversation_started"
                session_data["last_response"] = agent_response
                
                return {
                    "session_id": session_id,
                    "agent_response": agent_response,
                    "next_steps": "Respond with customer preferences"
                }, 200
            else:
                # Handle customer response
                agent_response = agent.handle_response(customer_response)
                session_data["last_response"] = agent_response
                
                # Check if booking is confirmed
                if agent_response.get("status") == "confirmation":
                    # Create a booking record
                    booking_record = {
                        "booking_id": f"BOOK-{len(dtc_bookings) + 1}",
                        "slot": agent.current_recommendation,
                        "dtc_info": session_data["processed_data"],
                        "vehicle_id": session_data["dtc_data"].get("vehicle_id"),
                        "location": session_data["customer_preferences"].get("location", {}),
                        "timestamp": datetime.now().isoformat(),
                        "customer_id": session_data["dtc_data"].get("additional_info", {}).get("customer_id"),
                        "session_id": session_id
                    }
                    dtc_bookings.append(booking_record)
                    session_data["agent_state"] = "booking_confirmed"
                    
                    return {
                        "session_id": session_id,
                        "agent_response": agent_response,
                        "booking": booking_record,
                        "status": "booking_confirmed"
                    }, 200
                else:
                    session_data["agent_state"] = "in_progress"
                    return {
                        "session_id": session_id,
                        "agent_response": agent_response,
                        "next_steps": "Continue the conversation"
                    }, 200
                    
        except Exception as e:
            logger.error(f"Error in interactive session: {str(e)}")
            return {"error": str(e)}, 500

class DTCBookingsResource(Resource):
    """Resource for retrieving DTC-triggered bookings"""
    
    def get(self):
        """Get all DTC-triggered bookings"""
        return {"bookings": dtc_bookings}, 200

# Add resources to API
api.add_resource(DTCResource, '/api/dtc')
api.add_resource(InteractiveSessionResource, '/api/dtc/session/<string:session_id>')
api.add_resource(DTCBookingsResource, '/api/dtc/bookings')

# Add a health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

def start_api(host='0.0.0.0', port=5000, debug=False):
    """Start the Flask API server"""
    logger.info(f"Starting DTC API server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    start_api(debug=True) 