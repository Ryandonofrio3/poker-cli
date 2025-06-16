"""
Custom agent implementations with different poker playing styles
Each agent follows the documented agent interface pattern
"""

from texasholdem import TexasHoldEm, ActionType
from typing import Tuple, Optional
import random
from hand_evaluator import (
    evaluate_hand_strength,
    get_pot_odds,
    should_be_aggressive,
    should_fold,
    estimate_winning_probability,
    get_effective_stack_size,
)


def create_passive_agent(check_call_bias: float = 0.8) -> callable:
    """
    Creates a passive agent that prefers CHECK/CALL over aggressive actions

    Args:
        check_call_bias: Probability of choosing passive action when available (0.0-1.0)
    """

    def passive_agent(game: TexasHoldEm) -> Tuple[ActionType, Optional[int]]:
        """Passive agent: prefers checking and calling, rarely raises"""
        try:
            moves = game.get_available_moves()
            action_types = list(moves.action_types)

            # Remove FOLD unless hand is very weak
            hand_strength = evaluate_hand_strength(game, game.current_player)
            if hand_strength > 0.2 and ActionType.FOLD in action_types:
                action_types.remove(ActionType.FOLD)

            # Strongly prefer CHECK/CALL
            passive_actions = []
            aggressive_actions = []

            for action in action_types:
                if action in [ActionType.CHECK, ActionType.CALL]:
                    passive_actions.append(action)
                else:
                    aggressive_actions.append(action)

            # Choose passive action most of the time
            if passive_actions and random.random() < check_call_bias:
                selected_action = random.choice(passive_actions)
            elif aggressive_actions:
                selected_action = random.choice(aggressive_actions)
            elif action_types:
                selected_action = random.choice(action_types)
            else:
                return (ActionType.FOLD, None)

            # Handle RAISE with conservative amounts
            if selected_action == ActionType.RAISE:
                try:
                    raise_range = moves.raise_range
                    if raise_range:
                        # Choose small raise (bottom 25% of range)
                        min_raise = min(raise_range)
                        max_raise = max(raise_range)
                        conservative_max = min_raise + (max_raise - min_raise) * 0.25
                        total = random.randint(min_raise, int(conservative_max))
                        return (ActionType.RAISE, total)
                except:
                    pass
                # Fallback to CALL if raise fails
                if ActionType.CALL in action_types:
                    return (ActionType.CALL, None)

            return (selected_action, None)

        except Exception as e:
            # Fallback to call
            return (ActionType.CALL, None)

    return passive_agent


def create_tight_agent(fold_threshold: float = 0.4) -> callable:
    """
    Creates a tight agent that folds weak hands and only plays strong ones

    Args:
        fold_threshold: Hand strength below which to fold (0.0-1.0)
    """

    def tight_agent(game: TexasHoldEm) -> Tuple[ActionType, Optional[int]]:
        """Tight agent: folds weak hands, plays strong hands aggressively"""
        try:
            player_id = game.current_player
            hand_strength = evaluate_hand_strength(game, player_id)
            moves = game.get_available_moves()
            action_types = list(moves.action_types)

            # Fold weak hands unless pot odds are excellent
            if should_fold(game, player_id, fold_threshold):
                if ActionType.FOLD in action_types:
                    return (ActionType.FOLD, None)

            # With strong hands, be aggressive
            if hand_strength > 0.7 and should_be_aggressive(game, player_id):
                if ActionType.RAISE in action_types:
                    try:
                        raise_range = moves.raise_range
                        if raise_range:
                            # Strong raise with good hands
                            min_raise = min(raise_range)
                            max_raise = max(raise_range)
                            # Raise in upper 50% of range
                            mid_point = min_raise + (max_raise - min_raise) * 0.5
                            total = random.randint(int(mid_point), max_raise)
                            return (ActionType.RAISE, total)
                    except:
                        pass

            # With medium hands, be cautious
            if hand_strength > 0.5:
                if ActionType.CALL in action_types:
                    return (ActionType.CALL, None)
                elif ActionType.CHECK in action_types:
                    return (ActionType.CHECK, None)

            # With weak hands that didn't fold, check/call cheaply
            if ActionType.CHECK in action_types:
                return (ActionType.CHECK, None)
            elif ActionType.CALL in action_types:
                # Only call if pot odds are good
                pot_odds = get_pot_odds(game, player_id)
                if pot_odds < 0.3:  # Good pot odds
                    return (ActionType.CALL, None)

            # Last resort
            if ActionType.FOLD in action_types:
                return (ActionType.FOLD, None)
            elif action_types:
                return (action_types[0], None)

            return (ActionType.FOLD, None)

        except Exception as e:
            return (ActionType.CALL, None)

    return tight_agent


