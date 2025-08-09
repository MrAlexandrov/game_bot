"""
Test script to verify that all modules can be imported correctly
"""

import sys
import os

# Check Python version
if sys.version_info[0] < 3:
    print("This bot requires Python 3.7 or higher.")
    print("Current Python version: {}".format(sys.version))
    sys.exit(1)

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    try:
        # Test importing the main bot module
        from game_bot.bot import main
        print("game_bot.bot imported successfully")
        
        # Test importing the gRPC client
        from game_bot.grpc_client import GameServiceClient
        print("game_bot.grpc_client imported successfully")
        
        # Test importing the game state
        from game_bot.game_state import game_state_manager
        print("game_bot.game_state imported successfully")
        
        # Test importing the proto wrapper
        from game_bot.proto_wrapper import IMPORT_SUCCESS
        if IMPORT_SUCCESS:
            print("game_bot.proto_wrapper imported successfully with proto modules")
        else:
            print("game_bot.proto_wrapper imported successfully (proto modules not available)")
        
        # Test importing the config
        from game_bot.config import TELEGRAM_BOT_TOKEN, BACKEND_GRPC_ADDRESS
        print("game_bot.config imported successfully")
        
        print("\nAll imports successful! The bot code is syntactically correct.")
        return True
        
    except ImportError as e:
        print("Import error: {}".format(e))
        # Check if it's a proto-related import error
        if "proto" in str(e):
            print("This might be because the proto files haven't been generated yet.")
            print("Run './generate_proto.sh' to generate the required proto files.")
        return False
    except Exception as e:
        print("Unexpected error: {}".format(e))
        return False

if __name__ == "__main__":
    test_imports()