"""
Configuration for the game bot
"""

import os
import yaml
from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

# Load configuration from YAML file
config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Telegram Bot Token (from environment variable only)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Backend service gRPC address (from environment variable or config file)
BACKEND_GRPC_ADDRESS = os.getenv("BACKEND_GRPC_ADDRESS") or config.get('backend', {}).get('grpc_address', "localhost:8081")

# Game settings (from config file)
POINTS_PER_CORRECT_ANSWER = config.get('game', {}).get('points_per_correct_answer', 10)