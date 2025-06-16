# COMPREHENSIVE TODO: Texas Hold'em CLI with LLM Agents

## OVERVIEW
Build a command-line interface system using the `texasholdem` package to create poker games with different agent types, ultimately connecting large language models to play against each other. All implementations must be grounded in the actual documented API.

**✅ PHASE 1 COMPLETED** - Foundation is solid and working!
**✅ PHASE 2 COMPLETED** - Custom agents implemented and working!
**✅ PHASE 3 COMPLETED** - LLM integration working with GPT-4.1 and Llama!

---

## ✅ PHASE 1: FOUNDATION - CLI Game Engine (COMPLETED)

### ✅ 1.1 Core Game CLI Implementation
**Grounded in:** `TexasHoldEm` class API from `holdem_docs/api/holdem.md`

- ✅ **Create main CLI game loop** using documented methods:
  - `TexasHoldEm(buyin, big_blind, small_blind, max_players)` constructor
  - `game.is_game_running()` for main loop condition
  - `game.start_hand()` to initiate each hand
  - `game.is_hand_running()` for hand loop condition
  
- ✅ **Implement game state display** using documented properties:
  - `game.current_player` - whose turn it is
  - `game.board` - community cards (List[Card])
  - `game.hand_phase` - current phase (PREHAND, PREFLOP, FLOP, TURN, RIVER, SETTLE)
  - `game.players[player_id].chips` - player chip counts
  - `game.players[player_id].state` - player states (IN, OUT, TO_CALL, ALL_IN, SKIP)
  - `game.get_hand(player_id)` - player hole cards
  - `game.pots[pot_id].get_total_amount()` - pot amounts

- ✅ **Action validation and execution** using documented methods:
  - `game.get_available_moves()` returns `MoveIterator` with valid actions
  - `game.validate_move(player_id, action, total)` for validation
  - `game.take_action(action_type, total)` for execution
  - `game.chips_to_call(player_id)` for call amounts
  - `game.min_raise()` for minimum raise amounts

### ✅ 1.2 Built-in Agent Integration
**Grounded in:** `texasholdem.agents.basic` from `holdem_docs/agents.md`

- ✅ **Import and test existing agents:**
  - `from texasholdem.agents import random_agent, call_agent`
  - `random_agent(game, no_fold=False)` returns `(ActionType, total)`
  - `call_agent(game)` returns `(ActionType, None)`

- ✅ **Create agent selection system:**
  - Map player positions to agent functions
  - Support mixed human/agent games
  - Use documented pattern: `game.take_action(*agent_function(game))`

- ✅ **Custom aggressive agent workaround:** Fixed upstream bug in `random_agent(no_fold=True)`

### ✅ 1.3 Game History and Export
**Grounded in:** `History` class from `holdem_docs/game_history.md`

- ✅ **Implement game recording:**
  - `game.export_history(path)` to save PGN files
  - `game.hand_history` property for current hand data
  - Store games in `./game_logs/` directory

---

## ✅ PHASE 2: CUSTOM AGENT FRAMEWORK (COMPLETED)

### ✅ 2.1 Agent Architecture Enhancement
**Grounded in:** Custom agent patterns from `holdem_docs/custom_agents.md`

- ✅ **Created enhanced agent base functions:**
  ```python
  def create_passive_agent() -> AgentFunction:
      # Prefers CHECK/CALL, avoids aggressive plays
      
  def create_tight_agent() -> AgentFunction:
      # Folds more often, only plays strong hands
      
  def create_loose_agent() -> AgentFunction:
      # Plays more hands, calls more often
      
  def create_bluff_agent() -> AgentFunction:
      # Occasionally raises with weak hands
      
  def create_position_aware_agent() -> AgentFunction:
      # Adjusts play based on table position
  ```

### ✅ 2.2 Hand Strength Analysis Tools
**Grounded in:** Available game state from `TexasHoldEm` class

- ✅ **Created hand evaluation helpers:**
  ```python
  def evaluate_hand_strength(game: TexasHoldEm, player_id: int) -> float:
      # Use texasholdem.evaluator to get hand strength (0.0-1.0)
      
  def get_pot_odds(game: TexasHoldEm, player_id: int) -> float:
      # Calculate pot odds for calling decisions
      
  def should_be_aggressive(hand_strength: float, pot_odds: float) -> bool:
      # Decision logic for aggressive play
  ```

### ✅ 2.3 Advanced Agent Behaviors
**Building on documented game state access**

