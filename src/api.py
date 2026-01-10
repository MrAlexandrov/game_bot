"""
API клиент для взаимодействия с HTTP API игры
"""

import os
import logging
import requests

logger = logging.getLogger(__name__)

# Конфигурация
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080")


class GameAPI:
    """Класс для работы с HTTP API игры"""

    @staticmethod
    def get_all_packs():
        """Получить все доступные паки вопросов"""
        try:
            response = requests.get(f"{API_BASE_URL}/packs", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting packs: {e}")
            return []

    @staticmethod
    def create_game_session(pack_id: str):
        """Создать новую игровую сессию"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/games", json={"pack_id": pack_id}, timeout=5
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error creating game session: {e}")
            return None

    @staticmethod
    def add_player(game_session_id: str, player_name: str):
        """Добавить игрока в сессию"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/games/{game_session_id}/players",
                json={"player_name": player_name},
                timeout=5,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error adding player: {e}")
            return None

    @staticmethod
    def start_game(game_session_id: str):
        """Начать игру"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/games/{game_session_id}/start", timeout=5
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error starting game: {e}")
            return None

    @staticmethod
    def get_current_question(game_session_id: str):
        """Получить текущий вопрос"""
        try:
            response = requests.get(
                f"{API_BASE_URL}/games/{game_session_id}/state", timeout=5
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting current question: {e}")
            return None

    @staticmethod
    def submit_answer(game_session_id: str, player_id: str, variant_id: str):
        """Отправить ответ игрока"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/games/{game_session_id}/answers",
                json={"player_id": player_id, "variant_id": variant_id},
                timeout=5,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error submitting answer: {e}")
            return None

    @staticmethod
    def get_game_results(game_session_id: str):
        """Получить результаты игры"""
        try:
            response = requests.get(
                f"{API_BASE_URL}/games/{game_session_id}/results", timeout=5
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting game results: {e}")
            return None

    @staticmethod
    def upload_pack_from_yaml(yaml_content: str):
        """Загрузить пак из YAML"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/packs/yaml",
                data=yaml_content.encode("utf-8"),
                headers={"Content-Type": "text/plain; charset=utf-8"},
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error uploading pack from YAML: {e}")
            return None
