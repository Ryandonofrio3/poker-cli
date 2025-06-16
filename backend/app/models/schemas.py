"""
📊 Data models and schemas for Texas Hold'em API
Pydantic models for request/response validation and serialization
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Union, Any
from enum import Enum
from datetime import datetime
import uuid


# Enums for type safety
class ActionType(str, Enum):
    FOLD = "FOLD"
    CHECK = "CHECK"
    CALL = "CALL"
    RAISE = "RAISE"


class HandPhase(str, Enum):
    PREHAND = "PREHAND"
    PREFLOP = "PREFLOP"
    FLOP = "FLOP"
    TURN = "TURN"
    RIVER = "RIVER"
    SETTLE = "SETTLE"


class PlayerState(str, Enum):
    IN = "IN"
    OUT = "OUT"
    TO_CALL = "TO_CALL"
    ALL_IN = "ALL_IN"
    SKIP = "SKIP"


class GameStatus(str, Enum):
    WAITING = "WAITING"  # Waiting for players
    RUNNING = "RUNNING"  # Game in progress
    PAUSED = "PAUSED"  # Temporarily paused
    COMPLETED = "COMPLETED"  # Game finished
    ERROR = "ERROR"  # Error state


# Request Models
class GameConfig(BaseModel):
    """Configuration for creating a new game"""

    max_players: int = Field(
        default=6, ge=2, le=9, description="Number of players (2-9)"
    )
    buyin: int = Field(default=1000, ge=50, description="Starting chip amount")
    big_blind: int = Field(default=20, ge=2, description="Big blind amount")
    small_blind: int = Field(default=10, ge=1, description="Small blind amount")
    max_hands: Optional[int] = Field(
        default=15, ge=1, description="Maximum hands to play"
    )
    agents: Dict[int, str] = Field(
        default={}, description="Player ID to agent type mapping"
    )
    preset: Optional[str] = Field(default=None, description="Use preset configuration")
    debug_mode: bool = Field(
        default=False, description="Enable debug mode (show all cards)"
    )

    @validator("small_blind")
    def small_blind_less_than_big_blind(cls, v, values):
        if "big_blind" in values and v >= values["big_blind"]:
            raise ValueError("Small blind must be less than big blind")
        return v

    @validator("agents")
    def validate_agents(cls, v, values):
        if "max_players" in values:
            max_players = values["max_players"]
            for player_id in v.keys():
                if player_id >= max_players:
                    raise ValueError(
                        f"Player ID {player_id} exceeds max_players {max_players}"
                    )
        return v


class PlayerAction(BaseModel):
    """Player action request"""

    player_id: int = Field(..., ge=0, description="Player ID making the action")
    action_type: ActionType = Field(..., description="Type of action")
    amount: Optional[int] = Field(
        default=None, ge=0, description="Amount for RAISE action"
    )

    @validator("amount")
    def validate_amount_for_raise(cls, v, values):
        if "action_type" in values and values["action_type"] == ActionType.RAISE:
            if v is None or v <= 0:
                raise ValueError("RAISE action requires positive amount")
        return v


class JoinGameRequest(BaseModel):
    """Request to join a game as human player"""

    player_name: Optional[str] = Field(
        default="Human Player", description="Display name"
    )
    agent_type: str = Field(
        default="human", description="Agent type (should be 'human')"
    )


# Response Models
class Card(BaseModel):
    """Playing card representation"""

    rank: str = Field(..., description="Card rank (2-9, T, J, Q, K, A)")
    suit: str = Field(..., description="Card suit (♠, ♥, ♦, ♣)")
    pretty_string: str = Field(..., description="Human-readable card string")


class PlayerInfo(BaseModel):
    """Player information and state"""

    player_id: int = Field(..., description="Player ID")
    chips: int = Field(..., description="Current chip count")
    state: PlayerState = Field(..., description="Player state")
    agent_type: str = Field(..., description="Agent type")
    agent_name: str = Field(..., description="Display name for agent")
    hole_cards: Optional[List[Card]] = Field(
        default=None, description="Player's hole cards (hidden from others)"
    )
    is_current_player: bool = Field(
        default=False, description="Whether it's this player's turn"
    )
    chips_to_call: int = Field(default=0, description="Chips needed to call")
    hand_strength: Optional[float] = Field(
        default=None, description="Hand strength percentage (debug mode)"
    )


class PotInfo(BaseModel):
    """Pot information"""

    pot_id: int = Field(..., description="Pot ID")
    total_amount: int = Field(..., description="Total chips in pot")
    eligible_players: List[int] = Field(
        ..., description="Player IDs eligible for this pot"
    )


class GameState(BaseModel):
    """Complete game state"""

    game_id: str = Field(..., description="Unique game identifier")
    status: GameStatus = Field(..., description="Current game status")
    phase: HandPhase = Field(..., description="Current hand phase")
    current_player: Optional[int] = Field(
        default=None, description="Player ID whose turn it is"
    )
    hand_number: int = Field(default=0, description="Current hand number")
    max_hands: int = Field(..., description="Maximum hands to play")

    # Board and cards
    board: List[Card] = Field(default=[], description="Community cards")

    # Players
    players: List[PlayerInfo] = Field(..., description="All players in the game")

    # Pots
    pots: List[PotInfo] = Field(..., description="All pots in current hand")
    total_pot: int = Field(..., description="Total chips across all pots")

    # Available actions
    available_actions: List[ActionType] = Field(
        default=[], description="Valid actions for current player"
    )
    min_raise_amount: Optional[int] = Field(
        default=None, description="Minimum raise amount"
    )

    # Game configuration
    big_blind: int = Field(..., description="Big blind amount")
    small_blind: int = Field(..., description="Small blind amount")
    debug_mode: bool = Field(default=False, description="Debug mode enabled")

    # Timing
    created_at: datetime = Field(..., description="Game creation time")
    updated_at: datetime = Field(..., description="Last update time")


class ActionResult(BaseModel):
    """Result of a player action"""

    success: bool = Field(..., description="Whether action was successful")
    message: str = Field(..., description="Result message")
    action_type: ActionType = Field(..., description="Action that was performed")
    amount: Optional[int] = Field(default=None, description="Amount involved")
    player_id: int = Field(..., description="Player who performed action")
    new_state: Optional[GameState] = Field(
        default=None, description="Updated game state"
    )


class GameCreated(BaseModel):
    """Response when game is created"""

    game_id: str = Field(..., description="Unique game identifier")
    message: str = Field(..., description="Success message")
    websocket_url: str = Field(..., description="WebSocket URL for real-time updates")
    initial_state: GameState = Field(..., description="Initial game state")


class GameHistory(BaseModel):
    """Game history and statistics"""

    game_id: str = Field(..., description="Game identifier")
    total_hands: int = Field(..., description="Total hands played")
    duration_minutes: float = Field(..., description="Game duration in minutes")
    final_results: List[Dict[str, Any]] = Field(
        ..., description="Final player standings"
    )
    hand_history: List[Dict[str, Any]] = Field(..., description="Complete hand history")


class AvailableAgent(BaseModel):
    """Available agent type information"""

    agent_id: str = Field(..., description="Agent identifier")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="Agent description")
    category: str = Field(..., description="Agent category (AI, LLM, Human)")
    is_available: bool = Field(..., description="Whether agent is currently available")


class PresetConfig(BaseModel):
    """Preset game configuration"""

    preset_id: str = Field(..., description="Preset identifier")
    name: str = Field(..., description="Preset name")
    description: str = Field(..., description="Preset description")
    config: GameConfig = Field(..., description="Game configuration")


# WebSocket Message Models
class WebSocketMessage(BaseModel):
    """Base WebSocket message"""

    type: str = Field(..., description="Message type")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Message timestamp"
    )


class GameUpdateMessage(WebSocketMessage):
    """Game state update via WebSocket"""

    type: str = Field(default="game_update", description="Message type")
    game_state: GameState = Field(..., description="Updated game state")
    last_action: Optional[Dict[str, Any]] = Field(
        default=None, description="Last action performed"
    )


class PlayerActionMessage(WebSocketMessage):
    """Player action via WebSocket"""

    type: str = Field(default="player_action", description="Message type")
    action: PlayerAction = Field(..., description="Player action")


class ErrorMessage(WebSocketMessage):
    """Error message via WebSocket"""

    type: str = Field(default="error", description="Message type")
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Error details")


# Utility Models
class APIResponse(BaseModel):
    """Standard API response wrapper"""

    success: bool = Field(..., description="Whether request was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(default=None, description="Response data")
    errors: Optional[List[str]] = Field(default=None, description="Error details")


class HealthCheck(BaseModel):
    """Health check response"""

    status: str = Field(..., description="API status")
    version: str = Field(..., description="API version")
    active_games: int = Field(..., description="Number of active games")
    uptime_seconds: float = Field(..., description="API uptime in seconds")
    features: List[str] = Field(..., description="Available features")
