"""
Display functions for Texas Hold'em CLI
Clean, colorful game state visualization
"""

import os
from colorama import Fore, Back, Style, init
from texasholdem import TexasHoldEm, HandPhase
from game_engine import (
    get_current_player,
    get_game_phase,
    get_board_cards,
    get_player_chips,
    get_player_state,
    get_player_hand,
    get_pot_total,
    get_chips_to_call,
    get_available_actions,
)

# Initialize colorama
init(autoreset=True)


def clear_screen():
    """Clear the terminal screen"""
    os.system("cls" if os.name == "nt" else "clear")


def format_card(card) -> str:
    """Format a card for display with colors"""
    if not card:
        return "??"

    card_str = card.pretty_string
    # Color red suits red, black suits white
    if "♥" in card_str or "♦" in card_str:
        return Fore.RED + card_str + Style.RESET_ALL
    else:
        return Fore.WHITE + card_str + Style.RESET_ALL


def format_cards(cards) -> str:
    """Format a list of cards for display"""
    if not cards:
        return "No cards"
    return " ".join(format_card(card) for card in cards)


def get_hand_phase_display(phase: HandPhase) -> str:
    """Get a formatted display string for the hand phase"""
    phase_colors = {
        HandPhase.PREHAND: Fore.YELLOW,
        HandPhase.PREFLOP: Fore.GREEN,
        HandPhase.FLOP: Fore.BLUE,
        HandPhase.TURN: Fore.MAGENTA,
        HandPhase.RIVER: Fore.RED,
        HandPhase.SETTLE: Fore.CYAN,
    }

    color = phase_colors.get(phase, Fore.WHITE)
    return f"{color}{phase.name}{Style.RESET_ALL}"


def display_welcome():
    """Display welcome message"""
    clear_screen()
    print(f"{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.CYAN}🂡  TEXAS HOLD'EM POKER BATTLE  🂠")
    print(f"{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.GREEN}Welcome to the ultimate poker AI showdown!")
    print(
        f"{Fore.WHITE}Watch different AI agents battle it out with unique strategies."
    )
    print()


def display_menu_header(title: str):
    """Display a menu header"""
    print(f"{Fore.CYAN}{'=' * 50}")
    print(f"{Fore.CYAN}{title}")
    print(f"{Fore.CYAN}{'=' * 50}")
    print()


def display_error(message: str):
    """Display an error message"""
    print(f"{Fore.RED}❌ Error: {message}{Style.RESET_ALL}")
    print()


def display_header():
    """Display the game header"""
    print(Fore.CYAN + "=" * 60)
    print(Fore.CYAN + "🂡  TEXAS HOLD'EM CLI - LLM POKER BATTLE  🂠")
    print(Fore.CYAN + "=" * 60)
    print()


def display_game_phase(game: TexasHoldEm):
    """Display current game phase"""
    phase = get_game_phase(game)
    phase_colors = {
        HandPhase.PREHAND: Fore.YELLOW,
        HandPhase.PREFLOP: Fore.GREEN,
        HandPhase.FLOP: Fore.BLUE,
        HandPhase.TURN: Fore.MAGENTA,
        HandPhase.RIVER: Fore.RED,
        HandPhase.SETTLE: Fore.CYAN,
    }

    color = phase_colors.get(phase, Fore.WHITE)
    print(f"{color}Phase: {phase.name}{Style.RESET_ALL}")
    print()


def display_board(game: TexasHoldEm):
    """Display community cards"""
    board = get_board_cards(game)
    phase = get_game_phase(game)

    print(Fore.YELLOW + "BOARD:")
    if not board:
        print("  No community cards yet")
    else:
        print(f"  {format_cards(board)}")
    print()


def display_pot(game: TexasHoldEm):
    """Display pot information"""
    pot_total = get_pot_total(game)
    print(f"{Fore.GREEN}💰 POT: {pot_total} chips{Style.RESET_ALL}")
    print()


def display_player_info(game: TexasHoldEm, player_id: int, show_cards: bool = False):
    """Display information for a single player"""
    chips = get_player_chips(game, player_id)
    state = get_player_state(game, player_id)
    current = get_current_player(game)

    # Highlight current player
    if player_id == current:
        prefix = f"{Back.YELLOW}{Fore.BLACK}► PLAYER {player_id}{Style.RESET_ALL}"
    else:
        prefix = f"  Player {player_id}"

    # Color code player state
    state_colors = {
        "IN": Fore.GREEN,
        "OUT": Fore.RED,
        "TO_CALL": Fore.YELLOW,
        "ALL_IN": Fore.MAGENTA,
        "SKIP": Fore.CYAN,
    }
    state_color = state_colors.get(state, Fore.WHITE)

    print(f"{prefix} | {chips} chips | {state_color}{state}{Style.RESET_ALL}")

    # Show cards if requested
    if show_cards:
        try:
            hand = get_player_hand(game, player_id)
            if hand:
                print(f"    Cards: {format_cards(hand)}")
        except:
            print("    Cards: Hidden")

    # Show chips to call for current player
    if player_id == current:
        try:
            to_call = get_chips_to_call(game, player_id)
            if to_call > 0:
                print(f"    {Fore.YELLOW}To call: {to_call} chips{Style.RESET_ALL}")
        except:
            pass


def display_all_players(game: TexasHoldEm, show_cards: bool = False):
    """Display all players"""
    print(Fore.CYAN + "PLAYERS:")
    for i in range(len(game.players)):
        display_player_info(game, i, show_cards)
    print()


def display_available_actions(game: TexasHoldEm):
    """Display available actions for current player"""
    try:
        moves = game.get_available_moves()  # Get the MoveIterator object
        current = get_current_player(game)

        print(f"{Fore.CYAN}Available actions for Player {current}:")
        # Access action_types property of MoveIterator
        for action in moves.action_types:
            print(f"  • {action.name}")
        print()
    except Exception as e:
        print(f"No actions available: {e}")
        print()


def display_full_game_state(game: TexasHoldEm, show_all_cards: bool = False):
    """Display complete game state"""
    clear_screen()
    display_header()
    display_game_phase(game)
    display_board(game)
    display_pot(game)
    display_all_players(game, show_all_cards)
    display_available_actions(game)


def display_action_result(player_id: int, action_name: str, amount: int = None):
    """Display the result of a player action"""
    if amount:
        print(
            f"{Fore.GREEN}✓ Player {player_id} {action_name} {amount}{Style.RESET_ALL}"
        )
    else:
        print(f"{Fore.GREEN}✓ Player {player_id} {action_name}{Style.RESET_ALL}")
    print()


def display_hand_result(game: TexasHoldEm):
    """Display hand completion message"""
    print(f"{Fore.MAGENTA}🏆 Hand completed!{Style.RESET_ALL}")
    print()


def display_game_over():
    """Display game over message"""
    print(f"{Fore.RED}🎮 Game Over!{Style.RESET_ALL}")
    print()


def prompt_continue():
    """Prompt user to continue"""
    input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
