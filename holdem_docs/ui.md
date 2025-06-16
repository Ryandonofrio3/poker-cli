User Interfaces | SirRender00/texasholdem | DeepWiki
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
User Interfaces
Relevant source files
This document provides an overview of the user interface system in the Texas Hold'em package. It covers the available GUI options, their architecture, and common usage patterns. For information about game agents that can interact with these interfaces, see Game Agents.

GUI Architecture
The Texas Hold'em package implements a layered GUI architecture that separates interface behaviors from game logic. This approach allows for different UI implementations while maintaining consistent game interactions.

main_block

blocks

1
*
*
*
AbstractGUI

+game: TexasHoldEm

+visible_players: List[int]

+enable_animation: bool

+no_wait: bool

+display_state()

+display_action()

+set_visible_players()

+display_win()

+wait_until_prompted()

+run_step()

+from_history()

TextGUI

+main_block: _Block

+accept_input()

+display_error()

+prompt_input()

+refresh()

+hide()

+_display_action()

_Block

+name: str

+window: curses._CursesWindow

+blocks: Dict[str, _Block]

+content: Tuple

+content_stack: deque

+add_content()

+stash_state()

+pop_state()

+new_block()

+get_block()

+erase()

+refresh()

Sources: 
texasholdem/gui/abstract_gui.py
 
texasholdem/gui/text_gui.py
24-1045

AbstractGUI Base Class
The AbstractGUI class defines the common interface that all GUI implementations must provide. It serves as the foundation for consistent user interaction regardless of the specific GUI implementation.

Key methods that all GUI implementations must provide include:

Method	Purpose
display_state()	Shows the current game state
display_action()	Displays the most recent action
set_visible_players()	Controls which players' cards are visible
display_win()	Shows the winner of a hand
wait_until_prompted()	Waits for user input before continuing
prompt_input()	Prompts the user for action input
accept_input()	Captures and processes user input
The class also provides compound methods built from these primitives:

Method	Purpose
run_step()	Handles a complete player turn (display, input, validate, action)
from_history()	Displays a previously recorded game history
Sources: 
texasholdem/gui/abstract_gui.py
 
docs/guis.rst
9-33

TextGUI Implementation
The TextGUI is a terminal-based implementation of the AbstractGUI that uses the Python curses library to create an interactive text interface.

Screen Layout
The TextGUI organizes the poker table using a geometric layout that positions player information around an elliptical table:

TextGUI Layout

Player Bets

Player 1 Bet

Player 2 Bet

Player 3 Bet

Player 4 Bet

Player 5 Bet

Player 6 Bet

Main Window

Table Ellipse

Board Block

History Block

Input Block

Error Block

Available Actions

Version Info

Player Information

Player 1 Info

Player 2 Info

Player 3 Info

Player 4 Info

Player 5 Info

Player 6 Info

Sources: 
texasholdem/gui/text_gui.py
632-724
 
texasholdem/gui/text_gui.py
843-867

Block System
The TextGUI is built on a custom block system that manages curses windows in a hierarchical structure:

The _Block class wraps a curses window and can contain child blocks
Each block manages its content and positioning
Blocks can stash and restore their state for refresh operations
The main_block contains all other blocks in a tree structure
This approach simplifies screen layout management and content updating across the complex UI.

Sources: 
texasholdem/gui/text_gui.py
136-393

User Interaction Flow
This diagram illustrates how user input is processed through the TextGUI:

TexasHoldEm
TextGUI
User
TexasHoldEm
TextGUI
User
alt
[Invalid Move]
[Valid Move]
display_state()
Show game state
prompt_input()
Request action
Enter action (e.g., "call", "fold", "raise 50")
accept_input()
validate_move()
Error message
display_error()
Show error message
Confirm valid move
take_action()
Update game state
display_action()
Show action animation
Sources: 
texasholdem/gui/text_gui.py
541-630
 
texasholdem/gui/text_gui.py
934-943
 
