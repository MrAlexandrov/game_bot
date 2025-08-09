#!/bin/bash

# Remove any previously generated files
rm -f proto/handlers/*_pb2.py proto/handlers/*_pb2_grpc.py
rm -f proto/models/*_pb2.py proto/models/*_pb2_grpc.py

# Generate Python gRPC code from proto files
# Use a more explicit approach to ensure correct package structure
python3 -m grpc_tools.protoc \
  -I./proto \
  --python_out=./proto \
  --grpc_python_out=./proto \
  ./proto/models/models.proto \
  ./proto/models/game.proto \
  ./proto/handlers/cruds.proto \
  ./proto/handlers/hello.proto

# Check if generation was successful
if [ $? -eq 0 ]; then
    echo "Proto generation successful!"
    
    # Add UTF-8 encoding declaration to all generated files
    find proto -name "*_pb2.py" -exec sed -i '1i\# -*- coding: utf-8 -*-' {} \;
    find proto -name "*_pb2_grpc.py" -exec sed -i '1i\# -*- coding: utf-8 -*-' {} \;
    
    # Fix import paths in generated files with more precise patterns
    # We need to be very careful about the order of replacements
    
    # Fix models_pb2 imports in models package (should be relative)
    if [ -f proto/models/models_pb2.py ]; then
        # Replace direct imports with relative imports
        sed -i 's/import models_pb2/from . import models_pb2 as models_dot_models__pb2/g' proto/models/models_pb2.py
    fi
    
    # Fix imports in models/game_pb2.py (should import from parent models package)
    if [ -f proto/models/game_pb2.py ]; then
        sed -i 's/import models_pb2/from ..models import models_pb2 as models_dot_models__pb2/g' proto/models/game_pb2.py
    fi
    
    # Fix imports in handlers package (should import from models package)
    if [ -f proto/handlers/cruds_pb2.py ]; then
        # Fix imports from models package
        sed -i 's/import models_pb2/from ..models import models_pb2 as models_dot_models__pb2/g' proto/handlers/cruds_pb2.py
        sed -i 's/import game_pb2/from ..models import game_pb2 as models_dot_game__pb2/g' proto/handlers/cruds_pb2.py
    fi
    
    if [ -f proto/handlers/cruds_pb2_grpc.py ]; then
        # Fix imports from models package
        sed -i 's/import models_pb2/from ..models import models_pb2 as models_dot_models__pb2/g' proto/handlers/cruds_pb2_grpc.py
        # Fix relative imports within handlers package
        sed -i 's/import cruds_pb2/from . import cruds_pb2 as handlers_dot_cruds__pb2/g' proto/handlers/cruds_pb2_grpc.py
    fi
    
    if [ -f proto/handlers/hello_pb2.py ]; then
        # Fix imports from models package
        sed -i 's/import models_pb2/from ..models import models_pb2 as models_dot_models__pb2/g' proto/handlers/hello_pb2.py
    fi
    
    if [ -f proto/handlers/hello_pb2_grpc.py ]; then
        # Fix imports from models package
        sed -i 's/import models_pb2/from ..models import models_pb2 as models_dot_models__pb2/g' proto/handlers/hello_pb2_grpc.py
        # Fix relative imports within handlers package
        sed -i 's/import hello_pb2/from . import hello_pb2 as handlers_dot_hello__pb2/g' proto/handlers/hello_pb2_grpc.py
    fi
    
    # Final cleanup for any malformed import lines
    # Remove any duplicate "from" keywords that might have been created
    find proto -name "*.py" -exec sed -i 's/from from \.\./from ../g' {} \;
    find proto -name "*.py" -exec sed -i 's/from from \./from ./g' {} \;
    
    echo "Import paths fixed!"
    echo "Generated files are now in the correct location with proper import paths."
    
    # Show what files were generated
    echo "Generated files:"
    find proto -name "*_pb2*.py" | sort
else
    echo "Proto generation failed!"
    exit 1
fi