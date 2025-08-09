"""
Wrapper module for proto imports to handle import path issues
"""

import sys
import os

# Add the current directory to the path so we can import proto modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import the generated proto modules with error handling
try:
    # Import models
    from proto.models import models_pb2 as models_models_pb2
    from proto.models import game_pb2 as models_game_pb2
    
    # Import handlers
    from proto.handlers import cruds_pb2 as handlers_cruds_pb2
    from proto.handlers import cruds_pb2_grpc as handlers_cruds_pb2_grpc
    from proto.handlers import hello_pb2 as handlers_hello_pb2
    from proto.handlers import hello_pb2_grpc as handlers_hello_pb2_grpc
    
    # Make them available as module attributes
    models_pb2 = models_models_pb2
    game_pb2 = models_game_pb2
    cruds_pb2 = handlers_cruds_pb2
    cruds_pb2_grpc = handlers_cruds_pb2_grpc
    hello_pb2 = handlers_hello_pb2
    hello_pb2_grpc = handlers_hello_pb2_grpc
    
    # Success flag
    IMPORT_SUCCESS = True
    
except ImportError as e:
    print("Failed to import proto modules: {}".format(e))
    print("Make sure you've run the proto generation script: ./generate_proto.sh")
    
    # Create mock modules for development
    class MockModule:
        pass
    
    models_pb2 = MockModule()
    game_pb2 = MockModule()
    cruds_pb2 = MockModule()
    cruds_pb2_grpc = MockModule()
    hello_pb2 = MockModule()
    hello_pb2_grpc = MockModule()
    
    # Success flag
    IMPORT_SUCCESS = False