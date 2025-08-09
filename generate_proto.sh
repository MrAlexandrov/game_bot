#!/bin/bash

# Generate Python gRPC code from proto files
python -m grpc_tools.protoc -I./proto \
  --python_out=. \
  --grpc_python_out=. \
  ./proto/models/models.proto \
  ./proto/models/game.proto \
  ./proto/handlers/cruds.proto \
  ./proto/handlers/hello.proto

# Fix import paths in generated files
sed -i 's/import models/import game_bot.proto.models/g' proto/handlers/cruds_pb2.py
sed -i 's/from models/from game_bot.proto.models/g' proto/handlers/cruds_pb2_grpc.py
sed -i 's/import handlers/import game_bot.proto.handlers/g' proto/handlers/cruds_pb2_grpc.py