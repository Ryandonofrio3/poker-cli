"""
Debug the actual game configuration to see why agents aren't being assigned properly
"""

from texasholdem import TexasHoldEm
from agent_manager import (
    create_gpt_4_1_showcase_config,
    get_agent_action,
    get_agent_name,
    display_agent_config,
    LLM_AVAILABLE,
)


def test_game_config():
    """Test the actual game configuration"""
    print("🧪 Testing Game Configuration...")
    print("=" * 50)

    print(f"LLM_AVAILABLE: {LLM_AVAILABLE}")

    # Create the config that main.py uses
    config = create_gpt_4_1_showcase_config()

    print("Agent Configuration:")
    display_agent_config(config)

    # Test each player assignment
    for player_id in config:
        agent_name = get_agent_name(player_id, config)
        print(f"Player {player_id}: {agent_name}")

    return config


def test_single_action():
    """Test getting a single action from the game"""
    print("\n🎮 Testing Single Action...")
    print("=" * 50)

    # Create game
    game = TexasHoldEm(buyin=2000, big_blind=40, small_blind=20, max_players=6)
    game.start_hand()

    # Get config
    config = create_gpt_4_1_showcase_config()

    # Test the current player
    current_player = game.current_player
    print(f"Current player: {current_player}")

    # Get agent name
    agent_name = get_agent_name(current_player, config)
    print(f"Agent name: {agent_name}")

    # Show game state
    print(f"Game phase: {game.hand_phase}")
    print(f"Available moves: {list(game.get_available_moves().action_types)}")

    # Get action
    print(f"\nGetting action for Player {current_player}...")
    action, amount = get_agent_action(game, current_player, config)
    print(f"Action result: {action} {amount}")


def main():
    """Main debug function"""
    print("🚀 GAME CONFIG DEBUG SESSION")
    print("=" * 60)

    test_game_config()
    test_single_action()

    print("\n" + "=" * 60)
    print("🏁 DEBUG COMPLETE")


if __name__ == "__main__":
    main()
