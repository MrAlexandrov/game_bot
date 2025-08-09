#!/bin/bash

# Generate Python gRPC code from proto files
python -m grpc_tools.protoc -I./proto \
  --python_out=. \
  --grpc_python_out=. \
  ./proto/models/models.proto \
  ./proto/models/game.proto \
  ./proto/handlers/cruds.proto \
  ./proto/handlers/hello.proto

# Check if generation was successful
if [ $? -eq 0 ]; then
    echo "Proto generation successful!"
    
    # Fix import paths in generated files if they exist
    if [ -f proto/handlers/cruds_pb2.py ]; then
        sed -i 's/import models_pb2/from . import models_pb2/g' proto/handlers/cruds_pb2.py
    fi
    
    if [ -f proto/handlers/cruds_pb2_grpc.py ]; then
        sed -i 's/from models_pb2/from . import models_pb2/g' proto/handlers/cruds_pb2_grpc.py
        sed -i 's/import cruds_pb2/from . import cruds_pb2/g' proto/handlers/cruds_pb2_grpc.py
    fi
    
    echo "Import paths fixed!"
else
    echo "Proto generation failed!"
fi