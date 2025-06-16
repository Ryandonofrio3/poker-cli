Text GUI | SirRender00/texasholdem | DeepWiki
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
Text GUI
Relevant source files
The Text GUI is a command-line interface for the Texas Hold'em poker game, offering a robust terminal-based visualization system. This document covers the TextGUI class implementation, its architecture, usage patterns, and customization options. The Text GUI provides a complete poker table visualization with player information, cards, betting animations, and game history tracking in a terminal environment.

Core Architecture
The Text GUI system is built on Python's curses library, which provides terminal control capabilities for text-based interfaces. The architecture follows a block-based approach where the screen is divided into distinct sections for different UI elements.

contains

contains

AbstractGUI

+game: TexasHoldEm

+visible_players: List[int]

+enable_animation: bool

+no_wait: bool

+display_state()

+display_action()

+display_win()

+accept_input()

+prompt_input()

+display_error()

+wait_until_prompted()

TextGUI

-main_block: _Block

-_action_patterns: List[Tuple]

-_command_patterns: List[Tuple]

+refresh()

+hide()

-_capture_string()

-_recalculate_object_blocks()

-_paint_table_ring()

-_player_block()

-_board_block()

-_history_block()

_Block

+name: str

+window: curses._CursesWindow

+blocks: Dict[str, _Block]

+content: Tuple

+content_stack: deque

+add_content()

+new_block()

+erase()

+refresh()

+stash_state()

+pop_state()

Sources: 
texasholdem/gui/text_gui.py
24-25
 
texasholdem/gui/text_gui.py
137-167
 
texasholdem/gui/text_gui.py
437-489

The TextGUI inherits from AbstractGUI, providing concrete implementations for all the required interface methods. It manages a hierarchical structure of _Block objects, each representing a rectangular region on the screen with specific content and functionality.

Screen Layout and Components
The Text GUI organizes the game display into a structured layout with predefined regions for different elements. The screen components include:

Main Window

Shows cards for visible players

Shows bet amounts

Shows community cards and pot

Shows action history

Captures user commands

Displays error messages

Shows available actions

Shows software version

Visual table representation

Player Info Blocks

Player Bet Blocks

Board Block

History Block

Input Block

Error Block

Available Actions Block

Version Block

Table Ellipse

UserView

UserInteraction

MetaInfo

Sources: 
texasholdem/gui/text_gui.py
402-410
 
texasholdem/gui/text_gui.py
632-724

The screen layout is dynamically calculated based on terminal dimensions, with player information blocks placed in an elliptical arrangement around a central table. The positions are computed using mathematical formulas to create a visually appealing poker table representation.

Block System
The core of the Text GUI is the _Block class, which wraps around curses windows to provide enhanced functionality:

Sources: 
texasholdem/gui/text_gui.py
113-126
 
texasholdem/gui/text_gui.py
136-394

Each _Block instance can contain content and child blocks, forming a tree structure. The system supports:

Content alignment (top, middle, bottom)
Text justification (left, center, right)
Borders
Text wrapping
State management (stashing/retrieving content)
Nested blocks for complex layouts
Initialization and Usage
Basic Initialization
To use the Text GUI, you instantiate it with a TexasHoldEm game instance:

from texasholdem.game.game import TexasHoldEm
from texasholdem.gui.text_gui import TextGUI

game = TexasHoldEm(num_players=6)
gui = TextGUI(game=game)
Sources: 
texasholdem/gui/text_gui.py
438-490

Configuration Options
The TextGUI constructor accepts several parameters to customize behavior:

Sources: 
texasholdem/gui/text_gui.py
437-456

game: The TexasHoldEm game instance to visualize
visible_players: Player IDs whose cards should be visible (default: all players)
enable_animation: Whether to show chip movement animations (default: True)
no_wait: Whether to skip waits for user input (default: False)
Main Features
Displaying Game State
The display_state() method renders the complete game state, including:

Player information (name, state, chips)
Player cards (visible for selected players)
Current bets
Community cards
Pot information
Game history
Available actions for current player
Sources: 
texasholdem/gui/text_gui.py
901-932

Player Information Display
Each player's information is displayed in blocks arranged in an elliptical pattern around the central table:

