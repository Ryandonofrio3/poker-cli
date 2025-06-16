Game Agents | SirRender00/texasholdem | DeepWiki
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
Game Agents
Relevant source files
This page provides an overview of the game agents system in the Texas Hold'em package. Game agents are automated players that can make decisions during gameplay, enabling simulation, testing, and mixed human-AI gameplay. For detailed information about creating your own custom agents, see Creating Custom Agents.

Overview
The Texas Hold'em package includes a set of basic agents that can be used out-of-the-box to automate player decisions. These agents provide a foundation for gameplay without human intervention and can be used for various purposes:

Running simulations to test game mechanics
Creating practice environments for human players
Benchmarking custom agent implementations
Filling seats in games with fewer human players
Sources: 
README.md
13-14
 
README.md
115-130

Agent Architecture
Agent Integration With Game System

Agent System

TexasHoldEm Game

TexasHoldEm Class

ActionType

get_available_moves()

Game State
- hand_phase
- current_player
- chips_to_call
- player hands
- board cards

take_action(action, total)

Agent Function
(call_agent/random_agent)

Decision Logic

An agent in the Texas Hold'em package is implemented as a function that receives the game state and returns an action decision. The game system calls the agent function when it's an automated player's turn, and the agent's decision is then executed through the game's take_action() method.

Sources: 
texasholdem/agents/basic.py
15-52
 
README.md
115-130

Built-in Agents
The package includes two basic agent implementations:

call_agent
The call_agent is a simple strategy that only calls when facing a bet or checks otherwise. It never raises or folds.

call_agent Decision Flow

Sources: 
texasholdem/agents/basic.py
15-28

random_agent
The random_agent makes decisions uniformly at random from the available legal moves. When raising, it selects a random amount between the minimum raise and the player's remaining chips.

random_agent Decision Flow

Yes

No

Game calls random_agent()

Get available moves

no_fold parameter
set to true?

Remove FOLD from options

Sample random move from available options

Return selected move and amount

Sources: 
texasholdem/agents/basic.py
31-52

Agent Interface
All agents in the Texas Hold'em package follow the same interface pattern. An agent is a function that:

Takes a TexasHoldEm game object as its primary parameter (plus optional configuration parameters)
Returns a tuple of (ActionType, total) where:
ActionType is one of CHECK, CALL, FOLD, or RAISE
total is the total bet amount for RAISE actions (None for other actions)
Parameter	Type	Description
game	TexasHoldEm	The current game instance containing all game state
additional parameters	various	Configuration parameters specific to each agent
Return Value	Type	Description
action_type	ActionType	The action to take (CHECK, CALL, FOLD, RAISE)
total	int or None	For RAISE: the total bet amount, for others: None
Sources: 
texasholdem/agents/basic.py
15-16
 
texasholdem/agents/basic.py
31-32

Using Agents in Games
Agents can be integrated into games in several ways. The most common approach is to delegate decision-making to an agent when it's a specific player's turn.

Example Integration Pattern

Yes

No

Yes

No

Start game loop

game.start_hand()

Is hand running?

Is current player
controlled by agent?

Call agent function
to get move

game.take_action(action, total)

Wait for human input

Hand complete

The code example below demonstrates how to create a game where even-numbered players use the random_agent and odd-numbered players use the call_agent:

from texasholdem import TexasHoldEm
from texasholdem.agents import random_agent, call_agent

game = TexasHoldEm(buyin=500, big_blind=5, small_blind=2)
game.start_hand()

while game.is_hand_running():
    if game.current_player % 2 == 0:
        game.take_action(*random_agent(game))
    else:
        game.take_action(*call_agent(game))
Sources: 
README.md
115-130

Agent Selection Strategy
When building games with multiple agents or mixed human-agent play, you can implement various agent selection strategies:

Agent Selection Patterns

Agent Selection Methods

Position Based
(e.g., seat number)

Configuration Map
(player_id -> agent function)

Skill Level Selection
(novice, intermediate, expert)

Mixed Strategy
(combine multiple agents)

TexasHoldEm Game

Agent Function

ActionType + total

You can select agents based on:

Player position (e.g., even vs odd seats)
Player ID mapping to specific agent functions
Desired difficulty level
Mixed strategies that combine multiple agents
Sources: 
tests/game/conftest.py
19-22
 
README.md
115-130

Implementation Details
Agent Function Signatures
The built-in agents have the following signatures:

call_agent(game: TexasHoldEm) -> Tuple[ActionType, None]: Returns CALL if someone raised, otherwise CHECK
random_agent(game: TexasHoldEm, no_fold: bool = False) -> Tuple[ActionType, int]: Returns a random action, with an option to prevent folding
The agents access game state through the game parameter, including:

Current player's ID: game.current_player
Current player's state: game.players[game.current_player].state
Available moves: game.get_available_moves()
Chips required to call: game.chips_to_call(game.current_player)
Sources: 
texasholdem/agents/basic.py
15-52

Game Integration
Agents are integrated with the game through the standard take_action() method. The agent function's return value is directly passed to this method using Python's tuple unpacking syntax:

game.take_action(*agent_function(game))
This pattern allows agents to be seamlessly swapped without changing the integration code.

Sources: 
README.md
126-129

Testing with Agents
The testing framework uses agents extensively to validate game mechanics through repeated simulations. This helps identify edge cases and ensure the consistency of game rules.

The conftest.py file includes predicates for automated testing where agents play through entire tournaments to verify various game properties stay consistent throughout long sessions.

Sources: 
tests/game/conftest.py
203-369

Related Pages
For information about implementing your own custom agents with advanced strategies, see Creating Custom Agents.

Dismiss
Refresh this wiki

Enter email to refresh
On this page
Game Agents
Overview
Agent Architecture
Built-in Agents
call_agent
random_agent
Agent Interface
Using Agents in Games
Agent Selection Strategy
Implementation Details
Agent Function Signatures
Game Integration
Testing with Agents
Related Pages
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