texasholdem/gui/text_gui.py
944-949
 
texasholdem/gui/text_gui.py
960-1012

Key Features
The TextGUI provides several notable features:

Card Visibility Control: Selectively show or hide player cards
Action Animation: Animated chip movements for betting actions
Command-Based Input: Simple text commands for game actions
Game History Display: Shows a record of actions in the current hand
Error Handling: Clear display of error messages for invalid inputs
Command Input
The TextGUI accepts the following text commands:

Command	Action	Description
check	CHECK	Make a checking action when no bet to call
call	CALL	Call the current bet
fold	FOLD	Fold your hand
raise X or raise to X	RAISE	Raise to X chips total
all-in or all_in	ALL_IN	Bet all remaining chips
exit or quit	(System)	Exit the application
Sources: 
texasholdem/gui/text_gui.py
460-466
 
texasholdem/gui/text_gui.py
471
 
docs/guis.rst
160-165

Platform Compatibility
The TextGUI uses the curses library which has different compatibility across operating systems:

Unix/Linux/macOS: Full native support
Windows: Requires the windows-curses package (automatically installed as a dependency)
Windows Limitation: Only Python 3.10 or lower is supported on Windows due to windows-curses compatibility
Some features like window resizing may behave differently across platforms.

Sources: 
texasholdem/gui/text_gui.py
28-33
 
docs/guis.rst
43-49

Common Usage Patterns
Basic Usage
To play the game with manual input:

from texasholdem.game.game import TexasHoldEm
from texasholdem.gui.text_gui import TextGUI

game = TexasHoldEm(buyin=500, big_blind=5, small_blind=2, max_players=6)
gui = TextGUI(game=game)

while game.is_game_running():
    game.start_hand()
    
    while game.is_hand_running():
        gui.run_step()  # Handles display, input, action
    
    gui.display_win()  # Show the winner
Watching AI Agents Play
To observe automated agents playing against each other:

from texasholdem.game.game import TexasHoldEm
from texasholdem.gui.text_gui import TextGUI
from texasholdem.agents.basic import random_agent

game = TexasHoldEm(buyin=500, big_blind=5, small_blind=2, max_players=6)
gui = TextGUI(game=game)

while game.is_game_running():
    game.start_hand()
    
    while game.is_hand_running():
        gui.display_state()
        gui.wait_until_prompted()  # Wait for user to press Enter
        
        game.take_action(*random_agent(game))
        gui.display_action()
    
    gui.display_win()
Playing Against AI Agents
To play as one player with AI opponents:

from texasholdem.game.game import TexasHoldEm
from texasholdem.gui.text_gui import TextGUI
from texasholdem.agents.basic import random_agent

game = TexasHoldEm(buyin=500, big_blind=5, small_blind=2, max_players=6)
gui = TextGUI(game=game, visible_players=[0])  # Only see your own cards

while game.is_game_running():
    game.start_hand()
    
    while game.is_hand_running():
        if game.current_player == 0:  # Human player's turn
            gui.run_step()
        else:  # AI player's turn
            gui.display_state()
            game.take_action(*random_agent(game))
            gui.display_action()
    
    gui.display_win()
Sources: 
docs/guis.rst
51-166

Future Extensions
The package is designed to support additional GUI implementations in the future. Potential extensions might include:

Web-based interfaces
Graphical interfaces using libraries like Pygame or Tkinter
Mobile app interfaces
To create a new GUI implementation, developers would need to subclass the AbstractGUI class and implement all required methods.

Sources: 
docs/guis.rst
6-8

Dismiss
Refresh this wiki

Enter email to refresh
On this page
User Interfaces
GUI Architecture
AbstractGUI Base Class
TextGUI Implementation
Screen Layout
Block System
User Interaction Flow
Key Features
Command Input
Platform Compatibility
Common Usage Patterns
Basic Usage
Watching AI Agents Play
Playing Against AI Agents
Future Extensions
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