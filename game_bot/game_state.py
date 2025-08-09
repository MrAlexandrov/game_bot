"""
Game state management for the Telegram bot
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

# Try to import the generated proto classes
try:
    from proto.models import models_pb2
except ImportError:
    # If proto files haven't been generated yet, create a mock class
    class MockModelsPb2:
        class Question:
            pass
    models_pb2 = MockModelsPb2()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PlayerState:
    """Represents a player's state in a game session"""
    player_id: str
    player_name: str
    score: int = 0
    current_question_index: int = 0
    answers: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class GameSessionState:
    """Represents the state of a game session"""
    game_session_id: str
    pack_id: str
    state: str  # waiting, active, finished
    players: Dict[int, PlayerState] = field(default_factory=dict)  # telegram_user_id -> PlayerState
    questions: List[models_pb2.Question] = field(default_factory=list)
    current_question_index: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class GameStateManager:
    """Manages game states for multiple sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, GameSessionState] = {}  # game_session_id -> GameSessionState
        self.user_sessions: Dict[int, str] = {}  # telegram_user_id -> game_session_id
    
    def create_session(self, game_session_id: str, pack_id: str) -> GameSessionState:
        """Create a new game session state"""
        session_state = GameSessionState(
            game_session_id=game_session_id,
            pack_id=pack_id,
            state="waiting"
        )
        self.sessions[game_session_id] = session_state
        return session_state
    
    def get_session(self, game_session_id: str) -> Optional[GameSessionState]:
        """Get a game session state by ID"""
        return self.sessions.get(game_session_id)
    
    def get_session_by_user(self, telegram_user_id: int) -> Optional[GameSessionState]:
        """Get a game session state by telegram user ID"""
        game_session_id = self.user_sessions.get(telegram_user_id)
        if game_session_id:
            return self.sessions.get(game_session_id)
        return None
    
    def add_player_to_session(self, game_session_id: str, telegram_user_id: int, 
                             player_id: str, player_name: str) -> bool:
        """Add a player to a game session"""
        session = self.sessions.get(game_session_id)
        if not session:
            return False
        
        player_state = PlayerState(
            player_id=player_id,
            player_name=player_name
        )
        session.players[telegram_user_id] = player_state
        self.user_sessions[telegram_user_id] = game_session_id
        return True
    
    def get_player_state(self, game_session_id: str, telegram_user_id: int) -> Optional[PlayerState]:
        """Get a player's state in a game session"""
        session = self.sessions.get(game_session_id)
        if not session:
            return None
        return session.players.get(telegram_user_id)
    
    def set_session_questions(self, game_session_id: str, questions: List[models_pb2.Question]):
        """Set questions for a game session"""
        session = self.sessions.get(game_session_id)
        if session:
            session.questions = questions
    
    def start_session(self, game_session_id: str):
        """Start a game session"""
        session = self.sessions.get(game_session_id)
        if session:
            session.state = "active"
            session.started_at = datetime.now()
            session.current_question_index = 0
            # Reset all players to start at question 0
            for player in session.players.values():
                player.current_question_index = 0
    
    def end_session(self, game_session_id: str):
        """End a game session"""
        session = self.sessions.get(game_session_id)
        if session:
            session.state = "finished"
            session.finished_at = datetime.now()
    
    def get_current_question(self, game_session_id: str) -> Optional[models_pb2.Question]:
        """Get the current question for a game session"""
        session = self.sessions.get(game_session_id)
        if not session or not session.questions:
            return None
        
        if session.current_question_index < len(session.questions):
            return session.questions[session.current_question_index]
        return None
    
    def advance_question(self, game_session_id: str) -> bool:
        """Advance to the next question in a game session"""
        session = self.sessions.get(game_session_id)
        if not session or not session.questions:
            return False
        
        if session.current_question_index < len(session.questions) - 1:
            session.current_question_index += 1
            # Advance all players to the next question
            for player in session.players.values():
                player.current_question_index = session.current_question_index
            return True
        return False
    
    def record_answer(self, game_session_id: str, telegram_user_id: int, 
                     question_id: str, variant_id: str, is_correct: bool, points: int):
        """Record a player's answer"""
        session = self.sessions.get(game_session_id)
        if not session:
            return
        
        player_state = session.players.get(telegram_user_id)
        if not player_state:
            return
        
        # Record the answer
        answer = {
            "question_id": question_id,
            "variant_id": variant_id,
            "is_correct": is_correct,
            "points": points,
            "timestamp": datetime.now()
        }
        player_state.answers.append(answer)
        
        # Update score if correct
        if is_correct:
            player_state.score += points
    
    def get_session_results(self, game_session_id: str) -> List[Dict[str, Any]]:
        """Get the results for a game session"""
        session = self.sessions.get(game_session_id)
        if not session:
            return []
        
        results = []
        for telegram_user_id, player_state in session.players.items():
            results.append({
                "telegram_user_id": telegram_user_id,
                "player_name": player_state.player_name,
                "score": player_state.score,
                "answers": player_state.answers
            })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def remove_session(self, game_session_id: str):
        """Remove a game session and clean up user references"""
        session = self.sessions.get(game_session_id)
        if not session:
            return
        
        # Remove user references to this session
        users_to_remove = [
            user_id for user_id, session_id in self.user_sessions.items() 
            if session_id == game_session_id
        ]
        for user_id in users_to_remove:
            del self.user_sessions[user_id]
        
        # Remove the session
        del self.sessions[game_session_id]


# Global game state manager instance
game_state_manager = GameStateManager()