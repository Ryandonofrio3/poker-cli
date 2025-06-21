"""
Enhanced prompt builder for LLM poker agents
Provides comprehensive game state information for decision making
"""

from texasholdem import TexasHoldEm, HandPhase, ActionType
from typing import List, Dict, Optional
from hand_evaluator import (
    evaluate_hand_strength,
    get_pot_odds,
    get_effective_stack_size,
    get_hand_description,
    estimate_winning_probability,
)


def format_cards_for_prompt(cards: List) -> str:
    """Format cards for text prompt"""
    if not cards:
        return "None"
    return ", ".join(card.pretty_string for card in cards)


def get_position_description(game: TexasHoldEm, player_id: int) -> str:
    """Get position description relative to button"""
    try:
        total_players = len(game.players)
        button_pos = game.btn_loc if hasattr(game, "btn_loc") else 0

        relative_pos = (player_id - button_pos) % total_players

        if relative_pos == 0:
            return "Button (best position)"
        elif relative_pos == 1:
            return "Small Blind (early position)"
        elif relative_pos == 2:
            return "Big Blind (early position)"
        elif relative_pos <= total_players // 2:
            return "Early Position"
        elif relative_pos <= total_players * 0.75:
            return "Middle Position"
        else:
            return "Late Position"
    except:
        return "Unknown Position"


def get_opponent_analysis(game: TexasHoldEm, player_id: int) -> str:
    """Analyze opponents still in the hand"""
    try:
        opponents_in_hand = []
        for pid in game.in_pot_iter():
            if pid != player_id:
                chips = game.players[pid].chips
                state = game.players[pid].state.name
                opponents_in_hand.append(f"Player {pid} ({chips} chips, {state})")

        if not opponents_in_hand:
            return "No opponents remaining"

        return f"{len(opponents_in_hand)} opponents: " + ", ".join(opponents_in_hand)
    except:
        return "Unable to analyze opponents"


def get_betting_action_summary(game: TexasHoldEm) -> str:
    """Summarize recent betting action"""
    # This is simplified - could be enhanced with actual action history
    try:
        current_phase = game.hand_phase.name
        pot_total = sum(pot.get_total_amount() for pot in game.pots)

        return f"Current phase: {current_phase}, Pot: {pot_total} chips"
    except:
        return "Betting action unknown"


