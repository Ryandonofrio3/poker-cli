"""
🎮 Texas Hold'em FastAPI Backend
Transform CLI poker system into scalable, production-ready API
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Import routers
from .routers import games, agents
from .core.config import settings
from .services.game_manager import GameManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global game manager instance
game_manager = GameManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("🚀 Starting Texas Hold'em API Backend...")
    logger.info(f"🎯 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🎲 Max concurrent games: {settings.MAX_CONCURRENT_GAMES}")

    yield

    logger.info("🏁 Shutting down Texas Hold'em API Backend...")
    await game_manager.cleanup_all_games()


# Create FastAPI application
app = FastAPI(
    title="Texas Hold'em Poker API",
    description="🃏 Scalable poker backend with LLM agents, human players, and real-time gameplay",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(games.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1")


@app.get("/")
async def root():
    """API health check and welcome message"""
    return {
        "message": "🃏 Texas Hold'em Poker API",
        "version": "1.0.0",
        "status": "🚀 Running",
        "docs": "/docs",
        "active_games": len(game_manager.active_games),
        "features": [
            "🤖 LLM Agent Integration",
            "🧑‍💻 Human Player Support",
            "🔄 Real-time WebSocket Updates",
            "📊 Game History & Analytics",
            "🎯 Multiple Agent Personalities",
        ],
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "active_games": len(game_manager.active_games),
        "memory_usage": "TODO: Add memory stats",
        "uptime": "TODO: Add uptime calculation",
    }


@app.websocket("/ws/games/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    """WebSocket endpoint for real-time game updates"""
    await websocket.accept()
    logger.info(f"🔌 WebSocket connected for game {game_id}")

    try:
        # Register websocket with game manager
        success = await game_manager.add_websocket(game_id, websocket)
        if not success:
            await websocket.close(code=4004, reason="Game not found")
            return

        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await websocket.receive_json()
                logger.info(f"📨 WebSocket message received: {data}")

                # Handle different message types
                message_type = data.get("type")
                if message_type == "ping":
                    await websocket.send_json({"type": "pong"})
                elif message_type == "player_action":
                    # Forward to game manager
                    result = await game_manager.handle_websocket_action(game_id, data)
                    await websocket.send_json(result)
                else:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": f"Unknown message type: {message_type}",
                        }
                    )

            except Exception as e:
                logger.error(f"❌ Error processing WebSocket message: {e}")
                await websocket.send_json(
                    {"type": "error", "message": "Failed to process message"}
                )

    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket disconnected for game {game_id}")
    except Exception as e:
        logger.error(f"❌ WebSocket error for game {game_id}: {e}")
    finally:
        await game_manager.remove_websocket(game_id, websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
