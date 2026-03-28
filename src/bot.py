#!/usr/bin/env python3
"""
Telegram Bot для игры в викторину через HTTP API
"""

import os
import logging
from typing import Dict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

from .api import GameAPI

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Конфигурация
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Состояния для ConversationHandler
SELECTING_PACK, WAITING_FOR_PLAYERS, PLAYING, UPLOADING_PACK = range(4)

# Хранилище активных игр (в продакшене использовать Redis или БД)
active_games: Dict[int, dict] = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало работы с ботом"""
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n\n"
        "Я бот для игры в викторину! 🎮\n\n"
        "Используй /newgame чтобы начать новую игру\n"
        "Используй /help для получения справки"
    )
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать справку"""
    help_text = """
🎮 *Команды бота:*

/start - Начать работу с ботом
/newgame - Создать новую игру
/uploadpack - Загрузить новый пак вопросов из YAML файла
/cancel - Отменить текущую игру
/help - Показать эту справку

*Как играть:*
1. Создайте новую игру командой /newgame
2. Выберите пак вопросов
3. Другие игроки нажимают «Присоединиться»
4. Когда все готовы — нажмите «Начать игру»
5. Отвечайте на вопросы, выбирая правильные варианты
6. В конце игры увидите результаты!

*Как загрузить пак:*
1. Используйте команду /uploadpack
2. Отправьте YAML файл с вопросами
3. Пак будет добавлен в систему

Удачи! 🍀
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def new_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Создать новую игру"""
    # Получаем доступные паки
    packs = GameAPI.get_all_packs()

    if not packs:
        await update.message.reply_text(
            "❌ Не удалось загрузить список паков. Попробуйте позже."
        )
        return ConversationHandler.END

    # Создаем клавиатуру с паками
    keyboard = []
    for pack in packs:
        keyboard.append(
            [InlineKeyboardButton(pack["title"], callback_data=f"pack_{pack['id']}")]
        )

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎯 Выберите пак вопросов:", reply_markup=reply_markup
    )

    return SELECTING_PACK