- ✅ **Position-aware agents:** Use `game.current_player` and button position
- ✅ **Stack-size aware agents:** Use `game.players[player_id].chips` for decisions
- ✅ **Personality-based decision making:** Different risk tolerances and play styles

---

## ✅ PHASE 3: LLM INTEGRATION SYSTEM (COMPLETED!)

### ✅ 3.1 Enhanced Prompt Builder
**Grounded in:** Current `prompt_builder.py` and documented game state

- ✅ **Expanded prompt_builder.py to use ALL documented game information:**
  ```python
  def create_llm_prompt(game: TexasHoldEm, player_id: int, **kwargs) -> str:
      # Use game.hand_phase enum value
      # Use game.board for community cards  
      # Use game.get_hand(player_id) for hole cards
      # Use game.chips_to_call(player_id) for betting context
      # Use game.players[player_id].chips for stack size
      # Use game.get_available_moves() for valid actions
      # Include pot odds and hand strength analysis
  ```

- ✅ **Created personality-specific prompt templates:**
  - Balanced, Aggressive, Conservative, Mathematical, Bluffer personalities
  - Phase-specific prompts for PREFLOP, FLOP, TURN, RIVER
  - Comprehensive game state analysis in prompts

### ✅ 3.2 Multi-LLM Agent Implementation
**Following agent interface from `holdem_docs/custom_agents.md`**

- ✅ **Created LLM agent wrapper:**
  ```python
  def create_llm_agent(model_name: str, **config) -> AgentFunction:
      def llm_agent(game: TexasHoldEm) -> Tuple[ActionType, Optional[int]]:
          # Generate prompt using enhanced prompt_builder
          # Query specified LLM
          # Parse response to ActionType and amount
          # Validate using game.validate_move()
          # Return (ActionType, total) tuple
      return llm_agent
  ```

- ✅ **Support multiple LLM providers:**
  - ✅ OpenAI GPT-4.1 models (Premium, structured outputs)
  - ✅ Meta Llama 3.1 models (Free, good performance)
  - ✅ Google Gemma models (Free, text parsing fallback)
  - ✅ OpenRouter API integration with structured outputs
  - ✅ Automatic fallback from structured to text parsing

### ✅ 3.3 Response Parsing and Validation
**Grounded in:** `ActionType` enum and validation methods

- ✅ **Created robust response parser:**
  - ✅ Structured JSON output parsing for supported models
  - ✅ Text parsing fallback for unsupported models
  - ✅ Maps LLM responses to `ActionType.CHECK`, `ActionType.CALL`, `ActionType.FOLD`, `ActionType.RAISE`
  - ✅ Handles raise amounts using `game.min_raise()` constraints
  - ✅ Fallback to `call_agent` behavior on parse failures
  - ✅ Comprehensive error logging for debugging

---

## 🎮 PHASE 4: HUMAN PLAYER INTEGRATION (NEXT PRIORITY)

### 4.1 Human Input System
**Building on existing CLI framework**

- [ ] **Create human player input functions:**
  ```python
  def get_human_action(game: TexasHoldEm, player_id: int) -> Tuple[ActionType, Optional[int]]:
      # Display available actions to human
      # Accept input via CLI (fold/check/call/raise X)
      # Validate input against available moves
      # Return properly formatted action tuple
  ```

- [ ] **Enhanced display for human players:**
  - Show only human player's cards (hide others)
  - Display pot odds and hand strength hints
  - Clear action input prompts
  - Help system for poker rules

### 4.2 Mixed Game Configuration
**Extending agent_manager.py**

- [ ] **Flexible game setup:**
  ```python
  def create_mixed_game_config() -> Dict[int, Union[AgentFunction, str]]:
      # Map player_id to:
      # - "human" for human players
      # - AgentFunction for AI agents  
      # - LLM agent functions
      # Support any combination
  ```

---

## 🎯 ULTIMATE GOAL: MIXED HUMAN/AI/LLM GAMES

### ✅ Current Game Configurations (Working!):
- ✅ **GPT-4.1 Showcase:** 5 different GPT-4.1 agents + 1 Llama
- ✅ **LLM Battle:** 6 different LLMs with unique personalities
- ✅ **Premium vs Free:** GPT-4.1 vs Llama vs Gemma
- ✅ **LLM vs AI:** Mixed LLM and traditional AI agents
- ✅ **Custom AI Showcase:** 6 different traditional AI personalities

