"""
LLM-powered poker agents using OpenRouter
Each agent has a different personality and decision-making style
"""

from texasholdem import TexasHoldEm, ActionType
from typing import Tuple, Optional, Dict
import time
from llm_client import OpenRouterClient, get_model_name, AVAILABLE_MODELS
from prompt_builder import (
    create_comprehensive_prompt,
    create_simple_prompt,
    create_personality_prompt,
)


class LLMAgent:
    """Base class for LLM-powered poker agents"""

    def __init__(
        self,
        model: str,  # Full model name, not key
        personality: str = "balanced",
        use_simple_prompts: bool = False,
    ):
        self.client = OpenRouterClient()
        self.model = model
        self.personality = personality
        self.use_simple_prompts = use_simple_prompts
        self.decision_count = 0
        self.total_thinking_time = 0.0

    def make_decision(self, game: TexasHoldEm) -> Tuple[ActionType, Optional[int]]:
        """Make a poker decision using the LLM"""
        start_time = time.time()

        try:
            player_id = game.current_player

            # DEBUG: Print what model we're using
            print(f"🤖 LLM Agent ({self.model}) is thinking...")

            # Create prompt based on settings
            if self.use_simple_prompts:
                prompt = create_simple_prompt(game, player_id)
            else:
                prompt = create_personality_prompt(game, player_id, self.personality)

            # Get LLM decision
            decision = self.client.make_poker_decision(self.model, prompt)

            # Parse the decision
            action_str = decision["action"].upper()
            amount = decision.get("amount")
            reasoning = decision.get("reasoning", "No reasoning provided")
            confidence = decision.get("confidence", 0.5)

            # Convert string to ActionType
            action = ActionType[action_str]

            # Validate the decision
            moves = game.get_available_moves()
            if action not in moves.action_types:
                print(f"LLM chose invalid action {action_str}, falling back to CALL")
                action = (
                    ActionType.CALL
                    if ActionType.CALL in moves.action_types
                    else ActionType.FOLD
                )
                amount = None

            # Handle raise amounts
            if action == ActionType.RAISE:
                if amount is None:
                    # Default to minimum raise
                    try:
                        raise_range = moves.raise_range
                        amount = min(raise_range) if raise_range else game.min_raise()
                    except:
                        # Fallback to CALL if raise fails
                        action = ActionType.CALL
                        amount = None
                else:
                    # Validate raise amount
                    try:
                        raise_range = moves.raise_range
                        if raise_range and amount not in raise_range:
                            # Clamp to valid range
                            amount = max(
                                min(raise_range), min(amount, max(raise_range))
                            )
                    except:
                        action = ActionType.CALL
                        amount = None
            else:
                amount = None

            # Track performance
            thinking_time = time.time() - start_time
            self.decision_count += 1
            self.total_thinking_time += thinking_time

            # Display LLM reasoning (optional)
            print(f"🤖 LLM Reasoning: {reasoning} (Confidence: {confidence:.2f})")

            return (action, amount)

        except Exception as e:
            print(f"❌ LLM decision failed: {e}")
            print(f"❌ Model: {self.model}, Personality: {self.personality}")
            print(f"❌ Full error: {type(e).__name__}: {str(e)}")
            # Fallback to safe action
            moves = game.get_available_moves()
            if ActionType.CALL in moves.action_types:
                print("❌ Falling back to CALL")
                return (ActionType.CALL, None)
            elif ActionType.CHECK in moves.action_types:
                print("❌ Falling back to CHECK")
                return (ActionType.CHECK, None)
            else:
                print("❌ Falling back to FOLD")
                return (ActionType.FOLD, None)

    def get_stats(self) -> Dict:
        """Get performance statistics"""
        avg_time = self.total_thinking_time / max(1, self.decision_count)
        return {
            "decisions_made": self.decision_count,
            "total_thinking_time": self.total_thinking_time,
            "average_thinking_time": avg_time,
            "model": self.model,
            "personality": self.personality,
        }


