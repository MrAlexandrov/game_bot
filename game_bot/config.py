"""
Configuration for the game bot
"""

import os

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Backend service gRPC address
BACKEND_GRPC_ADDRESS = os.getenv("BACKEND_GRPC_ADDRESS", "localhost:8081")

# Game settings
POINTS_PER_CORRECT_ANSWER = 10