def create_comprehensive_prompt(
    game: TexasHoldEm, player_id: int, model_personality: str = "balanced", hand_memory: List[Dict] = None
) -> str:
    """
    Create a comprehensive prompt for LLM decision making

    Args:
        game: TexasHoldEm game instance
        player_id: Player making the decision
        model_personality: Personality style for the model
    """
    try:
        # Basic game information
        hole_cards = game.get_hand(player_id)
        board_cards = game.board
        current_phase = game.hand_phase.name

        # Player information
        player_chips = game.players[player_id].chips
        chips_to_call = game.chips_to_call(player_id)

        # Advanced analysis
        hand_strength = evaluate_hand_strength(game, player_id)
        pot_odds = get_pot_odds(game, player_id)
        stack_ratio = get_effective_stack_size(game, player_id)
        hand_description = get_hand_description(game, player_id)
        win_probability = estimate_winning_probability(game, player_id)

        # Position and opponents
        position = get_position_description(game, player_id)
        opponents = get_opponent_analysis(game, player_id)
        betting_summary = get_betting_action_summary(game)

        # Available actions
        moves = game.get_available_moves()
        available_actions = [action.name for action in moves.action_types]

        # Raise range if applicable
        raise_info = ""
        if ActionType.RAISE in moves.action_types:
            try:
                raise_range = moves.raise_range
                if raise_range:
                    min_raise = min(raise_range)
                    max_raise = max(raise_range)
                    raise_info = f"Raise range: {min_raise} to {max_raise} chips"
            except:
                raise_info = "Raise amount to be determined"

        # Personality-based system message addition
        personality_traits = {
            "aggressive": "You prefer aggressive play and look for opportunities to bet and raise.",
            "conservative": "You play tight and only make moves with strong hands or good odds.",
            "balanced": "You play a balanced strategy, adapting to the situation.",
            "bluffer": "You occasionally bluff and use deception as part of your strategy.",
            "mathematical": "You focus heavily on pot odds, hand strength, and mathematical analysis.",
        }

        personality_note = personality_traits.get(
            model_personality, personality_traits["balanced"]
        )

        # Hand memory section
        memory_section = ""
        if hand_memory:
            memory_section = "\n=== MY PREVIOUS ACTIONS THIS HAND ===\n"
            for i, action in enumerate(hand_memory, 1):
                phase = action.get("phase", "Unknown")
                act = action.get("action", "Unknown")
                amount = action.get("amount")
                reasoning = action.get("reasoning", "No reasoning")
                confidence = action.get("confidence", 0.5)
                
                if amount:
                    memory_section += f"{i}. {phase}: {act} {amount} chips (Confidence: {confidence:.2f})\n"
                    memory_section += f"   Reasoning: {reasoning}\n"
                else:
                    memory_section += f"{i}. {phase}: {act} (Confidence: {confidence:.2f})\n"
                    memory_section += f"   Reasoning: {reasoning}\n"
        else:
            memory_section = "\n=== MY PREVIOUS ACTIONS THIS HAND ===\nNo previous actions taken this hand.\n"

        # Build the comprehensive prompt
        prompt = f"""POKER SITUATION ANALYSIS

=== GAME STATE ===
Phase: {current_phase}
Your Position: {position}
{betting_summary}

=== YOUR HAND ===
Hole Cards: {format_cards_for_prompt(hole_cards)}
Board Cards: {format_cards_for_prompt(board_cards)}
Hand Description: {hand_description}
Hand Strength: {hand_strength:.2f} (0.0 = weakest, 1.0 = strongest)
Estimated Win Probability: {win_probability:.2f}

=== FINANCIAL SITUATION ===
Your Chips: {player_chips}
Chips to Call: {chips_to_call}
Pot Odds: {pot_odds:.2f} (lower = better odds)
Stack Ratio: {stack_ratio:.2f} (1.0 = full starting stack)
{raise_info}

=== OPPONENTS ===
{opponents}
{memory_section}
=== AVAILABLE ACTIONS ===
{", ".join(available_actions)}

=== PLAYING STYLE ===
{personality_note}

=== DECISION REQUIRED ===
Based on this comprehensive analysis, what action should you take? Consider:
1. Hand strength and win probability
2. Pot odds and stack size
3. Position and opponent behavior
4. Current betting phase and board texture
5. Your playing style and image
6. Your previous actions this hand and their outcomes

Provide your decision with reasoning and confidence level."""

        return prompt

    except Exception as e:
        # Fallback prompt if analysis fails
        return f"""POKER DECISION NEEDED

You are Player {player_id} in a Texas Hold'em game.
Your cards: {format_cards_for_prompt(hole_cards) if "hole_cards" in locals() else "Unknown"}
Board: {format_cards_for_prompt(board_cards) if "board_cards" in locals() else "Unknown"}
Phase: {current_phase if "current_phase" in locals() else "Unknown"}

Available actions: {", ".join(available_actions) if "available_actions" in locals() else "Unknown"}

Make your decision based on the available information. Error in analysis: {e}"""


def create_simple_prompt(game: TexasHoldEm, player_id: int, hand_memory: List[Dict] = None) -> str:
    """Create a simpler prompt for faster processing"""
    try:
        hole_cards = game.get_hand(player_id)
        board_cards = game.board
        phase = game.hand_phase.name
        chips = game.players[player_id].chips
        to_call = game.chips_to_call(player_id)

        moves = game.get_available_moves()
        actions = [action.name for action in moves.action_types]

        # Simple memory section
        memory_text = ""
        if hand_memory:
            memory_text = "\nPrevious actions: "
            for action in hand_memory:
                act = action.get("action", "Unknown")
                phase = action.get("phase", "Unknown")
                memory_text += f"{phase}:{act} "

        return f"""Texas Hold'em Decision:

Your cards: {format_cards_for_prompt(hole_cards)}
Board: {format_cards_for_prompt(board_cards)}
Phase: {phase}
Your chips: {chips}
To call: {to_call}
Available: {", ".join(actions)}{memory_text}

What's your move?"""

    except Exception as e:
        return f"Make a poker decision. Error: {e}"


def create_personality_prompt(
    game: TexasHoldEm, player_id: int, personality: str, hand_memory: List[Dict] = None
) -> str:
    """Create a prompt with specific personality traits"""
    base_prompt = create_comprehensive_prompt(game, player_id, personality, hand_memory)

    personality_additions = {
        "aggressive": "\n\nRemember: You're an aggressive player who likes to bet and raise to put pressure on opponents.",
        "conservative": "\n\nRemember: You're a conservative player who only plays strong hands and folds when uncertain.",
        "bluffer": "\n\nRemember: You're a strategic player who occasionally bluffs to keep opponents guessing.",
        "mathematical": "\n\nRemember: You're a mathematical player who focuses on odds, probabilities, and expected value.",
    }

    addition = personality_additions.get(personality, "")
    return base_prompt + addition
