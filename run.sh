#!/bin/bash

# Script to run the Telegram bot

echo "Starting Telegram bot..."

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "Error: docker-compose.yml not found!"
    exit 1
fi

# Start the Telegram bot
docker-compose up

echo "Telegram bot stopped."