def create_loose_agent(play_rate: float = 0.8) -> callable:
    """
    Creates a loose agent that plays many hands and calls frequently

    Args:
        play_rate: Probability of playing a hand rather than folding (0.0-1.0)
    """

    def loose_agent(game: TexasHoldEm) -> Tuple[ActionType, Optional[int]]:
        """Loose agent: plays many hands, calls frequently, occasionally bluffs"""
        try:
            player_id = game.current_player
            hand_strength = evaluate_hand_strength(game, player_id)
            moves = game.get_available_moves()
            action_types = list(moves.action_types)

            # Rarely fold (only with terrible hands and bad pot odds)
            if hand_strength < 0.15 and random.random() > play_rate:
                if ActionType.FOLD in action_types:
                    return (ActionType.FOLD, None)

            # Remove fold from consideration most of the time
            if ActionType.FOLD in action_types and random.random() < play_rate:
                action_types.remove(ActionType.FOLD)

            # Occasionally bluff with weak hands
            if hand_strength < 0.4 and random.random() < 0.2:  # 20% bluff rate
                if ActionType.RAISE in action_types:
                    try:
                        raise_range = moves.raise_range
                        if raise_range:
                            # Small bluff bet
                            min_raise = min(raise_range)
                            max_raise = max(raise_range)
                            bluff_max = min_raise + (max_raise - min_raise) * 0.3
                            total = random.randint(min_raise, int(bluff_max))
                            return (ActionType.RAISE, total)
                    except:
                        pass

            # With strong hands, be more aggressive
            if hand_strength > 0.6:
                if ActionType.RAISE in action_types and random.random() < 0.6:
                    try:
                        raise_range = moves.raise_range
                        if raise_range:
                            total = random.choice(list(raise_range))
                            return (ActionType.RAISE, total)
                    except:
                        pass

            # Default to calling/checking frequently
            preferred_actions = []
            if ActionType.CALL in action_types:
                preferred_actions.append(ActionType.CALL)
            if ActionType.CHECK in action_types:
                preferred_actions.append(ActionType.CHECK)

            if preferred_actions:
                return (random.choice(preferred_actions), None)

            # Random action from available
            if action_types:
                action = random.choice(action_types)
                if action == ActionType.RAISE:
                    try:
                        raise_range = moves.raise_range
                        if raise_range:
                            total = random.choice(list(raise_range))
                            return (ActionType.RAISE, total)
                    except:
                        return (ActionType.CALL, None)
                return (action, None)

            return (ActionType.FOLD, None)

        except Exception as e:
            return (ActionType.CALL, None)

    return loose_agent


