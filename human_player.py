"""
Human player input system for Texas Hold'em CLI
Supports both debug mode (see all cards) and realistic mode (hidden cards)
"""

from texasholdem import TexasHoldEm, ActionType, HandPhase
from typing import Tuple, Optional, List
from display import format_card, get_hand_phase_display
from hand_evaluator import evaluate_hand_strength, get_pot_odds
import colorama
from colorama import Fore, Back, Style


def display_human_game_state(
    game: TexasHoldEm, player_id: int, debug_mode: bool = False
):
    """
    Display game state for human player with optional debug mode

    Args:
        game: TexasHoldEm game instance
        player_id: Human player's ID
        debug_mode: If True, show all players' cards
    """
    print(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🎮 YOUR TURN - Player {player_id}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")

    # Game phase
    phase_display = get_hand_phase_display(game.hand_phase)
    print(f"📍 Phase: {phase_display}")

    # Community cards
    if game.board:
        board_str = " ".join(format_card(card) for card in game.board)
        print(f"🃏 Board: {board_str}")
    else:
        print(
            f"🃏 Board: {Fore.LIGHTBLACK_EX}(No community cards yet){Style.RESET_ALL}"
        )

    print()

    # Your hand (always visible)
    your_hand = game.get_hand(player_id)
    hand_str = " ".join(format_card(card) for card in your_hand)
    print(f"{Fore.YELLOW}{Back.BLUE} YOUR HAND: {hand_str} {Style.RESET_ALL}")

    # Hand strength analysis
    if game.board:  # Only show if there are community cards
        try:
            hand_strength = evaluate_hand_strength(game, player_id)
            strength_color = (
                Fore.GREEN
                if hand_strength > 0.7
                else Fore.YELLOW
                if hand_strength > 0.4
                else Fore.RED
            )
            print(
                f"💪 Hand Strength: {strength_color}{hand_strength:.2f}{Style.RESET_ALL}"
            )
        except:
            pass

    print()

    # Opponent information
    print(f"{Fore.LIGHTBLUE_EX}👥 OPPONENTS:{Style.RESET_ALL}")
    for i in range(game.max_players):
        if i == player_id:
            continue

        chips = game.players[i].chips
        state = game.players[i].state.name

        # State color coding
        state_color = (
            Fore.GREEN
            if state == "IN"
            else Fore.YELLOW
            if state == "TO_CALL"
            else Fore.RED
            if state == "OUT"
            else Fore.CYAN
            if state == "ALL_IN"
            else Fore.WHITE
        )

        opponent_info = (
            f"  Player {i}: {chips} chips ({state_color}{state}{Style.RESET_ALL})"
        )

        # Show cards in debug mode
        if debug_mode:
            try:
                opponent_hand = game.get_hand(i)
                if opponent_hand:
                    cards_str = " ".join(format_card(card) for card in opponent_hand)
                    opponent_info += f" - {cards_str}"
            except:
                pass

        print(opponent_info)

    print()

    # Pot information
    pot_total = sum(pot.get_total_amount() for pot in game.pots)
    print(f"💰 Pot: {Fore.GREEN}{pot_total} chips{Style.RESET_ALL}")

    # Betting information
    chips_to_call = game.chips_to_call(player_id)
    if chips_to_call > 0:
        print(f"📞 To Call: {Fore.YELLOW}{chips_to_call} chips{Style.RESET_ALL}")

        # Pot odds
        if pot_total > 0:
            pot_odds = get_pot_odds(game, player_id)
            print(f"📊 Pot Odds: {Fore.CYAN}{pot_odds:.1%}{Style.RESET_ALL}")

    your_chips = game.players[player_id].chips
    print(f"💎 Your Chips: {Fore.GREEN}{your_chips}{Style.RESET_ALL}")

    print()


def get_available_actions_display(game: TexasHoldEm, player_id: int) -> List[str]:
    """Get human-readable available actions"""
    available_actions = []
    moves = game.get_available_moves()

    for action in moves.action_types:
        if action == ActionType.FOLD:
            available_actions.append("FOLD")
        elif action == ActionType.CHECK:
            available_actions.append("CHECK")
        elif action == ActionType.CALL:
            chips_to_call = game.chips_to_call(player_id)
            available_actions.append(f"CALL ({chips_to_call})")
        elif action == ActionType.RAISE:
            # Use the actual raise range instead of misleading min_raise()
            try:
                raise_range = moves.raise_range
                if raise_range:
                    min_raise_actual = min(raise_range)
                    max_chips = game.players[player_id].chips
                    available_actions.append(f"RAISE ({min_raise_actual}-{max_chips})")
                else:
                    # Fallback if no raise range available
                    min_raise = game.min_raise()
                    max_chips = game.players[player_id].chips
                    available_actions.append(f"RAISE ({min_raise}-{max_chips})")
            except:
                # Final fallback
                min_raise = game.min_raise()
                max_chips = game.players[player_id].chips
                available_actions.append(f"RAISE ({min_raise}-{max_chips})")

    return available_actions


def get_human_action(
    game: TexasHoldEm, player_id: int, debug_mode: bool = False
) -> Tuple[ActionType, Optional[int]]:
    """
    Get action input from human player

    Args:
        game: TexasHoldEm game instance
        player_id: Human player's ID
        debug_mode: If True, show all players' cards

    Returns:
        Tuple of (ActionType, amount)
    """
    # Display game state
    display_human_game_state(game, player_id, debug_mode)

    # Get available actions
    moves = game.get_available_moves()
    available_actions = get_available_actions_display(game, player_id)

    print(f"{Fore.CYAN}🎯 Available Actions:{Style.RESET_ALL}")
    for i, action in enumerate(available_actions, 1):
        print(f"  {i}. {action}")

    print(f"\n{Fore.YELLOW}💡 Tips:{Style.RESET_ALL}")
    print("  • Type action name (fold/check/call/raise) or number")
    print("  • For RAISE, add amount: 'raise 100' or 'r 100'")
    print("  • Type 'help' for poker rules")

    while True:
        try:
            user_input = (
                input(f"\n{Fore.GREEN}Your action: {Style.RESET_ALL}").strip().lower()
            )

            if user_input == "help":
                display_poker_help()
                continue

            # Parse input
            parts = user_input.split()
            action_str = parts[0]

            # Handle numbered choices
            if action_str.isdigit():
                choice = int(action_str) - 1
                if 0 <= choice < len(available_actions):
                    action_str = available_actions[choice].split()[0].lower()
                else:
                    print(
                        f"{Fore.RED}❌ Invalid choice. Pick 1-{len(available_actions)}{Style.RESET_ALL}"
                    )
                    continue

            # Parse action
            if action_str in ["f", "fold"]:
                if ActionType.FOLD in moves.action_types:
                    return ActionType.FOLD, None
                else:
                    print(f"{Fore.RED}❌ FOLD not available{Style.RESET_ALL}")

            elif action_str in ["ch", "check"]:
                if ActionType.CHECK in moves.action_types:
                    return ActionType.CHECK, None
                else:
                    print(f"{Fore.RED}❌ CHECK not available{Style.RESET_ALL}")

            elif action_str in ["c", "call"]:
                if ActionType.CALL in moves.action_types:
                    return ActionType.CALL, None
                else:
                    print(f"{Fore.RED}❌ CALL not available{Style.RESET_ALL}")

            elif action_str in ["r", "raise"]:
                if ActionType.RAISE in moves.action_types:
                    # Get the actual valid raise range
                    try:
                        raise_range = moves.raise_range
                        if raise_range:
                            min_raise_actual = min(raise_range)
                            max_raise_actual = max(raise_range)
                        else:
                            # Fallback to old method if raise_range not available
                            min_raise_actual = game.min_raise()
                            max_raise_actual = game.players[player_id].chips
                    except:
                        # Final fallback
                        min_raise_actual = game.min_raise()
                        max_raise_actual = game.players[player_id].chips

                    # Get raise amount
                    if len(parts) > 1:
                        try:
                            amount = int(parts[1])
                        except ValueError:
                            print(
                                f"{Fore.RED}❌ Invalid raise amount. Use: 'raise 100'{Style.RESET_ALL}"
                            )
                            continue
                    else:
                        # Prompt for amount with correct range
                        amount_input = input(
                            f"Raise amount ({min_raise_actual}-{max_raise_actual}): "
                        )
                        try:
                            amount = int(amount_input)
                        except ValueError:
                            print(f"{Fore.RED}❌ Invalid amount{Style.RESET_ALL}")
                            continue

                    # Validate raise amount
                    if game.validate_move(player_id, ActionType.RAISE, amount):
                        return ActionType.RAISE, amount
                    else:
                        print(
                            f"{Fore.RED}❌ Invalid raise. Must be {min_raise_actual}-{max_raise_actual}{Style.RESET_ALL}"
                        )
                else:
                    print(f"{Fore.RED}❌ RAISE not available{Style.RESET_ALL}")
            else:
                print(
                    f"{Fore.RED}❌ Unknown action. Type: fold, check, call, raise, or help{Style.RESET_ALL}"
                )

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⚠️  Use 'fold' to exit gracefully{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")


def display_poker_help():
    """Display poker rules and help"""
    print(f"\n{Fore.CYAN}{'=' * 50}")
    print("🃏 TEXAS HOLD'EM QUICK REFERENCE")
    print(f"{'=' * 50}{Style.RESET_ALL}")

    print(f"\n{Fore.YELLOW}📋 ACTIONS:{Style.RESET_ALL}")
    print("  • FOLD - Give up your hand, lose any chips bet")
    print("  • CHECK - Pass action (only if no bet to call)")
    print("  • CALL - Match the current bet")
    print("  • RAISE - Increase the bet (others must call or fold)")

    print(f"\n{Fore.YELLOW}🎯 HAND RANKINGS (High to Low):{Style.RESET_ALL}")
    rankings = [
        "Royal Flush - A♠ K♠ Q♠ J♠ 10♠",
        "Straight Flush - 5♥ 6♥ 7♥ 8♥ 9♥",
        "Four of a Kind - K♠ K♥ K♦ K♣ A♠",
        "Full House - A♠ A♥ A♦ 8♠ 8♥",
        "Flush - A♠ J♠ 9♠ 6♠ 3♠",
        "Straight - 5♥ 6♠ 7♦ 8♣ 9♥",
        "Three of a Kind - K♠ K♥ K♦ A♠ Q♥",
        "Two Pair - A♠ A♥ 8♦ 8♠ K♥",
        "One Pair - A♠ A♥ K♦ Q♠ J♥",
        "High Card - A♠ K♥ Q♦ J♠ 9♥",
    ]

    for i, hand in enumerate(rankings, 1):
        print(f"  {i:2}. {hand}")

    print(f"\n{Fore.YELLOW}🎮 GAME FLOW:{Style.RESET_ALL}")
    print("  1. Each player gets 2 hole cards")
    print("  2. PREFLOP - Betting round")
    print("  3. FLOP - 3 community cards, betting round")
    print("  4. TURN - 1 more community card, betting round")
    print("  5. RIVER - Final community card, betting round")
    print("  6. SHOWDOWN - Best 5-card hand wins")

    print(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")
    input()


def create_human_agent(player_id: int, debug_mode: bool = False):
    """
    Create a human agent function

    Args:
        player_id: The player ID for this human
        debug_mode: If True, show all players' cards

    Returns:
        Agent function that prompts human for input
    """

    def human_agent(game: TexasHoldEm) -> Tuple[ActionType, Optional[int]]:
        return get_human_action(game, player_id, debug_mode)

    return human_agent


def display_showdown_results(game: TexasHoldEm, debug_mode: bool = True):
    """
    Display detailed showdown results for debugging and learning

    Args:
        game: TexasHoldEm game instance after hand completion
        debug_mode: If True, show all player hands
    """
    if not hasattr(game, "hand_history") or not game.hand_history:
        return

    print(f"\n{Fore.MAGENTA}{'=' * 60}")
    print("🏆 SHOWDOWN RESULTS")
    print(f"{'=' * 60}{Style.RESET_ALL}")

    # Show final board
    if game.board:
        board_str = " ".join(format_card(card) for card in game.board)
        print(f"🃏 Final Board: {board_str}")

    print()

    # Show all player hands if debug mode or if hand went to showdown
    for player_id in range(game.max_players):
        try:
            player_hand = game.get_hand(player_id)
            if not player_hand:
                continue

            chips = game.players[player_id].chips
            state = game.players[player_id].state.name

            hand_str = " ".join(format_card(card) for card in player_hand)

            # Try to get hand strength
            try:
                if game.board:
                    hand_strength = evaluate_hand_strength(game, player_id)
                    strength_str = f" (Strength: {hand_strength:.2f})"
                else:
                    strength_str = ""
            except:
                strength_str = ""

            state_color = (
                Fore.GREEN
                if state == "IN"
                else Fore.RED
                if state == "OUT"
                else Fore.YELLOW
            )

            print(f"Player {player_id}: {hand_str}{strength_str}")
            print(f"  Status: {state_color}{state}{Style.RESET_ALL}, Chips: {chips}")
            print()

        except Exception as e:
            print(
                f"Player {player_id}: {Fore.RED}(Hand not available){Style.RESET_ALL}"
            )

    print(f"{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")
    input()
