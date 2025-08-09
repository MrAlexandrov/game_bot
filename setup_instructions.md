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
python3 main.py
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

After running the proto generation script, you should have these files:
- `proto/handlers/cruds_pb2.py`
- `proto/handlers/cruds_pb2_grpc.py`
- `proto/models/models_pb2.py`
- `proto/models/game_pb2.py`

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