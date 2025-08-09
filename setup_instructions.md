# Setup Instructions

Since you'll be setting up and running this bot on a different machine, here are the steps you need to follow:

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- python-telegram-bot==13.15
- grpcio==1.50.0
- protobuf==3.20.3

## 2. Generate gRPC Code

Install the gRPC tools:
```bash
pip install grpcio-tools==1.50.0
```

Then run the generation script:
```bash
chmod +x generate_proto.sh
./generate_proto.sh
```

This script will:
- Generate Python code from the proto files
- Fix import paths in the generated files

## 3. Set Environment Variables

You need to set these environment variables:

```bash
export TELEGRAM_BOT_TOKEN="your_actual_telegram_bot_token"
export BACKEND_GRPC_ADDRESS="address_of_your_backend_service:port"
```

## 4. Run the Bot

```bash
python main.py
```

## Troubleshooting

If you encounter import errors after generating the gRPC code, you may need to manually fix some import paths in the generated files in the `proto/handlers/` and `proto/models/` directories.

The generated files should be:
- `proto/handlers/cruds_pb2.py`
- `proto/handlers/cruds_pb2_grpc.py`
- `proto/models/models_pb2.py`
- `proto/models/game_pb2.py`

Make sure the import statements in these files correctly reference the package structure.