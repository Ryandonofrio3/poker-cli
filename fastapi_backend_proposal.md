# FastAPI Backend Architecture Proposal

## Overview
Transform your existing CLI poker system into a service-oriented architecture with FastAPI, enabling web frontends, multiplayer games, and better deployment options.

## Core Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Client    │    │   Web Client    │    │  Mobile Client  │
│   (existing)    │    │   (future)      │    │   (future)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Backend                         │
├─────────────────────────────────────────────────────────────────┤
│  WebSocket Game Sessions  │  REST API  │  Game State Manager   │
├─────────────────────────────────────────────────────────────────┤
│           Your Existing Game Engine (Unchanged)                │
│  • TexasHoldEm wrapper    • Agent Manager    • LLM Integration │
└─────────────────────────────────────────────────────────────────┘
                                 │
┌─────────────────────────────────────────────────────────────────┐
│                    Database Layer (Optional)                   │
│               PostgreSQL/SQLite for Game History               │
└─────────────────────────────────────────────────────────────────┘
```

## Implementation Strategy

### Phase 1: Core API Foundation (Week 1)
```python
# app/main.py
from fastapi import FastAPI, WebSocket, HTTPException
from typing import Dict, List
import uuid

app = FastAPI(title="Texas Hold'em API", version="1.0.0")

# Game session manager
active_games: Dict[str, GameSession] = {}

@app.post("/games", response_model=GameResponse)
async def create_game(config: GameConfig):
    """Create a new poker game"""
    game_id = str(uuid.uuid4())
    session = GameSession(game_id, config)
    active_games[game_id] = session
    return GameResponse(game_id=game_id, status="created")

@app.get("/games/{game_id}/state")
async def get_game_state(game_id: str):
    """Get current game state"""
    session = active_games.get(game_id)
    if not session:
        raise HTTPException(404, "Game not found")
    return session.get_state()

@app.post("/games/{game_id}/actions")
async def take_action(game_id: str, action: PlayerAction):
    """Execute a player action"""
    session = active_games.get(game_id)
    if not session:
        raise HTTPException(404, "Game not found")
    return await session.execute_action(action)
```

### Phase 2: WebSocket Integration (Week 2)
```python
@app.websocket("/games/{game_id}/ws")
async def game_websocket(websocket: WebSocket, game_id: str):
    """Real-time game updates"""
    await websocket.accept()
    session = active_games.get(game_id)
    
    try:
        while True:
            # Listen for player actions
            data = await websocket.receive_json()
            result = await session.execute_action(data)
            
            # Broadcast game state updates
            await websocket.send_json({
                "type": "game_update",
                "state": session.get_state(),
                "action_result": result
            })
    except WebSocketDisconnect:
        await session.remove_player(websocket)
```

### Phase 3: Game Session Management
```python
# app/models/game_session.py
class GameSession:
    def __init__(self, game_id: str, config: GameConfig):
        self.game_id = game_id
        self.game = TexasHoldEm(**config.to_dict())
        self.agent_config = create_agent_config(config.agents)
        self.connected_players: Dict[int, WebSocket] = {}
        self.game_history = []
    
    async def execute_action(self, action: PlayerAction):
        """Execute action and update all connected clients"""
        # Use your existing game engine
        result = self.game.take_action(action.type, action.amount)
        
        # Record in history
        self.game_history.append({
            "timestamp": datetime.now(),
            "player_id": action.player_id,
            "action": action.type.name,
            "amount": action.amount
        })
        
        # Notify all connected players
        await self.broadcast_update()
        return result
    
    def get_state(self) -> GameState:
        """Convert your game state to API format"""
        return GameState(
            game_id=self.game_id,
            phase=self.game.hand_phase.name,
            current_player=self.game.current_player,
            board=[card.pretty_string for card in self.game.board],
            pot_total=sum(pot.get_total_amount() for pot in self.game.pots),
            players=[self._format_player(i) for i in range(self.game.max_players)],
            available_actions=self._get_available_actions()
        )
