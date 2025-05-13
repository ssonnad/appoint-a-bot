#!/bin/bash
# This script stops any existing API server, starts a fresh one, and runs the C1A96 demo

# Colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Appoint-a-Bot - API Server and C1A96 Demo Runner ===${NC}\n"

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Kill any existing processes using port 8080
echo -e "${YELLOW}Stopping any existing API servers on port 8080...${NC}"
PID=$(lsof -ti:8080)
if [ ! -z "$PID" ]; then
  echo "Killing process $PID using port 8080"
  kill -9 $PID
  sleep 1
else
  echo "No process found using port 8080"
fi

# Start the API server
echo -e "\n${GREEN}Starting a fresh API server...${NC}"
# Run the API server in the background
python -m src.appoint_a_bot.main start-api > api_server.log 2>&1 &
API_SERVER_PID=$!
echo "API server started with PID: $API_SERVER_PID"

# Wait for the server to start
echo -e "${YELLOW}Waiting for API server to initialize...${NC}"
sleep 3

# Check if the server is running
echo -e "${GREEN}Checking API server status...${NC}"
if curl -s http://localhost:8080/health > /dev/null; then
  echo -e "${GREEN}API server is running!${NC}"
else
  echo -e "${RED}API server failed to start. Check api_server.log for details.${NC}"
  exit 1
fi

# Run the C1A96 demo
echo -e "\n${BLUE}Running the C1A96 brake pad DTC demo...${NC}"
python -m src.appoint_a_bot.main brake-pad-demo

# Print a message about the running server
echo -e "\n${YELLOW}The API server is still running with PID $API_SERVER_PID${NC}"
echo -e "To stop it, run: ${GREEN}kill -9 $API_SERVER_PID${NC}"
echo -e "Or to keep it running for more demos, leave it as is." 