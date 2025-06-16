"""
Main CLI interface for Texas Hold'em with AI agents
"""

from texasholdem import TexasHoldEm
from display import display_welcome, display_menu_header, display_error
from agent_manager import (
    create_agent_config,
    create_custom_showcase_config,
    create_llm_showcase_config,
    create_llm_vs_ai_config,
    create_gpt_4_1_showcase_config,
    create_premium_vs_free_config,
    create_test_config,
    create_balanced_config,
    create_human_vs_ai_config,
    create_human_vs_ai_debug_config,
    create_human_vs_llm_config,
    create_human_vs_llm_debug_config,
    create_human_heads_up_config,
    create_human_heads_up_debug_config,
    display_agent_config,
    list_available_agents,
    LLM_AVAILABLE,
)
from game_engine import run_single_hand, run_full_game


def display_main_menu():
    """Display the main menu options"""
    display_menu_header("TEXAS HOLD'EM CLI - MAIN MENU")

    print("🎮 HUMAN PLAYER MODES:")
    print("1. 🧑‍💻 Human vs AI (Realistic)")
    print("2. 🔍 Human vs AI (Debug - See All Cards)")
    print("3. 🧑‍💻🤖 Human vs LLM (Realistic)")
    print("4. 🔍🤖 Human vs LLM (Debug - See All Cards)")
    print("5. 🎯 Human Heads-Up vs AI (Realistic)")
    print("6. 🔍🎯 Human Heads-Up vs AI (Debug)")

    print("\n🤖 AI-ONLY MODES:")
    print("7. 🎲 Quick Test Game (2 players)")
    print("8. 🎯 Balanced 6-Player Game")
    print("9. 🤖 Custom Agent Showcase")

    if LLM_AVAILABLE:
        print("10. 🦙💎 LLM Agent Showcase (Mixed)")
        print("11. ⚔️  LLM vs Traditional AI Battle")
        print("12. 🤖✨ gpt-4.1 Premium Showcase")
        print("13. 💰🆚 Premium vs Free LLM Battle")
    else:
        print("10. ❌ LLM Agents (Not Available)")
        print("11. ❌ LLM vs AI (Not Available)")
        print("12. ❌ gpt-4.1 Showcase (Not Available)")
        print("13. ❌ Premium vs Free (Not Available)")

    print("\n🛠️ UTILITIES:")
    print("14. 📋 List Available Agents")
    print("15. 🎮 Custom Game Configuration")
    print("0. 🚪 Exit")
    print()


def get_user_choice() -> str:
    """Get user menu choice"""
    try:
        choice = input("Enter your choice (0-15): ").strip()
        return choice
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
        exit(0)


def run_human_vs_ai():
    """Run human vs AI game (realistic mode)"""
    print("🧑‍💻 Starting Human vs AI Game (Realistic Mode)...")
    print("You'll play against 5 AI opponents with different personalities.")
    print("Opponent cards are hidden - just like real poker!")

    agent_config = create_human_vs_ai_config()
    display_agent_config(agent_config)

    game = TexasHoldEm(buyin=1000, big_blind=20, small_blind=10, max_players=6)
    run_full_game(game, agent_config, max_hands=10)


def run_human_vs_ai_debug():
    """Run human vs AI game (debug mode)"""
    print("🔍 Starting Human vs AI Game (Debug Mode)...")
    print("You can see all opponent cards - perfect for learning and testing!")

    agent_config = create_human_vs_ai_debug_config()
    display_agent_config(agent_config)

    game = TexasHoldEm(buyin=1000, big_blind=20, small_blind=10, max_players=6)
    run_full_game(game, agent_config, max_hands=10)


def run_human_vs_llm():
    """Run human vs LLM game (realistic mode)"""
    if not LLM_AVAILABLE:
        display_error(
            "LLM agents are not available. Check your API key and connection."
        )
        return

    print("🧑‍💻🤖 Starting Human vs LLM Game (Realistic Mode)...")
    print("You'll play against 5 LLM opponents with strategic reasoning!")
    print("Watch their thought processes as they make decisions.")

    agent_config = create_human_vs_llm_config()
    display_agent_config(agent_config)

    game = TexasHoldEm(buyin=1500, big_blind=30, small_blind=15, max_players=6)
    run_full_game(game, agent_config, max_hands=8)


