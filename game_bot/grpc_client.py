"""
gRPC client for communicating with the backend service
"""

import grpc
import logging
from typing import List, Optional

from game_bot.config import BACKEND_GRPC_ADDRESS
from game_bot.proto.handlers import cruds_pb2, cruds_pb2_grpc
from game_bot.proto.models import models_pb2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GameServiceClient:
    def __init__(self):
        self.channel = grpc.insecure_channel(BACKEND_GRPC_ADDRESS)
        self.stub = cruds_pb2_grpc.QuizServiceStub(self.channel)
        logger.info(f"Connected to backend service at {BACKEND_GRPC_ADDRESS}")

    def create_game_session(self, pack_id: str) -> Optional[models_pb2.GameSession]:
        """Create a new game session with the specified pack"""
        try:
            request = cruds_pb2.CreateGameSessionRequest(pack_id=pack_id)
            response = self.stub.CreateGameSession(request)
            return response.game_session
        except grpc.RpcError as e:
            logger.error(f"Failed to create game session: {e}")
            return None

    def get_game_session(self, game_session_id: str) -> Optional[models_pb2.GameSession]:
        """Get game session by ID"""
        try:
            request = cruds_pb2.GetGameSessionRequest(id=game_session_id)
            response = self.stub.GetGameSession(request)
            return response.game_session
        except grpc.RpcError as e:
            logger.error(f"Failed to get game session: {e}")
            return None

    def start_game_session(self, game_session_id: str) -> Optional[models_pb2.GameSession]:
        """Start a game session"""
        try:
            request = cruds_pb2.StartGameSessionRequest(id=game_session_id)
            response = self.stub.StartGameSession(request)
            return response.game_session
        except grpc.RpcError as e:
            logger.error(f"Failed to start game session: {e}")
            return None

    def end_game_session(self, game_session_id: str) -> Optional[models_pb2.GameSession]:
        """End a game session"""
        try:
            request = cruds_pb2.EndGameSessionRequest(id=game_session_id)
            response = self.stub.EndGameSession(request)
            return response.game_session
        except grpc.RpcError as e:
            logger.error(f"Failed to end game session: {e}")
            return None

    def get_all_packs(self) -> List[models_pb2.Pack]:
        """Get all available quiz packs"""
        try:
            request = cruds_pb2.GetAllPacksRequest()
            response = self.stub.GetAllPacks(request)
            return list(response.packs)
        except grpc.RpcError as e:
            logger.error(f"Failed to get packs: {e}")
            return []

    def get_questions_by_pack_id(self, pack_id: str) -> List[models_pb2.Question]:
        """Get all questions for a pack"""
        try:
            request = cruds_pb2.GetQuestionsByPackIdRequest(pack_id=pack_id)
            response = self.stub.GetQuestionsByPackId(request)
            return list(response.questions)
        except grpc.RpcError as e:
            logger.error(f"Failed to get questions: {e}")
            return []

    def get_variants_by_question_id(self, question_id: str) -> List[models_pb2.Variant]:
        """Get all variants for a question"""
        try:
            request = cruds_pb2.GetVariantsByQuestionIdRequest(question_id=question_id)
            response = self.stub.GetVariantsByQuestionId(request)
            return list(response.variants)
        except grpc.RpcError as e:
            logger.error(f"Failed to get variants: {e}")
            return []

    def add_player(self, game_session_id: str, player_name: str) -> Optional[models_pb2.Player]:
        """Add a player to a game session"""
        try:
            request = cruds_pb2.AddPlayerRequest(
                game_session_id=game_session_id,
                name=player_name
            )
            response = self.stub.AddPlayer(request)
            return response.player
        except grpc.RpcError as e:
            logger.error(f"Failed to add player: {e}")
            return None

    def get_players(self, game_session_id: str) -> List[models_pb2.Player]:
        """Get all players in a game session"""
        try:
            request = cruds_pb2.GetPlayersRequest(game_session_id=game_session_id)
            response = self.stub.GetPlayers(request)
            return list(response.players)
        except grpc.RpcError as e:
            logger.error(f"Failed to get players: {e}")
            return []

    def submit_answer(self, player_id: str, question_id: str, variant_id: str) -> Optional[cruds_pb2.SubmitAnswerResponse]:
        """Submit a player's answer"""
        try:
            request = cruds_pb2.SubmitAnswerRequest(
                player_id=player_id,
                question_id=question_id,
                variant_id=variant_id
            )
            response = self.stub.SubmitAnswer(request)
            return response
        except grpc.RpcError as e:
            logger.error(f"Failed to submit answer: {e}")
            return None

    def get_player_answers(self, player_id: str) -> List[models_pb2.PlayerAnswer]:
        """Get all answers submitted by a player"""
        try:
            request = cruds_pb2.GetPlayerAnswersRequest(player_id=player_id)
            response = self.stub.GetPlayerAnswers(request)
            return list(response.answers)
        except grpc.RpcError as e:
            logger.error(f"Failed to get player answers: {e}")
            return []

    def close(self):
        """Close the gRPC channel"""
        self.channel.close()