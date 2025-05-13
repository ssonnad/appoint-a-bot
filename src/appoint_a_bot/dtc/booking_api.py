"""
REST API for the Booking Service.
Provides endpoints for handling appointment bookings.
"""
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from datetime import datetime
import logging
from typing import Dict, Any, Optional, List

from src.appoint_a_bot.dtc.booking import booking_service
from src.appoint_a_bot.dtc.dtc_processor import DTCProcessor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
api = Api(app)

# Create DTC processor instance
dtc_processor = DTCProcessor()

class BookingResource(Resource):
    """Resource for handling bookings via REST API"""
    
    def post(self):
        """
        Create a new booking.
        
        Expected payload:
        {
            "slot_id": "slot-202305151000-loc1",
            "customer_info": {
                "vehicle_id": "VIN12345",
                "customer_id": "CUST123",
                "vehicle_make": "Toyota",
                "vehicle_model": "Camry",
                "vehicle_year": 2020,
                "mileage": 35000
            }
        }
        """
        try:
            booking_data = request.json
            
            if not booking_data:
                return {"error": "No data provided"}, 400
                
            # Extract slot ID and find available slots
            slot_id = booking_data.get("slot_id")
            if not slot_id:
                return {"error": "No slot_id provided"}, 400
                
            customer_info = booking_data.get("customer_info", {})
            if not customer_info or not customer_info.get("vehicle_id"):
                return {"error": "Customer information is required"}, 400
                
            # Find available slots for the next 30 days
            start_date = datetime.now()
            end_date = start_date.replace(hour=23, minute=59, second=59) + datetime.timedelta(days=30)
            
            available_slots = booking_service.find_available_slots(start_date, end_date)
            
            # Find the requested slot
            selected_slot = None
            for slot in available_slots:
                if slot["id"] == slot_id:
                    selected_slot = slot
                    break
                    
            if not selected_slot:
                return {"error": f"Slot {slot_id} not found or not available"}, 404
                
            # Create the booking
            booking = booking_service.create_booking(
                slot=selected_slot,
                customer_info=customer_info
            )
            
            return {
                "status": "booked",
                "message": "Appointment successfully booked",
                "booking": booking
            }, 201
            
        except Exception as e:
            logger.error(f"Error creating booking: {str(e)}")
            return {"error": str(e)}, 500
    
    def get(self, booking_id=None):
        """
        Get booking information.
        If booking_id is provided, get that specific booking.
        Otherwise, get all bookings.
        """
        try:
            if booking_id:
                booking = booking_service.get_booking(booking_id)
                if booking:
                    return {"booking": booking}, 200
                else:
                    return {"error": f"Booking {booking_id} not found"}, 404
            else:
                bookings = booking_service.get_all_bookings()
                return {"bookings": bookings}, 200
                
        except Exception as e:
            logger.error(f"Error retrieving booking(s): {str(e)}")
            return {"error": str(e)}, 500

class SlotsResource(Resource):
    """Resource for handling available slots"""
    
    def get(self):
        """
        Get available slots for a date range.
        
        Query parameters:
        - start_date: ISO format start date (defaults to today)
        - end_date: ISO format end date (defaults to 7 days from now)
        - location_id: Optional location ID
        - include_transport: Whether to include transport options (true/false)
        """
        try:
            # Get query parameters
            start_date_str = request.args.get("start_date")
            end_date_str = request.args.get("end_date")
            location_id = request.args.get("location_id")
            include_transport = request.args.get("include_transport", "false").lower() == "true"
            
            # Parse dates or use defaults
            try:
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00')) if start_date_str else datetime.now()
            except (ValueError, AttributeError):
                start_date = datetime.now()
                
            try:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00')) if end_date_str else (start_date + datetime.timedelta(days=7))
            except (ValueError, AttributeError):
                end_date = start_date + datetime.timedelta(days=7)
            
            # Find available slots
            slots = booking_service.find_available_slots(
                start_date=start_date,
                end_date=end_date,
                location_id=location_id,
                include_transport=include_transport
            )
            
            return {"slots": slots}, 200
            
        except Exception as e:
            logger.error(f"Error retrieving slots: {str(e)}")
            return {"error": str(e)}, 500

class DTCBookingResource(Resource):
    """Resource for handling DTC-triggered bookings"""
    
    def post(self):
        """
        Process DTC data and create a booking.
        
        Expected payload:
        {
            "dtc_code": "P0001",
            "vehicle_id": "VIN12345",
            "timestamp": "2023-06-01T12:00:00Z",
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
                
            # Extract appointment preferences
            appointment_prefs = processed_data.get("appointment_preferences", {})
            
            # Create a booking based on the DTC data
            booking_result = booking_service.create_dtc_booking(
                dtc_data=dtc_data,
                appointment_preferences=appointment_prefs
            )
            
            if booking_result.get("status") == "error":
                return booking_result, 404
                
            # Return both DTC info and booking confirmation
            result = {
                "status": "booked",
                "message": f"Appointment automatically booked based on DTC {processed_data['dtc_code']}",
                "dtc_info": processed_data,
                "booking": booking_result.get("booking")
            }
            
            logger.info(f"Automatically booked appointment for DTC {processed_data['dtc_code']} - Vehicle: {dtc_data.get('vehicle_id')}")
            return result, 201
            
        except Exception as e:
            logger.error(f"Error processing DTC booking: {str(e)}")
            return {"error": str(e)}, 500

# Add resources to API
api.add_resource(BookingResource, '/api/bookings', '/api/bookings/<string:booking_id>')
api.add_resource(SlotsResource, '/api/slots')
api.add_resource(DTCBookingResource, '/api/dtc-booking')

# Add a health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "booking_service": "running",
        "bookings_count": len(booking_service.get_all_bookings())
    })

def start_api(host='0.0.0.0', port=8080, debug=False):
    """Start the Flask API server"""
    logger.info(f"Starting Booking API server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    start_api(debug=True) 