Core Game System | SirRender00/texasholdem | DeepWiki
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
Core Game System
Relevant source files
The Core Game System is the central architecture of the Texas Hold'em package, responsible for managing the game state, enforcing rules, facilitating player actions, and coordinating the flow of play. This page provides a technical overview of the system's structure, components, and how they interact to create a complete poker game implementation.

For information about specific card representations, see Card System. For details on hand strength evaluation, see Hand Evaluation.

System Overview
The Core Game System implements a tournament-style Texas Hold'em poker game following World Series of Poker rules. It manages the full lifecycle of a poker game including:

Player management and state tracking
Blind posting and button movement
Betting rounds and action validation
Pot creation and management
Side pot calculation and distribution
Hand settlement and winner determination
Sources: 
texasholdem/game/game.py
200-211
 
texasholdem/game/game.py
211-295
 
texasholdem/game/__init__.py
1-18

Primary Components
TexasHoldEm Class
The TexasHoldEm class is the central coordinator of the game, providing the main API for game interaction and internal logic for rule enforcement. It manages:

Game configuration (blinds, buy-in)
Player state and actions
Betting rounds and pot management
Game phase transitions
Hand history recording
Internal State

TexasHoldEm API

Initializes

Posts blinds

Deals cards

Updates

Updates

Records

Potentially changes

Changes

Based on

Based on

Based on

Checks

Checks

Uses

start_hand()

take_action(action, total)

is_hand_running()

get_available_moves()

validate_move()

export_history()

players: List[Player]

board: List[Card]

pots: List[Pot]

hand_phase: HandPhase

hand_history: History

current_player: int

btn_loc, bb_loc, sb_loc: int

Sources: 
texasholdem/game/game.py
211-295
 
docs/game_information.rst
6-100

Supporting Types and State Management
The Core Game System includes several enumerations and specialized classes for state management:

HandPhase: Enumeration of game phases (PREHAND, PREFLOP, FLOP, TURN, RIVER, SETTLE)
ActionType: Possible player actions (FOLD, CHECK, CALL, RAISE, ALL_IN)
PlayerState: Player's state in the game (IN, TO_CALL, ALL_IN, OUT, SKIP)
Player: Class representing a player with chips and state
Pot: Class representing a betting pot with player contributions
MoveIterator: Iterator over valid moves for a player
History: Records the full history of a hand for replay and export
Each of these components maintains its own state and provides methods for state transitions and information access.

Sources: 
texasholdem/game/__init__.py
1-18
 
texasholdem/game/game.py
41-197

Game Flow and State Machine
The Core Game System implements a state machine that governs the flow of a poker hand. The state transitions follow the standard Texas Hold'em hand structure:

create game

start_hand()

betting complete

betting complete

betting complete

betting complete

hand complete

PREHAND

PREFLOP

FLOP

TURN

RIVER

SETTLE

Betting Round
take_action()

round complete

continue round

Action

NextPlayer

For each hand phase, the system executes specific logic:

PREHAND: Preparation for a new hand (not a formal betting round)

Button is moved, blinds are posted
Cards are dealt to players
Hand history is initialized
PREFLOP: First betting round

First player to act is to the left of big blind
No community cards are dealt yet
FLOP: Second betting round

Three community cards are dealt
First player to act is to the left of button
TURN: Third betting round

One additional community card is dealt
RIVER: Fourth betting round

Final community card is dealt
SETTLE: Hand resolution

Hands are evaluated
Pot(s) are distributed to winner(s)
Sources: 
texasholdem/game/game.py
943-970
 
docs/game_information.rst
149-183

Action Handling
The Core Game System processes player actions through a validation and execution pipeline that ensures game rules are properly enforced:

Valid

Invalid

FOLD

CHECK

CALL

RAISE

ALL_IN

Yes

No

Game needs player action

Determine current player

get_available_moves()

take_action(action, total)

validate_move()

_take_action() internal method

Raise ValueError

Action Type?

Set player state to OUT
Remove from pots

No chips added

Add chips to match current bet

Add chips above current bet

Translate to CALL or RAISE

Move to next player

Is betting
round over?

Move to next hand phase

The take_action() method is the primary interface for executing player actions:

