# Telegram Bot Setup Guide

This guide explains how to set up and run the Telegram bot for the quiz game.

## Overview

The Telegram bot has been migrated from the backend repository to the main game project. It uses HTTP API to communicate with the backend service.

**Key Changes:**
- ✅ Moved from `/Users/mrralexandrov/projects/game_userver/telegram_bot` to `/Users/mrralexandrov/projects/game/frontend/telegram_bot`
- ✅ Updated to use HTTP API instead of gRPC
- ✅ Integrated with Docker Compose for easy deployment
- ✅ Old bot backed up to `telegram_bot_old_backup` directory

## Prerequisites

1. **Telegram Bot Token**: Get one from [@BotFather](https://t.me/botfather)
   - Send `/newbot` to BotFather
   - Follow the instructions
   - Save the token you receive

2. **Backend Service**: The game backend must be running and accessible

## Quick Start with Docker Compose

### 1. Set up environment variables

Create a `.env` file in the project root (`/Users/mrralexandrov/projects/game/`):

```bash
# In /Users/mrralexandrov/projects/game/
cat > .env << 'EOF'
TELEGRAM_BOT_TOKEN=your_bot_token_here
EOF
```

Replace `your_bot_token_here` with your actual bot token from BotFather.

### 2. Start all services

From the project root:

```bash
cd /Users/mrralexandrov/projects/game
docker-compose up -d
```

This will start:
- PostgreSQL database
- Backend service (userver)
- Telegram bot

### 3. Check logs

```bash
# View all logs
docker-compose logs -f

# View only bot logs
docker-compose logs -f telegram_bot

# View only backend logs
docker-compose logs -f backend
```

### 4. Stop services

```bash
docker-compose down
```

## Manual Setup (Without Docker)

If you prefer to run the bot manually:

### 1. Install Poetry

```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. Install dependencies

```bash
cd /Users/mrralexandrov/projects/game/frontend/telegram_bot
poetry install
```

### 3. Set environment variables

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export API_BASE_URL="http://localhost:8080"
```

### 4. Run the bot

```bash
# Using Poetry
poetry run python bot.py

# Or activate the virtual environment first
poetry shell
python bot.py
```

## Using the Bot

Once the bot is running, open Telegram and find your bot:

### Available Commands

- `/start` - Welcome message and introduction
- `/newgame` - Create a new quiz game
- `/cancel` - Cancel the current game
- `/help` - Show help information

### Game Flow

1. **Start a game**: Send `/newgame`
2. **Select a pack**: Choose from available quiz packs
3. **Wait for players**: Other players can join (currently single-player)
4. **Begin**: Click "▶️ Начать игру" to start
5. **Answer questions**: Select answers from the options
6. **View results**: See final scores when the game ends

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | - | Yes |
| `API_BASE_URL` | Backend API URL | `http://localhost:8080` | No |

### Docker Compose Configuration

The bot is configured in [`docker-compose.yml`](../../docker-compose.yml):

```yaml
telegram_bot:
  build:
    context: ./frontend/telegram_bot
  environment:
    - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    - API_BASE_URL=http://backend:8080
  depends_on:
    - backend
```

## API Endpoints Used

The bot communicates with these backend endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/packs` | GET | Get all quiz packs |
| `/games` | POST | Create a game session |
| `/games/{id}/players` | POST | Add a player |
| `/games/{id}/start` | POST | Start the game |
| `/games/{id}/state` | GET | Get current question |
| `/games/{id}/answers` | POST | Submit an answer |
| `/games/{id}/results` | GET | Get game results |

## Troubleshooting

### Bot doesn't respond

1. Check if the bot is running:
   ```bash
   docker-compose ps telegram_bot
   ```

2. Check bot logs:
   ```bash
   docker-compose logs telegram_bot
   ```

3. Verify the token is correct in `.env` file

### "Cannot connect to backend" error

1. Ensure backend is running:
   ```bash
   docker-compose ps backend
   ```

2. Check backend logs:
   ```bash
   docker-compose logs backend
   ```

3. Verify backend is accessible:
   ```bash
   curl http://localhost:8080/packs
   ```

### "No packs available" error

The database needs to be populated with quiz data. Check the backend documentation for how to add packs and questions.

### Bot crashes on startup

1. Check Python version (requires 3.8+):
   ```bash
   python --version
   ```

2. Reinstall dependencies:
   ```bash
   poetry install --no-cache
   ```

## Development

### Project Structure

```
frontend/telegram_bot/
├── bot.py              # Main bot logic
├── pyproject.toml     # Poetry configuration and dependencies
├── Dockerfile         # Docker configuration
├── .env.example       # Environment template
├── README.md          # Original documentation
├── SETUP.md           # This file
├── CHANGELOG.md       # Version history
└── QUICKSTART.md      # Quick reference
```

### Making Changes

1. Edit [`bot.py`](./bot.py) for bot logic changes
2. Update [`pyproject.toml`](./pyproject.toml) if adding dependencies:
   ```bash
   poetry add package-name
   ```
3. Rebuild the Docker image:
   ```bash
   docker-compose build telegram_bot
   docker-compose up -d telegram_bot
   ```

### Testing Locally

```bash
# Set environment variables
export TELEGRAM_BOT_TOKEN="your_token"
export API_BASE_URL="http://localhost:8080"

# Run the bot with Poetry
poetry run python bot.py
```

## Migration Notes

### What Changed

1. **Location**: Moved from backend repo to main game project
2. **API**: Changed from gRPC to HTTP REST API
3. **Deployment**: Integrated with Docker Compose
4. **Configuration**: Simplified environment variables

### Old Bot Backup

The old gRPC-based bot is backed up at:
```
/Users/mrralexandrov/projects/game/frontend/telegram_bot_old_backup/
```

You can reference it if needed, but the new HTTP-based bot is recommended.

## Next Steps

1. ✅ Bot is set up and ready to use
2. 📝 Add quiz packs to the database (see backend documentation)
3. 🎮 Test the bot by creating a game
4. 🚀 Deploy to production (optional)

## Support

For issues or questions:
1. Check the [main README](../../README.md)
2. Review backend documentation
3. Check bot logs for error messages

## License

This project follows the same license as the main game project.