# Game Bot

A Telegram bot for conducting quiz games using the game_userver backend service.

## Features

- Create and join quiz games
- Multiple players can participate in the same game
- Various quiz packs with questions and answers
- Score tracking and game results
- Real-time game management

## Prerequisites

- Python 3.7 or higher
- A Telegram bot token (from BotFather)
- Access to the game_userver backend service

## Setup

1. Clone the repository (if not already cloned)

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Generate the gRPC client code from proto files:
   ```bash
   chmod +x generate_proto.sh
   ./generate_proto.sh
   ```

4. Set up environment variables:
   ```bash
   export TELEGRAM_BOT_TOKEN="your_telegram_bot_token_here"
   export BACKEND_GRPC_ADDRESS="localhost:8082"  # Adjust if your backend is on a different address
   ```

## Running the Bot

```bash
python main.py
```

## Usage

Once the bot is running, you can interact with it using these commands:

- `/start` - Show help message
- `/newgame` - Start a new quiz game
- `/join` - Join an existing game
- `/packs` - List available quiz packs
- `/cancel` - Cancel current game

## How to Play

1. Start a new game with `/newgame` and select a quiz pack
2. Other players can join with `/join` while the game is waiting for players
3. The game creator starts the game when ready
4. Answer questions as they appear
5. See final scores when the game ends

## Project Structure

```
game_bot/
├── game_bot/           # Main bot package
│   ├── __init__.py     # Package initializer
│   ├── config.py       # Configuration settings
│   ├── grpc_client.py  # gRPC client for backend service
│   ├── game_state.py   # Game state management
│   └── bot.py          # Main bot logic
├── proto/              # Protocol buffer definitions
├── main.py             # Entry point
├── requirements.txt    # Python dependencies
├── generate_proto.sh   # Script to generate gRPC code
└── README.md           # This file
```

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

## Troubleshooting

### Common Issues

1. **"Module not found" errors**: Make sure you've run the proto generation script
2. **Connection errors**: Verify the backend service is running and accessible
3. **Authentication errors**: Check your Telegram bot token

### Logs

The bot logs information and errors to the console. For more detailed logging, you can modify the logging level in `bot.py` and `grpc_client.py`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request