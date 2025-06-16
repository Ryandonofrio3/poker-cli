"""
Core game engine functions for Texas Hold'em CLI
Uses documented TexasHoldEm package methods
"""

from texasholdem import TexasHoldEm, ActionType, HandPhase
from texasholdem.agents import random_agent, call_agent
from typing import Dict, List, Callable, Tuple, Optional
import os
from datetime import datetime
import time


def create_game(
    buyin: int = 500, big_blind: int = 5, small_blind: int = 2, max_players: int = 6
) -> TexasHoldEm:
    """Create a new Texas Hold'em game using documented constructor"""
    return TexasHoldEm(
        buyin=buyin,
        big_blind=big_blind,
        small_blind=small_blind,
        max_players=max_players,
    )


def is_game_active(game: TexasHoldEm) -> bool:
    """Check if game is still running using documented method"""
    return game.is_game_running()


def is_hand_active(game: TexasHoldEm) -> bool:
    """Check if current hand is still running using documented method"""
    return game.is_hand_running()


def start_new_hand(game: TexasHoldEm) -> None:
    """Start a new hand using documented method"""
    game.start_hand()


def get_current_player(game: TexasHoldEm) -> int:
    """Get current player ID using documented property"""
    return game.current_player


def get_game_phase(game: TexasHoldEm) -> HandPhase:
    """Get current hand phase using documented property"""
    return game.hand_phase


def get_board_cards(game: TexasHoldEm) -> List:
    """Get community cards using documented property"""
    return game.board


def get_player_chips(game: TexasHoldEm, player_id: int) -> int:
    """Get player's chip count using documented property"""
    return game.players[player_id].chips


def get_player_state(game: TexasHoldEm, player_id: int) -> str:
    """Get player's state using documented property"""
    return game.players[player_id].state.name


def get_player_hand(game: TexasHoldEm, player_id: int) -> List:
    """Get player's hole cards using documented method"""
    return game.get_hand(player_id)


def get_pot_total(game: TexasHoldEm) -> int:
    """Get total pot amount using documented property"""
    return sum(pot.get_total_amount() for pot in game.pots)


def get_chips_to_call(game: TexasHoldEm, player_id: int) -> int:
    """Get chips needed to call using documented method"""
    return game.chips_to_call(player_id)


def get_available_actions(game: TexasHoldEm) -> List[ActionType]:
    """Get available actions for current player using documented method"""
    try:
        moves = game.get_available_moves()
        # Access the action_types property of MoveIterator
        return list(moves.action_types)
    except Exception as e:
        print(f"Error getting available actions: {e}")
        return []


def validate_action(
    game: TexasHoldEm, player_id: int, action: ActionType, total: Optional[int] = None
) -> bool:
    """Validate if action is legal using documented method"""
    try:
        return game.validate_move(player_id, action, total)
    except:
        return False


def execute_action(
    game: TexasHoldEm, action: ActionType, total: Optional[int] = None
) -> bool:
    """Execute player action using documented method"""
    try:
        game.take_action(action, total)
        return True
    except Exception as e:
        print(f"Action failed: {e}")
        return False


def get_min_raise_amount(game: TexasHoldEm) -> int:
    """Get minimum raise amount using documented method"""
    return game.min_raise()


def export_game_history(game: TexasHoldEm, path: str = "./game_logs") -> str:
    """Export game history using documented method"""
    # Ensure directory exists
    os.makedirs(path, exist_ok=True)

    # Create unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"poker_game_{timestamp}.pgn"
    full_path = os.path.join(path, filename)

    return game.export_history(full_path)


def clear_phantom_pot_chips(game: TexasHoldEm) -> int:
    """
    Simple fix for texasholdem package bug where pot chips are distributed correctly
    but the pot itself isn't cleared, leading to phantom chips.

    Args:
        game: TexasHoldEm game instance

    Returns:
        int: Number of phantom chips cleared
    """
    if game.is_hand_running():
        return 0  # Hand still running

    # Get phantom chips (pot should be 0 after hand completion)
    phantom_chips = sum(pot.get_total_amount() for pot in game.pots)

    if phantom_chips > 0:
        # Clear the phantom chips
        for pot in game.pots:
            pot.amount = 0
            pot.player_amounts.clear()

    return phantom_chips


