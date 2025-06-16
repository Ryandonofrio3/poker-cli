"""
Agent management functions for Texas Hold'em CLI
Handle built-in agents, custom agents, LLM agents, and agent selection
"""

from texasholdem import TexasHoldEm, ActionType
from texasholdem.agents import random_agent, call_agent
from typing import Dict, Callable, Tuple, Optional
import time
import random

# Import our custom agents
from custom_agents import (
    create_passive_agent,
    create_tight_agent,
    create_loose_agent,
    create_bluff_agent,
    create_position_aware_agent,
)

# Import LLM agents
try:
    from llm_agents import (
        create_balanced_llama,
        create_aggressive_llama,
        create_conservative_llama,
        create_balanced_gemma,
        create_bluffer_gemma,
        create_mathematical_gemma,
        create_balanced_gpt_4_1,
        create_aggressive_gpt_4_1,
        create_conservative_gpt_4_1,
        create_mathematical_gpt_4_1,
        create_bluffer_gpt_4_1,
    )

    LLM_AVAILABLE = True
except ImportError as e:
    print(f"LLM agents not available: {e}")
    LLM_AVAILABLE = False


# Agent function type definition
AgentFunction = Callable[[TexasHoldEm], Tuple[ActionType, Optional[int]]]

# Available built-in agents
BUILTIN_AGENTS = {
    "random": random_agent,
    "call": call_agent,
}


def get_random_agent_action(game: TexasHoldEm) -> Tuple[ActionType, Optional[int]]:
    """Get action from random agent using documented interface"""
    return random_agent(game, no_fold=False)


def get_call_agent_action(game: TexasHoldEm) -> Tuple[ActionType, Optional[int]]:
    """Get action from call agent using documented interface"""
    return call_agent(game)


def get_aggressive_random_agent_action(
    game: TexasHoldEm,
) -> Tuple[ActionType, Optional[int]]:
    """
    Get action from aggressive random agent (no folding)

    This is a workaround for the bug in random_agent(no_fold=True)
    We implement our own version that avoids folding.
    """
    moves = game.get_available_moves()
    action_types = list(moves.action_types)

    # Remove FOLD from available actions if it exists
    if ActionType.FOLD in action_types:
        action_types.remove(ActionType.FOLD)

    # If no actions left (shouldn't happen), fallback to call
    if not action_types:
        return get_call_agent_action(game)

    # Randomly select from remaining actions
    selected_action = random.choice(action_types)

    if selected_action == ActionType.RAISE:
        # For RAISE, we need to pick a random amount from the valid range
        try:
            raise_range = moves.raise_range
            if raise_range:
                total = random.choice(list(raise_range))
                return (ActionType.RAISE, total)
            else:
                # No valid raise range, fallback to CALL
                return (ActionType.CALL, None)
        except:
            # If there's any issue with raise range, fallback to CALL
            return (ActionType.CALL, None)
    else:
        # For CHECK, CALL, ALL_IN - no total needed
        return (selected_action, None)


# Initialize custom agents (these return agent functions)
passive_agent = create_passive_agent(check_call_bias=0.8)
tight_agent = create_tight_agent(fold_threshold=0.4)
loose_agent = create_loose_agent(play_rate=0.8)
bluff_agent = create_bluff_agent(bluff_rate=0.3)
position_aware_agent = create_position_aware_agent()

# Initialize LLM agent variables (will be set if available)
gpt_4_1_balanced = None
gpt_4_1_aggressive = None
gpt_4_1_conservative = None
gpt_4_1_mathematical = None
gpt_4_1_bluffer = None
llama_balanced = None
llama_aggressive = None
llama_conservative = None
gemma_balanced = None
gemma_bluffer = None
gemma_mathematical = None