def run_human_vs_llm_debug():
    """Run human vs LLM game (debug mode)"""
    if not LLM_AVAILABLE:
        display_error(
            "LLM agents are not available. Check your API key and connection."
        )
        return

    print("🔍🤖 Starting Human vs LLM Game (Debug Mode)...")
    print("You can see all opponent cards AND their strategic reasoning!")
    print("Perfect for understanding LLM poker strategies.")

    agent_config = create_human_vs_llm_debug_config()
    display_agent_config(agent_config)

    game = TexasHoldEm(buyin=1500, big_blind=30, small_blind=15, max_players=6)
    run_full_game(game, agent_config, max_hands=8)


def run_human_heads_up():
    """Run human heads-up vs AI (realistic mode)"""
    print("🎯 Starting Human Heads-Up Game (Realistic Mode)...")
    print("One-on-one poker against a strong AI opponent!")

    agent_config = create_human_heads_up_config()
    display_agent_config(agent_config)

    game = TexasHoldEm(buyin=1000, big_blind=20, small_blind=10, max_players=2)
    run_full_game(game, agent_config, max_hands=15)


def run_human_heads_up_debug():
    """Run human heads-up vs AI (debug mode)"""
    print("🔍🎯 Starting Human Heads-Up Game (Debug Mode)...")
    print("One-on-one poker with opponent cards visible - great for learning!")

    agent_config = create_human_heads_up_debug_config()
    display_agent_config(agent_config)

    game = TexasHoldEm(buyin=1000, big_blind=20, small_blind=10, max_players=2)
    run_full_game(game, agent_config, max_hands=15)


def run_quick_test():
    """Run a quick 2-player test game"""
    print("🎲 Starting Quick Test Game...")
    agent_config = create_test_config()
    display_agent_config(agent_config)

    game = TexasHoldEm(buyin=1000, big_blind=20, small_blind=10, max_players=2)
    run_single_hand(game, agent_config)


def run_balanced_game():
    """Run a balanced 6-player game"""
    print("🎯 Starting Balanced 6-Player Game...")
    agent_config = create_balanced_config()
    display_agent_config(agent_config)

    game = TexasHoldEm(buyin=1000, big_blind=20, small_blind=10, max_players=6)
    run_full_game(game, agent_config, max_hands=10)


def run_custom_showcase():
    """Run custom agent showcase"""
    print("🤖 Starting Custom Agent Showcase...")
    agent_config = create_custom_showcase_config()
    display_agent_config(agent_config)

    game = TexasHoldEm(buyin=1000, big_blind=20, small_blind=10, max_players=6)
    run_full_game(game, agent_config, max_hands=15)


def run_llm_showcase():
    """Run LLM agent showcase"""
    if not LLM_AVAILABLE:
        display_error(
            "LLM agents are not available. Check your API key and connection."
        )
        return

    print("🦙💎 Starting LLM Agent Showcase...")
    print("This will feature 6 different LLM agents with unique personalities!")
    agent_config = create_llm_showcase_config()
    display_agent_config(agent_config)

    game = TexasHoldEm(buyin=1500, big_blind=30, small_blind=15, max_players=6)
    run_full_game(game, agent_config, max_hands=12)


def run_llm_vs_ai():
    """Run LLM vs traditional AI battle"""
    if not LLM_AVAILABLE:
        display_error(
            "LLM agents are not available. Check your API key and connection."
        )
        return

    print("⚔️  Starting LLM vs Traditional AI Battle...")
    print("3 LLM agents vs 3 traditional AI agents!")
    agent_config = create_llm_vs_ai_config()
    display_agent_config(agent_config)

    game = TexasHoldEm(buyin=1200, big_blind=25, small_blind=12, max_players=6)
    run_full_game(game, agent_config, max_hands=20)


