"""
🔧 Configuration settings for Texas Hold'em API
Environment variables, constants, and application settings
"""

from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # API Configuration
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:8080",  # Vue dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]

    # Game Configuration
    MAX_CONCURRENT_GAMES: int = 100
    GAME_CLEANUP_INTERVAL_SECONDS: int = 300  # 5 minutes
    MAX_INACTIVE_TIME_SECONDS: int = 1800  # 30 minutes

    # Default Game Settings
    DEFAULT_BUYIN: int = 1000
    DEFAULT_BIG_BLIND: int = 20
    DEFAULT_SMALL_BLIND: int = 10
    DEFAULT_MAX_PLAYERS: int = 6
    DEFAULT_MAX_HANDS: int = 15

    # LLM Configuration (from existing system)
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")
    LLM_REQUEST_TIMEOUT: int = 30
    LLM_MAX_RETRIES: int = 3

    # Database Configuration (optional, for future use)
    DATABASE_URL: str = "sqlite:///./poker_games.db"

    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # WebSocket Configuration
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30
    MAX_WEBSOCKET_CONNECTIONS_PER_GAME: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


# Agent Configuration (matches your existing system)
AVAILABLE_AGENT_TYPES = {
    # Traditional AI Agents
    "random": "Random Agent (Unpredictable)",
    "call": "Call Agent (Always calls)",
    "aggressive_random": "Aggressive Random (No folding)",
    "passive": "Passive Agent (Prefers check/call)",
    "tight": "Tight Agent (Folds often, strong hands only)",
    "loose": "Loose Agent (Plays many hands)",
    "bluff": "Bluff Agent (Occasional bluffs)",
    "position_aware": "Position-Aware Agent",
    # LLM Agents (if available)
    "gpt_4_1_balanced": "GPT-4.1 Balanced (Premium)",
    "gpt_4_1_aggressive": "GPT-4.1 Aggressive (Premium)",
    "gpt_4_1_conservative": "GPT-4.1 Conservative (Premium)",
    "gpt_4_1_mathematical": "GPT-4.1 Mathematical (Premium)",
    "gpt_4_1_bluffer": "GPT-4.1 Bluffer (Premium)",
    "llama_balanced": "Llama 3.1 Balanced (Free)",
    "llama_aggressive": "Llama 3.1 Aggressive (Free)",
    "llama_conservative": "Llama 3.1 Conservative (Free)",
    "gemma_balanced": "Gemma 3 Balanced (Free)",
    "gemma_mathematical": "Gemma 3 Mathematical (Free)",
    # Human player
    "human": "Human Player",
}

# Preset game configurations (matches your existing system)
PRESET_GAME_CONFIGS = {
    "test": {
        "name": "Quick Test Game",
        "description": "2-player quick test",
        "max_players": 2,
        "agents": {0: "call", 1: "random"},
    },
    "balanced": {
        "name": "Balanced 6-Player Game",
        "description": "Mix of different AI personalities",
        "max_players": 6,
        "agents": {
            0: "random",
            1: "call",
            2: "aggressive_random",
            3: "passive",
            4: "tight",
            5: "loose",
        },
    },
    "custom_showcase": {
        "name": "Custom Agent Showcase",
        "description": "6 different custom AI personalities",
        "max_players": 6,
        "agents": {
            0: "passive",
            1: "tight",
            2: "loose",
            3: "bluff",
            4: "position_aware",
            5: "aggressive_random",
        },
    },
    "llm_showcase": {
        "name": "LLM Showcase",
        "description": "6 different LLM agents (requires API keys)",
        "max_players": 6,
        "agents": {
            0: "gpt_4_1_balanced",
            1: "llama_aggressive",
            2: "gemma_mathematical",
            3: "gpt_4_1_bluffer",
            4: "llama_conservative",
            5: "gpt_4_1_mathematical",
        },
    },
    "human_vs_ai": {
        "name": "Human vs AI",
        "description": "Human player against 5 AI opponents",
        "max_players": 6,
        "agents": {
            0: "human",
            1: "aggressive_random",
            2: "tight",
            3: "loose",
            4: "bluff",
            5: "position_aware",
        },
    },
    "human_vs_llm": {
        "name": "Human vs LLM",
        "description": "Human player against 5 LLM opponents",
        "max_players": 6,
        "agents": {
            0: "human",
            1: "gpt_4_1_balanced",
            2: "llama_aggressive",
            3: "gemma_mathematical",
            4: "gpt_4_1_conservative",
            5: "llama_balanced",
        },
    },
}


# API Response Messages
class APIMessages:
    GAME_CREATED = "🎮 Game created successfully"
    GAME_NOT_FOUND = "❌ Game not found"
    INVALID_ACTION = "❌ Invalid action"
    PLAYER_JOINED = "🧑‍💻 Player joined successfully"
    GAME_FULL = "❌ Game is full"
    WEBSOCKET_CONNECTED = "🔌 WebSocket connected"
    WEBSOCKET_DISCONNECTED = "🔌 WebSocket disconnected"