# Initialize LLM agents if available
if LLM_AVAILABLE:
    print("🔧 Initializing LLM agents...")
    try:
        # gpt-4.1 agents (best performance)
        gpt_4_1_balanced = create_balanced_gpt_4_1()
        gpt_4_1_aggressive = create_aggressive_gpt_4_1()
        gpt_4_1_conservative = create_conservative_gpt_4_1()
        gpt_4_1_mathematical = create_mathematical_gpt_4_1()
        gpt_4_1_bluffer = create_bluffer_gpt_4_1()
        print("✅ GPT-4.1 agents initialized successfully")

        # Llama agents (good performance, free)
        llama_balanced = create_balanced_llama()
        llama_aggressive = create_aggressive_llama()
        llama_conservative = create_conservative_llama()
        print("✅ Llama agents initialized successfully")

        # Gemma agents (fallback)
        gemma_balanced = create_balanced_gemma()
        gemma_bluffer = create_bluffer_gemma()
        gemma_mathematical = create_mathematical_gemma()
        print("✅ Gemma agents initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing LLM agents: {e}")
        LLM_AVAILABLE = False


def create_agent_config(agent_assignments: Dict[int, str]) -> Dict[int, AgentFunction]:
    """
    Create agent configuration mapping player IDs to agent functions

    Args:
        agent_assignments: Dict mapping player_id to agent_name

    Returns:
        Dict mapping player_id to agent function
    """
    agent_config = {}

    for player_id, agent_name in agent_assignments.items():
        if agent_name == "random":
            agent_config[player_id] = get_random_agent_action
        elif agent_name == "call":
            agent_config[player_id] = get_call_agent_action
        elif agent_name == "aggressive":
            agent_config[player_id] = get_aggressive_random_agent_action
        elif agent_name == "passive":
            agent_config[player_id] = passive_agent
        elif agent_name == "tight":
            agent_config[player_id] = tight_agent
        elif agent_name == "loose":
            agent_config[player_id] = loose_agent
        elif agent_name == "bluff":
            agent_config[player_id] = bluff_agent
        elif agent_name == "position":
            agent_config[player_id] = position_aware_agent
        elif (
            agent_name == "gpt_4_1_balanced"
            and LLM_AVAILABLE
            and gpt_4_1_balanced is not None
        ):
            agent_config[player_id] = gpt_4_1_balanced
        elif (
            agent_name == "gpt_4_1_aggressive"
            and LLM_AVAILABLE
            and gpt_4_1_aggressive is not None
        ):
            agent_config[player_id] = gpt_4_1_aggressive
        elif (
            agent_name == "gpt_4_1_conservative"
            and LLM_AVAILABLE
            and gpt_4_1_conservative is not None
        ):
            agent_config[player_id] = gpt_4_1_conservative
        elif (
            agent_name == "gpt_4_1_mathematical"
            and LLM_AVAILABLE
            and gpt_4_1_mathematical is not None
        ):
            agent_config[player_id] = gpt_4_1_mathematical
        elif (
            agent_name == "gpt_4_1_bluffer"
            and LLM_AVAILABLE
            and gpt_4_1_bluffer is not None
        ):
            agent_config[player_id] = gpt_4_1_bluffer
        elif (
            agent_name == "llama_balanced"
            and LLM_AVAILABLE
            and llama_balanced is not None
        ):
            agent_config[player_id] = llama_balanced
        elif (
            agent_name == "llama_aggressive"
            and LLM_AVAILABLE
            and llama_aggressive is not None
        ):
            agent_config[player_id] = llama_aggressive
        elif (
            agent_name == "llama_conservative"
            and LLM_AVAILABLE
            and llama_conservative is not None
        ):
            agent_config[player_id] = llama_conservative
        elif (
            agent_name == "gemma_balanced"
            and LLM_AVAILABLE
            and gemma_balanced is not None
        ):
            agent_config[player_id] = gemma_balanced
        elif (
            agent_name == "gemma_bluffer"
            and LLM_AVAILABLE
            and gemma_bluffer is not None
        ):
            agent_config[player_id] = gemma_bluffer
        elif (
            agent_name == "gemma_mathematical"
            and LLM_AVAILABLE
            and gemma_mathematical is not None
        ):
            agent_config[player_id] = gemma_mathematical
        else:
            # Default to call agent for unknown types
            print(
                f"⚠️  Unknown agent type '{agent_name}' for Player {player_id}, using call agent"
            )
            agent_config[player_id] = get_call_agent_action

    return agent_config


