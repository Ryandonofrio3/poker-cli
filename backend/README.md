# 🃏 Texas Hold'em FastAPI Backend

**Production-ready poker API with LLM integration and real-time gameplay.**

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Your existing poker CLI system working
- OpenRouter API key for LLM agents (optional)

### Installation

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   # Copy from your main project's .env
   cp ../.env .env
   ```

3. **Run the API:**
   ```bash
   python run.py
   ```

4. **Access the API:**
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## 📊 API Endpoints

### 🎮 Games
- `POST /api/v1/games` - Create new game
- `GET /api/v1/games/{game_id}/state` - Get game state  
- `POST /api/v1/games/{game_id}/actions` - Execute action
- `WS /ws/games/{game_id}` - Real-time updates

### 🤖 Agents  
- `GET /api/v1/agents` - List available agents
- `GET /api/v1/agents/{agent_id}` - Get agent details
- `GET /api/v1/agents/llm/status` - LLM availability

## 🎯 Example Usage

### Create a Game
```bash
curl -X POST "http://localhost:8000/api/v1/games" \
     -H "Content-Type: application/json" \
     -d '{
       "max_players": 6,
       "buyin": 1000,
       "agents": {
         "0": "human",
         "1": "gpt_4_1_balanced", 
         "2": "llama_aggressive"
       }
     }'
```

### Execute Action
```bash
curl -X POST "http://localhost:8000/api/v1/games/{game_id}/actions" \
     -H "Content-Type: application/json" \
     -d '{
       "player_id": 0,
       "action_type": "RAISE",
       "amount": 40
     }'
```

## 🏗️ Architecture

Your existing CLI system is now wrapped in a scalable FastAPI backend with:
- **Zero breaking changes** to existing code
- **Real-time WebSocket** updates
- **Production-ready** deployment
- **Comprehensive API** documentation

## 🎮 Available Presets

- **test** - Quick 2-player game
- **balanced** - 6-player AI mix
- **human_vs_llm** - Human vs LLM agents
- **llm_showcase** - LLM agent demonstration

## 🤖 Agent Types

- **Traditional AI:** random, call, tight, loose, bluff
- **LLM Agents:** GPT-4.1, Llama 3.1, Gemma 3 
- **Human Players:** Manual input via API/WebSocket

**Your poker system just became production-ready!** 🚀