def run_gpt_4_1_showcase():
    """Run gpt-4.1 premium agent showcase"""
    if not LLM_AVAILABLE:
        display_error(
            "LLM agents are not available. Check your API key and connection."
        )
        return

    print("🤖✨ Starting gpt-4.1 Premium Showcase...")
    print("This will feature 5 different gpt-4.1 agents + 1 Llama for comparison!")
    print(
        "Note: gpt-4.1 agents use premium API calls and have the best structured output support."
    )
    agent_config = create_gpt_4_1_showcase_config()
    display_agent_config(agent_config)

    game = TexasHoldEm(buyin=2000, big_blind=40, small_blind=20, max_players=6)
    run_full_game(game, agent_config, max_hands=8)


def run_premium_vs_free():
    """Run premium vs free LLM battle"""
    if not LLM_AVAILABLE:
        display_error(
            "LLM agents are not available. Check your API key and connection."
        )
        return

    print("💰🆚 Starting Premium vs Free LLM Battle...")
    print("3 Premium gpt-4.1 agents vs 3 Free agents (Llama + Gemma)!")
    print("Let's see if premium models have a poker advantage!")
    agent_config = create_premium_vs_free_config()
    display_agent_config(agent_config)

    game = TexasHoldEm(buyin=1500, big_blind=30, small_blind=15, max_players=6)
    run_full_game(game, agent_config, max_hands=15)


def run_custom_configuration():
    """Allow user to create custom game configuration"""
    print("🎮 Custom Game Configuration")
    print("Create your own agent lineup!")
    print()

    list_available_agents()

    num_players = int(input("Number of players (2-6): "))
    if num_players < 2 or num_players > 6:
        print("Invalid number of players. Using 6.")
        num_players = 6

    agent_assignments = {}
    for i in range(num_players):
        agent_name = input(f"Agent for Player {i}: ").strip().lower()
        agent_assignments[i] = agent_name

    agent_config = create_agent_config(agent_assignments)
    display_agent_config(agent_config)

    buyin = int(input("Buy-in amount (default 1000): ") or "1000")
    big_blind = int(input("Big blind (default 20): ") or "20")
    small_blind = big_blind // 2

    game = TexasHoldEm(
        buyin=buyin,
        big_blind=big_blind,
        small_blind=small_blind,
        max_players=num_players,
    )
    run_full_game(game, agent_config, max_hands=15)


def main():
    """Main CLI loop"""
    display_welcome()

    # Check LLM availability on startup
    if LLM_AVAILABLE:
        print("✅ LLM agents are available and ready!")
    else:
        print("⚠️  LLM agents are not available. Check your .env file and API key.")
    print()

    while True:
        display_main_menu()
        choice = get_user_choice()

        try:
            if choice == "0":
                print("Thanks for playing! 👋")
                break
            elif choice == "1":
                run_human_vs_ai()
            elif choice == "2":
                run_human_vs_ai_debug()
            elif choice == "3":
                run_human_vs_llm()
            elif choice == "4":
                run_human_vs_llm_debug()
            elif choice == "5":
                run_human_heads_up()
            elif choice == "6":
                run_human_heads_up_debug()
            elif choice == "7":
                run_quick_test()
            elif choice == "8":
                run_balanced_game()
            elif choice == "9":
                run_custom_showcase()
            elif choice == "10":
                run_llm_showcase()
            elif choice == "11":
                run_llm_vs_ai()
            elif choice == "12":
                run_gpt_4_1_showcase()
            elif choice == "13":
                run_premium_vs_free()
            elif choice == "14":
                list_available_agents()
            elif choice == "15":
                run_custom_configuration()
            else:
                display_error("Invalid choice. Please select 0-15.")

        except KeyboardInterrupt:
            print("\n\nGame interrupted. Returning to main menu...")
        except Exception as e:
            display_error(f"An error occurred: {e}")

        if choice != "0":
            input("\nPress Enter to return to main menu...")


if __name__ == "__main__":
    main()
