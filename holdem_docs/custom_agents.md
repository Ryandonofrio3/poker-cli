Creating Custom Agents | SirRender00/texasholdem | DeepWiki
DeepWiki
SirRender00/texasholdem

Try DeepWiki for private repos in
Devin

Share

Last indexed: 25 April 2025 (84aaee)
Home
Installation and Setup
Core Game System
Game Logic
Card System
Hand Evaluation
User Interfaces
Text GUI
Game Agents
Creating Custom Agents
Game History
Development Guide
Project Structure
Testing
CI/CD Pipeline
API Reference
TexasHoldEm Class
Card and Deck
Game History
Creating Custom Agents
Relevant source files
This document explains how to create custom game agents for the Texas Hold'em system. Agents are functions that make decisions on behalf of players during gameplay. The system provides basic agents out of the box, but you can create custom agents with more sophisticated decision-making strategies.

For information about using the pre-built agents, see Game Agents.

Agent Interface
In the Texas Hold'em system, agents are functions that follow a specific interface:

Agent Function

Input: TexasHoldEm game state

Process: Decision Logic

Output: (ActionType, total) tuple

The agent function:

Takes a TexasHoldEm game object as its primary input
Returns a tuple with two elements:
An ActionType (e.g., CHECK, CALL, FOLD, RAISE)
A total value (integer or None)
Sources: 
texasholdem/agents/basic.py
15-28
 
texasholdem/agents/basic.py
31-51

Basic Agent Implementation Structure
To create a custom agent, you need to implement a function with the following signature:

The basic structure will typically look like this:

def my_custom_agent(game: TexasHoldEm, *optional_params) -> Tuple[ActionType, Optional[int]]:
    # 1. Analyze game state
    
    # 2. Make decision
    
    # 3. Return action and total
    return action_type, total_value
Sources: 
texasholdem/agents/basic.py
15-28
 
texasholdem/agents/basic.py
31-51

Example Agents
The system includes two built-in agents that demonstrate the basic patterns:

Call Agent
The call_agent simply calls when another player has raised, or checks otherwise:

TO_CALL state

Otherwise

Start call_agent

Check player state

Return CALL, None

Return CHECK, None

End

Sources: 
texasholdem/agents/basic.py
15-28

Random Agent
The random_agent makes random decisions from the available moves:

Start random_agent

Get available moves

Remove FOLD option if no_fold=True

Sample a random move

Return sampled move

Sources: 
texasholdem/agents/basic.py
31-51

Accessing Game Information
When creating a custom agent, you have access to various information from the game state through the TexasHoldEm object:

Information	Method/Property	Description
Current player	game.current_player	Index of the player who needs to act
Player data	game.players[player_id]	Access player objects with state, chips, etc.
Player hand	game.get_hand(player_id)	Get the cards in a player's hand
Community cards	game.board	Cards on the board (flop, turn, river)
Available moves	game.get_available_moves()	Returns a MoveIterator with valid actions
Chips to call	game.chips_to_call(player_id)	How many chips the player needs to call
Minimum raise	game.min_raise()	Minimum amount that can be raised
Hand phase	game.hand_phase	Current phase (PREFLOP, FLOP, etc.)
Pot amount	game.pots[pot_id].get_total_amount()	Total amount in a pot
Sources: 
texasholdem/agents/basic.py
15-28
 
texasholdem/agents/basic.py
31-51
 
tests/game/conftest.py
32-201

Using MoveIterator for Action Selection
The get_available_moves() method returns a MoveIterator object, which helps you work with available actions:

MoveIterator

action_types: List[ActionType]

raise_range: range

sample(): Select random move

contains(): Check if move is valid

Custom Agent

Return valid (ActionType, total) tuple

Key methods of MoveIterator:

action_types: List of available action types
raise_range: Range of valid raise amounts (if raising is allowed)
sample(): Select a random move from available options
__contains__(): Check if a specific move is valid
Sources: 
texasholdem/game/move.py
15-125
 
texasholdem/agents/basic.py
31-51

Creating a Decision-Making Strategy
When creating a custom agent, you'll typically follow this process:

Analyze the game state
Evaluate the player's hand relative to the community cards
Consider the betting context (pot size, player positions, etc.)
Select an action based on your strategy
Verify the action is valid using get_available_moves()
Return the action and total value
Valid

Invalid

Start custom_agent

Analyze game state

Evaluate player's hand

Consider betting context

Select preliminary action

Validate action is legal

Return action, total

Select fallback action

Sources: 
texasholdem/agents/basic.py
15-28
 
texasholdem/agents/basic.py
31-51

Testing Custom Agents
To test your custom agent, you can:

Create a game instance
Register your agent for one or more players
Run the game for multiple hands
Analyze the results
The test framework in the repository includes several useful predicates for validating game behavior:

AgentTests

Predicates

EmptyPots

LastRaiseChecker

MinRaiseChecker

RaiseOptionChecker

AvailableMoveChecker

Custom Agent

Unit Tests for Strategy

Simulation Tests

Predicate-based Tests

The GamePredicate class and its subclasses provide a framework for validating game behavior before and after actions are taken.

Sources: 
tests/game/conftest.py
204-240
 
tests/game/conftest.py
243-369

Best Practices
When creating custom agents, consider these best practices:

Validate actions: Always ensure your chosen action is valid before returning it
Handle all game phases: Create logic for all hand phases (PREFLOP, FLOP, TURN, RIVER)
Consider pot odds: Base decisions on the ratio between pot size and cost to call
Use configuration parameters: Make your agent configurable for different playing styles
Provide fallback actions: Have safe default actions if your primary choice is invalid
Test thoroughly: Run your agent in many different scenarios to ensure it behaves correctly
Integration Example
To integrate your custom agent into a game:

Hand loop

Game loop

Create TexasHoldEm instance

Game loop

game.start_hand()

Hand loop

Hand completed

Get current player's action

Call custom_agent(game)

game.take_action(action, total)

Sources: 
texasholdem/agents/basic.py
15-28
 
texasholdem/agents/basic.py
31-51
 
tests/game/conftest.py
32-201

Dismiss
Refresh this wiki

Enter email to refresh
On this page
Creating Custom Agents
Agent Interface
Basic Agent Implementation Structure
Example Agents
Call Agent
Random Agent
Accessing Game Information
Using MoveIterator for Action Selection
Creating a Decision-Making Strategy
Testing Custom Agents
Best Practices
Integration Example
Ask Devin about SirRender00/texasholdem
Deep Research

Syntax error in text
mermaid version 11.6.0
Syntax error in text
mermaid version 11.6.0
Syntax error in text
mermaid version 11.6.0
Syntax error in text
mermaid version 11.6.0
Syntax error in text
mermaid version 11.6.0
Syntax error in text
mermaid version 11.6.0
Syntax error in text
mermaid version 11.6.0
Syntax error in text
mermaid version 11.6.0
Syntax error in text
mermaid version 11.6.0