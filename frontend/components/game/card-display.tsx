/**
 * 🃏 Card Display Component
 * Beautiful poker card visualization with proper suit colors
 */

import { Card, getCardSuitColor } from '@/types/game';
import { cn } from '@/lib/utils';

interface CardDisplayProps {
  card?: Card | null;
  hidden?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  animated?: boolean;
}

export function CardDisplay({ 
  card, 
  hidden = false, 
  size = 'md', 
  className,
  animated = false 
}: CardDisplayProps) {
  const sizeClasses = {
    sm: 'w-8 h-12 text-xs',
    md: 'w-12 h-16 text-sm', 
    lg: 'w-16 h-24 text-base'
  };

  // Hidden card (face down)
  if (hidden || !card) {
    return (
      <div className={cn(
        'rounded-lg border-2 border-gray-400 bg-gradient-to-br from-blue-900 to-blue-800',
        'flex items-center justify-center',
        'shadow-md relative overflow-hidden',
        sizeClasses[size],
        animated && 'transition-all duration-300 hover:scale-105',
        className
      )}>
        {/* Card back pattern */}
        <div className="absolute inset-1 rounded bg-gradient-to-br from-blue-700 to-blue-600 opacity-80" />
        <div className="relative text-blue-200 font-bold">?</div>
      </div>
    );
  }

  const suitColor = getCardSuitColor(card.suit);
  const colorClasses = suitColor === 'red' 
    ? 'text-red-600 border-red-300' 
    : 'text-gray-800 border-gray-300';

  return (
    <div className={cn(
      'rounded-lg border-2 bg-white shadow-md',
      'flex flex-col items-center justify-between p-1',
      'relative font-bold select-none',
      sizeClasses[size],
      colorClasses,
      animated && 'transition-all duration-300 hover:scale-105 hover:shadow-lg',
      className
    )}>
      {/* Top-left rank and suit */}
      <div className="flex flex-col items-center leading-none">
        <span className="font-bold">{card.rank}</span>
        <span className="text-lg leading-none">{card.suit}</span>
      </div>

      {/* Center suit (larger) */}
      <div className={cn(
        "text-2xl leading-none",
        size === 'sm' && 'text-lg',
        size === 'lg' && 'text-3xl'
      )}>
        {card.suit}
      </div>

      {/* Bottom-right rank and suit (rotated) */}
      <div className="flex flex-col items-center leading-none rotate-180">
        <span className="font-bold">{card.rank}</span>
        <span className="text-lg leading-none">{card.suit}</span>
      </div>

      {/* Subtle shine effect */}
      <div className="absolute inset-0 rounded-lg bg-gradient-to-br from-white/20 to-transparent pointer-events-none" />
    </div>
  );
}

// Component for displaying multiple cards (like hole cards or board)
interface CardGroupProps {
  cards: (Card | null)[];
  hidden?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  animated?: boolean;
  spacing?: 'tight' | 'normal' | 'loose';
}

export function CardGroup({ 
  cards, 
  hidden = false, 
  size = 'md', 
  className,
  animated = true,
  spacing = 'normal'
}: CardGroupProps) {
  const spacingClasses = {
    tight: '-space-x-2',
    normal: 'space-x-1',
    loose: 'space-x-2'
  };

  return (
    <div className={cn(
      'flex items-center',
      spacingClasses[spacing],
      className
    )}>
      {cards.map((card, index) => (
        <CardDisplay
          key={index}
          card={card}
          hidden={hidden}
          size={size}
          animated={animated}
          className={animated ? `hover:z-10 relative transition-transform duration-200` : undefined}
        />
      ))}
    </div>
  );
}

// Empty card placeholder
export function EmptyCard({ size = 'md', className }: { size?: 'sm' | 'md' | 'lg'; className?: string }) {
  const sizeClasses = {
    sm: 'w-8 h-12',
    md: 'w-12 h-16', 
    lg: 'w-16 h-24'
  };

  return (
    <div className={cn(
      'rounded-lg border-2 border-dashed border-gray-300 bg-gray-50',
      'flex items-center justify-center',
      sizeClasses[size],
      className
    )}>
      <div className="w-4 h-4 border-2 border-gray-300 rounded bg-white" />
    </div>
  );
} 