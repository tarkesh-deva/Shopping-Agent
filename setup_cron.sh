#!/bin/bash

# Get the absolute path to the project directory
PROJECT_DIR="/Users/tarkeshdeva/Desktop/AR Navigation App/MCP Server - Shopping"

# Activate virtual environment and run the script
COMMAND="cd $PROJECT_DIR && source venv/bin/activate && python offline_price_update.py --notify"

# Create a temporary file with the current crontab
crontab -l > temp_crontab 2>/dev/null || echo "" > temp_crontab

# Check if the cron job already exists
if grep -q "$COMMAND" temp_crontab; then
    echo "Cron job already exists. No changes made."
else
    # Add the new cron jobs for 11 AM and 8 PM IST
    # Note: Cron uses the system's local time, so adjust accordingly if your system is not in IST
    echo "# Shopping Assistant price update jobs" >> temp_crontab
    echo "0 11 * * * $COMMAND # Run at 11 AM IST" >> temp_crontab
    echo "0 20 * * * $COMMAND # Run at 8 PM IST" >> temp_crontab
    
    # Install the new crontab
    crontab temp_crontab
    echo "Cron jobs added successfully for 11 AM and 8 PM IST."
fi

# Clean up
rm temp_crontab

echo "To view your crontab, run: crontab -l"
