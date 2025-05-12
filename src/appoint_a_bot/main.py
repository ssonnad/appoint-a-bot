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

def print_usage():
    """Print usage information."""
    print("Appoint-a-Bot - Appointment Scheduling System")
    print("\nUsage:")
    print("  python -m src.appoint_a_bot.main [command]")
    print("\nCommands:")
    print("  demo       - Run the interactive demo")
    print("  final-demo - Run the complete final demo with both scenarios")
    print("  help       - Show this help message")

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Appoint-a-Bot - Appointment Scheduling System")
    parser.add_argument('command', nargs='?', default='help',
                        help='Command to run (demo, final-demo, help)')

    args = parser.parse_args()

    if args.command == 'demo':
        run_conversation_demo()
    elif args.command == 'final-demo':
        run_final_demo()
    elif args.command == 'help':
        print_usage()
    else:
        print(f"Unknown command: {args.command}")
        print_usage()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main()) 