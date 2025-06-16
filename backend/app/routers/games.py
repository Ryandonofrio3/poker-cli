"""
🎮 Games Router
API endpoints for managing poker games, game state, and player actions
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any
from datetime import datetime
import logging

from ..models.schemas import (
    GameConfig,
    GameCreated,
    GameState,
    PlayerAction,
    ActionResult,
    APIResponse,
    GameHistory,
    PresetConfig,
    JoinGameRequest,
)
from ..core.config import PRESET_GAME_CONFIGS, APIMessages
from ..services.game_manager import GameManager

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/games", tags=["Games"])


# Import game manager instance from main module
def get_game_manager():
    """Get game manager instance"""
    from ..main import game_manager

    return game_manager


@router.post("", response_model=GameCreated, status_code=201)
async def create_game(
    config: GameConfig,
    background_tasks: BackgroundTasks,
    game_manager: GameManager = Depends(get_game_manager),
) -> GameCreated:
    """
    🎮 Create a new poker game

    Creates a new game session with the specified configuration.
    Supports preset configurations and custom agent setups.
    """
    try:
        # Apply preset if specified (BEFORE validation)
        if config.preset and config.preset in PRESET_GAME_CONFIGS:
            preset = PRESET_GAME_CONFIGS[config.preset]
            config.max_players = preset["max_players"]
            config.agents = preset["agents"]
            logger.info(
                f"🎯 Applied preset '{config.preset}' with {len(config.agents)} agents"
            )

        # Validate configuration
        if config.max_players < 2:
            raise HTTPException(400, "Game must have at least 2 players")

        if config.max_players > 9:
            raise HTTPException(400, "Game cannot have more than 9 players")

        # Check if enough agents are configured
        if len(config.agents) < 2:
            raise HTTPException(400, "Game must have at least 2 agents configured")

        # Create the game
        game_id = await game_manager.create_game(config)
        session = game_manager.get_game(game_id)

        if not session:
            raise HTTPException(500, "Failed to create game session")

        # Get initial game state
        initial_state = session.get_current_state()

        # Construct WebSocket URL
        websocket_url = f"ws://localhost:8000/ws/games/{game_id}"

        logger.info(f"🎮 Created game {game_id} via API")

        return GameCreated(
            game_id=game_id,
            message=APIMessages.GAME_CREATED,
            websocket_url=websocket_url,
            initial_state=initial_state,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating game: {e}")
        raise HTTPException(500, f"Failed to create game: {str(e)}")


@router.get("/{game_id}/state", response_model=GameState)
async def get_game_state(
    game_id: str, game_manager: GameManager = Depends(get_game_manager)
) -> GameState:
    """
    📊 Get current game state

    Returns the complete current state of the specified game,
    including player information, board cards, pot, and available actions.
    """
    session = game_manager.get_game(game_id)
    if not session:
        raise HTTPException(404, APIMessages.GAME_NOT_FOUND)

    try:
        game_state = session.get_current_state()
        logger.debug(f"📊 Retrieved state for game {game_id}")
        return game_state

    except Exception as e:
        logger.error(f"Error getting game state: {e}")
        raise HTTPException(500, f"Failed to get game state: {str(e)}")


@router.post("/{game_id}/actions", response_model=ActionResult)
async def execute_action(
    game_id: str,
    action: PlayerAction,
    game_manager: GameManager = Depends(get_game_manager),
) -> ActionResult:
    """
    🎯 Execute a player action

    Execute a poker action (fold, check, call, raise) for a player.
    This will also trigger AI players to take their turns.
    """
    try:
        result = await game_manager.execute_game_action(game_id, action)

        if result.success:
            logger.info(
                f"🎯 Executed {action.action_type} by player {action.player_id} in game {game_id}"
            )
        else:
            logger.warning(
                f"⚠️ Failed action {action.action_type} by player {action.player_id}: {result.message}"
            )

        return result

    except Exception as e:
        logger.error(f"Error executing action: {e}")
        raise HTTPException(500, f"Failed to execute action: {str(e)}")


@router.get("/{game_id}/available-actions", response_model=List[str])
async def get_available_actions(
    game_id: str, game_manager: GameManager = Depends(get_game_manager)
) -> List[str]:
    """
    🎲 Get available actions for current player

    Returns a list of valid actions that the current player can take.
    """
    session = game_manager.get_game(game_id)
    if not session:
        raise HTTPException(404, APIMessages.GAME_NOT_FOUND)

    try:
        game_state = session.get_current_state()
        actions = [action.value for action in game_state.available_actions]

        logger.debug(f"🎲 Available actions for game {game_id}: {actions}")
        return actions

    except Exception as e:
        logger.error(f"Error getting available actions: {e}")
        raise HTTPException(500, f"Failed to get available actions: {str(e)}")


@router.post("/{game_id}/join", response_model=APIResponse)
async def join_game(
    game_id: str,
    join_request: JoinGameRequest,
    game_manager: GameManager = Depends(get_game_manager),
) -> APIResponse:
    """
    🧑‍💻 Join a game as a human player

    Allows a human player to join an existing game.
    Currently returns success immediately - full implementation would handle player slots.
    """
    session = game_manager.get_game(game_id)
    if not session:
        raise HTTPException(404, APIMessages.GAME_NOT_FOUND)

    try:
        # TODO: Implement actual player joining logic
        # For now, return success (human players are configured at game creation)

        logger.info(f"🧑‍💻 Player joined game {game_id}")

        return APIResponse(
            success=True,
            message=APIMessages.PLAYER_JOINED,
            data={"game_id": game_id, "player_name": join_request.player_name},
        )

    except Exception as e:
        logger.error(f"Error joining game: {e}")
        raise HTTPException(500, f"Failed to join game: {str(e)}")


@router.delete("/{game_id}")
async def delete_game(
    game_id: str, game_manager: GameManager = Depends(get_game_manager)
) -> APIResponse:
    """
    🗑️ Delete/end a game

    Removes a game session and cleans up resources.
    """
    session = game_manager.get_game(game_id)
    if not session:
        raise HTTPException(404, APIMessages.GAME_NOT_FOUND)

    try:
        # Remove from active games
        del game_manager.active_games[game_id]

        logger.info(f"🗑️ Deleted game {game_id}")

        return APIResponse(
            success=True, message="Game deleted successfully", data={"game_id": game_id}
        )

    except Exception as e:
        logger.error(f"Error deleting game: {e}")
        raise HTTPException(500, f"Failed to delete game: {str(e)}")


@router.get("/{game_id}/history", response_model=GameHistory)
async def get_game_history(
    game_id: str, game_manager: GameManager = Depends(get_game_manager)
) -> GameHistory:
    """
    📈 Get game history and statistics

    Returns detailed history of the game including all hands played,
    actions taken, and final results.
    """
    session = game_manager.get_game(game_id)
    if not session:
        raise HTTPException(404, APIMessages.GAME_NOT_FOUND)

    try:
        # Calculate game duration
        duration = (session.updated_at - session.created_at).total_seconds() / 60

        # Get final results
        game_state = session.get_current_state()
        final_results = []

        for player in game_state.players:
            final_results.append(
                {
                    "player_id": player.player_id,
                    "agent_name": player.agent_name,
                    "final_chips": player.chips,
                    "profit_loss": player.chips - session.config.buyin,
                }
            )

        # Sort by final chips (descending)
        final_results.sort(key=lambda x: x["final_chips"], reverse=True)

        return GameHistory(
            game_id=game_id,
            total_hands=session.hand_number,
            duration_minutes=duration,
            final_results=final_results,
            hand_history=session.action_history,
        )

    except Exception as e:
        logger.error(f"Error getting game history: {e}")
        raise HTTPException(500, f"Failed to get game history: {str(e)}")


@router.get("", response_model=List[Dict[str, Any]])
async def list_active_games(
    game_manager: GameManager = Depends(get_game_manager),
) -> List[Dict[str, Any]]:
    """
    📋 List all active games

    Returns a list of all currently running games with basic information.
    """
    try:
        games = []
        for game_id, session in game_manager.active_games.items():
            game_state = session.get_current_state()

            games.append(
                {
                    "game_id": game_id,
                    "status": game_state.status.value,
                    "phase": game_state.phase.value,
                    "hand_number": game_state.hand_number,
                    "max_hands": game_state.max_hands,
                    "players": len(game_state.players),
                    "created_at": session.created_at.isoformat(),
                    "updated_at": session.updated_at.isoformat(),
                }
            )

        logger.debug(f"📋 Listed {len(games)} active games")
        return games

    except Exception as e:
        logger.error(f"Error listing games: {e}")
        raise HTTPException(500, f"Failed to list games: {str(e)}")


@router.get("/presets", response_model=List[PresetConfig])
async def get_preset_configurations() -> List[PresetConfig]:
    """
    ⚙️ Get available preset game configurations

    Returns all available preset configurations that can be used
    when creating new games.
    """
    try:
        presets = []
        for preset_id, preset_data in PRESET_GAME_CONFIGS.items():
            config = GameConfig(
                max_players=preset_data["max_players"], agents=preset_data["agents"]
            )

            presets.append(
                PresetConfig(
                    preset_id=preset_id,
                    name=preset_data["name"],
                    description=preset_data["description"],
                    config=config,
                )
            )

        logger.debug(f"⚙️ Retrieved {len(presets)} preset configurations")
        return presets

    except Exception as e:
        logger.error(f"Error getting presets: {e}")
        raise HTTPException(500, f"Failed to get presets: {str(e)}")


# Health check endpoint specific to games
@router.get("/health", response_model=Dict[str, Any])
async def games_health_check(
    game_manager: GameManager = Depends(get_game_manager),
) -> Dict[str, Any]:
    """
    🏥 Games service health check

    Returns health information specific to the games service.
    """
    try:
        total_games = len(game_manager.active_games)
        running_games = sum(
            1
            for session in game_manager.active_games.values()
            if session.status.name == "RUNNING"
        )

        return {
            "status": "healthy",
            "service": "games",
            "total_active_games": total_games,
            "running_games": running_games,
            "completed_games": total_games - running_games,
            "uptime_seconds": (
                datetime.now() - game_manager.start_time
            ).total_seconds(),
        }

    except Exception as e:
        logger.error(f"Games health check failed: {e}")
        return {"status": "unhealthy", "service": "games", "error": str(e)}
