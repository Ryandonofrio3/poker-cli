API Reference | SirRender00/texasholdem | DeepWiki
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
API Reference
Relevant source files
This page provides comprehensive reference documentation for the public API of the texasholdem package. It covers the core classes, functions, and interfaces that developers can use to create Texas Hold'em poker games, simulations, and extensions.

For information about installing and setting up the package, see Installation and Setup. For a conceptual overview of the core game system, see Core Game System.

API Architecture Overview
The texasholdem API is organized into several main components that work together to provide a complete poker game system.

API Component Relationships
Supporting Components

Core API Components

TexasHoldEm

Card

Deck

evaluate()

History

AbstractGUI/TextGUI

Agent Functions

HandPhase

ActionType

PlayerState

MoveIterator

LOOKUP_TABLE

Sources:

API Usage Flow
"Agent Function"
"TextGUI"
"evaluate()"
"Deck"
"TexasHoldEm"
"Application"
"Agent Function"
"TextGUI"
"evaluate()"
"Deck"
"TexasHoldEm"
"Application"
loop
[Until hand ends]
Create game(num_players, ...)
Create and shuffle deck
start_hand()
Deal cards
current_player()
Call agent(game)
valid_moves()
action, value
take_action(player, action, value)
render()
Updated game state
Evaluate player hands
Winners and pot distribution
Sources:

Core Game API
TexasHoldEm Class
The central class that manages the state and rules of a Texas Hold'em poker game.

Key Methods
Method	Description
__init__(num_players, starting_stack=1000, small_blind=5, big_blind=10, ante=0, deck=None, dealer_idx=0)	Creates a new game with specified parameters
start_hand()	Starts a new hand, dealing cards and posting blinds
current_player()	Returns the index of the player currently to act
valid_moves()	Returns a list of valid moves for the current player
take_action(player_idx, action_type, value=None)	Executes a player action
get_hand_phase()	Returns the current phase of the hand (PREFLOP, FLOP, etc.)
get_table_cards()	Returns the community cards on the table
is_game_running()	Returns True if the game is still in progress
is_hand_running()	Returns True if a hand is in progress
copy()	Creates a deep copy of the current game state (added in 0.10.0)
Sources: 
docs/changelog-0.10.0.rst
6

Game State Enumerations
HandPhase
Represents the different phases of a Texas Hold'em hand:

PREHAND: Before a hand has started
PREFLOP: Initial betting round after hole cards are dealt
FLOP: Betting round after first three community cards are dealt
TURN: Betting round after fourth community card is dealt
RIVER: Final betting round after fifth community card is dealt
SHOWDOWN: Hand evaluation and pot distribution
ActionType
Represents the possible actions a player can take:

FOLD: Discard hand and forfeit interest in the current pot
CHECK: Pass action to next player (when no bet is required)
CALL: Match the current bet
RAISE: Increase the current bet (must specify value)
ALLIN: Bet all remaining chips
Sources:

Card System API
Card Class
Represents a single playing card with a rank and suit.

Key Methods
Method	Description
__init__(rank, suit)	Creates a card with specified rank (2-14) and suit ('h','d','c','s')
new(card_str)	Static method to create a card from string representation (e.g., "Ah")
to_int()	Returns an integer representation of the card
from_int(int_val)	Static method to create a card from its integer representation
__str__()	Returns string representation (e.g., "Ah" for Ace of hearts)
Deck Class
Represents a standard deck of 52 playing cards.

Key Methods
Method	Description
__init__(cards=None, seed=None)	Creates a deck, optionally with specified cards and random seed
shuffle()	Randomizes the order of cards in the deck
deal()	Returns the top card from the deck
deal_n(n)	Returns the top n cards from the deck
reset()	Resets the deck to a new, unshuffled 52-card deck
Sources:

For more detailed information about the Card System, see Card System.

Hand Evaluation API
evaluate Function
The evaluate function is used to determine the strength of a poker hand.

evaluate(cards)
cards: A list of Card objects (5-7 cards)
Returns: An integer ranking of the hand strength (lower values indicate stronger hands)
The function can evaluate the following hand types (from strongest to weakest):