```

## Data Models
```python
# app/models/schemas.py
from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum

class ActionType(str, Enum):
    FOLD = "FOLD"
    CHECK = "CHECK"
    CALL = "CALL"
    RAISE = "RAISE"

class GameConfig(BaseModel):
    max_players: int = 6
    buyin: int = 1000
    big_blind: int = 20
    small_blind: int = 10
    agents: Dict[int, str]  # player_id -> agent_name

class PlayerAction(BaseModel):
    player_id: int
    action_type: ActionType
    amount: Optional[int] = None

class GameState(BaseModel):
    game_id: str
    phase: str
    current_player: int
    board: List[str]
    pot_total: int
    players: List[Dict]
    available_actions: List[ActionType]
```

## API Endpoints Design

### Game Management
- `POST /games` - Create new game
- `GET /games/{id}` - Get game info
- `DELETE /games/{id}` - End game
- `GET /games/{id}/state` - Current state
- `GET /games/{id}/history` - Game history

### Player Actions  
- `POST /games/{id}/actions` - Execute action
- `GET /games/{id}/available-actions` - Valid moves
- `POST /games/{id}/join` - Join as human player

### Agent Management
- `GET /agents` - List available agents
- `POST /games/{id}/agents` - Add AI agent
- `PUT /games/{id}/agents/{player_id}` - Update agent

### Real-time
- `WS /games/{id}/ws` - WebSocket for live updates

## Integration with Your Existing System

### CLI Client Becomes API Client
```python
# cli_client.py - New wrapper for your existing CLI
class APIGameClient:
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.base_url = api_base_url
        self.game_id = None
    
    def create_game(self, config: dict):
        response = requests.post(f"{self.base_url}/games", json=config)
        self.game_id = response.json()["game_id"]
    
    def get_state(self):
        response = requests.get(f"{self.base_url}/games/{self.game_id}/state")
        return response.json()
    
    def take_action(self, action_type: str, amount: int = None):
        response = requests.post(
            f"{self.base_url}/games/{self.game_id}/actions",
            json={"action_type": action_type, "amount": amount}
        )
        return response.json()

# main.py - Minimal changes to existing CLI
def run_api_game():
    client = APIGameClient()
    config = {
        "max_players": 6,
        "agents": {0: "human", 1: "gpt_4_1_balanced", 2: "llama_aggressive"}
    }
    client.create_game(config)
    
    # Your existing display logic works with client.get_state()
    # Your existing input handling works with client.take_action()
```

## Benefits of This Approach

1. **Zero Breaking Changes**: Your CLI continues working exactly as before
2. **Immediate Value**: API can be used for automation, testing, tournaments
3. **Future-Proof**: Foundation for web UI, mobile apps, integrations
4. **Better Testing**: API endpoints are easier to test than CLI
5. **Deployment Ready**: Docker container, cloud deployment
6. **Analytics Ready**: Database integration for advanced statistics

## Timeline Estimate

- **Week 1**: Core FastAPI setup, basic endpoints
- **Week 2**: WebSocket integration, game session management  
- **Week 3**: CLI client refactoring, testing
- **Week 4**: Database integration, deployment setup

## Why NOT the Other Options (Yet)

### Enhanced Game Output
- **Good idea but tactical**: This improves UX but doesn't change architecture
- **Do this after FastAPI**: API makes it easier to display rich results

### LLM Memory System  
- **Complex feature**: Requires careful design, could destabilize current system
- **Do this later**: API provides better foundation for persistent memory

### Test Suite
- **Important but not urgent**: Your existing tests are comprehensive
- **API makes testing easier**: REST endpoints are simpler to test than CLI

### Frontend Design
- **Premature without API**: Building UI directly on game engine creates tight coupling
- **FastAPI enables better frontend**: Clean separation, real-time updates

## Conclusion

FastAPI backend is the perfect next step because it:
- Preserves your excellent work
- Unlocks immediate new capabilities  
- Creates foundation for all future enhancements
- Positions you for production deployment

Your system is already impressive - this makes it truly scalable and professional. 