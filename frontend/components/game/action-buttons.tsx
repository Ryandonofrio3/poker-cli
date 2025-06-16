/**
 * 🎯 Action Buttons Component
 * Interactive buttons for human player actions
 */

import { useState } from 'react';
import { ActionType, PlayerAction, getActionLabel } from '@/types/game';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { 
  HandMetal, 
  Check, 
  Phone, 
  TrendingUp, 
  DollarSign 
} from 'lucide-react';

interface ActionButtonsProps {
  availableActions: ActionType[];
  minRaiseAmount: number | null;
  currentChips: number;
  chipsToCall: number;
  onAction: (action: PlayerAction) => void;
  disabled?: boolean;
  playerId: number;
  className?: string;
}

export function ActionButtons({
  availableActions,
  minRaiseAmount,
  currentChips,
  chipsToCall,
  onAction,
  disabled = false,
  playerId,
  className
}: ActionButtonsProps) {
  const [raiseAmount, setRaiseAmount] = useState(minRaiseAmount || 0);
  const [isLoading, setIsLoading] = useState(false);

  const handleAction = async (actionType: ActionType, amount?: number) => {
    if (disabled || isLoading) return;

    setIsLoading(true);
    try {
      const action: PlayerAction = {
        player_id: playerId,
        action_type: actionType,
        ...(amount && { amount })
      };
      
      await onAction(action);
    } finally {
      setIsLoading(false);
    }
  };

  // Update raise amount when min changes
  if (minRaiseAmount && raiseAmount < minRaiseAmount) {
    setRaiseAmount(minRaiseAmount);
  }

  const maxRaise = currentChips;
  const canRaise = availableActions.includes('RAISE') && minRaiseAmount && raiseAmount >= minRaiseAmount;

  return (
    <Card className={cn('p-4 bg-white border-2 border-blue-200', className)}>
      <div className="space-y-4">
        {/* Header */}
        <div className="text-center">
          <h3 className="text-lg font-semibold text-gray-900">Your Turn</h3>
          <p className="text-sm text-gray-600">Choose your action</p>
        </div>

        <Separator />

        {/* Action info */}
        {chipsToCall > 0 && (
          <div className="text-center p-2 bg-yellow-50 border border-yellow-200 rounded">
            <p className="text-sm font-medium text-yellow-800">
              <DollarSign className="w-4 h-4 inline mr-1" />
              {chipsToCall} chips to call
            </p>
          </div>
        )}

        {/* Main action buttons */}
        <div className="grid grid-cols-2 gap-3">
          {/* Fold */}
          {availableActions.includes('FOLD') && (
            <Button
              variant="destructive"
              size="lg"
              onClick={() => handleAction('FOLD')}
              disabled={disabled || isLoading}
              className="h-12 font-semibold"
            >
              <HandMetal className="w-5 h-5 mr-2" />
              Fold
            </Button>
          )}

          {/* Check */}
          {availableActions.includes('CHECK') && (
            <Button
              variant="outline"
              size="lg"
              onClick={() => handleAction('CHECK')}
              disabled={disabled || isLoading}
              className="h-12 font-semibold"
            >
              <Check className="w-5 h-5 mr-2" />
              Check
            </Button>
          )}

          {/* Call */}
          {availableActions.includes('CALL') && (
            <Button
              variant="default"
              size="lg"
              onClick={() => handleAction('CALL')}
              disabled={disabled || isLoading}
              className="h-12 font-semibold bg-green-600 hover:bg-green-700"
            >
              <Phone className="w-5 h-5 mr-2" />
              Call {chipsToCall > 0 ? `$${chipsToCall}` : ''}
            </Button>
          )}

          {/* All-in (special case of raise) */}
          {availableActions.includes('RAISE') && (
            <Button
              variant="destructive"
              size="lg"
              onClick={() => handleAction('RAISE', currentChips)}
              disabled={disabled || isLoading}
              className="h-12 font-semibold bg-red-600 hover:bg-red-700"
            >
              <TrendingUp className="w-5 h-5 mr-2" />
              All-In ${currentChips}
            </Button>
          )}
        </div>

        {/* Raise section */}
        {availableActions.includes('RAISE') && minRaiseAmount && (
          <>
            <Separator />
            <div className="space-y-3">
              <Label htmlFor="raise-amount" className="text-sm font-semibold">
                Raise Amount
              </Label>
              
              <div className="flex items-center gap-2">
                <div className="flex-1">
                  <Input
                    id="raise-amount"
                    type="number"
                    min={minRaiseAmount}
                    max={maxRaise}
                    value={raiseAmount}
                    onChange={(e) => setRaiseAmount(Number(e.target.value))}
                    disabled={disabled || isLoading}
                    className="text-center font-mono"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Min: ${minRaiseAmount}</span>
                    <span>Max: ${maxRaise}</span>
                  </div>
                </div>
                
                <Button
                  onClick={() => handleAction('RAISE', raiseAmount)}
                  disabled={disabled || isLoading || !canRaise}
                  className="px-6 h-11 font-semibold bg-blue-600 hover:bg-blue-700"
                >
                  <TrendingUp className="w-4 h-4 mr-2" />
                  Raise
                </Button>
              </div>

              {/* Quick raise buttons */}
              <div className="flex gap-2">
                {[
                  { label: 'Min', value: minRaiseAmount },
                  { label: '2x', value: Math.min(minRaiseAmount * 2, maxRaise) },
                  { label: '3x', value: Math.min(minRaiseAmount * 3, maxRaise) },
                  { label: 'Pot', value: Math.min(chipsToCall * 2, maxRaise) },
                ].map(({ label, value }) => (
                  <Button
                    key={label}
                    variant="outline"
                    size="sm"
                    onClick={() => setRaiseAmount(value)}
                    disabled={disabled || isLoading}
                    className="flex-1 text-xs"
                  >
                    {label}
                  </Button>
                ))}
              </div>
            </div>
          </>
        )}

        {/* Loading state */}
        {isLoading && (
          <div className="text-center py-2">
            <div className="inline-flex items-center gap-2 text-sm text-gray-600">
              <div className="w-4 h-4 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin" />
              Processing action...
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}

// Simple action buttons for mobile/compact view
export function CompactActionButtons({
  availableActions,
  onAction,
  disabled = false,
  playerId,
  className
}: {
  availableActions: ActionType[];
  onAction: (action: PlayerAction) => void;
  disabled?: boolean;
  playerId: number;
  className?: string;
}) {
  const handleQuickAction = (actionType: ActionType) => {
    const action: PlayerAction = {
      player_id: playerId,
      action_type: actionType,
    };
    onAction(action);
  };

  return (
    <div className={cn('flex gap-2', className)}>
      {availableActions.includes('FOLD') && (
        <Button
          variant="destructive"
          size="sm"
          onClick={() => handleQuickAction('FOLD')}
          disabled={disabled}
        >
          Fold
        </Button>
      )}
      
      {availableActions.includes('CHECK') && (
        <Button
          variant="outline"
          size="sm"
          onClick={() => handleQuickAction('CHECK')}
          disabled={disabled}
        >
          Check
        </Button>
      )}
      
      {availableActions.includes('CALL') && (
        <Button
          variant="default"
          size="sm"
          onClick={() => handleQuickAction('CALL')}
          disabled={disabled}
        >
          Call
        </Button>
      )}
    </div>
  );
} 