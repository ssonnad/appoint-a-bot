# Appoint-a-Bot

An intelligent appointment scheduling system with three core components.

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
│   ├── demo/             # Demo scripts
│   │   ├── demo_conversation.py
│   │   └── final_demo.py
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
```

## Usage Flow

1. The MCP Connector fetches available time slots from the external system
2. The Analyzer processes these slots to find the optimal recommendation
3. The Agent presents this recommendation to the customer
4. Based on customer feedback, the Agent either completes the booking or refines the search parameters
5. If refinement is needed, the process loops back to step 1 with new parameters

## Development

To contribute to the project, follow these steps:

1. Clone the repository
2. Create and activate a virtual environment
3. Install in development mode: `pip install -e .`
4. Run the tests: `pytest` (requires pytest to be installed)
5. Make your changes and submit a pull request 