def get_agent_action(
    game: TexasHoldEm, player_id: int, agent_config: Dict[int, AgentFunction]
) -> Tuple[ActionType, Optional[int]]:
    """
    Get action from specified agent for given player

    Args:
        game: TexasHoldEm game instance
        player_id: Player ID to get action for
        agent_config: Agent configuration mapping

    Returns:
        Tuple of (ActionType, total_amount)
    """
    if player_id in agent_config:
        agent_func = agent_config[player_id]
        agent_name = get_agent_name(player_id, agent_config)
        print(f"🎯 Getting action for Player {player_id} using: {agent_name}")
        try:
            return agent_func(game)
        except Exception as e:
            print(f"❌ Agent error for player {player_id} ({agent_name}): {e}")
            print(f"❌ Full error: {type(e).__name__}: {str(e)}")
            # Fallback to call agent
            print("❌ Falling back to call agent")
            return get_call_agent_action(game)
    else:
        # Default to call agent if no specific agent assigned
        print(f"🎯 No agent assigned to Player {player_id}, using call agent")
        return get_call_agent_action(game)


def is_player_agent_controlled(
    player_id: int, agent_config: Dict[int, AgentFunction]
) -> bool:
    """Check if player is controlled by an agent"""
    return player_id in agent_config


def get_agent_name(player_id: int, agent_config: Dict[int, AgentFunction]) -> str:
    """Get the name of the agent controlling a player"""
    if player_id not in agent_config:
        return "Human"

    agent_func = agent_config[player_id]

    # Handle human agents first
    if hasattr(agent_func, "__closure__") and agent_func.__closure__:
        try:
            # Try to detect debug mode from closure for human agents
            closure_vars = [
                cell.cell_contents
                for cell in agent_func.__closure__
                if cell.cell_contents is not None
            ]
            if True in closure_vars:
                return "Human (Debug Mode)"
            elif False in closure_vars:
                return "Human (Realistic)"
        except:
            pass

    # Check for human agent by function name
    func_name = getattr(agent_func, "__name__", str(agent_func))
    if "human_agent" in func_name:
        return "Human Player"

    # Built-in agents
    if agent_func == get_random_agent_action:
        return "Random Agent"
    elif agent_func == get_call_agent_action:
        return "Call Agent"
    elif agent_func == get_aggressive_random_agent_action:
        return "Aggressive Agent"
    # Custom agents
    elif agent_func == passive_agent:
        return "Passive Agent"
    elif agent_func == tight_agent:
        return "Tight Agent"
    elif agent_func == loose_agent:
        return "Loose Agent"
    elif agent_func == bluff_agent:
        return "Bluff Agent"
    elif agent_func == position_aware_agent:
        return "Position Agent"
    # LLM agents
    elif LLM_AVAILABLE:
        # gpt-4.1 agents
        if agent_func == gpt_4_1_balanced:
            return "🤖 gpt-4.1 Balanced"
        elif agent_func == gpt_4_1_aggressive:
            return "🤖 gpt-4.1 Aggressive"
        elif agent_func == gpt_4_1_conservative:
            return "🤖 gpt-4.1 Conservative"
        elif agent_func == gpt_4_1_mathematical:
            return "🤖 gpt-4.1 Mathematical"
        elif agent_func == gpt_4_1_bluffer:
            return "🤖 gpt-4.1 Bluffer"
        # Llama agents
        elif agent_func == llama_balanced:
            return "🦙 Llama Balanced"
        elif agent_func == llama_aggressive:
            return "🦙 Llama Aggressive"
        elif agent_func == llama_conservative:
            return "🦙 Llama Conservative"
        # Gemma agents
        elif agent_func == gemma_balanced:
            return "💎 Gemma Balanced"
        elif agent_func == gemma_bluffer:
            return "💎 Gemma Bluffer"
        elif agent_func == gemma_mathematical:
            return "💎 Gemma Mathematical"

    return "Custom Agent"


