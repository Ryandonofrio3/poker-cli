Game History | SirRender00/texasholdem | DeepWiki
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
Game History
Relevant source files
This document provides a technical overview of the game history system in the Texas Hold'em package. The system records, exports, and imports the complete history of poker hands, enabling game replay and analysis. The history system captures every aspect of a poker hand's lifecycle, from initial setup through betting rounds to final settlement.

Overview
The game history system provides functionality to:

Record all actions and state changes during a poker hand
Export history to human-readable PGN (Poker Game Notation) files
Import history from PGN files for hand replay
Validate imported history for consistency and correctness
The system supports full serialization and deserialization of game state, allowing games to be analyzed, shared, or replayed after completion.

Sources: 
texasholdem/game/history.py
1-11

Core Components
The history system consists of several interrelated dataclasses that capture different phases of a poker hand:

contains

contains

contains

contains

History

+PrehandHistory prehand

+BettingRoundHistory preflop

+BettingRoundHistory flop

+BettingRoundHistory turn

+BettingRoundHistory river

+SettleHistory settle

+to_string()

+from_string()

+export_history()

+import_history()

PrehandHistory

+int btn_loc

+int big_blind

+int small_blind

+Dict[int, int] player_chips

+Dict[int, List[Card]] player_cards

+to_string()

+from_string()

BettingRoundHistory

+List[Card] new_cards

+List[PlayerAction] actions

+to_string()

+from_string()

SettleHistory

+List[Card] new_cards

+Dict[int, Tuple] pot_winners

+to_string()

+from_string()

PlayerAction

+int player_id

+ActionType action_type

+Optional[int] total

+Optional[int] value

+to_string()

+from_string()

Sources: 
texasholdem/game/history.py
31-65
 
texasholdem/game/history.py
127-188
 
texasholdem/game/history.py
188-262
 
texasholdem/game/history.py
263-364
 
texasholdem/game/history.py
366-672

History Data Structure
The History class is the central component that contains records of each phase in a Texas Hold'em hand:

Prehand Phase: Initial game state including:

Button position
Blind values
Player chip stacks
Player hole cards
Betting Rounds:

Preflop (required)
Flop (optional)
Turn (optional)
River (optional)
Each betting round tracks:

New community cards revealed
Sequence of player actions
Settle Phase: Final settlement including:

Any remaining community cards
Pot winners, amounts, and hand rankings
Each component of the history structure implements serialization and deserialization methods (to_string() and from_string()) that enable export to and import from text files.

Sources: 
texasholdem/game/history.py
366-401

Game History Workflow
Import Process

Export Process

Game Execution

Records actions during play

Populated during gameplay

export_history()

Write to file

import_history()

Validate

Replay or analyze

TexasHoldEm Game Instance

History Object

Complete History

Convert to string representation

PGN File

Parse PGN file

Reconstituted History

Game State Sequence

Sources: 
texasholdem/game/history.py
402-435
 
texasholdem/game/history.py
496-533
 
texasholdem/game/history.py
535-572

PGN Format
The history is stored in a human-readable text format with the .pgn file extension. The format organizes information by game phases, with each phase section having a standardized structure:

PREHAND
Big Blind: <bb_value>
Small Blind: <sb_value>
Player Chips: <chips_player0>,<chips_player1>,...
Player Cards: [<card1> <card2>],[<card1> <card2>],...

PREFLOP
New Cards: []
1. (<player_id>,<action_type>[,<total_amount>]);(<player_id>,<action_type>[,<total_amount>]);...
2. (<player_id>,<action_type>[,<total_amount>]);...

FLOP
New Cards: [<card1>,<card2>,<card3>]
1. (<player_id>,<action_type>[,<total_amount>]);...

...additional phases...

SETTLE
New Cards: [<any_remaining_cards>]
Winners: (Pot 0,<amount>,<best_rank>,[<winner_ids>]);...
Key conventions in the PGN format:

Player IDs are canonicalized so the button is always player 0
Actions are grouped by "orbits" (betting rounds)
Comments can be added using # and are ignored during import
Sources: 
texasholdem/game/history.py
4-11
 
texasholdem/game/history.py
402-435
 
texasholdem/game/history.py
437-456

Exporting Game History
The export_history() method saves a game's history to a PGN file:

export_history(path)

No path specified

Path is directory

File exists

Write to file

Write to file

Write to file

TexasHoldEm Instance

Determine output path

Use default: ./texas.pgn

Use directory/texas.pgn

Increment filename: texas(n).pgn

PGN File

Usage:

texas = TexasHoldEm()
# ... play game ...
history_path = texas.export_history()  # Default: ./texas.pgn
# Or specify a path:
history_path = texas.export_history("./my_games/")
Sources: 
texasholdem/game/history.py
496-533
 
tests/game/test_history.py
98-147

Importing Game History
Game history can be imported from PGN files for replay or analysis:

import_history(path)

from_string()

Construct History object

_check_missing_sections()

_check_unique_cards()

_check_correct_board_len()

Iterate through

PGN File

Read file content

Parse PGN structure

Validate history

Check required phases

Verify no duplicate cards

Verify correct number of cards

Return generator of game states

Game State Sequence

The import_history() static method returns a generator that yields TexasHoldEm instances representing each state in the game's history, allowing replay or step-by-step analysis.

Usage:

# Import and replay a game
for game_state in TexasHoldEm.import_history("./texas.pgn"):
    # Each game_state is a TexasHoldEm instance at a specific point in the game
    print(game_state.hand_phase)
Validation checks ensure the imported history is consistent and correctly structured:

No missing required sections (preflop, settle)
Cards are unique across all phases
Correct number of new cards in each phase
Sources: 
texasholdem/game/history.py
535-572
 
texasholdem/game/history.py
574-642
 
tests/game/test_history.py
66-96

Error Handling
The history system implements the HistoryImportError exception class for reporting problems with PGN files:

try:
    for game_state in TexasHoldEm.import_history("invalid.pgn"):
        pass
except HistoryImportError as e:
    print(f"Error importing game history: {e}")
Common import errors include:

Missing required sections
Duplicate cards
Incorrect number of community cards
Mismatched player counts
Malformed PGN structure
Sources: 
texasholdem/game/history.py
31-36
 
texasholdem/game/history.py
574-642
 
tests/game/test_history.py
149-158

Integration with Game System
Analysis

Export/Import

Core Game Components

contains

records

tracks

stores

export_history()

import_history()

iterate

analyze

TexasHoldEm

hand_history: History

ActionType actions

HandPhase transitions

Card distributions

PGN File

Replayed TexasHoldEm instances

Step through game states

Decision points, outcomes

The history system is tightly integrated with the main TexasHoldEm class, which automatically records game events in its hand_history attribute. This integration allows seamless export of a game's history at any point.

Sources: 
texasholdem/game/history.py
366-401
 
tests/game/test_history.py
23-63

API Reference
See the comprehensive API documentation in the Game History API Reference for detailed information on available methods and properties.

Key methods include:

Class	Method	Description
History	to_string()	Converts the history to a formatted string representation
History	from_string(string)	Creates a History object from its string representation
History	export_history(path)	Saves the history to a PGN file
History	import_history(path)	Static method that loads a history from a PGN file
History	combined_actions()	Returns a list of all PlayerAction objects across all phases
Sources: 
texasholdem/game/history.py
402-435
 
texasholdem/game/history.py
457-472
 
texasholdem/game/history.py
496-533
 
texasholdem/game/history.py
535-572
 
texasholdem/game/history.py
660-671

Dismiss
Refresh this wiki

Enter email to refresh
On this page
Game History
Overview
Core Components
History Data Structure
Game History Workflow
PGN Format
Exporting Game History
Importing Game History
Error Handling
Integration with Game System
API Reference
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