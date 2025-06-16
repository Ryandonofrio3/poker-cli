TexasHoldEm Class | SirRender00/texasholdem | DeepWiki
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
TexasHoldEm Class
Relevant source files
This document provides detailed technical documentation for the core TexasHoldEm class, which serves as the central component of the Texas Hold'em implementation. The class represents a tournament-style Texas Hold'em table and manages the entire game state, including players, cards, betting rounds, pot management, and game phase transitions. For information about the card representation system, see Card and Deck.

Class Purpose and Responsibilities
The TexasHoldEm class is responsible for:

Maintaining the complete state of a poker game
Enforcing game rules and valid actions
Managing players, cards, and betting rounds
Tracking and distributing pots
Recording game history for later replay
Providing an interface for agents or UIs to interact with the game
Sources: 
texasholdem/game/game.py
211-1376

Class Structure and Properties
TexasHoldEm

+int buyin

+int big_blind

+int small_blind

+int max_players

+List<Player> players

+int btn_loc

+int bb_loc

+int sb_loc

+int current_player

+List<Pot> pots

+Deck _deck

+List<Card> board

+Dict hands

+int last_raise

+bool raise_option

+int num_hands

+HandPhase hand_phase

+GameState game_state

+History hand_history

+start_hand()

+take_action(action_type, total)

+validate_move(player_id, action, total)

+get_available_moves()

+is_hand_running()

+is_game_running()

+export_history()

+import_history()

Sources: 
texasholdem/game/game.py
211-296

Key Attributes
Attribute	Type	Description
buyin	int	The buy-in amount for each player
big_blind	int	The big blind amount
small_blind	int	The small blind amount
max_players	int	Maximum number of players at the table (default: 9)
players	List[Player]	List of Player objects representing all players
btn_loc	int	The player ID who has the button
bb_loc	int	The player ID who has the big blind
sb_loc	int	The player ID who has the small blind
current_player	int	The player ID whose turn it is to act
pots	List[Pot]	The active pot objects in the game
board	List[Card]	The communal cards on the board
hands	Dict[int, List[Card]]	Map from player ID to their hand
hand_phase	HandPhase	The current phase of the hand
game_state	GameState	The current state of the game
hand_history	History	Records the history of the current hand
Sources: 
texasholdem/game/game.py
226-252

Game Flow and Hand Phases
The TexasHoldEm class manages a poker game through a series of hand phases. Each phase represents a distinct stage of a poker hand, with specific behaviors and transitions.

start_hand()

deal cards

betting completed

betting completed

betting completed

betting completed

hand completed

game over

PREHAND

PREFLOP

FLOP

TURN

RIVER

SETTLE

Setup blinds, reset pots, deal cards

First betting round

Deal 3 community cards

Deal 1 more community card

Deal 1 final community card

Evaluate hands, distribute pots

Sources: 
texasholdem/game/game.py
1142-1165
 
texasholdem/game/game.py
304-373
 
texasholdem/game/game.py
943-1051
 
texasholdem/game/game.py
574-632

Hand Phases
HandPhase	Description	New Cards	Next Phase
PREHAND	Setup phase between hands, not a running hand	0	PREFLOP
PREFLOP	Initial betting round after hole cards are dealt	0	FLOP
FLOP	Betting round after first three community cards	3	TURN
TURN	Betting round after fourth community card	1	RIVER
RIVER	Final betting round after fifth community card	1	SETTLE
SETTLE	Final phase where hands are evaluated and pots distributed	0	PREHAND
Sources: 
docs/game_information.rst
151-167
 
texasholdem/game/game.py
943-1051

Player Management
Player States
The TexasHoldEm class uses the PlayerState enum to track the status of each player in the game:

New hand

Another player raises

Player calls

Player bets all chips

Player calls with all chips

Player folds

Player folds

Hand completes

Hand completes

IN

TO_CALL

ALL_IN

OUT

Player has matched all bets

Player needs to match a bet

Player has no more chips

Player has folded

Sources: 
docs/game_information.rst
202-210
 
texasholdem/game/game.py
487-490
 
texasholdem/game/game.py
895-900

Player Iterators
The TexasHoldEm class provides several methods to iterate through players in different ways:

Method	Description	Parameters
player_iter()	Iterates through all players	loc, reverse, match_states, filter_states
in_pot_iter()	Iterates through players with a stake in the pot	loc, reverse
active_iter()	Iterates through players who can take an action	loc, reverse
Sources: 
texasholdem/game/game.py
374-447
 
docs/game_information.rst
106-119

Betting Mechanics
Pot System
The TexasHoldEm class uses a sophisticated pot system that handles main pots and side pots automatically.

Pot Management

Yes

No

Post Bet

Check for All-In

Split Pot

Update Player Last Pot

