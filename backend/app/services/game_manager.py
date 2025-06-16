"""
🎮 Game Manager Service
Manages poker game sessions, WebSocket connections, and integrates with existing poker engine
"""

import asyncio
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import WebSocket

# Import existing poker system (adjust paths as needed)
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from texasholdem import (
    TexasHoldEm,
    ActionType as TexasActionType,
    HandPhase as TexasHandPhase,
)
from agent_manager import create_agent_config, get_agent_action, get_agent_name
from game_engine import (
    run_single_hand,
    get_game_phase,
    get_player_chips,
    get_player_state,
)
from hand_evaluator import evaluate_hand_strength

from ..models.schemas import (
    GameState,
    GameStatus,
    PlayerInfo,
    PotInfo,
    Card,
    ActionResult,
    ActionType,
    HandPhase,
    PlayerState,
    GameConfig,
    PlayerAction,
)
from ..core.config import settings, AVAILABLE_AGENT_TYPES, PRESET_GAME_CONFIGS

logger = logging.getLogger(__name__)


class GameSession:
    """Individual game session manager"""

    def __init__(self, game_id: str, config: GameConfig):
        self.game_id = game_id
        self.config = config
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.hand_number = 0
        self.status = GameStatus.WAITING

        # Create the underlying texasholdem game
        self.texas_game = TexasHoldEm(
            buyin=config.buyin,
            big_blind=config.big_blind,
            small_blind=config.small_blind,
            max_players=config.max_players,
        )

        # Create agent configuration using existing system
        self.agent_config = create_agent_config(config.agents)

        # WebSocket connections for real-time updates
        self.websockets: List[WebSocket] = []

        # Game history
        self.action_history: List[Dict[str, Any]] = []
        self.last_action: Optional[Dict[str, Any]] = None

        logger.info(
            f"🎮 Created game session {game_id} with {config.max_players} players"
        )

    def _convert_texas_action_to_api(self, texas_action: TexasActionType) -> ActionType:
        """Convert texasholdem ActionType to API ActionType"""
        mapping = {
            TexasActionType.FOLD: ActionType.FOLD,
            TexasActionType.CHECK: ActionType.CHECK,
            TexasActionType.CALL: ActionType.CALL,
            TexasActionType.RAISE: ActionType.RAISE,
        }
        return mapping.get(texas_action, ActionType.FOLD)

    def _convert_api_action_to_texas(self, api_action: ActionType) -> TexasActionType:
        """Convert API ActionType to texasholdem ActionType"""
        mapping = {
            ActionType.FOLD: TexasActionType.FOLD,
            ActionType.CHECK: TexasActionType.CHECK,
            ActionType.CALL: TexasActionType.CALL,
            ActionType.RAISE: TexasActionType.RAISE,
        }
        return mapping.get(api_action, TexasActionType.FOLD)

    def _convert_texas_phase_to_api(self, texas_phase: TexasHandPhase) -> HandPhase:
        """Convert texasholdem HandPhase to API HandPhase"""
        mapping = {
            TexasHandPhase.PREHAND: HandPhase.PREHAND,
            TexasHandPhase.PREFLOP: HandPhase.PREFLOP,
            TexasHandPhase.FLOP: HandPhase.FLOP,
            TexasHandPhase.TURN: HandPhase.TURN,
            TexasHandPhase.RIVER: HandPhase.RIVER,
            TexasHandPhase.SETTLE: HandPhase.SETTLE,
        }
        return mapping.get(texas_phase, HandPhase.PREHAND)

    def _convert_card_to_api(self, texas_card) -> Card:
        """Convert texasholdem Card to API Card"""
        try:
            pretty = texas_card.pretty_string
            return Card(rank=pretty[0], suit=pretty[1], pretty_string=pretty)
        except:
            return Card(rank="?", suit="?", pretty_string="??")

    def get_current_state(self) -> GameState:
        """Get current game state in API format"""
        try:
            # Get basic game info
            current_player = None
            if self.texas_game.is_hand_running():
                current_player = self.texas_game.current_player

            # Convert board cards
            board_cards = [
                self._convert_card_to_api(card) for card in self.texas_game.board
            ]

            # Build player info
            players = []
            for player_id in range(self.texas_game.max_players):
                try:
                    chips = self.texas_game.players[player_id].chips
                    state_name = self.texas_game.players[player_id].state.name

                    # Convert player state
                    player_state = PlayerState.IN  # Default
                    if state_name == "OUT":
                        player_state = PlayerState.OUT
                    elif state_name == "TO_CALL":
                        player_state = PlayerState.TO_CALL
                    elif state_name == "ALL_IN":
                        player_state = PlayerState.ALL_IN
                    elif state_name == "SKIP":
                        player_state = PlayerState.SKIP

                    # Get hole cards (only show in debug mode or for current action)
                    hole_cards = None
                    if self.config.debug_mode:
                        try:
                            texas_cards = self.texas_game.get_hand(player_id)
                            if texas_cards:
                                hole_cards = [
                                    self._convert_card_to_api(card)
                                    for card in texas_cards
                                ]
                        except:
                            pass

                    # Get hand strength for debug mode
                    hand_strength = None
                    if self.config.debug_mode and len(self.texas_game.board) >= 3:
                        try:
                            hand_strength = evaluate_hand_strength(
                                self.texas_game, player_id
                            )
                        except:
                            pass

                    # Get agent info
                    agent_type = self.config.agents.get(player_id, "unknown")
                    agent_name = get_agent_name(player_id, self.agent_config)

                    player_info = PlayerInfo(
                        player_id=player_id,
                        chips=chips,
                        state=player_state,
                        agent_type=agent_type,
                        agent_name=agent_name,
                        hole_cards=hole_cards,
                        is_current_player=(player_id == current_player),
                        chips_to_call=self.texas_game.chips_to_call(player_id)
                        if current_player == player_id
                        else 0,
                        hand_strength=hand_strength,
                    )
                    players.append(player_info)

                except Exception as e:
                    logger.error(f"Error getting player {player_id} info: {e}")
                    # Add placeholder player
                    players.append(
                        PlayerInfo(
                            player_id=player_id,
                            chips=0,
                            state=PlayerState.OUT,
                            agent_type="unknown",
                            agent_name="Unknown",
                        )
                    )

            # Get pot information
            pots = []
            total_pot = 0
            for pot_id, pot in enumerate(self.texas_game.pots):
                try:
                    pot_amount = pot.get_total_amount()
                    total_pot += pot_amount

                    pots.append(
                        PotInfo(
                            pot_id=pot_id,
                            total_amount=pot_amount,
                            eligible_players=list(
                                range(self.texas_game.max_players)
                            ),  # Simplified
                        )
                    )
                except:
                    pass

            # Get available actions for current player
            available_actions = []
            min_raise_amount = None
            if current_player is not None:
                try:
                    moves = self.texas_game.get_available_moves()
                    available_actions = [
                        self._convert_texas_action_to_api(action)
                        for action in moves.action_types
                    ]

                    if TexasActionType.RAISE in moves.action_types:
                        min_raise_amount = self.texas_game.min_raise()
                except:
                    pass

            # Determine game status
            if not self.texas_game.is_game_running():
                status = GameStatus.COMPLETED
            elif self.texas_game.is_hand_running():
                status = GameStatus.RUNNING
            else:
                status = GameStatus.WAITING

            return GameState(
                game_id=self.game_id,
                status=status,
                phase=self._convert_texas_phase_to_api(self.texas_game.hand_phase),
                current_player=current_player,
                hand_number=self.hand_number,
                max_hands=self.config.max_hands or 15,
                board=board_cards,
                players=players,
                pots=pots,
                total_pot=total_pot,
                available_actions=available_actions,
                min_raise_amount=min_raise_amount,
                big_blind=self.config.big_blind,
                small_blind=self.config.small_blind,
                debug_mode=self.config.debug_mode,
                created_at=self.created_at,
                updated_at=self.updated_at,
            )

        except Exception as e:
            logger.error(f"Error getting game state: {e}")
            # Return error state
            return GameState(
                game_id=self.game_id,
                status=GameStatus.ERROR,
                phase=HandPhase.PREHAND,
                hand_number=self.hand_number,
                max_hands=self.config.max_hands or 15,
                players=[],
                pots=[],
                total_pot=0,
                big_blind=self.config.big_blind,
                small_blind=self.config.small_blind,
                created_at=self.created_at,
                updated_at=datetime.now(),
            )

    async def execute_action(self, action: PlayerAction) -> ActionResult:
        """Execute a player action"""
        try:
            # Convert API action to texasholdem action
            texas_action = self._convert_api_action_to_texas(action.action_type)

            # Execute action using existing game engine
            self.texas_game.take_action(texas_action, action.amount)

            # Record action in history
            action_record = {
                "timestamp": datetime.now(),
                "player_id": action.player_id,
                "action_type": action.action_type.value,
                "amount": action.amount,
            }
            self.action_history.append(action_record)
            self.last_action = action_record
            self.updated_at = datetime.now()

            # Broadcast update to all connected WebSockets
            await self._broadcast_update()

            return ActionResult(
                success=True,
                message=f"Action {action.action_type.value} executed successfully",
                action_type=action.action_type,
                amount=action.amount,
                player_id=action.player_id,
                new_state=self.get_current_state(),
            )

        except Exception as e:
            logger.error(f"Error executing action: {e}")
            return ActionResult(
                success=False,
                message=f"Failed to execute action: {str(e)}",
                action_type=action.action_type,
                amount=action.amount,
                player_id=action.player_id,
            )

    async def process_ai_turns(self):
        """Process AI agent turns until human player or hand end"""
        max_iterations = 50  # Safety limit
        iterations = 0

        while self.texas_game.is_hand_running() and iterations < max_iterations:
            current_player = self.texas_game.current_player
            if current_player is None:
                break

            # Check if current player is human
            agent_type = self.config.agents.get(current_player, "unknown")
            if agent_type == "human":
                # Wait for human input via WebSocket/API
                break

            # Get AI action using existing system
            try:
                texas_action, amount = get_agent_action(
                    self.texas_game, current_player, self.agent_config
                )

                # Execute AI action
                api_action = PlayerAction(
                    player_id=current_player,
                    action_type=self._convert_texas_action_to_api(texas_action),
                    amount=amount,
                )

                await self.execute_action(api_action)
                iterations += 1

            except Exception as e:
                logger.error(
                    f"Error processing AI turn for player {current_player}: {e}"
                )
                break

        # Check if hand ended
        if not self.texas_game.is_hand_running():
            await self._handle_hand_completion()

    async def _handle_hand_completion(self):
        """Handle end of hand"""
        try:
            # Clear phantom chips (from existing system)
            from game_engine import clear_phantom_pot_chips

            clear_phantom_pot_chips(self.texas_game)

            self.hand_number += 1
            self.updated_at = datetime.now()

            # Check if game should continue
            if (
                self.hand_number >= (self.config.max_hands or 15)
                or not self.texas_game.is_game_running()
            ):
                self.status = GameStatus.COMPLETED
                logger.info(
                    f"🏁 Game {self.game_id} completed after {self.hand_number} hands"
                )
            else:
                # Start next hand
                self.texas_game.start_hand()
                logger.info(
                    f"🔄 Started hand #{self.hand_number + 1} in game {self.game_id}"
                )

            await self._broadcast_update()

        except Exception as e:
            logger.error(f"Error handling hand completion: {e}")

    async def add_websocket(self, websocket: WebSocket):
        """Add WebSocket connection"""
        self.websockets.append(websocket)
        logger.info(
            f"🔌 Added WebSocket to game {self.game_id} ({len(self.websockets)} total)"
        )

    async def remove_websocket(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.websockets:
            self.websockets.remove(websocket)
            logger.info(
                f"🔌 Removed WebSocket from game {self.game_id} ({len(self.websockets)} total)"
            )

    async def _broadcast_update(self):
        """Broadcast game state update to all connected WebSockets"""
        if not self.websockets:
            return

        game_state = self.get_current_state()
        message = {
            "type": "game_update",
            "game_state": game_state.dict(),
            "last_action": self.last_action,
            "timestamp": datetime.now().isoformat(),
        }

        # Send to all connected WebSockets
        disconnected = []
        for websocket in self.websockets:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send WebSocket message: {e}")
                disconnected.append(websocket)

        # Remove disconnected WebSockets
        for websocket in disconnected:
            await self.remove_websocket(websocket)


class GameManager:
    """Main game manager handling all game sessions"""

    def __init__(self):
        self.active_games: Dict[str, GameSession] = {}
        self.start_time = datetime.now()
        logger.info("🎮 Game Manager initialized")

    async def create_game(self, config: GameConfig) -> str:
        """Create a new game session"""
        # Generate unique game ID
        game_id = str(uuid.uuid4())

        # Create game session
        session = GameSession(game_id, config)
        self.active_games[game_id] = session

        # Start the first hand if we have enough agents
        if len(config.agents) >= 2:
            session.texas_game.start_hand()
            session.status = GameStatus.RUNNING

            # Process AI turns asynchronously
            asyncio.create_task(session.process_ai_turns())

        logger.info(f"🎮 Created game {game_id} with {config.max_players} players")
        return game_id

    def get_game(self, game_id: str) -> Optional[GameSession]:
        """Get game session by ID"""
        return self.active_games.get(game_id)

    async def execute_game_action(
        self, game_id: str, action: PlayerAction
    ) -> ActionResult:
        """Execute action in a game"""
        session = self.get_game(game_id)
        if not session:
            return ActionResult(
                success=False,
                message="Game not found",
                action_type=action.action_type,
                player_id=action.player_id,
            )

        result = await session.execute_action(action)

        # Continue with AI turns after human action
        if result.success:
            asyncio.create_task(session.process_ai_turns())

        return result

    async def add_websocket(self, game_id: str, websocket: WebSocket) -> bool:
        """Add WebSocket to game session"""
        session = self.get_game(game_id)
        if not session:
            return False

        await session.add_websocket(websocket)
        return True

    async def remove_websocket(self, game_id: str, websocket: WebSocket):
        """Remove WebSocket from game session"""
        session = self.get_game(game_id)
        if session:
            await session.remove_websocket(websocket)

    async def handle_websocket_action(
        self, game_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle WebSocket action message"""
        try:
            action_data = data.get("action", {})
            action = PlayerAction(**action_data)
            result = await self.execute_game_action(game_id, action)

            return {
                "type": "action_result",
                "success": result.success,
                "message": result.message,
                "game_state": result.new_state.dict() if result.new_state else None,
            }

        except Exception as e:
            logger.error(f"Error handling WebSocket action: {e}")
            return {"type": "error", "message": f"Failed to process action: {str(e)}"}

    async def cleanup_inactive_games(self):
        """Clean up inactive games"""
        cutoff_time = datetime.now() - timedelta(
            seconds=settings.MAX_INACTIVE_TIME_SECONDS
        )
        inactive_games = [
            game_id
            for game_id, session in self.active_games.items()
            if session.updated_at < cutoff_time
        ]

        for game_id in inactive_games:
            logger.info(f"🧹 Cleaning up inactive game {game_id}")
            del self.active_games[game_id]

    async def cleanup_all_games(self):
        """Clean up all games on shutdown"""
        logger.info(f"🧹 Cleaning up {len(self.active_games)} active games")
        self.active_games.clear()