async def pack_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора пака"""
    query = update.callback_query
    await query.answer()

    pack_id = query.data.replace("pack_", "")
    chat_id = update.effective_chat.id
    user = update.effective_user

    # Создаем игровую сессию
    game_session = GameAPI.create_game_session(pack_id)

    if not game_session:
        await query.edit_message_text(
            "❌ Не удалось создать игровую сессию. Попробуйте позже."
        )
        return ConversationHandler.END

    # Добавляем создателя как первого игрока
    creator_name = user.first_name or f"Player_{user.id}"
    player = GameAPI.add_player(game_session["id"], creator_name)

    if not player:
        await query.edit_message_text("❌ Не удалось добавить игрока. Попробуйте позже.")
        return ConversationHandler.END

    # Сохраняем информацию об игре
    active_games[chat_id] = {
        "game_session_id": game_session["id"],
        "players": {user.id: player["id"]},
        "player_names": [creator_name],
        "current_question": None,
    }

    keyboard = [
        [InlineKeyboardButton("🎮 Присоединиться", callback_data="join_game")],
        [InlineKeyboardButton("▶️ Начать игру", callback_data="start_game")],
        [InlineKeyboardButton("❌ Отменить", callback_data="cancel_game")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"✅ Игра создана!\n\n"
        f"👥 Игроки ({len(active_games[chat_id]['player_names'])}):\n"
        f"• {creator_name}\n\n"
        f"Другие игроки могут нажать «Присоединиться».\n"
        f"Когда все будут готовы, нажмите «Начать игру».",
        reply_markup=reply_markup,
    )

    return WAITING_FOR_PLAYERS


async def join_game_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Присоединиться к игре"""
    query = update.callback_query

    chat_id = update.effective_chat.id
    user = update.effective_user

    if chat_id not in active_games:
        await query.answer("❌ Игра не найдена!", show_alert=True)
        return WAITING_FOR_PLAYERS

    game_info = active_games[chat_id]

    if user.id in game_info["players"]:
        await query.answer("Вы уже в игре!", show_alert=True)
        return WAITING_FOR_PLAYERS

    player_name = user.first_name or f"Player_{user.id}"
    player = GameAPI.add_player(game_info["game_session_id"], player_name)

    if not player:
        await query.answer("❌ Не удалось присоединиться к игре!", show_alert=True)
        return WAITING_FOR_PLAYERS

    await query.answer()

    game_info["players"][user.id] = player["id"]
    game_info["player_names"].append(player_name)

    players_text = "\n".join(f"• {name}" for name in game_info["player_names"])
    keyboard = [
        [InlineKeyboardButton("🎮 Присоединиться", callback_data="join_game")],
        [InlineKeyboardButton("▶️ Начать игру", callback_data="start_game")],
        [InlineKeyboardButton("❌ Отменить", callback_data="cancel_game")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"✅ {player_name} присоединился к игре!\n\n"
        f"👥 Игроки ({len(game_info['player_names'])}):\n"
        f"{players_text}\n\n"
        f"Когда все будут готовы, нажмите «Начать игру».",
        reply_markup=reply_markup,
    )

    return WAITING_FOR_PLAYERS


async def start_game_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Начать игру"""
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id

    if chat_id not in active_games:
        await query.edit_message_text("❌ Игра не найдена.")
        return ConversationHandler.END

    game_info = active_games[chat_id]

    # Запускаем игру
    result = GameAPI.start_game(game_info["game_session_id"])

    if not result:
        await query.edit_message_text("❌ Не удалось начать игру. Попробуйте позже.")
        return ConversationHandler.END

    await query.edit_message_text("🎮 Игра началась! Загружаю первый вопрос...")

    # Показываем первый вопрос
    await show_question(update, context)

    return PLAYING


async def show_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать текущий вопрос"""
    chat_id = update.effective_chat.id

    if chat_id not in active_games:
        return

    game_info = active_games[chat_id]

    # Получаем текущий вопрос
    question_data = GameAPI.get_current_question(game_info["game_session_id"])

    if not question_data or "error" in question_data:
        # Игра закончилась
        await show_results(update, context)
        return

    question = question_data["question"]
    variants = question_data["variants"]

    # Сохраняем текущий вопрос
    game_info["current_question"] = question

    # Создаем клавиатуру с вариантами ответов
    keyboard = []
    for variant in variants:
        keyboard.append(
            [
                InlineKeyboardButton(
                    variant["text"], callback_data=f"answer_{variant['id']}"
                )
            ]
        )

    reply_markup = InlineKeyboardMarkup(keyboard)

    question_text = f"❓ *Вопрос:*\n\n{question['text']}"

    if question.get("image_url"):
        question_text += f"\n\n🖼 Изображение: {question['image_url']}"

    await context.bot.send_message(
        chat_id=chat_id,
        text=question_text,
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка ответа игрока"""
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if chat_id not in active_games:
        await query.edit_message_text("❌ Игра не найдена.")
        return ConversationHandler.END

    game_info = active_games[chat_id]

    if user_id not in game_info["players"]:
        await query.answer("❌ Вы не участвуете в этой игре!", show_alert=True)
        return PLAYING

    variant_id = query.data.replace("answer_", "")
    player_id = game_info["players"][user_id]
    game_session_id = game_info["game_session_id"]

    # Отправляем ответ
    result = GameAPI.submit_answer(game_session_id, player_id, variant_id)

    if not result:
        await query.answer("❌ Ошибка при отправке ответа!", show_alert=True)
        return PLAYING

    result_text = result.get("result")
    is_correct = result_text == "correct"
    game_finished = result_text == "game_finished" or result.get("game_finished", False)

    if game_finished:
        await query.edit_message_text("🏁 Игра завершена! Показываю результаты...")
        await show_results(update, context)
        return ConversationHandler.END

    # Показываем результат ответа этому игроку
    await query.edit_message_text(
        "✅ Правильно!" if is_correct else "❌ Неправильно!"
    )

    # Проверяем, сдвинулся ли вопрос (все игроки ответили?)
    question_data = GameAPI.get_current_question(game_session_id)

    if not question_data or "error" in question_data:
        # Игра завершилась (race condition или последний ответ)
        await show_results(update, context)
        return ConversationHandler.END

    prev_question_id = (
        game_info["current_question"]["id"]
        if game_info.get("current_question")
        else None
    )
    new_question_id = question_data["question"]["id"]

    if prev_question_id != new_question_id:
        # Вопрос сменился — все ответили, показываем следующий
        await show_question(update, context)
    else:
        # Вопрос ещё тот же — ждём остальных игроков
        await context.bot.send_message(
            chat_id=chat_id,
            text="⏳ Ваш ответ принят! Ожидаем ответы других игроков...",
        )

    return PLAYING


async def show_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать результаты игры"""
    chat_id = update.effective_chat.id

    if chat_id not in active_games:
        return

    game_info = active_games[chat_id]

    # Получаем результаты
    results = GameAPI.get_game_results(game_info["game_session_id"])

    if not results:
        message = "❌ Не удалось загрузить результаты."
    else:
        players = results.get("players", [])
        # Сортируем по очкам
        players.sort(key=lambda p: p.get("score", 0), reverse=True)

        message = "🏆 *Результаты игры:*\n\n"

        medals = ["🥇", "🥈", "🥉"]
        for i, player in enumerate(players):
            medal = medals[i] if i < len(medals) else "👤"
            player_name = player.get("name", "Unknown")
            player_score = player.get("score", 0)
            message += f"{medal} {player_name}: {player_score} очков\n"

        message += "\n\nСпасибо за игру! 🎉\n"
        message += "Используйте /newgame чтобы сыграть еще раз!"

    await context.bot.send_message(
        chat_id=chat_id, text=message, parse_mode="Markdown"
    )

    # Удаляем игру из активных
    if chat_id in active_games:
        del active_games[chat_id]


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отменить текущую игру"""
    chat_id = update.effective_chat.id

    if chat_id in active_games:
        del active_games[chat_id]

    await update.message.reply_text(
        "❌ Игра отменена.\n\n" "Используйте /newgame чтобы начать новую игру."
    )

    return ConversationHandler.END


async def cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отменить игру через callback"""
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id

    if chat_id in active_games:
        del active_games[chat_id]

    await query.edit_message_text(
        "❌ Игра отменена.\n\n" "Используйте /newgame чтобы начать новую игру."
    )

    return ConversationHandler.END


async def upload_pack_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Начать процесс загрузки пака"""
    await update.message.reply_text(
        "📤 *Загрузка пака вопросов*\n\n"
        "Отправьте мне YAML файл с вопросами.\n\n"
        "Формат файла:\n"
        "```yaml\n"
        "title: Название пака\n"
        "questions:\n"
        "  - text: Текст вопроса\n"
        "    variants:\n"
        "      - text: Вариант 1\n"
        "      - text: Вариант 2\n"
        "        is_correct: true\n"
        "```\n\n"
        "Используйте /cancel для отмены.",
        parse_mode="Markdown",
    )
    return UPLOADING_PACK


async def handle_pack_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка загруженного файла пака"""
    if not update.message.document:
        await update.message.reply_text(
            "❌ Пожалуйста, отправьте файл.\n" "Используйте /cancel для отмены."
        )
        return UPLOADING_PACK

    document = update.message.document

    # Проверяем расширение файла
    if not (
        document.file_name.endswith(".yaml") or document.file_name.endswith(".yml")
    ):
        await update.message.reply_text(
            "❌ Пожалуйста, отправьте файл с расширением .yaml или .yml\n"
            "Используйте /cancel для отмены."
        )
        return UPLOADING_PACK

    try:
        # Скачиваем файл
        file = await context.bot.get_file(document.file_id)
        file_content = await file.download_as_bytearray()
        yaml_content = file_content.decode("utf-8")

        await update.message.reply_text("⏳ Загружаю пак на сервер...")

        # Отправляем на сервер
        result = GameAPI.upload_pack_from_yaml(yaml_content)

        if result and "id" in result:
            await update.message.reply_text(
                f"✅ *Пак успешно загружен!*\n\n"
                f"📦 Название: {result.get('title', 'Без названия')}\n"
                f"🆔 ID: `{result['id']}`\n\n"
                f"Теперь вы можете использовать этот пак в игре!",
                parse_mode="Markdown",
            )
        else:
            error_msg = (
                result.get("error", "Неизвестная ошибка")
                if result
                else "Не удалось загрузить пак"
            )
            await update.message.reply_text(
                f"❌ Ошибка при загрузке пака:\n{error_msg}\n\n"
                "Проверьте формат файла и попробуйте снова."
            )

    except Exception as e:
        logger.error(f"Error processing pack file: {e}")
        await update.message.reply_text(
            f"❌ Ошибка при обработке файла: {str(e)}\n\n"
            "Проверьте формат файла и попробуйте снова."
        )

    return ConversationHandler.END


def run_bot():
    """Запуск бота"""
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return

    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Создаем ConversationHandler для игры.
    # per_user=False: состояние отслеживается per-chat, а не per-user,
    # чтобы все пользователи чата могли участвовать в одной игре.
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("newgame", new_game)],
        states={
            SELECTING_PACK: [CallbackQueryHandler(pack_selected, pattern="^pack_")],
            WAITING_FOR_PLAYERS: [
                CallbackQueryHandler(join_game_callback, pattern="^join_game$"),
                CallbackQueryHandler(start_game_callback, pattern="^start_game$"),
                CallbackQueryHandler(cancel_callback, pattern="^cancel_game$"),
            ],
            PLAYING: [CallbackQueryHandler(answer_callback, pattern="^answer_")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_user=False,
    )

    # ConversationHandler для загрузки паков
    upload_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("uploadpack", upload_pack_command)],
        states={
            UPLOADING_PACK: [MessageHandler(filters.Document.ALL, handle_pack_file)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler)
    application.add_handler(upload_conv_handler)

    # Запускаем бота
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
