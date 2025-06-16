/**
 * 👤 Player Status Component
 * Displays player information, chips, status, and cards
 */

import { PlayerInfo, isHumanPlayer } from '@/types/game';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { CardGroup } from './card-display';
import { User, Bot, Crown, Timer } from 'lucide-react';

interface PlayerStatusProps {
  player: PlayerInfo;
  isCurrentPlayer: boolean;
  showCards: boolean;
  position?: 'top' | 'right' | 'bottom' | 'left';
  compact?: boolean;
  className?: string;
}

export function PlayerStatus({ 
  player, 
  isCurrentPlayer, 
  showCards,
  position = 'bottom',
  compact = false,
  className 
}: PlayerStatusProps) {
  
  const isHuman = isHumanPlayer(player);
  
  // Get chip color based on amount
  const getChipColor = (chips: number) => {
    if (chips > 1500) return 'text-green-600 bg-green-50 border-green-200';
    if (chips > 800) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    if (chips > 300) return 'text-orange-600 bg-orange-50 border-orange-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  // Get state color and label
  const getStateDisplay = (state: string) => {
    switch (state) {
      case 'IN': return { label: 'In Hand', color: 'bg-green-500' };
      case 'TO_CALL': return { label: 'To Call', color: 'bg-yellow-500' };
      case 'ALL_IN': return { label: 'All In', color: 'bg-red-500' };
      case 'OUT': return { label: 'Folded', color: 'bg-gray-400' };
      case 'SKIP': return { label: 'Skip', color: 'bg-gray-400' };
      default: return { label: state, color: 'bg-gray-400' };
    }
  };

  const stateDisplay = getStateDisplay(player.state);

  return (
    <div className={cn(
      'relative rounded-lg border-2 bg-white shadow-md transition-all duration-300',
      isCurrentPlayer 
        ? 'border-blue-500 bg-blue-50 shadow-lg scale-105' 
        : 'border-gray-200 hover:border-gray-300',
      player.state === 'OUT' && 'opacity-60',
      compact ? 'p-2' : 'p-4',
      className
    )}>
      
      {/* Current player indicator */}
      {isCurrentPlayer && (
        <div className="absolute -top-2 -right-2 w-4 h-4 bg-blue-500 rounded-full animate-pulse">
          <Timer className="w-3 h-3 text-white absolute top-0.5 left-0.5" />
        </div>
      )}

      {/* Player avatar and info */}
      <div className={cn(
        'flex items-center gap-3',
        compact && 'gap-2'
      )}>
        <Avatar className={cn(compact ? 'w-8 h-8' : 'w-12 h-12')}>
          <AvatarFallback className={cn(
            'font-bold',
            isHuman ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'
          )}>
            {isHuman ? (
              <User className={cn(compact ? 'w-4 h-4' : 'w-6 h-6')} />
            ) : (
              <Bot className={cn(compact ? 'w-4 h-4' : 'w-6 h-6')} />
            )}
          </AvatarFallback>
        </Avatar>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className={cn(
              'font-semibold truncate',
              compact ? 'text-sm' : 'text-base'
            )}>
              Player {player.player_id}
            </h3>
            {isCurrentPlayer && (
              <Crown className="w-4 h-4 text-yellow-500 flex-shrink-0" />
            )}
          </div>
          
          <p className={cn(
            'text-gray-600 truncate',
            compact ? 'text-xs' : 'text-sm'
          )}>
            {player.agent_name}
          </p>
        </div>
      </div>

      {/* Chips and state */}
      <div className={cn(
        'flex items-center justify-between gap-2 mt-3',
        compact && 'mt-2'
      )}>
        <div className={cn(
          'px-3 py-1 rounded-full border font-bold',
          getChipColor(player.chips),
          compact ? 'text-xs px-2 py-0.5' : 'text-sm'
        )}>
          ${player.chips.toLocaleString()}
        </div>

        <div className="flex items-center gap-2">
          <div className={cn(
            'w-2 h-2 rounded-full',
            stateDisplay.color
          )} />
          <span className={cn(
            'text-gray-600 font-medium',
            compact ? 'text-xs' : 'text-sm'
          )}>
            {stateDisplay.label}
          </span>
        </div>
      </div>

      {/* Action info for current player */}
      {isCurrentPlayer && player.chips_to_call > 0 && (
        <div className={cn(
          'mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-center',
          compact && 'mt-1 p-1'
        )}>
          <span className={cn(
            'text-yellow-700 font-medium',
            compact ? 'text-xs' : 'text-sm'
          )}>
            To call: ${player.chips_to_call}
          </span>
        </div>
      )}

      {/* Cards */}
      {player.hole_cards && showCards && (
        <div className={cn(
          'mt-3 flex justify-center',
          compact && 'mt-2'
        )}>
          <CardGroup 
            cards={player.hole_cards}
            size={compact ? 'sm' : 'md'}
            animated={true}
            spacing="tight"
          />
        </div>
      )}

      {/* Hand strength indicator (debug mode) */}
      {player.hand_strength !== null && player.hand_strength !== undefined && (
        <div className={cn(
          'mt-2 text-center',
          compact && 'mt-1'
        )}>
          <Badge variant="outline" className={cn(compact ? 'text-xs' : 'text-sm')}>
            Strength: {(player.hand_strength * 100).toFixed(1)}%
          </Badge>
        </div>
      )}
    </div>
  );
}

// Component for displaying multiple players in a grid
interface PlayersGridProps {
  players: PlayerInfo[];
  currentPlayer: number | null;
  humanPlayerId?: number | null;
  showAllCards?: boolean;
  compact?: boolean;
  className?: string;
}

export function PlayersGrid({ 
  players, 
  currentPlayer, 
  humanPlayerId,
  showAllCards = false,
  compact = false,
  className 
}: PlayersGridProps) {
  return (
    <div className={cn(
      'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4',
      compact && 'gap-2',
      className
    )}>
      {players.map((player) => (
        <PlayerStatus
          key={player.player_id}
          player={player}
          isCurrentPlayer={player.player_id === currentPlayer}
          showCards={showAllCards || player.player_id === humanPlayerId}
          compact={compact}
        />
      ))}
    </div>
  );
} 