def add_thinking_delay(min_seconds: float = 0.1, max_seconds: float = 0.5):
    """Add a realistic thinking delay for agents"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)


def create_default_6_player_config() -> Dict[int, AgentFunction]:
    """Create a default 6-player configuration with mixed agents"""
    return create_agent_config(
        {
            0: "random",  # Player 0: Random
            1: "call",  # Player 1: Call
            2: "aggressive",  # Player 2: Aggressive
            3: "tight",  # Player 3: Tight (NEW)
            4: "loose",  # Player 4: Loose (NEW)
            5: "bluff",  # Player 5: Bluff (NEW)
        }
    )


def create_llm_showcase_config() -> Dict[int, AgentFunction]:
    """Create a configuration showcasing LLM agents"""
    if not LLM_AVAILABLE:
        return create_default_6_player_config()

    return create_agent_config(
        {
            0: "llama_balanced",  # Player 0: Llama Balanced
            1: "gemma_balanced",  # Player 1: Gemma Balanced
            2: "llama_aggressive",  # Player 2: Llama Aggressive
            3: "gemma_bluffer",  # Player 3: Gemma Bluffer
            4: "llama_conservative",  # Player 4: Llama Conservative
            5: "gemma_mathematical",  # Player 5: Gemma Mathematical
        }
    )


def create_llm_vs_ai_config() -> Dict[int, AgentFunction]:
    """Create a mixed LLM vs traditional AI configuration"""
    if not LLM_AVAILABLE:
        return create_default_6_player_config()

    return create_agent_config(
        {
            0: "llama_balanced",  # Player 0: LLM
            1: "tight",  # Player 1: Traditional AI
            2: "gemma_bluffer",  # Player 2: LLM
            3: "loose",  # Player 3: Traditional AI
            4: "llama_aggressive",  # Player 4: LLM
            5: "position",  # Player 5: Traditional AI
        }
    )


def create_custom_showcase_config() -> Dict[int, AgentFunction]:
    """Create a configuration showcasing all custom agent types"""
    return create_agent_config(
        {
            0: "passive",  # Player 0: Passive Agent
            1: "tight",  # Player 1: Tight Agent
            2: "loose",  # Player 2: Loose Agent
            3: "bluff",  # Player 3: Bluff Agent
            4: "position",  # Player 4: Position-Aware Agent
            5: "aggressive",  # Player 5: Aggressive Agent
        }
    )


def create_test_config() -> Dict[int, AgentFunction]:
    """Create a simple test configuration"""
    return create_agent_config(
        {
            0: "call",
            1: "random",
        }
    )


def create_mixed_personality_config() -> Dict[int, AgentFunction]:
    """Create a mixed configuration with variety of playing styles"""
    return create_agent_config(
        {
            0: "tight",  # Conservative player
            1: "loose",  # Aggressive/loose player
            2: "bluff",  # Strategic bluffer
            3: "passive",  # Passive check/caller
            4: "position",  # Position-aware player
            5: "random",  # Unpredictable player
        }
    )


def display_agent_config(agent_config: Dict[int, AgentFunction]):
    """Display current agent configuration"""
    print("Agent Configuration:")
    for player_id in sorted(agent_config.keys()):
        agent_name = get_agent_name(player_id, agent_config)
        print(f"  Player {player_id}: {agent_name}")
    print()


def list_available_agents():
    """List all available agent types"""
    print("Available Agent Types:")
    print("Built-in Agents:")
    print("  random      - Random actions")
    print("  call        - Always calls/checks")
    print("  aggressive  - Random without folding")
    print("\nCustom Agents:")
    print("  passive     - Prefers check/call, rarely raises")
    print("  tight       - Folds weak hands, aggressive with strong hands")
    print("  loose       - Plays many hands, calls frequently")
    print("  bluff       - Occasionally bluffs with weak hands")
    print("  position    - Adjusts play based on table position")

    if LLM_AVAILABLE:
        print("\nLLM Agents:")
        print("gpt-4.1 Agents (Premium, Best Performance):")
        print("  gpt-4.1_balanced     - 🤖 gpt-4.1 with balanced strategy")
        print("  gpt-4.1_aggressive   - 🤖 gpt-4.1 with aggressive style")
        print("  gpt-4.1_conservative - 🤖 gpt-4.1 with conservative approach")
        print("  gpt-4.1_mathematical - 🤖 gpt-4.1 with mathematical focus")
        print("  gpt-4.1_bluffer      - 🤖 gpt-4.1 with bluffing tactics")
        print("\nLlama Agents (Free, Good Performance):")
        print("  llama_balanced     - 🦙 Llama with balanced strategy")
        print("  llama_aggressive   - 🦙 Llama with aggressive style")
        print("  llama_conservative - 🦙 Llama with conservative approach")
        print("\nGemma Agents (Free, Text Parsing):")
        print("  gemma_balanced     - 💎 Gemma with balanced strategy")
        print("  gemma_bluffer      - 💎 Gemma with bluffing tactics")
        print("  gemma_mathematical - 💎 Gemma with mathematical focus")
    else:
        print("\nLLM Agents: ❌ Not available (check API key and connection)")
    print()


def get_agent_description(agent_name: str) -> str:
    """Get description of an agent type"""
    descriptions = {
        "random": "Makes random legal actions",
        "call": "Always calls or checks when possible",
        "aggressive": "Random actions but never folds",
        "passive": "Prefers passive play (check/call), rarely raises",
        "tight": "Folds weak hands, plays strong hands aggressively",
        "loose": "Plays many hands, calls frequently, occasional bluffs",
        "bluff": "Strategic bluffer - raises with weak hands sometimes",
        "position": "Adjusts tightness/aggression based on table position",
        "gpt-4.1_balanced": "gpt-4.1 with balanced poker strategy (premium)",
        "gpt-4.1_aggressive": "gpt-4.1 with aggressive poker style (premium)",
        "gpt-4.1_conservative": "gpt-4.1 with conservative poker approach (premium)",
        "gpt-4.1_mathematical": "gpt-4.1 with mathematical poker analysis (premium)",
        "gpt-4.1_bluffer": "gpt-4.1 with strategic bluffing tactics (premium)",
        "llama_balanced": "Llama with balanced poker strategy (free)",
        "llama_aggressive": "Llama with aggressive poker style (free)",
        "llama_conservative": "Llama with conservative poker approach (free)",
        "gemma_balanced": "Gemma with balanced poker strategy (free)",
        "gemma_bluffer": "Gemma with bluffing specialist (free)",
        "gemma_mathematical": "Gemma with mathematical poker analysis (free)",
    }
    return descriptions.get(agent_name, "Unknown agent type")


def create_balanced_config() -> Dict[int, AgentFunction]:
    """Create a well-balanced configuration for interesting gameplay"""
    return create_agent_config(
        {
            0: "tight",  # The rock - tight/aggressive
            1: "loose",  # The maniac - loose/aggressive
            2: "passive",  # The calling station
            3: "bluff",  # The tricky player
            4: "position",  # The technical player
            5: "call",  # The predictable player
        }
    )


def create_gpt_4_1_showcase_config() -> Dict[int, AgentFunction]:
    """Create a configuration showcasing gpt-4.1 agents"""
    if not LLM_AVAILABLE:
        return create_default_6_player_config()

    return create_agent_config(
        {
            0: "gpt_4_1_balanced",  # Player 0: gpt-4.1 Balanced
            1: "gpt_4_1_aggressive",  # Player 1: gpt-4.1 Aggressive
            2: "gpt_4_1_conservative",  # Player 2: gpt-4.1 Conservative
            3: "gpt_4_1_mathematical",  # Player 3: gpt-4.1 Mathematical
            4: "gpt_4_1_bluffer",  # Player 4: gpt-4.1 Bluffer
            5: "llama_balanced",  # Player 5: Llama for comparison
        }
    )


def create_premium_vs_free_config() -> Dict[int, AgentFunction]:
    """Create a configuration comparing premium vs free LLM agents"""
    if not LLM_AVAILABLE:
        return create_default_6_player_config()

    return create_agent_config(
        {
            0: "gpt_4_1_balanced",  # Premium
            1: "llama_balanced",  # Free
            2: "gpt_4_1_aggressive",  # Premium
            3: "gemma_bluffer",  # Free
            4: "gpt_4_1_mathematical",  # Premium
            5: "llama_conservative",  # Free
        }
    )


def create_human_vs_ai_config() -> Dict[int, Callable]:
    """Create configuration for human vs AI agents (realistic mode)"""
    from human_player import create_human_agent

    return {
        0: create_human_agent(0, debug_mode=False),  # Human player (realistic)
        1: get_aggressive_random_agent_action,
        2: tight_agent,
        3: loose_agent,
        4: bluff_agent,
        5: position_aware_agent,
    }


def create_human_vs_ai_debug_config() -> Dict[int, Callable]:
    """Create configuration for human vs AI agents (debug mode - see all cards)"""
    from human_player import create_human_agent

    return {
        0: create_human_agent(0, debug_mode=True),  # Human player (debug)
        1: get_aggressive_random_agent_action,
        2: tight_agent,
        3: loose_agent,
        4: bluff_agent,
        5: position_aware_agent,
    }


def create_human_vs_llm_config() -> Dict[int, Callable]:
    """Create configuration for human vs LLM agents (realistic mode)"""
    from human_player import create_human_agent

    return {
        0: create_human_agent(0, debug_mode=False),  # Human player (realistic)
        1: gpt_4_1_balanced
        if LLM_AVAILABLE and gpt_4_1_balanced
        else get_call_agent_action,
        2: llama_aggressive if LLM_AVAILABLE and llama_aggressive else tight_agent,
        3: gpt_4_1_conservative
        if LLM_AVAILABLE and gpt_4_1_conservative
        else loose_agent,
        4: llama_balanced if LLM_AVAILABLE and llama_balanced else bluff_agent,
        5: gpt_4_1_bluffer
        if LLM_AVAILABLE and gpt_4_1_bluffer
        else position_aware_agent,
    }


def create_human_vs_llm_debug_config() -> Dict[int, Callable]:
    """Create configuration for human vs LLM agents (debug mode - see all cards)"""
    from human_player import create_human_agent

    return {
        0: create_human_agent(0, debug_mode=True),  # Human player (debug)
        1: gpt_4_1_balanced
        if LLM_AVAILABLE and gpt_4_1_balanced
        else get_call_agent_action,
        2: llama_aggressive if LLM_AVAILABLE and llama_aggressive else tight_agent,
        3: gpt_4_1_conservative
        if LLM_AVAILABLE and gpt_4_1_conservative
        else loose_agent,
        4: llama_balanced if LLM_AVAILABLE and llama_balanced else bluff_agent,
        5: gpt_4_1_bluffer
        if LLM_AVAILABLE and gpt_4_1_bluffer
        else position_aware_agent,
    }


def create_human_heads_up_config() -> Dict[int, Callable]:
    """Create configuration for human vs one AI opponent (heads-up)"""
    from human_player import create_human_agent

    return {
        0: create_human_agent(0, debug_mode=False),  # Human player
        1: gpt_4_1_balanced
        if LLM_AVAILABLE and gpt_4_1_balanced
        else tight_agent,  # Strong opponent
    }


def create_human_heads_up_debug_config() -> Dict[int, Callable]:
    """Create configuration for human vs one AI opponent (heads-up debug)"""
    from human_player import create_human_agent

    return {
        0: create_human_agent(0, debug_mode=True),  # Human player (debug)
        1: gpt_4_1_balanced
        if LLM_AVAILABLE and gpt_4_1_balanced
        else tight_agent,  # Strong opponent
    }
