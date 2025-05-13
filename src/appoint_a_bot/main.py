#!/usr/bin/env python3
"""
Appoint-a-Bot - Main Entry Point

This script provides a simple command-line interface to run the different
demonstration scenarios and serves as the main entry point for the application.
"""

import sys
import argparse
from datetime import datetime, timedelta

from src.appoint_a_bot.connector.mcp_connector import MCPConnector
from src.appoint_a_bot.analyzer.analyzer import Analyzer
from src.appoint_a_bot.agent.agent import Agent
from src.appoint_a_bot.demo.demo_conversation import run_demo as run_conversation_demo
from src.appoint_a_bot.demo.final_demo import main as run_final_demo
from src.appoint_a_bot.demo.dtc_demo import run_demo as run_dtc_demo
from src.appoint_a_bot.demo.booking_demo import run_demo as run_booking_demo
from src.appoint_a_bot.demo.interactive_dtc_demo import run_demo as run_interactive_dtc_demo
from src.appoint_a_bot.demo.c1a96_demo import run_demo as run_brake_pad_demo
from src.appoint_a_bot.dtc.api import start_api as start_dtc_api
from src.appoint_a_bot.dtc.booking_api import start_api as start_booking_api

def print_usage():
    """Print usage information."""
    print("Appoint-a-Bot - Appointment Scheduling System")
    print("\nUsage:")
    print("  python -m src.appoint_a_bot.main [command]")
    print("\nCommands:")
    print("  demo       - Run the interactive demo")
    print("  final-demo - Run the complete final demo with both scenarios")
    print("  dtc-demo   - Run the DTC API demo")
    print("  booking-demo - Run the Booking API demo with mock data")
    print("  interactive-dtc-demo - Run the interactive DTC demo with location data")
    print("  brake-pad-demo - Run the C1A96 critical brake pad DTC demo")
    print("  start-api  - Start the DTC REST API server")
    print("  booking-api - Start the Booking REST API server (with mocked data)")
    print("  help       - Show this help message")

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Appoint-a-Bot - Appointment Scheduling System")
    parser.add_argument('command', nargs='?', default='help',
                        help='Command to run (demo, final-demo, dtc-demo, booking-demo, interactive-dtc-demo, brake-pad-demo, start-api, booking-api, help)')
    parser.add_argument('--host', default='0.0.0.0', help='Host for API server')
    parser.add_argument('--port', type=int, default=8080, help='Port for API server')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')

    args = parser.parse_args()

    if args.command == 'demo':
        run_conversation_demo()
    elif args.command == 'final-demo':
        run_final_demo()
    elif args.command == 'dtc-demo':
        run_dtc_demo()
    elif args.command == 'booking-demo':
        run_booking_demo()
    elif args.command == 'interactive-dtc-demo':
        run_interactive_dtc_demo()
    elif args.command == 'brake-pad-demo':
        run_brake_pad_demo()
    elif args.command == 'start-api':
        print(f"Starting DTC REST API on {args.host}:{args.port}...")
        print("Press Ctrl+C to stop the server.")
        start_dtc_api(host=args.host, port=args.port, debug=args.debug)
    elif args.command == 'booking-api':
        print(f"Starting Booking REST API on {args.host}:{args.port}...")
        print("This API uses mocked data for demonstration purposes.")
        print("Press Ctrl+C to stop the server.")
        start_booking_api(host=args.host, port=args.port, debug=args.debug)
    elif args.command == 'help':
        print_usage()
    else:
        print(f"Unknown command: {args.command}")
        print_usage()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main()) 