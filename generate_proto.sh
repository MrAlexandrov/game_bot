#!/bin/bash

# Remove any previously generated files
rm -f proto/handlers/*_pb2.py proto/handlers/*_pb2_grpc.py
rm -f proto/models/*_pb2.py proto/models/*_pb2_grpc.py

echo "Generating Python gRPC code from proto files..."

# Generate Python gRPC code from proto files
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
    
    echo "Generated files:"
    find proto -name "*_pb2*.py" | sort
    
    echo ""
    echo "You can now run the bot with: python3 main.py"
else
    echo "Proto generation failed!"
    exit 1
fi