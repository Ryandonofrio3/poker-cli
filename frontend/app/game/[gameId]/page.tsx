'use client';

/**
 * 🎮 Game Page - Main Poker Interface
 * Real-time poker game with WebSocket updates
 */

import { useParams, useRouter } from 'next/navigation';
import { useGameState, useIsHumanTurn, useHumanPlayer } from '@/hooks/use-game-state';
import { PlayerAction } from '@/types/game';

import { GameBoard } from '@/components/game/game-board';
import { PlayersGrid } from '@/components/game/player-status';
import { ActionButtons } from '@/components/game/action-buttons';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';

import { 
  Home, 
  RefreshCw, 
  Wifi, 
  WifiOff, 
  AlertCircle,
  Trophy,
  Clock
} from 'lucide-react';

export default function GamePage() {
  const params = useParams();
  const router = useRouter();
  const gameId = params.gameId as string;

  const {
    gameState,
    isLoading,
    error,
    connectionStatus,
    executeAction,
    refreshState,
    isConnected,
    reconnect,
  } = useGameState({ gameId });

  const isHumanTurn = useIsHumanTurn(gameState);
  const humanPlayerId = useHumanPlayer(gameState);

  const handleAction = async (action: PlayerAction) => {
    const result = await executeAction(action);
    if (result && !result.success) {
      console.error('Action failed:', result.message);
    }
  };

  const getConnectionStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'text-green-600';
      case 'connecting': return 'text-yellow-600';
      case 'disconnected': return 'text-gray-600';
      case 'error': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getConnectionIcon = (status: string) => {
    switch (status) {
      case 'connected': return <Wifi className="w-4 h-4" />;
      case 'connecting': return <Clock className="w-4 h-4 animate-spin" />;
      default: return <WifiOff className="w-4 h-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
      <div className="container mx-auto px-4 py-6">
        
        {/* Header with connection status */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              onClick={() => router.push('/')}
              className="flex items-center gap-2"
            >
              <Home className="w-4 h-4" />
              New Game
            </Button>
            
            <div className="flex items-center gap-2">
              <Badge 
                variant="outline" 
                className={`flex items-center gap-1 ${getConnectionStatusColor(connectionStatus)}`}
              >
                {getConnectionIcon(connectionStatus)}
                {connectionStatus.charAt(0).toUpperCase() + connectionStatus.slice(1)}
              </Badge>
              
              {gameState && (
                <Badge variant="secondary">
                  Game ID: {gameId.slice(0, 8)}...
                </Badge>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={refreshState}
              disabled={isLoading}
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            </Button>
            
            {!isConnected && (
              <Button
                variant="outline"
                size="sm"
                onClick={reconnect}
                className="text-orange-600 border-orange-200 hover:bg-orange-50"
              >
                Reconnect
              </Button>
            )}
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <Alert className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Loading State */}
        {isLoading && !gameState && (
          <div className="space-y-6">
            <Skeleton className="h-64 w-full" />
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className="h-32" />
              ))}
            </div>
          </div>
        )}

        {/* Game Interface */}
        {gameState && (
          <div className="space-y-6">
            
            {/* Game Board */}
            <GameBoard gameState={gameState} />

            {/* Players Grid */}
            <PlayersGrid
              players={gameState.players}
              currentPlayer={gameState.current_player}
              humanPlayerId={humanPlayerId}
              showAllCards={gameState.debug_mode}
            />

            {/* Human Player Actions */}
            {isHumanTurn && humanPlayerId !== null && (
              <div className="flex justify-center">
                <div className="w-full max-w-md">
                  <ActionButtons
                    availableActions={gameState.available_actions}
                    minRaiseAmount={gameState.min_raise_amount}
                    currentChips={gameState.players.find(p => p.player_id === humanPlayerId)?.chips || 0}
                    chipsToCall={gameState.players.find(p => p.player_id === humanPlayerId)?.chips_to_call || 0}
                    onAction={handleAction}
                    playerId={humanPlayerId}
                    disabled={!isConnected || isLoading}
                  />
                </div>
              </div>
            )}

            {/* Game Status Messages */}
            {gameState.status === 'COMPLETED' && (
              <Card className="p-6 text-center bg-gradient-to-r from-yellow-50 to-green-50 border-yellow-200">
                <Trophy className="w-12 h-12 text-yellow-600 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  Game Complete!
                </h2>
                <p className="text-gray-600 mb-4">
                  Thanks for playing! Check out the final results above.
                </p>
                <Button onClick={() => router.push('/')} size="lg">
                  Play Again
                </Button>
              </Card>
            )}

            {gameState.status === 'WAITING' && (
              <Card className="p-4 text-center bg-blue-50 border-blue-200">
                <Clock className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                <p className="text-blue-800 font-medium">
                  Waiting for more players to join...
                </p>
              </Card>
            )}

            {gameState.current_player !== null && !isHumanTurn && (
              <Card className="p-4 text-center bg-gray-50 border-gray-200">
                <div className="flex items-center justify-center gap-2 text-gray-600">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                  <span>
                    Waiting for {gameState.players.find(p => p.player_id === gameState.current_player)?.agent_name || `Player ${gameState.current_player}`}...
                  </span>
                </div>
              </Card>
            )}

          </div>
        )}

        {/* Game not found */}
        {!isLoading && !gameState && !error && (
          <Card className="p-8 text-center">
            <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Game Not Found
            </h2>
            <p className="text-gray-600 mb-4">
              The game you're looking for might have ended or the ID is incorrect.
            </p>
            <Button onClick={() => router.push('/')}>
              <Home className="w-4 h-4 mr-2" />
              Back to Home
            </Button>
          </Card>
        )}

      </div>
    </div>
  );
} 