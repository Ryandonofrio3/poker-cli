'use client';

/**
 * 🏠 Home Page - Game Selection
 * Choose presets or create custom games
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api-client';
import { PresetConfig, AvailableAgent } from '@/types/game';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Spade, 
  Users, 
  Bot, 
  Zap, 
  Play, 
  AlertCircle,
  Gamepad2,
  Crown
} from 'lucide-react';

export default function HomePage() {
  const router = useRouter();
  const [presets, setPresets] = useState<PresetConfig[]>([]);
  const [agents, setAgents] = useState<AvailableAgent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [creatingGame, setCreatingGame] = useState<string | null>(null);

  // Load presets and agents on mount
  useEffect(() => {
    const loadData = async () => {
      try {
        const [presetsData, agentsData] = await Promise.all([
          apiClient.getPresets(),
          apiClient.getAgents()
        ]);
        
        setPresets(presetsData);
        setAgents(agentsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load game data');
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  const handleCreateGame = async (presetId: string) => {
    setCreatingGame(presetId);
    setError(null);

    try {
      const result = await apiClient.createGame({ preset: presetId });
      console.log('🎮 Game created:', result);
      
      // Navigate to the game page
      router.push(`/game/${result.game_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create game');
    } finally {
      setCreatingGame(null);
    }
  };

  const getPresetIcon = (presetId: string) => {
    if (presetId.includes('human')) return <Users className="w-5 h-5" />;
    if (presetId.includes('llm')) return <Zap className="w-5 h-5" />;
    if (presetId.includes('ai')) return <Bot className="w-5 h-5" />;
    return <Gamepad2 className="w-5 h-5" />;
  };

  const getPresetColor = (presetId: string) => {
    if (presetId.includes('human')) return 'border-blue-200 hover:border-blue-300';
    if (presetId.includes('llm')) return 'border-purple-200 hover:border-purple-300';
    if (presetId.includes('ai')) return 'border-green-200 hover:border-green-300';
    return 'border-gray-200 hover:border-gray-300';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 bg-gradient-to-br from-green-600 to-blue-600 rounded-full text-white">
              <Spade className="w-8 h-8" />
            </div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
              Texas Hold'em Poker
            </h1>
          </div>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Jump into a game with AI agents, LLMs, or create your own custom match. 
            No sign-up required!
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <Alert className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Loading State */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.from({ length: 6 }).map((_, i) => (
              <Card key={i} className="h-64">
                <CardHeader>
                  <Skeleton className="h-4 w-2/3" />
                  <Skeleton className="h-3 w-full" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-20 w-full mb-4" />
                  <Skeleton className="h-10 w-full" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          /* Preset Games Grid */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {presets.map((preset) => (
              <Card 
                key={preset.preset_id} 
                className={`transition-all duration-200 hover:shadow-lg ${getPresetColor(preset.preset_id)}`}
              >
                <CardHeader>
                  <div className="flex items-center gap-2">
                    {getPresetIcon(preset.preset_id)}
                    <CardTitle className="text-lg">{preset.name}</CardTitle>
                  </div>
                  <CardDescription className="text-sm">
                    {preset.description}
                  </CardDescription>
                </CardHeader>
                
                <CardContent className="space-y-4">
                  {/* Game Info */}
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Players:</span>
                      <span className="ml-1 font-medium">{preset.config.max_players}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Buy-in:</span>
                      <span className="ml-1 font-medium">${preset.config.buyin}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Big Blind:</span>
                      <span className="ml-1 font-medium">${preset.config.big_blind}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Hands:</span>
                      <span className="ml-1 font-medium">{preset.config.max_hands}</span>
                    </div>
                  </div>

                  {/* Agent Types */}
                  <div>
                    <p className="text-sm text-gray-500 mb-2">Opponents:</p>
                    <div className="flex flex-wrap gap-1">
                      {Object.values(preset.config.agents || {}).map((agentType, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {agentType.replace(/_/g, ' ')}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {/* Action Button */}
                  <Button
                    onClick={() => handleCreateGame(preset.preset_id)}
                    disabled={creatingGame === preset.preset_id}
                    className="w-full"
                    size="lg"
                  >
                    {creatingGame === preset.preset_id ? (
                      <div className="flex items-center gap-2">
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        Creating...
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <Play className="w-4 h-4" />
                        Start Game
                      </div>
                    )}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Available Agents Info */}
        {!isLoading && agents.length > 0 && (
          <div className="mt-12">
            <Card className="bg-white/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Crown className="w-5 h-5 text-yellow-500" />
                  Available AI Opponents
                </CardTitle>
                <CardDescription>
                  These intelligent agents are ready to play against you
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {agents.slice(0, 6).map((agent) => (
                    <div key={agent.agent_id} className="flex items-center gap-3 p-3 rounded-lg bg-white/50">
                      <div className="p-2 rounded-full bg-gradient-to-br from-gray-100 to-gray-200">
                        {agent.category === 'LLM' ? (
                          <Zap className="w-4 h-4 text-purple-600" />
                        ) : (
                          <Bot className="w-4 h-4 text-gray-600" />
                        )}
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-sm">{agent.name}</p>
                        <p className="text-xs text-gray-500">{agent.category}</p>
                      </div>
                      <Badge 
                        variant={agent.is_available ? "default" : "secondary"}
                        className="text-xs"
                      >
                        {agent.is_available ? "Ready" : "Busy"}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Footer */}
        <div className="mt-12 text-center text-gray-500 text-sm">
          <p>Powered by FastAPI • Built with Next.js • Real-time via WebSockets</p>
        </div>
      </div>
    </div>
  );
}
