#!/bin/bash
# Interactive DTC API Examples
# This script demonstrates how to interact with the Appoint-a-Bot DTC API
# to send DTCs with location data and handle interactive booking sessions.

# API URL - change this to match your setup
API_URL="http://localhost:8080"

# Colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Appoint-a-Bot - Interactive DTC API Examples ===${NC}\n"

# 1. Send a medium-severity DTC with location to create an interactive session
echo -e "${GREEN}1. Sending a P0100 DTC (medium severity) with location data${NC}"
echo -e "${YELLOW}This should trigger an interactive booking session${NC}\n"

DTC_RESPONSE=$(curl -s -X POST $API_URL/api/dtc \
  -H "Content-Type: application/json" \
  -d '{
    "dtc_code": "P0100",
    "vehicle_id": "VIN-12345",
    "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
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
      "customer_id": "CUST123",
      "vehicle_make": "Toyota",
      "vehicle_model": "Camry",
      "vehicle_year": 2020
    }
  }')

echo "$DTC_RESPONSE" | python -m json.tool
echo

# Extract session ID from response - fixing the extraction
SESSION_ID=$(echo "$DTC_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('session_id', ''))")

if [[ -z "$SESSION_ID" ]]; then
  echo -e "${RED}Error: No session ID returned. DTC may have been auto-booked due to high severity.${NC}"
  exit 1
fi

echo -e "${GREEN}Created interactive session with ID: ${YELLOW}$SESSION_ID${NC}\n"
sleep 2

# 2. Get session info
echo -e "${GREEN}2. Getting session information${NC}\n"

curl -s -X GET $API_URL/api/dtc/session/$SESSION_ID | python -m json.tool
echo
sleep 2

# 3. Start the conversation
echo -e "${GREEN}3. Starting the conversation with the agent${NC}\n"

CONVERSATION_START=$(curl -s -X POST $API_URL/api/dtc/session/$SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{"response": {"type": "start"}}')

echo "$CONVERSATION_START" | python -m json.tool
echo

# Extract agent message using Python for more reliable parsing
AGENT_MSG=$(echo "$CONVERSATION_START" | python -c "import sys, json; data = json.load(sys.stdin); print(data.get('agent_response', {}).get('message', 'No message available'))")
echo -e "${BLUE}Agent: ${NC}$AGENT_MSG"
echo
sleep 2

# 4. Reject the initial recommendation
echo -e "${GREEN}4. Rejecting the initial recommendation${NC}"
echo -e "${YELLOW}Customer: I'd like to see other options${NC}\n"

REJECT_RESPONSE=$(curl -s -X POST $API_URL/api/dtc/session/$SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{"response": {"type": "reject"}}')

echo "$REJECT_RESPONSE" | python -m json.tool
echo

# Use Python for more reliable parsing
AGENT_MSG=$(echo "$REJECT_RESPONSE" | python -c "import sys, json; data = json.load(sys.stdin); print(data.get('agent_response', {}).get('message', 'No message available'))")
echo -e "${BLUE}Agent: ${NC}$AGENT_MSG"
echo
sleep 2

# 5. Provide date range
NEXT_WEEK_START=$(date -v+7d +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -d "+7 days" +"%Y-%m-%dT%H:%M:%SZ")
NEXT_WEEK_END=$(date -v+12d +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -d "+12 days" +"%Y-%m-%dT%H:%M:%SZ")

NEXT_WEEK_START_READABLE=$(date -v+7d +"%A, %B %d" 2>/dev/null || date -d "+7 days" +"%A, %B %d")
NEXT_WEEK_END_READABLE=$(date -v+12d +"%A, %B %d" 2>/dev/null || date -d "+12 days" +"%A, %B %d")

echo -e "${GREEN}5. Providing a date range${NC}"
echo -e "${YELLOW}Customer: I'd prefer next week, from $NEXT_WEEK_START_READABLE to $NEXT_WEEK_END_READABLE${NC}\n"

DATE_RESPONSE=$(curl -s -X POST $API_URL/api/dtc/session/$SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{
    "response": {
      "type": "date_range",
      "start_date": "'$NEXT_WEEK_START'",
      "end_date": "'$NEXT_WEEK_END'"
    }
  }')

echo "$DATE_RESPONSE" | python -m json.tool
echo

# Use Python for more reliable parsing
AGENT_MSG=$(echo "$DATE_RESPONSE" | python -c "import sys, json; data = json.load(sys.stdin); print(data.get('agent_response', {}).get('message', 'No message available'))")
echo -e "${BLUE}Agent: ${NC}$AGENT_MSG"
echo
sleep 2

# 6. Provide transport preference
echo -e "${GREEN}6. Answering transport question${NC}"
echo -e "${YELLOW}Customer: Yes, I'll need transport${NC}\n"

TRANSPORT_RESPONSE=$(curl -s -X POST $API_URL/api/dtc/session/$SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{
    "response": {
      "type": "transport_preference",
      "transport_required": true
    }
  }')

echo "$TRANSPORT_RESPONSE" | python -m json.tool
echo

# Use Python for more reliable parsing
AGENT_MSG=$(echo "$TRANSPORT_RESPONSE" | python -c "import sys, json; data = json.load(sys.stdin); print(data.get('agent_response', {}).get('message', 'No message available'))")
echo -e "${BLUE}Agent: ${NC}$AGENT_MSG"
echo
sleep 2

# 7. Accept the appointment
echo -e "${GREEN}7. Accepting the appointment${NC}"
echo -e "${YELLOW}Customer: That works for me, let's book it${NC}\n"

ACCEPT_RESPONSE=$(curl -s -X POST $API_URL/api/dtc/session/$SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{"response": {"type": "accept"}}')

echo "$ACCEPT_RESPONSE" | python -m json.tool
echo

# Use Python for more reliable parsing
AGENT_MSG=$(echo "$ACCEPT_RESPONSE" | python -c "import sys, json; data = json.load(sys.stdin); print(data.get('agent_response', {}).get('message', 'No message available'))")
echo -e "${BLUE}Agent: ${NC}$AGENT_MSG"
echo -e "${GREEN}=== BOOKING CONFIRMED ===${NC}"
echo

# 8. Check all bookings
echo -e "${GREEN}8. Checking all DTC bookings${NC}\n"

curl -s -X GET $API_URL/api/dtc/bookings | python -m json.tool
echo

echo -e "${BLUE}=== End of Demonstration ===${NC}\n"
echo -e "Run this script again to create a new booking session, or modify the DTC code to try different scenarios."
echo -e "For high-severity DTCs (like C0045 or C1A96), the booking will be automatic with no interactive session." 