"""
Debug script for LLM agents - isolate and test individual agents
"""

from texasholdem import TexasHoldEm, ActionType
from llm_agents import create_balanced_gpt_4_1, create_balanced_llama
from llm_client import OpenRouterClient, create_llm_client
from prompt_builder import create_personality_prompt
import traceback


def test_llm_client_directly():
    """Test the LLM client directly"""
    print("🧪 Testing LLM Client Directly...")
    print("=" * 50)

    try:
        client = create_llm_client()
        print("✅ LLM client created successfully")

        # Test GPT-4.1 directly
        print("\n🔍 Testing GPT-4.1 Mini directly...")
        test_prompt = "You have pocket aces (A♠ A♥) in early position preflop. The blinds are 10/20. What should you do?"

        try:
            decision = client.make_poker_decision("openai/gpt-4.1-mini", test_prompt)
            print(f"✅ GPT-4.1 Mini SUCCESS: {decision}")
        except Exception as e:
            print(f"❌ GPT-4.1 Mini FAILED: {e}")
            print(f"Full traceback: {traceback.format_exc()}")

        # Test Llama directly
        print("\n🔍 Testing Llama directly...")
        try:
            decision = client.make_poker_decision(
                "meta-llama/llama-3.1-8b-instruct", test_prompt
            )
            print(f"✅ Llama SUCCESS: {decision}")
        except Exception as e:
            print(f"❌ Llama FAILED: {e}")
            print(f"Full traceback: {traceback.format_exc()}")

    except Exception as e:
        print(f"❌ Failed to create LLM client: {e}")
        print(f"Full traceback: {traceback.format_exc()}")


def test_agent_creation():
    """Test creating LLM agents"""
    print("\n🧪 Testing Agent Creation...")
    print("=" * 50)

    try:
        print("🔍 Creating GPT-4.1 agent...")
        gpt_agent = create_balanced_gpt_4_1()
        print("✅ GPT-4.1 agent created successfully")
        print(f"Agent type: {type(gpt_agent)}")
    except Exception as e:
        print(f"❌ Failed to create GPT-4.1 agent: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
        gpt_agent = None

    try:
        print("\n🔍 Creating Llama agent...")
        llama_agent = create_balanced_llama()
        print("✅ Llama agent created successfully")
        print(f"Agent type: {type(llama_agent)}")
    except Exception as e:
        print(f"❌ Failed to create Llama agent: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
        llama_agent = None

    return gpt_agent, llama_agent


def test_agent_in_game(agent_func, agent_name):
    """Test an agent in a real game scenario"""
    print(f"\n🎮 Testing {agent_name} in Game Scenario...")
    print("=" * 50)

    if agent_func is None:
        print(f"❌ {agent_name} agent is None, skipping test")
        return

    try:
        # Create a simple 2-player game
        game = TexasHoldEm(buyin=1000, big_blind=20, small_blind=10, max_players=2)
        game.start_hand()

        print(f"🎯 Game state: {game.hand_phase}")
        print(f"🎯 Current player: {game.current_player}")
        print(f"🎯 Available moves: {list(game.get_available_moves().action_types)}")

        # Get action from agent
        print(f"🤖 Getting action from {agent_name}...")
        action, amount = agent_func(game)
        print(f"✅ {agent_name} chose: {action} {amount}")

        # Validate the action
        moves = game.get_available_moves()
        if action in moves.action_types:
            print(f"✅ Action is valid!")
        else:
            print(f"❌ Action is INVALID! Available: {list(moves.action_types)}")

    except Exception as e:
        print(f"❌ {agent_name} failed in game: {e}")
        print(f"Full traceback: {traceback.format_exc()}")


def test_prompt_generation():
    """Test prompt generation for LLM agents"""
    print("\n🧪 Testing Prompt Generation...")
    print("=" * 50)

    try:
        # Create a simple game for prompt testing
        game = TexasHoldEm(buyin=1000, big_blind=20, small_blind=10, max_players=2)
        game.start_hand()

        player_id = game.current_player
        print(f"🎯 Testing prompt for Player {player_id}")

        # Generate prompt
        prompt = create_personality_prompt(game, player_id, "balanced")
        print(f"✅ Prompt generated successfully!")
        print(f"Prompt length: {len(prompt)} characters")
        print(f"First 200 chars: {prompt[:200]}...")

    except Exception as e:
        print(f"❌ Prompt generation failed: {e}")
        print(f"Full traceback: {traceback.format_exc()}")


def main():
    """Run all debug tests"""
    print("🚀 LLM AGENT DEBUG SESSION")
    print("=" * 60)

    # Test 1: LLM Client directly
    test_llm_client_directly()

    # Test 2: Agent creation
    gpt_agent, llama_agent = test_agent_creation()

    # Test 3: Prompt generation
    test_prompt_generation()

    # Test 4: Agents in game
    test_agent_in_game(gpt_agent, "GPT-4.1")
    test_agent_in_game(llama_agent, "Llama")

    print("\n" + "=" * 60)
    print("🏁 DEBUG SESSION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
