#!/bin/bash

# Remove any previously generated files
rm -f proto/handlers/*_pb2.py proto/handlers/*_pb2_grpc.py
rm -f proto/models/*_pb2.py proto/models/*_pb2_grpc.py

# Generate Python gRPC code from proto files
python3 -m grpc_tools.protoc -I./proto \
  --python_out=./proto \
  --grpc_python_out=./proto \
  ./proto/models/models.proto \
  ./proto/models/game.proto \
  ./proto/handlers/cruds.proto \
  ./proto/handlers/hello.proto

# Check if generation was successful
if [ $? -eq 0 ]; then
    echo "Proto generation successful!"
    
    # Fix import paths in generated files
    # For models files
    if [ -f proto/models/models_pb2.py ]; then
        sed -i '1i\# -*- coding: utf-8 -*-' proto/models/models_pb2.py
        # Fix relative imports within models package
        sed -i 's/import models_pb2/from . import models_pb2/g' proto/models/models_pb2.py
    fi
    
    if [ -f proto/models/game_pb2.py ]; then
        sed -i '1i\# -*- coding: utf-8 -*-' proto/models/game_pb2.py
        # Fix relative imports within models package
        sed -i 's/import models_pb2/from . import models_pb2/g' proto/models/game_pb2.py
    fi
    
    # For handlers files
    if [ -f proto/handlers/cruds_pb2.py ]; then
        sed -i '1i\# -*- coding: utf-8 -*-' proto/handlers/cruds_pb2.py
        # Fix imports from models package
        sed -i 's/import models_pb2/from ..models import models_pb2/g' proto/handlers/cruds_pb2.py
    fi
    
    if [ -f proto/handlers/cruds_pb2_grpc.py ]; then
        sed -i '1i\# -*- coding: utf-8 -*-' proto/handlers/cruds_pb2_grpc.py
        # Fix imports from models package
        sed -i 's/from models_pb2/from ..models import models_pb2/g' proto/handlers/cruds_pb2_grpc.py
        # Fix relative imports within handlers package
        sed -i 's/import cruds_pb2/from . import cruds_pb2/g' proto/handlers/cruds_pb2_grpc.py
    fi
    
    if [ -f proto/handlers/hello_pb2.py ]; then
        sed -i '1i\# -*- coding: utf-8 -*-' proto/handlers/hello_pb2.py
        # Fix imports from models package
        sed -i 's/import models_pb2/from ..models import models_pb2/g' proto/handlers/hello_pb2.py
    fi
    
    if [ -f proto/handlers/hello_pb2_grpc.py ]; then
        sed -i '1i\# -*- coding: utf-8 -*-' proto/handlers/hello_pb2_grpc.py
        # Fix imports from models package
        sed -i 's/from models_pb2/from ..models import models_pb2/g' proto/handlers/hello_pb2_grpc.py
        # Fix relative imports within handlers package
        sed -i 's/import hello_pb2/from . import hello_pb2/g' proto/handlers/hello_pb2_grpc.py
    fi
    
    echo "Import paths fixed!"
    echo "Generated files are now in the correct location with proper import paths."
else
    echo "Proto generation failed!"
fi