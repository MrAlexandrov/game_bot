"""
gRPC client for communicating with the backend service
"""

import grpc
import logging
import sys
import os

# Add the current directory to the path so we can import proto modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typing import List, Optional

from game_bot.config import BACKEND_GRPC_ADDRESS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GameServiceClient:
    def __init__(self):
        # Import the generated proto classes inside the constructor
        # to avoid import errors if proto files haven't been generated yet
        try:
            from proto.handlers import cruds_pb2, cruds_pb2_grpc
            from proto.models import models_pb2, game_pb2
            self.cruds_pb2 = cruds_pb2
            self.cruds_pb2_grpc = cruds_pb2_grpc
            self.models_pb2 = models_pb2
            self.game_pb2 = game_pb2
        except ImportError as e:
            logger.error("Failed to import proto modules: {}".format(e))
            logger.error("Make sure you've run the proto generation script: ./generate_proto.sh")
            raise
        except SyntaxError as e:
            logger.error("Syntax error in generated proto files: {}".format(e))
            logger.error("Try regenerating the proto files with: ./generate_proto.sh")
            raise
        
        self.channel = grpc.insecure_channel(BACKEND_GRPC_ADDRESS)
        self.stub = self.cruds_pb2_grpc.QuizServiceStub(self.channel)
        logger.info("Connected to backend service at {}".format(BACKEND_GRPC_ADDRESS))

    def create_game_session(self, pack_id: str) -> Optional[object]:
        """Create a new game session with the specified pack"""
        try:
            request = self.cruds_pb2.CreateGameSessionRequest(pack_id=pack_id)
            response = self.stub.CreateGameSession(request)
            return response.game_session
        except grpc.RpcError as e:
            logger.error("Failed to create game session: {}".format(e))
            return None
        except Exception as e:
            logger.error("Unexpected error creating game session: {}".format(e))
            return None

    def get_game_session(self, game_session_id: str) -> Optional[object]:
        """Get game session by ID"""
        try:
            request = self.cruds_pb2.GetGameSessionRequest(id=game_session_id)
            response = self.stub.GetGameSession(request)
            return response.game_session
        except grpc.RpcError as e:
            logger.error("Failed to get game session: {}".format(e))
            return None
        except Exception as e:
            logger.error("Unexpected error getting game session: {}".format(e))
            return None

    def start_game_session(self, game_session_id: str) -> Optional[object]:
        """Start a game session"""
        try:
            request = self.cruds_pb2.StartGameSessionRequest(id=game_session_id)
            response = self.stub.StartGameSession(request)
            return response.game_session
        except grpc.RpcError as e:
            logger.error("Failed to start game session: {}".format(e))
            return None
        except Exception as e:
            logger.error("Unexpected error starting game session: {}".format(e))
            return None

    def end_game_session(self, game_session_id: str) -> Optional[object]:
        """End a game session"""
        try:
            request = self.cruds_pb2.EndGameSessionRequest(id=game_session_id)
            response = self.stub.EndGameSession(request)
            return response.game_session
        except grpc.RpcError as e:
            logger.error("Failed to end game session: {}".format(e))
            return None
        except Exception as e:
            logger.error("Unexpected error ending game session: {}".format(e))
            return None

    def get_all_packs(self) -> List[object]:
        """Get all available quiz packs"""
        try:
            request = self.cruds_pb2.GetAllPacksRequest()
            response = self.stub.GetAllPacks(request)
            return list(response.packs)
        except grpc.RpcError as e:
            logger.error("Failed to get packs: {}".format(e))
            return []
        except Exception as e:
            logger.error("Unexpected error getting packs: {}".format(e))
            return []

    def get_questions_by_pack_id(self, pack_id: str) -> List[object]:
        """Get all questions for a pack"""
        try:
            request = self.cruds_pb2.GetQuestionsByPackIdRequest(pack_id=pack_id)
            response = self.stub.GetQuestionsByPackId(request)
            return list(response.questions)
        except grpc.RpcError as e:
            logger.error("Failed to get questions: {}".format(e))
            return []
        except Exception as e:
            logger.error("Unexpected error getting questions: {}".format(e))
            return []

    def get_variants_by_question_id(self, question_id: str) -> List[object]:
        """Get all variants for a question"""
        try:
            request = self.cruds_pb2.GetVariantsByQuestionIdRequest(question_id=question_id)
            response = self.stub.GetVariantsByQuestionId(request)
            return list(response.variants)
        except grpc.RpcError as e:
            logger.error("Failed to get variants: {}".format(e))
            return []
        except Exception as e:
            logger.error("Unexpected error getting variants: {}".format(e))
            return []

    def add_player(self, game_session_id: str, player_name: str) -> Optional[object]:
        """Add a player to a game session"""
        try:
            request = self.cruds_pb2.AddPlayerRequest(
                game_session_id=game_session_id,
                name=player_name
            )
            response = self.stub.AddPlayer(request)
            return response.player
        except grpc.RpcError as e:
            logger.error("Failed to add player: {}".format(e))
            return None
        except Exception as e:
            logger.error("Unexpected error adding player: {}".format(e))
            return None

    def get_players(self, game_session_id: str) -> List[object]:
        """Get all players in a game session"""
        try:
            request = self.cruds_pb2.GetPlayersRequest(game_session_id=game_session_id)
            response = self.stub.GetPlayers(request)
            return list(response.players)
        except grpc.RpcError as e:
            logger.error("Failed to get players: {}".format(e))
            return []
        except Exception as e:
            logger.error("Unexpected error getting players: {}".format(e))
            return []

    def submit_answer(self, player_id: str, question_id: str, variant_id: str) -> Optional[object]:
        """Submit a player's answer"""
        try:
            request = self.cruds_pb2.SubmitAnswerRequest(
                player_id=player_id,
                question_id=question_id,
                variant_id=variant_id
            )
            response = self.stub.SubmitAnswer(request)
            return response
        except grpc.RpcError as e:
            logger.error("Failed to submit answer: {}".format(e))
            return None
        except Exception as e:
            logger.error("Unexpected error submitting answer: {}".format(e))
            return None

    def get_player_answers(self, player_id: str) -> List[object]:
        """Get all answers submitted by a player"""
        try:
            request = self.cruds_pb2.GetPlayerAnswersRequest(player_id=player_id)
            response = self.stub.GetPlayerAnswers(request)
            return list(response.answers)
        except grpc.RpcError as e:
            logger.error("Failed to get player answers: {}".format(e))
            return []
        except Exception as e:
            logger.error("Unexpected error getting player answers: {}".format(e))
            return []

    def close(self):
        """Close the gRPC channel"""
        self.channel.close()