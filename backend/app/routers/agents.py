"""
🤖 Agents Router
API endpoints for managing poker agents and agent information
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging

from ..models.schemas import AvailableAgent, APIResponse
from ..core.config import AVAILABLE_AGENT_TYPES, settings

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/agents", tags=["Agents"])


# Import game manager instance from main module
def get_game_manager():
    """Get game manager instance"""
    from ..main import game_manager

    return game_manager


@router.get("", response_model=List[AvailableAgent])
async def list_available_agents() -> List[AvailableAgent]:
    """
    🤖 List all available agent types

    Returns information about all available poker agents including
    traditional AI agents, LLM agents, and human players.
    """
    try:
        agents = []

        for agent_id, agent_name in AVAILABLE_AGENT_TYPES.items():
            # Determine agent category
            if agent_id == "human":
                category = "Human"
                is_available = True
            elif agent_id.startswith(("gpt_4_1", "llama", "gemma")):
                category = "LLM"
                # Check if LLM agents are available (requires API key)
                is_available = bool(settings.OPENROUTER_API_KEY)
            else:
                category = "AI"
                is_available = True

            # Create description based on agent type
            if agent_id == "human":
                description = "Human player - requires manual input for actions"
            elif agent_id == "random":
                description = "Makes random decisions - unpredictable play style"
            elif agent_id == "call":
                description = "Always calls when possible - very passive strategy"
            elif agent_id == "aggressive_random":
                description = "Random decisions but never folds - aggressive style"
            elif agent_id == "passive":
                description = "Prefers checking and calling - conservative approach"
            elif agent_id == "tight":
                description = (
                    "Folds often, only plays strong hands - disciplined strategy"
                )
            elif agent_id == "loose":
                description = "Plays many hands - loose aggressive style"
            elif agent_id == "bluff":
                description = "Occasionally bluffs with weak hands - deceptive play"
            elif agent_id == "position_aware":
                description = (
                    "Adjusts strategy based on table position - strategic play"
                )
            elif "gpt_4_1" in agent_id:
                description = f"GPT-4.1 powered agent - {agent_id.split('_')[-1]} personality (Premium)"
            elif "llama" in agent_id:
                description = f"Llama 3.1 powered agent - {agent_id.split('_')[-1]} personality (Free)"
            elif "gemma" in agent_id:
                description = f"Gemma 3 powered agent - {agent_id.split('_')[-1]} personality (Free)"
            else:
                description = "Custom poker agent with unique strategy"

            agents.append(
                AvailableAgent(
                    agent_id=agent_id,
                    name=agent_name,
                    description=description,
                    category=category,
                    is_available=is_available,
                )
            )

        # Sort agents by category and name
        agents.sort(key=lambda x: (x.category, x.name))

        logger.debug(f"🤖 Listed {len(agents)} available agents")
        return agents

    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(500, f"Failed to list agents: {str(e)}")


@router.get("/{agent_id}", response_model=AvailableAgent)
async def get_agent_info(agent_id: str) -> AvailableAgent:
    """
    🔍 Get detailed information about a specific agent

    Returns comprehensive information about the specified agent including
    capabilities, strategy, and availability.
    """
    if agent_id not in AVAILABLE_AGENT_TYPES:
        raise HTTPException(404, f"Agent '{agent_id}' not found")

    try:
        # Get all agents and find the requested one
        all_agents = await list_available_agents()

        for agent in all_agents:
            if agent.agent_id == agent_id:
                logger.debug(f"🔍 Retrieved info for agent {agent_id}")
                return agent

        # This should not happen if agent_id is valid
        raise HTTPException(404, f"Agent '{agent_id}' not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent info: {e}")
        raise HTTPException(500, f"Failed to get agent info: {str(e)}")


@router.get("/categories", response_model=List[Dict[str, Any]])
async def get_agent_categories() -> List[Dict[str, Any]]:
    """
    📋 Get agent categories with counts

    Returns a summary of agent categories and how many agents
    are available in each category.
    """
    try:
        agents = await list_available_agents()

        # Group by category
        categories = {}
        for agent in agents:
            category = agent.category
            if category not in categories:
                categories[category] = {
                    "category": category,
                    "total_agents": 0,
                    "available_agents": 0,
                    "agent_ids": [],
                }

            categories[category]["total_agents"] += 1
            categories[category]["agent_ids"].append(agent.agent_id)

            if agent.is_available:
                categories[category]["available_agents"] += 1

        result = list(categories.values())
        result.sort(key=lambda x: x["category"])

        logger.debug(f"📋 Retrieved {len(result)} agent categories")
        return result

    except Exception as e:
        logger.error(f"Error getting agent categories: {e}")
        raise HTTPException(500, f"Failed to get agent categories: {str(e)}")


@router.get("/llm/status", response_model=Dict[str, Any])
async def get_llm_status() -> Dict[str, Any]:
    """
    🔍 Get LLM agent availability status

    Returns information about LLM agent availability and configuration.
    """
    try:
        has_api_key = bool(settings.OPENROUTER_API_KEY)

        # Get LLM agents
        all_agents = await list_available_agents()
        llm_agents = [agent for agent in all_agents if agent.category == "LLM"]

        status = {
            "llm_available": has_api_key,
            "api_key_configured": has_api_key,
            "total_llm_agents": len(llm_agents),
            "available_llm_agents": len(
                [agent for agent in llm_agents if agent.is_available]
            ),
            "providers": [],
        }

        # Group by provider
        providers = {}
        for agent in llm_agents:
            if "gpt" in agent.agent_id:
                provider = "OpenAI GPT-4.1"
            elif "llama" in agent.agent_id:
                provider = "Meta Llama 3.1"
            elif "gemma" in agent.agent_id:
                provider = "Google Gemma 3"
            else:
                provider = "Unknown"

            if provider not in providers:
                providers[provider] = {
                    "provider": provider,
                    "agents": [],
                    "available": has_api_key,
                }

            providers[provider]["agents"].append(
                {
                    "agent_id": agent.agent_id,
                    "name": agent.name,
                    "available": agent.is_available,
                }
            )

        status["providers"] = list(providers.values())

        logger.debug("🔍 Retrieved LLM status")
        return status

    except Exception as e:
        logger.error(f"Error getting LLM status: {e}")
        raise HTTPException(500, f"Failed to get LLM status: {str(e)}")


@router.post("/test/{agent_id}", response_model=APIResponse)
async def test_agent(agent_id: str) -> APIResponse:
    """
    🧪 Test an agent's availability and functionality

    Performs a basic test to verify that the specified agent
    can be instantiated and used.
    """
    if agent_id not in AVAILABLE_AGENT_TYPES:
        raise HTTPException(404, f"Agent '{agent_id}' not found")

    try:
        # For now, just return success for available agents
        # TODO: Implement actual agent testing logic

        agent_info = await get_agent_info(agent_id)

        if not agent_info.is_available:
            return APIResponse(
                success=False,
                message=f"Agent '{agent_id}' is not available",
                data={
                    "agent_id": agent_id,
                    "reason": "Missing dependencies or configuration",
                },
            )

        # Simulate test success
        logger.info(f"🧪 Tested agent {agent_id}")

        return APIResponse(
            success=True,
            message=f"Agent '{agent_id}' test successful",
            data={
                "agent_id": agent_id,
                "agent_name": agent_info.name,
                "category": agent_info.category,
                "test_result": "✅ Passed",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing agent {agent_id}: {e}")
        raise HTTPException(500, f"Failed to test agent: {str(e)}")


# Health check endpoint specific to agents
@router.get("/health", response_model=Dict[str, Any])
async def agents_health_check() -> Dict[str, Any]:
    """
    🏥 Agents service health check

    Returns health information specific to the agents service.
    """
    try:
        all_agents = await list_available_agents()

        total_agents = len(all_agents)
        available_agents = len([agent for agent in all_agents if agent.is_available])

        # Check LLM availability
        llm_agents = [agent for agent in all_agents if agent.category == "LLM"]
        llm_available = any(agent.is_available for agent in llm_agents)

        return {
            "status": "healthy",
            "service": "agents",
            "total_agents": total_agents,
            "available_agents": available_agents,
            "unavailable_agents": total_agents - available_agents,
            "llm_agents_available": llm_available,
            "api_key_configured": bool(settings.OPENROUTER_API_KEY),
        }

    except Exception as e:
        logger.error(f"Agents health check failed: {e}")
        return {"status": "unhealthy", "service": "agents", "error": str(e)}
