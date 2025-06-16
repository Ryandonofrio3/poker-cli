Game Logic | SirRender00/texasholdem | DeepWiki
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
Game Logic
Relevant source files
This page documents the core game mechanics, rules, states, actions, and flow of a Texas Hold'em game in the texasholdem package. It focuses on how the game progresses through different phases, how player actions are processed, and how betting rounds, pots, and hand resolutions are managed. For information about the card representation and deck management, see Card System. For details on hand evaluation and ranking, see Hand Evaluation.

Game Overview
The TexasHoldEm class is the central coordinator of the game, managing state transitions, player actions, and rule enforcement. It implements tournament-style Texas Hold'em with World Series of Poker rules, including complex scenarios like side pots and all-in situations.

Game System Components

manages

tracks

manages

validates

tracks

generates

determines

affects

defines

iterates

posts to

rewards

TexasHoldEm

HandPhase

Player

Pot

ActionType

PlayerState

MoveIterator

Game Flow

Player Actions

Sources:

texasholdem/game/game.py
211-1137
texasholdem/game/hand_phase.py
17-83
Hand Phases and Game Flow
The game progresses through six distinct phases, each representing a specific stage in a Texas Hold'em hand.

start_hand()

"Deal cards & post blinds"

"Betting complete"

"Betting complete"

"Betting complete"

"Betting complete"

"Hand complete"

PREHAND

PREFLOP

FLOP

TURN

RIVER

SETTLE

Betting Round
"Current player to act"

"Action selected"

"Valid"

"Invalid"

"Update player state"

"Round complete"

"More players to act"

PlayerAction

ValidateMove

ExecuteAction

NextPlayer

Sources:

texasholdem/game/hand_phase.py
17-83
texasholdem/game/game.py
943-1128
HandPhase Enum
The HandPhase enum defines six phases of a poker hand:

PREHAND: Initial setup phase before a hand begins - blinds are posted, cards are dealt
PREFLOP: First betting round with just hole cards
FLOP: Second betting round after three community cards are dealt
TURN: Third betting round after a fourth community card is dealt
RIVER: Final betting round after the fifth community card is dealt
SETTLE: Evaluation of hands and distribution of pots to winners
Each phase has associated metadata about the number of new cards dealt and what the next phase will be.

Sources:

texasholdem/game/hand_phase.py
17-83
docs/game_information.rst
149-183
Player Management
Player States
The PlayerState enum defines the possible states a player can be in during the game:

State	Description
IN	Player has posted enough chips to be in the current pot
OUT	Player has folded this hand
TO_CALL	Player needs to call to stay in the hand
ALL_IN	Player has committed all their chips
SKIP	Player cannot play in the game (e.g., no chips left)
Sources:

texasholdem/game/game.py
41-62
docs/game_information.rst
186-212
Player Class
The Player class is used for bookkeeping player information:

Player

+player_id: int

+chips: int

+state: PlayerState

+last_pot: int

Sources:

texasholdem/game/game.py
41-62
Player Iteration
The TexasHoldEm class provides several methods to iterate through players:

player_iter(): General iterator over all players
in_pot_iter(): Iterator over players with a stake in the pot
active_iter(): Iterator over players who can take an action
These iterators are crucial for determining the action order and for tracking which players are involved in each betting round.

Sources:

texasholdem/game/game.py
374-447
docs/game_information.rst
101-121
Actions and Betting Logic
Action Types
The ActionType enum defines the possible actions a player can take:

Action	Description
FOLD	Discard hand and forfeit interest in the pot
CHECK	Pass action without betting (only if no previous bet)
CALL	Match the current bet to stay in the hand
RAISE	Increase the current bet amount
ALL_IN	Commit all remaining chips
Sources:

texasholdem/game/game.py
872-905
docs/game_information.rst
36-46
Move Validation and Execution
The game engine validates moves before they are executed, ensuring they follow poker rules:

Action Processing

Valid

ALL_IN

CALL or RAISE

Post chips

Update

Update

validate_move()

take_action()

_translate_allin()

_player_post()

Player State

Pot Management

Sources:

texasholdem/game/game.py
712-836
texasholdem/game/game.py
873-923
Available Moves
The get_available_moves() method returns a MoveIterator containing all valid actions for the current player, automatically handling constraints like:

Players who can check vs. those who must call
Minimum and maximum raise amounts
Special rules like WSOP Rule 96 regarding all-in raises
Sources:

texasholdem/game/game.py
838-871
texasholdem/game/move.py
14-125
Pot Management
Pot Class
The Pot class manages the chips bet by players in each round:

Pot

+amount: int

+raised: int

+player_amounts: Dict[int, int]

+chips_to_call(player_id) : : int

+player_post(player_id, amount) : : void

+collect_bets() : : void

+split_pot(raised_level) : : Optional[Pot]

Sources:

texasholdem/game/game.py
64-197
Side Pot Creation
The game engine automatically creates side pots when a player is all-in:

When a player goes all-in, a new side pot is created
Players with more chips can continue betting in the newer pot
Each player's last_pot attribute tracks which pots they're eligible for
This complex mechanism ensures that players only win the portion of the pot for which they've contributed chips.

Sources:

texasholdem/game/game.py
449-522
docs/game_information.rst
272-286
Hand Settlement
When a betting round completes, the game progresses to the next phase. After the River (or if all but one player has folded), the hand enters the SETTLE phase:

Any remaining community cards are dealt (if needed for all-in situations)
Hands are evaluated using the evaluator module
The pot is awarded to the winning player(s)
Chips are distributed properly, with leftover chips going to the player left of the button (WSOP Rule 73)
Sources:

texasholdem/game/game.py
574-632
tests/evaluator/conftest.py
358-429
Special Rules Implementation
All-In Rules
The game implements WSOP Rule 96, which states that an all-in raise that is less than the previous raise does not reopen the betting round unless multiple all-in raises combined exceed the previous raise.

WSOP Rule 96 Logic

Sum(30+25) > 50

Sum(30+25) < 50

Previous Raise: 50

Decision Point

Player 1 All-in: 30

Player 2 All-in: 25

Reopen Betting

Don't Reopen Betting

Sources:

texasholdem/game/game.py
923-942
texasholdem/game/game.py
991-1039
docs/game_information.rst
141-147
Game State Management
The overall game has two states defined by the GameState enum:

RUNNING: The table is active and can play hands
STOPPED: The table is inactive due to lack of players or chips
Sources:

texasholdem/game/game.py
200-210
tests/game/test_game.py
127-146
Canonical Game Loop
Here's how a typical game loop would be structured:

while game.is_game_running():
    game.start_hand()
    while game.is_hand_running():
        action, total = some_agent(game)
        game.take_action(action, total=total)
This loop will run until there's only one player left with chips.

Sources:

docs/game_information.rst
67-80
tests/game/test_game.py
234-251
Dismiss
Refresh this wiki

Enter email to refresh
On this page
Game Logic
Game Overview
Hand Phases and Game Flow
HandPhase Enum
Player Management
Player States
Player Class
Player Iteration
Actions and Betting Logic
Action Types
Move Validation and Execution
Available Moves
Pot Management
Pot Class
Side Pot Creation
Hand Settlement
Special Rules Implementation
All-In Rules
Game State Management
Canonical Game Loop
Ask Devin about SirRender00/texasholdem
Deep Research

Syntax error in text
mermaid version 11.6.0
Syntax error in text
mermaid version 11.6.0
Syntax error in text
mermaid version 11.6.0