Royal Flush
Straight Flush
Four of a Kind
Full House
Flush
Straight
Three of a Kind
Two Pair
One Pair
High Card
The evaluator uses an efficient algorithm based on prime number encoding and lookup tables to achieve fast performance.

Sources:

For more detailed information about hand evaluation, see Hand Evaluation.

Game History API
History Class
Records and manages the history of actions in a Texas Hold'em game.

Key Methods
Method	Description
add_action(player_idx, action_type, value)	Records a player action
add_deal(cards)	Records cards being dealt
export_pgn()	Exports the game history in PGN format
import_pgn(pgn_str)	Imports a game history from PGN format
The PGN (Portable Game Notation) format allows for human-readable game history that can be saved and loaded.

Sources:

For more detailed information about game history, see Game History.

User Interface API
AbstractGUI Class
Abstract base class for creating graphical user interfaces for Texas Hold'em games.

Key Methods
Method	Description
__init__(game)	Initializes with a TexasHoldEm instance
render()	Renders the current game state
animate_action(player_idx, action_type, value)	Animates a player action
animate_deal(cards)	Animates cards being dealt
TextGUI Class
A concrete implementation of AbstractGUI that renders the game state as text in the console.

Additional Features
Displays player stacks, bets, and cards
Shows the pot size and community cards
Visualizes active players and current player
As of 0.10.0, also displays available actions
Sources: 
docs/changelog-0.10.0.rst
7-8

For more detailed information about user interfaces, see User Interfaces and Text GUI.

Agent API
Agent Protocol
Agents in the texasholdem package are functions that take a game state and return an action decision.

Agent function signature:

def agent_function(game):
    # Analyze game state
    return action_type, value
Built-in Agents
The package includes several built-in agents:

Agent	Description
call_agent	Always calls if possible, otherwise checks, and folds as a last resort
random_agent	Randomly selects from valid moves
Sources:

For more information about agents, see Game Agents and Creating Custom Agents.

Advanced API Features
Game State Copying
The copy() method added in version 0.10.0 allows creating a deep copy of a game state, which is useful for agents that need to simulate potential outcomes or for game state analysis.

Sources: 
docs/changelog-0.10.0.rst
6

Custom Deck Creation
You can provide a custom deck to the TexasHoldEm constructor for testing or specialized games:

custom_deck = Deck(cards=[custom_card_list], seed=42)
game = TexasHoldEm(num_players=2, deck=custom_deck)
Sources:

API Changes in Recent Versions
Changes in 0.11.0
Fixed a bug where a RAISE action with None value was returned by the iterator
Added support for Python 3.12
Sources: 
docs/changelog-0.11.0.rst
4-10

Changes in 0.10.0
Added new copy() method to the TexasHoldEm class
Added available actions printing in the TextGUI
Sources: 
docs/changelog-0.10.0.rst
4-8

Using the API in Applications
Application Integration Pattern
Implementation Layer

API Layer

Application Layer

User Application

Simulation

AI Training

TexasHoldEm API

Card & Deck API

Evaluation API

GUI API

Agent API

History API

Game Logic

Data Structures

Evaluation Algorithms

Sources:

For complete examples and detailed usage information, see the dedicated sections for each component in the wiki: TexasHoldEm Class, Card and Deck, and Game History.

Dismiss
Refresh this wiki

Enter email to refresh
On this page
API Reference
API Architecture Overview
API Component Relationships
API Usage Flow
Core Game API
TexasHoldEm Class
Key Methods
Game State Enumerations
HandPhase
ActionType
Card System API
Card Class
Key Methods
Deck Class
Key Methods
Hand Evaluation API
evaluate Function
Game History API
History Class
Key Methods
User Interface API
AbstractGUI Class
Key Methods
TextGUI Class
Additional Features
Agent API
Agent Protocol
Built-in Agents
Advanced API Features
Game State Copying
Custom Deck Creation
API Changes in Recent Versions
Changes in 0.11.0
Changes in 0.10.0
Using the API in Applications
Application Integration Pattern
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