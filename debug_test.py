"""
Debug test to isolate the aggressive agent issue
"""

from texasholdem import TexasHoldEm
from texasholdem.agents import random_agent, call_agent
from agent_manager import get_aggressive_random_agent_action


def test_agents():
    # Create a simple game
    game = TexasHoldEm(buyin=500, big_blind=10, small_blind=5, max_players=6)
    game.start_hand()

    print("=== TESTING AGENTS ===")
    print(f"Current player: {game.current_player}")
    print(f"Game phase: {game.hand_phase}")

    # Test call agent (should work)
    print("\n1. Testing call_agent...")
    try:
        action, total = call_agent(game)
        print(f"✓ call_agent worked: {action.name}, {total}")
    except Exception as e:
        print(f"✗ call_agent failed: {e}")

    # Test random agent with no_fold=False (should work)
    print("\n2. Testing random_agent(no_fold=False)...")
    try:
        action, total = random_agent(game, no_fold=False)
        print(f"✓ random_agent(no_fold=False) worked: {action.name}, {total}")
    except Exception as e:
        print(f"✗ random_agent(no_fold=False) failed: {e}")

    # Test random agent with no_fold=True (this is failing)
    print("\n3. Testing random_agent(no_fold=True)...")
    try:
        action, total = random_agent(game, no_fold=True)
        print(f"✓ random_agent(no_fold=True) worked: {action.name}, {total}")
    except Exception as e:
        print(f"✗ random_agent(no_fold=True) failed: {e}")

    # Test our custom aggressive agent workaround
    print("\n4. Testing our custom aggressive agent...")
    try:
        action, total = get_aggressive_random_agent_action(game)
        print(f"✓ Custom aggressive agent worked: {action.name}, {total}")
    except Exception as e:
        print(f"✗ Custom aggressive agent failed: {e}")
        import traceback

        traceback.print_exc()

    # Test MoveIterator directly
    print("\n5. Testing MoveIterator directly...")
    try:
        moves = game.get_available_moves()
        print(f"MoveIterator type: {type(moves)}")
        print(f"Available action types: {moves.action_types}")
        print(f"Action types type: {type(moves.action_types)}")

        # Test sample method
        sampled = moves.sample()
        print(f"Sampled move: {sampled}")
        print(f"Sampled move type: {type(sampled)}")

    except Exception as e:
        print(f"✗ MoveIterator test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_agents()
