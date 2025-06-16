SirRender00/texasholdem | DeepWiki
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
Home
Relevant source files
Purpose and Scope
The texasholdem package is a comprehensive Python implementation of Texas Hold'em Poker that provides game logic, card representation, hand evaluation, user interfaces, and agent capabilities. This document introduces the core features, architecture, and usage of the package, serving as a starting point for both users and developers.

For installation instructions, see Installation and Setup. For detailed API documentation, see API Reference.

Sources: 
pyproject.toml
1-42
 
README.md
9-15

Key Features
The texasholdem package offers a robust implementation of Texas Hold'em Poker with the following key features:

Complete Game Logic: Implementation following World Series of Poker Official Rules
Fast Hand Evaluation: Efficient evaluation of poker hands using integer-based card representation and lookup tables
Game History: Export and import game history in human-readable format
User Interfaces: Text-based GUI for playing and replaying games
AI Agents: Simple agents (random, call) and support for custom agent development
Card System: Fast 32-bit integer representation of cards for efficient operations
Sources: 
README.md
9-15
 
README.md
70-72

System Architecture
Core Component Relationships
Agents

User Interface

Hand Evaluation

Card System

Core Game System

TexasHoldEm

HandPhase

ActionType

PlayerState

History

Card

Deck

evaluate

LOOKUP_TABLE

TextGUI

random_agent

call_agent

This diagram shows the relationships between the core components of the system. The TexasHoldEm class is the central coordinator, managing game state and rules while interacting with other components like the card system, hand evaluator, and interfaces for GUI and agents.

Sources: 
README.md
70-169

Game Execution Flow
Create TexasHoldEm

is_game_running() == True

start_hand()

betting complete

betting complete

betting complete

betting complete

is_hand_running() == False

is_game_running() == False

Initialize

PreHand

PreFlop

Flop

Turn

River

Settle

Betting Round
validate_move()

take_action()

current_player++

round complete

continue round

PlayerAction

ValidateMove

TakeAction

NextPlayer

EvaluateHands

DistributePots

This statechart illustrates the game flow, showing how a poker hand progresses through different phases (PreFlop, Flop, Turn, River) with betting rounds in between, followed by hand evaluation and pot distribution.

Sources: 
README.md
76-100

Getting Started
Installation
The package is available on PyPI and can be installed with pip:

pip install texasholdem
For the latest experimental version:

pip install texasholdem --pre
Sources: 
README.md
38-48

Quick Example
Here's a simple example to get started with a text-based interface:

from texasholdem.game.game import TexasHoldEm
from texasholdem.gui.text_gui import TextGUI

game = TexasHoldEm(buyin=500, big_blind=5, small_blind=2, max_players=6)
gui = TextGUI(game=game)

while game.is_game_running():
    game.start_hand()

    while game.is_hand_running():
        gui.run_step()

    path = game.export_history('./pgns')     # save history
    gui.replay_history(path)                 # replay history
Sources: 
README.md
50-68

Core Components
Game Logic
The TexasHoldEm class is the main entry point for game operations. It manages the game state, enforces rules, and provides methods for taking actions and querying game information.

from texasholdem import TexasHoldEm, HandPhase, ActionType

game = TexasHoldEm(buyin=500, big_blind=5, small_blind=2, max_players=9)
game.start_hand()

assert game.hand_phase == HandPhase.PREFLOP
assert game.chips_to_call(game.current_player) == game.big_blind

game.take_action(ActionType.CALL)
Sources: 
README.md
76-100

Card System
Cards are represented as 32-bit integers for fast operations and evaluation:

from texasholdem import Card

card = Card("Kd")                       # King of Diamonds
assert isinstance(card, int)            # True
assert card.rank == 11                  # 2nd highest rank (0-12)
assert card.pretty_string == "[ K ♦ ]"
Sources: 
README.md
102-113

Hand Evaluation
The evaluator module provides fast evaluation of poker hands:

from texasholdem import Card
from texasholdem.evaluator import evaluate, rank_to_string

hand_rank = evaluate(cards=[Card("Kd"), Card("5d")],
               board=[Card("Qd"),
                      Card("6d"),
                      Card("5s"),
                      Card("2d"),
                      Card("5h")])
assert hand_rank == 927
assert rank_to_string(927) == "Flush, King High"
Sources: 
README.md
154-169

Agents
The package comes with basic agents that can be used for automated play:

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

Game History
Export and import game histories to/from human-readable files:

# export to file
game.export_history("./pgns/my_game.pgn")

# import and replay
gui = TextGUI()
gui.replay_history("./pgns/my_game.pgn")
Sources: 
README.md
132-152

Technical Architecture
Infrastructure

Public API

Applications

Text-based UI

Custom Applications

Game Simulations

TexasHoldEm Game Logic

Hand Evaluation

Card Representation

Agent Interface

History Import/Export

Lookup Tables

PGN Serialization

Validation Rules

Card Bit Encoding

The architecture follows a layered design with clear separation of concerns. Applications use the public API to interact with the game system, while the infrastructure layer handles the implementation details like card encoding and lookup tables.

Sources: 
README.md
70-169

Version Information
The current stable version is 0.11.0 (released March 30, 2024). Key updates in this version include:

Support for Python 3.12
Bug fixes for RAISE actions with None value
For detailed information on versions and the roadmap to v1.0.0, see:

Changelog for release history
Version 1.0.0 Roadmap
 for upcoming features
Sources: 
README.md
16-22
 
docs/changelog-0.11.0.rst
1-10

Contributing
The project welcomes contributions from developers:

Report bugs or suggest features through 
GitHub Issues
Contribute code by following the Developer's Guide
Contact the maintainer at evyn.machi@gmail.com to become a contributor
Sources: 
README.md
30-36
 
docs/index.rst
31-38

Dismiss
Refresh this wiki

Enter email to refresh
On this page
Home
Purpose and Scope
Key Features
System Architecture
Core Component Relationships
Game Execution Flow
Getting Started
Installation
Quick Example
Core Components
Game Logic
Card System
Hand Evaluation
Agents
Game History
Technical Architecture
Version Information
Contributing
Ask Devin about SirRender00/texasholdem
Deep Research

Syntax error in text
mermaid version 11.6.0