It validates the action based on the current game state
It executes the action using internal methods
It updates the game state and history
It transitions to the next player or phase as appropriate
The validate_move() method ensures that an action is valid, checking:

The player is allowed to act
The action is allowed in the current state
For raise actions, the amount is within legal limits
The get_available_moves() method returns a MoveIterator with all valid moves for the current player, useful for agents and interfaces.

Sources: 
texasholdem/game/game.py
837-871
 
texasholdem/game/game.py
712-836
 
texasholdem/game/game.py
872-900

Pot Management
The Core Game System includes sophisticated pot management logic that handles complex scenarios like:

Main pot and side pot creation
All-in situations and pot limits
Equal distribution of winnings
Handling odd chips according to WSOP rules
Settle Phase

Yes

No

Yes

No

If SETTLE phase

Player posts bet

Player all-in?

_split_pot()
Create side pot at all-in level

Update pot with player's bet

Update player eligibility for pots

Betting round
complete?

Collect all bets into pot.amount

Continue betting round

Hand phase complete

Evaluate player hands

Determine winners for each pot

Distribute pot amounts to winners

Handle odd chips (to player left of button)

The Pot class manages bet tracking and pot splitting:

It tracks the total amount already collected (amount)
It tracks player bets for the current round (player_amounts)
It handles pot splitting when players go all-in (split_pot())
The system implements the World Series of Poker rules for pot distribution, including Rule 73 regarding odd chips (leftover chips that can't be evenly divided among winners are awarded to the first seat to the left of the button).

Sources: 
texasholdem/game/game.py
64-197
 
texasholdem/game/game.py
449-472
 
texasholdem/game/game.py
574-632

Integration with Other Systems
The Core Game System integrates with other components in the codebase:

Card System Integration
The TexasHoldEm class uses the Card System for:

Creating and managing a deck (_deck attribute)
Drawing and tracking player hands (hands attribute)
Managing community cards (board attribute)
Sources: 
texasholdem/game/game.py
341-348

Hand Evaluation Integration
During the SETTLE phase, the Core Game System uses the evaluation module to:

Evaluate the strength of each player's hand
Determine winners for each pot
Distribute chips accordingly
player_ranks[player_id] = evaluator.evaluate(self.hands[player_id], self.board)
Sources: 
texasholdem/game/game.py
608-610

History System Integration
The Core Game System records all game events in a History object, which can be:

Exported to PGN format for storage
Imported for replay
Used for analysis
The history tracks prehand information, betting rounds, and settlement outcomes.

Sources: 
texasholdem/game/game.py
352-363
 
texasholdem/game/game.py
583-584

Usage Example
The Core Game System can be used as follows:

from texasholdem import TexasHoldEm, ActionType

# Create a game with 500 chip buy-in, 5 chip big blind, 2 chip small blind
game = TexasHoldEm(buyin=500, big_blind=5, small_blind=2)

# Start a hand
game.start_hand()

# Game loop
while game.is_hand_running():
    # Access current state
    current_player = game.current_player
    hand_phase = game.hand_phase
    available_moves = game.get_available_moves()
    
    # Decide on an action (in this case, always call)
    if ActionType.CALL in available_moves.action_types:
        game.take_action(ActionType.CALL)
    else:
        game.take_action(ActionType.CHECK)
Sources: 
README.md
53-68

Summary
The Core Game System provides a complete implementation of Texas Hold'em poker game mechanics, following World Series of Poker rules. It handles all aspects of gameplay from dealing cards to determining winners and distributing pots. The system is designed to be flexible, allowing integration with different user interfaces and AI agents.

Key features of the Core Game System include:

Complete state machine for hand progression
Comprehensive action validation and execution
Advanced pot management including side pots
Support for all-in situations and special cases
History recording for replay and analysis
Sources: 
README.md
9-15
 
texasholdem/game/game.py
211-232

Dismiss
Refresh this wiki

Enter email to refresh
On this page
Core Game System
System Overview
Primary Components
TexasHoldEm Class
Supporting Types and State Management
Game Flow and State Machine
Action Handling
Pot Management
Integration with Other Systems
Card System Integration
Hand Evaluation Integration
History System Integration
Usage Example
Summary
Ask Devin about SirRender00/texasholdem
Deep Research

Syntax error in text
mermaid version 11.6.0
Syntax error in text
mermaid version 11.6.0