Player Block Content

Player ID

Player State

Chip Count

Position Indicator (Button/SB/BB)

Cards (visible or hidden)

Sources: 
texasholdem/gui/text_gui.py
725-764

Game History
The history panel on the right side of the display shows a chronological record of the game actions:

Sources: 
texasholdem/gui/text_gui.py
786-825

Animations
When enabled, the TextGUI provides animations for player actions, particularly for chip movements during bets and calls:

"Player Bet Block"
"Animation System"
"Player Block"
"Player Bet Block"
"Animation System"
"Player Block"
When player raises or calls
loop
[Animation
Steps]
Start animation from player position
Calculate next position
Draw symbol at position
Sleep briefly
End animation at bet position
Sources: 
texasholdem/gui/text_gui.py
954-1012

User Input Handling
The TextGUI provides a command-line interface for user input, supporting various poker actions:

Input Commands

call

check

fold

raise [amount]

all-in

exit/quit

User Input

Command Parsing

Valid Action
(return to game)

System Command
(e.g., exit)

Error
(display message)

Sources: 
texasholdem/gui/text_gui.py
460-466
 
texasholdem/gui/text_gui.py
541-630

The input system:

Supports standard poker commands (call, check, fold, raise, all-in)
Handles system commands (exit, quit)
Provides error messages for invalid input
Has backspace and line editing capabilities
Cross-Platform Support
The TextGUI includes special handling for Windows compatibility, as the curses library has some differences on Windows:

Windows Adjustments

Yes

No

Detect OS

Is Windows?

Apply Windows-specific adjustments

Use standard behavior

Use curses.resize_term instead of resizeterm

Different handling for backspace key

Special Ctrl+C handling

Adjusted animation timing

Sources: 
texasholdem/gui/text_gui.py
28-34
 
texasholdem/gui/text_gui.py
427-434
 
texasholdem/gui/text_gui.py
574-576

Integration with Game System
The TextGUI integrates closely with the TexasHoldEm game system to visualize the game state and facilitate player interaction:

"Human Player"
"TextGUI"
"TexasHoldEm"
"Human Player"
"TextGUI"
"TexasHoldEm"
loop
[Game Round]
Initialize with game reference
display_state()
Show game state
prompt_input()
Display input prompt
Enter action
Return parsed action
Process action
display_action()
Show action animation
display_win()
Show final results
Sources: 
texasholdem/gui/text_gui.py
901-1034

Advanced Customization
Visible Players
By default, all player cards are visible. For a more realistic poker experience, you can customize which players' cards are shown:

# Only show cards for player 0
gui.set_visible_players([0])

# Show cards for multiple players
gui.set_visible_players([0, 2, 4])
Sources: 
texasholdem/gui/text_gui.py
502-512

Disabling Animations
For faster gameplay or if terminal support is limited, animations can be disabled:

# Disable animations in constructor
gui = TextGUI(game=game, enable_animation=False)
Sources: 
texasholdem/gui/text_gui.py
437-456
 
texasholdem/gui/text_gui.py
951-960

Testing and Development Notes
The Text GUI has dedicated test cases to ensure proper functioning, including tests for:

Display state verification
Input command parsing
Visible player settings
Platform compatibility
Windows-specific testing is performed through a dedicated CI workflow to ensure cross-platform functionality.

Sources: 
tests/gui/text_gui.py
1-196
 
.github/workflows/windows-gui-tests.yml
1-47

Recent Changes
The Text GUI underwent a significant overhaul in version 0.7.0, adding:

A history panel
Support for 2-9 players
Chip movement animations
Improved user experience
Some methods were deprecated in favor of more consistently named alternatives.

Sources: 
docs/changelog-0.7.0.rst
1-22
 
texasholdem/gui/text_gui.py
498-538

Dismiss
Refresh this wiki

Enter email to refresh
On this page
Text GUI
Core Architecture
Screen Layout and Components
Block System
Initialization and Usage
Basic Initialization
Configuration Options
Main Features
Displaying Game State
Player Information Display
Game History
Animations
User Input Handling
Cross-Platform Support
Integration with Game System
Advanced Customization
Visible Players
Disabling Animations
Testing and Development Notes
Recent Changes
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