def create_bluff_agent(bluff_rate: float = 0.3) -> callable:
    """
    Creates an agent that occasionally bluffs with weak hands

    Args:
        bluff_rate: Probability of bluffing with weak hands (0.0-1.0)
    """

    def bluff_agent(game: TexasHoldEm) -> Tuple[ActionType, Optional[int]]:
        """Bluff agent: plays normally but occasionally bluffs with weak hands"""
        try:
            player_id = game.current_player
            hand_strength = evaluate_hand_strength(game, player_id)
            moves = game.get_available_moves()
            action_types = list(moves.action_types)

            # Bluff with weak hands occasionally
            if hand_strength < 0.4 and random.random() < bluff_rate:
                if ActionType.RAISE in action_types:
                    try:
                        raise_range = moves.raise_range
                        if raise_range:
                            # Medium-sized bluff
                            min_raise = min(raise_range)
                            max_raise = max(raise_range)
                            bluff_amount = min_raise + (
                                max_raise - min_raise
                            ) * random.uniform(0.3, 0.7)
                            total = int(bluff_amount)
                            return (ActionType.RAISE, total)
                    except:
                        pass

            # Strong hands - play aggressively
            if hand_strength > 0.7:
                if ActionType.RAISE in action_types and random.random() < 0.8:
                    try:
                        raise_range = moves.raise_range
                        if raise_range:
                            # Large raise with strong hand
                            min_raise = min(raise_range)
                            max_raise = max(raise_range)
                            strong_amount = min_raise + (
                                max_raise - min_raise
                            ) * random.uniform(0.6, 1.0)
                            total = int(strong_amount)
                            return (ActionType.RAISE, total)
                    except:
                        pass

            # Medium hands - standard play
            if hand_strength > 0.5:
                if ActionType.CALL in action_types:
                    return (ActionType.CALL, None)
                elif ActionType.CHECK in action_types:
                    return (ActionType.CHECK, None)

            # Weak hands - fold or check
            if hand_strength < 0.3:
                if ActionType.CHECK in action_types:
                    return (ActionType.CHECK, None)
                elif ActionType.FOLD in action_types:
                    pot_odds = get_pot_odds(game, player_id)
                    if pot_odds > 0.4:  # Bad pot odds
                        return (ActionType.FOLD, None)

            # Default behavior
            if ActionType.CALL in action_types:
                return (ActionType.CALL, None)
            elif ActionType.CHECK in action_types:
                return (ActionType.CHECK, None)
            elif action_types:
                return (action_types[0], None)

            return (ActionType.FOLD, None)

        except Exception as e:
            return (ActionType.CALL, None)

    return bluff_agent


def create_position_aware_agent() -> callable:
    """
    Creates an agent that adjusts play based on position relative to button
    """

    def position_aware_agent(game: TexasHoldEm) -> Tuple[ActionType, Optional[int]]:
        """Position-aware agent: tighter in early position, looser in late position"""
        try:
            player_id = game.current_player
            hand_strength = evaluate_hand_strength(game, player_id)
            moves = game.get_available_moves()
            action_types = list(moves.action_types)

            # Determine position relative to button
            # This is simplified - could be enhanced with better position logic
            total_players = len(game.players)
            button_pos = game.btn_loc if hasattr(game, "btn_loc") else 0

            # Calculate relative position (0 = early, 1 = late)
            position_factor = (player_id - button_pos) % total_players / total_players

            # Adjust fold threshold based on position
            # Early position = tighter (higher fold threshold)
            # Late position = looser (lower fold threshold)
            base_fold_threshold = 0.4
            position_adjustment = (0.5 - position_factor) * 0.2  # ±0.1 adjustment
            fold_threshold = base_fold_threshold + position_adjustment

            # Fold weak hands more in early position
            if hand_strength < fold_threshold:
                if ActionType.FOLD in action_types:
                    return (ActionType.FOLD, None)

            # Be more aggressive in late position with decent hands
            aggression_threshold = 0.5 + position_factor * 0.2
            if hand_strength > aggression_threshold and position_factor > 0.6:
                if ActionType.RAISE in action_types and random.random() < 0.7:
                    try:
                        raise_range = moves.raise_range
                        if raise_range:
                            total = random.choice(list(raise_range))
                            return (ActionType.RAISE, total)
                    except:
                        pass

            # Standard play for medium hands
            if hand_strength > 0.4:
                if ActionType.CALL in action_types:
                    return (ActionType.CALL, None)
                elif ActionType.CHECK in action_types:
                    return (ActionType.CHECK, None)

            # Default actions
            if ActionType.CHECK in action_types:
                return (ActionType.CHECK, None)
            elif ActionType.CALL in action_types:
                return (ActionType.CALL, None)
            elif ActionType.FOLD in action_types:
                return (ActionType.FOLD, None)

            return (ActionType.FOLD, None)

        except Exception as e:
            return (ActionType.CALL, None)

    return position_aware_agent
