/**
 * 🎲 Game Board Component
 * Central board showing community cards, pot, and game phase
 */

import { GameState, getPhaseDisplay } from '@/types/game';
import { cn } from '@/lib/utils';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CardGroup, EmptyCard } from './card-display';
import { Coins, Clock, Trophy } from 'lucide-react';

interface GameBoardProps {
  gameState: GameState;
  className?: string;
}

export function GameBoard({ gameState, className }: GameBoardProps) {
  // Create array of 5 cards (community cards + empty placeholders)
  const boardCards = Array.from({ length: 5 }, (_, index) => 
    gameState.board[index] || null
  );

  // Get phase color
  const getPhaseColor = (phase: string) => {
    switch (phase) {
      case 'PREHAND': return 'bg-gray-100 text-gray-700';
      case 'PREFLOP': return 'bg-blue-100 text-blue-700';
      case 'FLOP': return 'bg-green-100 text-green-700';
      case 'TURN': return 'bg-yellow-100 text-yellow-700';
      case 'RIVER': return 'bg-red-100 text-red-700';
      case 'SETTLE': return 'bg-purple-100 text-purple-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <Card className={cn('p-6 bg-gradient-to-br from-green-50 to-green-100 border-green-200', className)}>
      {/* Game info header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Badge 
            variant="outline" 
            className={cn('text-sm font-semibold', getPhaseColor(gameState.phase))}
          >
            <Clock className="w-4 h-4 mr-1" />
            {getPhaseDisplay(gameState.phase)}
          </Badge>
          
          <Badge variant="outline" className="text-sm">
            Hand {gameState.hand_number + 1} / {gameState.max_hands}
          </Badge>
        </div>

        <div className="text-right">
          <p className="text-sm text-gray-600">Game Status</p>
          <Badge 
            variant={gameState.status === 'RUNNING' ? 'default' : 'secondary'}
            className="capitalize"
          >
            {gameState.status.toLowerCase()}
          </Badge>
        </div>
      </div>

      {/* Community cards */}
      <div className="text-center mb-6">
        <h2 className="text-lg font-semibold text-gray-700 mb-4">Community Cards</h2>
        <div className="flex justify-center">
          <div className="flex gap-2">
            {boardCards.map((card, index) => (
              <div key={index}>
                {card ? (
                  <CardGroup 
                    cards={[card]} 
                    size="lg" 
                    animated={true}
                  />
                ) : (
                  <EmptyCard size="lg" />
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Pot information */}
      <div className="bg-white rounded-lg p-4 shadow-sm border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Coins className="w-5 h-5 text-yellow-600" />
            <span className="font-semibold text-gray-700">Total Pot</span>
          </div>
          <div className="text-2xl font-bold text-green-600">
            ${gameState.total_pot.toLocaleString()}
          </div>
        </div>
      </div>

      {/* Game completion indicator */}
      {gameState.status === 'COMPLETED' && (
        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-center">
          <Trophy className="w-6 h-6 text-yellow-600 mx-auto mb-2" />
          <p className="font-semibold text-yellow-800">Game Completed!</p>
        </div>
      )}
    </Card>
  );
} 