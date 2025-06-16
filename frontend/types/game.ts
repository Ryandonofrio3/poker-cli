/**
 * 🃏 Game Types - Mirror of FastAPI Backend Schemas
 * These types ensure type safety between frontend and backend
 */

// Enums for type safety
export type ActionType = 'FOLD' | 'CHECK' | 'CALL' | 'RAISE';
export type HandPhase = 'PREHAND' | 'PREFLOP' | 'FLOP' | 'TURN' | 'RIVER' | 'SETTLE';
export type PlayerState = 'IN' | 'OUT' | 'TO_CALL' | 'ALL_IN' | 'SKIP';
export type GameStatus = 'WAITING' | 'RUNNING' | 'PAUSED' | 'COMPLETED' | 'ERROR';

// Card representation
export interface Card {
  rank: string;          // "A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"
  suit: string;          // "♠", "♥", "♦", "♣"
  pretty_string: string; // "A♠", "K♥", etc.
}

// Player information
export interface PlayerInfo {
  player_id: number;
  chips: number;
  state: PlayerState;
  agent_type: string;
  agent_name: string;
  hole_cards?: Card[] | null;  // Only visible for human player or debug mode
  is_current_player: boolean;
  chips_to_call: number;
  hand_strength?: number | null;  // 0.0-1.0, debug mode only
}

// Pot information
export interface PotInfo {
  pot_id: number;
  total_amount: number;
  eligible_players: number[];
}

// Main game state
export interface GameState {
  game_id: string;
  status: GameStatus;
  phase: HandPhase;
  current_player: number | null;
  hand_number: number;
  max_hands: number;
  
  // Cards and board
  board: Card[];
  
  // Players and pots
  players: PlayerInfo[];
  pots: PotInfo[];
  total_pot: number;
  
  // Available actions
  available_actions: ActionType[];
  min_raise_amount: number | null;
  
  // Game configuration
  big_blind: number;
  small_blind: number;
  debug_mode: boolean;
  
  // Timing
  created_at: string;    // ISO string
  updated_at: string;    // ISO string
}

// Request types
export interface GameConfig {
  max_players?: number;
  buyin?: number;
  big_blind?: number;
  small_blind?: number;
  max_hands?: number;
  agents?: Record<number, string>;  // player_id -> agent_type
  preset?: string;
  debug_mode?: boolean;
}

export interface PlayerAction {
  player_id: number;
  action_type: ActionType;
  amount?: number;  // Required for RAISE
}

export interface JoinGameRequest {
  player_name?: string;
  agent_type?: string;
}

// Response types
export interface GameCreated {
  game_id: string;
  message: string;
  websocket_url: string;
  initial_state: GameState;
}

export interface ActionResult {
  success: boolean;
  message: string;
  action_type: ActionType;
  amount?: number;
  player_id: number;
  new_state?: GameState;
}

export interface GameHistory {
  game_id: string;
  total_hands: number;
  duration_minutes: number;
  final_results: Array<{
    player_id: number;
    agent_name: string;
    final_chips: number;
    profit_loss: number;
  }>;
  hand_history: Array<Record<string, any>>;
}

export interface AvailableAgent {
  agent_id: string;
  name: string;
  description: string;
  category: 'AI' | 'LLM' | 'Human';
  is_available: boolean;
}

export interface PresetConfig {
  preset_id: string;
  name: string;
  description: string;
  config: GameConfig;
}

// WebSocket message types
export interface WebSocketMessage {
  type: string;
  timestamp: string;
}

export interface GameUpdateMessage extends WebSocketMessage {
  type: 'game_update';
  game_state: GameState;
  last_action?: Record<string, any>;
}

export interface PlayerActionMessage extends WebSocketMessage {
  type: 'player_action';
  action: PlayerAction;
}

export interface ErrorMessage extends WebSocketMessage {
  type: 'error';
  error: string;
  details?: Record<string, any>;
}

// API Response wrapper
export interface APIResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  errors?: string[];
}

// Utility types for UI
export interface GameUIState {
  isLoading: boolean;
  error: string | null;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
}

// Helper type for human player detection
export function isHumanPlayer(player: PlayerInfo): boolean {
  return player.agent_type === 'human';
}

// Helper type for card suit colors
export function getCardSuitColor(suit: string): 'red' | 'black' {
  return suit === '♥' || suit === '♦' ? 'red' : 'black';
}

// Helper type for game phase display
export function getPhaseDisplay(phase: HandPhase): string {
  const phaseMap: Record<HandPhase, string> = {
    PREHAND: 'Pre-Hand',
    PREFLOP: 'Pre-Flop',
    FLOP: 'Flop',
    TURN: 'Turn', 
    RIVER: 'River',
    SETTLE: 'Settlement'
  };
  return phaseMap[phase] || phase;
}

// Helper for action button labels
export function getActionLabel(action: ActionType, amount?: number): string {
  switch (action) {
    case 'FOLD': return 'Fold';
    case 'CHECK': return 'Check';
    case 'CALL': return 'Call';
    case 'RAISE': return amount ? `Raise $${amount}` : 'Raise';
    default: return action;
  }
} 