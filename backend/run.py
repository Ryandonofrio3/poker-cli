#!/usr/bin/env python3
"""
🚀 FastAPI Backend Startup Script
Runs the Texas Hold'em Poker API with dependency injection
"""

import sys
import os
from pathlib import Path

# Add the parent directory to Python path so we can import from the main project
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Set up environment
os.environ.setdefault("ENVIRONMENT", "development")

import uvicorn
from fastapi import Depends

# Import our FastAPI app and game manager
from app.main import app, game_manager


# Fix dependency injection for game manager
def get_game_manager_override():
    """Override for game manager dependency"""
    return game_manager


# Override the dependency in routers
from app.routers import games, agents

games.get_game_manager = get_game_manager_override
agents.get_game_manager = lambda: game_manager  # In case it's needed


def main():
    """Main startup function"""
    print("🚀 Starting Texas Hold'em FastAPI Backend...")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🐍 Python path includes: {parent_dir}")

    # Development server configuration
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        log_level="info",
        access_log=True,
    )


if __name__ == "__main__":
    main()
