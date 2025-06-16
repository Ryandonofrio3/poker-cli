"""
Hand evaluation utilities for custom agents
Grounded in texasholdem.evaluator module
"""

from texasholdem import TexasHoldEm, Card
from texasholdem.evaluator import evaluate, rank_to_string
from typing import List, Tuple, Optional
import itertools


def evaluate_hand_strength(game: TexasHoldEm, player_id: int) -> float:
    """
    Evaluate hand strength as a percentage (0.0 = worst, 1.0 = best)

    Uses the documented evaluate() function from texasholdem.evaluator
    """
    try:
        hole_cards = game.get_hand(player_id)
        board = game.board

        if not hole_cards or len(hole_cards) != 2:
            return 0.0

        # Combine hole cards and board for evaluation
        all_cards = hole_cards + board

        if len(all_cards) < 2:
            return 0.0

        # Use the documented evaluate function
        hand_rank = evaluate(cards=hole_cards, board=board)

        # Convert rank to strength percentage
        # Lower rank numbers are better (1 = royal flush, 7462 = high card)
        # Convert to 0.0-1.0 scale where 1.0 is best
        strength = 1.0 - ((hand_rank - 1) / 7461.0)
        return max(0.0, min(1.0, strength))

    except Exception as e:
        # Fallback for any evaluation errors
        return 0.5


def get_hand_description(game: TexasHoldEm, player_id: int) -> str:
    """Get human-readable hand description"""
    try:
        hole_cards = game.get_hand(player_id)
        board = game.board

        if not hole_cards:
            return "No hand"

        hand_rank = evaluate(cards=hole_cards, board=board)
        return rank_to_string(hand_rank)

    except:
        return "Unknown hand"


def get_pot_odds(game: TexasHoldEm, player_id: int) -> float:
    """
    Calculate pot odds for calling decisions

    Returns ratio of chips to call vs pot size
    Lower values = better pot odds
    """
    try:
        chips_to_call = game.chips_to_call(player_id)
        if chips_to_call == 0:
            return 0.0  # No cost to continue

        pot_total = sum(pot.get_total_amount() for pot in game.pots)

        if pot_total == 0:
            return float("inf")  # Avoid division by zero

        # Return call cost as ratio of pot
        return chips_to_call / pot_total

    except:
        return 1.0  # Default to even odds


def get_effective_stack_size(game: TexasHoldEm, player_id: int) -> float:
    """
    Get stack size as ratio of starting chips

    Returns 0.0-1.0 where 1.0 is full starting stack
    """
    try:
        current_chips = game.players[player_id].chips
        # Estimate starting stack based on current game setup
        # This could be enhanced to track actual starting amounts
        estimated_starting = game.buyin if hasattr(game, "buyin") else 1000

        return current_chips / estimated_starting

    except:
        return 0.5


def is_drawing_hand(hole_cards: List[Card], board: List[Card]) -> bool:
    """
    Check if hand has drawing potential (flush/straight draws)

    This is a simplified version - could be enhanced with more sophisticated analysis
    """
    try:
        if len(board) < 3:  # Need flop to evaluate draws
            return False

        all_cards = hole_cards + board

        # Check for flush draw (4 of same suit)
        suits = {}
        for card in all_cards:
            suit_str = card.pretty_string[-2]  # Get suit from pretty string
            suits[suit_str] = suits.get(suit_str, 0) + 1

        if any(count >= 4 for count in suits.values()):
            return True

        # Check for straight draw (simplified)
        ranks = []
        for card in all_cards:
            ranks.append(card.rank)

        ranks.sort()
        consecutive = 1
        max_consecutive = 1

        for i in range(1, len(ranks)):
            if ranks[i] == ranks[i - 1] + 1:
                consecutive += 1
                max_consecutive = max(max_consecutive, consecutive)
            else:
                consecutive = 1

        return max_consecutive >= 4

    except:
        return False


def estimate_winning_probability(game: TexasHoldEm, player_id: int) -> float:
    """
    Estimate probability of winning based on hand strength and game context

    This is a simplified heuristic - could be enhanced with Monte Carlo simulation
    """
    try:
        hand_strength = evaluate_hand_strength(game, player_id)

        # Adjust based on number of opponents
        opponents_in_hand = len(list(game.in_pot_iter())) - 1
        if opponents_in_hand <= 0:
            return 1.0  # No opponents, guaranteed win

        # Reduce win probability based on number of opponents
        # More opponents = lower chance of winning
        opponent_factor = 1.0 / (1.0 + opponents_in_hand * 0.3)

        # Combine hand strength with opponent factor
        win_probability = hand_strength * opponent_factor

        # Add drawing potential bonus if early in hand
        if len(game.board) <= 4:  # Flop or turn
            hole_cards = game.get_hand(player_id)
            if hole_cards and is_drawing_hand(hole_cards, game.board):
                win_probability += 0.1  # Small bonus for drawing hands

        return max(0.0, min(1.0, win_probability))

    except:
        return 0.5


def should_be_aggressive(game: TexasHoldEm, player_id: int) -> bool:
    """
    Determine if situation favors aggressive play

    Based on hand strength, position, and pot odds
    """
    try:
        hand_strength = evaluate_hand_strength(game, player_id)
        pot_odds = get_pot_odds(game, player_id)
        stack_ratio = get_effective_stack_size(game, player_id)

        # Strong hand = be aggressive
        if hand_strength > 0.7:
            return True

        # Good pot odds with decent hand
        if hand_strength > 0.5 and pot_odds < 0.3:
            return True

        # Large stack allows for more aggression
        if hand_strength > 0.6 and stack_ratio > 0.7:
            return True

        return False

    except:
        return False


def should_fold(game: TexasHoldEm, player_id: int, fold_threshold: float = 0.3) -> bool:
    """
    Determine if hand should be folded

    Args:
        fold_threshold: Hand strength below which to fold (0.0-1.0)
    """
    try:
        hand_strength = evaluate_hand_strength(game, player_id)
        pot_odds = get_pot_odds(game, player_id)

        # Always fold very weak hands
        if hand_strength < fold_threshold:
            return True

        # Fold decent hands with terrible pot odds
        if hand_strength < 0.6 and pot_odds > 0.5:
            return True

        return False

    except:
        return False
