#!/bin/bash
# High Severity DTC API Example
# This script demonstrates how a high-severity DTC triggers automatic booking without interactive session

# API URL - change this to match your setup
API_URL="http://localhost:8080"

# Colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Appoint-a-Bot - High Severity DTC Example ===${NC}\n"

# Send a high-severity DTC (C1A96 - Critical brake pad thickness)
echo -e "${GREEN}Sending a C1A96 DTC (HIGH severity - Brake Pad Thickness Critical)${NC}"
echo -e "${YELLOW}This should trigger automatic booking with transport${NC}\n"

DTC_RESPONSE=$(curl -s -X POST $API_URL/api/dtc \
  -H "Content-Type: application/json" \
  -d '{
    "dtc_code": "C1A96",
    "vehicle_id": "VIN-BRAKE-TEST",
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

# Check if we got an automatic booking
BOOKING_STATUS=$(echo "$DTC_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('status', ''))")

if [[ "$BOOKING_STATUS" == "booked" ]]; then
  echo -e "${GREEN}SUCCESS: DTC was automatically booked as expected for a high-severity code${NC}"
  
  # Extract and display booking details
  BOOKING_ID=$(echo "$DTC_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('booking', {}).get('booking_id', 'Unknown'))")
  DTC_CODE=$(echo "$DTC_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('dtc_info', {}).get('dtc_code', 'Unknown'))")
  DTC_DESC=$(echo "$DTC_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('dtc_info', {}).get('description', 'Unknown'))")
  TRANSPORT=$(echo "$DTC_RESPONSE" | python -c "import sys, json; print('Yes' if json.load(sys.stdin).get('booking', {}).get('slot', {}).get('transport_included', False) else 'No')")
  
  echo -e "${BLUE}Booking Details:${NC}"
  echo -e "Booking ID: $BOOKING_ID"
  echo -e "DTC: $DTC_CODE - $DTC_DESC"
  echo -e "Transport included: $TRANSPORT"
  echo -e "This urgent appointment was booked automatically without user interaction"
else
  echo -e "${RED}ERROR: High-severity DTC did not trigger automatic booking${NC}"
  echo -e "Expected 'booked' status but got '$BOOKING_STATUS'"
fi

echo
echo -e "${GREEN}Checking all DTC bookings:${NC}\n"
curl -s -X GET $API_URL/api/dtc/bookings | python -m json.tool

echo -e "\n${BLUE}=== End of Demonstration ===${NC}" 