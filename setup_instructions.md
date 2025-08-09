# Setup Instructions

Since you'll be setting up and running this bot on a different machine, here are the steps you need to follow:

## Prerequisites

- Python 3.7 or higher (the bot uses async/await syntax which requires Python 3.7+)
- A Telegram bot token (from BotFather)
- Access to the game_userver backend service

## 1. Install Dependencies

```bash
# Make sure you're using Python 3
python3 --version

# Install the required dependencies
pip3 install -r requirements.txt
```

This will install:
- python-telegram-bot==13.15 (requires Python 3.7+)
- grpcio==1.50.0
- protobuf==3.20.3

## 2. Generate gRPC Code

Install the gRPC tools:
```bash
pip3 install grpcio-tools==1.50.0
```

Then run the generation script:
```bash
chmod +x generate_proto.sh
./generate_proto.sh
```

This script will:
- Generate Python code from the proto files directly into the `proto/` directory structure
- Fix import paths in the generated files

## 3. Set Environment Variables

You need to set these environment variables:

```bash
export TELEGRAM_BOT_TOKEN="your_actual_telegram_bot_token"
export BACKEND_GRPC_ADDRESS="address_of_your_backend_service:port"
```

## 4. Run the Bot

```bash
python3 main.py
```

## Directory Structure

After generating the proto files, your directory structure should look like this:

```
game_bot/
├── game_bot/           # Main bot package
│   ├── __init__.py     # Package initializer
│   ├── config.py       # Configuration settings
│   ├── grpc_client.py  # gRPC client for backend service
│   ├── game_state.py   # Game state management
│   └── bot.py          # Main bot logic
├── proto/              # Protocol buffer definitions and generated code
│   ├── __init__.py
│   ├── handlers/       # Handler proto files and generated code
│   │   ├── __init__.py
│   │   ├── cruds.proto
│   │   ├── cruds_pb2.py
│   │   ├── cruds_pb2_grpc.py
│   │   ├── hello.proto
│   │   ├── hello_pb2.py
│   │   └── hello_pb2_grpc.py
│   └── models/         # Model proto files and generated code
│       ├── __init__.py
│       ├── game.proto
│       ├── game_pb2.py
│       ├── game_pb2_grpc.py
│       ├── models.proto
│       ├── models_pb2.py
│       └── models_pb2_grpc.py
├── main.py             # Entry point
├── requirements.txt    # Python dependencies
├── generate_proto.sh   # Script to generate gRPC code
└── README.md           # This file
```

## Troubleshooting

### Common Issues

1. **Python version issues**: Make sure you're using Python 3.7 or higher
2. **Proto generation fails**: Make sure you have `grpcio-tools` installed before running the script
3. **Import errors**: If you still get import errors after generating the proto code, try running:
   ```bash
   export PYTHONPATH=/path/to/game_bot:$PYTHONPATH
   ```
4. **Connection errors**: Verify the backend service is running and accessible
5. **Authentication errors**: Check your Telegram bot token

### Generated Files

After running the proto generation script, you should have these files in the `proto/` directory:
- `proto/handlers/cruds_pb2.py`
- `proto/handlers/cruds_pb2_grpc.py`
- `proto/handlers/hello_pb2.py`
- `proto/handlers/hello_pb2_grpc.py`
- `proto/models/models_pb2.py`
- `proto/models/models_pb2_grpc.py`
- `proto/models/game_pb2.py`
- `proto/models/game_pb2_grpc.py`

### Logs

The bot logs information and errors to the console. For more detailed logging, you can modify the logging level in `bot.py` and `grpc_client.py`.

## Development

### Adding New Features

1. Modify the proto files if you need to change the API
2. Regenerate the gRPC code with `./generate_proto.sh`
3. Update the `grpc_client.py` with new methods if needed
4. Add new command handlers in `bot.py`

### Code Structure

- `config.py` - Contains all configuration variables
- `grpc_client.py` - Handles all communication with the backend service
- `game_state.py` - Manages in-memory game state
- `bot.py` - Contains all Telegram bot logic and command handlers