def run_single_hand(game: TexasHoldEm, agent_config: Dict[int, Callable]) -> bool:
    """
    Run a single hand of poker to completion using the provided agent configuration.

    Args:
        game: TexasHoldEm game instance
        agent_config: Dictionary mapping player_id to agent function

    Returns:
        bool: True if hand completed successfully, False otherwise
    """
    if not game.is_game_running():
        return False

    try:
        # Check if there's a human player
        has_human_player = any(
            "human_agent" in str(agent_func) or hasattr(agent_func, "__closure__")
            for agent_func in agent_config.values()
        )

        # Start the hand
        game.start_hand()

        # Play until hand is complete
        max_actions = 100  # Safety limit
        action_count = 0

        while game.is_hand_running() and action_count < max_actions:
            current_player = game.current_player

            # Get agent function for current player
            if current_player not in agent_config:
                # Fallback to fold if no agent configured
                action, amount = ActionType.FOLD, None
            else:
                agent_function = agent_config[current_player]
                action, amount = agent_function(game)

            # Execute the action
            game.take_action(action, amount)
            action_count += 1

        # Clear phantom pot chips after hand completion
        phantom_chips = clear_phantom_pot_chips(game)

        # Display showdown results if there's a human player
        if has_human_player:
            from human_player import display_showdown_results

            display_showdown_results(game, debug_mode=True)

        return True

    except Exception as e:
        print(f"Error in run_single_hand: {e}")
        return False


def run_full_game(game: TexasHoldEm, agent_config: Dict, max_hands: int = 10) -> None:
    """
    Run a full poker game with multiple hands

    Args:
        game: TexasHoldEm game instance
        agent_config: Dict mapping player_id to agent functions
        max_hands: Maximum number of hands to play
    """
    from display import display_game_over, prompt_continue
    from agent_manager import get_agent_name

    print(f"🎮 Starting full game with {max_hands} hands...")
    print()

    hand_count = 0

    while is_game_active(game) and hand_count < max_hands:
        hand_count += 1
        print(f"\n{'=' * 50}")
        print(f"🂡 HAND {hand_count}/{max_hands} 🂠")
        print(f"{'=' * 50}")

        # Show current chip standings
        print("💰 Current Chip Standings:")
        for player_id in range(len(game.players)):
            chips = get_player_chips(game, player_id)
            agent_name = get_agent_name(player_id, agent_config)
            print(f"  Player {player_id} ({agent_name}): {chips} chips")
        print()

        # Run the hand
        run_single_hand(game, agent_config)

        # Check if game should continue
        if not is_game_active(game):
            print("🏁 Game ended - not enough players to continue!")
            break

        # Pause between hands (except for last hand)
        if hand_count < max_hands and is_game_active(game):
            input(f"\nPress Enter to continue to hand {hand_count + 1}...")

    # Game completed
    print(f"\n{'=' * 50}")
    print("🏆 GAME COMPLETED!")
    print(f"{'=' * 50}")

    # Final chip standings
    print("🏆 Final Results:")
    results = []
    for player_id in range(len(game.players)):
        chips = get_player_chips(game, player_id)
        agent_name = get_agent_name(player_id, agent_config)
        results.append((chips, player_id, agent_name))

    # Sort by chips (descending)
    results.sort(reverse=True)

    for rank, (chips, player_id, agent_name) in enumerate(results, 1):
        medal = (
            "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "🏅"
        )
        print(f"  {medal} #{rank}: Player {player_id} ({agent_name}) - {chips} chips")

    print(f"\nTotal hands played: {hand_count}")
    display_game_over()
