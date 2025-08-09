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
    
    echo "Fixing import paths in generated files..."
    
    # Fix the specific issues you mentioned, being very precise to avoid duplicates:
    
    # In proto/handlers/cruds_pb2.py - fix malformed imports
    if [ -f proto/handlers/cruds_pb2.py ]; then
        # Fix the specific pattern: from models from ..models import models_pb2 as models_dot_models__pb2 as models_dot_models__pb2
        # First remove any existing alias to prevent duplicates
        sed -i 's/from models from \.\.models import models_pb2 as models_dot_models__pb2 as models_dot_models__pb2/from models from ..models import models_pb2 as models_dot_models__pb2/' proto/handlers/cruds_pb2.py
        sed -i 's/from models from \.\.models import game_pb2 as models_dot_game__pb2 as models_dot_game__pb2/from models from ..models import game_pb2 as models_dot_game__pb2/' proto/handlers/cruds_pb2.py
        # Then fix the malformed import
        sed -i 's/from models from \.\.models import models_pb2/from ..models import models_pb2/' proto/handlers/cruds_pb2.py
        sed -i 's/from models from \.\.models import game_pb2/from ..models import game_pb2/' proto/handlers/cruds_pb2.py
        # Also fix simpler malformed imports
        sed -i 's/from models import models_pb2/from ..models import models_pb2/' proto/handlers/cruds_pb2.py
        sed -i 's/from models import game_pb2/from ..models import game_pb2/' proto/handlers/cruds_pb2.py
    fi
    
    # In proto/handlers/cruds_pb2_grpc.py - fix malformed imports
    if [ -f proto/handlers/cruds_pb2_grpc.py ]; then
        # Fix the specific pattern: from handlers from . import cruds_pb2 as handlers_dot_cruds__pb2 as handlers_dot_cruds__pb2
        # First remove any existing alias to prevent duplicates
        sed -i 's/from handlers from \. import cruds_pb2 as handlers_dot_cruds__pb2 as handlers_dot_cruds__pb2/from handlers from . import cruds_pb2 as handlers_dot_cruds__pb2/' proto/handlers/cruds_pb2_grpc.py
        # Then fix the malformed import
        sed -i 's/from handlers from \. import cruds_pb2/from . import cruds_pb2/' proto/handlers/cruds_pb2_grpc.py
        # Also fix models imports
        sed -i 's/from models from \.\.models import models_pb2/from ..models import models_pb2/' proto/handlers/cruds_pb2_grpc.py
    fi
    
    # Fix similar issues in other files
    find proto -name "*.py" -exec sed -i 's/from models from \.\.models/from ..models/g' {} \;
    find proto -name "*.py" -exec sed -i 's/from handlers from \./from ./g' {} \;
    
    # Clean up any remaining duplicate "as" clauses
    find proto -name "*.py" -exec sed -i 's/as models_dot_models__pb2 as models_dot_models__pb2/as models_dot_models__pb2/g' {} \;
    find proto -name "*.py" -exec sed -i 's/as models_dot_game__pb2 as models_dot_game__pb2/as models_dot_game__pb2/g' {} \;
    find proto -name "*.py" -exec sed -i 's/as handlers_dot_cruds__pb2 as handlers_dot_cruds__pb2/as handlers_dot_cruds__pb2/g' {} \;
    find proto -name "*.py" -exec sed -i 's/as handlers_dot_hello__pb2 as handlers_dot_hello__pb2/as handlers_dot_hello__pb2/g' {} \;
    
    echo "Import paths fixed!"
    
    # Show what files were generated
    echo "Generated files:"
    find proto -name "*_pb2*.py" | sort
    
    echo ""
    echo "You can now run the bot with: python3 main.py"
else
    echo "Proto generation failed!"
    exit 1
fi