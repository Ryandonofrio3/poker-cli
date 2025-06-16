/**
 * 🎮 Game State Hook
 * Combines REST API calls with WebSocket updates for complete game state management
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { apiClient } from '@/lib/api-client';
import { useWebSocket } from './use-websocket';
import { GameState, PlayerAction, ActionResult, GameUIState } from '@/types/game';

interface UseGameStateProps {
  gameId: string | null;
  autoRefresh?: boolean;
}

interface UseGameStateReturn extends GameUIState {
  gameState: GameState | null;
  executeAction: (action: PlayerAction) => Promise<ActionResult | null>;
  refreshState: () => Promise<void>;
  isConnected: boolean;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
  reconnect: () => void;
}

export function useGameState({ 
  gameId, 
  autoRefresh = true 
}: UseGameStateProps): UseGameStateReturn {
  
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Use refs to prevent infinite loops
  const gameIdRef = useRef(gameId);
  const autoRefreshRef = useRef(autoRefresh);
  
  useEffect(() => {
    gameIdRef.current = gameId;
    autoRefreshRef.current = autoRefresh;
  });

  // Memoized callbacks for WebSocket
  const handleGameUpdate = useCallback((newGameState: GameState) => {
    console.log('🔄 Game state updated via WebSocket');
    setGameState(newGameState);
    setError(null); // Clear any previous errors
  }, []);

  const handleWebSocketError = useCallback((wsError: string) => {
    console.error('🔌 WebSocket error:', wsError);
    setError(`Connection error: ${wsError}`);
  }, []);

  const handleConnectionChange = useCallback((status: 'connecting' | 'connected' | 'disconnected' | 'error') => {
    console.log('🔌 Connection status:', status);
    if (status === 'error') {
      setError('Connection lost. Trying to reconnect...');
    } else if (status === 'connected') {
      setError(null);
    }
  }, []);

  // WebSocket for real-time updates
  const { 
    isConnected, 
    connectionStatus, 
    reconnect 
  } = useWebSocket({
    gameId,
    onGameUpdate: handleGameUpdate,
    onError: handleWebSocketError,
    onConnectionChange: handleConnectionChange
  });

  // Fetch game state from API
  const refreshState = useCallback(async () => {
    const currentGameId = gameIdRef.current;
    if (!currentGameId) return;

    setIsLoading(true);
    setError(null);

    try {
      const state = await apiClient.getGameState(currentGameId);
      setGameState(state);
      console.log('📊 Game state refreshed from API');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch game state';
      setError(errorMessage);
      console.error('❌ Error fetching game state:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Execute player action
  const executeAction = useCallback(async (action: PlayerAction): Promise<ActionResult | null> => {
    const currentGameId = gameIdRef.current;
    if (!currentGameId) return null;

    setIsLoading(true);
    setError(null);

    try {
      console.log('🎯 Executing action:', action);
      const result = await apiClient.executeAction(currentGameId, action);
      
      if (result.success) {
        console.log('✅ Action successful:', result.message);
        // WebSocket will update the state automatically
        // But if WebSocket is disconnected, use the returned state
        if (!isConnected && result.new_state) {
          setGameState(result.new_state);
        }
      } else {
        console.warn('⚠️ Action failed:', result.message);
        setError(result.message);
      }
      
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to execute action';
      setError(errorMessage);
      console.error('❌ Error executing action:', err);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [isConnected]);

  // Initial load when gameId changes
  useEffect(() => {
    if (gameId) {
      refreshState();
    } else {
      setGameState(null);
      setError(null);
      setIsLoading(false);
    }
  }, [gameId, refreshState]);

  // Auto-refresh fallback when WebSocket is disconnected
  useEffect(() => {
    if (!gameId || !autoRefresh || isConnected) return;

    const interval = setInterval(() => {
      console.log('🔄 Auto-refreshing (WebSocket disconnected)');
      refreshState();
    }, 5000); // Refresh every 5 seconds when WebSocket is down (increased from 3s)

    return () => clearInterval(interval);
  }, [gameId, autoRefresh, isConnected, refreshState]);

  return {
    gameState,
    isLoading,
    error,
    connectionStatus,
    executeAction,
    refreshState,
    isConnected,
    reconnect,
  };
}

// Helper hook for checking if current player is human
export function useIsHumanTurn(gameState: GameState | null): boolean {
  if (!gameState || gameState.current_player === null) return false;
  
  const currentPlayer = gameState.players.find(p => p.player_id === gameState.current_player);
  return currentPlayer?.agent_type === 'human' || false;
}

// Helper hook for getting current human player
export function useHumanPlayer(gameState: GameState | null): number | null {
  if (!gameState) return null;
  
  const humanPlayer = gameState.players.find(p => p.agent_type === 'human');
  return humanPlayer?.player_id ?? null;
}