### Target Mixed Game Configurations:
- [ ] **6-Player Mixed:** 2 Humans + 2 AI Agents + 2 LLMs
- [ ] **Human vs LLM:** 1 Human + 5 varied LLM opponents
- [ ] **Testing Setup:** 1 Human + 1 LLM + 4 basic agents

### Features for Mixed Games:
- [ ] **Flexible player assignment** during game creation
- ✅ **Real-time player type display** (Human/Agent/LLM)
- [ ] **Pause/resume functionality** for human thinking time
- ✅ **Action logging** with player type attribution
- [ ] **Performance analytics** comparing different player types

---

## 🐛 CRITICAL BUG FIXES COMPLETED

### ✅ Bug #1: texasholdem Package - random_agent(no_fold=True)
**Status:** ✅ Fixed with custom workaround

### ✅ Bug #2: Agent Configuration Naming Inconsistency  
**Date:** June 6, 2025  
**Status:** ✅ Fixed  
**Issue:** Configuration used `"gpt-4.1_balanced"` (hyphen) but agent creation checked for `"gpt_4_1_balanced"` (underscore)
**Fix:** Updated all configuration functions to use consistent underscore naming
**Impact:** GPT-4.1 agents now work perfectly in all game modes

### ✅ Bug #3: texasholdem Package - Phantom Pot Chips After Hand Completion
**Date:** June 15, 2025  
**Status:** ✅ Fixed with phantom chip clearing  
**Issue:** When hands end by folding, pot distribution works correctly but phantom chips remain in pot, causing chip duplication (2030 chips instead of 2000).
**Root Cause:** texasholdem package distributes pot to winner correctly but doesn't clear the pot afterward
**Fix:** Simple `clear_phantom_pot_chips()` function clears phantom chips after hand completion
**Impact:** ✅ Chip conservation restored, multi-hand games work perfectly, tests passing

---


## PHASE 6: FASTAPI BACKEND FOR FRONTEND INTEGRATION (FUTURE)

### 6.1 FastAPI Application Setup
**Grounded in:** Game state properties and history system from documentation

- [ ] **Core FastAPI application** with WebSocket support
- [ ] **Real-time game state API** endpoints
- [ ] **Performance analytics API** for frontend visualization

---

## TECHNICAL REQUIREMENTS

### Dependencies (All Working!)
- ✅ `uv pip install texasholdem` - Core poker engine
- ✅ `uv pip install colorama` - Terminal colors
- ✅ `uv pip install openai requests python-dotenv` - LLM integrations
- ✅ Required imports based on documentation:
  ```python
  from texasholdem import TexasHoldEm, ActionType, HandPhase, Card
  from texasholdem.agents import random_agent, call_agent
  from texasholdem.evaluator import evaluate, rank_to_string
  ```

### Error Handling (Comprehensive!)
- ✅ Validate all actions using `game.validate_move()`
- ✅ Handle invalid agent responses with fallback to `call_agent`
- ✅ Graceful handling of game exceptions
- ✅ LLM timeout and error handling with structured/text parsing fallback
- ✅ Comprehensive debugging and error logging

### Testing Strategy (Robust!)
- ✅ Unit tests for each agent type  
- ✅ Integration tests using `game.import_history()` for replay
- ✅ LLM integration testing with multiple models
- ✅ Debug scripts for isolating issues
- ✅ Game configuration validation tests

---

## IMPLEMENTATION STATUS (UPDATED!)

1. ✅ **Phase 1 Complete** - Foundation working perfectly
2. ✅ **Phase 2 Complete** - Custom AI agents with diverse personalities  
3. ✅ **Phase 3 Complete** - LLM integration with GPT-4.1, Llama, Gemma
4. 🎯 **Phase 4 - Human Players** - Enable human participation (NEXT)
5. 🎪 **Mixed Game Testing** - Human + AI + LLM games (READY)
6. 🏆 **Phase 5 - Advanced Features** - Polish and enhance
7. 🌐 **Phase 6 - FastAPI Backend** - Web interface preparation

**Current Status:** 🎉 **MASSIVE SUCCESS!** 
- ✅ LLM vs LLM battles working perfectly
- ✅ GPT-4.1 structured outputs with strategic reasoning
- ✅ 5 different LLM personalities + 6 AI agent types
- ✅ Mixed agent games with beautiful CLI interface
- 🎯 Ready for human player integration!

**Next Session Goal:** Add human player input system to enable the ultimate mixed human/AI/LLM poker games!

All implementations use only documented methods and properties from the texasholdem package. Refer to `holdem_docs/` for exact API specifications.