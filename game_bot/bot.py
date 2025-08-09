"""
Main Telegram bot implementation for the quiz game
"""

import logging
from typing import Dict, List, Optional
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from game_bot.config import TELEGRAM_BOT_TOKEN, POINTS_PER_CORRECT_ANSWER
from game_bot.grpc_client import GameServiceClient
from game_bot.game_state import game_state_manager, GameSessionState, PlayerState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global gRPC client
grpc_client = GameServiceClient()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command"""
    welcome_message = (
        "🎉 Welcome to the Quiz Bot! 🎉\n\n"
        "I can help you play quiz games with your friends!\n\n"
        "Available commands:\n"
        "/start - Show this help message\n"
        "/newgame - Start a new quiz game\n"
        "/join - Join an existing game (only works when a game is waiting for players)\n"
        "/packs - List available quiz packs\n"
        "/cancel - Cancel current game\n\n"
        "To start playing, use /newgame and select a quiz pack!"
    )
    
    await update.message.reply_text(welcome_message)


async def packs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /packs command to list available quiz packs"""
    try:
        packs = grpc_client.get_all_packs()
        
        if not packs:
            await update.message.reply_text("No quiz packs available at the moment.")
            return
        
        message = "📚 Available Quiz Packs:\n\n"
        for i, pack in enumerate(packs, 1):
            message += f"{i}. {pack.title}\n"
        
        message += "\nUse /newgame to start a new game with one of these packs!"
        
        await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Error fetching packs: {e}")
        await update.message.reply_text("Sorry, I couldn't fetch the quiz packs at the moment. Please try again later.")


