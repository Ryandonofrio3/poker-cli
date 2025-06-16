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
This document provides a comprehensive API reference for the Game History subsystem of the Texas Hold'em package. It covers the classes, methods, and file formats used for recording, exporting, and importing poker game histories. For information about the general concept of game history in the system architecture, see the Game History overview in Game History.

1. Game History Overview
The Game History subsystem allows for the detailed recording of Texas Hold'em poker hands. It captures all actions, cards, and results in a format that can be:

Exported to human-readable Portable Game Notation (PGN) files
Imported from PGN files
Used to replay or analyze hands
This system provides complete information necessary to reconstruct every state of a poker hand, making it valuable for analysis, debugging, and training AI agents.

Game Integration

History System

records

exports

imports to

History

PrehandHistory

BettingRoundHistory

SettleHistory

PlayerAction

TexasHoldEm

PGN Files

Sources: 
texasholdem/game/history.py
31-672

2. History Data Model
The History subsystem uses multiple dataclasses to represent different phases of a poker hand. Each phase captures the relevant information needed to reconstruct that portion of the game.

2.1 Core Classes
1
1
1
1
1
1
0..4
0..*
History

prehand: PrehandHistory

preflop: BettingRoundHistory

flop: BettingRoundHistory

turn: BettingRoundHistory

river: BettingRoundHistory

settle: SettleHistory

to_string()

from_string()

export_history()

import_history()

PrehandHistory

btn_loc: int

big_blind: int

small_blind: int

player_chips: Dict[int, int]

player_cards: Dict[int, List[Card]]

to_string()

from_string()

BettingRoundHistory

new_cards: List[Card]

actions: List[PlayerAction]

to_string()

from_string()

SettleHistory

new_cards: List[Card]

pot_winners: Dict[int, Tuple]

to_string()

from_string()

PlayerAction

player_id: int

action_type: ActionType

total: Optional[int]

value: Optional[int]

to_string()

from_string()

Sources: 
texasholdem/game/history.py
38-53
 
texasholdem/game/history.py
127-146
 
texasholdem/game/history.py
188-202
 
texasholdem/game/history.py
263-278
 
texasholdem/game/history.py
366-400

2.2 History Class
The main History class serves as the container for all phases of a hand:

Attribute	Type	Description
prehand	PrehandHistory	Records button position, blinds, starting chips, and hole cards
preflop	BettingRoundHistory	Records actions during the preflop betting round
flop	BettingRoundHistory (optional)	Records the flop cards and subsequent betting
turn	BettingRoundHistory (optional)	Records the turn card and subsequent betting
river	BettingRoundHistory (optional)	Records the river card and subsequent betting
settle	SettleHistory	Records the pot winners and best hand ranks
Sources: 
texasholdem/game/history.py
366-400

3. Recording Game History
The History system records actions and events as they occur during a Texas Hold'em hand. Each phase of the hand populates its corresponding history component.

"PlayerAction"
"BettingRoundHistory"
"History"
"TexasHoldEm"
"PlayerAction"
"BettingRoundHistory"
"History"
"TexasHoldEm"
Prehand Phase
Preflop Phase
loop
[For each player action]
Repeat for flop, turn, river phases
Settle Phase
Initialize history for current hand
Record button position, blinds, chips, cards
Create BettingRoundHistory for preflop
Create PlayerAction record
Add action to preflop history
Record pot winners and hand ranks
Sources: 
texasholdem/game/history.py
366-400
 
texasholdem/game/history.py
660-671

4. PGN Export and Import
4.1 Texas Hold'em PGN Format
The History system uses a custom Portable Game Notation (PGN) format specifically designed for Texas Hold'em. The file extension is .pgn.

PGN Format Conventions:

The button is assigned ID 0
Each action is represented as (player_id, action_type, total)
Winners are represented per-pot as (Pot id, amount, best rank, winner ids)
Sections are separated by blank lines
Comments can be included using # character
Sources: 
texasholdem/game/history.py
1-11
 
texasholdem/game/history.py
24-28

4.2 Export Process
Exporting game history writes a human-readable PGN file:

export_history()

to_string()

write to file

TexasHoldEm

History

String Representation

.pgn file

File naming conventions:

If a specific file is provided, it's used directly
If a directory is provided, it defaults to texas.pgn
If the file exists, it uses numerical suffixes (e.g., texas(1).pgn, texas(2).pgn)
Sources: 
texasholdem/game/history.py
496-533
 
tests/game/test_history.py
98-146

4.3 Import Process
Importing from a PGN file recreates the game state:

read file

from_string()

import_history()

iterate

.pgn file

String Content

History

Game States Iterator

TexasHoldEm

The import process performs validation checks:

Ensures all required sections are present
Verifies cards are unique
Checks for correct board lengths
Ensures there are at least 2 players
Sources: 
texasholdem/game/history.py
535-572
 
texasholdem/game/history.py
574-642

5. API Reference
5.1 History Class Methods
Method	Description
to_string()	Converts the history to a string representation
from_string(string)	Creates a History object from a string representation
export_history(path)	Exports the history to a PGN file at the specified path
import_history(path)	Static method that imports a history from a PGN file
combined_actions()	Returns a list of all PlayerAction objects across all phases
__getitem__(hand_phase)	Allows accessing history phases using HandPhase enum values
Sources: 
texasholdem/game/history.py
402-435
 
texasholdem/game/history.py
457-494
 
texasholdem/game/history.py
496-533
 
texasholdem/game/history.py
535-572
 
texasholdem/game/history.py
660-671

5.2 Auxiliary Classes
PrehandHistory
Records information about the state before a hand begins:

Button location (btn_loc)
Big blind amount (big_blind)
Small blind amount (small_blind)
Player chips (player_chips)
Player cards (player_cards)
Sources: 
texasholdem/game/history.py
38-84

PlayerAction
Records a single player action:

Player ID (player_id)
Action type (action_type)
Total bet amount (total)
Raise value (value)
Sources: 
texasholdem/game/history.py
127-186

BettingRoundHistory
Records a complete betting round:

New cards revealed (new_cards)
List of actions (actions)
Sources: 
texasholdem/game/history.py
188-260

SettleHistory
Records the results of a hand:

Any remaining cards to be revealed (new_cards)
Winners for each pot (pot_winners)
Sources: 
texasholdem/game/history.py
263-363

5.3 Error Handling
The HistoryImportError exception is thrown when there are issues importing a PGN file, such as:

File not found
Missing sections
Non-unique cards
Incorrect board lengths
Too few players
Sources: 
texasholdem/game/history.py
31-36
 
texasholdem/game/history.py
574-642

6. Example PGN Format
Below is an example of what a PGN file might look like:

PREHAND
Big Blind: 10
Small Blind: 5
Player Chips: 1000,1000,1000,1000
Player Cards: [Ah Kh],[Qc Jc],[Ts 9s],[2d 3d]

PREFLOP
New Cards: []
1. (0,CALL);(1,RAISE,30);(2,CALL);(3,FOLD)
2. (0,CALL)

FLOP
New Cards: [5h,6h,7h]
1. (0,CHECK);(1,BET,50);(2,CALL)
2. (0,CALL)

TURN
New Cards: [8d]
1. (0,CHECK);(1,CHECK);(2,BET,100)
2. (0,FOLD);(1,CALL)

RIVER
New Cards: [9c]
1. (1,CHECK);(2,BET,200)
2. (1,CALL)

SETTLE
New Cards: []
Winners: (Pot 0,795,1607,2)
Sources: 
texasholdem/game/history.py
402-435

Dismiss
Refresh this wiki

Enter email to refresh
On this page
Game History
1. Game History Overview
2. History Data Model
2.1 Core Classes
2.2 History Class
3. Recording Game History
4. PGN Export and Import
4.1 Texas Hold'em PGN Format
4.2 Export Process
4.3 Import Process
5. API Reference
5.1 History Class Methods
5.2 Auxiliary Classes
PrehandHistory
PlayerAction
BettingRoundHistory
SettleHistory
5.3 Error Handling
6. Example PGN Format
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