Update Player States

Complete Betting Round

Collect Bets into Pot

Sources: 
texasholdem/game/game.py
449-470
 
texasholdem/game/game.py
471-523

Action Validation
The class implements a comprehensive validation system to ensure all player actions follow the rules of poker:

Action Validation

No

Yes

Valid for state

Invalid for state

Valid amount

Invalid amount

validate_move()

Is current player?

Invalid move

Check action type

Check player state

If raise, check amount

Valid move

Sources: 
texasholdem/game/game.py
720-836

Core Game Methods
Game Initialization
# Create a new Texas Hold'em game
game = TexasHoldEm(buyin=500, big_blind=5, small_blind=2, max_players=6)
Sources: 
docs/game_information.rst
18-20
 
texasholdem/game/game.py
256-296

Starting a Hand
The start_hand() method initiates a new poker hand:

Resets player states
Moves the button and blinds
Posts blinds
Deals hole cards to players
Sets up the hand history
Sources: 
texasholdem/game/game.py
1064-1087
 
texasholdem/game/game.py
304-373
 
docs/game_information.rst
24-33

Taking Actions
The take_action() method allows players to take actions during their turn:

# Examples of taking actions
game.take_action(ActionType.CALL)  # Call
game.take_action(ActionType.RAISE, total=50)  # Raise to 50
game.take_action(ActionType.FOLD)  # Fold
The method validates the action and updates the game state accordingly.

Sources: 
texasholdem/game/game.py
1096-1141
 
docs/game_information.rst
38-44

Available Moves
The get_available_moves() method returns a special iterator (MoveIterator) that provides information about all valid moves for the current player.

moves = game.get_available_moves()
Sources: 
texasholdem/game/game.py
839-871
 
docs/game_information.rst
60-65

Game Status Methods
Method	Return Type	Description
is_hand_running()	bool	Returns true if a hand is in progress
is_game_running()	bool	Returns true if the game has enough active players
chips_to_call(player_id)	int	Returns how many chips a player needs to call
player_bet_amount(player_id)	int	Returns how many chips a player has bet this round
chips_at_stake(player_id)	int	Returns how many chips a player can win
min_raise()	int	Returns the minimum amount a player can raise by
Sources: 
texasholdem/game/game.py
633-711
 
texasholdem/game/game.py
1166-1179

Game History
The class provides methods to record and replay game history:

export_history(path): Exports the current hand history to a PGN file
import_history(path): Static method that returns a game iterator from a PGN file
The history system captures all actions and can be used to replay hands exactly as they were played.

Sources: 
texasholdem/game/game.py
1182-1285
 
docs/game_information.rst
244-268

Internal Implementation Details
The TexasHoldEm class relies on several helper methods for its internal operations:

_prehand(): Handles setup for a new hand
_betting_round(): Manages a betting round of the game
_settle(): Evaluates hands and distributes pots
_player_post(): Handles a player posting chips to the pot
_split_pot(): Creates side pots when players go all-in
The class also uses a state machine pattern to manage the flow of the game and ensure consistent state transitions.

Sources: 
texasholdem/game/game.py
304-373
 
texasholdem/game/game.py
943-1051
 
texasholdem/game/game.py
574-632
 
texasholdem/game/game.py
471-523
 
texasholdem/game/game.py
449-470

Usage Example
# Create a new Texas Hold'em game
game = TexasHoldEm(buyin=500, big_blind=5, small_blind=2)

# Standard game loop
while game.is_game_running():
    game.start_hand()
    while game.is_hand_running():
        # Get available moves
        moves = game.get_available_moves()
        
        # Choose an action (e.g., from an agent)
        action, total = some_agent_function(game)
        
        # Take the action
        game.take_action(action, total=total)
Sources: 
docs/game_information.rst
74-79

Related Classes
The TexasHoldEm class interacts with several other important classes:

Player: Represents a player in the game with chips and state
Pot: Manages betting pots and side pot creation
HandPhase: Enum representing the phases of a poker hand
ActionType: Enum representing the types of actions a player can take
PlayerState: Enum representing the possible states of a player
History: Records the history of a hand for later replay
Sources: 
texasholdem/game/game.py
41-62
 
texasholdem/game/game.py
64-197
 
texasholdem/game/game.py
24-38

Dismiss
Refresh this wiki

Enter email to refresh
On this page
TexasHoldEm Class
Class Purpose and Responsibilities
Class Structure and Properties
Key Attributes
Game Flow and Hand Phases
Hand Phases
Player Management
Player States
Player Iterators
Betting Mechanics
Pot System
Action Validation
Core Game Methods
Game Initialization
Starting a Hand
Taking Actions
Available Moves
Game Status Methods
Game History
Internal Implementation Details
Usage Example
Related Classes
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