async def newgame_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /newgame command to start a new game"""
    try:
        # Get available packs
        packs = grpc_client.get_all_packs()
        
        if not packs:
            await update.message.reply_text("No quiz packs available. Please ask an admin to add some packs.")
            return
        
        # Store packs in context for later use
        context.user_data["available_packs"] = packs
        
        # Create keyboard with pack options
        keyboard = [[pack.title] for pack in packs]
        keyboard.append(["Cancel"])
        
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        
        message = "🎮 Choose a quiz pack to start a new game:\n\n"
        for i, pack in enumerate(packs, 1):
            message += f"{i}. {pack.title}\n"
        
        await update.message.reply_text(message, reply_markup=reply_markup)
        context.user_data["awaiting_pack_selection"] = True
        
    except Exception as e:
        logger.error(f"Error starting new game: {e}")
        await update.message.reply_text(
            "Sorry, I couldn't start a new game at the moment. Please try again later.",
            reply_markup=ReplyKeyboardRemove()
        )


async def join_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /join command to join an existing game"""
    user = update.effective_user
    session_state = game_state_manager.get_session_by_user(user.id)
    
    if session_state:
        if session_state.state == "waiting":
            await update.message.reply_text(
                "You're already part of a game that's waiting for players! "
                "Wait for the game creator to start the game.",
                reply_markup=ReplyKeyboardRemove()
            )
        elif session_state.state == "active":
            await update.message.reply_text(
                "You're already in an active game! Finish that game first.",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await update.message.reply_text(
                "You're already in a finished game. Use /cancel to leave it.",
                reply_markup=ReplyKeyboardRemove()
            )
        return
    
    # Find any active sessions waiting for players
    waiting_sessions = [
        session for session in game_state_manager.sessions.values()
        if session.state == "waiting"
    ]
    
    if not waiting_sessions:
        await update.message.reply_text(
            "There are no games currently waiting for players. "
            "Start a new game with /newgame!",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    # For simplicity, join the first waiting session
    # In a real implementation, you might want to let the user choose
    session_to_join = waiting_sessions[0]
    
    # Add player to the session
    player_name = user.first_name or user.username or f"Player_{user.id}"
    player = grpc_client.add_player(session_to_join.game_session_id, player_name)
    
    if not player:
        await update.message.reply_text(
            "Sorry, I couldn't add you to the game. Please try again.",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    # Add player to game state
    game_state_manager.add_player_to_session(
        session_to_join.game_session_id, user.id, player.id, player_name
    )
    
    # Get all players in the session
    players = grpc_client.get_players(session_to_join.game_session_id)
    
    # Notify all players in the session
    message = f"🎉 {player_name} has joined the game!\n\n"
    message += "Players in this game:\n"
    for p in players:
        message += f"• {p.name}\n"
    
    message += "\nWait for the game creator to start the game with the 'Start Game' button."
    
    # For now, we'll just send to the joining player
    # In a real implementation, you'd want to notify all players
    await update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /cancel command to cancel current game"""
    user = update.effective_user
    session_state = game_state_manager.get_session_by_user(user.id)
    
    if not session_state:
        await update.message.reply_text(
            "You're not currently in any game.",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    # Remove user from session
    if user.id in session_state.players:
        del session_state.players[user.id]
    
    # Remove user session reference
    if user.id in game_state_manager.user_sessions:
        del game_state_manager.user_sessions[user.id]
    
    await update.message.reply_text(
        "You've left the game.",
        reply_markup=ReplyKeyboardRemove()
    )


async def handle_pack_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pack selection for a new game"""
    user = update.effective_user
    
    # Check if we're waiting for pack selection
    if not context.user_data.get("awaiting_pack_selection"):
        return
    
    # Clear the flag
    context.user_data["awaiting_pack_selection"] = False
    
    selected_pack_title = update.message.text
    
    # Check if user wants to cancel
    if selected_pack_title == "Cancel":
        await update.message.reply_text(
            "Game creation cancelled.",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    # Find the selected pack
    packs = context.user_data.get("available_packs", [])
    selected_pack = None
    for pack in packs:
        if pack.title == selected_pack_title:
            selected_pack = pack
            break
    
    if not selected_pack:
        await update.message.reply_text(
            "Invalid selection. Please try again with /newgame.",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    # Create a new game session
    game_session = grpc_client.create_game_session(selected_pack.id)
    
    if not game_session:
        await update.message.reply_text(
            "Sorry, I couldn't create a new game session. Please try again.",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    # Create game state
    session_state = game_state_manager.create_session(
        game_session.id, selected_pack.id
    )
    
    # Add the creator as the first player
    player_name = user.first_name or user.username or f"Player_{user.id}"
    player = grpc_client.add_player(game_session.id, player_name)
    
    if not player:
        await update.message.reply_text(
            "Sorry, I couldn't add you to the game. Please try again.",
            reply_markup=ReplyKeyboardRemove()
        )
        # Clean up the session state
        game_state_manager.remove_session(game_session.id)
        return
    
    # Add player to game state
    game_state_manager.add_player_to_session(
        game_session.id, user.id, player.id, player_name
    )
    
    # Get questions for this pack
    questions = grpc_client.get_questions_by_pack_id(selected_pack.id)
    
    if not questions:
        await update.message.reply_text(
            f"The selected pack '{selected_pack.title}' has no questions. "
            "Please choose a different pack.",
            reply_markup=ReplyKeyboardRemove()
        )
        # Clean up
        game_state_manager.remove_session(game_session.id)
        return
    
    # Store questions in game state
    game_state_manager.set_session_questions(game_session.id, questions)
    
    # Create waiting room keyboard
    keyboard = [["Start Game"], ["Cancel Game"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    
    message = f"🎮 New Game Created!\n\n"
    message += f"Pack: {selected_pack.title}\n"
    message += f"Questions: {len(questions)}\n\n"
    message += f"Players:\n• {player_name} (creator)\n\n"
    message += "Waiting for more players to join...\n"
    message += "Other players can join with /join\n\n"
    message += "When ready, press 'Start Game' to begin!"
    
    await update.message.reply_text(message, reply_markup=reply_markup)
    context.user_data["game_creator"] = True
    context.user_data["current_game_session_id"] = game_session.id


async def handle_waiting_room_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle actions in the waiting room"""
    user = update.effective_user
    message_text = update.message.text
    
    session_state = game_state_manager.get_session_by_user(user.id)
    
    if not session_state:
        return
    
    # Check if user is the game creator
    is_creator = context.user_data.get("game_creator", False)
    
    if message_text == "Start Game":
        if not is_creator:
            await update.message.reply_text("Only the game creator can start the game!")
            return
        
        # Start the game
        game_session = grpc_client.start_game_session(session_state.game_session_id)
        
        if not game_session:
            await update.message.reply_text(
                "Sorry, I couldn't start the game. Please try again.",
                reply_markup=ReplyKeyboardRemove()
            )
            return
        
        # Update game state
        game_state_manager.start_session(session_state.game_session_id)
        
        # Notify all players that the game is starting
        message = "🚀 Game Starting!\n\n"
        message += "Get ready for the first question!"
        
        await update.message.reply_text(
            message,
            reply_markup=ReplyKeyboardRemove()
        )
        
        # Present the first question
        await present_question(update, context, session_state.game_session_id)
        
    elif message_text == "Cancel Game":
        if not is_creator:
            await update.message.reply_text("Only the game creator can cancel the game!")
            return
        
        # Clean up the game session
        game_state_manager.remove_session(session_state.game_session_id)
        
        await update.message.reply_text(
            "Game cancelled.",
            reply_markup=ReplyKeyboardRemove()
        )


async def present_question(update: Update, context: ContextTypes.DEFAULT_TYPE, game_session_id: str):
    """Present the current question to all players"""
    session_state = game_state_manager.get_session(game_session_id)
    
    if not session_state:
        return
    
    # Get current question
    question = game_state_manager.get_current_question(game_session_id)
    
    if not question:
        # No more questions, end the game
        await end_game(update, context, game_session_id)
        return
    
    # Get variants for this question
    variants = grpc_client.get_variants_by_question_id(question.id)
    
    if not variants:
        # Skip this question if no variants
        if game_state_manager.advance_question(game_session_id):
            await present_question(update, context, game_session_id)
        else:
            await end_game(update, context, game_session_id)
        return
    
    # Create keyboard with answer options
    keyboard = [[variant.text] for variant in variants]
    keyboard.append(["Leave Game"])
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    
    # Format question message
    message = f"❓ Question {session_state.current_question_index + 1}/{len(session_state.questions)}:\n\n"
    message += f"{question.text}\n\n"
    
    if question.image_url:
        message += f"Image: {question.image_url}\n\n"
    
    message += "Choose your answer:"
    
    # For now, we'll just send to the user who triggered the question
    # In a real implementation, you'd want to send to all players
    await update.message.reply_text(message, reply_markup=reply_markup)
    
    # Store question context for answer processing
    context.user_data["awaiting_answer"] = True
    context.user_data["current_question_id"] = question.id
    context.user_data["current_variants"] = variants


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle player answers"""
    user = update.effective_user
    message_text = update.message.text
    
    # Check if we're waiting for an answer
    if not context.user_data.get("awaiting_answer"):
        return
    
    # Check if player wants to leave
    if message_text == "Leave Game":
        await cancel_command(update, context)
        return
    
    # Get current question and variants
    question_id = context.user_data.get("current_question_id")
    variants = context.user_data.get("current_variants", [])
    
    if not question_id or not variants:
        return
    
    # Find the selected variant
    selected_variant = None
    for variant in variants:
        if variant.text == message_text:
            selected_variant = variant
            break
    
    if not selected_variant:
        await update.message.reply_text("Invalid answer. Please select one of the options.")
        return
    
    # Clear the flag
    context.user_data["awaiting_answer"] = False
    
    # Get session state
    session_state = game_state_manager.get_session_by_user(user.id)
    
    if not session_state:
        await update.message.reply_text(
            "You're not in a game. Start a new game with /newgame",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    # Get player state
    player_state = game_state_manager.get_player_state(session_state.game_session_id, user.id)
    
    if not player_state:
        await update.message.reply_text(
            "You're not registered in this game.",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    # Submit answer to backend
    response = grpc_client.submit_answer(
        player_state.player_id, question_id, selected_variant.id
    )
    
    if not response:
        await update.message.reply_text(
            "Sorry, there was an error submitting your answer. Please try again.",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    # Record answer in game state
    game_state_manager.record_answer(
        session_state.game_session_id, user.id, question_id, 
        selected_variant.id, response.is_correct, response.points
    )
    
    # Send feedback
    if response.is_correct:
        feedback = f"✅ Correct! You earned {response.points} points."
    else:
        feedback = "❌ Incorrect. Better luck next time!"
    
    await update.message.reply_text(feedback, reply_markup=ReplyKeyboardRemove())
    
    # Advance to next question or end game
    if game_state_manager.advance_question(session_state.game_session_id):
        # Present next question
        await present_question(update, context, session_state.game_session_id)
    else:
        # End the game
        await end_game(update, context, session_state.game_session_id)


async def end_game(update: Update, context: ContextTypes.DEFAULT_TYPE, game_session_id: str):
    """End the game and show results"""
    session_state = game_state_manager.get_session(game_session_id)
    
    if not session_state:
        return
    
    # End game session in backend
    grpc_client.end_game_session(game_session_id)
    
    # Update game state
    game_state_manager.end_session(game_session_id)
    
    # Get results
    results = game_state_manager.get_session_results(game_session_id)
    
    # Format results message
    message = "🏆 Game Over! 🏆\n\n"
    message += "Final Scores:\n\n"
    
    for i, result in enumerate(results, 1):
        medal = ""
        if i == 1:
            medal = "🥇"
        elif i == 2:
            medal = "🥈"
        elif i == 3:
            medal = "🥉"
        
        message += f"{medal} {result['player_name']}: {result['score']} points\n"
    
    message += "\nThanks for playing! Start a new game with /newgame"
    
    # Send results to all players
    # For now, we'll just send to the user who triggered the end
    await update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())
    
    # Clean up session
    game_state_manager.remove_session(game_session_id)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages"""
    user = update.effective_user
    message_text = update.message.text
    
    # Check if we're waiting for pack selection
    if context.user_data.get("awaiting_pack_selection"):
        await handle_pack_selection(update, context)
        return
    
    # Check if we're in waiting room
    session_state = game_state_manager.get_session_by_user(user.id)
    if session_state and session_state.state == "waiting":
        if message_text in ["Start Game", "Cancel Game"]:
            await handle_waiting_room_action(update, context)
            return
    
    # Check if we're waiting for an answer
    if context.user_data.get("awaiting_answer"):
        await handle_answer(update, context)
        return
    
    # Default response
    await update.message.reply_text(
        "I didn't understand that command. Use /start to see available commands.",
        reply_markup=ReplyKeyboardRemove()
    )


def main():
    """Start the bot"""
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("packs", packs_command))
    application.add_handler(CommandHandler("newgame", newgame_command))
    application.add_handler(CommandHandler("join", join_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    
    # Add message handler for text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Run the bot
    logger.info("Starting Telegram bot...")
    application.run_polling()


if __name__ == "__main__":
    main()