def create_llm_agent(
    model: str, personality: str = "balanced", simple_prompts: bool = False
) -> callable:
    """Create a generic LLM agent"""
    agent = LLMAgent(model, personality, simple_prompts)

    def llm_agent(game: TexasHoldEm) -> Tuple[ActionType, Optional[int]]:
        return agent.make_decision(game)

    return llm_agent


# GPT-4.1 agents (best structured output support)
def create_balanced_gpt_4_1():
    """Create a balanced GPT-4.1 agent"""
    return create_llm_agent(model="openai/gpt-4.1-mini", personality="balanced")


def create_aggressive_gpt_4_1():
    """Create an aggressive GPT-4.1 agent"""
    return create_llm_agent(model="openai/gpt-4.1-mini", personality="aggressive")


def create_conservative_gpt_4_1():
    """Create a conservative gpt-4.1 agent"""
    return create_llm_agent(model="openai/gpt-4.1-mini", personality="conservative")


def create_mathematical_gpt_4_1():
    """Create a mathematical gpt-4.1 agent"""
    return create_llm_agent(model="openai/gpt-4.1-mini", personality="mathematical")


def create_bluffer_gpt_4_1():
    """Create a bluffing gpt-4.1 agent"""
    return create_llm_agent(model="openai/gpt-4.1-mini", personality="bluffer")


# Llama agents (good structured output support)
def create_balanced_llama():
    """Create a balanced Llama agent"""
    return create_llm_agent(
        model="meta-llama/llama-3.1-8b-instruct", personality="balanced"
    )


def create_aggressive_llama():
    """Create an aggressive Llama agent"""
    return create_llm_agent(
        model="meta-llama/llama-3.1-8b-instruct", personality="aggressive"
    )


def create_conservative_llama():
    """Create a conservative Llama agent"""
    return create_llm_agent(
        model="meta-llama/llama-3.1-8b-instruct", personality="conservative"
    )


# Gemma agents (fallback to text parsing)
def create_balanced_gemma():
    """Create a balanced Gemma agent (text parsing fallback)"""
    return create_llm_agent(model="google/gemma-3-27b-it:free", personality="balanced")


def create_bluffer_gemma():
    """Create a bluffing Gemma agent (text parsing fallback)"""
    return create_llm_agent(model="google/gemma-3-27b-it:free", personality="bluffer")


def create_mathematical_gemma():
    """Create a mathematical Gemma agent (text parsing fallback)"""
    return create_llm_agent(
        model="google/gemma-3-27b-it:free", personality="mathematical"
    )


def test_llm_connection():
    """Test LLM connection with multiple models"""
    print("Testing LLM connections...")

    # Test models in order of preference
    test_models = [
        ("openai/gpt-4.1-mini", "GPT-4.1 Mini"),
        ("meta-llama/llama-3.1-8b-instruct", "Llama 3.1 8B"),
        ("google/gemma-3-27b-it:free", "Gemma 3 27B"),
    ]

    client = OpenRouterClient()
    working_models = []

    for model, name in test_models:
        print(f"Testing {name}...")
        try:
            if client.test_connection(model):
                working_models.append((model, name))
                print(f"{name} connection: ✅ Success")
            else:
                print(f"{name} connection: ❌ Failed")
        except Exception as e:
            print(f"{name} connection: ❌ Error - {e}")

    return len(working_models) > 0


# Agent registry for easy access
AGENT_REGISTRY = {
    # gpt-4.1 agents (premium, best performance)
    "gpt_4_1_balanced": create_balanced_gpt_4_1,
    "gpt_4_1_aggressive": create_aggressive_gpt_4_1,
    "gpt_4_1_conservative": create_conservative_gpt_4_1,
    "gpt_4_1_mathematical": create_mathematical_gpt_4_1,
    "gpt_4_1_bluffer": create_bluffer_gpt_4_1,
    # Llama agents (free, good performance)
    "llama_balanced": create_balanced_llama,
    "llama_aggressive": create_aggressive_llama,
    "llama_conservative": create_conservative_llama,
    # Gemma agents (free, text parsing fallback)
    "gemma_balanced": create_balanced_gemma,
    "gemma_bluffer": create_bluffer_gemma,
    "gemma_mathematical": create_mathematical_gemma,
}
