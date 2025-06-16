/**
 * 🔌 WebSocket Hook for Real-time Game Updates
 * Manages WebSocket connection to FastAPI backend
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { GameState, GameUpdateMessage, ErrorMessage } from '@/types/game';

interface UseWebSocketProps {
  gameId: string | null;
  onGameUpdate?: (gameState: GameState) => void;
  onError?: (error: string) => void;
  onConnectionChange?: (status: 'connecting' | 'connected' | 'disconnected' | 'error') => void;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
  lastMessage: any;
  sendMessage: (message: any) => void;
  reconnect: () => void;
}

export function useWebSocket({
  gameId,
  onGameUpdate,
  onError,
  onConnectionChange,
}: UseWebSocketProps): UseWebSocketReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  const [lastMessage, setLastMessage] = useState<any>(null);
  
  const websocketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  // Memoize callbacks to prevent infinite loops
  const onGameUpdateRef = useRef(onGameUpdate);
  const onErrorRef = useRef(onError);
  const onConnectionChangeRef = useRef(onConnectionChange);

  useEffect(() => {
    onGameUpdateRef.current = onGameUpdate;
    onErrorRef.current = onError;
    onConnectionChangeRef.current = onConnectionChange;
  });

  const updateConnectionStatus = useCallback((status: typeof connectionStatus) => {
    setConnectionStatus(status);
    setIsConnected(status === 'connected');
    onConnectionChangeRef.current?.(status);
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (websocketRef.current?.readyState === WebSocket.OPEN) {
      websocketRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, cannot send message:', message);
    }
  }, []);

  const connect = useCallback(() => {
    if (!gameId) return;

    // Don't connect if already connecting or connected
    if (websocketRef.current?.readyState === WebSocket.CONNECTING || 
        websocketRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const wsBaseUrl = process.env.NEXT_PUBLIC_WS_BASE_URL || 'ws://localhost:8000';
    const wsUrl = `${wsBaseUrl}/ws/games/${gameId}`;
    
    console.log('🔌 Connecting to WebSocket:', wsUrl);
    updateConnectionStatus('connecting');

    try {
      const ws = new WebSocket(wsUrl);
      websocketRef.current = ws;

      ws.onopen = () => {
        console.log('🔌 WebSocket connected');
        updateConnectionStatus('connected');
        reconnectAttemptsRef.current = 0;
        
        // Send ping to verify connection
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping' }));
        }
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);

          // Handle different message types
          switch (data.type) {
            case 'game_update':
              const updateMessage = data as GameUpdateMessage;
              onGameUpdateRef.current?.(updateMessage.game_state);
              break;
              
            case 'error':
              const errorMessage = data as ErrorMessage;
              console.error('🔌 WebSocket error message:', errorMessage.error);
              onErrorRef.current?.(errorMessage.error);
              break;
              
            case 'pong':
              // Connection is alive
              break;
              
            default:
              console.log('🔌 Unknown WebSocket message type:', data.type);
          }
        } catch (error) {
          console.error('🔌 Error parsing WebSocket message:', error);
        }
      };

      ws.onclose = (event) => {
        console.log('🔌 WebSocket closed:', event.code, event.reason);
        updateConnectionStatus('disconnected');
        
        // Attempt to reconnect unless it was a clean close
        if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 10000);
          console.log(`🔌 Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current + 1}/${maxReconnectAttempts})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++;
            connect();
          }, delay);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          console.error('🔌 Max reconnection attempts reached');
          updateConnectionStatus('error');
        }
      };

      ws.onerror = (error) => {
        console.error('🔌 WebSocket error:', error);
        updateConnectionStatus('error');
      };

    } catch (error) {
      console.error('🔌 Failed to create WebSocket:', error);
      updateConnectionStatus('error');
    }
  }, [gameId, updateConnectionStatus]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (websocketRef.current) {
      websocketRef.current.close(1000, 'Component unmounting');
      websocketRef.current = null;
    }

    updateConnectionStatus('disconnected');
  }, [updateConnectionStatus]);

  const reconnect = useCallback(() => {
    disconnect();
    reconnectAttemptsRef.current = 0;
    setTimeout(() => connect(), 100); // Small delay before reconnecting
  }, [disconnect, connect]);

  // Connect when gameId changes
  useEffect(() => {
    if (gameId) {
      connect();
    } else {
      disconnect();
    }

    return disconnect;
  }, [gameId, connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  // Ping interval to keep connection alive
  useEffect(() => {
    if (!isConnected) return;

    const pingInterval = setInterval(() => {
      if (websocketRef.current?.readyState === WebSocket.OPEN) {
        websocketRef.current.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000); // Ping every 30 seconds

    return () => clearInterval(pingInterval);
  }, [isConnected]);

  return {
    isConnected,
    connectionStatus,
    lastMessage,
    sendMessage,
    reconnect,
  };
} 