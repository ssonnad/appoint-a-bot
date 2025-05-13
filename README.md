# Appoint-a-Bot

Appoint-a-Bot is an appointment scheduling system with REST API capabilities to handle vehicle Diagnostic Trouble Codes (DTCs) and automate service scheduling.

## Overview

The system processes vehicle DTCs, determines service urgency based on severity, and uses smart appointment scheduling to book the most suitable time slots.

The appointment booking system has the following components:

1. **DTC Processor**: Analyzes diagnostic trouble codes and assesses urgency
2. **MCP Connector**: Fetches available time slots from service centers
3. **Analyzer**: Processes and filters available slots based on criteria
4. **Agent**: Manages customer interaction and booking workflows

## New Feature: Interactive Booking with Location Data

The system now supports interactive booking sessions based on DTC severity:

- High-severity DTCs (like brake issues - C0045, C1A96) are automatically booked with transport options
- Medium/low-severity DTCs trigger interactive booking sessions where customers can:
  - Select preferred date ranges
  - Choose location preferences
  - Choose transport options
  - Confirm or reject recommendations

The system now also accepts customer location data with DTCs, including:
- Coordinates (latitude/longitude)
- Address information
- Preferred service location
- Maximum distance willing to travel

## API Endpoints

### DTC API
- `POST /api/dtc`: Send DTC data with location information
- `GET /api/dtc/bookings`: Get all DTC-triggered bookings

### Interactive Session API
- `GET /api/dtc/session/<session_id>`: Get the current state of an interactive session
- `POST /api/dtc/session/<session_id>`: Continue the interactive booking conversation

## Running the Application

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/appoint-a-bot.git
cd appoint-a-bot

# Install dependencies
pip install -e .
```

### Running Demos

Several demo scripts are available to demonstrate the system's functionality:

```bash
# Run the interactive DTC demo with location data
python -m src.appoint_a_bot.main interactive-dtc-demo

# Run the DTC API demo
python -m src.appoint_a_bot.main dtc-demo

# Run the booking API demo
python -m src.appoint_a_bot.main booking-demo

# Start the DTC API server
python -m src.appoint_a_bot.main start-api
```

### Example: Using the API with cURL

Send a DTC with location data:

```bash
curl -X POST http://localhost:8080/api/dtc \
  -H "Content-Type: application/json" \
  -d '{
    "dtc_code": "P0100",
    "vehicle_id": "VIN-12345",
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
      "preferred_location_id": "SERVICE_LOC_1",
      "distance_willing_to_travel": 25
    },
    "additional_info": {
      "mileage": 35000,
      "customer_id": "CUST123"
    }
  }'
```

For medium/low severity DTCs, you'll get a session ID for interactive booking:

```bash
# Example response (truncated)
{
  "status": "interactive_session_created",
  "session_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "next_step": "Start the conversation with the agent using the session ID"
}
```

For a complete example with interactive booking, see the `examples/interactive_dtc_api_examples.sh` script.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## System Architecture

### 1. MCP Connector

The MCP Connector is responsible for retrieving available time slots from an external service.

- Fetches time slots via an external URL
- Handles API authentication and communication
- Returns structured time slot data for further processing

### 2. Analyzer

The Analyzer processes the time slots retrieved by the MCP Connector.

- Analyzes available time slots based on various parameters
- Identifies the closest/most suitable time slot to the customer's needs
- Optimizes recommendations based on time proximity and availability
- Returns the best match time slot to the Agent

### 3. Agent

The Agent manages customer interaction and serves as the interface between the system and the customer.

- Presents the recommended time slot to the customer
- Handles customer responses:
  - If customer accepts the time slot, proceeds with booking
  - If customer declines, collects preferred date range
  - Asks if transport options are required
- Communicates with the Analyzer to fetch refined recommendations based on customer feedback
- Manages the complete appointment booking workflow

### 4. DTC Module & REST API

The DTC (Diagnostic Trouble Code) module processes vehicle diagnostic codes and automatically books appointments.

- Receives DTCs from external vehicle systems via a REST API
- Analyzes code severity to determine appointment urgency
- Uses the existing system components to find and book appropriate time slots
- Returns booking confirmation with relevant details
- Exposes endpoints for accessing DTC-triggered bookings

## Project Structure

```
src/
├── appoint_a_bot/
│   ├── connector/        # MCP Connector component
│   │   └── mcp_connector.py
│   ├── analyzer/         # Analyzer component
│   │   └── analyzer.py
│   ├── agent/            # Agent component
│   │   └── agent.py
│   ├── dtc/              # DTC handling and REST API
│   │   ├── __init__.py
│   │   ├── dtc_processor.py
│   │   └── api.py
│   ├── demo/             # Demo scripts
│   │   ├── demo_conversation.py
│   │   ├── final_demo.py
│   │   └── dtc_demo.py
│   └── main.py           # Main entry point
└── ...
```

## Installation

1. Create a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install the package:
   ```
   pip install -e .
   ```

## Usage

You can run the demos using the following commands:

```
# Run the interactive demo
python -m src.appoint_a_bot.main demo

# Run the complete demonstration with both scenarios
python -m src.appoint_a_bot.main final-demo

# Run the DTC API demo 
python -m src.appoint_a_bot.main dtc-demo

# Start the DTC REST API server
python -m src.appoint_a_bot.main start-api [--host HOST] [--port PORT] [--debug]
```

## Usage Flow

1. The MCP Connector fetches available time slots from the external system
2. The Analyzer processes these slots to find the optimal recommendation
3. The Agent presents this recommendation to the customer
4. Based on customer feedback, the Agent either completes the booking or refines the search parameters
5. If refinement is needed, the process loops back to step 1 with new parameters

## DTC API Endpoints

The REST API includes the following endpoints:

- `POST /api/dtc`: Submit a new DTC from a vehicle to trigger appointment booking
  ```json
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
  ```

- `GET /api/dtc/bookings`: Retrieve all DTC-triggered bookings
- `GET /health`: Check the API server status

## Development

To contribute to the project, follow these steps:

1. Clone the repository
2. Create and activate a virtual environment
3. Install in development mode: `pip install -e .`
4. Run the tests: `pytest` (requires pytest to be installed)
5. Make your changes and submit a pull request 

## Visual Diagrams
Install mermaid to visualize the architecture diagram
npx @mermaid-js/mermaid-cli -i docs/architecture.md -o architecture.png
